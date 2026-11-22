#!/usr/bin/env python3
"""Build the site: content/ (Markdown + YAML) + templates/ (Jinja2) + static/  ->  public/

  python3 build.py                 build into public/
  python3 build.py --serve [PORT]  build, serve on http://localhost:PORT (default 8000), rebuild and reload on changes

See README.md for the content model.
"""
import datetime
import functools
import http.server
import json
import re
import shutil
import struct
import sys
import threading
import time
from pathlib import Path

import jinja2
import markdown
import yaml
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
CONTENT, TEMPLATES, STATIC, OUT = (ROOT / d for d in ("content", "templates", "static", "public"))
SITE_FILE = ROOT / "site.yml"
MD_EXTENSIONS = ["attr_list", "md_in_html", "tables", "fenced_code", "footnotes", "sane_lists", "toc"]


class BuildError(Exception):
    pass


# ── Markdown ──────────────────────────────────────────────────────────────

_md = markdown.Markdown(extensions=MD_EXTENSIONS)
# A paragraph holding only a YouTube link becomes a click-to-play video.
_YOUTUBE = re.compile(
    r'<p><a href="https://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})[^"]*">([^<]*)</a></p>'
)


def _video(m):
    vid, title = m[1], m[2]
    return (
        f'<a class="yt" href="https://www.youtube.com/watch?v={vid}" data-yt="{vid}" data-title="{title}" aria-label="Play video: {title}">'
        f'<img src="https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" alt="" loading="lazy" decoding="async">'
        f'<span class="yt-play">{icon("play")}</span></a>'
    )


def md(text):
    _md.reset()
    return Markup(_YOUTUBE.sub(_video, _md.convert(str(text or ""))))


def md_inline(text):
    """Inline Markdown (for YAML fields): no surrounding <p>."""
    return Markup(re.sub(r"^<p>(.*)</p>$", r"\1", str(md(text)), flags=re.S))


def md_toc(text):
    """[(id, title)] of the level-2 headings in a Markdown text."""
    md(text)
    out = []

    def walk(tokens):
        for t in tokens:
            if t["level"] == 2:
                out.append((t["id"], Markup(t["name"])))
            walk(t["children"])

    walk(_md.toc_tokens)
    return out


