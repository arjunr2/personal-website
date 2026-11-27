#!/usr/bin/env python3
"""Browser checks of the built site (run `python3 build.py` first).

  python3 tools/check_site.py

Every page in public/, on desktop (1440x900) and phone (390x844), in light and dark:
FAIL on JavaScript errors, failed requests, broken images, sideways scrolling on the phone,
internal links or #anchors that go nowhere, and pages without exactly one <h1>.
Then a few interactions (theme switch, news filter, lightbox, PDF preview, video, deep link) and a no-JavaScript load.
WARN: things to look at by hand. Exit status is 0 when nothing failed.
"""
import sys
import urllib.parse

import cdp

# Third parties whose own noise is not the site's problem.
NOISE = ("youtube.com", "youtube-nocookie.com", "googlevideo.com", "doubleclick.net", "ggpht.com", "google.com/", "gstatic.com/cv")

PAGE_JS = r"""
(async () => {
  const out = { fails: [], warns: [] };
  // Load every lazy image, then wait for them.
  document.querySelectorAll('img[loading="lazy"]').forEach((i) => (i.loading = "eager"));
  await Promise.race([
    Promise.all([...document.images].map((i) => (i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; })))),
    new Promise((r) => setTimeout(r, 8000)),
  ]);
  for (const i of document.images) if (!i.complete || i.naturalWidth === 0) out.fails.push("broken image " + i.getAttribute("src"));
  const de = document.documentElement, over = de.scrollWidth - de.clientWidth;
  if (over > 1) {
    const bad = [...document.querySelectorAll("body *")].filter((e) => { const r = e.getBoundingClientRect(); return r.width && r.right > de.clientWidth + 1; });
    out.overflow = over + "px wider than the viewport, e.g. " + bad.slice(0, 3).map((e) => e.tagName.toLowerCase() + "." + [...e.classList].join(".")).join(", ");
  }
  const h1 = document.querySelectorAll("h1").length;
  if (h1 !== 1) out.fails.push(h1 + " <h1> elements (want 1)");
  if (!document.querySelector("main")) out.fails.push("no <main>");
  if (!de.lang || !document.title.trim()) out.fails.push("missing lang or <title>");
  const noAlt = [...document.images].filter((i) => !i.hasAttribute("alt"));
  if (noAlt.length) out.fails.push(noAlt.length + " <img> without alt, e.g. " + noAlt[0].getAttribute("src"));
  const named = (el) => el.textContent.trim() || el.getAttribute("aria-label") || el.getAttribute("title") || el.querySelector("img[alt]:not([alt=''])");
  const anon = [...document.querySelectorAll("a[href], button")].filter((el) => el.checkVisibility() && !named(el));
  if (anon.length) out.fails.push(anon.length + " link(s)/button(s) without an accessible name");
  out.theme = de.dataset.theme;
  // Phone: tiny text
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let small = 0;
  while (w.nextNode()) { const el = w.currentNode.parentElement; if (w.currentNode.nodeValue.trim() && el.checkVisibility() && parseFloat(getComputedStyle(el).fontSize) < 11) small++; }
  if (small) out.warns.push(small + " text run(s) under 11px");
  out.links = [...document.querySelectorAll("a[href]")].map((a) => a.href);
  out.ids = [...document.querySelectorAll("[id]")].map((e) => e.id);
  return out;
})()
"""


def event_problems(events):
    urls, out = {}, []
    for e in events:
        m, p = e["method"], e.get("params", {})
        if m == "Network.requestWillBeSent":
            urls[p["requestId"]] = p["request"]["url"]
        elif m == "Network.responseReceived" and p["response"]["status"] >= 400:
            out.append("HTTP %d  %s" % (p["response"]["status"], p["response"]["url"]))
        elif m == "Network.loadingFailed" and not p.get("canceled") and p.get("errorText") != "net::ERR_ABORTED":
            out.append("%s  %s" % (p.get("errorText"), urls.get(p["requestId"], "?")))
        elif m == "Runtime.exceptionThrown":
            d = p["exceptionDetails"]
            out.append("uncaught  " + (d.get("exception", {}).get("description") or d.get("text", "")).splitlines()[0])
        elif m == "Runtime.consoleAPICalled" and p["type"] in ("error", "assert"):
            out.append("console.error  " + " ".join(str(a.get("value", a.get("description", ""))) for a in p["args"])[:200])
    return [x for x in dict.fromkeys(out) if not any(n in x for n in NOISE)]


def page_urls():
    return [url for _, url in cdp.pages()]


