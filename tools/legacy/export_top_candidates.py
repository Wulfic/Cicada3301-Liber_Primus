#!/usr/bin/env python3
"""Export top-ranked anchored candidates to a Markdown report.
Reads `data/anchored_results/ranked_summary.json` and per-run _seg.json files,
then writes `data/anchored_results/top_ranked_candidates.md` with the top 12.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AR = BASE / 'data' / 'anchored_results'
RANKED = AR / 'ranked_summary.json'
OUT = AR / 'top_ranked_candidates.md'

if not RANKED.exists():
    print('Ranked summary not found:', RANKED)
    raise SystemExit(1)

entries = json.load(open(RANKED, 'r', encoding='utf-8'))

top = entries[:12]

def clean_words(words):
    # join tokens to form a readable line; lower-case and capitalize first char
    s = ' '.join(words)
    s = s.replace('  ', ' ')
    s = s.lower()
    if len(s) > 0:
        s = s[0].upper() + s[1:]
    return s

md = []
md.append('# Top Ranked Anchored Candidates')
md.append('Generated from anchored hillclimb runs (pages 21–30).')
md.append('')
for e in top:
    page = e.get('page')
    mode = e.get('mode')
    desc = e.get('desc')
    seg_score = e.get('seg_score')
    quad_score = e.get('quad_score')
    word_score = e.get('word_score')
    snippet = e.get('snippet') or ''
    mapping = e.get('mapping')
    file = e.get('file')

    md.append(f"## Page {page} — {mode}")
    md.append(f"- Candidate: **{desc}**")
    md.append(f"- Scores: seg={seg_score}  quad={quad_score}  word={word_score}")
    md.append(f"- Source file: `{file}`")
    if mapping:
        md.append(f"- Mapping: `{mapping}`")

    # try to load segmented version
    seg_path = AR / (Path(file).stem + '_seg.json')
    seg_text = None
    if seg_path.exists():
        try:
            sj = json.load(open(seg_path, 'r', encoding='utf-8'))
            words = sj.get('words', [])
            seg_text = clean_words(words)
        except Exception:
            seg_text = None

    md.append('')
    md.append('**Raw snippet (top 400 chars):**')
    md.append('')
    md.append('```')
    md.append(snippet)
    md.append('```')
    md.append('')
    if seg_text:
        md.append('**Segmented / cleaned text:**')
        md.append('')
        md.append('```')
        md.append(seg_text)
        md.append('```')
        md.append('')
    md.append('---')
    md.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

print('Wrote', OUT)
