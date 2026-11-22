"""Drive headless Chrome over the DevTools protocol, with a throwaway static server for public/.

Standard library only. Used by check_site.py and shots.py.
"""
import base64
import functools
import http.server
import json
import os
import pathlib
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]  # repository root
PUBLIC = ROOT / "public"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
IPHONE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
)
DESKTOP = dict(width=1440, height=900, dpr=1, mobile=False)
MOBILE = dict(width=390, height=844, dpr=2, mobile=True)


class _Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class _Server(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass  # the browser dropping a connection is not interesting


def serve(root=PUBLIC):
    """Serve `root` on a free local port. Returns (server, base_url)."""
    server = _Server(("127.0.0.1", 0), functools.partial(_Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, "http://127.0.0.1:%d" % server.server_address[1]


def pages():
    """[(name, url)] of the built pages (redirect stubs left out), e.g. ("home", "/")."""
    out = []
    for path in sorted(PUBLIC.rglob("index.html")):
        if 'http-equiv="refresh"' in path.read_text(encoding="utf-8"):
            continue
        rel = path.parent.relative_to(PUBLIC).as_posix()
        out.append(("home", "/") if rel == "." else (rel.replace("/", "-"), "/" + rel + "/"))
    return out


class _WebSocket:
    """Just enough of RFC 6455 for a local DevTools connection (text frames, no extensions)."""

    def __init__(self, url):
        u = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall(
            (
                "GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (u.path, u.hostname, u.port, key)
            ).encode()
        )
        self.buf = bytearray()
        while b"\r\n\r\n" not in self.buf:
            self.buf += self.sock.recv(4096)
        head, _, rest = bytes(self.buf).partition(b"\r\n\r\n")
        if b" 101 " not in head.split(b"\r\n")[0]:
            raise RuntimeError("WebSocket handshake failed: %r" % head[:200])
        self.buf = bytearray(rest)
        self.parts = []

    def send(self, text):
        data = text.encode()
        head = bytearray([0x81])
        n = len(data)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head.append(0x80 | 126)
            head += struct.pack(">H", n)
        else:
            head.append(0x80 | 127)
            head += struct.pack(">Q", n)
        mask = os.urandom(4)
        head += mask
        body = bytes(b ^ mask[i & 3] for i, b in enumerate(data))
        self.sock.sendall(bytes(head) + body)

    def _need(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 16)
            if not chunk:
                raise EOFError("browser closed the connection")
            self.buf += chunk

    def recv(self, timeout=30.0):
        """Next text message, or None if nothing complete arrives within `timeout` seconds."""
        self.sock.settimeout(max(timeout, 0.01))
        try:
            while True:
                self._need(2)
                b1, b2 = self.buf[0], self.buf[1]
                n, off = b2 & 0x7F, 2
                if n == 126:
                    self._need(4)
                    n, off = struct.unpack(">H", self.buf[2:4])[0], 4
                elif n == 127:
                    self._need(10)
                    n, off = struct.unpack(">Q", self.buf[2:10])[0], 10
                masked = b2 & 0x80
                if masked:
                    off += 4
                self._need(off + n)
                payload = bytes(self.buf[off : off + n])
                if masked:
                    mask = self.buf[off - 4 : off]
                    payload = bytes(b ^ mask[i & 3] for i, b in enumerate(payload))
                del self.buf[: off + n]
                op = b1 & 0x0F
                if op == 8:
                    raise EOFError("browser closed the connection")
                if op in (9, 10):  # ping / pong
                    continue
                self.parts.append(payload)
                if b1 & 0x80:
                    msg = b"".join(self.parts).decode()
                    self.parts = []
                    return msg
        except socket.timeout:
            return None


class Browser:
    """One headless Chrome page. Use as a context manager."""

    def __init__(self, width=1440, height=900, dpr=1, mobile=False, scheme=None, reduced_motion=False):
        self.width, self.height, self.dpr = width, height, dpr
        self.dir = tempfile.mkdtemp(prefix="cdp-")
        self.proc = subprocess.Popen(
            [
                CHROME, "--headless=new", "--remote-debugging-port=0", "--user-data-dir=" + self.dir,
                "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--hide-scrollbars",
                "--mute-audio", "--window-size=%d,%d" % (width, height), "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        port_file = pathlib.Path(self.dir, "DevToolsActivePort")
        deadline = time.time() + 30
        while not (port_file.exists() and port_file.read_text().strip()):
            if time.time() > deadline or self.proc.poll() is not None:
                self.close()
                raise RuntimeError("Chrome did not start (CHROME=%s)" % CHROME)
            time.sleep(0.05)
        port = port_file.read_text().split()[0]
        targets = json.load(urllib.request.urlopen("http://127.0.0.1:%s/json/list" % port, timeout=10))
        page = next(t for t in targets if t["type"] == "page")
        self.ws = _WebSocket(page["webSocketDebuggerUrl"])
        self.seq = 0
        self.events = []
        for domain in ("Page", "Runtime", "Network", "Log"):
            self.cmd(domain + ".enable")
        self.cmd("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=dpr, mobile=mobile)
        if mobile:
            self.cmd("Emulation.setTouchEmulationEnabled", enabled=True)
            self.cmd("Emulation.setUserAgentOverride", userAgent=IPHONE_UA)
        features = []
        if scheme:
            features.append({"name": "prefers-color-scheme", "value": scheme})
        if reduced_motion:
            features.append({"name": "prefers-reduced-motion", "value": "reduce"})
        if features:
            self.cmd("Emulation.setEmulatedMedia", features=features)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.dir, ignore_errors=True)

    def cmd(self, method, **params):
        self.seq += 1
        self.ws.send(json.dumps({"id": self.seq, "method": method, "params": params}))
        deadline = time.time() + 60
        while True:
            raw = self.ws.recv(timeout=deadline - time.time())
            if raw is None:
                raise TimeoutError("no reply to " + method)
            msg = json.loads(raw)
            if msg.get("id") == self.seq:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"].get("message")))
                return msg.get("result", {})
            if "method" in msg:
                self.events.append(msg)

    def pump(self, seconds):
        """Let the page run for `seconds`, collecting events."""
        deadline = time.time() + seconds
        while time.time() < deadline:
            raw = self.ws.recv(timeout=deadline - time.time())
            if raw is not None:
                msg = json.loads(raw)
                if "method" in msg:
                    self.events.append(msg)

    def eval(self, expression):
        """Evaluate JS in the page (promises are awaited) and return its JSON value."""
        r = self.cmd("Runtime.evaluate", expression=expression, awaitPromise=True, returnByValue=True, userGesture=True)
        if "exceptionDetails" in r:
            d = r["exceptionDetails"]
            raise RuntimeError("JS error: " + (d.get("exception", {}).get("description") or d.get("text", "")))
        return r.get("result", {}).get("value")

    def goto(self, url, settle=1.5):
        """Load a URL, then wait for the load event, web fonts, and `settle` seconds."""
        mark = len(self.events)
        started = self.cmd("Page.navigate", url=url)
        deadline = time.time() + 45
        # A hash-only change of the current document has no loaderId and fires no load event.
        while "loaderId" in started and not any(e["method"] == "Page.loadEventFired" for e in self.events[mark:]):
            if time.time() > deadline:
                break
            self.pump(0.1)
        try:
            self.eval("document.fonts.ready.then(() => true)")
        except Exception:
            pass
        self.pump(settle)

    def page_height(self):
        return int(self.cmd("Page.getLayoutMetrics")["cssContentSize"]["height"])

    def screenshot(self, path, clip=None):
        """Viewport screenshot, or the page region clip=(x, y, w, h) in CSS pixels."""
        params = {"format": "png"}
        if clip:
            x, y, w, h = clip
            params.update(clip={"x": x, "y": y, "width": w, "height": h, "scale": 1}, captureBeyondViewport=True)
        data = self.cmd("Page.captureScreenshot", **params)["data"]
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_bytes(base64.b64decode(data))
        return path
