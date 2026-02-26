#!/usr/bin/env python3
"""
Deep investigation of Page 61 and Page 62 with DIVINITY key.
Page 61 vigenere(DIVINITY, sub) starts with "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY..."
This is the exact plaintext of Page 03/04! 

Test hypothesis: Pages 61-62 are encrypted with DIVINITY key using F-skip rule,
same as Pages 03-04.
"""

import os
from pathlib import Path

# Gematria Primus mapping
RUNE_TO_IDX = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,
    'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,  'ᚻ': 8,  'ᚾ': 9,
    'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14,
    'ᛋ': 15, 'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19,
    'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23, 'ᚪ': 24,
    'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28, 'ᛂ': 11,
}

IDX_TO_LATIN = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R',
    5: 'C', 6: 'G', 7: 'W', 8: 'H', 9: 'N',
    10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X',
    15: 'S', 16: 'T', 17: 'B', 18: 'E', 19: 'M',
    20: 'L', 21: 'NG', 22: 'OE', 23: 'D', 24: 'A',
    25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA',
}

LATIN_TO_IDX = {}
for idx, lat in IDX_TO_LATIN.items():
    LATIN_TO_IDX[lat] = idx

SEPARATORS = {'-', '•', ' '}
PUNCTUATION = {'.', ',', ':', ';', '!', '?', '/', '%', '&', '$', '\n', '\r', "'"}

