"""Stage B · post-render QA on the actual rendered file.

ctx keys (all optional except video):
  video        rendered MP4 to check (with burned captions if any)
  clean        same render without captions (better for face/quality checks)
  source       presenter footage: video file or 30 fps JPG folder;  source_offset  seconds (section start in the source)
  source_native  [w, h] of the original upload (when `source` holds re-scaled frames)
  audio_source file whose audio is the plain voice (for caption/speech sync); defaults to source or video
  srt, ass     delivered captions (.srt) and the .ass that was burned;  captions_burned  bool (default: ass given)
  face         calibration {x, y, h} (EV.face) used when no face detector is available
  aspect       "16:9" | "9:16";  kind  "final" | "preview";  expected_frames  int
  size         [w, h] expected output size (overrides the aspect's standard size, e.g. a 720x1280 web copy);  fps  expected fps
  template     default template id;  category  talk|ads|science|explain
  scenes       [{t0, t1, template, static?, allow_face_hidden?, allow_crop?}]   (from plan.json sections)
  events       [t, ...] expected visual events (card in/out) treated like transitions
  trace        Stage A trace JSON (expected presenter geometry per time)
"""
import json, math
from pathlib import Path

import cv2
import numpy as np

from . import cache, face as F, media, subs
from .config import Config
from .report import Report


def _scene_of(scenes, t):
    for i, s in enumerate(scenes):
        if s["t0"] <= t < s["t1"]: return i, s
    return (len(scenes) - 1, scenes[-1]) if scenes else (None, {})


