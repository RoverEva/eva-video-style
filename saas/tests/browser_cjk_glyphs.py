#!/usr/bin/env python3
"""Chinese glyph rendering (no □ boxes) in a real browser.   browser_cjk_glyphs.py SITE [--local-auth API] [--shots DIR]

Runs Chromium twice: (1) with the machine's Chinese system fonts HIDDEN (fontconfig allow-list of Latin-only font
folders: the situation that produced □□□ on staging), (2) with the normal system fonts. For every page in 简体中文 it
collects each visible Chinese character together with the computed font of the element it sits in, draws it on a canvas
with exactly that font, and compares the pixels with a code point no font has (U+E000 / U+10FFFD, i.e. the missing-
glyph box) — a match or a blank drawing = □. Also: a control proves the hidden-fonts browser really has no Chinese font
(plain sans-serif "中" is a box there); English pages never download the Chinese font file (performance); English text
still uses Figtree / Bricolage Grotesque.
Pages: header + account menu, homepage (hero, How EVA works, studio, an error message, sign-in panel), Gallery + template
details, Pricing, video page, My Videos, My Account (signed in with --local-auth; staging shows the signed-out views)."""
import json, os, sys, tempfile, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

SITE = sys.argv[1].rstrip("/"); LOCAL = sys.argv[sys.argv.index("--local-auth") + 1].rstrip("/") if "--local-auth" in sys.argv else None
SHOTS = Path(sys.argv[sys.argv.index("--shots") + 1]) if "--shots" in sys.argv else None
fails, errs = [], []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m, flush=True)
    if not c: fails.append(m)

# a fontconfig that only sees Latin font folders (no CJK, no Korean/Japanese fonts with Han glyphs)
LATIN_DIRS = [d for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/truetype/liberation2",
                          "/usr/share/fonts/truetype/freefont", "/usr/share/fonts/truetype/ubuntu", "/usr/share/fonts/truetype/croscore") if Path(d).is_dir()]
fc = Path(tempfile.mkdtemp()) / "fonts.conf"
fc.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>' + "".join(f"<dir>{d}</dir>" for d in LATIN_DIRS)
              + f"<cachedir>{fc.parent}/cache</cachedir></fontconfig>")

GLYPHS_JS = r"""async () => {
  const isCJK = c => { const u = c.codePointAt(0); return (u >= 0x3400 && u <= 0x9FFF) || (u >= 0x3000 && u <= 0x303F) || (u >= 0xFF00 && u <= 0xFFEF); };
  const seen = new Map(), w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const n = w.currentNode, p = n.parentElement; if (!p || p.closest('script,style,[hidden]')) continue;
    const r = p.getBoundingClientRect(), cs = getComputedStyle(p); if (!r.width || !r.height || cs.visibility === 'hidden' || cs.display === 'none') continue;
    for (const ch of n.nodeValue) if (isCJK(ch) && ch.trim()) { const f = `${cs.fontStyle} ${cs.fontWeight} 40px ${cs.fontFamily}`; const k = f + '|' + ch; if (!seen.has(k)) seen.set(k, [ch, f, p.tagName.toLowerCase() + (p.className ? '.' + String(p.className).split(' ')[0] : '')]); }
  }
  await document.fonts.ready;
  for (const [ch, f] of seen.values()) { try { await document.fonts.load(f, ch); } catch (e) {} }
  const cv = document.createElement('canvas'); cv.width = 60; cv.height = 60; const ctx = cv.getContext('2d', { willReadFrequently: true });
  const draw = (s, f) => { ctx.clearRect(0, 0, 60, 60); ctx.font = f; ctx.fillStyle = '#000'; ctx.textBaseline = 'top'; ctx.fillText(s, 5, 5); return ctx.getImageData(0, 0, 60, 60).data; };
  const same = (a, b) => { for (let i = 3; i < a.length; i += 4) if (a[i] !== b[i]) return false; return true; };
  const blank = a => { for (let i = 3; i < a.length; i += 4) if (a[i]) return false; return true; };
  const bad = [], fams = new Set();
  for (const [ch, f, where] of seen.values()) {
    const g = draw(ch, f), t1 = draw('', f), t2 = draw('\u{10FFFD}', f);
    if (blank(g) || same(g, t1) || same(g, t2)) bad.push(ch + ' (' + where + ')');
    fams.add(f.split(' 40px ')[1].split(',')[0]);
  }
  const loaded = [...document.fonts].filter(x => x.family.replace(/"/g, '') === 'EVA SC' && x.status === 'loaded').map(x => x.weight);
  return { n: seen.size, chars: new Set([...seen.values()].map(x => x[0])).size, bad, fams: [...fams], evaSc: loaded };
}"""
CONTROL_JS = r"""() => { const cv = document.createElement('canvas'); cv.width = 60; cv.height = 60; const c = cv.getContext('2d');
  const d = s => { c.clearRect(0, 0, 60, 60); c.font = '40px sans-serif'; c.textBaseline = 'top'; c.fillText(s, 5, 5); return c.getImageData(0, 0, 60, 60).data.join(); };
  return d('中') === d('') || d('中') === d('\u{10FFFD}'); }"""

