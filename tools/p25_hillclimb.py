#!/usr/bin/env python3
import re
import random
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
P25_OFF = DATA / 'p25_offset_results.txt'
OUT = DATA / 'p25_hillclimb_results.txt'
REF = BASE / 'reference'
PAGES = BASE / 'pages'

RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]

def load_page_indices(page=25):
    p = PAGES / f"page_{page:02d}" / "runes.txt"
    s = p.read_text(encoding='utf-8')
    return [RUNE_TO_IDX[c] for c in s if c in RUNE_TO_IDX]

def load_liber_al_indices():
    p = REF / 'liber_al_vel_legis.txt'
    s = p.read_text(encoding='utf-8', errors='ignore').upper()
    rev = {v:i for i,v in enumerate(IDX_TO_LETTER)}
    res=[]
    i=0
    while i<len(s):
        matched=False
        for length in (3,2,1):
            if i+length<=len(s):
                chunk = s[i:i+length]
                if chunk in rev:
                    res.append(rev[chunk]); i+=length; matched=True; break
        if not matched:
            i+=1
    return res

def decrypt_with_key(cipher, key, mode='beaufort'):
    res=[]
    klen=len(key)
    for i,c in enumerate(cipher):
        k = key[i % klen]
        if mode=='beaufort': p=(k - c) % 29
        elif mode=='sub': p=(c - k) % 29
        elif mode=='add': p=(c + k) % 29
        res.append(p)
    return res

def indices_to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

COMMON_TRIS = ['THE','AND','ING','ION','ENT','THA','NTH','ERE']

def trigram_score(text):
    t=re.sub('[^A-Z]','',text.upper())
    s=0
    for tri in COMMON_TRIS:
        s += t.count(tri)*5
    s += t.count('E')*2 + t.count('A') + t.count('I') + t.count('O')
    return s

def score_text(text):
    return trigram_score(text)

def letters_in_text(text):
    return sorted(set(re.findall(r'[A-Z]', text.upper())))

def random_mapping(alpha):
    letters=list(alpha)
    perm=letters[:]; random.shuffle(perm)
    return {a:b for a,b in zip(letters,perm)}

def apply_map(text,mapping):
    return ''.join(mapping.get(ch,ch) if ch.isalpha() else ch for ch in text.upper())

def hillclimb_simple(text, restarts=6, iters=2000):
    alpha = letters_in_text(text)
    if not alpha:
        return text,0
    best_s=-10**9; best_dec=None
    for r in range(restarts):
        mapping = random_mapping(alpha)
        dec = apply_map(text,mapping)
        cur_s = score_text(dec)
        for i in range(iters):
            a,b = random.sample(alpha,2)
            m2 = mapping.copy(); m2[a],m2[b] = mapping[b],mapping[a]
            dec2 = apply_map(text,m2); s2 = score_text(dec2)
            if s2>cur_s:
                mapping = m2; cur_s=s2
        if cur_s>best_s:
            best_s=cur_s; best_dec=apply_map(text,mapping)
    return best_dec,best_s

def parse_top_offsets(n=6):
    if not P25_OFF.exists(): return []
    lines = P25_OFF.read_text(encoding='utf-8').splitlines()
    res=[]
    for L in lines:
        m=re.search(r'offset=(\d+)\s+mode=(\w+)', L)
        if m:
            off=int(m.group(1)); mode=m.group(2)
            res.append((off,mode))
        if len(res)>=n: break
    seen=set(); uniq=[]
    for t in res:
        if t not in seen: seen.add(t); uniq.append(t)
    return uniq

def main():
    cipher = load_page_indices(25)
    la = load_liber_al_indices()
    tops = parse_top_offsets(10)
    out=[]
    for off,mode in tops:
        n=len(cipher)
        key = (la*(((n+len(la)-1)//len(la))+1))[off:off+n]
        plain = decrypt_with_key(cipher,key,mode)
        txt = indices_to_runeglish(plain)
        dec,sc = hillclimb_simple(txt, restarts=8, iters=3000)
        out.append(f'OFFSET={off} MODE={mode} SCORE={sc}\n')
        out.append(dec+'\n\n')
        print('Processed offset',off,'mode',mode,'score',sc)
    OUT.write_text('\n'.join(out), encoding='utf-8')
    print('Wrote',OUT)

if __name__=='__main__':
    main()
