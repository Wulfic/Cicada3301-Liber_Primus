"""
Multi-page F-skip Vigenère solver.
Tests F-skip (literal F = skip key) with known Cicada keywords on multiple unsolved pages.
Also tests Caesar+F-skip combinations for pages 31-54.
"""
import os, sys
from itertools import product

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

DIGRAPHS_ORDERED = [('TH',2),('NG',21),('EA',28),('OE',22),('EO',12),('AE',25),('IA',27)]
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
    while i < len(text):
        found = False
        for dg, val in DIGRAPHS_ORDERED:
            if text[i:i+len(dg)] == dg:
                result.append(val)
                i += len(dg)
                found = True
                break
        if not found:
            if text[i] in ENG2GP:
                result.append(ENG2GP[text[i]])
            i += 1
    return result

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

def score_text(text):
    s = 0
    for w in ['WISDOM','THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS',
              'WHICH','ARE','WITHIN','HOLY','LIVES','EACH','BEING','UNTO',
              'YOURSELF','INTELLIGENCE','INSTRUCTION','COMMAND','YOUR','OWN',
              'SELF','LAW','SACRED','DIVINITY','PILGRIM','TRUTH','BELIEVE',
              'NOTHING','FIND','SEEK','WEB','DEEP','HASHES','EXISTS','END',
              'PAGE','DUTY','EVERY','PRESERVE','WEAK','CONSUME','ENOUGH',
              'FOLLOW','DOGMA','BELONG','CIRCUMFERENCE','LOSS','KOAN','MASTER',
              'WHAT','HAVE','KNOW','TRUE','FROM','THEY','WILL','THEIR','HAS',
              'WELCOME','STUDY','HERE','ASKED','STUDENT','NAME','CALLED',
              'DOOR','WENT','DECIDED','MAN','CAME','SAID','TOLD','GIVE',
              'VOICE','LESSON','DURING','JUST','WARNING','EXCEPT','BOOK',
              'PRACTICE','THREE','BEHAVIORS','CAUSE','CONSUMPTION','WE',
              'BECAUSE','TOO','MUCH','MOST','THINGS','WORTH','PRESERVING',
              'STRONG','LATER','OBTAIN','NEED','LUCK','NOW','PRIMES',
              'TOTIENT','ENCRYPTED','SHOULD','PARABLE','LIKE','INSTAR',
              'TUNNELING','SURFACE','MUST','SHED','EMERGE','OUR','SOME',
              'TEST','YOUR','QUESTION','DO','FOUR','UNREASONABLE','DAY',
              'WAS','WHOSE','TEACHER','HIS','HER','WHO','HOW','WHEN']:
        c = text.count(w)
        s += c * len(w)
    return s

# Known Cicada keywords
KEYWORDS = {
    'DIVINITY': eng_to_gp('DIVINITY'),
    'FIRFUMFERENFE': eng_to_gp('FIRFUMFERENFE'),
    'CIRCUMFERENCE': eng_to_gp('CIRCUMFERENCE'),
    'SACRED': eng_to_gp('SACRED'),
    'PILGRIM': eng_to_gp('PILGRIM'),
    'PRIMUS': eng_to_gp('PRIMUS'),
    'WISDOM': eng_to_gp('WISDOM'),
    'TRUTH': eng_to_gp('TRUTH'),
    'INSTAR': eng_to_gp('INSTAR'),
    'INTUS': eng_to_gp('INTUS'),
    'LIBER': eng_to_gp('LIBER'),
    'CABAL': eng_to_gp('CABAL'),
    'MOBIUS': eng_to_gp('MOBIUS'),
    'SHADOW': eng_to_gp('SHADOW'),
    'VOID': eng_to_gp('VOID'),
    'AETHEREAL': eng_to_gp('AETHEREAL'),
    'CARNAL': eng_to_gp('CARNAL'),
    'ANALOG': eng_to_gp('ANALOG'),
    'MOURNFUL': eng_to_gp('MOURNFUL'),
    'OBSCURA': eng_to_gp('OBSCURA'),
    'EMERGENCE': eng_to_gp('EMERGENCE'),
    'CONSUMPTION': eng_to_gp('CONSUMPTION'),
    'ADHERENCE': eng_to_gp('ADHERENCE'),
    'DECEPTION': eng_to_gp('DECEPTION'),
    'PRESERVATION': eng_to_gp('PRESERVATION'),
    'KOAN': eng_to_gp('KOAN'),
    'CICADA': eng_to_gp('CICADA'),
    'YAHEOOPYJ': [26,24,8,18,3,3,13,26,11],  # known P17 key
    'DEOR': eng_to_gp('DEOR'),
}