def _draw(img, boxes=(), mask=None, label=None):
    im = img.copy()
    if mask is not None:
        m = (mask > 32).astype(np.uint8)
        cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(im, cnt, -1, (255, 0, 255), 3)
    for (x, y, w, h), col in boxes:
        cv2.rectangle(im, (int(x), int(y)), (int(x + w), int(y + h)), col, 4)
    if label:
        cv2.rectangle(im, (0, 0), (im.shape[1], 54), (0, 0, 0), -1)
        cv2.putText(im, label[:70], (12, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    return im


class Post:
    def __init__(self, ctx, out_dir, config=None):
        self.ctx = dict(ctx); self.cfg = config if isinstance(config, Config) else Config(config, ctx.get("category"))
        self.rep = Report("post", out_dir, context={k: (str(v) if isinstance(v, Path) else v) for k, v in ctx.items() if k not in ("trace_data",)})
        self.scenes = ctx.get("scenes") or []

    def th(self, t=None, section=None):
        if isinstance(t, str): t, section = None, t   # th("render") == th(None, "render")
        tpl = self.ctx.get("template")
        if t is not None and self.scenes: tpl = _scene_of(self.scenes, t)[1].get("template") or tpl
        d = self.cfg.for_template(tpl)
        return d[section] if section else d

    def scene_info(self, t):
        if not self.scenes: return None, self.ctx.get("template")
        i, s = _scene_of(self.scenes, t); return i, s.get("template") or self.ctx.get("template")

    def static_span(self, a, b):
        """True if [a, b] lies (within the transition guard) inside parts declared static (plan scene `static`, --static scene
        indexes or time ranges, or a template/scene index listed in motion.static_scenes): an intended still is never 'frozen'"""
        g = self.th()["transition_guard_s"]; mth = self.th("motion")
        st = [sc for i, sc in enumerate(self.scenes) if sc.get("static") or i in mth["static_scenes"]
              or (sc.get("template") or self.ctx.get("template")) in mth["static_scenes"]]
        st = [(sc["t0"], sc["t1"]) for sc in st] + [tuple(r) for r in self.ctx.get("static_ranges") or []]
        if not st: return False
        st = sorted(st); cur = a
        for t0, t1 in st:   # walk the union of static scenes from a
            if t0 - g <= cur < t1: cur = t1
        return cur + g >= b

    def guarded(self, t):
        g = self.th()["transition_guard_s"]; ev = list(self.ctx.get("events") or [])
        for s in self.scenes: ev += [s["t0"], s["t1"]]
        dur = self.dur
        return t < .5 or t > dur - .3 or any(abs(t - e) <= g for e in ev)

    # ───────────────────────── run ─────────────────────────
    def run(self):
        R = self.rep; V = self.ctx["video"]
        try:
            self.p = media.probe(V)
        except Exception as e:
            R.add("RENDER_STREAMS", "FAIL", f"output cannot be read: {e}", fix="re-run the render/assembly stage"); return R.write()
        self.dur = (self.p["video"] or {}).get("duration") or self.p["duration"]
        R.info["video"] = {k: self.p[k] for k in ("format", "duration", "bytes")} | {"video": self.p["video"], "audio": self.p["audio"]}
        self.check_render()
        if not self.p["video"]: return R.write()
        self.samples = self.sample_times()
        self.load_frames()
        self.check_face()
        self.check_captions()
        self.check_quality()
        self.check_motion()
        self.check_sync()
        return R.write()

    # ───────────────────────── render / format ─────────────────────────
    def check_render(self):
        R, p, th = self.rep, self.p, self.th("render"); v, a = p["video"], p["audio"]
        if not v:
            R.add("RENDER_STREAMS", "FAIL", "no video stream in the output", fix="re-run assembly; check FFmpeg logs"); return
        if th["require_audio"] and not a:
            R.add("RENDER_STREAMS", "FAIL", "no audio stream (the speaker's voice is missing)", fix="re-run assembly with the source audio (assemble.sh)")
        else: R.ran("RENDER_STREAMS")
        fmt_ok = any(c in p["format"] for c in th["containers"])
        if not fmt_ok or v["codec"] not in th["codecs"]:
            R.add("RENDER_FORMAT", "FAIL", f"container/codec {p['format']}/{v['codec']} (expected {'/'.join(th['containers'])} with {'/'.join(th['codecs'])})", fix="export H.264 in MP4")
        elif v["pix_fmt"] != "yuv420p":
            R.add("RENDER_FORMAT", "WARN", f"pixel format {v['pix_fmt']} (yuv420p plays everywhere)", fix="encode with -pix_fmt yuv420p")
        else: R.ran("RENDER_FORMAT")
        W, H = v["width"], v["height"]; asp = self.ctx.get("aspect")
        sizes = th["preview_sizes"] if self.ctx.get("kind") == "preview" else th["sizes"]
        if self.ctx.get("size"):
            exp = list(self.ctx["size"])
            if [W, H] != exp:
                R.add("RENDER_SIZE", "FAIL", f"output is {W}x{H}, expected {exp[0]}x{exp[1]}", fix="render at the requested size and do not rescale the master")
            else: R.ran("RENDER_SIZE", f"{W}x{H}")
            if asp and (W > H) != (asp == "16:9"):
                R.add("RENDER_SIZE", "FAIL", f"output is {W}x{H} but the job asked for {asp}", fix="render with the right --ar")
        elif asp:
            exp = sizes.get(asp)
            if exp and [W, H] != list(exp):
                R.add("RENDER_SIZE", "FAIL", f"output is {W}x{H}, expected {exp[0]}x{exp[1]} for {asp}", fix="render with the right --ar and do not rescale the master")
            else: R.ran("RENDER_SIZE", f"{W}x{H}")
        elif [W, H] not in [list(s) for s in list(th["sizes"].values()) + list(th["preview_sizes"].values())]:
            R.add("RENDER_SIZE", "WARN", f"non-standard output size {W}x{H}", fix="pass --aspect so the expected size is known")
        else: R.ran("RENDER_SIZE", f"{W}x{H}")
        if v["sar"] not in ("1:1", "0:1", None, "N/A"):
            R.add("RENDER_SAR", "FAIL", f"non-square pixels (SAR {v['sar']}): the picture is shown stretched", fix="encode with setsar=1")
        else: R.ran("RENDER_SAR")
        want_fps = self.ctx.get("fps") or th["fps"]
        if abs(v["fps"] - want_fps) > .01 or (v["avg_fps"] and abs(v["avg_fps"] - want_fps) > .05):
            R.add("RENDER_FPS", "FAIL", f"frame rate {v['fps']:.3f} (avg {v['avg_fps']:.3f}), expected {want_fps}", fix=f"render and encode at {want_fps} fps")
        else: R.ran("RENDER_FPS")
        args = (th["black_pix_th"], .1, th["freeze_noise"], 1.0)
        dp = cache.memo(cache.key("decode", cache.file_sig(self.ctx["video"]), args, bool(a)),
                        lambda: media.decode_pass(self.ctx["video"], *args, audio=bool(a)))
        self.decode = dp
        if dp["errors"] or dp["returncode"]:
            R.add("RENDER_DECODE", "FAIL", f"decoder errors: {'; '.join(dp['errors'][:3]) or 'ffmpeg exit ' + str(dp['returncode'])}", fix="re-encode; check for a truncated chunk")
        else: R.ran("RENDER_DECODE")
        n = dp["frames"] or v.get("nb_frames"); exp_n = self.ctx.get("expected_frames"); tol = th["frame_tolerance"]
        R.info["frames"] = n
        if exp_n and n is not None:
            if n < exp_n - tol:
                R.add("RENDER_DURATION", "FAIL", f"{n} frames, expected {exp_n}: the ending is truncated by {(exp_n - n) / 30:.2f}s", t=(n / 30, exp_n / 30), fix="re-render the last chunk; section lengths must add up to the source frame count")
            elif n > exp_n + tol:
                R.add("RENDER_DURATION", "WARN", f"{n} frames, expected {exp_n} ({(n - exp_n) / 30:.2f}s too long)", fix="check section boundaries (frame-exact)")
            else: R.ran("RENDER_DURATION", f"{n} frames")
        elif n: R.ran("RENDER_DURATION", f"{n} frames (no expected count given)")
        if a:
            gap = abs(a["duration"] - v["duration"])
            if gap > th["av_mismatch_fail_s"]:
                R.add("RENDER_AV_SYNC", "FAIL", f"audio {a['duration']:.2f}s vs video {v['duration']:.2f}s", fix="assemble with -shortest from a source of the same length")
            elif gap > th["av_mismatch_warn_s"]:
                R.add("RENDER_AV_SYNC", "WARN", f"audio {a['duration']:.2f}s vs video {v['duration']:.2f}s ({gap:.2f}s apart)", fix="trim the audio to the video length")
            else: R.ran("RENDER_AV_SYNC")
        for s0, s1 in dp["blacks"]:
            d = s1 - s0; mid = (s0 + s1) / 2
            if d >= th["black_fail_s"]:
                R.add("RENDER_BLACK", "FAIL", f"black screen for {d:.2f}s", t=(s0, s1), fix="a scene or chunk failed to render; check its frames dir / page errors")
            elif d >= th["black_warn_s"] and not self.guarded(mid):
                R.add("RENDER_BLACK", "WARN", f"black frames for {d:.2f}s outside a transition", t=(s0, s1), fix="check the scene at this time")
        R.ran("RENDER_BLACK")
        for s0, s1 in dp["freezes"]:
            s1 = s1 if s1 is not None else self.dur; d = s1 - s0
            if self.static_span(s0, s1): R.info.setdefault("freeze_in_static_scene", []).append([round(s0, 2), round(s1, 2)]); continue
            if d >= th["freeze_warn_s"]:
                R.add("RENDER_FREEZE", "WARN", f"picture does not change for {d:.2f}s (stuck presenter frames or an intended static shot)", t=(s0, s1),
                      fix="if unintended: check the image-sequence folder and src0; mark static scenes in the plan to silence this")
        R.ran("RENDER_FREEZE")
        if dp["lufs"] is not None:
            if abs(dp["lufs"] - th["lufs_target"]) > th["lufs_tolerance"]:
                R.add("AUDIO_LOUDNESS", "WARN", f"integrated loudness {dp['lufs']:.1f} LUFS (target {th['lufs_target']})", fix="loudnorm I=-16 (assemble.sh)")
            else: R.ran("AUDIO_LOUDNESS", f"{dp['lufs']:.1f} LUFS")
        self.bpp = v["bit_rate"] / (v["width"] * v["height"] * max(1, v["fps"])) if v.get("bit_rate") else None
        R.info["bits_per_pixel"] = round(self.bpp, 4) if self.bpp else None

    # ───────────────────────── sampling ─────────────────────────
    def sample_times(self):
        th = self.th(); dur = self.dur; step = th["sample_every_s"]
        ts = list(np.arange(.1, max(.11, dur - .05), step))
        for s in self.scenes: ts += [s["t0"] + .15, s["t1"] - .15, (s["t0"] + s["t1"]) / 2]
        self.ass_events = []
        if self.ctx.get("ass") and Path(self.ctx["ass"]).exists():
            self.ass_events, self.ass_play = subs.parse_ass(Path(self.ctx["ass"]).read_text(encoding="utf-8-sig"))
            ts += [(e["start"] + e["end"]) / 2 for e in self.ass_events]
        fps = self.p["video"]["fps"] or 30
        fr = sorted({min(int(round(t * fps)), int(dur * fps) - 1) for t in ts if 0 <= t < dur})
        if len(fr) > 160: fr = fr[::math.ceil(len(fr) / 160)]
        self.fps = fps
        return fr

    def load_frames(self):
        R = self.rep
        self.final = media.read_frames(self.ctx["video"], self.samples)
        self.clean = media.read_frames(self.ctx["clean"], self.samples) if self.ctx.get("clean") and Path(self.ctx["clean"]).exists() else {}
        self.src, self.srcobj = {}, None
        if self.ctx.get("source") and Path(self.ctx["source"]).exists():
            try:
                self.srcobj = media.Source(self.ctx["source"], self.ctx.get("source_offset", 0))
                self.src = self.srcobj.frames_at([n / self.fps for n in self.samples])
            except Exception as e:
                R.info["source_error"] = str(e)
        th = self.th("render"); H, W = self.p["video"]["height"], self.p["video"]["width"]
        run = []
        for n in self.samples:   # blank (uniform) frames: nothing rendered at all
            f = self.final.get(n)
            if f is None: continue
            small = cv2.resize(f, (96, int(96 * H / W)), interpolation=cv2.INTER_AREA)
            if small.std() < th["blank_std"] and small.mean() > 20: run.append(n)
            else:
                self._blank(run); run = []
        self._blank(run); R.ran("RENDER_BLANK")
        self.check_compression()

    def check_compression(self):
        """bitrate floor for masters. Low bitrate alone is not damage (a flat colour stage compresses very well), so the
        floor is set well below any real Eva render (>= 0.02 bits/pixel measured) and only WARNs; detail lost against
        the source is measured by QUALITY_SHARPNESS."""
        R = self.rep; th = self.th("quality")
        if self.ctx.get("kind") == "preview": R.skip("QUALITY_BITRATE", "preview (compressed on purpose)"); return
        if not self.bpp: R.skip("QUALITY_BITRATE", "container reports no video bitrate"); return
        if self.bpp < th["min_bits_per_pixel"]:
            R.add("QUALITY_BITRATE", "WARN", f"very low bitrate ({self.bpp:.4f} bits/pixel, {self.p['video']['bit_rate'] / 1e6:.2f} Mb/s): compression artefacts likely",
                  fix="encode with a lower CRF (render.mjs uses 16, assemble.sh 18) and do not re-compress the master")
        else: R.ran("QUALITY_BITRATE", f"{self.bpp:.3f} bits/pixel")

    def _blank(self, run):
        if not run: return
        t0, t1 = run[0] / self.fps, run[-1] / self.fps
        th = self.th("render")
        sev = "FAIL" if len(run) >= th["blank_fail_samples"] else "WARN"
        ev = self.rep.evidence("RENDER_BLANK", t0, self.final[run[0]])
        self.rep.add("RENDER_BLANK", sev, f"blank single-colour frame{'s' if len(run) > 1 else ''} (nothing rendered)", t=(t0, t1), evidence=ev,
                     fix="a scene failed to build or its assets did not load; run `python3 -m qa pre` on the page")

    # ───────────────────────── face / subject ─────────────────────────
    def check_face(self):
        R = self.rep
        if not self.src:
            for c in ("FACE_CROP", "FACE_SCALE", "FACE_VISIBLE", "FACE_STRETCH"): R.skip(c, "no source footage given (--source)")
            self.faces = {}; return
        det = F.Detector(self.ctx.get("face"))
        R.info["face_backend"] = det.name or "none"
        if det.name is None:
            for c in ("FACE_CROP", "FACE_SCALE", "FACE_VISIBLE", "FACE_STRETCH"): R.skip(c, "no face detector and no calibration")
            self.faces = {}; return
        H, W = self.p["video"]["height"], self.p["video"]["width"]
        SW, SH = self.srcobj.size; s_ref = max(W / SW, H / SH)   # full-bleed (cover) scale = the footage's own size on this frame
        native = self.ctx.get("source_native"); up_base = (SW / native[0]) if native else 1.0
        self.faces, cand = {}, {"crop": [], "scale": [], "head": [], "stretch": []}
        src_found = 0
        out_file = self.ctx["clean"] if self.clean else self.ctx["video"]
        ck = (cache.file_sig(out_file), cache.file_sig(self.ctx["source"]), self.ctx.get("source_offset", 0), det.name, self.ctx.get("face"))
        # pass 1: source detections for every sample, made consistent (a false detection on one frame must not be tracked)
        cal = det.from_calibration((SW, SH)) if det.calibration else None
        raw = [cache.memo(cache.key("detect2", ck, n), lambda n=n: [list(b) for b in det.detect_all(self.src.get(n / self.fps))]
                          if self.src.get(n / self.fps) is not None else []) for n in self.samples]
        srcbox = dict(zip(self.samples, F.consistent([[tuple(b) for b in r] for r in raw], cal)))
        R.info["face_source_rejected"] = sum(1 for _, how in srcbox.values() if how in ("consistent", "reference"))
        for n in self.samples:
            t = n / self.fps; s = self.src.get(t); o = self.clean.get(n) if self.clean else self.final.get(n)
            if s is None or o is None: continue

            def measure():
                box, how = srcbox[n]
                if box is None: box = det.from_calibration((SW, SH)); how = "calibration"
                if box is None: return {}
                return {"box": list(box), "how": how, "m": F.track(s, box, o)}
            hit = cache.memo(cache.key("track2", ck, n), measure)   # measurements only; thresholds are applied below
            if not hit: continue
            box, how, m = tuple(hit["box"]), hit["how"], hit["m"]
            src_found += how in ("detector", "consistent")
            if not m: continue
            fth = self.th(t, "face")
            conf = "high" if (m["score"] >= fth["high_conf"] or (m["out_frac"] > .02 and m["inframe"] >= .8)) else "medium" if m["score"] >= fth["detect_min_conf"] else "none"
            m.update(t=t, conf=conf, src_box=box, src_how=how, subject_scale=round(m["scale"] * 1.0 / s_ref, 3), upscale=round(m["scale"] * up_base, 3))
            m["head"] = F.head_from_face(m["box"]); m["head_edges"] = F.edges_out(m["head"], W, H)
            self.faces[n] = m
        R.info["face_samples"] = {"total": len(self.samples), "source_face_detected": src_found, "matched_high": sum(1 for m in self.faces.values() if m["conf"] == "high"),
                                  "matched_medium": sum(1 for m in self.faces.values() if m["conf"] == "medium")}
        fs = R.info["face_samples"]
        if fs["matched_high"] == 0:
            # medium matches alone are not evidence: a face pushed out of frame can still "match" background texture
            R.add("FACE_TRACK", "WARN", f"the presenter's face was not found with confidence in any of {len(self.samples)} sampled frames "
                  f"(face missing, fully covered or pushed out of frame?): face checks are unverified",
                  fix="look at the evidence/contact sheet; check the source/offset passed to QA", evidence=R.evidence("FACE_TRACK", self.samples[len(self.samples) // 2] / self.fps,
                  self.final.get(self.samples[len(self.samples) // 2])))
            for c in ("FACE_CROP", "FACE_SCALE", "FACE_VISIBLE", "FACE_STRETCH", "FACE_HEAD_EDGE"): R.skip(c, "no high-confidence face match")
            self.faces = {}; return
        if fs["matched_high"] < .3 * fs["source_face_detected"]:
            R.add("FACE_TRACK", "WARN", f"the face was matched with confidence in only {fs['matched_high']} of {fs['source_face_detected']} sampled frames: "
                  "face checks cover those frames only", fix="review the other frames on a contact sheet")
        else: R.ran("FACE_TRACK", f"{fs['matched_high']} high-confidence matches")
        scenes = self.scenes
        for n, m in sorted(self.faces.items()):
            if m["conf"] == "none": continue
            t = m["t"]; fth = self.th(t, "face"); sc = _scene_of(scenes, t)[1] if scenes else {}
            allow_crop = fth["allow_crop"] or sc.get("allow_crop")
            if not allow_crop and m["out_frac"] > fth["fail_face_out"]:
                cand["crop"].append((n, m))
            elif not allow_crop and any(v > fth["warn_head_out"] for v in m["head_edges"].values()):
                cand["head"].append((n, m))
            if m["subject_scale"] > fth["max_subject_scale"]: cand["scale"].append((n, m))
            if (m["visible"] is not None and m["visible"] < fth["warn_visible"] and m["out_frac"] < .05 and m["conf"] == "high"
                    and not sc.get("allow_face_hidden")):
                sid, tpl = self.scene_info(t)
                ev = self.rep.evidence("FACE_VISIBLE", t, _draw(self.final.get(n), [(m["box"], (0, 160, 255))], label=f"face {m['visible']:.0%} visible @ {t:.2f}s"))
                R.add("FACE_VISIBLE", "WARN", f"face only {m['visible']:.0%} visible (covered by graphics or cut by the window edge)", t=t, scene=sid, template=tpl, evidence=ev,
                      data={"visible": m["visible"], "cells": m["cells"]}, fix="keep text and window edges off the face (template safe zones)")
        R.ran("FACE_VISIBLE")
        self._group("FACE_CROP", cand["crop"], lambda m: f"face cut by the frame edge ({', '.join(f'{k} {v:.0%}' for k, v in F.edges_out(m['box'], W, H).items())} of the face outside)",
                    "keep the presenter at the footage's own scale and move her only as far as her whole head stays in frame",
                    data=lambda m: {"worst_out_frac": m["out_frac"], "edges": F.edges_out(m["box"], W, H), "subject_scale": m["subject_scale"]})
        # forehead/hair or chin past the frame edge. The head box is estimated from the face box (hair line varies), so only
        # a deep cut (fail_head_out) on a run of high-confidence samples is a confirmed FAIL; shallower cuts WARN
        self._group("FACE_HEAD_EDGE", cand["head"], lambda m: f"head cut by the frame edge ({', '.join(f'{k} {v:.0%}' for k, v in m['head_edges'].items())} of the head outside: forehead/hair or chin)",
                    "re-check the face calibration and the pose; the whole head (hair to chin) must stay in frame",
                    must=lambda m: max(m["head_edges"].values()) >= self.th(m["t"], "face")["fail_head_out"],
                    data=lambda m: {"edges": m["head_edges"]}, worst=lambda m: max(m["head_edges"].values()))
        fail_scale = lambda m: m["subject_scale"] > self.th(m["t"], "face")["fail_subject_scale"]
        self._group("FACE_SCALE", cand["scale"], lambda m: f"presenter enlarged to {m['subject_scale']:.2f}x the footage's own size (limit {self.th(m['t'], 'face')['max_subject_scale']:.2f}x)",
                    "do not zoom the presenter for layout; move her instead (EVA_VIDEO_STYLE: presenter never enlarged)",
                    must=fail_scale, data=lambda m: {"worst_subject_scale": m["subject_scale"]})
        # stretch is a property of how a layer is scaled, so it is uniform over a scene: judge the median per scene
        # (single-sample aspect estimates are noisy and never decide alone)
        # only faces fully in frame: the aspect of a half-visible face is not measurable (the probe can trade width for
        # in-frame overlap), so cropped samples are judged by FACE_CROP/FACE_SCALE, never by FACE_STRETCH
        hi = [m for m in self.faces.values() if m["conf"] == "high" and m["out_frac"] <= .05]
        if len(hi) >= 4:
            groups = {}
            for m in hi: groups.setdefault(self.scene_info(m["t"])[0], []).append(m)
            R.info["subject_aspect_median"] = round(float(np.median([m["aspect"] for m in hi])), 3)
            worst = None
            for sid, ms in groups.items():
                if len(ms) < 3: continue
                med = float(np.median([m["aspect"] for m in ms]))
                if worst is None or abs(med - 1) > abs(worst[1] - 1): worst = (sid, med, ms)
            fth = self.th(None, "face")
            if worst and abs(worst[1] - 1) > fth["fail_stretch"]:
                sid, med, ms = worst
                R.add("FACE_STRETCH", "FAIL", f"presenter is stretched: width/height {med:.2f}x her real proportions", t=(ms[0]["t"], ms[-1]["t"]), scene=sid,
                      template=self.scene_info(ms[0]["t"])[1], fix="scale the footage uniformly (object-fit: cover), never to a fixed width AND height",
                      data={"median_aspect": round(med, 3), "samples": len(ms)})
            elif worst and abs(worst[1] - 1) > fth["max_stretch"]:
                sid, med, ms = worst
                R.add("FACE_STRETCH", "WARN", f"presenter may be stretched (median width/height {med:.2f}x)", t=(ms[0]["t"], ms[-1]["t"]), scene=sid,
                      fix="check that the presenter is scaled uniformly", data={"median_aspect": round(med, 3), "samples": len(ms)})
            else: R.ran("FACE_STRETCH", f"aspect {R.info['subject_aspect_median']:.3f}")
        else: R.skip("FACE_STRETCH", "fewer than 4 high-confidence face matches")
        self._check_layout_vs_trace()
        # presenter required but missing
        miss = [n for n in self.samples if self.faces.get(n, {}).get("conf", "none") == "none"
                and self.th(n / self.fps, "face")["require_presenter"] and not self.guarded(n / self.fps)]
        if len(miss) >= 3:
            R.add("FACE_PRESENT", "WARN", f"presenter not found in {len(miss)} sampled frames where the template expects her", t=(miss[0] / self.fps, miss[-1] / self.fps),
                  fix="check the presenter window opacity / frames folder for these scenes")

    def _group(self, check, items, msg, fix, must=None, data=None, worst=None):
        """confirmed FAIL only for a run of >= min_fail_samples high-confidence samples outside transitions; else WARN"""
        R = self.rep; R.ran(check)
        if not items: return
        idx = {n: i for i, n in enumerate(self.samples)}
        runs, cur = [], []
        for n, m in items:
            if cur and idx[n] != idx[cur[-1][0]] + 1: runs.append(cur); cur = []
            cur.append((n, m))
        if cur: runs.append(cur)
        for run in runs:
            strong = [(n, m) for n, m in run if m["conf"] == "high" and not self.guarded(m["t"]) and (must is None or must(m))]
            need = self.th(run[0][1]["t"], "face")["min_fail_samples"]
            sev = "FAIL" if len(strong) >= need else "WARN"
            n, m = max(run, key=lambda x: worst(x[1]) if worst else x[1].get("subject_scale", 0) if check == "FACE_SCALE" else x[1]["out_frac"])
            t0, t1 = run[0][1]["t"], run[-1][1]["t"]; sid, tpl = self.scene_info(m["t"])
            ev = R.evidence(check, m["t"], _draw(self.final.get(n), [(m["head"], (0, 0, 255)), (m["box"], (0, 255, 0))], label=f"{check} {sev} @ {m['t']:.2f}s"))
            note = "" if sev == "FAIL" else " (uncertain: short, low-confidence or during a transition)"
            R.add(check, sev, msg(m) + note, t=(t0, t1), scene=sid, template=tpl, evidence=ev, fix=fix,
                  data=dict((data(m) if data else {}), confidence=m["conf"], samples=len(run), match_score=m["score"]))

    def _check_layout_vs_trace(self):
        """measured face vs the face position the engine laid out (Stage A trace), where the trace knows it"""
        tr = self.ctx.get("trace_data") or {}
        exp = [s for s in tr.get("samples", []) if s.get("face")]
        if not exp: self.rep.skip("FACE_LAYOUT", "no Stage A trace with presenter geometry"); return
        R = self.rep; bad = []
        for n, m in self.faces.items():
            if m["conf"] != "high": continue
            e = min(exp, key=lambda s: abs(s["t"] - m["t"]))
            if abs(e["t"] - m["t"]) > .06 or not e["face"].get("visible", True): continue
            eh = e["face"]["h"]; mh = m["head"][3]
            ratio = mh / max(1, eh)
            tol = self.th(m["t"], "face")["expected_scale_tolerance"]
            if abs(ratio - 1) > max(tol, .25):   # the trace head box is an estimate from EV.face: generous tolerance
                bad.append((n, m, ratio))
        for n, m, r in bad[:20]:
            sid, tpl = self.scene_info(m["t"])
            R.add("FACE_LAYOUT", "WARN", f"rendered head is {r:.2f}x the size the layout planned (calibration off or an extra zoom)", t=m["t"], scene=sid, template=tpl,
                  fix="re-calibrate EV.face; look for CSS scale on the presenter")
        R.ran("FACE_LAYOUT")

    # ───────────────────────── captions ─────────────────────────
    def check_captions(self):
        R = self.rep; ctx = self.ctx
        if ctx.get("srt") and Path(ctx["srt"]).exists():
            th = self.th("srt")
            probs, self.srt_cues = subs.validate_srt(Path(ctx["srt"]).read_text(encoding="utf-8-sig", errors="replace"), self.dur, th, "captions .srt")
            for sev, chk, msg, t in probs: R.add(chk, sev, msg, t=t, fix="fix the cue in the delivered .srt (never the user's original SRT)")
            for c in ("SRT_SYNTAX", "SRT_TIMING", "SRT_ORDER", "SRT_BOUNDS", "SRT_READ"): R.ran(c)
            if self.ass_events:
                pr = subs.compare_srt_ass(self.srt_cues, self.ass_events, self.th("captions")["srt_ass_tolerance_s"])
                if pr: R.add("CAP_TIMING", "FAIL", "burned captions do not follow the delivered SRT: " + "; ".join(pr[:3]), fix="re-run captions.py and burn the .ass it wrote")
                else: R.ran("CAP_TIMING", "burned .ass events match the .srt")
        else:
            self.srt_cues = []; R.skip("SRT_TIMING", "no delivered .srt given")
        if not self.ass_events:
            for c in ("CAP_BOUNDS", "CAP_FACE", "CAP_LINES", "CAP_CONTRAST"): R.skip(c, "no burned .ass given (--ass)")
            return
        H, W = self.p["video"]["height"], self.p["video"]["width"]
        on = lambda n: [e for e in self.ass_events if e["start"] <= n / self.fps < e["end"]]
        mframes = [n for n in self.samples if on(n)]
        try:
            masks = media.render_ass_alpha(ctx["ass"], (W, H), mframes, self.fps)
        except Exception as e:
            R.add("CAP_RENDER", "WARN", f"could not render the .ass for checking: {e}", fix="install libass fonts / FONTSDIR"); return
        cth = self.th("captions"); asp = ctx.get("aspect") or ("9:16" if H > W else "16:9")
        sl, st, sr, sb = cth["safe"][asp]; e = cth["edge_px"]
        burned = ctx.get("captions_burned", True)
        cap_face_cand = []
        for n in mframes:
            mk = masks.get(n)
            if mk is None: continue
            t = n / self.fps; sid, tpl = self.scene_info(t); cth = self.th(t, "captions")
            ys, xs = np.nonzero(mk > 24)
            if not len(xs):
                continue
            x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            text = " / ".join(ev["text"].replace("\n", " ") for ev in on(n))[:60]
            if x0 <= e or y0 <= e or x1 >= W - 1 - e or y1 >= H - 1 - e:
                ev = R.evidence("CAP_BOUNDS", t, _draw(self.final.get(n, np.zeros((H, W, 3), np.uint8)), mask=mk, label=f"caption at frame edge @ {t:.2f}s"))
                R.add("CAP_BOUNDS", "FAIL", f"caption reaches the frame edge and is cut off: \"{text}\"", t=t, scene=sid, template=tpl, evidence=ev,
                      fix="wrap the line (MarginL/R) or move it inside the frame; check \\pos overrides", data={"bbox": [int(x0), int(y0), int(x1), int(y1)]})
            elif x0 < sl or y0 < st or x1 > W - sr or y1 > H - sb:
                R.add("CAP_SAFE", "WARN", f"caption outside the safe area ({asp}): \"{text}\"", t=t, scene=sid, template=tpl,
                      fix="keep captions in the caption zone (EV.zone('caption'))", data={"bbox": [int(x0), int(y0), int(x1), int(y1)]})
            # lines
            rows = (mk > 24).any(axis=1); bands, run = 0, 0
            for r_ in np.concatenate([rows, [False]]):
                if r_: run += 1
                else:
                    if run >= 8: bands += 1
                    run = 0
            if bands > cth["max_lines"]:
                R.add("CAP_LINES", "WARN", f"caption wraps to {bands} lines (max {cth['max_lines']}): \"{text}\"", t=t, scene=sid, template=tpl,
                      fix="shorter phrases (phrase_srt max_chars) or a smaller font")
            # face
            m = self.faces.get(n) if hasattr(self, "faces") else None
            if m and m["conf"] != "none":
                fb = [int(v) for v in m["box"]]; hb = [int(v) for v in m["head"]]
                dil = cv2.dilate((mk > 24).astype(np.uint8), np.ones((5, 5), np.uint8))
                def cover(b):
                    x, y, w, h = b; x0_, y0_, x1_, y1_ = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
                    return float(dil[y0_:y1_, x0_:x1_].sum()) / max(1, w * h) if x1_ > x0_ and y1_ > y0_ else 0.0
                fc, hc = cover(fb), cover(hb)
                m["cap_cover"] = fc
                if fc > cth["fail_face_cover"]: cap_face_cand.append((n, dict(m, cap_cover=round(fc, 3), mask=mk, text=text)))
                elif hc > cth["warn_head_cover"]:
                    R.add("CAP_FACE", "WARN", f"caption overlaps the presenter's hair/chin area ({hc:.0%} of the head box): \"{text}\"", t=t, scene=sid, template=tpl,
                          fix="move captions below the chin or put the presenter higher for this pose")
            # contrast (final frame)
            f = self.final.get(n)
            if f is not None: self._contrast(f, mk, t, sid, tpl, text, cth)
            # burned at all?
            c = self.clean.get(n) if self.clean else None
            if burned and c is not None and f is not None:
                core = cv2.erode((mk > 200).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
                if core.sum() > 50 and np.abs(f.astype(int) - c.astype(int))[core].mean() < 6:
                    R.add("CAP_BURN", "FAIL", f"caption expected but not burned into the video: \"{text}\"", t=t, scene=sid, template=tpl,
                          fix="burn the .ass with assemble.sh (libass + fonts)")
        for c in ("CAP_BOUNDS", "CAP_SAFE", "CAP_LINES", "CAP_CONTRAST", "CAP_BURN"): R.ran(c)
        if not hasattr(self, "faces") or not self.faces: R.skip("CAP_FACE", "presenter face not tracked (no source)")
        # caption over the face: a confirmed overlap on high-confidence samples blocks delivery
        R.ran("CAP_FACE")
        idx = {n: i for i, n in enumerate(self.samples)}
        runs, cur = [], []
        for n, m in cap_face_cand:
            if cur and idx[n] != idx[cur[-1][0]] + 1: runs.append(cur); cur = []
            cur.append((n, m))
        if cur: runs.append(cur)
        for run in runs:
            strong = [x for x in run if x[1]["conf"] == "high"]
            n, m = max(run, key=lambda x: x[1]["cap_cover"]); t = m["t"]; sid, tpl = self.scene_info(t)
            sev = "FAIL" if strong and (len(strong) >= 2 or any(not self.guarded(x[1]["t"]) for x in strong)) else "WARN"
            ev = R.evidence("CAP_FACE", t, _draw(self.final.get(n), [(m["box"], (0, 0, 255))], mask=m["mask"], label=f"caption over face {m['cap_cover']:.0%} @ {t:.2f}s"))
            R.add("CAP_FACE", sev, f"caption covers {m['cap_cover']:.0%} of the presenter's face: \"{m['text']}\"" + ("" if sev == "FAIL" else " (low confidence)"),
                  t=(run[0][1]["t"], run[-1][1]["t"]), scene=sid, template=tpl, evidence=ev,
                  fix="keep captions in the caption zone below the face for this pose (raise MarginV or move the presenter window); do not cover the face",
                  data={"worst_cover": m["cap_cover"], "samples": len(run), "confidence": m["conf"]})

    def _contrast(self, f, mk, t, sid, tpl, text, cth):
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        lum = lambda v: v ** 2.2
        core = cv2.erode((mk > 200).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        m1 = cv2.dilate((mk > 24).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ring = (cv2.dilate((mk > 24).astype(np.uint8), np.ones((25, 25), np.uint8)) > 0) & ~m1
        if core.sum() < 50 or ring.sum() < 50: return
        fill, bg = np.median(g[core]), np.median(g[ring])
        outline = (cv2.dilate(core.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & ~core & (mk > 24)
        ol = np.median(g[outline]) if outline.sum() > 20 else bg
        cr = lambda a, b: (max(lum(a), lum(b)) + .05) / (min(lum(a), lum(b)) + .05)
        c_bg, c_ol = cr(fill, bg), cr(fill, ol)
        if c_bg < cth["min_contrast"] and c_ol < cth["min_outline_contrast"]:
            self.rep.add("CAP_CONTRAST", "WARN", f"caption hard to read (contrast {c_bg:.1f}:1 to background, {c_ol:.1f}:1 to outline): \"{text}\"", t=t, scene=sid, template=tpl,
                         fix="thicker outline or a soft plate behind the caption (caption_zones.py)")

    # ───────────────────────── quality ─────────────────────────
    def check_quality(self):
        R = self.rep
        hi = [m for m in getattr(self, "faces", {}).values() if m["conf"] == "high" and m["out_frac"] < .03 and (m["visible"] or 0) >= .7]
        if len(hi) < 2: R.skip("QUALITY_SHARPNESS", "fewer than 2 clean, fully visible face matches"); return
        ratios = []
        for m in hi:
            n = int(round(m["t"] * self.fps)); o = self.clean.get(n) if self.clean else self.final.get(n); s = self.src.get(m["t"])
            x, y, w, h = [int(round(v)) for v in m["box"]]; sx, sy, sw, sh = [int(round(v)) for v in m["src_box"]]
            if w < 40 or h < 40 or x < 0 or y < 0 or x + w > o.shape[1] or y + h > o.shape[0] or sx < 0 or sy < 0: continue   # whole face only
            oc = cv2.cvtColor(o[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY)
            sc = cv2.cvtColor(s[sy:sy + sh, sx:sx + sw], cv2.COLOR_BGR2GRAY)
            if oc.size == 0 or sc.size == 0: continue
            ref = cv2.resize(sc, (oc.shape[1], oc.shape[0]), interpolation=cv2.INTER_AREA if sw > w else cv2.INTER_CUBIC)
            lap = lambda a: cv2.Laplacian(a, cv2.CV_32F).var()
            if lap(ref) < 5: continue
            ratios.append(lap(oc) / lap(ref))
        if not ratios: R.skip("QUALITY_SHARPNESS", "no usable face crops"); return
        med = float(np.median(ratios)); R.info["face_sharpness_ratio_median"] = round(med, 3)
        lim = self.th(None, "quality")["min_sharpness_ratio"]
        tpls = {s.get("template") for s in self.scenes} | {self.ctx.get("template")}
        lim = max([lim] + [self.cfg.for_template(t)["quality"]["min_sharpness_ratio"] for t in tpls if t])
        if med < lim:
            R.add("QUALITY_SHARPNESS", "WARN", f"presenter is softer than the source footage (sharpness {med:.2f}x the source at the same size, expected >= {lim:.2f})",
                  t=(hi[0]["t"], hi[-1]["t"]), fix="use the HD frame for the presenter (no extra blur/haze on her), encode at CRF <= 18")
        else: R.ran("QUALITY_SHARPNESS", f"{med:.2f}x source")
        up = float(np.median([m["upscale"] for m in hi])); R.info["presenter_upscale_median"] = round(up, 2)
        if up > self.th(None, "quality")["warn_upscale"]:
            R.add("QUALITY_UPSCALE", "WARN", f"presenter is shown {up:.1f}x larger than the uploaded footage's pixels: detail is limited by the source resolution",
                  fix="ask for a higher-resolution upload (1080p portrait / landscape)")
        else: R.ran("QUALITY_UPSCALE")

    # ───────────────────────── motion graphics ─────────────────────────
    def check_motion(self):
        R = self.rep
        if not self.scenes: R.skip("MOTION_ANIMATION", "no scene list (plan.json)"); return
        H, W = self.p["video"]["height"], self.p["video"]["width"]; frames = self.clean or self.final
        for i, s in enumerate(self.scenes):
            mth = self.th(s["t0"], "motion"); tpl = s.get("template") or self.ctx.get("template")
            if s.get("static") or tpl in mth["static_scenes"] or i in mth["static_scenes"] or not mth["expects_animation"] or self.static_span(s["t0"] + .2, s["t1"] - .2): continue
            ns = [n for n in self.samples if s["t0"] + .2 <= n / self.fps < s["t1"] - .2 and n in frames]
            if len(ns) < 3: continue
            diffs = []
            for a, b in zip(ns, ns[1:]):
                fa, fb = (cv2.resize(cv2.cvtColor(frames[k], cv2.COLOR_BGR2GRAY), (160, int(160 * H / W)), interpolation=cv2.INTER_AREA).astype(np.float32) for k in (a, b))
                keep = np.ones_like(fa, bool)
                for k in (a, b):   # ignore the presenter (she always moves)
                    m = getattr(self, "faces", {}).get(k)
                    if m and m["conf"] != "none":
                        x, y, w, h = m["head"]; s_ = 160 / W
                        keep[max(0, int((y - h * .2) * s_)):int((y + h * 3.5) * s_), max(0, int((x - w * 1.2) * s_)):int((x + w * 2.2) * s_)] = False
                diffs.append(float(np.abs(fa - fb)[keep].mean()) if keep.any() else 0.0)
            if max(diffs) < mth["min_graphics_change"]:
                R.add("MOTION_ANIMATION", "WARN", f"no motion-graphics change detected in this scene (max {max(diffs):.2f}); intended static scenes are fine",
                      t=(s["t0"], s["t1"]), scene=i, template=tpl, fix="if animation was expected, check the scene's update() runs; else mark the scene static")
        R.ran("MOTION_ANIMATION")

    # ───────────────────────── caption / speech sync ─────────────────────────
    def check_sync(self):
        R = self.rep; cues = getattr(self, "srt_cues", []) or [dict(start=e["start"], end=e["end"]) for e in self.ass_events]
        if not cues: R.skip("SYNC_SPEECH", "no captions"); return
        srcs = [self.ctx.get("audio_source"), self.ctx.get("source") if self.ctx.get("source") and not Path(self.ctx["source"]).is_dir() else None, self.ctx["video"]]
        pcm = None
        for s in srcs:
            if s and Path(s).exists():
                pcm = media.audio_pcm(s)
                if pcm is not None: R.info["sync_audio"] = str(s); break
        if pcm is None: R.skip("SYNC_SPEECH", "no audio"); return
        hop = 160; n = len(pcm) // hop
        e = 10 * np.log10(np.maximum(1e-10, (pcm[:n * hop].reshape(n, hop) ** 2).mean(1)))
        floor = np.percentile(e, 15); speech = e > max(floor + 12, e.max() - 45)
        speech = np.convolve(speech.astype(float), np.ones(15) / 15, "same") > .3   # 150 ms smoothing
        fr = 100.0; dur = n / fr
        cap = np.zeros(n, bool)
        for c in cues: cap[int(c["start"] * fr):int(c["end"] * fr)] = True
        sth = self.th("sync")
        lone = [c for c in cues if speech[int(c["start"] * fr):max(int(c["start"] * fr) + 1, int(c["end"] * fr))].mean() < sth["min_speech_overlap"]]
        def score(lag):
            k = int(lag * fr); a = np.roll(cap, k)
            return float((a & speech).sum()) / max(1, a.sum())
        lags = np.arange(-1.5, 1.51, .05); sc = [score(l) for l in lags]; best = float(lags[int(np.argmax(sc))])
        R.info["sync"] = {"speech_coverage_at_0": round(score(0), 3), "best_lag_s": round(best, 2), "best_coverage": round(max(sc), 3),
                          "method": "energy VAD vs caption on/off (not word alignment)"}
        if len(lone) > sth["warn_cues_without_speech"] * len(cues) and len(cues) >= 3:
            R.add("SYNC_SPEECH", "WARN", f"{len(lone)} of {len(cues)} captions are shown while nobody is speaking", t=(lone[0]["start"], lone[-1]["end"]),
                  fix="check caption timing against the voice", data=R.info["sync"])
        elif abs(best) >= sth["warn_lag_s"] and max(sc) - score(0) > .12:
            R.add("SYNC_SPEECH", "WARN", f"captions look offset from the speech by about {best:+.2f}s", fix="shift the caption timing", data=R.info["sync"])
        else: R.ran("SYNC_SPEECH", f"caption/speech coverage {score(0):.0%} (energy-based)")


def run(ctx, out_dir, config=None):
    return Post(ctx, out_dir, config).run()
