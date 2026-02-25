#!/usr/bin/env python3
"""
CRITICAL VERIFICATION: Do pages 21-30 achieve high IoC with P63 keywords?
This resolves the key discrepancy between different sessions.
Also checks the correct GP mapping with J-fix.
"""

import os
from collections import Counter

# GP mapping with J fix (U+16C4)
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛞᛟᛡᛠᚪᚫᚣ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','D','OE','A','EA','IA','AE','Y']
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return runes_to_indices(text)

def ioc29(indices):
    """Index of coincidence * 29. English GP text should be ~1.7+"""
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

def keyword_to_idx(word):
    indices = []
    i = 0
    w = word.upper()
    while i < len(w):
        if i+2 <= len(w):
            d = w[i:i+2]
            if d == 'TH': indices.append(2); i += 2; continue
            elif d == 'EO': indices.append(12); i += 2; continue
            elif d == 'NG': indices.append(21); i += 2; continue
            elif d == 'OE': indices.append(23); i += 2; continue
            elif d == 'EA': indices.append(25); i += 2; continue
            elif d == 'IA': indices.append(26); i += 2; continue
            elif d == 'AE': indices.append(27); i += 2; continue
        ch = w[i]
        m = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,
             'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'D':22,'A':24,'Y':28}
        if ch in m:
            indices.append(m[ch])
        i += 1
    return indices

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

# ===== THE CLAIMED KEYWORD MAPPINGS FROM MASTER_STATUS.MD =====
CLAIMED_KEYS = {
    21: ('CABAL', 'beaufort'),
    22: ('DIVINITY', 'beaufort'),
    23: ('ENCRYPTION', 'add'),
    24: ('OBSCURA', 'beaufort'),
    25: ('CABAL', 'beaufort'),
    26: ('ENCRYPT', 'add'),
    27: ('SHADOWS', 'add'),
    28: ('DEOR', 'sub'),
    29: ('TOTIENT', 'beaufort'),
    30: ('MOURNFUL', 'add'),
}

CLAIMED_IOC = {
    21: 1.9728, 22: 1.8671, 23: 2.0044, 24: 2.0622, 25: 1.8920,
    26: 1.9844, 27: 2.1043, 28: 2.0678, 29: 2.1184, 30: 1.9756,
}

print("=" * 80)
print("CRITICAL VERIFICATION: Pages 21-30 IoC with P63 Keywords")
print("=" * 80)

