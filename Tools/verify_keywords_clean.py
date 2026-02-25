"""
Clean verification: Do Pages 21-30 actually respond to P63 keywords?
Tests full-text IoC*29 after Vigenere decryption with J-fixed GP mapping.
"""
import os, sys, math
from collections import Counter

# ===== GEMATRIA PRIMUS (J-FIXED) =====
GP_MAP = {
    '\u16A0': 0,   # F
    '\u16A2': 1,   # U/V
    '\u16A6': 2,   # TH
    '\u16A9': 3,   # O
    '\u16B1': 4,   # R
    '\u16B3': 5,   # C/K
    '\u16B7': 6,   # G
    '\u16B9': 7,   # W
    '\u16BA': 8,   # H
    '\u16BE': 9,   # N
    '\u16C1': 10,  # I
    '\u16C4': 11,  # J (U+16C4 - the CORRECT J rune!)
    '\u16C7': 12,  # EO
    '\u16C8': 13,  # P
    '\u16CB': 14,  # X
    '\u16CF': 15,  # S/Z
    '\u16D2': 16,  # T
    '\u16D6': 17,  # B
    '\u16D7': 18,  # E
    '\u16DA': 19,  # M
    '\u16DE': 20,  # L
    '\u16DF': 21,  # ING/NG
    '\u16E0': 22,  # OE
    '\u16E1': 23,  # D
    '\u16E3': 24,  # A
    '\u16E6': 25,  # AE
    '\u16E8': 26,  # Y
    '\u16EA': 27,  # IA/IO
    '\u16EB': 28,  # EA
}

# Reverse: index -> letter name
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_page_gp(page_num):
    """Load a page's runes as GP index values"""
    base = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"
    path = os.path.join(base, f"page_{page_num:02d}", "runes.txt")
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    values = []
    for ch in text:
        if ch in GP_MAP:
            values.append(GP_MAP[ch])
    return values

def ioc29(vals):
    """IoC * 29 for a sequence of integer values mod 29"""
    if len(vals) < 2:
        return 0
    ct = Counter(vals)
    n = len(vals)
    s = sum(c*(c-1) for c in ct.values())
    return 29 * s / (n * (n - 1))

def keyword_to_gp(word):
    """Convert a keyword string to GP indices using digraph rules"""
    result = []
    i = 0
    word = word.upper()
    while i < len(word):
        # Check digraphs first
        if i+1 < len(word):
            di = word[i:i+2]
            if di == 'TH':
                result.append(2); i += 2; continue
            elif di == 'EO':
                result.append(12); i += 2; continue
            elif di == 'NG':
                result.append(21); i += 2; continue
            elif di == 'OE':
                result.append(22); i += 2; continue
            elif di == 'AE':
                result.append(25); i += 2; continue
            elif di == 'IA' or di == 'IO':
                result.append(27); i += 2; continue
            elif di == 'EA':
                result.append(28); i += 2; continue
        # Single characters  
        ch = word[i]
        single_map = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,
                      'H':8,'N':9,'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,
                      'T':16,'B':17,'E':18,'M':19,'L':20,'D':23,'A':24,'Y':26}
        if ch in single_map:
            result.append(single_map[ch])
        i += 1
    return result

def vigenere_decrypt(cipher, key, mode='SUB'):
    """Decrypt cipher with Vigenere key in given mode"""
    result = []
    kl = len(key)
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'SUB':
            result.append((c - k) % 29)
        elif mode == 'ADD':
            result.append((c + k) % 29)
        elif mode == 'BEAU':  # Beaufort: key - cipher
            result.append((k - c) % 29)
    return result

def vals_to_text(vals):
    """Convert GP values to approximate English text"""
    return ''.join(GP_LETTERS[v].lower() for v in vals)

