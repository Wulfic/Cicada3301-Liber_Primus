"""Test Pages 21-30 with F-SKIP Vigenère using P63 keywords.
F-skip: when plaintext = F (value 0), key index doesn't advance.
This is confirmed from solved pages P03-04, P14-15, P55/73."""

import os
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                runes = [GP[c] for c in raw if c in GP]
                words = []
                current = []
                for c in raw:
                    if c in GP:
                        current.append(GP[c])
                    elif current:
                        words.append(current)
                        current = []
                if current:
                    words.append(current)
                return runes, words
    return None, None

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c * (c-1) for c in counts.values()) / (n * (n-1))

def fskip_decrypt(cipher, key, mode):
    """Decrypt with F-skip rule. Returns plaintext list."""
    kl = len(key)
    plain = []
    key_idx = 0
    for c in cipher:
        if mode == 'SUB':
            p = (c - key[key_idx % kl]) % 29
        elif mode == 'ADD':
            p = (c + key[key_idx % kl]) % 29
        else:  # BEAUFORT
            p = (key[key_idx % kl] - c) % 29
        plain.append(p)
        if p != 0:  # F = 0, don't advance key
            key_idx += 1
    return plain

def standard_decrypt(cipher, key, mode):
    """Standard Vigenère without F-skip."""
    kl = len(key)
    plain = []
    for i, c in enumerate(cipher):
        if mode == 'SUB':
            p = (c - key[i % kl]) % 29
        elif mode == 'ADD':
            p = (c + key[i % kl]) % 29
        else:
            p = (key[i % kl] - c) % 29
        plain.append(p)
    return plain

def single_rune_word_check(plain, words):
    """Check if single-rune words are A(24) or I(10)."""
    pos = 0
    total_single = 0
    correct_single = 0
    for word in words:
        if len(word) == 1:
            total_single += 1
            if plain[pos] in [24, 10]:
                correct_single += 1
        pos += len(word)
    return correct_single, total_single

# P63 keywords — try multiple GP encodings
KEYWORDS = {
    "CABAL": {
        "direct": [5,24,17,24,20],
        "no_digraph": [5,24,17,24,20],  # same
    },
    "DIVINITY": {
        "direct": [23,10,1,10,9,10,16,26],
        "no_digraph": [23,10,1,10,9,10,16,26],
    },
    "ENCRYPTION": {
        "with_digraph": [18,9,5,4,26,13,16,10,3,9],  # E,N,C,R,Y,P,T,I,O,N
        "no_digraph": [18,9,5,4,26,13,16,10,3,9],
    },
    "OBSCURA": {
        "direct": [3,17,15,5,1,4,24],
    },
    "ENCRYPT": {
        "direct": [18,9,5,4,26,13,16],
    },
    "SHADOWS": {
        "direct": [15,8,24,23,3,7,15],
    },
    "DEOR": {
        "direct": [23,12,4],  # D,EO,R with digraph
        "no_digraph": [23,18,3,4],  # D,E,O,R without digraph
    },
    "TOTIENT": {
        "direct": [16,3,16,10,18,9,16],
    },
    "MOURNFUL": {
        "direct": [19,3,1,4,9,0,1,20],
    },
}

# Page to keyword mapping from community
PAGE_KEYS = {
    21: ["CABAL"],
    22: ["DIVINITY"],  
    23: ["ENCRYPTION"],
    24: ["OBSCURA"],
    25: ["CABAL"],
    26: ["ENCRYPT"],
    27: ["SHADOWS"],
    28: ["DEOR"],
    29: ["TOTIENT"],
    30: ["MOURNFUL"],
}

print("="*100)
print("F-SKIP VIGENÈRE TEST: P63 keywords on pages 21-30")
print("  Testing: F-skip and standard, all modes, all key variants")
print("="*100)

all_results = []

