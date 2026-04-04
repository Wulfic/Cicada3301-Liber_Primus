#!/usr/bin/env python3
"""
Structural Analysis — P27=P44 relationship + novel cipher hypotheses
=====================================================================
1. Count P28-P43 runes, test mod 71/83 hypothesis
2. Test prime-indexed primes (PIPs) stream
3. Test P.S. number as key material
4. Test 7x7 magic square as keystream
5. Test P27+P44=71 page-number arithmetic for other page pairs
6. Complete P02 and P18 key recovery
"""

import sys, os, re
from pathlib import Path
from collections import Counter
from itertools import product
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
DATA_DIR = BASE / "data"

# === Gematria Primus ===
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0, 0), (0x16A2, 1), (0x16A6, 2), (0x16A9, 3), (0x16B1, 4),
    (0x16B3, 5), (0x16B7, 6), (0x16B9, 7), (0x16BB, 8), (0x16BE, 9),
    (0x16C1, 10), (0x16C4, 11), (0x16C7, 12), (0x16C8, 13), (0x16C9, 14),
    (0x16CB, 15), (0x16CF, 16), (0x16D2, 17), (0x16D6, 18), (0x16D7, 19),
    (0x16DA, 20), (0x16DD, 21), (0x16DF, 22), (0x16DE, 23), (0x16AA, 24),
    (0x16AB, 25), (0x16A3, 26), (0x16E1, 27), (0x16E0, 28),
]}
IDX_TO_LETTER = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
                  'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']

SEPARATORS = set('-. \n\r\t\u2022•/&$%')

def load_runes_raw(page_num):
    """Load runes as flat list of GP indices, preserving word boundaries."""
    path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not path.exists():
        return [], []
    with open(path, encoding='utf-8') as f:
        text = f.read()
    words = []
    current = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            current.append(RUNE_TO_IDX[ch])
        elif ch in SEPARATORS:
            if current:
                words.append(tuple(current))
                current = []
    if current:
        words.append(tuple(current))
    flat = [r for w in words for r in w]
    return flat, words

def ioc(values):
    if len(values) < 2:
        return 0.0
    c = Counter(values)
    n = len(values)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))

def decrypt(flat, key, mode='sub'):
    kl = len(key)
    if mode == 'sub':
        return [(flat[i] - key[i % kl]) % 29 for i in range(len(flat))]
    elif mode == 'add':
        return [(flat[i] + key[i % kl]) % 29 for i in range(len(flat))]
    elif mode == 'beaufort':
        return [(key[i % kl] - flat[i]) % 29 for i in range(len(flat))]
    return flat

def indices_to_text(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)

def score_english(text):
    score = 0
    words = re.findall(r'[A-Z]+', text.replace('TH', 'Z').replace('NG', 'Q').
                       replace('EA', 'X').replace('OE', 'V').replace('IO', 'K'))
    common = {'THE','AND','FOR','ARE','NOT','YOU','ALL','THIS','THAT','WITH',
              'HAVE','FROM','THEY','BEEN','WILL','INTO','THAN','THEM','WHEN',
              'SELF','TRUTH','SACRED','WISDOM','WITHIN','BEING','EACH','HOLY',
              'PATH','FIND','FOLLOW','KNOW','ALL','ONLY','COME','GREAT','ONE',
              'WAY','TRUE','TEST','SEEK','BOOK','DEEP','WEB','PAGE','DUTY',
              'EVERY','PILGRIM','INSTRUCTION','DIVINITY','CONSUMPTION','LIKE',
              'INSTAR','COMMAND','LAW','END','EMERGE','ABOVE','BEYOND','LOSS',
              'DEATH','DISCOVER','IMPOSE','QUESTION','CERTAINTY','CERTAINTY'}
    for w in words:
        if len(w) >= 4 and w in common:
            score += len(w) * 3
        elif len(w) >= 3 and w in common:
            score += len(w) * 2
    return score

def check_singleton_constraint(plain_words):
    """All single-rune words must be I(10) or A(24)."""
    for w in plain_words:
        if len(w) == 1 and w[0] not in (10, 24):
            return False
    return True

