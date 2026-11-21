#!/usr/bin/env python3
"""Compile compact .txt long-form scripts (src/*.txt) into scripts/*.json.

Format:  TITLE …   SUBJ zodiac|mbti KEY   Q a/b   B a/b   TAG a/b   then '# 章节名 motif' followed by one card per line.
Cards: '/' splits lines, leading '*' marks a key card, 【】 marks gold words.
"""
import json, os, sys, glob
MOTIFS = set('blueprint tree formation morph lanterns bloom lightlink fireworks checklist shield pillars circle gears brush target spotlight ignite sunburst arrows garden harvest summit planes balance ripples moonrise phoenix school duality messages heart bolts'.split())
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'mbti')); from vis import STATIC as VIS
OUTRO = ['这里是洞悉', '看见表象之外', '我们下期见']

def compile_txt(path):
    d = {'chapters': [], 'outro': OUTRO}; hook = {}
    for raw in open(path, encoding='utf-8'):
        l = raw.strip()
        if not l or l.startswith('//'): continue
        if l.startswith('# '):
            name, motif = l[2:].rsplit(' ', 1); assert motif in MOTIFS, (path, motif)
            d['chapters'].append({'name': name.strip(), 'motif': motif, 'cards': []}); continue
        k, _, v = l.partition(' ')
        if k == 'TITLE': d['title'] = v
        elif k == 'SUBJ': a, b = v.split(); d['subject'] = {a: b}
        elif k == 'Q': hook['q'] = v.split('/')
        elif k == 'B': hook['beats'] = v.split('/')
        elif k == 'TAG': hook['tagline'] = v
        else:
            import re
            for v in re.findall(r'\{([a-z0-9]+)', l): assert v in VIS, (path, v)
            d['chapters'][-1]['cards'].append(l)
    d['hook'] = hook
    return d

if __name__ == '__main__':
    for p in sorted(glob.glob(os.path.join(HERE, 'src', '*.txt'))) if len(sys.argv) < 2 else sys.argv[1:]:
        d = compile_txt(p); out = os.path.join(HERE, 'scripts', os.path.basename(p)[:-4] + '.json')
        with open(out, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False, indent=1)
        print(out, len(d['chapters']), sum(len(c['cards']) for c in d['chapters']))
