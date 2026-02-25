"""Re-derive P19 key with the FIXED GP mapping (including J variant U+16C4).
The old key was derived from broken 255-rune text; correct count is 271."""

import os, sys

# FIXED GP mapping
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,  # Both J variants
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English to GP - handle digraphs FIRST (longest match)
def english_to_gp(text):
    """Convert English text to GP indices, handling digraphs."""
    text = text.upper()
    gp = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH':
                gp.append(2); i += 2; continue
            elif digraph == 'NG':
                gp.append(21); i += 2; continue
            elif digraph == 'EO':
                gp.append(12); i += 2; continue
            elif digraph == 'OE':
                gp.append(22); i += 2; continue
            elif digraph == 'EA':
                gp.append(28); i += 2; continue
            elif digraph == 'AE':
                gp.append(25); i += 2; continue
            elif digraph == 'IA':
                gp.append(27); i += 2; continue
        c = text[i]
        mapping = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
                   'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
                   'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}
        if c in mapping:
            gp.append(mapping[c])
        elif c == ' ':
            pass  # Skip spaces (they are word separators, not runes)
        i += 1
    return gp

def load_page(pg):
    """Load cipher runes from page file with FIXED GP mapping."""
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                text = f.read()
                runes = [GP[c] for c in text if c in GP]
                # Also get the raw text with separators for context
                return runes, text
    return None, None

def load_page_with_positions(pg):
    """Load cipher runes AND their separator positions."""
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                text = f.read()
                runes = []
                sep_positions = []  # positions where separators occur
                rune_idx = 0
                for c in text:
                    if c in GP:
                        runes.append(GP[c])
                        rune_idx += 1
                    elif c in '•:.\'-\n':
                        sep_positions.append(rune_idx)
                return runes, sep_positions
    return None, None

# Load P19
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')
cipher, raw_text = load_page(19)
cipher_pos, seps = load_page_with_positions(19)

print(f"P19 cipher runes: {len(cipher)}")
print(f"First 50 cipher values: {cipher[:50]}")
print()

# Known plaintext: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
# Let's also try extended versions
plaintext_str = "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
plain_gp = english_to_gp(plaintext_str.replace(' ',''))
print(f"Known plaintext: {plaintext_str}")
print(f"GP encoding ({len(plain_gp)} runes): {plain_gp}")
print(f"GP text: {''.join(LATIN[v] for v in plain_gp)}")
print()

# Old key for reference
OLD_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]
print(f"Old key (47): {OLD_KEY}")
print()

# === METHOD 1: Derive key from known plaintext ===
print("="*70)
print("METHOD 1: Derive key using ADD formula: plain = (cipher + key) % 29")
print("  => key = (plain - cipher) % 29")
print("="*70)

# Compute key for known positions
n_known = min(len(plain_gp), len(cipher))
derived_key_add = [(plain_gp[i] - cipher[i]) % 29 for i in range(n_known)]
print(f"Derived key (ADD, first {n_known}): {derived_key_add}")
print(f"  As text: {''.join(LATIN[v] for v in derived_key_add)}")

# Check periodicity
print(f"\nChecking period 47:")
for period in [47, 46, 48, 43, 41, 37, 53]:
    mismatches = 0
    check_positions = 0
    for i in range(n_known):
        for j in range(i + period, n_known, period):
            check_positions += 1
            if derived_key_add[i] != derived_key_add[j]:
                mismatches += 1
    if check_positions > 0:
        print(f"  Period {period}: {mismatches}/{check_positions} mismatches ({100*mismatches/check_positions:.1f}%)")

# === METHOD 2: SUB formula ===
print()
print("="*70)
print("METHOD 2: Derive key using SUB formula: plain = (cipher - key) % 29")
print("  => key = (cipher - plain) % 29")
print("="*70)

derived_key_sub = [(cipher[i] - plain_gp[i]) % 29 for i in range(n_known)]
print(f"Derived key (SUB, first {n_known}): {derived_key_sub}")
print(f"  As text: {''.join(LATIN[v] for v in derived_key_sub)}")