# ============================================================
# STEP 1: Count runes in P28-P43, check mod 71/83
# ============================================================
print("=" * 60)
print("STEP 1: P28-P43 Rune Count Analysis")
print("=" * 60)

total = 0
counts = {}
for p in range(28, 44):
    flat, words = load_runes_raw(p)
    counts[p] = len(flat)
    total += len(flat)
    print(f"P{p:02d}: {len(flat)} runes")

print(f"\nTotal P28-P43: {total} runes")
print(f"Total mod 71: {total % 71}")
print(f"Total mod 83: {total % 83}")
print(f"Total mod 17: {total % 17}")
print(f"Total mod 29: {total % 29}")
for prime in [7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]:
    if total % prime == 0:
        print(f"  *** Total is divisible by {prime} ***")

# Also check P27 vs P44 ciphertext to confirm they match
print("\nVerifying P27=P44[0:234]:")
flat27, _ = load_runes_raw(27)
flat44, _ = load_runes_raw(44)
match = flat27 == flat44[:len(flat27)]
print(f"  P27 length: {len(flat27)}, P44 length: {len(flat44)}")
print(f"  P27 == P44[:234]: {match}")
if not match:
    for i, (a, b) in enumerate(zip(flat27, flat44)):
        if a != b:
            print(f"  First mismatch at position {i}: {a} != {b}")
            break

# ============================================================
# STEP 2: Page number arithmetic — find pairs where a+b = 71 or a-b = 17
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Page Number Arithmetic Pairs")
print("=" * 60)

pages_unsolved = list(range(21, 55))
print("Pairs with a+b = 71 (key length for odd-quarter pages):")
for i, a in enumerate(pages_unsolved):
    for b in pages_unsolved[i+1:]:
        if a + b == 71:
            flat_a, _ = load_runes_raw(a)
            flat_b, _ = load_runes_raw(b)
            min_len = min(len(flat_a), len(flat_b))
            matches = sum(1 for x,y in zip(flat_a[:min_len], flat_b[:min_len]) if x==y)
            print(f"  P{a}+P{b}=71 | match={matches}/{min_len}")

print("Pairs with |a-b| = 17 (P17 reference):")
for i, a in enumerate(pages_unsolved):
    for b in pages_unsolved[i+1:]:
        if abs(a - b) == 17:
            flat_a, _ = load_runes_raw(a)
            flat_b, _ = load_runes_raw(b)
            min_len = min(len(flat_a), len(flat_b))
            matches = sum(1 for x,y in zip(flat_a[:min_len], flat_b[:min_len]) if x==y)
            if matches > min_len * 0.1:
                print(f"  P{a}-P{b}=17 | match={matches}/{min_len}")

print("Pages where p mod 17 = 10 (same class as P27, P44):")
for p in range(0, 75):
    if p % 17 == 10:
        print(f"  P{p} (mod17={p%17})", end="")
        flat, _ = load_runes_raw(p)
        print(f" [{len(flat)} runes]")

# ============================================================
# STEP 3: Prime-Indexed Primes (PIPs) as keystream
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Prime-Indexed Primes (PIPs) Keystream")
print("=" * 60)

def sieve(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, limit+1, i):
                is_prime[j] = False
    return [i for i in range(2, limit+1) if is_prime[i]]

primes = sieve(1000000)
# PIPs: prime[prime[n]] for n starting at 1
pips = [primes[primes[n]-1] for n in range(min(50000, len(primes))) 
        if primes[n]-1 < len(primes)]
pips_key = [p % 29 for p in pips]
print(f"Generated {len(pips_key)} PIPs mod 29")
print(f"First 20 PIPs: {pips[:20]}")
print(f"First 20 PIPs mod 29: {pips_key[:20]}")

