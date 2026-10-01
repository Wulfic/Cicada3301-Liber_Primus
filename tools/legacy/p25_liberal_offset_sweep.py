#!/usr/bin/env python3
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"
REF = BASE / "reference"

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

COMMON_3GRAMS = {'THE':100,'AND':80,'ING':60,'ION':50,'ENT':40,'TIO':40}

def load_page_indices(page):
    p = PAGES_DIR / f"page_{page:02d}" / "runes.txt"
    s = p.read_text(encoding='utf-8')
    return [RUNE_TO_IDX[c] for c in s if c in RUNE_TO_IDX]

def load_liber_al_indices():
    p = REF / 'liber_al_vel_legis.txt'
    s = p.read_text(encoding='utf-8', errors='ignore').upper()
    # map letters to GP indices
    rev = {v:i for i,v in enumerate(IDX_TO_LETTER)}
    res = []
    i=0
    while i < len(s):
        matched=False
        for length in (3,2):
            if i+length<=len(s):
                chunk = s[i:i+length]
                if chunk in rev:
                    res.append(rev[chunk]); i+=length; matched=True; break
        if not matched:
            ch = s[i]
            if ch=='K': ch='C'
            if ch=='V': ch='U'
            if ch in rev:
                res.append(rev[ch])
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

def trigram_score(text):
    t=text.upper()
    s=0
    for i in range(len(t)-2):
        tri=t[i:i+3]
        s+=COMMON_3GRAMS.get(tri,0)
    return s

def compute_ioc(indices):
    n=len(indices)
    if n<2: return 0.0
    counts=Counter(indices)
    return 29 * sum(c*(c-1) for c in counts.values())/(n*(n-1))

def main():
    page=25
    cipher=load_page_indices(page)
    la=load_liber_al_indices()
    n=len(cipher)
    out=Path(DATA_DIR)/'p25_offset_results.txt'
    lines=[]

    # Coarse sweep
    for off in range(0,5001,100):
        key=(la*(((n+len(la)-1)//len(la))+1))[off:off+n]
        for mode in ('beaufort','sub'):
            plain=decrypt_with_key(cipher,key,mode)
            txt=indices_to_runeglish(plain)
            score=trigram_score(txt)
            ioc=compute_ioc(plain)
            lines.append((score,ioc,off,mode,txt[:200]))

    lines.sort(reverse=True)
    # take best coarse and refine around top offsets
    top_coarse = lines[:6]
    refine_offsets=set()
    for _,_,off,_,_ in top_coarse:
        for o in range(max(0,off-200), off+201): refine_offsets.add(o)

    for off in sorted(refine_offsets):
        key=(la*(((n+len(la)-1)//len(la))+1))[off:off+n]
        for mode in ('beaufort','sub'):
            plain=decrypt_with_key(cipher,key,mode)
            txt=indices_to_runeglish(plain)
            score=trigram_score(txt)
            ioc=compute_ioc(plain)
            lines.append((score,ioc,off,mode,txt[:200]))

    lines.sort(reverse=True)
    with open(out,'w',encoding='utf-8') as f:
        for sc,ioc,off,mode,txt in lines[:100]:
            f.write(f'offset={off} mode={mode} tri={sc} IoC={ioc:.4f}\n')
            f.write(txt+"\n\n")
    print('Wrote', out)

if __name__=='__main__':
    main()
