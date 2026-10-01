#!/usr/bin/env python3
"""Anchored hillclimb across modes for Page 21.

For each mode in ['sub','add','beaufort'] this script:
 - decrypts using the verified key
 - applies the chosen columnar candidate (w=7, perm=(5,1,0,3,6,2,4))
 - transliterates to ASCII
 - runs `mono_sub_solver.run_hillclimb` with anchors and given iters/restarts
 - saves best results to data/anchored_p21_modes_results.json

Usage example:
  .venv\Scripts\python.exe -u tools/anchored_hillclimb_modes_p21.py --restarts 4 --iters 1000000 --fixed THE

"""
import argparse
import json
import time
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
TOOLS_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(TOOLS_DIR))

import decrypt_page_with_verified_key as dpv
import mono_sub_solver as mss

TOKENS = ['TH','NG','EO','OE','AE','IO','EA', 'F','U','O','R','C','G','W','H','N','I','J','P','X','S','T','B','E','M','L','A','Y']
PHON = {
    'F':'f','U':'u','TH':'th','O':'o','R':'r','C':'c','G':'g','W':'w',
    'H':'h','N':'n','I':'i','J':'j','EO':'e','P':'p','X':'x','S':'s',
    'T':'t','B':'b','E':'e','M':'m','L':'l','NG':'ng','OE':'o','D':'d',
    'A':'a','AE':'ae','Y':'y','IO':'io','EA':'ea'
}


def transliterate_runeglish(s):
    i = 0
    out = []
    while i < len(s):
        matched = False
        for tok in TOKENS:
            if s.startswith(tok, i):
                out.append(PHON.get(tok, tok.lower()))
                i += len(tok)
                matched = True
                break
        if not matched:
            out.append(s[i].lower())
            i += 1
    return ''.join(out)


def reverse_columnar(text_indices, width, col_order=None):
    n = len(text_indices)
    nrows = (n + width - 1) // width
    full_cols = n % width if n % width != 0 else width
    if col_order is None:
        col_order = list(range(width))
    col_lengths = []
    for c in range(width):
        if n % width == 0:
            col_lengths.append(nrows)
        else:
            if c < full_cols:
                col_lengths.append(nrows)
            else:
                col_lengths.append(nrows - 1)
    columns = {}
    pos = 0
    for read_idx in range(width):
        col_idx = col_order[read_idx]
        clen = col_lengths[col_idx]
        columns[col_idx] = text_indices[pos:pos+clen]
        pos += clen
    result = []
    for row in range(nrows):
        for col in range(width):
            if row < len(columns.get(col, [])):
                result.append(columns[col][row])
    return result


def run_for_mode(mode, key, cipher_indices, perm, width, restarts, iters, fixed_letters, qg, floor, corpus):
    print(f"\n=== Mode: {mode} ===")
    plain_indices = dpv.decrypt_indices(cipher_indices, key, mode=mode)
    reordered = reverse_columnar(plain_indices, width, list(perm))
    runeglish = dpv.indices_to_runeglish(reordered)
    translit = transliterate_runeglish(runeglish)
    cipher_text = ''.join(ch for ch in translit.upper() if 'A' <= ch <= 'Z')
    print(f"Cipher length: {len(cipher_text)}")

    best = (None, -1e12, None, None)
    start = time.time()
    for r in range(restarts):
        print(f'  Restart {r+1}/{restarts} (iters={iters})...')
        t0 = time.time()
        plain_candidate, mapping, score = mss.run_hillclimb(cipher_text, qg, floor, corpus, iters=iters, fixed=fixed_letters)
        t = time.time() - t0
        print(f'   -> score={score:.6f} (t={t:.1f}s)')
        if score > best[1]:
            best = (f'restart_{r+1}', score, plain_candidate, mapping)
        # save intermediate results to disk to avoid losing long runs
        out = {
            'mode': mode,
            'restart': r+1,
            'iters': iters,
            'score': score,
            'plain_snippet': (plain_candidate or '')[:800],
            'mapping': mss.pretty_map(mapping)
        }
        # append to a log file
        logp = BASE / 'data' / 'anchored_p21_modes_log.jsonl'
        with open(logp, 'a', encoding='utf-8') as lf:
            lf.write(json.dumps(out) + '\n')
    total = time.time() - start
    print(f' Best score for mode {mode}: {best[1]:.6f} (t={total:.1f}s)')
    return best, cipher_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--restarts', type=int, default=4)
    parser.add_argument('--iters', type=int, default=1000000)
    parser.add_argument('--fixed', type=str, default='THE', help='letters to fix (e.g. THE,OUT)')
    parser.add_argument('--modes', type=str, default='sub,add,beaufort', help='comma separated modes')
    parser.add_argument('--page', type=int, default=21)
    args = parser.parse_args()

    modes = [m.strip() for m in args.modes.split(',') if m.strip()]
    restarts = args.restarts
    iters = args.iters

    page = args.page
    print(f'Page {page}: modes={modes} restarts={restarts} iters={iters}')

    vks = dpv.load_verified_keys()
    key = vks.get(str(page))
    if not key:
        print('No verified key for page', page)
        return
    text = dpv.load_page_runes(page)
    if not text:
        print('No runes.txt for page', page)
        return
    cipher_indices = dpv.extract_indices(text)

    perm = (5,1,0,3,6,2,4)
    width = 7

    fixed_letters = set(ch for ch in args.fixed.upper() if 'A' <= ch <= 'Z')

    corpus = mss.load_corpus_text()
    qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')

    results = {}
    for mode in modes:
        best, cipher_text = run_for_mode(mode, key, cipher_indices, perm, width, restarts, iters, fixed_letters, qg, floor, corpus)
        label, score, plain, mapping = best
        results[mode] = {
            'label': label,
            'score': score,
            'plain_snippet': (plain or '')[:2000],
            'mapping': mss.pretty_map(mapping) if mapping else None,
            'cipher_text_length': len(cipher_text)
        }
        # write intermediate results file
        outp = BASE / 'data' / 'anchored_p21_modes_results.json'
        with open(outp, 'w', encoding='utf-8') as outf:
            json.dump(results, outf, indent=2)

    print('\n=== All Modes Completed ===')
    print('Results written to data/anchored_p21_modes_results.json and log appended to data/anchored_p21_modes_log.jsonl')

if __name__ == '__main__':
    main()