# ===== P63 GRID KEYWORDS + MODES FROM MASTER TRACKING =====
PAGE_KEYS = {
    21: ('CABAL', 'BEAU'),
    22: ('DIVINITY', 'BEAU'),
    23: ('ENCRYPTION', 'ADD'),    # Note: ENCRYPTION has letters not in GP
    24: ('OBSCURA', 'BEAU'),
    25: ('CABAL', 'BEAU'),
    26: ('ENCRYPT', 'ADD'),
    27: ('SHADOWS', 'ADD'),
    28: ('DEOR', 'SUB'),
    29: ('TOTIENT', 'BEAU'),
    30: ('MOURNFUL', 'ADD'),
}

print("=" * 80)
print("DEFINITIVE VERIFICATION: P63 Keywords on Pages 21-30")
print("GP Mapping: J-FIXED (U+16C4 = index 11)")
print("=" * 80)

for page_num in range(21, 31):
    cipher = load_page_gp(page_num)
    if not cipher:
        print(f"\nPage {page_num}: NO DATA")
        continue
    
    raw_ioc = ioc29(cipher)
    
    keyword, mode = PAGE_KEYS[page_num]
    key = keyword_to_gp(keyword)
    
    print(f"\n{'='*60}")
    print(f"PAGE {page_num}: {len(cipher)} runes, raw IoC*29={raw_ioc:.4f}")
    print(f"Keyword: {keyword} -> GP indices: {key}")
    print(f"Mode: {mode}")
    
    decrypted = vigenere_decrypt(cipher, key, mode)
    dec_ioc = ioc29(decrypted)
    
    text = vals_to_text(decrypted)
    print(f"Decrypted IoC*29: {dec_ioc:.4f}")
    print(f"First 100 chars: {text[:100]}")
    
    # Also test ALL modes
    for test_mode in ['SUB', 'ADD', 'BEAU']:
        dec2 = vigenere_decrypt(cipher, key, test_mode)
        ioc2 = ioc29(dec2)
        if ioc2 > 1.3:
            t2 = vals_to_text(dec2)
            print(f"  {test_mode}: IoC*29={ioc2:.4f} -> {t2[:60]}")

    # Also test with EVERY P63 keyword
    all_keywords = ['CABAL','DIVINITY','SHADOWS','AETHEREAL','OBSCURA',
                    'MOURNFUL','VOID','CARNAL','MOBIUS','ANALOG','BUFFERS',
                    'FORM','DEOR','TOTIENT','ENCRYPT','ENCRYPTION']
    best_ioc = 0
    best_combo = None
    for kw in all_keywords:
        k = keyword_to_gp(kw)
        if not k:
            continue
        for m in ['SUB', 'ADD', 'BEAU']:
            d = vigenere_decrypt(cipher, k, m)
            ic = ioc29(d)
            if ic > best_ioc:
                best_ioc = ic
                best_combo = (kw, m, ic)
    
    print(f"Best overall: {best_combo[0]} {best_combo[1]} IoC*29={best_combo[2]:.4f}")

# Also test on a KNOWN solved page for validation
print(f"\n{'='*60}")
print("VALIDATION: Page 03 with DIVINITY (known solution)")
p03 = load_page_gp(3)
if p03:
    print(f"Page 03: {len(p03)} runes, raw IoC*29={ioc29(p03):.4f}")
    divkey = keyword_to_gp('DIVINITY')
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = vigenere_decrypt(p03, divkey, mode)
        ic = ioc29(dec)
        text = vals_to_text(dec)
        print(f"  {mode}: IoC*29={ic:.4f} -> {text[:80]}")

print(f"\n{'='*60}")
print("VALIDATION: Page 61 with DIVINITY (our solved page)")
p61 = load_page_gp(61)
if p61:
    print(f"Page 61: {len(p61)} runes, raw IoC*29={ioc29(p61):.4f}")
    divkey = keyword_to_gp('DIVINITY')
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = vigenere_decrypt(p61, divkey, mode)
        ic = ioc29(dec)
        text = vals_to_text(dec)
        print(f"  {mode}: IoC*29={ic:.4f} -> {text[:80]}")