def interactions(base, fails):
    """Behaviour, on desktop in light mode."""
    def expect(b, js, what):
        try:
            ok = b.eval(js)
        except RuntimeError as err:
            ok = False
            what += " (%s)" % err
        if not ok:
            fails.append("[interaction] " + what)

    with cdp.Browser(scheme="light", **cdp.DESKTOP) as b:
        b.goto(base + "/", settle=1.0)
        b.eval("document.getElementById('theme').click()")
        b.pump(1.0)
        expect(b, "document.documentElement.dataset.theme === 'dark' && localStorage.getItem('theme') === 'dark'", "theme button switches to dark and stores it")
        b.goto(base + "/projects/", settle=1.0)
        expect(b, "document.documentElement.dataset.theme === 'dark'", "stored theme carries to the next page")
        b.eval("localStorage.removeItem('theme')")

        b.goto(base + "/", settle=1.0)
        b.eval("document.querySelector('[data-preview][href=\"publications/\"]').click()")
        b.pump(2.0)
        expect(b, "location.pathname === '/publications/'", "a home tile opens its page (with the tile-to-hero transition)")
        b.eval("history.back()")
        b.pump(2.0)
        expect(b, "location.pathname === '/' && document.querySelectorAll('[style*=\"view-transition-name\"]').length === 0", "back on home, no tile keeps a transition name")

        expect(b, "document.querySelectorAll('.tl-item').length > 4 && [...document.querySelectorAll('.tl-item')].filter((li) => li.checkVisibility()).length === 4", "news starts collapsed to the latest 4 items")
        b.eval("document.querySelector('.news-toggle').click()")
        expect(b, "[...document.querySelectorAll('.tl-item')].every((li) => li.checkVisibility()) && document.querySelector('.news-toggle').getAttribute('aria-expanded') === 'true'", "See all expands every news item")
        b.eval("document.querySelector('.filter[data-filter=\"talk\"]').click()")
        expect(b, "[...document.querySelectorAll('.tl-item')].every((li) => li.hidden === (li.dataset.kind !== 'talk')) && document.querySelector('.tl-year[data-year=\"2026\"]').hidden", "a news filter shows only its kind (and the years that have it)")
        b.eval("document.querySelector('.filter[data-filter=\"\"]').click()")
        expect(b, "[...document.querySelectorAll('.tl-item, .tl-year')].every((li) => !li.hidden)", "All shows every news item again")

        b.goto(base + "/publications/", settle=1.0)
        b.eval("document.querySelector('.zoom').click()")
        b.pump(0.5)
        expect(b, "document.getElementById('lightbox').open && !!document.querySelector('#lightbox-plate img')", "Enlarge opens the figure lightbox")
        b.eval("document.getElementById('lightbox-close').click()")
        b.pump(0.5)
        expect(b, "!document.getElementById('lightbox').open", "lightbox closes")

        b.goto(base + "/gallery/", settle=1.0)
        b.eval("document.querySelector('a[data-yt]').click()")
        b.pump(0.5)
        expect(b, "!!document.querySelector('iframe.yt[src*=\"youtube-nocookie.com/embed/\"]')", "a video plays in place")

        b.goto(base + "/projects/#xc2064-fpga-design", settle=2.0)
        expect(b, "(() => { const r = document.getElementById('xc2064-fpga-design').getBoundingClientRect(); return r.top >= 0 && r.top < 200; })()", "a deep link scrolls to its project")
        fails += ["[interaction] " + x for x in event_problems(b.events)]

    with cdp.Browser(**cdp.DESKTOP) as b:  # without JavaScript the content is all there
        b.cmd("Emulation.setScriptExecutionDisabled", value=True)
        for url in page_urls():
            b.goto(base + url, settle=0.3)
            expect(b, "document.querySelector('main').innerText.length > 300 || document.querySelector('main').children.length > 0", "%s renders without JavaScript" % url)
            expect(b, "[...document.querySelectorAll('[data-js]')].every((e) => !e.checkVisibility())", "%s hides JS-only buttons without JavaScript" % url)


def main():
    server, base = cdp.serve()
    urls = page_urls()
    if not urls:
        sys.exit("public/ is empty: run python3 build.py first")
    fails, warns, links, ids = [], [], set(), {}
    for scheme in ("light", "dark"):
        for label, vp in (("desktop", cdp.DESKTOP), ("phone", cdp.MOBILE)):
            with cdp.Browser(scheme=scheme, **vp) as b:
                for url in urls:
                    tag = "[%s %s] %s" % (label, scheme, url)
                    b.goto(base + url, settle=0.8)
                    r = b.eval(PAGE_JS)
                    fails += ["%s: %s" % (tag, f) for f in r["fails"]]
                    if label == "phone":
                        warns += ["%s: %s" % (tag, w) for w in r["warns"]]
                    if r.get("overflow"):
                        (fails if label == "phone" else warns).append("%s scrolls sideways: %s" % (tag, r["overflow"]))
                    if r["theme"] != scheme:
                        fails.append("%s: theme is %s, system is %s" % (tag, r["theme"], scheme))
                    links.update(r["links"])
                    ids[url] = set(r["ids"])
                fails += ["[%s %s] %s" % (label, scheme, x) for x in event_problems(b.events)]

    # Internal links must land on a page, and #anchors on an element.
    for link in sorted(links):
        if not link.startswith(base):
            continue
        u = urllib.parse.urlparse(link)
        if u.path.endswith("/") and u.path not in ids and not (cdp.PUBLIC / u.path.lstrip("/") / "index.html").is_file():
            fails.append("link to a missing page: " + link[len(base):])
        elif not u.path.endswith("/") and not (cdp.PUBLIC / u.path.lstrip("/")).is_file():
            fails.append("link to a missing file: " + link[len(base):])
        elif u.fragment and u.fragment not in ids.get(u.path, set()):
            fails.append("link to a missing anchor: " + link[len(base):])

    interactions(base, fails)

    fails, warns = list(dict.fromkeys(fails)), list(dict.fromkeys(warns))
    print("checked %d pages x 2 viewports x 2 themes, %d internal links" % (len(urls), sum(1 for l in links if l.startswith(base))))
    for w in warns:
        print("WARN  " + w)
    for f in fails:
        print("FAIL  " + f)
    print("RESULT: %s (%d failure(s), %d warning(s))" % ("FAIL" if fails else "PASS", len(fails), len(warns)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
