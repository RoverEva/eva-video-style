/* EVA Video Studio website: home (demos + upload studio) and the private video page. No framework, no build step. */
(function () {
  const API = (window.EVA_API || "").replace(/\/$/, "");
  const $ = (s, r = document) => r.querySelector(s);
  const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "text" ? (e.textContent = v) : e.setAttribute(k, v);
    kids.forEach(k => e.append(k)); return e; };
  const TEMPLATES = { T17: "Sci-Fi Network", T20: "Soft Pop", T01: "Bold Lime", T09: "Gallery Wall" };
  const TRACKS = { "bright-pop": "Bright Pop", "calm-lofi": "Calm Lo-fi", "inspire": "Inspire", "luxury-ambient": "Luxury Ambient" };
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} } };

  async function call(path, body) {
    const r = await fetch(API + path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : {});
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || `Request failed (${r.status})`);
    return j;
  }

  /* before/after wipe: two synced videos, draggable divider (pointer + keyboard) */
  function wipe(box, demo, opts = {}) {
    box.innerHTML = ""; box.classList.toggle("landscape", !!opts.landscape);
    if (!demo || !demo.ready) { box.append(el("div", { class: "soon", text: demo ? `${demo.title} example coming soon` : "" })); return; }
    const a = el("video", { src: demo.before, muted: "", playsinline: "", loop: "", preload: "auto", "aria-label": "Raw upload" });
    const b = el("video", { src: demo.after, playsinline: "", loop: "", preload: "auto", class: "after", "aria-label": "Edited video" });
    a.muted = true; b.muted = true;
    const knob = el("button", { class: "knob", type: "button", "aria-label": "Move the comparison divider", text: "⇆" });
    const bar = el("div", { class: "bar" }, [knob]);
    const sound = el("button", { class: "tag l", type: "button", text: "Sound off" });
    box.append(a, b, bar, sound, el("span", { class: "tag r", text: "Edited" }));
    let split = 50; const set = v => { split = Math.max(0, Math.min(100, v)); box.style.setProperty("--split", split + "%"); }; set(50);
    const from = e => { const r = box.getBoundingClientRect(); set(((e.clientX - r.left) / r.width) * 100); };
    box.addEventListener("pointerdown", e => { if (e.target === sound) return; box.setPointerCapture(e.pointerId); from(e); box.onpointermove = from; });
    box.addEventListener("pointerup", () => { box.onpointermove = null; });
    knob.addEventListener("keydown", e => { if (e.key === "ArrowLeft") set(split - 5); if (e.key === "ArrowRight") set(split + 5); });
    sound.addEventListener("click", () => { b.muted = !b.muted; sound.textContent = b.muted ? "Sound off" : "Sound on"; });
    const sync = () => { if (Math.abs(a.currentTime - b.currentTime) > .12) a.currentTime = b.currentTime; };
    b.addEventListener("timeupdate", sync);
    const start = () => { a.play().catch(() => {}); b.play().catch(() => {}); };
    new IntersectionObserver(es => es.forEach(x => x.isIntersecting ? start() : (a.pause(), b.pause()))).observe(box);
  }

  async function home() {
    let demos = [];
    try { demos = (await (await fetch("demos/demos.json", { cache: "no-cache" })).json()).demos; } catch (e) {}
    const ready = demos.filter(d => d.ready);
    wipe($("#heroPhone"), ready[0] || demos[0]);
    const sw = $("#catSwitch"), cp = $("#catPhone");
    demos.forEach((d, i) => {
      const b = el("button", { type: "button", "aria-pressed": String(i === 0) }, [el("b", { text: d.title }), document.createTextNode(d.blurb)]);
      b.onclick = () => { sw.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); wipe(cp, d); };
      sw.append(b);
    });
    wipe(cp, demos[0]);

    // template chips (multi-select) + "let us choose"
    const tc = $("#tplChips");
    Object.entries(TEMPLATES).forEach(([id, name], i) => tc.append(el("label", { class: "chip" }, [el("input", { type: "checkbox", name: "tpl", value: id, ...(i === 0 ? { checked: "" } : {}) }), el("span", { text: name })])));
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
      const go = $("#go"); go.disabled = true;
      try {
        msg("Uploading…"); const up = await call("/api/uploads", { name: file.name, size: file.size, type });
        store.set("eva:" + up.job, up.token);
        meter.style.display = "block";
        await new Promise((res, rej) => { const x = new XMLHttpRequest(); x.open("PUT", up.put_url); x.setRequestHeader("Content-Type", up.put_type);
          x.upload.onprogress = p => { if (p.lengthComputable) { bar.style.width = (100 * p.loaded / p.total).toFixed(0) + "%"; msg(`Uploading… ${Math.round(100 * p.loaded / p.total)}%`); } };
          x.onload = () => x.status < 300 ? res() : rej(new Error("The upload was interrupted. Please try again."));
          x.onerror = () => rej(new Error("The upload was interrupted. Please try again.")); x.send(file); });
        msg("Starting your preview…");
        await call(`/api/jobs/${up.job}/preview`, Object.assign({ token: up.token }, opts));
        location.href = `video.html?id=${up.job}#t=${encodeURIComponent(up.token)}`;
      } catch (err) { msg(err.message, true); go.disabled = false; meter.style.display = "none"; }
    });
  }

  /* private video page: real backend progress, preview, regenerate, checkout, HD download. Survives refreshes: all
     state comes from the API; the private token is kept in this browser (and in the link). */
  async function video() {
    const q = new URLSearchParams(location.search), id = q.get("id");
    const hashT = new URLSearchParams(location.hash.slice(1)).get("t"); if (hashT) store.set("eva:" + id, hashT);
    const token = hashT || store.get("eva:" + id);
    const root = $("#job");
    if (!id || !token) { root.innerHTML = "<div><h1>We can't find this video</h1><p>Open the link from the device you uploaded on, or from your payment email.</p><a class='btn' href='/#studio'>Make a new video</a></div>"; return; }
    const phone = $("#jobPhone"), h1 = $("#jobTitle"), sub = $("#jobSub"), steps = $("#jobSteps"), act = $("#jobAction");
    const prog = $("#jobProg"), pctEl = $("#jobPct"), bar = $("#jobBar"), note = $("#jobProgNote");
    let shownSrc = null, payBusy = false, regenBusy = false, confirmOpen = false, timer = null, playable = false, seen = { key: "", pct: 0 };
    const again = ms => { clearTimeout(timer); timer = setTimeout(tick, ms); };

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

  window.EVA = { home, video };
})();
