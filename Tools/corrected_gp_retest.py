#!/usr/bin/env python3
"""
CORRECTED GP mapping verification and comprehensive retest.
Uses the CANONICAL Gematria Primus ordering from RuneSolver.py.

CRITICAL FIX: Positions 22-28 were wrong in all session 3 scripts.
CORRECT: ᛟ(OE=22), ᛞ(D=23), ᚪ(A=24), ᚫ(AE=25), ᚣ(Y=26), ᛡ(IA=27), ᛠ(EA=28)
WRONG:   ᛞ(D=22),  ᛟ(OE=23), ᛡ(A=24), ᛠ(EA=25), ᚪ(IA=26), ᚫ(AE=27), ᚣ(Y=28)

Also: V→U (index 1), K→C (index 5), Z→S (index 15), Q→C (index 5)
Also: J rune has TWO Unicode variants: ᛂ(U+16C2) and ᛄ(U+16C4), both = index 11
"""

import os, sys
from collections import Counter

# ====================== CORRECT GP MAPPING ======================
# Canonical ordering from RuneSolver.py, verified by P03 decryption
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
            'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11  # ᛄ alias for J (U+16C4)

# Letter-to-index mapping for keyword conversion
LETTER_TO_IDX = {}
for i, letters in enumerate(GP_LATIN):
    LETTER_TO_IDX[letters] = i
# Single-letter shortcuts
for i, letters in enumerate(GP_LATIN):
    if len(letters) == 1:
        LETTER_TO_IDX[letters] = i
# Additional mappings
LETTER_TO_IDX['V'] = 1   # V → U
LETTER_TO_IDX['K'] = 5   # K → C
LETTER_TO_IDX['Z'] = 15  # Z → S
LETTER_TO_IDX['Q'] = 5   # Q → C

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def keyword_to_idx(word):
    """Convert English word to GP index array, handling digraphs."""
    indices = []
    i = 0
    w = word.upper()
    while i < len(w):
        # Check digraphs first (2-letter)
        if i + 1 < len(w):
            digraph = w[i:i+2]
            if digraph in LETTER_TO_IDX:
                indices.append(LETTER_TO_IDX[digraph])
                i += 2
                continue
        # Single letter
        ch = w[i]
        if ch in LETTER_TO_IDX:
            indices.append(LETTER_TO_IDX[ch])
        i += 1
    return indices

def ioc29(indices):
    """Index of coincidence * 29."""
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return runes_to_indices(text)

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

# Fix Unicode output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ====================== PART 1: VERIFY MAPPING ======================
print("=" * 80)
print("PART 1: VERIFY CORRECT GP MAPPING")
print("=" * 80)

# Print mapping
print("\nGP Rune Order (indices 22-28 are the critical ones):")
for i in range(29):
    print(f"  [{i:2d}] {GP_RUNES[i]} = {GP_LATIN[i]:4s} (prime {GP_PRIMES[i]})")

# Test DIVINITY keyword
div_key = keyword_to_idx('DIVINITY')
print(f"\nDIVINITY keyword: {div_key}")
print(f"  Expected: [23, 10, 1, 10, 9, 10, 16, 26]")
assert div_key == [23, 10, 1, 10, 9, 10, 16, 26], f"DIVINITY key mismatch! Got {div_key}"
print("  ✓ CORRECT!")

# ====================== PART 2: DECRYPT P03 (CONTROL TEST) ======================
print("\n" + "=" * 80)
print("PART 2: DECRYPT P03 WITH DIVINITY (CONTROL TEST)")
print("=" * 80)

