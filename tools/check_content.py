#!/usr/bin/env python3
"""Check that the built site still says everything the old MkDocs pages said.

  python3 tools/check_content.py [REF]     # REF: git ref holding docs/*.md (default: main)

For each old page (git show REF:docs/<page>.md) the Markdown/HTML syntax is stripped, the text
is cut into runs at every piece of markup, and each run must appear (ignoring case, spacing and
punctuation) in the visible text of the matching built page. Every link, embedded video, PDF and
image of the old pages must also be referenced somewhere in the built site. Exit status 1 if not.
"""
import html.parser
import pathlib
import posixpath
import re
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PAGES = {"index": "/", "pubs": "/publications/", "experience": "/experience/", "projects": "/projects/", "hobbies": "/hobbies/", "resources": "/resources/"}
RENAMED = {"Headshot_Portrait.jpg": "headshot.jpg"}  # the web-optimised copy
# Old links Arjun replaced with newer ones (2026-11-23).
RELINKED = {
    "https://doi.org/10.1145/3689031.3717470": "https://dl.acm.org/doi/epdf/10.1145/3689031.3717470",
    "https://doi.org/10.1145/3720428": "https://dl.acm.org/doi/epdf/10.1145/3720428",
}
# Old text removed on purpose, at Arjun's request (2026-11-23): the contact block, and the
# "Biography" heading on home (it is still the intro's accessible name).
# Also old text Arjun has since rewritten (abstracts, 2026-11-23).
DROPPED = {
    "Webassembly (Wasm) adoption for new domains is often hindered by the lack of standard system interfaces. Kernel interface support in Wasm engines allow numerous languages and applications to target Wasm, including arbitrary high-level Wasm APIs (WASI), driving ISA portability and software safety down to even deeply embedded OS ecosystems",
    "Real-time cyber-physical systems naturally lend themselves to distributed compute, but are often programmed monolithically to curb complexity and safety exploits. Our framework, Silverline, explores programmability and orchestration of distributed applications transparently across wide range of hardware using WebAssembly for lightweight virtualization.",
    "Professional Experience",  # page renamed "Career"
    "Biography", "C/C++", "Python", "Ruby",  # languages dropped from the experience stacks
    "Contact", "Work Address", "CIC 2313E (2nd floor)", "CIC", "2313E", "(2nd floor)", "4720 Forbes Avenue, Pittsburgh, PA 15213", "arjunr2@andrew.cmu.edu"}
SEP = "\x00"


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def strip_markdown(text):
    """(text runs, link targets, image files) of an old MkDocs page."""
    links, images = [], []
    s = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    s = re.sub(r"<(style|script)\b.*?</\1>", " ", s, flags=re.S | re.I)
    links += re.findall(r'\b(?:src|href)="([^"]+)"', s)
    s = re.sub(r"!\[[^\]]*\]\(([^)\s]+)\)", lambda m: images.append(m[1]) or SEP, s)
    s = re.sub(r"\{[^{}\n]*\}", SEP, s)  # attribute lists
    s = re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", lambda m: links.append(m[2]) or SEP + m[1] + SEP, s)
    s = re.sub(r"<[^>]+>", SEP, s)
    s = re.sub(r"&\w+;", " ", s)
    s = re.sub(r":[a-z0-9_]+(?:-[a-z0-9_]+)*:", SEP, s)  # :icon-shortcodes:
    s = re.sub(r"^\s*#+\s*(.*)$", SEP + r"\1" + SEP, s, flags=re.M)  # headings
    s = re.sub(r"^\s*(?:[*-]|>|\?\?\?\s+\w+|---+)\s*", SEP, s, flags=re.M)  # other line-start syntax
    s = re.sub(r"\*+|`|\||\"", SEP, s)
    s = re.sub(r"\n\s*\n", SEP, s)
    runs = [" ".join(r.split()) for r in s.split(SEP)]
    return [r for r in runs if len(norm(r)) > 1], links, images


class Visible(html.parser.HTMLParser):
    """Visible text and every referenced URL of a built page."""

    SKIP = {"script", "style", "svg", "head", "template"}

    def __init__(self):
        super().__init__()
        self.text, self.refs, self.depth = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        for k, v in attrs:
            if v and k in ("href", "src", "data-pdf", "data-yt"):
                self.refs.append(v)

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.depth -= 1

    def handle_data(self, data):
        if not self.depth:
            self.text.append(data)


def built_pages():
    out = {}
    for path in PUBLIC.rglob("index.html"):
        rel = path.parent.relative_to(PUBLIC).as_posix()
        url = "/" if rel == "." else "/" + rel + "/"
        v = Visible()
        v.feed(path.read_text(encoding="utf-8"))
        out[url] = (norm(" ".join(v.text)), {urllib.parse.urljoin("http://site" + url, r) for r in v.refs} | set(v.refs))
    return out


def expected_ref(link):
    """What an old link should have become in the new site, or None to skip it."""
    if link == "#":
        return None  # placeholder: the item has no link
    if link in RELINKED:
        return RELINKED[link]
    m = re.match(r"https://www\.youtube\.com/embed/([\w-]+)", link)
    if m:
        return m[1]  # embedded video: its id
    m = re.match(r"(?:\.\./)*(\w+)\.md/?(#.*)?$", link)
    if m:
        page = PAGES.get(m[1], "/" + m[1] + "/")
        return "http://site" + page + (m[2] or "")
    if not re.match(r"[a-z]+:", link):
        return posixpath.basename(link.split("#")[0])  # a local file
    return link


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    if not PUBLIC.is_dir():
        sys.exit("public/ is missing: run python3 build.py first")
    built = built_pages()
    all_refs = set().union(*(refs for _, refs in built.values()))
    ref_blob = "\n".join(all_refs)
    problems, counts = [], [0, 0, 0]
    for name, url in PAGES.items():
        source = subprocess.run(["git", "show", "%s:docs/%s.md" % (ref, name)], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        runs, links, images = strip_markdown(source)
        text = built[url][0]
        for r in runs:
            if r in DROPPED:
                continue
            counts[0] += 1
            if norm(r) not in text:
                problems.append("%s: text missing from %s: %s" % (name, url, r))
        for link in links:
            want = expected_ref(link)
            if want is None:
                continue
            counts[1] += 1
            if want not in all_refs and not (("/" not in want or want.isalnum()) and want in ref_blob):
                problems.append("%s: link missing: %s (expected %s)" % (name, link, want))
        for src in images:
            counts[2] += 1
            base = posixpath.basename(src)
            if "/" + RENAMED.get(base, base) not in ref_blob:
                problems.append("%s: image missing: %s" % (name, src))
    print("compared %d text runs, %d links, %d images from %d old pages (git %s)" % (*counts, len(PAGES), ref))
    for p in problems:
        print("MISSING  " + p)
    print("RESULT: %s" % ("FAIL" if problems else "PASS (nothing missing)"))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