# Test PIPs keystream on all unsolved pages
print("\nTesting PIPs on unsolved pages (best mode per page):")
best_results_pips = []
for p in list(range(21, 55)):
    flat, words = load_runes_raw(p)
    if not flat:
        continue
    best = None
    for offset in range(0, min(1000, len(pips_key) - len(flat))):
        key_segment = pips_key[offset:offset+len(flat)]
        if len(key_segment) < len(flat):
            break
        for mode in ['sub', 'add', 'beaufort']:
            plain = decrypt(flat, key_segment, mode)
            plain_words = []
            pos = 0
            for w in words:
                plain_words.append(tuple(plain[pos:pos+len(w)]))
                pos += len(w)
            if not check_singleton_constraint(plain_words):
                continue
            iv = ioc(plain)
            if iv > 1.3:
                text = indices_to_text(plain[:100])
                score = score_english(text)
                if best is None or iv > best[0]:
                    best = (iv, offset, mode, text, score)
    if best and best[0] > 1.3:
        print(f"  P{p:02d}: IoC={best[0]:.4f} offset={best[1]} mode={best[2]} score={best[4]}")
        print(f"    Text: {best[3][:80]}")
        best_results_pips.append((p, best))

if not best_results_pips:
    print("  No PIPs results with IoC > 1.3")

# ============================================================
# STEP 4: P.S. Number as Key Material
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: P.S. Number as Key Material")
print("=" * 60)

PS_NUMBER = "104127906589199853598278987395943189564044251069556756437392269523726824238529590817398343903703744757648634152034234993571087136311"
print(f"P.S. number: {PS_NUMBER}")
print(f"Length: {len(PS_NUMBER)} digits")

# Encoding 1: Each digit directly (0-9)
key_digits = [int(d) for d in PS_NUMBER]
print(f"Digit key (first 20): {key_digits[:20]}")

# Encoding 2: Digit pairs mod 29
key_pairs = [int(PS_NUMBER[i:i+2]) % 29 for i in range(0, len(PS_NUMBER)-1, 2)]
print(f"Digit-pair key (first 20): {key_pairs[:20]}")

# Encoding 3: Convert to base 29
n = int(PS_NUMBER)
base29 = []
while n > 0:
    base29.append(int(n % 29))
    n //= 29
base29.reverse()
print(f"Base-29 key ({len(base29)} elements, first 20): {base29[:20]}")
print(f"Base-29 length: {len(base29)}, is prime: {len(base29) in primes[:500]}")

# Test all encodings
for key_name, key_data in [('digits', key_digits), ('pairs', key_pairs), ('base29', base29)]:
    print(f"\nTesting PS-number ({key_name}) on unsolved pages:")
    found_any = False
    for p in list(range(21, 55)):
        flat, words = load_runes_raw(p)
        if not flat or len(flat) > len(key_data):
            continue
        for offset in range(0, min(50, len(key_data) - len(flat))):
            key_seg = key_data[offset:offset+len(flat)]
            for mode in ['sub', 'add', 'beaufort']:
                plain = decrypt(flat, key_seg, mode)
                plain_words = []
                pos = 0
                for w in words:
                    plain_words.append(tuple(plain[pos:pos+len(w)]))
                    pos += len(w)
                if not check_singleton_constraint(plain_words):
                    continue
                iv = ioc(plain)
                if iv > 1.3:
                    text = indices_to_text(plain[:100])
                    score = score_english(text)
                    found_any = True
                    print(f"  P{p:02d}: IoC={iv:.4f} offset={offset} mode={mode} score={score}")
                    print(f"    {text[:80]}")
    if not found_any:
        print(f"  No results with IoC > 1.3 for {key_name} encoding")

# ============================================================
# STEP 5: 7x7 Magic Square as Keystream
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: 7x7 Magic Square (OpenPuff) as Keystream")
print("=" * 60)

magic_7x7 = [
    7, 375, 236, 190, 27, 17, 181,
    351, 223, 14, 47, 293, 98, 7,
    # Note: we only have partial data from tracker §9.7
    # Using first two rows (14 values), rest estimated to sum to 1033 each
]
# Full 7x7 from tracker: "7 375 236 190 27 17 181 / 351 223 14 47 293 98 7 / ..."
# We have only partial data. Let me use what's available.
# The tracker says "7×7 square (also sums to 1033)"
# Row 1: 7 375 236 190 27 17 181 → sum = 1033
# Row 2: 351 223 14 47 293 98 7 → sum = 1033
# Sums verify: 7+375+236+190+27+17+181=1033 ✓, 351+223+14+47+293+98+7=1033 ✓