for pg in range(21, 31):
    runes, words = load_page(pg)
    if not runes:
        continue
    
    n = len(runes)
    _, n_single = single_rune_word_check(runes, words)
    
    for kw_name in PAGE_KEYS.get(pg, []) + list(KEYWORDS.keys()):
        if kw_name not in KEYWORDS:
            continue
        for key_variant, key_gp in KEYWORDS[kw_name].items():
            for mode in ['SUB', 'ADD', 'BEAUFORT']:
                for use_fskip in [True, False]:
                    if use_fskip:
                        dec = fskip_decrypt(runes, key_gp, mode)
                    else:
                        dec = standard_decrypt(runes, key_gp, mode)
                    
                    ic = ioc(dec) * 29
                    correct, total = single_rune_word_check(dec, words)
                    
                    fskip_label = "F-skip" if use_fskip else "Std"
                    
                    all_results.append({
                        'pg': pg,
                        'kw': kw_name,
                        'variant': key_variant,
                        'mode': mode,
                        'fskip': fskip_label,
                        'ioc': ic,
                        'single_correct': correct,
                        'single_total': total,
                        'dec': dec,
                        'words': words,
                    })

# Sort by IoC (highest first)
all_results.sort(key=lambda x: (-x['ioc'], -x['single_correct']))

# Show top results per page
print("\nTOP 5 RESULTS PER PAGE (by IoC*29):")
for pg in range(21, 31):
    page_results = [r for r in all_results if r['pg'] == pg]
    print(f"\n  === Page {pg} (singles: {page_results[0]['single_total']}) ===")
    for r in page_results[:5]:
        # First 10 words
        pos = 0
        wds = []
        for word in r['words'][:10]:
            wn = len(word)
            word_dec = r['dec'][pos:pos+wn]
            wds.append(''.join(LATIN[v] for v in word_dec))
            pos += wn
        
        print(f"    {r['kw']:12s} {r['variant']:12s} {r['mode']:8s} {r['fskip']:6s} IoC*29={r['ioc']:.3f} singles={r['single_correct']}/{r['single_total']}")
        print(f"      Text: {' '.join(wds)}")

# Global winners by single-rune word accuracy
print("\n" + "="*100)
print("GLOBAL TOP 20 BY SINGLE-RUNE WORD ACCURACY")
print("="*100)

all_results.sort(key=lambda x: (-x['single_correct']/max(x['single_total'],1), -x['ioc']))
for r in all_results[:20]:
    pos = 0
    wds = []
    for word in r['words'][:8]:
        wn = len(word)
        word_dec = r['dec'][pos:pos+wn]
        wds.append(''.join(LATIN[v] for v in word_dec))
        pos += wn
    
    pct = r['single_correct']/max(r['single_total'],1)*100
    print(f"  P{r['pg']:02d} {r['kw']:12s} {r['mode']:8s} {r['fskip']:6s} singles={r['single_correct']}/{r['single_total']} ({pct:.0f}%) IoC={r['ioc']:.3f}")
    print(f"    Text: {' '.join(wds)}")

# === EXHAUSTIVE SINGLE-VALUE KEY SEARCH ===
print("\n" + "="*100)
print("EXHAUSTIVE: Try ALL single-byte keys (0-28) with F-skip on each page")
print("="*100)

for pg in range(21, 31):
    runes, words = load_page(pg)
    if not runes:
        continue
    
    best = None
    for k in range(29):
        for mode in ['SUB', 'ADD', 'BEAUFORT']:
            for use_fskip in [True, False]:
                key = [k]
                if use_fskip:
                    dec = fskip_decrypt(runes, key, mode)
                else:
                    dec = standard_decrypt(runes, key, mode)
                
                ic = ioc(dec) * 29
                correct, total = single_rune_word_check(dec, words)
                
                if best is None or ic > best[0]:
                    best = (ic, k, mode, use_fskip, correct, total, dec)
    
    ic, k, mode, fs, cor, tot, dec = best
    fs_label = "F-skip" if fs else "Std"
    pos = 0
    wds = []
    for word in words[:10]:
        wn = len(word)
        word_dec = dec[pos:pos+wn]
        wds.append(''.join(LATIN[v] for v in word_dec))
        pos += wn
    print(f"  P{pg:02d}: best single key={k}({LATIN[k]}) {mode} {fs_label} IoC*29={ic:.3f} singles={cor}/{tot}")
    print(f"    Text: {' '.join(wds)}")