def load_runes_detailed(page_num):
    """Load runes preserving all structure (separators, punctuation)."""
    base = Path(r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages")
    runes_file = base / f"page_{page_num:02d}" / "runes.txt"
    if not runes_file.exists():
        return None, None
    
    text = runes_file.read_text(encoding='utf-8')
    
    # Build structured representation
    elements = []  # list of ('rune', idx) or ('sep', char) or ('punct', char)
    cipher_indices = []
    
    for ch in text:
        if ch in RUNE_TO_IDX:
            idx = RUNE_TO_IDX[ch]
            elements.append(('rune', idx, ch))
            cipher_indices.append(idx)
        elif ch in SEPARATORS:
            elements.append(('sep', ch, ch))
        elif ch in PUNCTUATION:
            elements.append(('punct', ch, ch))
    
    return elements, cipher_indices

def text_to_indices(text):
    """Convert plaintext to GP indices."""
    text = text.upper()
    indices = []
    i = 0
    while i < len(text):
        matched = False
        # Try trigraphs
        if i + 3 <= len(text):
            trigraph = text[i:i+3]
            if trigraph == 'ING':
                indices.append(21)  # NG/ING
                i += 3
                matched = True
        if not matched and i + 2 <= len(text):
            digraph = text[i:i+2]
            if digraph in LATIN_TO_IDX:
                indices.append(LATIN_TO_IDX[digraph])
                i += 2
                matched = True
        if not matched:
            ch = text[i]
            if ch in LATIN_TO_IDX:
                indices.append(LATIN_TO_IDX[ch])
                i += 1
            elif ch == 'K':
                indices.append(5)  # K=C
                i += 1
            elif ch == 'V':
                indices.append(1)  # V=U 
                i += 1
            elif ch == 'Q':
                indices.append(5)  # Q≈C
                i += 1
            elif ch == 'Z':
                indices.append(15)  # Z≈S
                i += 1
            else:
                i += 1
    return indices

def indices_to_text(indices):
    return ''.join(IDX_TO_LATIN.get(i, '?') for i in indices)

# DIVINITY key
DIVINITY = text_to_indices("DIVINITY")
print(f"DIVINITY key indices: {DIVINITY}")

# ==================== LOAD AND ANALYZE PAGE 61 ====================

print("\n" + "=" * 70)
print("PAGE 61 ANALYSIS")
print("=" * 70)

elements_61, cipher_61 = load_runes_detailed(61)
print(f"Total runes: {len(cipher_61)}")
print(f"Raw text: {''.join(e[2] for e in elements_61[:80])}")

# Show the raw runes structure
print(f"\nFirst 50 elements:")
for i, elem in enumerate(elements_61[:50]):
    if elem[0] == 'rune':
        print(f"  [{i}] RUNE {elem[2]} = {elem[1]} ({IDX_TO_LATIN[elem[1]]})")
    else:
        print(f"  [{i}] {elem[0].upper()}: '{elem[2]}'")

# Method 1: Simple Vigenère subtraction (no F-skip)
print("\n--- Method 1: Vigenère SUB (no F-skip) ---")
plain_1 = []
key_len = len(DIVINITY)
for i, c in enumerate(cipher_61):
    k = DIVINITY[i % key_len]
    p = (c - k) % 29
    plain_1.append(p)
text_1 = indices_to_text(plain_1)
print(f"Result: {text_1}")

# Method 2: Vigenère with F-skip (like Pages 03-04)
# When cipher rune is ᚠ (F, index 0), it's a literal F - don't advance key
print("\n--- Method 2: Vigenère SUB with F-skip ---")
plain_2 = []
key_pos = 0
for i, c in enumerate(cipher_61):
    if c == 0:  # ᚠ = F
        plain_2.append(0)  # literal F
        # DON'T advance key position
    else:
        k = DIVINITY[key_pos % key_len]
        p = (c - k) % 29
        plain_2.append(p)
        key_pos += 1
text_2 = indices_to_text(plain_2)
print(f"Result: {text_2}")

# Method 3: Vigenère ADD (no F-skip)
print("\n--- Method 3: Vigenère ADD (no F-skip) ---")
plain_3 = []
for i, c in enumerate(cipher_61):
    k = DIVINITY[i % key_len]
    p = (c + k) % 29
    plain_3.append(p)
text_3 = indices_to_text(plain_3)
print(f"Result: {text_3}")

# Method 4: Beaufort (K - C) mod 29
print("\n--- Method 4: Beaufort (no F-skip) ---")
plain_4 = []
for i, c in enumerate(cipher_61):
    k = DIVINITY[i % key_len]
    p = (k - c) % 29
    plain_4.append(p)
text_4 = indices_to_text(plain_4)
print(f"Result: {text_4}")

# Method 5: Vigenère SUB with F-skip (cipher = F → output F, DON'T advance key)
# But check if the CIPHER contains ᚠ
f_positions = [i for i, c in enumerate(cipher_61) if c == 0]
print(f"\n\nF (ᚠ) positions in cipher: {f_positions}")
print(f"Total F runes: {len(f_positions)}")

# Method 6: Try different key starting positions (key continuation from previous page)
print("\n--- Method 6: Vigenère SUB with key offset ---")
for offset in range(8):
    plain = []
    for i, c in enumerate(cipher_61):
        k = DIVINITY[(i + offset) % key_len]
        p = (c - k) % 29
        plain.append(p)
    text = indices_to_text(plain)
    # Count common words
    text_upper = text.upper()
    word_count = sum(1 for w in ['THE', 'AND', 'YOU', 'FOR', 'ALL', 'THIS', 'THAT', 'WITH', 'WITHIN', 'WELCOME', 'PILGRIM'] if w in text_upper)
    print(f"  Offset {offset}: {text[:100]}  (words: {word_count})")

# Method 7: Try C+K (add cipher + key) like some Cicada pages use
print("\n--- Method 7: C+K mod 29 (no F-skip) ---")
plain_7 = []
for i, c in enumerate(cipher_61):
    k = DIVINITY[i % key_len]
    p = (c + k) % 29
    plain_7.append(p)
text_7 = indices_to_text(plain_7)
print(f"Result: {text_7[:200]}")

# Since Method 1 starts with "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END O..."
# Let's see where it breaks and try to fix the F-skip issue
print("\n\n" + "=" * 70)
print("DETAILED ALIGNMENT ANALYSIS")
print("=" * 70)

# Known plaintext from page 03/04
known_plain = """WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF"""

known_indices = text_to_indices(known_plain)
print(f"Known plaintext length: {len(known_indices)} GP indices")
print(f"Cipher length: {len(cipher_61)}")

# Derive key stream from known plaintext
print("\n--- Derived key (cipher - known_plain) mod 29 ---")
derived_key = []
for i in range(min(len(cipher_61), len(known_indices))):
    k = (cipher_61[i] - known_indices[i]) % 29
    derived_key.append(k)

# Show derived key vs expected DIVINITY key
print("Position | Cipher | Plain | Derived_K | Expected_K (DIVINITY)")
divinity_cycle = DIVINITY * ((len(cipher_61) // len(DIVINITY)) + 1)
mismatches = []
for i in range(min(60, len(derived_key))):
    expected_k = divinity_cycle[i]
    match = "✓" if derived_key[i] == expected_k else "✗"
    if derived_key[i] != expected_k:
        mismatches.append(i)
    print(f"  {i:3d}     | {cipher_61[i]:2d} ({IDX_TO_LATIN[cipher_61[i]]:3s}) | {known_indices[i]:2d} ({IDX_TO_LATIN[known_indices[i]]:3s}) | {derived_key[i]:2d} ({IDX_TO_LATIN[derived_key[i]]:3s}) | {expected_k:2d} ({IDX_TO_LATIN[expected_k]:3s}) {match}")

print(f"\nFirst 60 positions: {len(mismatches)} mismatches at: {mismatches}")

# If there are F-skips, try to identify them
# When cipher=ᚠ AND plain=F, no key was used → skip
# Check which positions have cipher == 0 (F)
print(f"\n--- F-skip analysis ---")
f_in_cipher = [i for i in range(len(cipher_61)) if cipher_61[i] == 0]
print(f"Cipher ᚠ positions: {f_in_cipher[:30]}")

f_in_plain = [i for i in range(min(len(cipher_61), len(known_indices))) if known_indices[i] == 0]
print(f"Plain F positions: {f_in_plain[:30]}")

both_f = [i for i in range(min(len(cipher_61), len(known_indices))) if cipher_61[i] == 0 and known_indices[i] == 0]
print(f"Both F positions: {both_f[:30]}")

# Now try with F-skip: when both cipher AND derived-plain are F, skip key
print("\n--- Method 8: Vigenère SUB with proper F-skip ---")
plain_8 = []
key_pos = 0
for i, c in enumerate(cipher_61):
    if c == 0:
        # Check: if decrypting with current key position gives F (0), then it's literal
        k = DIVINITY[key_pos % key_len]
        trial_p = (c - k) % 29
        if trial_p == 0:
            # Decrypt gives F when cipher is F → literal F, still advance key? 
            # Actually in the community method: if cipher is ᚠ, output literal F, DON'T advance
            plain_8.append(0)
            # Don't advance key
        else:
            # Cipher is F but decrypt doesn't give F → actually encrypted
            p = (c - k) % 29
            plain_8.append(p)
            key_pos += 1
    else:
        k = DIVINITY[key_pos % key_len]
        p = (c - k) % 29
        plain_8.append(p)
        key_pos += 1
text_8 = indices_to_text(plain_8)
print(f"Result: {text_8[:300]}")

# Check exact match length
print("\n--- Exact match comparison ---")
for method_name, result in [("No F-skip", plain_1), ("F-skip (always)", plain_2), ("F-skip (smart)", plain_8)]:
    match_len = 0
    for i in range(min(len(result), len(known_indices))):
        if result[i] == known_indices[i]:
            match_len += 1
        else:
            break
    full_result = indices_to_text(result)
    print(f"\n{method_name}: First {match_len} chars match")
    print(f"  Text: {full_result[:200]}")

# ==================== PAGE 62 ====================
print("\n\n" + "=" * 70)
print("PAGE 62 ANALYSIS")  
print("=" * 70)

elements_62, cipher_62 = load_runes_detailed(62)
print(f"Total runes: {len(cipher_62)}")

# Test with DIVINITY
for method_name, op in [("SUB", lambda c, k: (c - k) % 29), 
                         ("ADD", lambda c, k: (c + k) % 29),
                         ("Beaufort", lambda c, k: (k - c) % 29)]:
    plain = []
    for i, c in enumerate(cipher_62):
        k = DIVINITY[i % key_len]
        p = op(c, k)
        plain.append(p)
    text = indices_to_text(plain)
    print(f"\n  DIVINITY {method_name}: {text}")

# Try DIVINITY with F-skip on Page 62
print("\n  DIVINITY SUB + F-skip:")
plain_62f = []
key_pos = 0
for i, c in enumerate(cipher_62):
    if c == 0:
        plain_62f.append(0)
    else:
        k = DIVINITY[key_pos % key_len]
        p = (c - k) % 29
        plain_62f.append(p)
        key_pos += 1
text_62f = indices_to_text(plain_62f)
print(f"  Result: {text_62f}")

# Try continuation from Page 61
# If Page 61 uses DIVINITY key and ends at some key position, Page 62 continues
print("\n  Page 62 with DIVINITY key offset (continuation from P61):")
for offset in range(8):
    plain = []
    for i, c in enumerate(cipher_62):
        k = DIVINITY[(i + offset) % key_len]
        p = (c - k) % 29
        plain.append(p)
    text = indices_to_text(plain)
    print(f"    Offset {offset}: {text}")

# ==================== PAGE 60 ====================
print("\n\n" + "=" * 70)
print("PAGE 60 ANALYSIS")
print("=" * 70)

elements_60, cipher_60 = load_runes_detailed(60)
if cipher_60:
    print(f"Total runes: {len(cipher_60)}")
    print(f"Raw: {''.join(IDX_TO_LATIN[c] for c in cipher_60)}")
    
    # Direct (no cipher)
    print(f"\nDirect: {''.join(IDX_TO_LATIN[c] for c in cipher_60)}")
    
    # Caesar shifts
    for shift in range(29):
        plain = [(c - shift) % 29 for c in cipher_60]
        text = indices_to_text(plain)
        if 'CHAPTER' in text.upper() or 'INTUS' in text.upper():
            print(f"Caesar {shift}: {text}")

print("\n\nDone!")