print(f"\nChecking period 47:")
for period in [47, 46, 48, 43, 41, 37, 53]:
    mismatches = 0
    check_positions = 0
    for i in range(n_known):
        for j in range(i + period, n_known, period):
            check_positions += 1
            if derived_key_sub[i] != derived_key_sub[j]:
                mismatches += 1
    if check_positions > 0:
        print(f"  Period {period}: {mismatches}/{check_positions} mismatches ({100*mismatches/check_positions:.1f}%)")

# === METHOD 3: Try with old key on new text ===
print()
print("="*70)
print("METHOD 3: Decrypt with OLD key on FIXED 271-rune text (ADD)")
print("="*70)

decrypted_add = [(cipher[i] + OLD_KEY[i % 47]) % 29 for i in range(len(cipher))]
dec_text_add = ''.join(LATIN[v] for v in decrypted_add)
print(f"Decrypted (ADD): {dec_text_add[:100]}...")

decrypted_sub = [(cipher[i] - OLD_KEY[i % 47]) % 29 for i in range(len(cipher))]
dec_text_sub = ''.join(LATIN[v] for v in decrypted_sub)
print(f"Decrypted (SUB): {dec_text_sub[:100]}...")

# === METHOD 4: Word-aligned key derivation ===
# The plaintext has word separators. Let me align the ciphertext word structure
# with the plaintext words.
print()
print("="*70)
print("METHOD 4: Word-aligned analysis")
print("="*70)

# Parse ciphertext words
cipher_words = []
current_word = []
for c in raw_text:
    if c in GP:
        current_word.append(GP[c])
    elif c in '•:.\'-\n' and current_word:
        cipher_words.append(current_word)
        current_word = []
if current_word:
    cipher_words.append(current_word)

# Parse plaintext words
plain_words_str = plaintext_str.split()
plain_words_gp = [english_to_gp(w) for w in plain_words_str]

print(f"Cipher words ({len(cipher_words)}): lengths = {[len(w) for w in cipher_words[:20]]}...")
print(f"Plain words ({len(plain_words_gp)}): lengths = {[len(w) for w in plain_words_gp]}")
print()

# Align words
rune_pos = 0
aligned = True
for wi, (cw, pw_str, pw_gp) in enumerate(zip(cipher_words, plain_words_str, plain_words_gp)):
    if len(cw) != len(pw_gp):
        print(f"  Word {wi} MISMATCH: cipher '{[LATIN[v] for v in cw]}' ({len(cw)} runes) vs plain '{pw_str}' ({len(pw_gp)} runes)")
        aligned = False
    else:
        keys = [(pw_gp[j] - cw[j]) % 29 for j in range(len(cw))]
        print(f"  Word {wi}: '{pw_str}' -> key positions {rune_pos}-{rune_pos+len(cw)-1}: {keys} = {''.join(LATIN[v] for v in keys)}")
    rune_pos += len(cw)

    if wi >= len(plain_words_gp) - 1:
        break

# === METHOD 5: Try all possible digraph parses ===
print()
print("="*70)
print("METHOD 5: Check if 'DEOR' should be parsed differently")
print("="*70)

for parse in ["DEOR", "D-EO-R", "D-E-O-R", "DE-O-R"]:
    gp = []
    parts = parse.replace('-','')
    # Try manual parses
    if parse == "DEOR":
        gp = english_to_gp("DEOR")
    elif parse == "D-EO-R":
        gp = [23, 12, 4]
    elif parse == "D-E-O-R":
        gp = [23, 18, 3, 4]
    elif parse == "DE-O-R":
        gp = [23, 18, 3, 4]  # same thing - no DE digraph
    print(f"  '{parse}': GP = {gp} = {''.join(LATIN[v] for v in gp)}")

# === Try extending plaintext beyond known portion ===
print()
print("="*70)
print("METHOD 6: If key has period 47, decrypt BEYOND known plaintext")
print("="*70)

# Check ADD with period 47
# use first 47 key values from ADD derivation
if len(derived_key_add) >= 47:
    key47_new = derived_key_add[:47]
    print(f"New key (ADD, period 47): {key47_new}")
    full_dec = [(cipher[i] + key47_new[i % 47]) % 29 for i in range(len(cipher))]
    full_text = ''.join(LATIN[v] for v in full_dec)
    print(f"Full decryption (ADD):")
    # Print in chunks
    pos = 0
    for cw in cipher_words:
        word_dec = [full_dec[pos + j] for j in range(len(cw))]
        word_text = ''.join(LATIN[v] for v in word_dec)
        print(f"  {word_text}", end=' ')
        pos += len(cw)
        if pos > 200:
            print("...")
            break
    print()

