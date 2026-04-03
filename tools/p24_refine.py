#!/usr/bin/env python3
import re
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
P24_DIR = DATA / 'p24_candidates_processed'
INFILE = P24_DIR / 'candidate_w14_s25.txt'
OUT = DATA / 'p24_refine_results.txt'
WORDLIST = DATA / 'wordlist.txt'

COMMON_TRIS = ['THE','AND','ING','ION','ENT','THA','NTH','ERE','TIO']

def load_wordlist():
    p = WORDLIST
    if not p.exists(): return set()
    return set(w.strip().upper() for w in p.read_text(encoding='utf-8', errors='ignore').split())

def score_text(t, words):
    s=0
    u = re.sub('[^A-Z]','', t.upper())
    for tri in COMMON_TRIS: s += u.count(tri)*8
    # word matches
    for w in re.findall(r"[A-Z']+", t.upper()):
        if w in words: s += 25
        elif len(w)>3 and w[:3] in words: s += 6
    # vowel density
    s += u.count('E')*2 + u.count('A')
    return s

def letters_in_text(text):
    return sorted(set(re.findall(r'[A-Z]', text.upper())))

def random_map(alpha):
    a=list(alpha); b=a[:]; random.shuffle(b)
    return {x:y for x,y in zip(a,b)}

def apply_map(text,m):
    return ''.join(m.get(ch,ch) if ch.isalpha() else ch for ch in text.upper())

def refine(text, words, restarts=20, iters=20000):
    best_dec=None; best_score=-10**9
    alpha = letters_in_text(text)
    if not alpha:
        return text,0
    for r in range(restarts):
        m = random_map(alpha)
        dec = apply_map(text,m); sc = score_text(dec,words)
        for i in range(iters):
            a,b = random.sample(alpha,2)
            m2 = m.copy(); m2[a],m2[b] = m[b],m[a]
            dec2 = apply_map(text,m2); sc2 = score_text(dec2,words)
            if sc2>sc:
                m,sc = m2,sc2
        if sc>best_score:
            best_score=sc; best_dec=apply_map(text,m)
    return best_dec,best_score

def main():
    if not INFILE.exists():
        print('Input not found:', INFILE)
        return
    txt = INFILE.read_text(encoding='utf-8', errors='ignore')
    words = load_wordlist()
    dec,sc = refine(txt, words, restarts=24, iters=25000)
    OUT.write_text(f'SCORE={sc}\n\n'+dec, encoding='utf-8')
    print('Wrote', OUT, 'score=', sc)

if __name__=='__main__':
    main()
