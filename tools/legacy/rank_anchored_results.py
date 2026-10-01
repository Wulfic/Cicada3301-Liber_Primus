#!/usr/bin/env python3
"""Rank anchored hillclimb results by segmentation, quadgram, and word-score.
Writes `data/anchored_results/ranked_summary.json` and prints top 12 runs.
"""
import json
from pathlib import Path
import statistics

BASE = Path(__file__).resolve().parent.parent
AR = BASE / 'data' / 'anchored_results'
OUT = AR / 'ranked_summary.json'

files = sorted([p for p in AR.glob('p*_*.json') if p.name != 'summary.json' and not p.name.endswith('_seg.json')])
entries = []
for f in files:
    try:
        j = json.load(open(f, 'r', encoding='utf-8'))
    except Exception as e:
        print('Skipping', f.name, e)
        continue
    seg_path = f.with_name(f.stem + '_seg.json')
    seg_score = None
    if seg_path.exists():
        try:
            seg_j = json.load(open(seg_path, 'r', encoding='utf-8'))
            seg_score = seg_j.get('segment_score')
        except Exception:
            seg_score = None
    quad_score = j.get('best_score')
    word_score = j.get('candidate_word_score')
    page = j.get('page')
    mode = j.get('mode')
    desc = j.get('candidate_desc')
    snippet = (j.get('best_plain_snippet') or '')[:400]
    mapping = j.get('mapping')
    entries.append({
        'file': f.name,
        'page': page,
        'mode': mode,
        'desc': desc,
        'seg_score': seg_score,
        'quad_score': quad_score,
        'word_score': word_score,
        'cipher_len': j.get('cipher_len'),
        'best_restart': j.get('best_restart'),
        'snippet': snippet,
        'mapping': mapping
    })

# Helper to compute rank (1 is best). None values get worst rank = n+1
n = len(entries)

def rank_by(key, reverse=True):
    vals = [e[key] for e in entries]
    # replace None with a very low value for reverse sort (i.e., worst)
    def val_for(v):
        return (v if v is not None else float('-inf')) if reverse else (v if v is not None else float('inf'))
    sorted_vals = sorted([v for v in vals if v is not None], reverse=reverse)
    ranks = {}
    for i, v in enumerate(sorted_vals, 1):
        if v not in ranks:
            ranks[v] = i
    ranks_default = n + 1
    result = []
    for e in entries:
        v = e[key]
        if v is None:
            result.append(ranks_default)
        else:
            result.append(ranks.get(v, ranks_default))
    return result

seg_ranks = rank_by('seg_score', reverse=True)
quad_ranks = rank_by('quad_score', reverse=True)
word_ranks = rank_by('word_score', reverse=True)

for i, e in enumerate(entries):
    e['seg_rank'] = seg_ranks[i]
    e['quad_rank'] = quad_ranks[i]
    e['word_rank'] = word_ranks[i]
    e['combined_rank'] = e['seg_rank'] + e['quad_rank'] + e['word_rank']

entries.sort(key=lambda x: (x['combined_rank'], x.get('seg_score') or 0), reverse=False)

# assign final rank
for i, e in enumerate(entries, 1):
    e['final_rank'] = i

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(entries, f, indent=2)

# Print top 12
print('Top runs by combined rank:')
for e in entries[:12]:
    print(f"P{e['page']:02d} {e['mode']:8s} rank={e['final_rank']:2d} combined={e['combined_rank']:3d} seg={e['seg_score']:7} quad={e['quad_score']:9} word={e['word_score']:7} desc={e['desc']}")

print('\nWrote', OUT)