with sync_playwright() as p:
    for env_name, env in (("no system CJK fonts", dict(os.environ, FONTCONFIG_FILE=str(fc))), ("system fonts", dict(os.environ))):
        b = p.chromium.launch(env=env)
        for dev, vp in (("desktop", {"width": 1366, "height": 900}), ("phone", {"width": 390, "height": 844})):
            ctx = b.new_context(viewport=vp, device_scale_factor=1); pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
            font_reqs = []; pg.on("request", lambda r: "eva-sc-" in r.url and font_reqs.append(r.url))
            tag = f"{env_name} · {dev}"
            # English: no Chinese font download, Latin fonts unchanged
            pg.goto(SITE + "/?lang=en"); pg.wait_for_timeout(2500)
            fam = pg.evaluate("[getComputedStyle(document.body).fontFamily.split(',')[0], getComputedStyle(document.querySelector('.hero h1')).fontFamily.split(',')[0]]")
            check(not font_reqs and [x.strip('"') for x in fam] == ['Figtree', 'Bricolage Grotesque'], f"{tag} EN: Chinese font not downloaded ({len(font_reqs)} requests), Latin fonts {fam}")
            if env_name.startswith("no"): check(pg.evaluate(CONTROL_JS), f"{tag}: control — this browser has no Chinese system font (plain sans-serif 中 is a box)")
            pages = [("home", "/?lang=zh", None), ("home · How EVA works", "/", "#how"), ("home · studio + error message", "/", "studio"),
                     ("Gallery", "/templates.html", ".g-card"), ("template details", "/templates.html", "modal"), ("Pricing", "/pricing.html", ".pr-offer"),
                     ("video page", "/video.html?v=vdoesnotexist", None), ("My Videos", "/videos.html", None), ("My Account", "/account.html", None)]
            if LOCAL: pages += [("signed in · My Account", "/account.html", "auth"), ("signed in · My Videos + account menu", "/videos.html", "menu")]
            for name, path, act in pages:
                if act == "auth" and LOCAL:
                    tok = json.loads(urllib.request.urlopen(LOCAL + "/_local_signin?email=cjk%40example.com").read())
                    pg.evaluate("t => localStorage.setItem('eva:auth', t)", json.dumps(tok))
                pg.goto(SITE + path); pg.wait_for_timeout(2200)
                if act == "#how": pg.locator("#how").scroll_into_view_if_needed(); pg.wait_for_timeout(600)
                if act == "studio":
                    pg.locator("#studio").scroll_into_view_if_needed(); pg.click("#go"); pg.wait_for_timeout(800)
                if act == "modal": pg.click(".g-card[data-id=T17]"); pg.wait_for_selector("#gDlg[open]"); pg.wait_for_timeout(500)
                if act == "menu": pg.click(".avatar"); pg.wait_for_timeout(300)
                r = pg.evaluate(GLYPHS_JS)
                check(r["chars"] > 0 and not r["bad"], f"{tag} 简体中文 {name}: {r['chars']} Chinese characters ({r['n']} char/font pairs) all drawn as real glyphs; □: {r['bad'][:8]}")
                if SHOTS and name in ("home", "Gallery", "Pricing", "signed in · My Videos + account menu") and env_name.startswith("no"):
                    SHOTS.mkdir(parents=True, exist_ok=True); pg.screenshot(path=str(SHOTS / f"zh_nocjk_{name.split(' ')[0].replace('·', '')}_{dev}.png"))
            check(font_reqs and all("eva-sc-" in u for u in font_reqs), f"{tag} ZH: EVA SC subset fetched only in Chinese ({len(set(font_reqs))} files)")
            pg.evaluate("localStorage.removeItem('eva:auth')"); pg.goto(SITE + "/?lang=en"); ctx.close()
        b.close()
check(not errs, f"no page errors {errs[:2]}")
print("browser cjk glyphs:", "ok" if not fails else f"{len(fails)} FAILED"); sys.exit(1 if fails else 0)
