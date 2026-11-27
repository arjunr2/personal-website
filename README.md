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

Every list-like page is one YAML file in `content/`: page settings at the top, then an `items:` list,
one entry per paper, role, project or tile, shown in the order they appear in the file.
Each file starts with a comment listing the fields it understands.

| What | Where |
|---|---|
| Name, nav bar order, social links (under the biography), news tags | `site.yml` |
| Home: biography (the body: `## Headline` lines, each followed by a subline), photo, role/PhD cards, CV/resume PDFs (`resources:`) | `content/index.md` |
| News | `content/news.yml` |
| Publications | `content/publications.yml` |
| Career: industry roles, teaching, certificates | `content/career.yml` |
| Projects (Build Hub) | `content/projects.yml` |
| Gallery tiles | `content/gallery.yml` |
| Images, PDFs, CNAME, favicon | `static/` (copied as-is: `static/assets/x.png` is served at `/assets/x.png`) |
| CV and resume PDFs (kept in the repo, not published on the site) | `cv/` |
| Layout and look | `templates/<page>.html` (named after the content file), `static/style.css`, `static/site.js` |

**Text.** An item's `text:` is Markdown (its abstract, bullet list or hover text). For more than one line,
write `text: |` and indent the lines under it:

```yaml
    text: |
      * First bullet
          * A sub-bullet

      A second paragraph with a [link](https://example.com).
```

Paths and links that start with `/` are site paths (`/assets/...`, `/projects/#rtos-design`);
the build makes them relative, so the site also works under a sub-folder (the CMU copy).
Short fields such as captions, link labels and news text may use inline Markdown (`*em*`, `**bold**`, `[link](https://...)`).
Quote a YAML value that starts with `*`, `[` or `{`, or contains `: ` or a comma inside `{ ... }`.

**Order.** Items appear in file order: move an entry up or down to reorder it. News is newest first.

**Anchors.** An item's `id:` is its link (`/projects/#rtos-design`). Without one, it is made from the title.

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

Add an entry to `items:` in `content/publications.yml`, where you want it in the list:

```yaml
  - id: mypaper
    title: My New Paper
    authors: [Arjun Ramesh, Some Coauthor]
    figure: { src: /assets/pubs/MyPaper.svg, alt: What the figure shows }
    links:
      - { label: ASPLOS 2027, icon: acm, url: "https://doi.org/..." }
      - { label: Code, icon: github, url: "https://github.com/..." }
    text: |
      One paragraph of abstract.
```

## Add a project

Add an entry to `items:` in `content/projects.yml`:

```yaml
  - id: my-project
    title: "My Project: Hackathon 2027"
    team: Team of 3          # or Solo
    image: { src: /assets/projects/MyProject.jpg, alt: The prototype }
    image_style: photo       # optional: photo fills its box; plate (default) shows a logo on white
    links:
      - { label: Code, icon: github, url: "https://github.com/..." }
    text: |
      * What it does
          * A detail
```

Optional layout keys: `size: [7, 6]` (tile width in columns: of 12 on desktop, of 6 on tablet;
default `[4, 3]`), `image_beside: true` (image left of the text), `zoom: 1.1` (crop into a photo).

## Add a role

Add an entry to `items:` in `content/career.yml`:

```yaml
  - id: vectorware
    org: VectorWare
    role: Software Engineer
    location: Pittsburgh, PA
    current: true            # optional: a "Present" badge
    logo: { src: /assets/experience/Vectorware.png, alt: VectorWare logo }
    stack:
      - { icon: code, tags: [Rust, CUDA] }
    text: |
      * What I worked on
```

Optional `size: [7, 6]` as for projects. Teaching and certificates are the `teaching:` and `certificates:` lists in the same file.

## Add a gallery tile

Add an entry to `items:` in `content/gallery.yml`:

```yaml
  - title: Cycling
    caption: Climbing absurd gradients
    image: { src: /assets/hobbies/Cycling.jpg, alt: At the top of a climb }
    text: |
      The longer story, shown over the picture on hover.
```

Use `icon: bike` instead of `image:` for a tile without a photo, `plate: true` for a small graphic
(shown on a card), or `videos: [{ title: ..., url: "https://www.youtube.com/watch?v=..." }]` for YouTube
videos (several share one wider tile).

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
A page uses `templates/<name>.html` if one exists; set `template:` to pick another layout.

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
