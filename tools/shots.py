#!/usr/bin/env python3
"""Screenshot every page of the built site (run `python3 build.py` first).

  python3 tools/shots.py [OUT_DIR] [--only PAGE]   # default OUT_DIR: tools/shots/ (gitignored)

Writes <page>-<desktop|phone>-<light|dark>-NN.png: whole pages, cut into tiles.
"""
import pathlib
import sys

import cdp


def main():
    args = sys.argv[1:]
    only = None
    if "--only" in args:
        i = args.index("--only")
        only = args[i + 1]
        del args[i : i + 2]
    out = pathlib.Path(args[0]) if args else cdp.ROOT / "tools" / "shots"
    pages = cdp.pages()
    server, base = cdp.serve()
    for scheme in ("light", "dark"):
        for label, vp in (("desktop", cdp.DESKTOP), ("phone", cdp.MOBILE)):
            with cdp.Browser(scheme=scheme, **vp) as b:
                for name, url in pages:
                    if only and name != only:
                        continue
                    b.goto(base + url, settle=1.0)
                    b.eval("document.querySelectorAll('img[loading=lazy]').forEach((i) => (i.loading = 'eager'))")
                    b.pump(1.0)
                    height = b.page_height()
                    tile = 1000 if vp["mobile"] else 1500
                    for i in range(min(12, -(-height // tile))):
                        path = out / ("%s-%s-%s-%02d.png" % (name.replace("/", "-"), label, scheme, i + 1))
                        b.screenshot(path, clip=(0, i * tile, vp["width"], min(tile, height - i * tile)))
                    print("%s %s %s: %dpx" % (name, label, scheme, height))


if __name__ == "__main__":
    main()
