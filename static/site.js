// Behaviour only: every page is complete HTML without this file.
(() => {
  "use strict";
  const root = document.documentElement;
  const $ = (sel) => document.querySelector(sel);
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");

  /* Same-page view transition; `kind` lets the CSS pick an animation. */
  let token = 0;
  function transition(update, kind) {
    if (!document.startViewTransition || reducedMotion.matches) return update();
    const mine = ++token;
    if (kind) root.dataset.vt = kind;
    else delete root.dataset.vt;
    const vt = document.startViewTransition(update);
    vt.ready.catch(() => {});
    vt.finished.finally(() => { if (mine === token) delete root.dataset.vt; });
  }

  /* ── Theme: stored choice, else the system's (set before paint by the script in <head>) ── */
  const themeBtn = $("#theme");
  const stored = () => { try { return localStorage.getItem("theme"); } catch (err) { return null; } };
  const syncTheme = () => themeBtn.setAttribute("aria-label", root.dataset.theme === "dark" ? "Switch to light theme" : "Switch to dark theme");
  const setTheme = (t) => { root.dataset.theme = t; syncTheme(); };
  syncTheme();
  themeBtn.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem("theme", next); } catch (err) {}
    const r = themeBtn.getBoundingClientRect();
    root.style.setProperty("--tx", r.left + r.width / 2 + "px");
    root.style.setProperty("--ty", r.top + r.height / 2 + "px");
    transition(() => setTheme(next), "theme");
  });
  const systemDark = matchMedia("(prefers-color-scheme: dark)");
  systemDark.addEventListener("change", (ev) => { if (!stored()) setTheme(ev.matches ? "dark" : "light"); });

  /* ── Tile-to-page morph (cross-document view transition) ──
   * A page's hero is always named "hero"; on the home page, the tile for the page being opened
   * takes the name for the swap. The arriving side is handled in <head> (it must run before paint). */
  const previews = [...document.querySelectorAll("[data-preview]")];
  addEventListener("pageswap", (ev) => {
    if (!ev.viewTransition || !ev.activation || !ev.activation.entry.url) return;
    const path = new URL(ev.activation.entry.url).pathname;
    const tile = previews.find((a) => new URL(a.href).pathname === path);
    if (tile) tile.style.viewTransitionName = "hero";
  });
  addEventListener("pageshow", (ev) => {
    if (!ev.persisted) return;
    // Back from the cache: drop the name given at pageswap, and pick up a theme chosen elsewhere.
    previews.forEach((a) => (a.style.viewTransitionName = ""));
    const t = stored();
    setTheme(t === "light" || t === "dark" ? t : systemDark.matches ? "dark" : "light");
  });

  /* ── Keep the active page visible in the scrolling nav (tablet / phone) ── */
  const navList = $(".nav ul"), active = $('.nav a[aria-current="page"]');
  if (active && navList.scrollWidth > navList.clientWidth)
    navList.scrollLeft = active.offsetLeft - (navList.clientWidth - active.offsetWidth) / 2;

  /* ── Highlight the tile a #link points at ── */
  const target = () => {
    let id = location.hash.slice(1);
    try { id = decodeURIComponent(id); } catch (err) {}
    const el = id && document.getElementById(id);
    return el && el.matches(".tile, .group") ? el : null;
  };
  let flashTimer = 0;
  function flash() {
    const el = target();
    if (!el) return;
    document.querySelectorAll(".is-target").forEach((n) => n.classList.remove("is-target"));
    void el.offsetWidth; // restart the animation
    el.classList.add("is-target");
    clearTimeout(flashTimer);
    flashTimer = setTimeout(() => el.classList.remove("is-target"), 2200);
  }
  addEventListener("hashchange", flash);
  flash();
  // Web fonts and images can move a deep-linked tile after the first scroll: settle on it again.
  if (target()) {
    let moved = false;
    for (const ev of ["wheel", "touchstart", "keydown"]) addEventListener(ev, () => (moved = true), { once: true, passive: true });
    const settle = () => { const el = target(); if (el && !moved) el.scrollIntoView({ behavior: "instant" }); };
    if (document.fonts) document.fonts.ready.then(settle);
    addEventListener("load", settle);
  }

  /* ── News: a scrolling list inside its tile on wide screens ── */
  const newsScroll = $(".news-scroll");
  if (newsScroll) {
    const newsTile = newsScroll.closest(".tile");
    const syncNews = () => {
      const scrolls = newsScroll.scrollHeight > newsScroll.clientHeight + 2;
      // Only a scrolling list needs to be a named, focusable stop.
      for (const [k, v] of [["tabindex", "0"], ["role", "group"], ["aria-labelledby", "news-h"]]) {
        if (scrolls) newsScroll.setAttribute(k, v);
        else newsScroll.removeAttribute(k);
      }
      newsTile.classList.toggle("can-scroll", scrolls);
      newsTile.classList.toggle("at-end", !scrolls || newsScroll.scrollTop + newsScroll.clientHeight >= newsScroll.scrollHeight - 8);
    };
    newsScroll.addEventListener("scroll", syncNews, { passive: true });
    addEventListener("resize", syncNews);
    addEventListener("load", syncNews);
    syncNews();
  }

  /* ── Clicks: figure lightbox, copy email, videos, PDF previews ── */
  const lightbox = $("#lightbox");
  document.addEventListener("click", (ev) => {
    const t = ev.target;

    const fig = lightbox && t.closest(".pub-art, .zoom") && t.closest(".pub-fig");
    if (fig) {
      const img = fig.querySelector("img").cloneNode();
      img.removeAttribute("loading");
      $("#lightbox-plate").replaceChildren(img);
      lightbox.showModal();
      return;
    }
    if (lightbox && (t === lightbox || t.closest("#lightbox-close"))) lightbox.close();

    const copy = t.closest("[data-copy]");
    if (copy && navigator.clipboard) {
      navigator.clipboard.writeText(copy.dataset.copy).then(() => {
        copy.classList.add("done");
        copy.setAttribute("aria-label", "Copied");
        setTimeout(() => { copy.classList.remove("done"); copy.setAttribute("aria-label", "Copy email address"); }, 1600);
      }, () => {});
    }

    const yt = t.closest("a[data-yt]");
    if (yt) {
      ev.preventDefault();
      const f = document.createElement("iframe");
      f.className = "yt";
      f.src = "https://www.youtube-nocookie.com/embed/" + yt.dataset.yt + "?autoplay=1";
      f.title = yt.dataset.title;
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
      f.allowFullscreen = true;
      yt.replaceWith(f);
      return;
    }

    const pdf = t.closest("button[data-pdf]");
    if (pdf) {
      const view = document.getElementById(pdf.getAttribute("aria-controls"));
      const open = pdf.getAttribute("aria-expanded") !== "true";
      transition(() => {
        pdf.setAttribute("aria-expanded", String(open));
        pdf.querySelector("span").textContent = open ? "Hide preview" : "Preview";
        pdf.closest(".res").classList.toggle("is-open", open);
        view.hidden = !open;
        if (open && !view.firstChild) {
          const f = document.createElement("iframe");
          f.src = pdf.dataset.pdf; // loaded only once opened
          f.title = pdf.dataset.title;
          view.append(f);
        }
      });
      return;
    }

    // Re-clicking the link to the current #target still highlights it.
    const a = t.closest('a[href^="#"]');
    if (a && a.hash && a.hash === location.hash) flash();
  });
})();
