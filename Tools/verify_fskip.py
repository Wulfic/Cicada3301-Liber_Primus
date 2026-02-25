"""
Test F-skip Vigenere on Pages 21-30 AND validation pages.
F-skip: when decrypted value = 0 (F), don't advance key counter.
"""
import os, sys
from collections import Counter

# ===== GP MAP (J-FIXED) =====
GP_MAP = {
    '\u16A0': 0, '\u16A2': 1, '\u16A6': 2, '\u16A9': 3, '\u16B1': 4,
    '\u16B3': 5, '\u16B7': 6, '\u16B9': 7, '\u16BA': 8, '\u16BE': 9,
    '\u16C1': 10, '\u16C4': 11, '\u16C7': 12, '\u16C8': 13, '\u16CB': 14,
    '\u16CF': 15, '\u16D2': 16, '\u16D6': 17, '\u16D7': 18, '\u16DA': 19,
    '\u16DE': 20, '\u16DF': 21, '\u16E0': 22, '\u16E1': 23, '\u16E3': 24,
    '\u16E6': 25, '\u16E8': 26, '\u16EA': 27, '\u16EB': 28,
}
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_page(pn):
    p = os.path.join(r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages", f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(p): return []
    with open(p,'r',encoding='utf-8') as f: text = f.read()
    return [GP_MAP[c] for c in text if c in GP_MAP]

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
    """Decrypt with F-skip: when plaintext = skip_val, don't advance key"""
    result = []; key_idx = 0; kl = len(key)
    for c in cipher:
        k = key[key_idx % kl]
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        if p != skip_val: key_idx += 1
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
print("VALIDATION: Known solutions with F-skip")
print("=" * 80)

divinity = keyword_to_gp('DIVINITY')
print(f"DIVINITY key: {divinity}")

for pn, desc in [(3, "Welcome"), (61, "Pilgrim")]:
    cipher = load_page(pn)
    if not cipher: continue
    print(f"\nPage {pn}: {desc} ({len(cipher)} runes)")
    for mode in ['SUB','ADD','BEAU']:
        for off in range(len(divinity)):
            shifted = divinity[off:] + divinity[:off]
            d2 = fskip_decrypt(cipher, shifted, mode, skip_val=0)
            ic2 = ioc29(d2)
            if ic2 > 1.4:
                t2 = vals_to_text(d2)[:80]
                print(f"  {mode} off={off} Fskip: IoC={ic2:.4f} -> {t2}")

# ===== PAGES 21-30 WITH F-SKIP =====
print("\n" + "=" * 80)
print("PAGES 21-30: F-skip test with ALL keywords x ALL offsets")
print("=" * 80)

KEYWORDS = ['CABAL','DIVINITY','SHADOWS','AETHEREAL','OBSCURA','MOURNFUL',
            'VOID','CARNAL','MOBIUS','ANALOG','BUFFERS','FORM','DEOR',
            'TOTIENT','ENCRYPT','FIRFUMFERENFE','YAHEOOPYJ','CONSUMPTION',
            'PRESERVATION','ADHERENCE','CIRCUMFERENCE','PRIMALITY',
            'PILGRIMAGE','INSTAR','WELCOME','WISDOM','INSTRUCTION']

for pn in range(21, 31):
    cipher = load_page(pn)
    if not cipher: continue
    raw_ioc = ioc29(cipher)
    print(f"\n--- Page {pn}: {len(cipher)} runes, raw IoC={raw_ioc:.4f} ---")
    
    hits = []
    for kw in KEYWORDS:
        key = keyword_to_gp(kw)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            for off in range(len(key)):
                shifted = key[off:] + key[:off]
                # F-skip
                d = fskip_decrypt(cipher, shifted, mode, 0)
                ic = ioc29(d)
                if ic > 1.3:
                    hits.append((ic, kw, mode, off, 'Fskip', d))
                # No skip
                d2 = standard_decrypt(cipher, shifted, mode)
                ic2 = ioc29(d2)
                if ic2 > 1.3:
                    hits.append((ic2, kw, mode, off, 'noSkip', d2))
    
    hits.sort(reverse=True)
    for ic, kw, mode, off, sk, d in hits[:5]:
        t = vals_to_text(d)
        marker = " ** SIGNAL **" if ic > 1.5 else ""
        print(f"  {kw} {mode} off={off} {sk}: IoC={ic:.4f}{marker}")
        print(f"    {t[:80]}")
    if not hits:
        print(f"  No results above IoC=1.3")

# ===== ALL PAGES 18-54: Quick scan with F-skip DIVINITY =====
print("\n" + "=" * 80)
print("QUICK SCAN: All pages 18-54 with DIVINITY F-skip (best offset)")
print("=" * 80)

for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20: continue
    
    best_ic = 0
    best_info = None
    for mode in ['SUB','ADD','BEAU']:
        for off in range(len(divinity)):
            shifted = divinity[off:] + divinity[:off]
            d = fskip_decrypt(cipher, shifted, mode, 0)
            ic = ioc29(d)
            if ic > best_ic:
                best_ic = ic
                best_info = (mode, off, d)
    
    marker = " ** SIGNAL **" if best_ic > 1.5 else ""
    if best_ic > 1.3 or pn in [18, 19, 20]:
        t = vals_to_text(best_info[2])[:60] if best_info else ""
        print(f"  Page {pn}: DIVINITY {best_info[0]} off={best_info[1]} IoC={best_ic:.4f}{marker} -> {t}")