# Check SUB with period 47
if len(derived_key_sub) >= 47:
    key47_new_sub = derived_key_sub[:47]
    print(f"\nNew key (SUB, period 47): {key47_new_sub}")
    full_dec_sub = [(cipher[i] - key47_new_sub[i % 47]) % 29 for i in range(len(cipher))]
    full_text_sub = ''.join(LATIN[v] for v in full_dec_sub)
    print(f"Full decryption (SUB):")
    pos = 0
    for cw in cipher_words:
        word_dec = [full_dec_sub[pos + j] for j in range(len(cw))]
        word_text = ''.join(LATIN[v] for v in word_dec)
        print(f"  {word_text}", end=' ')
        pos += len(cw)
        if pos > 200:
            print("...")
            break
    print()

# === Check F-skip variant ===
print()
print("="*70)
print("METHOD 7: F-skip key derivation (skip key advance when plain=F=0)")
print("="*70)

# In F-skip mode, the key index only advances when the plaintext is NOT F (value 0)
# This changes alignment
# Try: plain = (cipher + key[k]) % 29, advance k only if plain != 0
# But we need to know plain to know when to skip... chicken-and-egg

# Instead, try OLD key with F-skip on new text
key_idx = 0
decrypted_fskip = []
for i in range(len(cipher)):
    p = (cipher[i] + OLD_KEY[key_idx % 47]) % 29
    decrypted_fskip.append(p)
    if p != 0:  # F = 0, skip key advance for F
        key_idx += 1

dec_text_fskip = ''.join(LATIN[v] for v in decrypted_fskip)
print(f"F-skip ADD (old key): {dec_text_fskip[:100]}...")

# Also try SUB with F-skip
key_idx = 0
decrypted_fskip_sub = []
for i in range(len(cipher)):
    p = (cipher[i] - OLD_KEY[key_idx % 47]) % 29
    decrypted_fskip_sub.append(p)
    if p != 0:
        key_idx += 1

dec_text_fskip_sub = ''.join(LATIN[v] for v in decrypted_fskip_sub)
print(f"F-skip SUB (old key): {dec_text_fskip_sub[:100]}...")

# === Comparison with old 255-rune analysis ===
print()
print("="*70)
print("COMPARISON: Where are the J runes in P19?")
print("="*70)

j_positions = []
for i, c in enumerate(raw_text):
    if c == '\u16C4':  # J variant
        j_positions.append(i)
    elif c == '\u16C2':
        j_positions.append(i)

# Count J runes in context
rune_idx = 0
j_rune_positions = []
for c in raw_text:
    if c in GP:
        if c in ['\u16C4', '\u16C2']:
            j_rune_positions.append(rune_idx)
        rune_idx += 1

print(f"J runes found at cipher positions: {j_rune_positions}")
print(f"Total J runes: {len(j_rune_positions)}")
print(f"Without J: {len(cipher) - len(j_rune_positions)} runes")
print()

# Show how the old key alignment shifts due to J insertions
print("Old 255-rune text was MISSING these J runes.")
print("This means every position AFTER the first J at position", 
      j_rune_positions[0] if j_rune_positions else "?",
      "was shifted in the old analysis.")
print()
print("To recover old behavior: remove J runes from cipher, apply key")
cipher_no_j = [v for i, v in enumerate(cipher) if i not in j_rune_positions]
print(f"Cipher without J: {len(cipher_no_j)} runes")
if len(cipher_no_j) == 255:
    # This should match what the old key produced
    dec_old = [(cipher_no_j[i] + OLD_KEY[i % 47]) % 29 for i in range(len(cipher_no_j))]
    dec_old_text = ''.join(LATIN[v] for v in dec_old)
    print(f"Decrypted (old key, no-J cipher, ADD): {dec_old_text[:100]}...")
    
    dec_old_sub = [(cipher_no_j[i] - OLD_KEY[i % 47]) % 29 for i in range(len(cipher_no_j))]
    dec_old_text_sub = ''.join(LATIN[v] for v in dec_old_sub)
    print(f"Decrypted (old key, no-J cipher, SUB): {dec_old_text_sub[:100]}...")
