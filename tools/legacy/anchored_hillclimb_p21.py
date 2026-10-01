#!/usr/bin/env python3
"""Anchored hillclimb for Page 21.
Creates the columnar perm candidate (w=7, perm=(5,1,0,3,6,2,4)),
transliterates it, then runs mono-sub hillclimb with fixed letters.
"""
import sys
import time
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

import decrypt_page_with_verified_key as dpv
import mono_sub_solver as mss

# reverse_columnar copied from refine_and_batch
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

# transliteration tokens
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


def main():
    page = 21
    print(f"Anchored hillclimb: page {page}")
    vks = dpv.load_verified_keys()
    key = vks.get(str(page))
    if not key:
        print('No verified key found for page 21')
        return
    text = dpv.load_page_runes(page)
    if not text:
        print('No runes.txt for page 21')
        return
    cipher_indices = dpv.extract_indices(text)
    # decrypt with verified key (sub)
    plain = dpv.decrypt_indices(cipher_indices, key, mode='sub')
    # apply chosen candidate: width=7 perm=(5,1,0,3,6,2,4)
    perm = (5,1,0,3,6,2,4)
    reordered = reverse_columnar(plain, 7, list(perm))
    runeglish = dpv.indices_to_runeglish(reordered)
    translit = transliterate_runeglish(runeglish)
    cipher_text = ''.join(ch for ch in translit.upper() if 'A' <= ch <= 'Z')
    print(f"Cipher length: {len(cipher_text)}")

    # prepare scoring
    corpus = mss.load_corpus_text()
    qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')

    restarts = 20
    iters = 50000
    fixed_letters = set(list('THE'))

    best_overall = (None, -1e12, None, None)
    start_time = time.time()
    for r in range(restarts):
        t0 = time.time()
        print(f'Running restart {r+1}/{restarts}... (iters={iters})')
        plain_candidate, mapping, score = mss.run_hillclimb(cipher_text, qg, floor, corpus, iters=iters, fixed=fixed_letters)
        elapsed = time.time() - t0
        print(f' -> score={score:.6f} (t={elapsed:.1f}s)')
        if score > best_overall[1]:
            best_overall = (f'restart_{r+1}', score, plain_candidate, mapping)
    total = time.time() - start_time
    print('\n=== Anchored Hillclimb Result ===')
    print('Best label:', best_overall[0])
    print('Best score:', best_overall[1])
    print('Plain snippet:', (best_overall[2] or '')[:500])
    try:
        print('Mapping:', mss.pretty_map(best_overall[3]))
    except Exception:
        pass
    print(f'Total time: {total:.1f}s')

if __name__ == '__main__':
    main()
