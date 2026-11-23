# Personal Website

Source for www.arjunramesh.me. Pages are Markdown and small YAML lists; `build.py` turns them
into a static site in `public/` (Python-Markdown + Jinja2 + PyYAML, the same pieces MkDocs uses).

## Preview locally

```shell
pip install -r requirements.txt     # once
python3 build.py --serve            # http://localhost:8000, rebuilds and reloads the page when you save
python3 build.py                    # just build into public/
```

## Where things live

| What | Where |
|---|---|
| Name, nav bar order, social links (under the biography), news tags | `site.yml` |
| Home: biography (the body) and photo | `content/index.md` |
| News | `content/news.yml` |
| Publications | `content/publications/<paper>.md` |
| Industry roles | `content/career/<company>.md`; teaching and certificates: `content/career/index.md` |
| Projects | `content/projects/<project>.md` |
| Hobbies | `content/hobbies/<section>.md` |
| PDFs on the Resources page | `content/resources.md` |
| Images, PDFs, CNAME, favicon | `static/` (copied as-is: `static/assets/x.png` is served at `/assets/x.png`) |
| Layout and look | `templates/*.html`, `static/style.css`, `static/site.js` |

Each content file starts with YAML front matter between `---` lines; the Markdown body below it
is the prose. Paths and links that start with `/` are site paths (`/assets/...`, `/projects/#rtos-design`);
the build makes them relative, so the site also works under a sub-folder (the CMU copy).
Anything with `url:`/`text:` in YAML may use inline Markdown (`*em*`, `**bold**`, `[link](https://...)`).
Quote a YAML value that starts with `*`, `[` or `{`, or contains `: `.

**Order.** Items in a folder are sorted by their `order:` number (smallest first), then by file
name. Leave gaps (10, 20, 30...) so a new item can slot in between, e.g. `order: 5` goes first.
News is listed in file order, newest first.

**Icons.** Wherever a file names an `icon:`, use a name from `templates/icons.json`
(e.g. `github`, `acm`, `arxiv`, `video`, `document`, `paper`, `talk`). Icons are always optional.

## Add a news item

Add an entry at the top of `content/news.yml`:

```yaml
- date: Dec 2026          # "Mon YYYY"
  kind: talk              # the tag and filter; its icon and colour are set under `news_kinds` in site.yml
  text: Invited talk – *My Talk Title* at [Some Venue](https://example.com)
```

## Add a paper

Create `content/publications/<short-name>.md`; the body is the abstract. The author matching
`name` in `site.yml` is highlighted. The first link is shown as the venue; a link without `url`
is a plain badge.

```markdown
---
title: My New Paper
order: 5
authors: [Arjun Ramesh, Some Coauthor]
figure: { src: /assets/pubs/MyPaper.svg, alt: What the figure shows }
links:
  - { label: ASPLOS 2027, icon: acm, url: "https://doi.org/..." }
  - { label: Code, icon: github, url: "https://github.com/..." }
---

One paragraph of abstract.
```

## Add a project

Create `content/projects/<anchor-name>.md` (the file name is its link: `/projects/#<anchor-name>`);
the body is the bullet list.

```markdown
---
title: "My Project: Hackathon 2027"
order: 110
team: Team of 3          # or Solo
image: { src: /assets/projects/MyProject.jpg, alt: The prototype }
image_style: photo       # optional: photo fills its box; plate (default) shows a logo on white
links:
  - { label: Code, icon: github, url: "https://github.com/..." }
---

* What it does
    * A detail
```

Optional layout keys: `size: [7, 6]` (tile width in columns: of 12 on desktop, of 6 on tablet;
default `[4, 3]`), `image_beside: true` (image left of the text), `zoom: 1.1` (crop into a photo).

## Add a role

Create `content/career/<company>.md`; the body is the bullet list.

```markdown
---
org: Vectorware
order: 5
role: Software Engineer
location: Pittsburgh, PA
logo: { src: /assets/experience/Vectorware.png, alt: Vectorware logo }
stack:
  - { icon: code, tags: [Rust, CUDA] }
  - { icon: tools, tags: [LLVM] }
---

* What I worked on
```

Optional `size: [7, 6]` as for projects, and `current: true` for a "Present" badge. Teaching and certificates are lists in `content/career/index.md`.

## Add a page

1. Create `content/<name>.md` (served at `/<name>/`):

   ```markdown
   ---
   title: Talks
   icon: talk          # optional: the icon in the title tile
   accent: hobbies     # optional colour: home, publications, experience, projects, hobbies or resources
   ---

   ## 2026

   Any Markdown: headings, lists, links, images, tables, code, quotes...
   ```

2. Add it to the nav in `site.yml`: `- { label: Talks, url: /talks/ }`

It gets a title tile and the body in a prose tile.
A paragraph that is only a YouTube link becomes a click-to-play video.
To give a page one of the special layouts instead, set `template:` to a file name in `templates/`.

## Deploy

Pushing to `main` runs `.github/workflows/deploy-pages.yml`: it builds the site and force-pushes
`public/` to the `gh-pages` branch with `ghp-import` (as `mkdocs gh-deploy` did), which GitHub Pages serves.
`push_deploy.sh` does the push and then pulls `gh-pages` into the CMU AFS web folder:

```shell
git add ...
git commit ...
./push_deploy.sh
```

## Checks

```shell
python3 build.py
python3 tools/check_content.py   # every word and link of the old MkDocs pages is still on the site
                                 # (reads git main:docs/; once main has moved on, pass the last MkDocs commit: 6ff51a4)
python3 tools/check_site.py      # headless Chrome: every page, desktop + phone, light + dark: errors, images, links, overflow
python3 tools/shots.py           # screenshots of every page into tools/shots/
```

The Chrome tools expect Google Chrome at its default macOS path (or set `CHROME=/path/to/chrome`).
