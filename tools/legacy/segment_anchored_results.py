#!/usr/bin/env python3
"""Segment best plaintexts from anchored hillclimb results.
Reads JSON files in data/anchored_results/, segments `best_plain_snippet` using
`tools/segment_runeglish.segment_text`, and writes per-run *_seg.json files.
"""
import json
from pathlib import Path
import sys
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
IN_DIR = DATA / 'anchored_results'

sys.path.insert(0, str(BASE / 'tools'))
import solve_p21_30 as solver
import segment_runeglish as seg


def process_file(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        j = json.load(f)
    txt = j.get('best_plain_snippet') or j.get('best_plain') or ''
    if not txt:
        print(f'No plaintext in {path.name}, skipping')
        return None
    text = ''.join(ch for ch in txt if ch.isalpha()).upper()
    solver.load_wordlist()
    score, words = seg.segment_text(text, solver.COMMON_WORDS, solver.gp_word_matches_english)
    matches = [solver.gp_word_matches_english(w) for w in words]
    out = {
        'source': path.name,
        'segment_score': score,
        'words': words,
        'matches': matches,
    }
    out_path = path.with_name(path.stem + '_seg.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    print(f'Wrote {out_path.name}: score={score}, words={len(words)}')
    return out_path


def main():
    if not IN_DIR.exists():
        print('No anchored_results directory found at', IN_DIR)
        return
    files = sorted([p for p in IN_DIR.glob('p*_*.json') if p.name != 'summary.json'])
    results = []
    for p in files:
        try:
            outp = process_file(p)
            if outp:
                results.append(str(outp))
        except Exception as e:
            print('Error processing', p.name, e)
    print('\nProcessed', len(results), 'files')

if __name__ == '__main__':
    main()
