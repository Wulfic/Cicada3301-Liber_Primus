"""
DEFINITIVE test using the CORRECT GP mapping from advanced_cipher_attack.py.
Tests F-skip Vigenere on validation pages and Pages 21-30.
"""
import os, sys
from collections import Counter

# ===== CORRECT GP MAP (from advanced_cipher_attack.py, verified working) =====
RUNE_TO_INDEX = {
    '\u16A0': 0,   # ᚠ F
    '\u16A2': 1,   # ᚢ U/V
    '\u16A6': 2,   # ᚦ TH
    '\u16A9': 3,   # ᚩ O
    '\u16B1': 4,   # ᚱ R
    '\u16B3': 5,   # ᚳ C/K
    '\u16B7': 6,   # ᚷ G
    '\u16B9': 7,   # ᚹ W
    '\u16BB': 8,   # ᚻ H
    '\u16BE': 9,   # ᚾ N
    '\u16C1': 10,  # ᛁ I
    '\u16C2': 11,  # ᛂ J (variant 1)
    '\u16C4': 11,  # ᛄ J (variant 2)
    '\u16C7': 12,  # ᛇ EO
    '\u16C8': 13,  # ᛈ P
    '\u16C9': 14,  # ᛉ X
    '\u16CB': 15,  # ᛋ S/Z
    '\u16CF': 16,  # ᛏ T
    '\u16D2': 17,  # ᛒ B
    '\u16D6': 18,  # ᛖ E
    '\u16D7': 19,  # ᛗ M
    '\u16DA': 20,  # ᛚ L
    '\u16DD': 21,  # ᛝ NG
    '\u16DF': 22,  # ᛟ OE
    '\u16DE': 23,  # ᛞ D
    '\u16AA': 24,  # ᚪ A
    '\u16AB': 25,  # ᚫ AE/Y (Anglo-Saxon)
    '\u16A3': 26,  # ᚣ Y
    '\u16E1': 27,  # ᛡ IA/IO
    '\u16E0': 28,  # ᛠ EA
}

GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_page(pn):
    p = os.path.join(r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages", f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(p): return []
    with open(p, 'r', encoding='utf-8') as f: text = f.read()
    return [RUNE_TO_INDEX[c] for c in text if c in RUNE_TO_INDEX]

def keyword_to_gp(word):
    result = []; i = 0; word = word.upper()
    while i < len(word):
        if i+1 < len(word):
            di = word[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap:
                result.append(dmap[di]); i += 2; continue
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if word[i] in smap: result.append(smap[word[i]])
        i += 1
    return result

def ioc29(vals):
    if len(vals) < 2: return 0
    ct = Counter(vals); n = len(vals)
    return 29 * sum(c*(c-1) for c in ct.values()) / (n*(n-1))

def vals_to_text(vals):
    return ''.join(GP_LETTERS[v].lower() for v in vals)

def fskip_decrypt(cipher, key, mode='SUB', skip_val=0):
    """F-skip: cipher F runes are literal F, don't advance key"""
    result = []; key_idx = 0; kl = len(key)
    for c in cipher:
        if c == skip_val:
            # Literal F - output F, don't advance key
            result.append(0)
        else:
            k = key[key_idx % kl]
            if mode == 'SUB': p = (c - k) % 29
            elif mode == 'ADD': p = (c + k) % 29
            elif mode == 'BEAU': p = (k - c) % 29
            result.append(p)
            key_idx += 1
    return result

def fskip_decrypt_v2(cipher, key, mode='SUB'):
    """F-skip v2: decrypt normally, but if plaintext = F, don't advance key"""
    result = []; key_idx = 0; kl = len(key)
    for c in cipher:
        k = key[key_idx % kl]
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        if p != 0:  # if plaintext is NOT F, advance key
            key_idx += 1
    return result

def standard_decrypt(cipher, key, mode='SUB'):
    result = []; kl = len(key)
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'SUB': result.append((c - k) % 29)
        elif mode == 'ADD': result.append((c + k) % 29)
        elif mode == 'BEAU': result.append((k - c) % 29)
    return result

# ===== VALIDATION: P03 with DIVINITY =====
print("=" * 80)
print("VALIDATION: Page 03 with DIVINITY (CORRECT GP mapping)")
print("=" * 80)

divinity = keyword_to_gp('DIVINITY')
print(f"DIVINITY key: {divinity}")

for pn in [3, 4, 61, 62]:
    cipher = load_page(pn)
    if not cipher: continue
    print(f"\nPage {pn}: {len(cipher)} runes, raw IoC*29={ioc29(cipher):.4f}")
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        # Standard
        d0 = standard_decrypt(cipher, divinity, mode)
        ic0 = ioc29(d0)
        
        # F-skip v1 (cipher F = literal F)
        d1 = fskip_decrypt(cipher, divinity, mode, 0)
        ic1 = ioc29(d1)
        
        # F-skip v2 (plaintext F = don't advance)
        d2 = fskip_decrypt_v2(cipher, divinity, mode)
        ic2 = ioc29(d2)
        
        best = max(ic0, ic1, ic2)
        if best > 1.3:
            t0 = vals_to_text(d0)[:60]
            t1 = vals_to_text(d1)[:60]
            t2 = vals_to_text(d2)[:60]
            print(f"  {mode}: std={ic0:.3f} skip1={ic1:.3f} skip2={ic2:.3f}")
            if ic0 == best: print(f"    std:  {t0}")
            if ic1 == best: print(f"    skip1: {t1}")
            if ic2 == best: print(f"    skip2: {t2}")
    
    # Try offsets 0-7 with best mode
    best_result = (0, '', 0, '', [])
    for off in range(len(divinity)):
        shifted = divinity[off:] + divinity[:off]
        for mode in ['SUB','ADD','BEAU']:
            for name, func in [('std', lambda c,k,m: standard_decrypt(c,k,m)),
                                ('skip1', lambda c,k,m: fskip_decrypt(c,k,m,0)),
                                ('skip2', lambda c,k,m: fskip_decrypt_v2(c,k,m))]:
                d = func(cipher, shifted, mode)
                ic = ioc29(d)
                if ic > best_result[0]:
                    best_result = (ic, mode, off, name, d)
    
    ic, mode, off, name, d = best_result
    t = vals_to_text(d)[:80]
    marker = " ** ENGLISH! **" if ic > 1.5 else ""
    print(f"  BEST: {mode} off={off} {name}: IoC={ic:.4f}{marker}")
    print(f"    {t}")

# ===== P63 KEYWORDS ON PAGES 21-30 =====
print("\n" + "=" * 80)
print("PAGES 21-30: All keywords x modes x offsets x skip-types")
print("=" * 80)

KEYWORDS = ['CABAL','DIVINITY','SHADOWS','AETHEREAL','OBSCURA','MOURNFUL',
            'VOID','CARNAL','MOBIUS','ANALOG','BUFFERS','FORM','DEOR',
            'TOTIENT','ENCRYPT','FIRFUMFERENFE','YAHEOOPYJ','CIRCUMFERENCE',
            'CONSUMPTION','PRESERVATION','ADHERENCE','WISDOM','INSTRUCTION',
            'PILGRIMAGE','INSTAR','WELCOME','WARNING','SACRED','PRIMES']

PAGE_CLAIMED = {
    21: ('CABAL', 'BEAU'), 22: ('DIVINITY', 'BEAU'), 23: ('ENCRYPTION', 'ADD'),
    24: ('OBSCURA', 'BEAU'), 25: ('CABAL', 'BEAU'), 26: ('ENCRYPT', 'ADD'),
    27: ('SHADOWS', 'ADD'), 28: ('DEOR', 'SUB'), 29: ('TOTIENT', 'BEAU'),
    30: ('MOURNFUL', 'ADD'),
}

for pn in range(21, 31):
    cipher = load_page(pn)
    if not cipher: continue
    raw_ioc = ioc29(cipher)
    print(f"\n--- Page {pn}: {len(cipher)} runes, raw IoC={raw_ioc:.4f} ---")
    
    # Test claimed key first
    claimed_kw, claimed_mode = PAGE_CLAIMED[pn]
    claimed_key = keyword_to_gp(claimed_kw)
    d_claimed = standard_decrypt(cipher, claimed_key, claimed_mode)
    ic_claimed = ioc29(d_claimed)
    t_claimed = vals_to_text(d_claimed)[:60]
    print(f"  CLAIMED: {claimed_kw} {claimed_mode}: IoC={ic_claimed:.4f} -> {t_claimed}")
    
    # Exhaustive search
    hits = []
    for kw in KEYWORDS:
        key = keyword_to_gp(kw)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            for off in range(len(key)):
                shifted = key[off:] + key[:off]
                for name, func in [('std', lambda c,k,m: standard_decrypt(c,k,m)),
                                    ('skip1', lambda c,k,m: fskip_decrypt(c,k,m,0)),
                                    ('skip2', lambda c,k,m: fskip_decrypt_v2(c,k,m))]:
                    d = func(cipher, shifted, mode)
                    ic = ioc29(d)
                    if ic > 1.4:
                        hits.append((ic, kw, mode, off, name, d))
    
    hits.sort(reverse=True)
    for ic, kw, mode, off, name, d in hits[:5]:
        t = vals_to_text(d)[:80]
        marker = " ** ENGLISH! **" if ic > 1.6 else " *signal*" if ic > 1.5 else ""
        print(f"  {kw} {mode} off={off} {name}: IoC={ic:.4f}{marker}")
        print(f"    {t}")
    if not hits:
        print(f"  No keyword above IoC=1.4")

# ===== QUICK SCAN: All pages 18-54 with top keywords =====
print("\n" + "=" * 80)
print("QUICK SCAN: Pages 18-54, best keyword+mode (threshold IoC > 1.4)")
print("=" * 80)

for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20: continue
    
    best = (0, '', '', 0, '', [])
    for kw in KEYWORDS[:15]:  # Top keywords only for speed
        key = keyword_to_gp(kw)
        if not key: continue
        for mode in ['SUB','ADD','BEAU']:
            for off in range(min(len(key), 4)):  # First 4 offsets
                shifted = key[off:] + key[:off]
                d = fskip_decrypt(cipher, shifted, mode, 0)
                ic = ioc29(d)
                if ic > best[0]:
                    best = (ic, kw, mode, off, 'skip1', d)
                d2 = standard_decrypt(cipher, shifted, mode)
                ic2 = ioc29(d2)
                if ic2 > best[0]:
                    best = (ic2, kw, mode, off, 'std', d2)
    
    ic, kw, mode, off, name, d = best
    if ic > 1.4 or pn in [18, 19, 20, 32, 44, 50]:
        t = vals_to_text(d)[:60]
        marker = " ** ENGLISH! **" if ic > 1.6 else " *signal*" if ic > 1.5 else ""
        print(f"  P{pn:02d} ({len(cipher)}): {kw} {mode} off={off} {name}: IoC={ic:.4f}{marker} -> {t}")
