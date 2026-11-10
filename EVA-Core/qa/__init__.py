"""Eva Video Style · automated video QA.

Stage A (pre-render)  qa.pre.run(ctx)   input metadata, SRT, plan/template config, face calibration, page trace (assets,
                                         fonts, page errors, presenter geometry, text over face, animation).
Stage B (post-render) qa.post.run(ctx)  the rendered file: streams/format/duration, black/blank/frozen spans, presenter
                                         tracking (crop, scale, stretch, visibility, sharpness), caption masks (frame edge,
                                         safe area, face, lines, contrast, burn-in), SRT/ASS timing, caption/speech sync.

Severity: FAIL = confirmed critical defect (blocks delivery), WARN = uncertain / subjective, PASS = validated.
CLI: python3 -m qa --help
"""
__version__ = "1.0.0"