def md_blocks(text):
    """One HTML fragment per paragraph-level block (blank-line separated)."""
    return [md(b) for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")


def md_cards(text):
    """Split on '### Heading' lines: [{title, html, image}], the image pulled out of the text."""
    cards = []
    for part in re.split(r"^### ", text, flags=re.M)[1:]:
        title, _, body = part.partition("\n")
        m = _IMAGE.search(body)
        image = {"src": m[2], "alt": m[1]} if m else None
        cards.append({"title": title.strip(), "html": md(_IMAGE.sub("", body)), "image": image})
    return cards


# ── Icons and images ──────────────────────────────────────────────────────

ICONS = {}


def icon(name, cls=""):
    if name not in ICONS:
        raise BuildError(f"unknown icon {name!r} (names are in templates/icons.json)")
    view_box, body = ICONS[name]
    return Markup(
        f'<svg class="icon{" " + cls if cls else ""}" viewBox="{view_box}" width="1em" height="1em" '
        f'fill="currentColor" aria-hidden="true" focusable="false">{body}</svg>'
    )


def icon_or_text(x):
    """An icon by name, otherwise the text itself (e.g. an emoji)."""
    return icon(x) if x in ICONS else Markup('<span class="emoji" aria-hidden="true">%s</span>') % x


@functools.lru_cache(maxsize=None)
def image_size(src):
    """(width, height) of a PNG, JPEG or SVG under static/, or None."""
    path = STATIC / src.lstrip("/")
    if not path.is_file():
        raise BuildError(f"missing file static{src}")
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            marker, length = data[i + 1], struct.unpack(">H", data[i + 2 : i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return w, h
            i += 2 + length
    if path.suffix == ".svg":
        m = re.search(rb'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', data[:8192])
        if m:
            return round(float(m[1])), round(float(m[2]))
    return None


def img(image, cls="", eager=False, decorative=False):
    """<img> for {src, alt}, with intrinsic width/height so the layout does not shift."""
    src = image["src"]
    size = image_size(src) if src.startswith("/") else None
    attrs = f' class="{cls}"' if cls else ""
    attrs += ' alt=""' if decorative else f' alt="{escape(image.get("alt", ""))}"'
    if size:
        attrs += f' width="{size[0]}" height="{size[1]}"'
    attrs += ' decoding="async"' + ("" if eager else ' loading="lazy"')
    return Markup(f'<img src="{escape(src)}"{attrs}>')


def ratio(image):
    w, h = image_size(image["src"]) or (1, 1)
    return w / h


# ── Content ───────────────────────────────────────────────────────────────


def read(path):
    """(front matter dict, Markdown body) of a content file."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n?(.*)", text, flags=re.S)
    try:
        meta, body = (yaml.safe_load(m[1]) or {}, m[2]) if m else ({}, text)
    except yaml.YAMLError as err:
        raise BuildError(f"{path.relative_to(ROOT)}: bad front matter: {err}")
    return meta, body


def load_items(folder):
    """The .md files of a folder page (all but index.md), sorted by `order`, then file name."""
    items = []
    for path in sorted(folder.glob("*.md")):
        if path.name != "index.md":
            meta, body = read(path)
            items.append({"id": path.stem, **meta, "body": body, "html": md(body)})
    return sorted(items, key=lambda x: x.get("order", float("inf")))


def load_pages():
    """{url: page}. content/X.md and content/X/index.md are pages at /X/; content/index.md is /."""
    pages = {}
    for path in sorted(CONTENT.rglob("*.md")):
        parts = path.relative_to(CONTENT).parts
        if path.name == "index.md":
            slug = "/".join(parts[:-1])
        elif len(parts) == 1:
            slug = path.stem
        else:
            continue  # an item of a folder page
        meta, body = read(path)
        url = "/" + (slug + "/" if slug else "")
        pages[url] = {
            "title": slug.replace("-", " ").title(),
            **meta,
            "url": url,
            "body": body,
            "html": md(body),
            "toc": md_toc(body),
            "entries": load_items(path.parent) if path.name == "index.md" and slug else [],
        }
    return pages


def load_news():
    news = yaml.safe_load((CONTENT / "news.yml").read_text(encoding="utf-8")) if (CONTENT / "news.yml").exists() else []
    for n in news:
        try:
            d = datetime.datetime.strptime(str(n["date"]), "%b %Y")
        except (KeyError, ValueError):
            raise BuildError(f'content/news.yml: date must look like "Sep 2026", got {n.get("date")!r}')
        n.update(iso=d.strftime("%Y-%m"), year=d.year)
    return news


# ── Build ─────────────────────────────────────────────────────────────────


def rel_url(target, page_url):
    """A site-root URL ("/x/") as seen from page_url, so the site also works under a sub-folder."""
    return "../" * (page_url.count("/") - 1) + target[1:] or "./"


def relativize(html, url):
    html = re.sub(r'\b(href|src|data-pdf)="(/(?!/)[^"]*)"', lambda m: f'{m[1]}="{rel_url(m[2], url)}"', html)
    # Off-site links open in a new tab.
    return re.sub(r'<a (?![^>]*target=)([^>]*href="https?://)', r'<a target="_blank" rel="noopener" \1', html)


def build():
    t0 = time.time()
    ICONS.clear()
    ICONS.update(json.loads((TEMPLATES / "icons.json").read_text(encoding="utf-8"))["icons"])
    image_size.cache_clear()
    site = yaml.safe_load(SITE_FILE.read_text(encoding="utf-8"))
    pages = load_pages()
    for n in site["nav"]:
        if n["url"] not in pages:
            raise BuildError(f"site.yml: nav url {n['url']} has no page in content/")
        n["accent"] = pages[n["url"]].get("accent", "home")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(md=md, inline=md_inline, blocks=md_blocks, cards=md_cards, ratio=ratio)
    now = datetime.datetime.now(datetime.timezone.utc)
    env.globals.update(
        site=site, pages=pages, news=load_news(), icon=icon, icon_or_text=icon_or_text, img=img,
        entries=lambda items, key: [(x["id"], x[key]) for x in items],
        updated=now.strftime("%d %b, %Y"),
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    for url, page in pages.items():
        name = page.get("template") or ("home" if url == "/" else "page")
        nav_i = next((i for i, n in enumerate(site["nav"]) if n["url"] == url), None)
        try:
            html = env.get_template(name + ".html").render(page=page)
        except jinja2.TemplateError as err:
            raise BuildError(f"{url} (template {name}.html): {err}")
        dest = OUT / url.strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(relativize(html, url), encoding="utf-8")
    for old, new in (site.get("redirects") or {}).items():
        dest = OUT / old.strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        to = rel_url(new, old)
        dest.write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={to}"><a href="{to}">{new}</a>\n', encoding="utf-8")
    print(f"built {len(pages)} pages into {OUT.relative_to(ROOT)}/ in {time.time() - t0:.2f}s")


# Live reload for --serve only: pages poll /__build and reload when the build number changes.
RELOAD_JS = b"""<script>(() => { let v; setInterval(async () => { try {
  const n = await (await fetch("/__build", { cache: "no-store" })).text();
  if (v && n !== v) location.reload(); v = n; } catch (e) {} }, 700); })();</script>"""


def serve(port):
    builds = [0]

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(OUT), **kwargs)

        def log_message(self, *args):
            pass

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def send_body(self, body, ctype):
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?")[0].split("#")[0]
            if path == "/__build":
                return self.send_body(str(builds[0]).encode(), "text/plain")
            file = Path(self.translate_path(path))
            if file.is_dir():
                file = file / "index.html"
            if file.suffix == ".html" and file.is_file():
                html = file.read_bytes().replace(b"</body>", RELOAD_JS + b"</body>", 1)
                return self.send_body(html, "text/html; charset=utf-8")
            super().do_GET()

    def snapshot():
        files = [SITE_FILE] + [p for d in (CONTENT, TEMPLATES, STATIC) for p in d.rglob("*")]
        return {p: p.stat().st_mtime for p in files if p.exists()}

    build()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"serving http://localhost:{port}/ (Ctrl+C to stop); rebuilding on changes")
    last = snapshot()
    try:
        while True:
            time.sleep(0.5)
            now = snapshot()
            if now != last:
                last = now
                try:
                    build()
                    builds[0] += 1
                except Exception as err:  # keep serving; show the problem
                    print(f"build failed: {err}")
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        if args and args[0] == "--serve":
            serve(int(args[1]) if len(args) > 1 else 8000)
        elif args:
            sys.exit(__doc__)
        else:
            build()
    except BuildError as err:
        sys.exit(f"build failed: {err}")
