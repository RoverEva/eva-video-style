/* Template Gallery: renders templates/catalog.json (built for 100+ styles).
   Grid cards = thumbnail + name + status (ID shown small). One filter menu + search, state in the URL.
   Paged: 12 cards on phones, 24 on larger screens, "Load more". Thumbnails lazy-load; demo videos load only when
   the detail modal asks for them. Only status "available" can be chosen for rendering ("Use template" → the studio
   with it preselected, and the studio accepts only the launch templates). */
(function () {
  const $ = s => document.querySelector(s);
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "text" ? (e.textContent = v) : e.setAttribute(k, v);
    kids.forEach(k => k && e.append(k)); return e; };
  const API = (window.EVA_API || "").replace(/\/$/, "");
  const STATUS = { available: "Available", preview: "Preview only", soon: "Coming soon" };
  const pageSize = () => (matchMedia("(max-width: 640px)").matches ? 12 : 24);
  let all = [], cats = [], clips = {}, shown = pageSize();
  const url = new URL(location.href), state = { q: url.searchParams.get("q") || "", cat: url.searchParams.get("cat") || "all" };

  const label = c => (cats.find(x => x.id === c) || {}).label || c;
  const norm = s => (s || "").toLowerCase().normalize("NFKD");
  const match = (t, q) => !q || norm([t.id, t.name, t.name_cn, t.best_for, ...t.categories.map(label)].join(" ")).includes(norm(q));
  const inCat = (t, c) => c === "all" || (c === "available" ? t.status === "available" : t.categories.includes(c));
  const rank = { available: 0, preview: 1, soon: 2 };
  const order = (a, b) => rank[a.status] - rank[b.status] || (a.status === "available" ? a.launch_order - b.launch_order
    : a.id.localeCompare(b.id, undefined, { numeric: true }));

  function thumb(t, cls) {
    const box = el("div", { class: cls + (t.thumb_aspect === "9:16" ? " tall" : "") });
    if (t.thumb) box.append(el("img", { src: t.thumb, alt: "", loading: "lazy", decoding: "async",
      width: t.thumb_aspect === "9:16" ? "360" : "640", height: t.thumb_aspect === "9:16" ? "640" : "360" }));
    else box.append(el("span", { class: "g-ph", text: "Preview coming soon" }));
    return box;
  }

  function card(t) {
    const b = el("button", { type: "button", class: "g-card " + t.status, "data-id": t.id, "aria-label": `${t.name}, ${STATUS[t.status]}. Open details` }, [
      thumb(t, "g-media"), el("span", { class: "g-id", text: t.id }),
      el("span", { class: "g-name", text: t.name }),
      el("span", { class: "g-st " + t.status, text: STATUS[t.status] })]);
    b.onclick = () => open(t);
    return b;
  }

  // detail modal: description, previews (videos only when the person presses play), Use template when available
  function open(t) {
    const d = $("#gDlg"), body = d.querySelector(".gd-body");
    const c = clips[t.id] || {};
    const views = el("div", { class: "gd-views" });
    const aspects = t.status === "available" && Object.keys(c).length ? ["9:16", "16:9"].filter(a => c[a]) : [];
    if (aspects.length) {
      aspects.forEach(a => {
        const v = el("div", { class: "gd-view" + (a === "9:16" ? " tall" : "") });
        const play = el("button", { type: "button", class: "gd-play", "aria-label": `Play the ${a} preview` });
        play.append(el("img", { src: c[a].thumb, alt: "", loading: "lazy" }), el("span", { text: "▶" }));
        play.onclick = () => { const vid = el("video", { src: c[a].video, controls: "", playsinline: "", autoplay: "", preload: "auto" }); v.replaceChildren(vid); vid.play().catch(() => {}); };
        v.append(play); views.append(el("figure", {}, [v, el("figcaption", { text: a === "9:16" ? "Vertical 9:16" : "Horizontal 16:9" })]));
      });
    } else views.append(el("figure", {}, [thumb(t, "gd-view"), el("figcaption", { text: t.thumb ? "Sample frame" : "" })]));
    const acts = el("div", { class: "gd-acts" });
    if (t.status === "available") acts.append(el("a", { class: "btn", href: `/?tpl=${t.id}#studio`, text: "Use template" }));
    else acts.append(el("p", { class: "hint", text: t.status === "soon" ? "Coming soon." : "Preview only — not available for rendering yet." }));
    body.replaceChildren(...[
      el("div", { class: "gd-head" }, [el("h2", { text: t.name }), el("span", { class: "g-st " + t.status, text: STATUS[t.status] })]),
      el("p", { class: "gd-meta", text: [t.id, t.name_cn, t.aspects.join(" · ")].filter(Boolean).join(" · ") }),
      views,
      el("p", { class: "gd-desc", text: t.best_for || "Details coming soon." }),
      t.note ? el("p", { class: "gd-note", text: t.note }) : null,
      t.categories.length ? el("p", { class: "gd-cats", text: t.categories.map(label).join(" · ") }) : null,
      acts].filter(Boolean));
    d.showModal();
  }
  function closeDlg() { const d = $("#gDlg"); d.querySelectorAll("video").forEach(v => { v.pause(); v.removeAttribute("src"); v.load(); }); d.close(); }

  function list() { return all.filter(t => inCat(t, state.cat) && match(t, state.q)).sort(order); }
  function render() {
    const l = list(), grid = $("#gGrid");
    grid.replaceChildren(...l.slice(0, shown).map(card));
    if (!l.length) grid.append(el("p", { class: "g-empty", text: "No templates match. Try another word or filter." }));
    $("#gCount").textContent = `${l.length} template${l.length === 1 ? "" : "s"}` + (l.length > shown ? ` · showing ${shown}` : "");
    const more = $("#gMore"); more.hidden = l.length <= shown;
    $("#gCat").value = state.cat;
    const u = new URL(location.href); state.q ? u.searchParams.set("q", state.q) : u.searchParams.delete("q");
    state.cat !== "all" ? u.searchParams.set("cat", state.cat) : u.searchParams.delete("cat"); history.replaceState(null, "", u);
  }

  async function main() {
    if (window.EVA && EVA.header) EVA.header();
    $("#gDlg .gd-close").onclick = closeDlg;
    $("#gDlg").addEventListener("cancel", e => { e.preventDefault(); closeDlg(); });
    $("#gDlg").addEventListener("click", e => { if (e.target.id === "gDlg") closeDlg(); });   // click on the backdrop
    let j; try { j = await (await fetch("templates/catalog.json", { cache: "no-cache" })).json(); }
    catch (e) { $("#gGrid").replaceChildren(el("p", { class: "note bad", text: "The gallery could not be loaded. Please refresh." })); return; }
    all = j.templates.filter(t => t.status !== "excluded"); cats = j.categories;   // excluded templates (T08) are never shown
    const opts = [{ id: "all", label: "All templates" }, { id: "available", label: "Available now" }, ...cats.filter(c => all.some(t => t.categories.includes(c.id)))];
    $("#gCat").replaceChildren(...opts.map(c => el("option", { value: c.id, text: `${c.label} (${all.filter(t => inCat(t, c.id)).length})` })));
    if (!opts.some(o => o.id === state.cat)) state.cat = "all";
    $("#gCat").onchange = e => { state.cat = e.target.value; shown = pageSize(); render(); };
    const q = $("#gQ"); q.value = state.q; let tm;
    q.addEventListener("input", () => { clearTimeout(tm); tm = setTimeout(() => { state.q = q.value.trim(); shown = pageSize(); render(); }, 150); });
    $("#gMore").onclick = () => { shown += pageSize(); render(); };
    render();
    try {   // the approved demos of the available templates (15-minute signed links); the gallery works without them
      const g = await (await fetch(`${API}/api/v2/gallery`)).json();
      for (const t of g.templates || []) for (const [a, x] of Object.entries(t.assets || {}))
        if (x.full15 && x.thumb) (clips[t.id] = clips[t.id] || {})[a] = { video: x.full15.url, thumb: x.thumb.url };
    } catch (e) {}
  }
  main();
})();