# Pages to test
PAGES = [22, 25, 27, 32, 40, 44, 49, 50, 54, 58, 60, 61]

def load_page(page_num):
    path = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return [GP[c] for c in raw if c in GP]

results_all = {}

for page_num in PAGES:
    cipher = load_page(page_num)
    if cipher is None or len(cipher) < 10:
        continue
    
    N = len(cipher)
    f_pos = [i for i in range(N) if cipher[i] == 0]
    n_f = len(f_pos)
    non_f = N - n_f
    
    print(f"\n{'='*80}")
    print(f"PAGE {page_num}: {N} runes, {n_f} F runes, non-F = {non_f}")
    
    # Check which keywords have non_f divisible by their length
    for kname, key in KEYWORDS.items():
        kl = len(key)
        if non_f % kl == 0:
            print(f"  Keywords with {non_f}%{kl}==0: {kname}")
    
    page_best = []
    
    # Test ALL F's literal (simple F-skip)
    for kname, key in KEYWORDS.items():
        kl = len(key)
        for mode in ['SUB', 'ADD', 'BEAU']:
            for off in range(kl):
                dec = []
                k = off
                for i in range(N):
                    if cipher[i] == 0:
                        dec.append(0)  # Literal F
                    else:
                        kv = key[k % kl]
                        if mode == 'SUB': dec.append((cipher[i] - kv) % MOD)
                        elif mode == 'ADD': dec.append((cipher[i] + kv) % MOD)
                        else: dec.append((kv - cipher[i]) % MOD)
                        k += 1
                text = gp_to_lat(dec)
                sc = score_text(text)
                if sc >= 30:
                    page_best.append((sc, kname, mode, off, 'all-F-lit', text))
    
    # Also test NO F-skip (standard Vigenère) for comparison
    for kname, key in KEYWORDS.items():
        kl = len(key)
        for mode in ['SUB', 'ADD', 'BEAU']:
            for off in range(kl):
                dec = [(cipher[i] - key[(i+off)%kl]) % MOD if mode == 'SUB'
                       else (cipher[i] + key[(i+off)%kl]) % MOD if mode == 'ADD'
                       else (key[(i+off)%kl] - cipher[i]) % MOD
                       for i in range(N)]
                text = gp_to_lat(dec)
                sc = score_text(text)
                if sc >= 30:
                    page_best.append((sc, kname, mode, off, 'no-skip', text))
    
    # For pages with few F runes, try exhaustive F-skip
    if n_f <= 12 and n_f > 0:
        for kname, key in KEYWORDS.items():
            kl = len(key)
            # Only test top 3 offsets from all-F-literal
            for mode in ['SUB']:  # Focus on SUB
                for off in range(kl):
                    for f_mask in range(2**n_f):
                        lit_set = set()
                        for bit in range(n_f):
                            if f_mask & (1 << bit):
                                lit_set.add(f_pos[bit])
                        
                        dec = []
                        k = off
                        for i in range(N):
                            if i in lit_set:
                                dec.append(0)
                            else:
                                kv = key[k % kl]
                                dec.append((cipher[i] - kv) % MOD)
                                k += 1
                        text = gp_to_lat(dec)
                        sc = score_text(text)
                        if sc >= 50:
                            mask_str = ''.join('1' if f_pos[b] in lit_set else '0' for b in range(n_f))
                            page_best.append((sc, kname, 'SUB', off, f'mask={mask_str}', text))
    
    page_best.sort(reverse=True)
    if page_best:
        print(f"  Top 5 results:")
        for sc, kname, mode, off, ftype, text in page_best[:5]:
            print(f"    score={sc:4d} {kname:15s} {mode:5s} off={off} {ftype}: {text[:100]}")
        results_all[page_num] = page_best[:5]
    else:
        print(f"  No results scored >= 30")

# Summary
print("\n" + "="*80)
print("SUMMARY OF ALL PAGES")
print("="*80)
for pn, results in sorted(results_all.items()):
    best = results[0]
    print(f"  P{pn:02d}: best={best[0]:4d} {best[1]:15s} {best[2]:5s} off={best[3]} {best[4]}: {best[5][:80]}")

print("\n=== DONE ===")