key_7x7 = [v % 29 for v in magic_7x7]
print(f"7x7 magic square values (first 14): {magic_7x7}")
print(f"Keys mod 29 (first 14): {key_7x7}")

# ============================================================
# STEP 6: Complete P02 Key Recovery
# ============================================================
print("\n" + "=" * 60)
print("STEP 6: P02 Key Recovery (Crib Dragging Completion)")
print("=" * 60)

flat02, words02 = load_runes_raw(2)
print(f"P02: {len(flat02)} runes, {len(words02)} words")

# Known partial key from tracker
key02 = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1, 
          6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]

# Show current decryption
plain02 = decrypt(flat02, key02, 'sub')
word_texts = []
pos = 0
for w in words02:
    wt = indices_to_text(plain02[pos:pos+len(w)])
    word_texts.append(wt)
    pos += len(w)
print("Current P02 decryption:")
print(' '.join(word_texts[:30]))
print()

# P02 context: mirrors P60 "CHAPTER I INTUS" and P02 itself should be similar
# Based on LP structure, P02 is expected to contain "CHAPTER..." header content
# Known fragments: "SAME AS THAT", "THE OTHER", "WITH A", "THE SONG"

# Known Cicada crib words to try dragging
CRIBS = [
    "CHAPTER", "INTUS", "WELCOME", "PILGRIM", "DIVINITY", "SACRED",
    "WISDOM", "TRUTH", "WITHIN", "BEING", "SELF", "PATH", "GREAT",
    "JOURNEY", "SAME", "OTHER", "SONG", "WITH", "THE", "AND",
    "FIND", "SEEK", "DEEP", "WEB", "INSTRUCTION", "CONSUME", "EACH",
    "YOUR", "ALL", "WILL", "LOOK", "FROM", "HOLY", "UNTO", "LAW",
]

def crib_drag(flat, words, partial_key, key_len, crib_indices, crib_pos, mode='sub'):
    """Try to derive key values from a crib at a given position."""
    results = []
    for pos in range(len(flat) - len(crib_indices)):
        if mode == 'sub':
            derived = [(flat[pos+i] - crib_indices[i]) % 29 for i in range(len(crib_indices))]
        elif mode == 'add':
            derived = [(crib_indices[i] - flat[pos+i]) % 29 for i in range(len(crib_indices))]
        # Check if these key values are consistent with partial_key
        key_pos = [((pos + i) % key_len) for i in range(len(derived))]
        consistent = True
        for kp, kv in zip(key_pos, derived):
            if partial_key[kp] is not None and partial_key[kp] != kv:
                consistent = False
                break
        if consistent:
            results.append((pos, derived, key_pos))
    return results

# Convert cribs to GP indices
def text_to_gp(text):
    """Convert text string to GP indices."""
    letter_to_idx = {v: k for k, v in enumerate(IDX_TO_LETTER)}
    # We need to parse multi-char letters (TH, NG, OE, EA, IO, EO, AE)
    idx = 0
    result = []
    text = text.upper()
    i = 0
    while i < len(text):
        # Try 2-char matches first
        c2 = text[i:i+2]
        if c2 in letter_to_idx:
            result.append(letter_to_idx[c2])
            i += 2
        elif text[i] in letter_to_idx:
            result.append(letter_to_idx[text[i]])
            i += 1
        else:
            i += 1  # skip unknown
    return result

# Build flexible key (None = unknown)
flex_key = list(key02)  # start with known key

# Apply current key decryption
plain_current = decrypt(flat02, flex_key, 'sub')
pos = 0; current_text = []
for w in words02:
    current_text.append(indices_to_text(plain_current[pos:pos+len(w)]))
    pos += len(w)
