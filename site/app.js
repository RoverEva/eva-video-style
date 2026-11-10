/* EVA Video Studio website: home (demos + upload studio) and the private video page. No framework, no build step. */
(function () {
  const API = (window.EVA_API || "").replace(/\/$/, "");
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "text" ? (e.textContent = v) : e.setAttribute(k, v);
    kids.forEach(k => e.append(k)); return e; };
  const TEMPLATES = { T23: "Creative Pop", T21: "Clean & Minimal", T17: "Sci-Fi Network", T02: "Electric Blue", T01: "Bold Lime" };
  const TRACKS = { "bright-pop": "Bright Pop", "calm-lofi": "Calm Lo-fi", "inspire": "Inspire", "luxury-ambient": "Luxury Ambient" };
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  /* ── sign-in (Supabase email link in production; a local stand-in for tests) + account API ── */
  let sb = null;
  if (window.EVA_SUPABASE_URL && window.supabase) sb = window.supabase.createClient(window.EVA_SUPABASE_URL, window.EVA_SUPABASE_ANON, { auth: { persistSession: true, detectSessionInUrl: true } });
  const auth = {
    async token() {
      if (window.EVA_LOCAL_AUTH) { try { return (JSON.parse(store.get("eva:auth") || "null") || {}).access_token || null; } catch (e) { return null; } }
      if (!sb) return null; const { data } = await sb.auth.getSession(); return data.session ? data.session.access_token : null;
    },
    async email() {
      if (window.EVA_LOCAL_AUTH) { try { return (JSON.parse(store.get("eva:auth") || "null") || {}).email || null; } catch (e) { return null; } }
      if (!sb) return null; const { data } = await sb.auth.getSession(); return data.session ? data.session.user.email : null;
    },
    async user() {   // {email, name} of the signed-in user, or null — the session persists across visits
      if (window.EVA_LOCAL_AUTH) { try { const j = JSON.parse(store.get("eva:auth") || "null"); return j && j.access_token ? { email: j.email, name: j.name || "" } : null; } catch (e) { return null; } }
      if (!sb) return null; const { data } = await sb.auth.getSession(); const x = data.session && data.session.user;
      return x ? { email: x.email, name: ((x.user_metadata || {}).display_name || "").trim() } : null;
    },
    async setName(name) {   // optional display name, kept on the Supabase user (no extra table)
      if (window.EVA_LOCAL_AUTH) { const j = JSON.parse(store.get("eva:auth") || "{}"); j.name = name; store.set("eva:auth", JSON.stringify(j)); return; }
      const { error } = await sb.auth.updateUser({ data: { display_name: name } }); if (error) throw new Error(error.message);
    },
    async signIn(email) {
      if (window.EVA_LOCAL_AUTH) { const j = await (await fetch(`${API}/_local_signin?email=${encodeURIComponent(email)}`)).json(); store.set("eva:auth", JSON.stringify(j)); return "signed-in"; }
      if (!sb) throw new Error("Sign-in is not available right now.");
      const { error } = await sb.auth.signInWithOtp({ email, options: { emailRedirectTo: location.href.split("#")[0] } });
      if (error) throw new Error(error.message); return "link-sent";
    },
    async signOut() { if (window.EVA_LOCAL_AUTH) store.set("eva:auth", ""); else if (sb) { let r = null; try { r = await sb.auth.signOut(); } catch (e) {} if (!r || r.error) await sb.auth.signOut({ scope: "local" }); } location.reload(); },
  };
  async function api2(path, body, method) {
    const t = await auth.token(); if (!t) { const e = new Error("Please sign in."); e.status = 401; throw e; }
    const r = await fetch(`${API}/api/v2${path}`, { method: method || (body ? "POST" : "GET"), headers: Object.assign({ authorization: `Bearer ${t}` }, body ? { "content-type": "application/json" } : {}), body: body ? JSON.stringify(body) : undefined });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error(j.error || `Request failed (${r.status})`); e.status = r.status; e.data = j; throw e; }
    return j;
  }
  const fmtDate = s => s ? new Date(s).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }) : "";
  // sign-in panel: shown in place (no redesign: the existing .confirm box style)
  function signInPanel(where, why) {
    const box = el("div", { class: "confirm" }), inp = el("input", { type: "email", placeholder: "you@example.com", "aria-label": "Email", class: "email-in", autocomplete: "email" });
    const b = el("button", { class: "btn", type: "button", text: "Email me a sign-in link" }), m = el("p", { class: "hint", text: "" });
    b.onclick = async () => { if (!/^\S+@\S+\.\S+$/.test(inp.value)) { m.textContent = "Enter your email address."; return; }
      b.disabled = true; try { const r = await auth.signIn(inp.value.trim()); if (r === "signed-in") location.reload(); else m.textContent = "Check your inbox: the link signs you in and brings you back here."; }
      catch (e) { m.textContent = e.message; b.disabled = false; } };
    box.append(el("p", { text: why || "Sign in with your email to save your videos and get 3 free previews." }), el("div", { class: "row" }, [inp, b]), m);
    where.replaceChildren(box); inp.focus();
  }
  // header: My Videos + account menu (avatar with the user's initial → My Account, My Videos, Credits & Billing, Sign Out)
  let ME = null, SIGNED_IN = false;
  const initial = u => ((u && (u.name || u.email)) || "?").trim().charAt(0).toUpperCase() || "?";
  async function header() {
    const nav = document.querySelector(".top nav"); if (!nav) return null;
    if (!nav.querySelector(".mv")) nav.append(el("a", Object.assign({ href: "videos.html", class: "mv", text: "My Videos" },
      /\/videos\.html$/.test(location.pathname) ? { "aria-current": "page" } : {})));
    let acct = nav.querySelector(".acct"); if (!acct) { acct = el("div", { class: "acct" }); nav.append(acct); }
    const u = await auth.user(); SIGNED_IN = !!u;
    ME = null; let meErr = null;
    if (u) { try { ME = await api2("/me"); } catch (e) { meErr = e; if (e.status === 401) SIGNED_IN = false; } }
    if (!SIGNED_IN) { acct.replaceChildren(el("a", { href: "videos.html", class: "signin", text: "Sign in" })); return null; }
    const btn = el("button", { type: "button", class: "avatar", "aria-haspopup": "menu", "aria-expanded": "false", "aria-label": "Account menu", text: initial(u) });
    const menu = el("div", { class: "acctmenu", role: "menu", hidden: "" }, [
      el("div", { class: "who" }, [el("b", { text: u.name || "Your account" }), el("span", { text: u.email || "" }),
        el("span", { class: "bal", text: ME ? `${ME.credits} credits · ${ME.free_left} of ${ME.free_limit || 3} free previews left` : (meErr ? "Balance unavailable right now" : "") })]),
      el("a", { href: "account.html", role: "menuitem", text: "My Account" }),
      el("a", { href: "videos.html", role: "menuitem", text: "My Videos" }),
      el("a", { href: "account.html#billing", role: "menuitem", text: "Credits & Billing" }),
      el("a", { href: "#", role: "menuitem", class: "signout", text: "Sign Out" })]);
    const close = () => { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); };
    btn.onclick = e => { e.stopPropagation(); menu.hidden = !menu.hidden; btn.setAttribute("aria-expanded", String(!menu.hidden)); };
    menu.querySelector(".signout").onclick = e => { e.preventDefault(); auth.signOut(); };
    document.addEventListener("click", e => { if (!acct.contains(e.target)) close(); });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && !menu.hidden) { close(); btn.focus(); } });
    acct.replaceChildren(btn, menu);
    return ME;
  }

  async function call(path, body) {
    const r = await fetch(API + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : {});
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
    return j;
  }

  /* before/after wipe: two synced videos, draggable divider (pointer + keyboard) */
  const WIPES = new Set();
  function wipe(box, demo, opts = {}) {
    box.innerHTML = ""; box.classList.toggle("landscape", !!opts.landscape);
    if (!demo || !demo.ready) { box.append(el("div", { class: "soon", text: demo ? `${demo.title} example coming soon` : "" })); return; }
    const a = el("video", { src: demo.before, muted: "", playsinline: "", loop: "", preload: "auto", "aria-label": "Raw upload" });
    const b = el("video", { src: demo.after, playsinline: "", loop: "", preload: "auto", class: "after", "aria-label": "Edited video" });
    a.muted = true; b.muted = true;
    const knob = el("button", { class: "knob", type: "button", "aria-label": "Move the comparison divider", text: "⇆" });
    const bar = el("div", { class: "bar" }, [knob]);
    const sound = el("button", { class: "tag l", type: "button", text: "Sound off", "aria-pressed": "false" });
    box.append(a, b, bar, sound, el("span", { class: "tag raw", text: "Raw" }), el("span", { class: "tag r", text: "Edited" }));
    const mute = () => { b.muted = true; sound.textContent = "Sound off"; sound.setAttribute("aria-pressed", "false"); };
    box._mute = mute; WIPES.add(box);
    let split = 50; const set = v => { split = Math.max(0, Math.min(100, v)); box.style.setProperty("--split", split + "%"); }; set(50);
    const from = e => { const r = box.getBoundingClientRect(); set(((e.clientX - r.left) / r.width) * 100); };
    box.addEventListener("pointerdown", e => { if (e.target === sound) return; box.setPointerCapture(e.pointerId); from(e); box.onpointermove = from; });
    box.addEventListener("pointerup", () => { box.onpointermove = null; });
    knob.addEventListener("keydown", e => { if (e.key === "ArrowLeft") set(split - 5); if (e.key === "ArrowRight") set(split + 5); });
    sound.addEventListener("click", () => {
      if (!b.muted) return mute();
      WIPES.forEach(x => x !== box && (x.isConnected ? x._mute() : WIPES.delete(x)));   // one comparison with sound at a time
      b.muted = false; sound.textContent = "Sound on"; sound.setAttribute("aria-pressed", "true"); b.play().catch(() => {}); });
    const sync = () => { if (Math.abs(a.currentTime - b.currentTime) > .12) a.currentTime = b.currentTime; };
    b.addEventListener("timeupdate", sync);
    const start = () => { a.play().catch(() => {}); b.play().catch(() => {}); };
    new IntersectionObserver(es => es.forEach(x => x.isIntersecting ? start() : (a.pause(), b.pause()))).observe(box);
  }

  async function home() {
    let cfg = {};
    try { cfg = await (await fetch("demos/demos.json", { cache: "no-cache" })).json(); } catch (e) {}
    let demos = cfg.demos || [];
    const byId = id => demos.find(d => d.id === id), hero = cfg.hero || {};
    // hero: both formats at once, each Raw upload next to the edit rendered from that same upload
    if ($("#heroV")) wipe($("#heroV"), byId(hero.vertical) || demos.find(d => d.ready && !d.hero_only));
    if ($("#heroH")) wipe($("#heroH"), byId(hero.horizontal), { landscape: true });
    demos = demos.filter(d => !d.hero_only);
    const sw = $("#catSwitch"), cp = $("#catPhone");
    demos.forEach((d, i) => {
      const b = el("button", { type: "button", "aria-pressed": String(i === 0) }, [el("b", { text: d.title }), document.createTextNode(d.blurb)]);
      b.onclick = () => { sw.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); wipe(cp, d); };
      sw.append(b);
    });
    wipe(cp, demos[0]);

    // template chips (multi-select) + "let us choose"
    const tc = $("#tplChips");
    // Template Gallery (GET /api/v2/gallery: 15-min signed links to approved assets only). Per card: static WebP for the
    // chosen aspect, ▶ plays the 5 s demo inline (muted), "Full preview" opens the 15 s demo. Selection is the chip.
    // No gallery (API down / assets not published): plain chips, the studio still works.
    let gallery = {};
    const dlg = el("dialog", { class: "tpldlg", "aria-label": "Template preview" });
    const dv = el("video", { controls: "", playsinline: "", preload: "none" });
    const close = el("button", { type: "button", class: "btn ghost", text: "Close" });
    dlg.append(dv, close); document.body.append(dlg);
    close.onclick = () => dlg.close(); dlg.addEventListener("close", () => { dv.pause(); dv.removeAttribute("src"); dv.load(); });
    const aspectNow = () => ($("[name=aspect]:checked") || {}).value || "9:16";
    // only assets made for the chosen aspect: a 9:16 demo is never shown as a 16:9 preview (or the reverse)
    const assetsFor = (id, ar) => { const g = gallery[id]; return (g && g.assets[ar]) || null; };
    const cards = {};
    Object.entries(TEMPLATES).forEach(([id, name], i) => {
      const media = el("div", { class: "tplmedia", hidden: "" });
      const play = el("button", { type: "button", class: "tplplay", "aria-label": `Play the ${name} demo`, "aria-pressed": "false" });
      const full = el("button", { type: "button", class: "tplfull", text: "Full preview", hidden: "" });
      media.append(play);
      const chip = el("label", { class: "chip" }, [el("input", { type: "checkbox", name: "tpl", value: id, ...(i === 0 ? { checked: "" } : {}) }), el("span", { text: name })]);
      const soon = el("div", { class: "tplsoon", hidden: "", text: "" });
      const card = el("div", { class: "tplcard", "data-tpl": id }, [media, soon, chip, full]);
      cards[id] = { card, media, play, full, name, soon };
      tc.append(card);
    });
    const paint = () => {
      const ar = aspectNow();
      Object.entries(cards).forEach(([id, c]) => {
        const a = assetsFor(id, ar);
        const other = gallery[id] && Object.keys(gallery[id].assets).length > 0;   // template in the gallery, not in this aspect yet
        c.media.hidden = !a; c.full.hidden = !(a && a.full15); c.card.classList.toggle("has-media", !!a || other);
        c.soon.hidden = !!a || !other; c.soon.textContent = other && !a ? `${ar} preview coming soon` : "";
        c.media.classList.toggle("wide", ar === "16:9"); c.soon.classList.toggle("wide", ar === "16:9");
        c.play.innerHTML = ""; c.play.setAttribute("aria-pressed", "false");
        if (!a) return;
        const img = el("img", { src: a.thumb.url, alt: `${c.name} template`, loading: "lazy", decoding: "async" });
        c.play.append(img, el("span", { class: "tplbadge", "aria-hidden": "true", text: "▶ 5 s" }));
        c.play.onclick = () => {
          const v = c.play.querySelector("video");
          if (v) { v.remove(); c.play.setAttribute("aria-pressed", "false"); return; }
          document.querySelectorAll(".tplplay video").forEach(x => { x.parentNode.setAttribute("aria-pressed", "false"); x.remove(); });
          const vid = el("video", { src: a.clip5.url, muted: "", autoplay: "", loop: "", playsinline: "", preload: "auto" }); vid.muted = true;
          c.play.append(vid); c.play.setAttribute("aria-pressed", "true"); vid.play().catch(() => {});
        };
        c.full.onclick = () => { if (!a.full15) return; dv.src = a.full15.url; dlg.showModal(); dv.play().catch(() => {}); };
      });
    };
    document.querySelectorAll("[name=aspect]").forEach(r => r.addEventListener("change", paint));
    const loadGallery = () => fetch(`${API}/api/v2/gallery`).then(r => r.ok ? r.json() : null).then(j => {
      if (!j) return; (j.templates || []).forEach(t => { gallery[t.id] = t; }); paint();
      setTimeout(loadGallery, Math.max(60, (j.expires_in || 900) - 60) * 1000);   // signed links last 15 min: refresh before expiry
    }).catch(() => {});
    loadGallery();
    tc.append(el("label", { class: "chip" }, [el("input", { type: "checkbox", name: "tplauto", value: "auto" }), el("span", { text: "Let us choose" })]));
    tc.addEventListener("change", e => { if (e.target.name === "tplauto" && e.target.checked) tc.querySelectorAll("[name=tpl]").forEach(x => x.checked = false);
      if (e.target.name === "tpl" && e.target.checked) $("[name=tplauto]").checked = false; });

    const kc = $("#trackChips");
    Object.entries(TRACKS).forEach(([id, name]) => {
      const au = el("audio", { src: `demos/music/${id}.mp3`, preload: "none" });
      const play = el("button", { type: "button", class: "play", text: "Listen" });
      play.onclick = () => { document.querySelectorAll("audio").forEach(x => x !== au && x.pause()); if (au.paused) { au.currentTime = 0; au.play(); play.textContent = "Stop"; } else { au.pause(); play.textContent = "Listen"; } };
      au.onpause = () => play.textContent = "Listen";
      kc.append(el("div", { class: "row" }, [el("label", { class: "chip" }, [el("input", { type: "checkbox", name: "track", value: id }), el("span", { text: name })]), play, au]));
    });
    $("#musicMode").addEventListener("change", () => { $("#trackPick").hidden = $("[name=music]:checked").value !== "track"; });
    kc.addEventListener("change", e => { const on = kc.querySelectorAll("[name=track]:checked"); if (on.length > 3) { e.target.checked = false; msg("Choose up to three tracks.", true); } });

    // file pick / drop
    let file = null; const drop = $("#drop"), input = $("#file");
    const pick = f => { file = f || null; $("#picked").style.display = file ? "block" : "none"; if (file) $("#picked").textContent = `${file.name} · ${(file.size / 1048576).toFixed(1)} MB`; msg(""); };
    input.onchange = () => pick(input.files[0]);
    async function costLine() {
      const line = $("#costLine"); if (!line) return;
      if (!ME) { line.textContent = "Your first 3 previews are free. Sign in when you're ready."; return; }
      const d = file ? await duration(file) : null; let q = null;
      try { q = await api2(`/quote?duration=${d || 30}`); } catch (e) {}
      if (!q) return;
      line.textContent = ME.free_left > 0 ? `This preview is free (${ME.free_left} of 3 free previews left). Full HD export: ${q.hd} credits.`
        : ME.credits >= q.preview ? `This preview costs ${q.preview} credits (you have ${ME.credits}). Full HD export: ${q.hd} credits.`
        : `This preview costs ${q.preview} credits and you have ${ME.credits}. Top up: $9.99 = 100 credits.`;
      $("#go").textContent = ME.free_left > 0 ? "Make my free preview" : `Make preview · ${q.preview} credits`;
    }
    header().then(costLine); input.addEventListener("change", costLine);
    ["dragover", "dragenter"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add("over"); }));
    ["dragleave", "drop"].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.remove("over"); }));
    drop.addEventListener("drop", e => pick(e.dataTransfer.files[0]));

    const meter = $("#meter"), bar = meter.firstElementChild;
    function msg(t, bad) { const m = $("#msg"); m.textContent = t; m.className = "msg" + (bad ? " err" : ""); }
    const duration = f => new Promise(res => { const v = document.createElement("video"); v.preload = "metadata";
      v.onloadedmetadata = () => { res(v.duration); URL.revokeObjectURL(v.src); }; v.onerror = () => res(null); v.src = URL.createObjectURL(f); });

    $("#studioForm").addEventListener("submit", async e => {
      e.preventDefault();
      if (!file) return msg("Choose a video first.", true);
      const type = file.type || (/\.mov$/i.test(file.name) ? "video/quicktime" : "video/mp4");
      if (!/^video\/(mp4|quicktime)$/.test(type)) return msg("Please upload an MP4 or MOV video.", true);
      if (file.size > 200 * 1048576) return msg("This video is larger than 200 MB. Trim or compress it, then try again.", true);
      const d = await duration(file);
      if (d && d > 30.5) return msg(`This video is ${Math.round(d)} seconds long. The limit is 30 seconds.`, true);
      const auto = $("[name=tplauto]").checked, tpls = [...document.querySelectorAll("[name=tpl]:checked")].map(x => x.value);
      if (!auto && !tpls.length) return msg("Choose a visual style, or Let us choose.", true);
      const music = $("[name=music]:checked").value, tracks = [...document.querySelectorAll("[name=track]:checked")].map(x => x.value);
      if (music === "track" && !tracks.length) return msg("Choose at least one track, or pick AI Auto Mix.", true);
      const opts = { aspect: $("[name=aspect]:checked").value, templates: tpls, template_mode: auto ? "auto" : tpls.length > 1 ? "multi" : "single", music, music_tracks: tracks };
      const go = $("#go");
      if (!(await auth.token())) { signInPanel($("#signinBox"), "Sign in with your email to make your preview. Your first 3 previews are free."); return; }
      go.disabled = true;
      try {
        msg("Uploading…"); const up = await api2("/projects", { name: file.name.replace(/\.[^.]+$/, ""), size: file.size, type, duration: d || null });
        up.job = up.project;
        meter.style.display = "block";
        await new Promise((res, rej) => { const x = new XMLHttpRequest(); x.open("PUT", up.put_url); x.setRequestHeader("Content-Type", up.put_type);
          x.upload.onprogress = p => { if (p.lengthComputable) { bar.style.width = (100 * p.loaded / p.total).toFixed(0) + "%"; msg(`Uploading… ${Math.round(100 * p.loaded / p.total)}%`); } };
          x.onload = () => x.status < 300 ? res() : rej(new Error("The upload was interrupted. Please try again."));
          x.onerror = () => rej(new Error("The upload was interrupted. Please try again.")); x.send(file); });
        msg("Starting your preview…");
        const r = await api2(`/projects/${up.project}/previews`, opts);
        location.href = `video.html?v=${r.version}`;
      } catch (err) {
        if (err.status === 402) { msg(err.message, true); showTopup($("#signinBox"), "/videos.html"); }
        else msg(err.message, true);
        go.disabled = false; meter.style.display = "none"; }
    });
  }

  function showTopup(where, returnTo, why) {
    const b = el("button", { class: "btn", type: "button", text: "Top up $9.99 · 100 credits" });
    b.onclick = async () => { b.disabled = true; try { location.href = (await api2("/topup", { return_to: returnTo || (location.pathname + location.search) })).url; } catch (e) { b.disabled = false; alertMsg(where, e.message); } };
    where.replaceChildren(el("div", { class: "confirm" }, [el("p", { text: why || "Credits pay for previews after your free ones (12–15 credits) and full HD exports (38–52 credits). Secure checkout by Stripe." }), el("div", { class: "row" }, [b])]));
  }
  const alertMsg = (where, t) => where.append(el("p", { class: "note bad", text: t }));

  /* private video page: real backend progress, preview, regenerate, checkout, HD download. Survives refreshes: all
     state comes from the API; the private token is kept in this browser (and in the link). */
  async function video() {
    const q = new URLSearchParams(location.search), id = q.get("id");
    const hashT = new URLSearchParams(location.hash.slice(1)).get("t"); if (hashT) store.set("eva:" + id, hashT);
    const token = hashT || store.get("eva:" + id), vparam = q.get("v");
    const root = $("#job");
    if (!vparam && (!id || !token)) { root.innerHTML = "<div><h1>We can't find this video</h1><p>Open the link from the device you uploaded on, or from your payment email.</p><a class='btn' href='/#studio'>Make a new video</a></div>"; return; }
    const phone = $("#jobPhone"), h1 = $("#jobTitle"), sub = $("#jobSub"), steps = $("#jobSteps"), act = $("#jobAction");
    const prog = $("#jobProg"), pctEl = $("#jobPct"), bar = $("#jobBar"), note = $("#jobProgNote");
    let shownSrc = null, payBusy = false, regenBusy = false, confirmOpen = false, timer = null, playable = false, seen = { key: "", pct: 0 };
    let loop = () => tick();   // the account page swaps in its own poller
    const again = ms => { clearTimeout(timer); timer = setTimeout(() => loop(), ms); };

    // progress: the number is the backend's; it never moves backwards within one render and only reads 100% once the
    // video can actually play in this browser
    function setProgress(key, pct, opts = {}) {
      if (key !== seen.key) seen = { key, pct: 0 };
      seen.pct = Math.max(seen.pct, Math.min(99, pct | 0));
      const shown = opts.playable ? 100 : seen.pct;
      prog.hidden = false; prog.classList.toggle("idle", !!opts.playable); prog.classList.toggle("stopped", !!opts.stopped);
      pctEl.textContent = shown + "%"; bar.firstElementChild.style.width = shown + "%";
      bar.setAttribute("aria-valuenow", String(shown)); bar.setAttribute("aria-valuetext", `${shown}% ${opts.label || ""}`.trim());
      note.textContent = opts.note || "";
    }
    const stageList = list => { steps.innerHTML = ""; (list || []).forEach(s => steps.append(el("li", { class: s.status === "active" ? "now" : s.status, text: s.label }))); };
    const loading = (text, landscape) => { if (shownSrc === "loading:" + text) return; shownSrc = "loading:" + text; playable = false;
      phone.innerHTML = ""; phone.classList.toggle("landscape", landscape); phone.classList.add("loading");
      phone.append(el("div", { class: "soon", text })); };
    const show = (src, landscape, onPlayable) => {
      if (src === shownSrc) return; shownSrc = src; playable = false;
      const vid = Object.assign(el("video", { src, controls: "", playsinline: "", loop: "", muted: "" }), { autoplay: true, muted: true });
      vid.addEventListener("loadeddata", () => { playable = true; phone.classList.remove("loading"); onPlayable && onPlayable(); }, { once: true });
      vid.onerror = () => { shownSrc = null; again(500); };   // expired 15-minute signed link: fetch a fresh one
      phone.classList.toggle("landscape", landscape); phone.replaceChildren(vid);
    };

    if (vparam) { header(); const k = $("#jobKeep"); if (k) k.textContent = "Saved privately in My Videos. Previews and your original upload are kept for 30 days, HD exports for 90 days."; return accountPage(vparam); }

    /* account version page (My Videos): preview / HD export of one saved version */
    function accountPage(vid) {
      let confirmFor = null, busy = false;
      const confirmBox = (text, yesLabel, onYes) => {
        const yes = el("button", { class: "btn", type: "button", text: yesLabel }), no = el("button", { class: "btn ghost", type: "button", text: "Cancel" });
        no.onclick = () => { confirmFor = null; atick(); };
        yes.onclick = async () => { if (busy) return; busy = true; yes.disabled = no.disabled = true; yes.textContent = "Starting…";
          try { await onYes(); } catch (e) { if (e.status === 402) { confirmFor = null; busy = false; return showTopup(act, location.pathname + location.search, e.message); } sub.textContent = e.message; }
          busy = false; confirmFor = null; shownSrc = null; atick(); };
        return el("div", { class: "confirm" }, [el("p", { text }), el("div", { class: "row" }, [yes, no])]);
      };
      async function atick() {
        let v; try { v = await api2(`/versions/${vid}`); }
        catch (e) { if (e.status === 401) { h1.textContent = "Sign in to see this video"; return signInPanel(act); }
                    if (e.status === 404) { h1.textContent = "We can't find this video"; sub.textContent = "It may have been deleted or have expired."; return; }
                    note.textContent = "Connection problem. Retrying…"; return again(8000); }
        const me = await header(); const land = (v.options || {}).aspect === "16:9"; act.innerHTML = "";
        if (q.get("topup") === "done") act.append(el("p", { class: "note", text: `Payment received. Your balance: ${me ? me.credits : "…"} credits.` }));
        if (q.get("topup") === "canceled") act.append(el("p", { class: "note", text: "Checkout was canceled. You haven't been charged." }));
        const tpl = (v.templates || []).join(" + "), until = v.expires_at ? ` Kept until ${fmtDate(v.expires_at)}.` : "";
        const running = s => s === "queued" || s === "running", hd = v.kind === "hd" ? v : v.hd;
        if (running(v.status)) {
          h1.textContent = v.kind === "hd" ? "Rendering your HD video" : `Making preview ${v.n}`;
          sub.textContent = `${v.project_title || ""} · ${tpl}. This usually takes ${v.kind === "hd" ? "a few" : "2–4"} minutes; you can leave and come back from My Videos.`;
          setProgress(vid, (v.progress || {}).progress || 0, { label: "rendering", note: (v.progress || {}).stalled ? "This is taking longer than usual. If it can't finish, nothing is charged." : "" });
          stageList((v.progress || {}).stages); loading(v.kind === "hd" ? "Rendering in full HD…" : "Rendering your preview…", land);
          const c = el("button", { class: "btn ghost", type: "button", text: "Cancel" });
          c.onclick = async () => { c.disabled = true; try { await api2(`/versions/${vid}/cancel`, {}); } catch (e) {} atick(); };
          act.append(c, el("a", { class: "btn ghost", href: "videos.html", text: "My Videos" })); return again(3000);
        }
        if (v.status !== "done") {
          h1.textContent = v.status === "canceled" ? "This render was canceled" : "This render didn't finish";
          sub.textContent = (v.status === "qa_failed" ? "It didn't pass our quality checks. " : v.status === "canceled" ? "" : "Something went wrong on our side. ") + "Nothing was charged: free previews and credits were returned.";
          setProgress(vid, 0, { stopped: true }); stageList([]); loading("Not available", land); phone.classList.remove("loading");
          act.append(el("a", { class: "btn", href: "videos.html", text: "Back to My Videos" })); return;
        }
        // done
        if (v.kind === "hd") {
          h1.textContent = "Your HD video is ready";
          sub.textContent = `${v.project_title || ""} · version ${v.n} · ${tpl}. Full HD ${(v.report || {}).width}×${(v.report || {}).height}.${until} Downloading again is free.`;
        } else {
          h1.textContent = `Preview ${v.n} is ready`;
          sub.textContent = `${v.project_title || ""} · ${tpl}. First 10 seconds with a watermark.${until}`;
        }
        show(v.video_url, land, () => setProgress(vid, 100, { playable: true, label: "ready" }));
        setProgress(vid, 99, { playable, label: "ready", note: playable ? "" : "Loading…" }); stageList([]);
        const credits = me ? me.credits : 0;
        if (hd && hd.status === "done") {
          const dl = el("a", { class: "btn", href: hd.download_url || "#", text: "Download HD" });
          dl.onclick = async e => { e.preventDefault(); try { location.href = (await api2(`/versions/${hd.id}`)).download_url; } catch (err) { sub.textContent = err.message; } };
          act.append(dl);
          if (v.kind === "preview") act.append(el("a", { class: "btn ghost", href: `video.html?v=${hd.id}`, text: "Play HD" }));
        } else if (hd && running(hd.status)) {
          act.append(el("a", { class: "btn", href: `video.html?v=${hd.id}`, text: "HD export in progress…" }));
        } else if (v.kind === "preview") {
          const cost = v.hd_cost;
          if (confirmFor === "hd") act.append(confirmBox(credits >= cost ? `Export this version in full 1080p for ${cost} credits? You have ${credits}; ${credits - cost} will be left. If the export fails, the credits come back.`
            : `Exporting costs ${cost} credits and you have ${credits}.`, credits >= cost ? `Export for ${cost} credits` : "Top up first",
            async () => { if (credits < cost) { const e = new Error(`Exporting costs ${cost} credits and you have ${credits}. Top up to continue.`); e.status = 402; throw e; }
              const r = await api2(`/versions/${vid}/hd`, {}); location.href = `video.html?v=${r.version}`; }));
          else { const b = el("button", { class: "btn", type: "button", text: `Export HD · ${cost} credits` }); b.onclick = () => { confirmFor = "hd"; atick(); }; act.append(b); }
        }
        if (v.kind === "preview") {
          const free = me && me.free_left > 0;
          if (confirmFor === "regen") act.append(confirmBox(free ? `Make a new version from the same upload and settings? It's free (${me.free_left} of 3 free previews left). Your current versions stay in My Videos.`
            : `Make a new version from the same upload and settings for ${v.preview_cost} credits? You have ${credits}. Your current versions stay saved, and if it fails the credits come back.`,
            free || credits >= v.preview_cost ? "Yes, make a new version" : "Top up first",
            async () => { const r = await api2(`/projects/${v.project_id}/previews`, {}); location.href = `video.html?v=${r.version}`; }));
          else { const b = el("button", { class: "btn ghost", type: "button", text: "New version" }); b.onclick = () => { confirmFor = "regen"; atick(); }; act.append(b); }
        }
        act.append(el("a", { class: "btn ghost", href: "videos.html", text: "My Videos" }));
      }
      loop = atick; document.addEventListener("visibilitychange", () => { if (!document.hidden) again(200); });
      atick();
    }

    function regenerateControls(v) {
      const pv = v.preview || {}, failed = pv.state === "failed" || pv.stalled, left = v.previews_left;
      const cost = failed ? "Free, and it doesn't count toward today's free previews." :
        `Free: uses 1 of your 3 free previews today (${left ?? "?"} left).`;
      const btn = el("button", { class: "btn ghost", type: "button", text: "Regenerate preview" });
      if (!failed && left === 0) { btn.disabled = true; btn.title = "You've used today's 3 free previews. They reset at 4 pm Pacific time."; }
      btn.onclick = () => { confirmOpen = true; render(v); };
      if (!confirmOpen) return [btn];
      const yes = el("button", { class: "btn", type: "button", text: "Yes, regenerate" }), no = el("button", { class: "btn ghost", type: "button", text: "Cancel" });
      no.onclick = () => { confirmOpen = false; render(v); };
      yes.onclick = async () => {
        if (regenBusy) return; regenBusy = true; yes.disabled = no.disabled = true; yes.textContent = "Starting…";
        try { await call(`/api/jobs/${id}/regenerate`, { token, n: v.preview_n }); }
        catch (e) { if (!/already being made/i.test(e.message)) sub.textContent = e.message; }   // a duplicate request just keeps polling the running one
        regenBusy = false; confirmOpen = false; shownSrc = null; again(300);
      };
      return [el("div", { class: "confirm" }, [el("p", { text: `Make a new preview from the same upload and settings? ${cost} No payment is taken.` }), el("div", { class: "row" }, [yes, no])])];
    }

    let last = null;
    function render(v) {
      last = v; const land = (v.options || {}).aspect === "16:9", pv = v.preview || {}, fn = v.final || {};
      act.innerHTML = "";
      if (q.get("canceled") && !v.paid) act.append(el("p", { class: "note", text: "Checkout was canceled. You haven't been charged." }));
      if (v.state === "refunded") {
        h1.textContent = "Your payment was refunded"; sub.textContent = "We couldn't render this video, even after retrying. The full amount is on its way back to your card; banks usually show it within 5–10 days.";
        setProgress("final", fn.progress || 0, { stopped: true, label: "refunded" }); stageList(fn.stages); return;
      }
      if (v.paid) {
        if (fn.url) {
          h1.textContent = "Your video is ready";
          sub.textContent = `Full HD, ${fn.width}×${fn.height}, ${Math.round(fn.duration || 0)} seconds. The download link works until ${new Date(fn.expires * 1000).toLocaleDateString()}.`;
          show(fn.url, land, () => setProgress("final", 100, { playable: true, label: "ready" }));
          setProgress("final", 99, { playable, label: "ready", note: playable ? "" : "Loading your video…" });
          const dl = el("a", { class: "btn", href: fn.url, download: `EVA_${id}.mp4`, text: "Download MP4" });
          dl.onclick = async e => { e.preventDefault();   // signed links live 15 minutes: always ask for a fresh one
            try { const f = (await call(`/api/jobs/${id}?t=${encodeURIComponent(token)}`)).final; location.href = f.url; } catch (err) { sub.textContent = err.message; } };
          act.append(dl); stageList(fn.stages); return;
        }
        h1.textContent = "Payment confirmed. Rendering your HD video";
        sub.textContent = "This usually takes a few minutes. You can keep this page open, or come back later with the same link.";
        setProgress("final", fn.progress || 0, { label: "rendering HD",
          note: fn.stalled ? "This is taking longer than usual. We're still on it, and if it can't finish you're refunded automatically." : "" });
        stageList(fn.stages);
        if (pv.url) show(pv.url, land); else loading("Rendering your HD video…", land);
        return again(4000);
      }
      if (pv.state === "rejected") {
        h1.textContent = "This video couldn't be processed"; sub.textContent = pv.error || "Please try another file.";
        setProgress("pv" + v.preview_n, pv.progress || 0, { stopped: true }); stageList(pv.stages);
        act.append(el("a", { class: "btn", href: "/#studio", text: "Upload another video" })); return;
      }
      if (pv.state === "failed") {
        h1.textContent = "Your preview didn't finish"; sub.textContent = "Something went wrong on our side. You can try again with the same video and settings.";
        setProgress("pv" + v.preview_n, pv.progress || 0, { stopped: true, label: "failed" }); stageList(pv.stages);
        loading("Preview not available", land); phone.classList.remove("loading");
        act.append(...regenerateControls(v), el("a", { class: "btn ghost", href: "/#studio", text: "Upload another video" })); return;
      }
      if (pv.url && pv.state === "done") {
        h1.textContent = q.get("paid") ? "Confirming your payment…" : "Your free preview is ready";
        sub.textContent = `This is the first 10 seconds with a watermark. The full video is 1080p, without the watermark, for $${v.price.toFixed(2)}.`;
        show(pv.url, land, () => setProgress("pv" + v.preview_n, 100, { playable: true, label: "ready" }));
        setProgress("pv" + v.preview_n, 99, { playable, label: "ready", note: playable ? "" : "Loading your preview…" });
        stageList(pv.stages);
        const pay = el("button", { class: "btn", type: "button", text: `Get the full video for $${v.price.toFixed(2)}` });
        pay.onclick = async () => { if (payBusy) return; payBusy = true; pay.disabled = true; pay.textContent = "Opening secure checkout…";
          try { location.href = (await call(`/api/jobs/${id}/checkout`, { token })).url; } catch (e) { sub.textContent = e.message; pay.disabled = false; payBusy = false; pay.textContent = `Get the full video for $${v.price.toFixed(2)}`; } };
        act.append(pay, ...(v.can_regenerate ? regenerateControls(v) : []));
        if (v.stripe_mode === "test") act.append(el("p", { class: "note", text: "Test mode: use card 4242 4242 4242 4242, any future date and any CVC. No real money moves." }));
        if (q.get("paid")) return again(2500);
        return;
      }
      // rendering (first preview or a regeneration)
      h1.textContent = v.preview_n ? "Making a new preview" : "Making your preview";
      sub.textContent = "We're listening, planning the cards and rendering. This usually takes 2–4 minutes.";
      setProgress("pv" + v.preview_n, pv.progress || 0, { label: "rendering preview",
        note: pv.stalled ? "This is taking longer than usual. You can wait, or start again for free." : "" });
      stageList(pv.stages); loading("Rendering your preview…", land);
      if (pv.stalled && v.can_regenerate) act.append(...regenerateControls(v));
      again(3000);
    }

    async function tick() {
      let v; try { v = await call(`/api/jobs/${id}?t=${encodeURIComponent(token)}`); }
      catch (e) { note.textContent = "Connection problem. Retrying…"; return again(8000); }
      render(v);
    }
    document.addEventListener("visibilitychange", () => { if (!document.hidden) again(200); });   // refresh promptly when the tab returns
    tick();
  }

  /* My Videos: projects → versions (previews + HD exports), private to the signed-in account */
  async function videos() {
    const list = $("#libList"), noteBox = $("#libNote"), q = new URLSearchParams(location.search);
    const me = await header();
    if (!me && SIGNED_IN) {   // signed in, but the account service did not answer: say so instead of asking to sign in again
      $("#libSub").textContent = "We couldn't load your videos right now.";
      const r = el("button", { class: "btn ghost", type: "button", text: "Try again" }); r.onclick = () => location.reload();
      return list.replaceChildren(el("p", { class: "note bad", text: "You're signed in, but your videos could not be loaded. Please try again in a moment." }), r);
    }
    if (!me) { $("#libSub").textContent = "Sign in to see your saved videos."; return signInPanel(list, "Sign in with your email to see your videos. New accounts get 3 free previews."); }
    const running = s => s === "queued" || s === "running";
    const pid = q.get("p");
    const dur = s => { s = Math.max(0, Math.round(+s || 0)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };
    const dayKey = d => { const x = new Date(d); return `${x.getFullYear()}-${x.getMonth()}-${x.getDate()}`; };
    const dayLabel = d => { const x = new Date(d), now = new Date();
      return x.toLocaleDateString(undefined, x.getFullYear() === now.getFullYear() ? { month: "short", day: "numeric" } : { month: "short", day: "numeric", year: "numeric" }); };
    // one project = every version made from one upload: previews, HD exports, downloads (the detailed view)
    function project(pr, a) {
        const head = el("div", { class: "proj-head" }, [
          el("div", {}, [el("h2", { text: pr.title }), el("p", { class: "hint", text: `Uploaded ${fmtDate(pr.created_at)}${pr.source_expires_at ? ` · original kept until ${fmtDate(pr.source_expires_at)}` : ""}` })])]);
        const acts = el("div", { class: "row" });
        const nv = el("button", { class: "btn ghost", type: "button", text: a.free_left > 0 ? "New version · free" : `New version · ${pr.costs.preview} credits` });
        nv.onclick = async () => { if (!confirm2(nv, a.free_left > 0 ? `Make a new version from the same upload and settings? Free (${a.free_left} free previews left).` : `Make a new version for ${pr.costs.preview} credits? You have ${a.credits}.`)) return;
          try { const r = await api2(`/projects/${pr.id}/previews`, {}); location.href = `video.html?v=${r.version}`; } catch (e) { noteBox.replaceChildren(el("p", { class: "note bad", text: e.message })); nv.disabled = false; } };
        const dp = el("button", { class: "btn ghost", type: "button", text: "Delete" });
        dp.onclick = async () => { if (!confirm2(dp, `Delete “${pr.title}” and all its versions? This can't be undone.`)) return;
          try { await api2(`/projects/${pr.id}/delete`, {}); location.href = "videos.html"; } catch (e) { noteBox.replaceChildren(el("p", { class: "note bad", text: e.message })); dp.disabled = false; } };
        acts.append(nv, dp); head.append(acts);
        const hdOf = id => pr.versions.find(x => x.kind === "hd" && x.source_version === id && !["failed", "qa_failed", "canceled"].includes(x.status));
        const cards = pr.versions.filter(v => v.kind === "preview").map(v => {
          const hd = hdOf(v.id), card = el("article", { class: "vcard" });
          const thumb = el("a", { class: "vthumb" + ((v.options || {}).aspect === "16:9" ? " wide" : ""), href: `video.html?v=${v.id}`, "aria-label": `Open version ${v.n}` });
          if (v.thumb_url) thumb.append(el("img", { src: v.thumb_url, alt: "", loading: "lazy" }));
          thumb.append(el("span", { class: "vbadge " + v.status, text: running(v.status) ? `${(v.progress || {}).progress || 0}%` : v.status === "done" ? (hd && hd.status === "done" ? "HD" : "Preview") : v.status.replace("_", " ") }));
          const star = el("button", { class: "star" + (v.favorite ? " on" : ""), type: "button", "aria-pressed": String(!!v.favorite), "aria-label": "Favorite", text: v.favorite ? "★" : "☆" });
          star.onclick = async () => { await api2(`/versions/${v.id}/favorite`, { favorite: !v.favorite }); render(); };
          const meta = el("div", { class: "vmeta" }, [el("div", { class: "vtitle" }, [el("b", { text: `Version ${v.n}` }), star]),
            el("div", { class: "hint", text: (v.templates || []).join(" + ") + ` · ${(v.options || {}).aspect}` }),
            el("div", { class: "hint", text: v.status === "done" ? `Preview kept until ${fmtDate(v.expires_at)}` + (hd && hd.status === "done" ? ` · HD until ${fmtDate(hd.expires_at)}` : "") : running(v.status) ? "Rendering…" : "Nothing was charged" })]);
          const row = el("div", { class: "row" });
          if (v.status === "done") {
            row.append(el("a", { class: "btn small", href: `video.html?v=${v.id}`, text: "Play" }));
            if (hd && hd.status === "done") { const d = el("a", { class: "btn small ghost", href: "#", text: "Download HD" });
              d.onclick = async e => { e.preventDefault(); location.href = (await api2(`/versions/${hd.id}`)).download_url; }; row.append(d); }
            else if (hd) row.append(el("a", { class: "btn small ghost", href: `video.html?v=${hd.id}`, text: "HD rendering…" }));
            else row.append(el("a", { class: "btn small ghost", href: `video.html?v=${v.id}`, text: `Export HD · ${pr.costs.hd}` }));
          }
          if (!running(v.status)) { const del = el("button", { class: "btn small ghost", type: "button", text: "Delete" });
            del.onclick = async () => { if (!confirm2(del, `Delete version ${v.n}${hd ? " and its HD export" : ""}?`)) return;
              try { if (hd) await api2(`/versions/${hd.id}/delete`, {}); await api2(`/versions/${v.id}/delete`, {}); render(); } catch (e) { noteBox.replaceChildren(el("p", { class: "note bad", text: e.message })); } };
            row.append(del); }
          card.append(thumb, meta, row); return card;
        });
        return el("section", { class: "proj" }, [head, el("div", { class: "vgrid" }, cards)]);
    }
    // grid: one compact thumbnail per uploaded video, grouped by day (newest first), duration badge only
    const cal = () => { const i = el("span", { class: "cal", "aria-hidden": "true" });
      i.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>'; return i; };
    function tile(pr) {
      const vs = pr.versions, live = vs.find(v => running(v.status));
      const shown = vs.find(v => v.thumb_url && v.status === "done") || vs.find(v => v.thumb_url) || vs[0] || {};
      const wide = ((shown.options || {}).aspect || "9:16") === "16:9";
      const t = el("div", { class: "mvthumb" + (wide ? " wide" : "") });
      if (shown.thumb_url) t.append(el("img", { src: shown.thumb_url, alt: "", loading: "lazy" }));
      else t.append(el("span", { class: "mvph", "aria-hidden": "true" }));
      t.append(el("span", { class: "dur", text: dur(pr.duration_s) }));
      if (live) { const pct = Math.max(4, Math.min(100, (live.progress || {}).progress || 0));
        const bar = el("span", { class: "mvprog", role: "progressbar", "aria-label": "Processing", "aria-valuenow": String(pct), "aria-valuemin": "0", "aria-valuemax": "100" }, [el("i")]);
        bar.firstChild.style.width = pct + "%"; t.append(bar); }
      return el("a", { class: "mvcard", href: `videos.html?p=${encodeURIComponent(pr.id)}`,
        "aria-label": `${pr.title || "Video"}, ${dur(pr.duration_s)}${live ? ", processing" : ""}` }, [t]);
    }
    const render = async () => {
      let data; try { data = await api2("/library"); } catch (e) { list.replaceChildren(el("p", { class: "note bad", text: e.message })); return; }
      const a = data.account;
      if (q.get("topup") === "done") noteBox.replaceChildren(el("p", { class: "note", text: `Payment received. Your balance is ${a.credits} credits.` }));
      if (q.get("topup") === "canceled") noteBox.replaceChildren(el("p", { class: "note", text: "Checkout was canceled. You haven't been charged." }));
      if (pid) {
        const pr = data.projects.find(x => x.id === pid);
        $("#libTitle").textContent = pr ? (pr.title || "Video") : "Video not found";
        $("#libSub").replaceChildren(el("a", { href: "videos.html", text: "← All videos" }));
        if (!pr) { list.replaceChildren(el("p", { class: "note", text: "This video was deleted or isn't in your account." })); return; }
        $("main.library").classList.add("pv"); list.replaceChildren(project(pr, a));
        if (pr.versions.some(v => running(v.status))) setTimeout(render, 4000);
        return;
      }
      if (!data.projects.length) { list.replaceChildren(el("div", { class: "empty" }, [el("p", { text: "No videos yet. Upload a talking-head clip to make your first preview." }), el("a", { class: "btn", href: "/#studio", text: "Make a video" })])); return; }
      const groups = [];
      [...data.projects].sort((x, y) => new Date(y.created_at) - new Date(x.created_at)).forEach(pr => {
        const k = dayKey(pr.created_at), g = groups[groups.length - 1];
        if (g && g.k === k) g.items.push(pr); else groups.push({ k, label: dayLabel(pr.created_at), items: [pr] });
      });
      list.replaceChildren(...groups.map(g => el("section", { class: "mvday" }, [
        el("h2", {}, [cal(), document.createTextNode(g.label + " "),
          el("span", { text: `(${g.items.length} video${g.items.length === 1 ? "" : "s"})` })]),
        el("div", { class: "mvgrid" }, g.items.map(tile))])));
      if (data.projects.some(pr => pr.versions.some(v => running(v.status)))) setTimeout(render, 4000);
    };
    // two-step inline confirm on the same button (no browser dialogs)
    function confirm2(btn, text) {
      if (btn.dataset.armed) { btn.disabled = true; return true; }
      btn.dataset.armed = "1"; const old = btn.textContent; btn.textContent = "Click again to confirm"; btn.title = text;
      noteBox.replaceChildren(el("p", { class: "note", text }));
      setTimeout(() => { delete btn.dataset.armed; btn.textContent = old; }, 5000); return false;
    }
    render();
  }


  /* My Account: who you are, balance, free previews, credit purchases + charges (read-only view of the existing ledger) */
  async function account() {
    const body = $("#acctBody"), q = new URLSearchParams(location.search);
    const me = await header(), u = await auth.user();
    if (!u || (!me && !SIGNED_IN)) return signInPanel(body, "Sign in with your email to see your account. New accounts get 3 free previews.");
    const card = (title, kids, id) => el("section", Object.assign({ class: "acard" }, id ? { id } : {}), [el("h2", { text: title }), ...kids]);
    // profile
    const name = el("input", { type: "text", class: "email-in", maxlength: "60", placeholder: "Optional", "aria-label": "Display name", value: u.name || "" });
    const save = el("button", { class: "btn ghost", type: "button", text: "Save" }), saved = el("span", { class: "hint", text: "" });
    save.onclick = async () => { save.disabled = true; try { await auth.setName(name.value.trim()); saved.textContent = "Saved."; header(); } catch (e) { saved.textContent = e.message; } save.disabled = false; };
    const profile = card("Profile", [
      el("dl", { class: "kv" }, [el("dt", { text: "Email" }), el("dd", { text: u.email || "" }), el("dt", { text: "Display name" }),
        el("dd", {}, [el("div", { class: "row" }, [name, save]), saved])]),
      el("p", { class: "hint", text: "You stay signed in on this device until you sign out." }),
      Object.assign(el("button", { class: "btn ghost", type: "button", text: "Sign out" }), { onclick: () => auth.signOut() })]);
    if (!me) { body.replaceChildren(profile, el("p", { class: "note bad", text: "Your balance and history could not be loaded right now. Please try again in a moment." })); return; }
    // balance + free previews + buy
    const buy = el("button", { class: "btn", type: "button", text: `Buy ${me.topup.credits} credits · $${(me.topup.cents / 100).toFixed(2)}` }), bnote = el("p", { class: "hint", text: "" });
    buy.onclick = async () => { buy.disabled = true; try { location.href = (await api2("/topup", { return_to: "/account.html#billing" })).url; } catch (e) { buy.disabled = false; bnote.textContent = e.message; } };
    const lim = me.free_limit || 3;
    const stats = el("div", { class: "stats" }, [
      el("div", {}, [el("b", { class: "bal-n", text: String(me.credits) }), el("span", { text: "credits" })]),
      el("div", {}, [el("b", { class: "bal-n", text: `${me.free_left}/${lim}` }), el("span", { text: "free previews left" })])]);
    const hist = el("div", { class: "hist" }, [el("p", { class: "hint", text: "Loading history…" })]);
    const billing = card("Credits & Billing", [stats, el("div", { class: "row" }, [buy, el("a", { class: "btn ghost", href: "videos.html", text: "My Videos" })]), bnote,
      el("h3", { text: "Purchases and charges" }), hist], "billing");
    const notes = [];
    if (q.get("topup") === "done") notes.push(el("p", { class: "note", text: `Payment received. Your balance is ${me.credits} credits.` }));
    if (q.get("topup") === "canceled") notes.push(el("p", { class: "note", text: "Payment canceled. Nothing was charged." }));
    body.replaceChildren(...notes, profile, billing);
    if (location.hash === "#billing") billing.scrollIntoView();
    try {
      const { items } = await api2("/history");
      if (!items.length) return hist.replaceChildren(el("p", { class: "hint", text: "No purchases or charges yet." }));
      const fmt = s => new Date(s).toLocaleString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" });
      const amt = x => x.type === "purchase" ? `+${x.credits} credits` + (x.amount_cents ? ` · $${(x.amount_cents / 100).toFixed(2)}` : "")
        : x.free ? "Free preview" : `${x.credits} credits`;
      const st = { charged: "Charged", refunded: "Refunded", "in progress": "In progress", paid: "Paid", granted: "Granted", applied: "Applied" };
      hist.replaceChildren(el("table", { class: "htab" }, [
        el("thead", {}, [el("tr", {}, ["Date", "Item", "Amount", "Status"].map(h => el("th", { text: h })))]),
        el("tbody", {}, items.map(x => el("tr", { class: x.status === "refunded" ? "refunded" : "" }, [
          el("td", { text: fmt(x.ts) }),
          el("td", {}, [x.version ? el("a", { href: `video.html?v=${encodeURIComponent(x.version)}`, text: x.label }) : document.createTextNode(x.label)]),
          el("td", { text: amt(x) }), el("td", { text: x.free && x.status === "refunded" ? "Returned" : (st[x.status] || x.status) })])))]));
    } catch (e) { hist.replaceChildren(el("p", { class: "note bad", text: "History is unavailable right now." })); }
  }

  window.EVA = { home, video, videos, account };
})();
