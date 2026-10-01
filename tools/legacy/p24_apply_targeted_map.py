#!/usr/bin/env python3
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
P24_DIR = DATA / 'p24_candidates_processed'
ORIG = P24_DIR / 'candidate_w14_s25.txt'
REF = DATA / 'p24_refine_results.txt'
OUT = DATA / 'p24_targeted_map_applied.txt'
WORDLIST = DATA / 'wordlist.txt'

def load_wordlist():
    p = WORDLIST
    if not p.exists():
        return set()
    return set(w.strip().upper() for w in p.read_text(encoding='utf-8', errors='ignore').split())

def score_text(t, words):
    u = re.sub('[^A-Z]','', t.upper())
    s = sum(u.count(tri) for tri in ['THE','AND','ING','ION'])*10
    for w in re.findall(r"[A-Z']+", t.upper()):
        if w in words: s += 25
    return s

def main():
    if not ORIG.exists() or not REF.exists():
        print('Missing input files')
        return
    orig = ORIG.read_text(encoding='utf-8', errors='ignore')
    ref = REF.read_text(encoding='utf-8', errors='ignore')
    # extract decoded block (after SCORE=... blank line)
    m = re.split(r'\n\n', ref, maxsplit=1)
    if len(m)<2:
        print('Refined decode not found')
        return
    dec = m[1].strip()
    # find APPLE occurrences
    targets = []
    for match in re.finditer(r'APPLE', dec):
        start = match.start()
        targets.append(start)
    mapping = {}
    # align dec and orig by characters (count only letters and spaces)
    def aligned_pairs(a,b):
        ai=0; bi=0
        pairs=[]
        while ai<len(a) and bi<len(b):
            ca=a[ai]; cb=b[bi]
            if ca.isalpha() and cb.isalpha():
                pairs.append((cb.upper(), ca.upper()))
                ai+=1; bi+=1
            else:
                # keep non-letters in sync by advancing both when they match
                if not ca.isalpha(): ai+=1
                if not cb.isalpha(): bi+=1
        return pairs

    pairs = aligned_pairs(orig, dec)
    # build mapping from cipher->plain using APPLE positions
    for pos in targets:
        # find corresponding index in pairs for pos-th letter in dec
        # count letters up to pos
        letter_index = sum(1 for i,ch in enumerate(dec[:pos]) if ch.isalpha())
        # map next 5 letters
        for k in range(5):
            idx = letter_index + k
            if idx < len(pairs):
                ciph, plain = pairs[idx]
                if ciph in mapping and mapping[ciph] != plain:
                    # conflict, skip
                    continue
                mapping[ciph] = plain

    # apply mapping to original
    applied = []
    for ch in orig:
        if ch.isalpha():
            chU = ch.upper()
            if chU in mapping:
                applied.append(mapping[chU])
            else:
                applied.append('_')
        else:
            applied.append(ch)
    out_text = ''.join(applied)
    words = load_wordlist()
    sc = score_text(out_text, words)
    OUT.write_text(f'SCORE={sc}\n\n'+out_text, encoding='utf-8')
    print('Wrote', OUT, 'score=', sc)

if __name__=='__main__':
    main()