print("P02 word-by-word with known key:")
for i, (w, t) in enumerate(zip(words02, current_text)):
    ki_start = sum(len(ww) for ww in words02[:i]) % 43
    print(f"  Word {i:2d} (ki:{ki_start:2d}): cipher_len={len(w)} -> '{t}'")

# ============================================================
# STEP 7: Complete P18 Key Recovery
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: P18 Key Recovery (Fill Missing Positions)")
print("=" * 60)

flat18, words18 = load_runes_raw(18)
print(f"P18: {len(flat18)} runes, {len(words18)} words")

# Current known key (53 elements)
key18 = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16, 
          9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24, 
          22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]

plain18 = decrypt(flat18, key18, 'sub')
word18_texts = []
pos = 0
for w in words18:
    word18_texts.append(indices_to_text(plain18[pos:pos+len(w)]))
    pos += len(w)
print("Current P18 decryption:")
print(' '.join(word18_texts))

# Known fragment: "BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY"
# Needs to be extended. P18 appears to be about an "oath" or "pledge" to Cicada
# Try to find more of the plaintext using expected LP content patterns

# Expected extensions based on LP theme:
# "BEING OF ALL I WILL ASC THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY"
# Common LP phrases after this: "MAKE KNOWN", "SEEK TRUTH", "FOLLOW PATH", etc.
# Also: the word "ASC" → "ASK" (K→C substitution), so "I WILL ASK" is the fragment

# The key positions where text is garbled:
print("\nSearching for garbled positions...")
for i, (w, t) in enumerate(zip(words18, word18_texts)):
    if len(t) >= 2 and not any(wrd in t for wrd in ['THE', 'OF', 'ALL', 'I', 'WILL', 'ASC', 
                                                       'OATH', 'IS', 'SWORN', 'TO', 'ONE', 
                                                       'WITHIN', 'ABOVE', 'WAY', 'BEING']):
        print(f"  Word {i}: '{t}' (len={len(t)}, starting key pos {sum(len(ww) for ww in words18[:i]) % 53})")

# ============================================================
# STEP 8: Summary of mod-17 page class analysis  
# ============================================================
print("\n" + "=" * 60)
print("STEP 8: Mod-17 Page Class Analysis (P27=P44 → same mod-17)")
print("=" * 60)

# Group all pages by their page_num mod 17
classes = {}
for p in range(0, 75):
    mod = p % 17
    if mod not in classes:
        classes[mod] = []
    classes[mod].append(p)

print("Pages grouped by page_number mod 17:")
for mod in sorted(classes.keys()):
    pages = classes[mod]
    flatlist = []
    for p in pages:
        flat, _ = load_runes_raw(p)
        flatlist.append(f"P{p}({len(flat)})")
    print(f"  mod={mod:2d}: {' '.join(flatlist)}")

# For mod-10 class (P10, P27, P44): check if P10 plaintext helps decode P27/P44
print("\nP10 (solved cleartext) similarity check with P27, P44:")
flat10, words10 = load_runes_raw(10)
flat27, words27 = load_runes_raw(27)
flat44, words44 = load_runes_raw(44)

# P10 is cleartext - so plain10 = flat10. If P27 uses P10's VALUES as key:
if flat10 and flat27:
    # Test: P27 decoded with P10 as key (Vigenère SUB)
    min_len = min(len(flat27), len(flat10))
    plain27_via_p10 = [(flat27[i] - flat10[i % len(flat10)]) % 29 for i in range(min_len)]
    text27 = indices_to_text(plain27_via_p10[:100])
    iv27 = ioc(plain27_via_p10)
    print(f"P27 decoded with P10 as key (sub): IoC={iv27:.4f}")
    print(f"  Text: {text27[:80]}")
    
    plain27_via_p10_add = [(flat27[i] + flat10[i % len(flat10)]) % 29 for i in range(min_len)]
    text27_add = indices_to_text(plain27_via_p10_add[:100])
    iv27_add = ioc(plain27_via_p10_add)
    print(f"P27 decoded with P10 as key (add): IoC={iv27_add:.4f}")
    print(f"  Text: {text27_add[:80]}")

print("\nDone. Check output above for any IoC > 1.3 hits.")
