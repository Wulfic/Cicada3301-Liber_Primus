"""
CORRECT F-skip Vigenere: when decrypted plaintext = F (0), don't advance key.
Test on all pages with all keywords.
"""
import os, sys
from collections import Counter

RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def load_page(pn):
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rune_text = ''
    for line in lines:
        if line.strip() and line.strip()[0].isascii() and line.strip()[0].isalpha():
            continue
        rune_text += line
    return [RUNE_TO_INDEX[c] for c in rune_text if c in RUNE_TO_INDEX]

def keyword_to_gp(word):
    result = []; i = 0; word = word.upper()
    while i < len(word):
        if i+1 < len(word):
            di = word[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap: result.append(dmap[di]); i += 2; continue
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

def text(vals): return ''.join(GP[v] for v in vals)

def fskip_vig(cipher, key, mode='SUB'):
    """Correct F-skip: when plaintext = F(0), don't advance key index"""
    result = []; ki = 0; kl = len(key)
    for c in cipher:
        k = key[ki % kl]
        if mode == 'SUB': p = (c - k) % 29
        elif mode == 'ADD': p = (c + k) % 29
        elif mode == 'BEAU': p = (k - c) % 29
        result.append(p)
        if p != 0:  # Advance key only if plaintext is NOT F
            ki += 1
    return result

def vig(cipher, key, mode='SUB'):
    """Standard Vigenere (no F-skip)"""
    result = []; kl = len(key)
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'SUB': result.append((c - k) % 29)
        elif mode == 'ADD': result.append((c + k) % 29)
        elif mode == 'BEAU': result.append((k - c) % 29)
    return result

# ===== VALIDATE P03 with F-skip =====
print("=" * 80)
print("VALIDATION: P03 with DIVINITY + F-skip")
print("=" * 80)

divinity = keyword_to_gp('DIVINITY')

for pn in [3, 4, 61, 62]:
    cipher = load_page(pn)
    if not cipher: continue
    print(f"\nPage {pn}: {len(cipher)} runes")
    for mode in ['SUB', 'ADD', 'BEAU']:
        # F-skip
        dec = fskip_vig(cipher, divinity, mode)
        ic = ioc29(dec)
        t = text(dec)
        if ic > 1.3:
            print(f"  F-skip {mode}: IoC={ic:.4f}")
            print(f"    {t[:100]}")

# P03+P04 continuous with F-skip
p03 = load_page(3)
p04 = load_page(4)
if p03 and p04:
    combined = p03 + p04
    dec = fskip_vig(combined, divinity, 'SUB')
    ic = ioc29(dec)
    t = text(dec)
    print(f"\nP03+P04 F-skip SUB ({len(combined)} runes): IoC={ic:.4f}")
    print(f"  {t[:120]}")
    print(f"  ...{t[-80:]}")

# P14+P15 continuous with FIRFUMFERENFE
firfum = keyword_to_gp('FIRFUMFERENFE')
p14 = load_page(14)
p15 = load_page(15)
if p14 and p15:
    for pdata, pname in [(p14, 'P14'), (p15, 'P15'), (p14+p15, 'P14+P15')]:
        dec = fskip_vig(pdata, firfum, 'SUB')
        ic = ioc29(dec)
        t = text(dec)
        print(f"\n{pname} FIRFUMFERENFE F-skip SUB ({len(pdata)} runes): IoC={ic:.4f}")
        print(f"  {t[:120]}")

# ===== SYSTEMATIC SCAN: ALL PAGES WITH F-SKIP =====
print("\n" + "=" * 80)
print("COMPREHENSIVE F-SKIP SCAN: Pages 17-54")
print("=" * 80)

KEYWORDS = ['DIVINITY','FIRFUMFERENFE','CABAL','SHADOWS','AETHEREAL','OBSCURA',
            'MOURNFUL','VOID','CARNAL','MOBIUS','ANALOG','BUFFERS','FORM','DEOR',
            'TOTIENT','ENCRYPT','YAHEOOPYJ','CIRCUMFERENCE','CONSUMPTION',
            'PRESERVATION','ADHERENCE','WISDOM','INSTRUCTION','PILGRIMAGE',
            'INSTAR','WELCOME','WARNING','SACRED','PRIMES','KOAN','MASTER',
            'SUOID','PRIMALITY']

for pn in range(17, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 10: continue
    raw_ioc = ioc29(cipher)
    
    best = (0, '', '', [])
    
    for kw_name in KEYWORDS:
        key = keyword_to_gp(kw_name)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            # F-skip
            dec = fskip_vig(cipher, key, mode)
            ic = ioc29(dec)
            if ic > best[0]:
                best = (ic, f'{kw_name} {mode} Fskip', '', dec)
            # Standard
            dec2 = vig(cipher, key, mode)
            ic2 = ioc29(dec2)
            if ic2 > best[0]:
                best = (ic2, f'{kw_name} {mode} std', '', dec2)
    
    # Also try Caesar + reversed
    for shift in range(29):
        dec = [(c + shift) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best[0]:
            best = (ic, f'CAESAR_{shift}', '', dec)
        dec2 = [(28 - c + shift) % 29 for c in cipher]
        ic2 = ioc29(dec2)
        if ic2 > best[0]:
            best = (ic2, f'REV_{shift}', '', dec2)
    
    ic, method, _, dec = best
    if ic > 1.3 or pn in [17,18,19,20,21,22,32,44,50]:
        t = text(dec)[:80]
        marker = " *** ENGLISH ***" if ic > 1.6 else " ** signal **" if ic > 1.4 else ""
        print(f"  P{pn:02d} ({len(cipher):4d}): raw={raw_ioc:.3f} best={ic:.4f} [{method}]{marker}")
        print(f"    {t}")

# ===== PAGES 55-74 F-SKIP CHECK =====
print("\n" + "=" * 80)
print("PAGES 55-74: F-skip validation")
print("=" * 80)

for pn in range(55, 75):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 5: continue
    
    best = (0, '', [])
    
    # DIVINITY F-skip
    dec = fskip_vig(cipher, divinity, 'SUB')
    ic = ioc29(dec)
    if ic > best[0]: best = (ic, 'DIVINITY Fskip SUB', dec)
    
    # Direct/Caesar/Rev
    for s in range(29):
        dec = [(c + s) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best[0]: best = (ic, f'CAESAR_{s}', dec)
        dec2 = [(28 - c + s) % 29 for c in cipher]
        ic2 = ioc29(dec2)
        if ic2 > best[0]: best = (ic2, f'REV_{s}', dec2)
    
    ic, method, dec = best
    marker = " SOLVED" if ic > 1.5 else ""
    print(f"  P{pn:02d} ({len(cipher):3d}): best={ic:.4f} [{method}]{marker}")
    if ic > 1.5:
        print(f"    {text(dec)[:70]}")
