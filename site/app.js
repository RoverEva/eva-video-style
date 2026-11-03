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

  /* private video page: polls the job, shows preview, checkout, HD download */
  async function video() {
    const q = new URLSearchParams(location.search), id = q.get("id");
    const hashT = new URLSearchParams(location.hash.slice(1)).get("t"); if (hashT) store.set("eva:" + id, hashT);
    const token = hashT || store.get("eva:" + id);
    const root = $("#job");
    if (!id || !token) { root.innerHTML = "<div><h1>We can't find this video</h1><p>Open the link from the device you uploaded on, or from your payment email.</p><a class='btn' href='/#studio'>Make a new video</a></div>"; return; }
    const phone = $("#jobPhone"), h1 = $("#jobTitle"), sub = $("#jobSub"), steps = $("#jobSteps"), act = $("#jobAction");
    let shownSrc = null, payBusy = false;
    const show = (src, landscape) => { if (src === shownSrc) return; shownSrc = src; phone.innerHTML = ""; phone.classList.toggle("landscape", landscape);
      const vid = Object.assign(el("video", { src, controls: "", playsinline: "", loop: "" }), { autoplay: true });
      vid.onerror = () => { shownSrc = null; setTimeout(tick, 500); };   // expired signed link: fetch a fresh one
      phone.append(vid); };
    const stepList = (items) => { steps.innerHTML = ""; items.forEach(([t, s]) => steps.append(el("li", { class: s, text: t }))); };

    async function tick() {
      let v; try { v = await call(`/api/jobs/${id}?t=${encodeURIComponent(token)}`); } catch (e) { sub.textContent = e.message; return setTimeout(tick, 8000); }
      const land = (v.options || {}).aspect === "16:9"; const pv = v.preview || {}, fn = v.final || {};
      const stage = (s, keys) => keys.indexOf(s);
      act.innerHTML = "";
      if (v.state === "refunded") {
        h1.textContent = "Your payment was refunded"; sub.textContent = "We couldn't render this video, even after retrying. The full amount is on its way back to your card; banks usually show it within 5–10 days.";
        stepList([]); return;
      }
      if (v.paid) {
        if (fn.url) {
          h1.textContent = "Your video is ready"; show(fn.url, land);
          sub.textContent = `Full HD, ${fn.width}×${fn.height}, ${Math.round(fn.duration || 0)} seconds. The download link works until ${new Date(fn.expires * 1000).toLocaleDateString()}.`;
          const dl = el("a", { class: "btn", href: fn.url, download: `EVA_${id}.mp4`, text: "Download MP4" });
          dl.onclick = async e => { e.preventDefault();   // signed links live 15 minutes: always ask for a fresh one
            try { const f = (await call(`/api/jobs/${id}?t=${encodeURIComponent(token)}`)).final; location.href = f.url; } catch (err) { sub.textContent = err.message; } };
          act.append(dl);
          stepList([["Payment confirmed", "done"], ["HD video rendered", "done"], ["Ready to download", "done"]]); return;
        }
        h1.textContent = "Payment confirmed. Rendering your HD video"; sub.textContent = "This usually takes about 5 minutes. You can keep this page open or come back later with the same link.";
        const s = stage(fn.stage, ["preparing", "rendering", "finishing"]);
        stepList([["Payment confirmed", "done"], ["Rendering full HD", s <= 1 ? "now" : "done"], ["Final checks", s === 2 ? "now" : ""], ["Ready to download", ""]]);
        if (pv.url) show(pv.url, land);
        return setTimeout(tick, 5000);
      }
      if (pv.state === "rejected" || pv.state === "failed") {
        h1.textContent = "This video couldn't be processed"; sub.textContent = pv.error || "Please try another file.";
        act.append(el("a", { class: "btn", href: "/#studio", text: "Upload another video" })); stepList([]); return;
      }
      if (pv.url) {
        h1.textContent = "Your free preview is ready"; show(pv.url, land);
        sub.textContent = `This is the first 10 seconds with a watermark. The full video is 1080p, without the watermark, for $${v.price.toFixed(2)}.`;
        const pay = el("button", { class: "btn", type: "button", text: `Get the full video for $${v.price.toFixed(2)}` });
        pay.onclick = async () => { if (payBusy) return; payBusy = true; pay.disabled = true; pay.textContent = "Opening secure checkout…";
          try { location.href = (await call(`/api/jobs/${id}/checkout`, { token })).url; } catch (e) { sub.textContent = e.message; pay.disabled = false; payBusy = false; pay.textContent = `Get the full video for $${v.price.toFixed(2)}`; } };
        act.append(pay, el("a", { class: "btn ghost", href: "/#studio", text: "Try a different video" }));
        if (q.get("paid")) { h1.textContent = "Confirming your payment…"; return setTimeout(tick, 2500); }
        if (v.stripe_mode === "test") act.append(el("p", { class: "note", text: "Test mode: use card 4242 4242 4242 4242, any future date and any CVC. No real money moves." }));
        stepList([["Uploaded", "done"], ["Preview rendered", "done"], ["Pay and get the full HD video", "now"]]); return;
      }
      h1.textContent = "Making your preview"; sub.textContent = "Listening, planning the cards and rendering. This takes 2–4 minutes.";
      const s = stage(pv.stage, ["preparing", "rendering", "finishing"]);
      stepList([["Uploaded", "done"], ["Transcribing and planning", s <= 0 ? "now" : "done"], ["Rendering", s === 1 ? "now" : s > 1 ? "done" : ""], ["Adding captions and music", s === 2 ? "now" : ""]]);
      setTimeout(tick, 4000);
    }
    tick();
  }

  window.EVA = { home, video };
})();
