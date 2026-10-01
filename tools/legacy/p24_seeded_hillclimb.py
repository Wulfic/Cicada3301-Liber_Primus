#!/usr/bin/env python3
import re
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
P24_DIR = DATA / 'p24_candidates_processed'
ORIG = P24_DIR / 'candidate_w14_s25.txt'
APPLIED = DATA / 'p24_targeted_map_applied.txt'
WORDLIST = DATA / 'wordlist.txt'
OUT = DATA / 'p24_seeded_refine.txt'

def load_wordlist():
    p = WORDLIST
    if not p.exists(): return set()
    return set(w.strip().upper() for w in p.read_text(encoding='utf-8', errors='ignore').split())

def score_text(t, words):
    u = re.sub('[^A-Z]','', t.upper())
    s = 0
    for tri,wt in [('THE',8),('AND',6),('ING',6),('ION',4),('ENT',4)]:
        s += u.count(tri)*wt
    for w in re.findall(r"[A-Z']+", t.upper()):
        if w in words: s += 20
    s += u.count('E')*2 + u.count('A')
    return s

def build_seed_mapping(orig, applied):
    # orig and applied aligned by letters in prior script
    pairs=[]
    ai=0; bi=0
    while ai<len(orig) and bi<len(applied):
        ca=orig[ai]; cb=applied[bi]
        if ca.isalpha() and (cb.isalpha() or cb=='_'):
            pairs.append((ca.upper(), cb.upper()))
            ai+=1; bi+=1
        else:
            if not ca.isalpha(): ai+=1
            if not cb.isalpha(): bi+=1
    seed_map = {}
    mapped_plain=set()
    for c,p in pairs:
        if p!='_':
            seed_map[c]=p; mapped_plain.add(p)
    return seed_map, mapped_plain

def letters_in_text(text):
    return sorted(set(re.findall(r'[A-Z]', text.upper())))

def random_assignment(domain, codomain):
    dom=list(domain); cod=list(codomain)
    random.shuffle(cod)
    return {d:c for d,c in zip(dom,cod)}

def apply_full_map(orig, full_map):
    out=[]
    for ch in orig:
        if ch.isalpha(): out.append(full_map.get(ch.upper(),'_'))
        else: out.append(ch)
    return ''.join(out)

def seeded_hillclimb(orig, seed_map, mapped_plain, words, restarts=12, iters=8000):
    alpha = letters_in_text(orig)
    unmapped = [c for c in alpha if c not in seed_map]
    plaintext_alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    # restrict codomain to letters that appear in applied or common letters
    # allow any uppercase letter as target
    best_dec=None; best_score=-10**9
    for r in range(restarts):
        # build initial mapping: seed_map fixed; assign random to unmapped
        available = [c for c in plaintext_alphabet if c not in mapped_plain]
        assign = random_assignment(unmapped, available)
        full_map = {**seed_map, **assign}
        dec = apply_full_map(orig, full_map); sc = score_text(dec, words)
        for i in range(iters):
            if not unmapped: break
            a,b = random.sample(unmapped,2)
            m2 = full_map.copy()
            m2[a], m2[b] = full_map[b], full_map[a]
            dec2 = apply_full_map(orig, m2); s2 = score_text(dec2, words)
            if s2>sc:
                full_map, sc = m2, s2
        if sc>best_score:
            best_score=sc; best_dec=apply_full_map(orig, full_map)
    return best_dec, best_score

def main():
    if not ORIG.exists() or not APPLIED.exists():
        print('Missing inputs')
        return
    orig = ORIG.read_text(encoding='utf-8', errors='ignore')
    applied = APPLIED.read_text(encoding='utf-8', errors='ignore')
    # skip header if file has SCORE= prefix
    if '\n\n' in applied:
        applied = applied.split('\n\n',1)[1]
    seed_map, mapped_plain = build_seed_mapping(orig, applied)
    words = load_wordlist()
    dec, sc = seeded_hillclimb(orig, seed_map, mapped_plain, words, restarts=16, iters=12000)
    OUT.write_text(f'SCORE={sc}\n\n'+dec, encoding='utf-8')
    print('Wrote', OUT, 'score=', sc)

if __name__=='__main__':
    main()