p03 = load_page(3)
if p03:
    key = div_key
    print(f"P03: {len(p03)} runes, raw IoC*29 = {ioc29(p03):.4f}")
    
    # Standard Vigenère subtraction: plaintext = (cipher - key) % 29
    ext_key = (key * (len(p03) // len(key) + 1))[:len(p03)]
    dec_sub = [(p03[i] - ext_key[i]) % 29 for i in range(len(p03))]
    text_sub = indices_to_latin(dec_sub)
    print(f"  SUB mode IoC*29 = {ioc29(dec_sub):.4f}")
    print(f"  Text: {text_sub[:100]}")
    
    # Beaufort: plaintext = (key - cipher) % 29
    dec_beau = [(ext_key[i] - p03[i]) % 29 for i in range(len(p03))]
    text_beau = indices_to_latin(dec_beau)
    print(f"  BEAUFORT IoC*29 = {ioc29(dec_beau):.4f}")
    print(f"  Text: {text_beau[:100]}")
    
    # ADD: plaintext = (cipher + key) % 29
    dec_add = [(p03[i] + ext_key[i]) % 29 for i in range(len(p03))]
    text_add = indices_to_latin(dec_add)
    print(f"  ADD mode IoC*29 = {ioc29(dec_add):.4f}")
    print(f"  Text: {text_add[:100]}")
    
    # Check if any starts with WELCOME
    for name, text in [('SUB', text_sub), ('BEAUFORT', text_beau), ('ADD', text_add)]:
        if text.startswith('WELCOME'):
            print(f"\n  ✓ {name} MODE PRODUCES 'WELCOME...' — MAPPING IS CORRECT!")

# ====================== PART 3: IOC VERIFICATION FOR P21-30 ======================
print("\n" + "=" * 80)
print("PART 3: IOC VERIFICATION FOR PAGES 21-30 WITH CORRECT MAPPING")
print("=" * 80)

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

for pn in range(21, 31):
    cipher = load_page(pn)
    if not cipher:
        continue
    
    claim_kw, claim_mode = CLAIMED_KEYS[pn]
    key = keyword_to_idx(claim_kw)
    ext_key = (key * (len(cipher) // len(key) + 1))[:len(cipher)]
    
    print(f"\nP{pn}: {len(cipher)} runes, raw IoC = {ioc29(cipher):.4f}")
    print(f"  Key: {claim_kw} = {key}")
    
    for mode in ['sub', 'add', 'beaufort']:
        if mode == 'sub':
            dec = [(cipher[i] - ext_key[i]) % 29 for i in range(len(cipher))]
        elif mode == 'add':
            dec = [(cipher[i] + ext_key[i]) % 29 for i in range(len(cipher))]
        else:
            dec = [(ext_key[i] - cipher[i]) % 29 for i in range(len(cipher))]
        
        ic = ioc29(dec)
        marker = " <--- CLAIMED" if mode == claim_mode else ""
        if ic > 1.3:
            marker += " ***HIGH IoC***"
        print(f"  {mode:10s}: IoC*29 = {ic:.4f}{marker}")
        if mode == claim_mode or ic > 1.3:
            text = indices_to_latin(dec)[:80]
            print(f"    Text: {text}")

# ====================== PART 4: EXHAUSTIVE KEYWORD SEARCH P18-54 ======================
print("\n" + "=" * 80)
print("PART 4: EXHAUSTIVE KEYWORD SEARCH (all keywords × all modes × pages 18-54)")
print("=" * 80)

ALL_KEYWORDS = {}
kw_list = [
    'DIVINITY', 'CABAL', 'SHADOWS', 'AETHEREAL', 'OBSCURA', 'MOBIUS',
    'MOURNFUL', 'VOID', 'CARNAL', 'ANALOG', 'FORM', 'TOTIENT', 'PRIMES',
    'WISDOM', 'ENCRYPT', 'ENCRYPTION', 'FIRFUMFERENFE', 'CICADA', 'CONSUMPTION',
    'INSTAR', 'CIRCUMFERENCE', 'PILGRIM', 'SACRED', 'DEOR', 'BUFFERS',
    'WARNING', 'WELCOME', 'BELIEVE', 'QUESTION', 'INSTRUCTION', 'LIBER',
    'PRIMUS', 'INTUS', 'KOAN', 'PARABLE', 'YAHEOOPYJ', 'SUOID', 'EMERGENCE',
    'ADHERENCE', 'COMMAND', 'SELF', 'HOLY', 'INTELLIGENCE', 'JOURNEY',
    'TRUTH', 'DEATH', 'KNOWLEDGE', 'EXPERIENCE', 'NOTHING', 'PRESERVE'
]
for kw in kw_list:
    key = keyword_to_idx(kw)
    if key:
        ALL_KEYWORDS[kw] = key

hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    
    for kw_name, key in ALL_KEYWORDS.items():
        ext_key = (key * (len(cipher) // len(key) + 1))[:len(cipher)]
        
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
    for ic, pn, kw, mode, text in hits[:40]:
        print(f"  P{pn:02d} {kw:16s}/{mode:8s}: IoC*29 = {ic:.4f}  {text}")
else:
    print("\n  *** NO RESULTS WITH IoC > 1.3 FOUND ***")

# ====================== PART 5: F-SKIP VIGENERE TEST ======================
print("\n" + "=" * 80)
print("PART 5: F-SKIP VIGENÈRE (DIVINITY key on all pages)")
print("=" * 80)

def fskip_vigenere(cipher_indices, key_indices, mode='sub'):
    """Vigenère where F runes (index 0) don't advance the key."""
    result = []
    k = 0
    for c in cipher_indices:
        if c == 0:  # F rune - literal, key doesn't advance
            result.append(0)
        else:
            kv = key_indices[k % len(key_indices)]
            if mode == 'sub':
                result.append((c - kv) % 29)
            elif mode == 'add':
                result.append((c + kv) % 29)
            else:  # beaufort
                result.append((kv - c) % 29)
            k += 1
    return result

FSKIP_KEYWORDS = {
    'DIVINITY': keyword_to_idx('DIVINITY'),
    'FIRFUMFERENFE': keyword_to_idx('FIRFUMFERENFE'),
    'CABAL': keyword_to_idx('CABAL'),
    'SHADOWS': keyword_to_idx('SHADOWS'),
    'OBSCURA': keyword_to_idx('OBSCURA'),
    'MOURNFUL': keyword_to_idx('MOURNFUL'),
    'TOTIENT': keyword_to_idx('TOTIENT'),
    'ENCRYPT': keyword_to_idx('ENCRYPT'),
    'ENCRYPTION': keyword_to_idx('ENCRYPTION'),
    'DEOR': keyword_to_idx('DEOR'),
}

fskip_hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    
    for kw_name, key in FSKIP_KEYWORDS.items():
        for mode in ['sub', 'add', 'beaufort']:
            # Test with different starting offsets
            for offset in range(len(key)):
                shifted_key = key[offset:] + key[:offset]
                dec = fskip_vigenere(cipher, shifted_key, mode)
                ic = ioc29(dec)
                if ic > 1.3:
                    text = indices_to_latin(dec)[:60]
                    fskip_hits.append((ic, pn, kw_name, mode, offset, text))

fskip_hits.sort(reverse=True)
if fskip_hits:
    print(f"\nFound {len(fskip_hits)} F-skip results with IoC > 1.3:")
    for ic, pn, kw, mode, off, text in fskip_hits[:40]:
        print(f"  P{pn:02d} {kw:16s}/{mode:8s} off={off}: IoC*29 = {ic:.4f}  {text}")
else:
    print("\n  *** NO F-SKIP RESULTS WITH IoC > 1.3 FOUND ***")

# ====================== PART 6: TOTIENT STREAM CIPHER ======================
print("\n" + "=" * 80)
print("PART 6: TOTIENT STREAM CIPHER (correct GP)")
print("=" * 80)

def generate_primes(n):
    """Generate first n primes."""
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes

def euler_totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

# Generate totient keystream: φ(prime_i) - 1
primes = generate_primes(2000)
totient_stream = [euler_totient(p) for p in primes]  # φ(p) = p-1 for prime p

totient_hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20:
        continue
    
    n = len(cipher)
    
    # Standard totient: plaintext = (cipher - (prime-1)) % 29 (as used on P56)
    for mode_name, op in [('sub', lambda c, k: (c - k) % 29), 
                           ('add', lambda c, k: (c + k) % 29),
                           ('beau', lambda c, k: (k - c) % 29)]:
        # Different starting positions in the prime sequence
        for start in range(0, 50, 1):
            dec = [op(cipher[i], totient_stream[start + i] % 29) for i in range(n)]
            ic = ioc29(dec)
            if ic > 1.3:
                text = indices_to_latin(dec)[:60]
                totient_hits.append((ic, pn, mode_name, start, text))

        # F-skip variant: F runes don't consume keystream
        for start in range(0, 20):
            dec = []
            k = start
            for c in cipher:
                if c == 0:
                    dec.append(0)
                else:
                    dec.append(op(c, totient_stream[k] % 29))
                    k += 1
            ic = ioc29(dec)
            if ic > 1.3:
                text = indices_to_latin(dec)[:60]
                totient_hits.append((ic, pn, f'{mode_name}_fskip', start, text))

totient_hits.sort(reverse=True)
if totient_hits:
    print(f"\nFound {len(totient_hits)} totient results with IoC > 1.3:")
    for ic, pn, mode, start, text in totient_hits[:30]:
        print(f"  P{pn:02d} {mode:12s} start={start:3d}: IoC*29 = {ic:.4f}  {text}")
else:
    print("\n  *** NO TOTIENT RESULTS WITH IoC > 1.3 ***")

# ====================== PART 7: CHECK RAW IOC OF ALL PAGES ======================
print("\n" + "=" * 80)
print("PART 7: RAW IoC OF ALL PAGES (with correct mapping)")
print("=" * 80)

for pn in range(0, 75):
    cipher = load_page(pn)
    if cipher and len(cipher) > 10:
        ic = ioc29(cipher)
        status = "SOLVED" if ic > 1.3 else "encrypted"
        print(f"  P{pn:02d}: {len(cipher):5d} runes, IoC*29 = {ic:.4f}  ({status})")

print("\n=== CORRECTED VERIFICATION COMPLETE ===")
