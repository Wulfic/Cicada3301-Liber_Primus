#!/usr/bin/env python3
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
P24_DIR = DATA / 'p24_candidates_processed'
WORDLIST = DATA / 'wordlist.txt'
OUT = DATA / 'p24_hillclimb_results.txt'

def load_wordlist():
    if not WORDLIST.exists():
        return set()
    return set(w.strip().upper() for w in WORDLIST.read_text(encoding='utf-8', errors='ignore').split())

COMMON_TRIS = ['THE','AND','ING','ION','ENT','THA','NTH','ERE','HER','TER']

def trigram_score(text):
    t = re.sub('[^A-Z]','',text.upper())
    s=0
    for tri in COMMON_TRIS:
        s += t.count(tri)*5
    # reward vowels density moderately
    s += t.count('A') + t.count('E')*2 + t.count('I') + t.count('O') + t.count('U')
    return s

def word_score(text, words):
    s=0
    for w in re.findall(r"[A-Z']+", text.upper()):
        if w in words:
            s += 12
    return s

def score_text(text, words):
    return trigram_score(text) + word_score(text, words)

def read_candidate_files():
    if not P24_DIR.exists():
        return []
    return sorted(p for p in P24_DIR.iterdir() if p.suffix=='.txt')

def letters_in_text(text):
    return sorted(set(re.findall(r'[A-Z]', text.upper())))

def random_mapping(alphabet):
    letters = list(alphabet)
    perm = letters[:]
    random.shuffle(perm)
    return {a:b for a,b in zip(letters,perm)}

def decode_with_map(text, mapping):
    def sub(m):
        ch=m.group(0)
        return mapping.get(ch, ch)
    return re.sub('[A-Z]', lambda m: sub(m), text)

def hillclimb(text, words, restarts=8, iters=3000):
    alpha = letters_in_text(text)
    if not alpha:
        return text,0
    best_overall = None
    best_score = -10**9
    for r in range(restarts):
        mapping = random_mapping(alpha)
        dec = ''.join(mapping.get(ch,ch) if ch.isalpha() else ch for ch in text.upper())
        cur_score = score_text(dec, words)
        improved=True
        for i in range(iters):
            a,b = random.sample(alpha,2)
            # swap targets in mapping
            m2 = mapping.copy()
            m2[a], m2[b] = mapping[b], mapping[a]
            dec2 = ''.join(m2.get(ch,ch) if ch.isalpha() else ch for ch in text.upper())
            s2 = score_text(dec2, words)
            if s2 > cur_score:
                mapping = m2; cur_score = s2
        if cur_score > best_score:
            best_score = cur_score
            best_overall = ''.join(mapping.get(ch,ch) if ch.isalpha() else ch for ch in text.upper())
    return best_overall, best_score

def main():
    words = load_wordlist()
    files = read_candidate_files()
    if not files:
        print('No P24 candidate files found in', P24_DIR)
        return
    out_lines=[]
    for f in files:
        text = f.read_text(encoding='utf-8', errors='ignore')
        dec,sc = hillclimb(text, words, restarts=6, iters=2500)
        out_lines.append(f'FILE: {f.name} SCORE: {sc}\n')
        out_lines.append(dec + '\n\n')
        print('Processed', f.name, 'best_score=', sc)
    OUT.write_text('\n'.join(out_lines), encoding='utf-8')
    print('Wrote', OUT)

if __name__=='__main__':
    main()