# First, verify our GP mapping by checking a KNOWN solution
print("\n--- CONTROL TEST: P03 with DIVINITY/Beaufort (known solution) ---")
p03 = load_page(3)
if p03:
    key = keyword_to_idx('DIVINITY')
    print(f"  P03: {len(p03)} runes, raw IoC*29 = {ioc29(p03):.4f}")
    print(f"  DIVINITY key = {key}")
    
    # Beaufort: p = (key - cipher) mod 29
    ext_key = key * (len(p03) // len(key) + 1)
    dec_beau = [(ext_key[i] - p03[i]) % 29 for i in range(len(p03))]
    print(f"  Beaufort IoC*29 = {ioc29(dec_beau):.4f}")
    print(f"  Text: {indices_to_latin(dec_beau)[:80]}")
    
    # SUB: p = (cipher - key) mod 29
    dec_sub = [(p03[i] - ext_key[i]) % 29 for i in range(len(p03))]
    print(f"  SUB IoC*29 = {ioc29(dec_sub):.4f}")
    print(f"  Text: {indices_to_latin(dec_sub)[:80]}")
    
    # ADD: p = (cipher + key) mod 29
    dec_add = [(p03[i] + ext_key[i]) % 29 for i in range(len(p03))]
    print(f"  ADD IoC*29 = {ioc29(dec_add):.4f}")
    print(f"  Text: {indices_to_latin(dec_add)[:80]}")

# Now test ALL claimed keywords on pages 21-30
print("\n" + "=" * 80)
print("MAIN TEST: Pages 21-30")
print("=" * 80)

for pn in range(21, 31):
    cipher = load_page(pn)
    if not cipher:
        print(f"\nP{pn}: NO DATA")
        continue
    
    claim_kw, claim_mode = CLAIMED_KEYS[pn]
    claim_ioc = CLAIMED_IOC[pn]
    key = keyword_to_idx(claim_kw)
    ext_key = key * (len(cipher) // len(key) + 1)
    
    print(f"\nP{pn}: {len(cipher)} runes, raw IoC*29 = {ioc29(cipher):.4f}")
    print(f"  Claimed: {claim_kw}/{claim_mode} -> IoC = {claim_ioc}")
    print(f"  Key indices: {key}")
    
    # Test all three modes
    for mode in ['sub', 'add', 'beaufort']:
        if mode == 'sub':
            dec = [(cipher[i] - ext_key[i]) % 29 for i in range(len(cipher))]
        elif mode == 'add':
            dec = [(cipher[i] + ext_key[i]) % 29 for i in range(len(cipher))]
        else:  # beaufort
            dec = [(ext_key[i] - cipher[i]) % 29 for i in range(len(cipher))]
        
        ic = ioc29(dec)
        marker = " <--- MATCH" if mode == claim_mode else ""
        marker += " ***HIGH***" if ic > 1.5 else ""
        print(f"  {mode:10s}: IoC*29 = {ic:.4f}{marker}")
        if ic > 1.3 or mode == claim_mode:
            text = indices_to_latin(dec)
            print(f"    Text: {text[:80]}")

# EXHAUSTIVE SEARCH: Try ALL keywords on ALL pages to find ANY high IoC
print("\n" + "=" * 80)
print("EXHAUSTIVE KEYWORD SEARCH (all keywords x all modes x pages 18-54)")
print("=" * 80)

ALL_KEYWORDS = {
    'DIVINITY': keyword_to_idx('DIVINITY'),
    'CABAL': keyword_to_idx('CABAL'),
    'SHADOWS': keyword_to_idx('SHADOWS'),
    'AETHEREAL': keyword_to_idx('AETHEREAL'),
    'OBSCURA': keyword_to_idx('OBSCURA'),
    'MOBIUS': keyword_to_idx('MOBIUS'),
    'MOURNFUL': keyword_to_idx('MOURNFUL'),
    'VOID': keyword_to_idx('VOID'),
    'CARNAL': keyword_to_idx('CARNAL'),
    'ANALOG': keyword_to_idx('ANALOG'),
    'FORM': keyword_to_idx('FORM'),
    'TOTIENT': keyword_to_idx('TOTIENT'),
    'PRIMES': keyword_to_idx('PRIMES'),
    'WISDOM': keyword_to_idx('WISDOM'),
    'ENCRYPT': keyword_to_idx('ENCRYPT'),
    'ENCRYPTION': keyword_to_idx('ENCRYPTION'),
    'FIRFUMFERENFE': keyword_to_idx('FIRFUMFERENFE'),
    'CICADA': keyword_to_idx('CICADA'),
    'CONSUMPTION': keyword_to_idx('CONSUMPTION'),
    'INSTAR': keyword_to_idx('INSTAR'),
    'CIRCUMFERENCE': keyword_to_idx('CIRCUMFERENCE'),
    'PILGRIM': keyword_to_idx('PILGRIM'),
    'SACRED': keyword_to_idx('SACRED'),
    'DEOR': keyword_to_idx('DEOR'),
    'BUFFERS': keyword_to_idx('BUFFERS'),
    'SUOID': keyword_to_idx('SUOID'),
    'WARNING': keyword_to_idx('WARNING'),
    'WELCOME': keyword_to_idx('WELCOME'),
    'BELIEVE': keyword_to_idx('BELIEVE'),
    'QUESTION': keyword_to_idx('QUESTION'),
    'INSTRUCTION': keyword_to_idx('INSTRUCTION'),
    'LIBER': keyword_to_idx('LIBER'),
    'PRIMUS': keyword_to_idx('PRIMUS'),
    'INTUS': keyword_to_idx('INTUS'),
    'KOAN': keyword_to_idx('KOAN'),
    'PARABLE': keyword_to_idx('PARABLE'),
    'YAHEOOPYJ': keyword_to_idx('YAHEOOPYJ'),
}

hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    
    for kw_name, key in ALL_KEYWORDS.items():
        if not key:
            continue
        ext_key = key * (len(cipher) // len(key) + 1)
        
        for mode in ['sub', 'add', 'beaufort']:
            if mode == 'sub':
                dec = [(cipher[i] - ext_key[i]) % 29 for i in range(len(cipher))]
            elif mode == 'add':
                dec = [(cipher[i] + ext_key[i]) % 29 for i in range(len(cipher))]
            else:
                dec = [(ext_key[i] - cipher[i]) % 29 for i in range(len(cipher))]
            
            ic = ioc29(dec)
            if ic > 1.3:
                text = indices_to_latin(dec)[:60]
                hits.append((ic, pn, kw_name, mode, text))

hits.sort(reverse=True)
if hits:
    print(f"\nFound {len(hits)} results with IoC > 1.3:")
    for ic, pn, kw, mode, text in hits[:30]:
        print(f"  P{pn:02d} {kw:15s}/{mode:8s}: IoC*29 = {ic:.4f}  {text}")
else:
    print("\n  *** NO RESULTS WITH IoC > 1.3 FOUND ***")

# ALSO: Check if the old analysis was using a DIFFERENT GP mapping (without J fix)
print("\n" + "=" * 80)
print("DIAGNOSTIC: Check if old analysis used different rune mapping")
print("=" * 80)

# Count J runes (U+16C4) in each page
for pn in range(21, 31):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    j_count = text.count('\u16c4')  # J rune
    total = len(runes_to_indices(text))
    print(f"  P{pn}: {total} runes total, {j_count} J runes ({100*j_count/total:.1f}%)")

# Final: what IoC would we get with the OLD (broken) mapping that drops J?
print("\n--- TEST: IoC with old mapping that DROPS J runes ---")
GP_RUNES_OLD = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛞᛟᛡᛠᚪᚫᚣ")  # Missing U+16C4
GP_RUNE_TO_IDX_OLD = {r: i for i, r in enumerate(GP_RUNES_OLD)}

for pn in [21, 27]:
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # New mapping (with J)
    new_indices = [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]
    # Old mapping (without J) 
    old_indices = [GP_RUNE_TO_IDX_OLD[ch] for ch in text if ch in GP_RUNE_TO_IDX_OLD]
    
    print(f"\n  P{pn}: new={len(new_indices)} runes, old={len(old_indices)} runes (diff={len(new_indices)-len(old_indices)})")
    
    claim_kw, claim_mode = CLAIMED_KEYS[pn]
    key = keyword_to_idx(claim_kw)
    
    # Test with NEW mapping
    ext_key = key * (len(new_indices) // len(key) + 1)
    dec_new_beau = [(ext_key[i] - new_indices[i]) % 29 for i in range(len(new_indices))]
    dec_new_add = [(new_indices[i] + ext_key[i]) % 29 for i in range(len(new_indices))]
    dec_new_sub = [(new_indices[i] - ext_key[i]) % 29 for i in range(len(new_indices))]
    
    # Test with OLD mapping
    ext_key_old = key * (len(old_indices) // len(key) + 1)
    dec_old_beau = [(ext_key_old[i] - old_indices[i]) % 29 for i in range(len(old_indices))]
    dec_old_add = [(old_indices[i] + ext_key_old[i]) % 29 for i in range(len(old_indices))]
    dec_old_sub = [(old_indices[i] - ext_key_old[i]) % 29 for i in range(len(old_indices))]
    
    # NOTE: OLD mapping has WRONG indices for runes after J position!
    # In the old mapping, ᛇ(EO)=11, ᛈ(P)=12, etc. instead of ᛇ(EO)=12, ᛈ(P)=13
    # This means old mapping != just dropping J; it SHIFTS all indices ≥ 12
    
    print(f"  {claim_kw}/{claim_mode} with NEW mapping:")
    print(f"    Beaufort IoC = {ioc29(dec_new_beau):.4f}")
    print(f"    ADD IoC = {ioc29(dec_new_add):.4f}")
    print(f"    SUB IoC = {ioc29(dec_new_sub):.4f}")
    
    print(f"  {claim_kw}/{claim_mode} with OLD mapping (drops J, shifts indices):")
    print(f"    Beaufort IoC = {ioc29(dec_old_beau):.4f}")
    print(f"    ADD IoC = {ioc29(dec_old_add):.4f}")
    print(f"    SUB IoC = {ioc29(dec_old_sub):.4f}")

print("\n=== VERIFICATION COMPLETE ===")
