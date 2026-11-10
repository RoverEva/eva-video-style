/* Template Gallery: renders templates/catalog.json (one entry per style; built to grow to 100+).
   Category chips + search (state kept in the URL), lazy images, paged rendering. Only status "available" can be chosen
   for rendering ("Use template" → the studio with it preselected); others are Preview only / Coming soon. */
(function () {
  const $ = s => document.querySelector(s);
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "text" ? (e.textContent = v) : e.setAttribute(k, v);
    kids.forEach(k => e.append(k)); return e; };
  const PAGE = 48, API = (window.EVA_API || "").replace(/\/$/, "");
  const BADGE = { available: "Available", preview: "Preview only", soon: "Coming soon" };
  let all = [], cats = [], clips = {}, shown = PAGE;
  const url = new URL(location.href), state = { q: url.searchParams.get("q") || "", cat: url.searchParams.get("cat") || "all" };

  const norm = s => (s || "").toLowerCase().normalize("NFKD");
  const match = (t, q) => !q || norm([t.id, t.name, t.name_cn, t.best_for, ...t.categories.map(c => (cats.find(x => x.id === c) || {}).label)].join(" ")).includes(norm(q));
  const inCat = (t, c) => c === "all" || (c === "available" ? t.status === "available" : t.categories.includes(c));
  const order = (a, b) => (a.status === "available") !== (b.status === "available") ? (a.status === "available" ? -1 : 1)
    : a.status === "available" ? a.launch_order - b.launch_order : a.id.localeCompare(b.id, undefined, { numeric: true });

  function card(t) {
    const tall = t.thumb_aspect === "9:16";
    const media = el("div", { class: "g-media" + (tall ? " tall" : "") });
    if (t.thumb) media.append(el("img", { src: t.thumb, alt: `${t.name} (${t.id}) sample frame`, loading: "lazy", decoding: "async",
                                          width: tall ? "360" : "640", height: tall ? "640" : "360" }));
    else media.append(el("div", { class: "g-ph" }, [el("span", { text: t.id }), el("small", { text: "Preview coming soon" })]));
    media.append(el("span", { class: "g-id", text: t.id }), el("span", { class: "g-badge " + t.status, text: BADGE[t.status] }));
    const body = el("div", { class: "g-body" }, [
      el("h3", {}, [document.createTextNode(t.name), t.name_cn ? el("span", { class: "cn", text: t.name_cn, lang: "zh" }) : ""]),
      el("p", { class: "g-best", text: t.best_for || "Details coming soon." }),
      el("div", { class: "g-tags" }, [...t.aspects.map(a => el("span", { class: "g-tag ar", text: a })),
        ...t.categories.slice(0, 1).map(c => el("span", { class: "g-tag", text: (cats.find(x => x.id === c) || {}).label || c }))])]);
    if (t.note) body.append(el("p", { class: "g-note", text: t.note }));
    const acts = el("div", { class: "g-acts" });
    if (t.status === "available") {
      acts.append(el("a", { class: "btn small", href: `/?tpl=${t.id}#studio`, text: "Use template" }));
      const c = clips[t.id];
      if (c) { const p = el("button", { class: "btn small ghost", type: "button", text: "▶ Preview" }); p.onclick = () => play(t, c); acts.append(p); }
    } else acts.append(el("span", { class: "g-off", text: t.status === "soon" ? "Coming soon" : "Not yet available for rendering" }));
    body.append(acts);
    return el("article", { class: "g-card " + t.status, "data-id": t.id }, [media, body]);
  }

  function play(t, c) {   // full 15 s demo from the signed gallery links (same assets as the studio picker)
    const d = $("#gDlg"), v = d.querySelector("video"); v.src = c.url; d.querySelector("p").textContent = `${t.id} ${t.name} · ${c.aspect}`;
    d.showModal(); v.play().catch(() => {});
    d.querySelector(".btn").onclick = () => { v.pause(); d.close(); };
    d.addEventListener("close", () => v.pause(), { once: true });
  }

  function render() {
    const list = all.filter(t => inCat(t, state.cat) && match(t, state.q)).sort(order);
    const grid = $("#gGrid");
    grid.replaceChildren(...list.slice(0, shown).map(card));
    if (!list.length) grid.append(el("p", { class: "g-empty", text: "No templates match. Try another word or category." }));
    const nAvail = list.filter(t => t.status === "available").length;
    $("#gCount").textContent = `${list.length} template${list.length === 1 ? "" : "s"}` + (list.length ? ` · ${nAvail} available now` : "");
    const more = $("#gMore"); more.hidden = list.length <= shown; more.onclick = () => { shown += PAGE; render(); };
    $("#gCats").querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.cat === state.cat)));
    const u = new URL(location.href); state.q ? u.searchParams.set("q", state.q) : u.searchParams.delete("q");
    state.cat !== "all" ? u.searchParams.set("cat", state.cat) : u.searchParams.delete("cat"); history.replaceState(null, "", u);
  }

  async function main() {
    if (window.EVA && EVA.header) EVA.header();
    let j; try { j = await (await fetch("templates/catalog.json", { cache: "no-cache" })).json(); }
    catch (e) { $("#gGrid").replaceChildren(el("p", { class: "note bad", text: "The gallery could not be loaded. Please refresh." })); return; }
    all = j.templates; cats = j.categories;
    const chips = [{ id: "all", label: "All" }, { id: "available", label: "Available now" },
      ...cats.filter(c => all.some(t => t.categories.includes(c.id)))];
    $("#gCats").replaceChildren(...chips.map(c => { const n = all.filter(t => inCat(t, c.id)).length;
      const b = el("button", { type: "button", "data-cat": c.id }, [document.createTextNode(c.label + " "), el("span", { text: String(n) })]);
      b.onclick = () => { state.cat = c.id; shown = PAGE; render(); }; return b; }));
    const q = $("#gQ"); q.value = state.q; let tm;
    q.addEventListener("input", () => { clearTimeout(tm); tm = setTimeout(() => { state.q = q.value.trim(); shown = PAGE; render(); }, 120); });
    render();
    try {   // optional: the approved 15 s demos of the available templates (signed links); the gallery works without them
      const g = await (await fetch(`${API}/api/v2/gallery`)).json();
      for (const t of g.templates || []) { const a = t.assets["16:9"] || t.assets["9:16"]; if (a && a.full15) clips[t.id] = { url: a.full15.url, aspect: t.assets["16:9"] ? "16:9" : "9:16" }; }
      render();
    } catch (e) {}
  }
  main();
})();
