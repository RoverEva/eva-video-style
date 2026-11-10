#!/usr/bin/env python3
"""Merge per-section sound cue files into one timeline.
usage: merge_cues.py OUT.json s1_cues.json:0 s2_cues.json:37.4 ...   (offset = section start in seconds)"""
import json, sys
out, allc = sys.argv[1], []
for arg in sys.argv[2:]:
    path, off = arg.rsplit(':', 1)
    for c in json.load(open(path)):
        c[1] = round(c[1] + float(off), 4); allc.append(c)
json.dump(sorted(allc, key=lambda c: c[1]), open(out, 'w'))
print(out, len(allc), 'cues')
