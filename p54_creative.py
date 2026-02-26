#!/usr/bin/env python3
"""
P54 Creative Key Derivation Attacks

Approaches:
1. Self-Reliance with GP PRIME values (not indices) as key
2. Self-Reliance with totient-of-GP-prime values as key
3. Ciphertext autokey (cipher feeds back as key - different from plaintext autokey)
4. P53 ciphertext runes as running key for P54
5. Other Emerson essays as running key
6. Mixed GP prime approaches
7. Self-Reliance WORD LENGTHS as key stream
8. Self-Reliance WORD INITIALS as key stream
"""

import sys, os, functools, re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print = functools.partial(print, flush=True)

N = 29
GP_NAMES = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# GP Unicode mapping
GP_UNICODE = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,
    '\u16B7':6,'\u16B9':7,'\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,
    '\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,
    '\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}

DIGRAPHS = {'TH':2, 'NG':21, 'EA':28, 'OE':22, 'AE':25, 'IA':27, 'EO':12}
SINGLES = {'F':0, 'U':1, 'O':3, 'R':4, 'C':5, 'G':6, 'W':7, 'H':8, 'N':9,
           'I':10, 'J':11, 'P':13, 'X':14, 'S':15, 'T':16, 'B':17, 'E':18,
           'M':19, 'L':20, 'D':23, 'A':24, 'Y':26}

def text_to_gp(text):
    text = text.upper()
    vals = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in DIGRAPHS:
                vals.append(DIGRAPHS[di])
                i += 2
                continue
        ch = text[i]
        if ch in SINGLES:
            vals.append(SINGLES[ch])
        i += 1
    return vals

def runes_to_gp(rune_text):
    """Convert rune text to GP values, skipping separators."""
    vals = []
    for ch in rune_text:
        if ch in GP_UNICODE:
            vals.append(GP_UNICODE[ch])
    return vals

def gp_to_text(vals):
    return ''.join(GP_NAMES[v] for v in vals)

# P54 cipher
CIPHER = [21, 25, 19, 10, 7, 15, 17, 14, 19, 15, 12, 6, 23, 2, 25, 0, 27, 24, 17, 5, 1, 7, 4, 17, 28, 0, 14, 10, 19, 1, 5, 13, 8, 21, 20, 12, 19, 15, 23, 27, 13, 0, 17, 8, 12, 5, 12, 18, 28, 18, 10, 6, 14, 6, 15, 18, 15, 12, 2, 2, 18, 15, 2, 22, 5, 28, 10, 19, 5, 14, 23, 11, 1, 17, 18, 10]
WORD_LENS = [1, 4, 2, 2, 6, 6, 2, 1, 12, 6, 4, 2, 7, 7, 2, 4, 2, 3, 3]
F_POSITIONS = [15, 25, 41]

# Load dictionary
print("Loading dictionary...")
with open('wordlist.txt', 'r') as f:
    ALL_WORDS = set(w.strip().upper() for w in f if w.strip())
print(f"  {len(ALL_WORDS)} words loaded")

def extract_words(plaintext_vals, wlens=WORD_LENS):
    words = []
    pos = 0
    for wl in wlens:
        words.append(gp_to_text(plaintext_vals[pos:pos+wl]))
        pos += wl
    return words

def count_matches(words):
    count = 0
    matched = []
    for i, w in enumerate(words):
        if w in ALL_WORDS:
            count += 1
            matched.append(f"W{i}={w}")
    return count, matched

def decrypt(cipher, key_vals, mode):
    plain = []
    for i in range(len(cipher)):
        c = cipher[i]
        k = key_vals[i % len(key_vals)] if isinstance(key_vals, list) and len(key_vals) < len(cipher) else key_vals[i]
        if mode == 'SUB':
            p = (c - k) % N
        elif mode == 'ADD':
            p = (c + k) % N
        elif mode == 'BEAU':
            p = (k - c) % N
        plain.append(p)
    return plain

# Load Self-Reliance
print("Loading Self-Reliance...")
with open('self_reliance.txt', 'r', encoding='utf-8') as f:
    sr_text = f.read()
prose_start = sr_text.find('I read the other day')
sr_gp = text_to_gp(sr_text[prose_start:] if prose_start > 0 else sr_text)
print(f"  SR GP values: {len(sr_gp)}")

# Load P53
print("Loading P53 runes...")
with open(r'LiberPrimus\pages\page_53\runes.txt', 'r', encoding='utf-8') as f:
    p53_runes = f.read()
p53_gp = runes_to_gp(p53_runes)
print(f"  P53 GP values: {len(p53_gp)}")

# Load other Emerson essays from Gutenberg
print("Loading full Emerson text for other essays...")
import urllib.request
gutenberg_cache = 'emerson_essays.txt'
if os.path.exists(gutenberg_cache):
    with open(gutenberg_cache, 'r', encoding='utf-8') as f:
        full_emerson = f.read()
else:
    url = 'https://www.gutenberg.org/cache/epub/16643/pg16643.txt'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        full_emerson = resp.read().decode('utf-8', errors='replace')
    with open(gutenberg_cache, 'w', encoding='utf-8') as f:
        f.write(full_emerson)
print(f"  Full Emerson: {len(full_emerson)} chars")

# Extract individual essays
essays = {}
essay_names = ['THE AMERICAN SCHOLAR', 'COMPENSATION', 'SELF-RELIANCE', 'SELF\nRELIANCE',
               'FRIENDSHIP', 'HEROISM', 'MANNERS', 'GIFTS', 'NATURE', 'SHAKESPEARE',
               'PRUDENCE', 'CIRCLES']
for name in essay_names:
    pos = full_emerson.find(name)
    if pos >= 0:
        # Find next essay
        end = len(full_emerson)
        for other in essay_names:
            if other == name:
                continue
            other_pos = full_emerson.find(other, pos + len(name) + 100)
            if other_pos > pos and other_pos < end:
                end = other_pos
        essays[name.replace('\n', ' ')] = full_emerson[pos:end]

print(f"  Extracted {len(essays)} essays")

outf = open('p54_creative_results.txt', 'w', encoding='utf-8')
best_overall = (0, '', '', [])

def test_key(label, key_vals, cipher=CIPHER, wlens=WORD_LENS, threshold=12):
    """Test a key against the cipher. Returns best match count."""
    global best_overall
    best = 0
    max_off = len(key_vals) - len(cipher)
    if max_off < 0:
        return 0
    
    for offset in range(max_off + 1):
        key_slice = key_vals[offset:offset + len(cipher)]
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt(cipher, key_slice, mode)
            words = extract_words(plain, wlens)
            matches, matched = count_matches(words)
            
            if matches >= threshold:
                text = ' '.join(words)
                line = f"  {label} off={offset} {mode}: {matches}/{len(wlens)}"
                print(line)
                print(f"    Text: {text}")
                print(f"    Matches: {', '.join(matched)}")
                outf.write(f"{line}\n    Text: {text}\n    Matches: {', '.join(matched)}\n")
            
            if matches > best:
                best = matches
            if matches > best_overall[0]:
                best_overall = (matches, label, f"off={offset} {mode}", matched)
    
    return best

# ═══════════════════════════════════════════════════════════════════
# 1. GP PRIME-based key from Self-Reliance
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("1. SELF-RELIANCE WITH GP PRIME VALUES AS KEY")
print("="*80)
outf.write("\n1. SR GP PRIME VALUES\n")

# Convert SR text to GP primes: each GP index → corresponding prime value → mod 29
sr_prime_key = [(GP_PRIMES[v]) % N for v in sr_gp]
print(f"  Key length: {len(sr_prime_key)}")
print(f"  First 20 key values: {sr_prime_key[:20]}")
b = test_key("SR_PRIME", sr_prime_key)
print(f"  BEST: {b}/{len(WORD_LENS)}")

# ═══════════════════════════════════════════════════════════════════
# 2. TOTIENT of GP PRIME values
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("2. SELF-RELIANCE WITH φ(GP_PRIME) AS KEY")
print("="*80)
outf.write("\n2. SR TOTIENT OF GP PRIME\n")

# φ(prime) = prime - 1 for all primes
sr_totient_key = [(GP_PRIMES[v] - 1) % N for v in sr_gp]
print(f"  First 20 key values: {sr_totient_key[:20]}")
b = test_key("SR_TOTIENT", sr_totient_key)
print(f"  BEST: {b}/{len(WORD_LENS)}")

# ═══════════════════════════════════════════════════════════════════
# 3. CIPHERTEXT AUTOKEY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("3. CIPHERTEXT AUTOKEY (cipher as feedback)")
print("="*80)
outf.write("\n3. CIPHERTEXT AUTOKEY\n")

# Autokey where key = primer + ciphertext
# P[i] = (C[i] - key[i]) mod 29
# key[0..k-1] = primer, key[k+i] = C[i]
# Try all short primers (1-4 values) 
for kl in range(1, 5):
    best_ct_ak = 0
    best_ct_result = None
    total = N ** kl
    for primer_int in range(total):
        primer = []
        v = primer_int
        for _ in range(kl):
            primer.append(v % N)
            v //= N
        
        # Build key: primer + ciphertext
        key = primer + list(CIPHER[:len(CIPHER) - kl])
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt(CIPHER, key, mode)
            words = extract_words(plain)
            matches, matched = count_matches(words)
            
            if matches > best_ct_ak:
                best_ct_ak = matches
                best_ct_result = (primer, mode, words, matched)
            
            if matches >= 13:
                text = ' '.join(words)
                print(f"  CT-AK kl={kl} primer={primer} {mode}: {matches}/19")
                print(f"    Text: {text}")
                print(f"    Matches: {', '.join(matched)}")
                outf.write(f"  CT-AK kl={kl} primer={primer} {mode}: {matches}/19\n")
                outf.write(f"    Text: {text}\n    Matches: {', '.join(matched)}\n")
                
                if matches > best_overall[0]:
                    best_overall = (matches, f"CT-AK kl={kl}", f"primer={primer} {mode}", matched)
    
    print(f"  CT-AK kl={kl}: BEST {best_ct_ak}/19")
    if best_ct_result:
        p, m, w, ml = best_ct_result
        print(f"    primer={p} {m}: {' '.join(w)}")
        print(f"    Matches: {', '.join(ml)}")
    outf.write(f"  CT-AK kl={kl}: BEST {best_ct_ak}/19\n")

# ═══════════════════════════════════════════════════════════════════
# 4. P53 CIPHERTEXT AS RUNNING KEY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("4. P53 CIPHERTEXT AS RUNNING KEY FOR P54")
print("="*80)
outf.write("\n4. P53 AS RUNNING KEY\n")

print(f"  P53 has {len(p53_gp)} GP values, P54 needs {len(CIPHER)}")
b = test_key("P53_KEY", p53_gp, threshold=10)
print(f"  BEST: {b}/{len(WORD_LENS)}")

# Also try P53 reversed
b = test_key("P53_REV", list(reversed(p53_gp)), threshold=10)
print(f"  P53_REV BEST: {b}/{len(WORD_LENS)}")

# P53 primes
p53_prime_key = [(GP_PRIMES[v]) % N for v in p53_gp]
b = test_key("P53_PRIME", p53_prime_key, threshold=10)
print(f"  P53_PRIME BEST: {b}/{len(WORD_LENS)}")

# P53 totient
p53_totient_key = [(GP_PRIMES[v] - 1) % N for v in p53_gp]
b = test_key("P53_TOTIENT", p53_totient_key, threshold=10)
print(f"  P53_TOTIENT BEST: {b}/{len(WORD_LENS)}")

# ═══════════════════════════════════════════════════════════════════
# 5. OTHER EMERSON ESSAYS
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("5. OTHER EMERSON ESSAYS AS RUNNING KEY")
print("="*80)
outf.write("\n5. OTHER EMERSON ESSAYS\n")

for ename, etext in essays.items():
    if 'SELF' in ename:
        continue  # Already tested
    egp = text_to_gp(etext)
    if len(egp) < len(CIPHER):
        continue
    b = test_key(f"ESSAY_{ename[:20]}", egp)
    print(f"  {ename[:30]}: {len(egp)} GP vals, BEST {b}/19")
    outf.write(f"  {ename[:30]}: BEST {b}/19\n")

# ═══════════════════════════════════════════════════════════════════
# 6. MULTIPLICATIVE KEY (mod 29)
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("6. MULTIPLICATIVE CIPHER WITH SR KEY")
print("="*80)
outf.write("\n6. MULTIPLICATIVE\n")

# P = C * K^(-1) mod 29 (multiplicative cipher)
# Need multiplicative inverses mod 29
def modinv(a, m=29):
    if a % m == 0:
        return None
    return pow(a, m - 2, m)

best_mult = 0
for offset in range(min(1000, len(sr_gp) - len(CIPHER) + 1)):
    key_slice = sr_gp[offset:offset + len(CIPHER)]
    for mult_mode in ['MULT', 'DIV']:
        plain = []
        valid = True
        for i in range(len(CIPHER)):
            k = key_slice[i]
            c = CIPHER[i]
            if k == 0:
                valid = False
                break
            if mult_mode == 'MULT':
                inv = modinv(k)
                if inv is None:
                    valid = False
                    break
                p = (c * inv) % N
            else:  # DIV
                p = (c * k) % N
            plain.append(p)
        
        if not valid:
            continue
        
        words = extract_words(plain)
        matches, matched = count_matches(words)
        if matches > best_mult:
            best_mult = matches
        if matches >= 12:
            text = ' '.join(words)
            print(f"  MULT off={offset} {mult_mode}: {matches}/19")
            print(f"    Text: {text}")

print(f"  MULT BEST: {best_mult}/19")
outf.write(f"  MULT BEST: {best_mult}/19\n")

# ═══════════════════════════════════════════════════════════════════
# 7. WORD LENGTH KEY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("7. SELF-RELIANCE WORD LENGTHS AS KEY")
print("="*80)
outf.write("\n7. WORD LENGTH KEY\n")

# Extract word lengths from Self-Reliance
sr_prose = sr_text[prose_start:] if prose_start > 0 else sr_text
sr_words_raw = re.findall(r'[a-zA-Z]+', sr_prose)
sr_word_lens = [(len(w)) % N for w in sr_words_raw]
print(f"  SR has {len(sr_words_raw)} words")

# Each cipher rune gets key = length of corresponding SR word
# But SR has many more words than cipher runes... try different mappings

# Method A: One SR word per cipher rune 
for offset in range(min(len(sr_word_lens) - len(CIPHER), 5000)):
    key = sr_word_lens[offset:offset + len(CIPHER)]
    for mode in ['SUB', 'ADD', 'BEAU']:
        plain = decrypt(CIPHER, key, mode)
        words = extract_words(plain)
        matches, matched = count_matches(words)
        if matches >= 12:
            text = ' '.join(words)
            print(f"  WLEN off={offset} {mode}: {matches}/19 → {text}")
            outf.write(f"  WLEN off={offset} {mode}: {matches}/19 → {text}\n")

# Method B: One SR word per P54 word (expand by repeated word length)
for offset in range(min(len(sr_words_raw) - 19, 5000)):
    key = []
    for i, wl in enumerate(WORD_LENS):
        word_idx = offset + i
        if word_idx >= len(sr_words_raw):
            break
        key.extend([len(sr_words_raw[word_idx]) % N] * wl)
    if len(key) < len(CIPHER):
        continue
    key = key[:len(CIPHER)]
    for mode in ['SUB', 'ADD', 'BEAU']:
        plain = decrypt(CIPHER, key, mode)
        words = extract_words(plain)
        matches, matched = count_matches(words)
        if matches >= 12:
            text = ' '.join(words)
            print(f"  WLEN-B off={offset} {mode}: {matches}/19 → {text}")

# ═══════════════════════════════════════════════════════════════════
# 8. WORD INITIAL LETTERS KEY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("8. SELF-RELIANCE WORD INITIALS AS KEY")
print("="*80)
outf.write("\n8. WORD INITIALS KEY\n")

sr_initials_gp = text_to_gp(''.join(w[0] for w in sr_words_raw if w))
print(f"  SR initials GP: {len(sr_initials_gp)} values")
b = test_key("SR_INITIALS", sr_initials_gp)
print(f"  BEST: {b}/19")

# ═══════════════════════════════════════════════════════════════════
# 9. MIXED: SR key XOR'd with position
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("9. POSITION-DEPENDENT KEY (SR + position)")
print("="*80)
outf.write("\n9. POSITION-DEPENDENT\n")

# Key[i] = (SR_GP[i+offset] + i) mod 29
best_pos = 0
for offset in range(min(200, len(sr_gp) - len(CIPHER))):
    key = [(sr_gp[offset + i] + i) % N for i in range(len(CIPHER))]
    for mode in ['SUB', 'ADD', 'BEAU']:
        plain = decrypt(CIPHER, key, mode)
        words = extract_words(plain)
        matches, matched = count_matches(words)
        if matches > best_pos:
            best_pos = matches
        if matches >= 12:
            text = ' '.join(words)
            print(f"  POS off={offset} {mode}: {matches}/19 → {text}")
            outf.write(f"  POS off={offset} {mode}: {matches}/19 → {text}\n")

# Key[i] = (SR_GP[i+offset] * i) mod 29  
for offset in range(min(200, len(sr_gp) - len(CIPHER))):
    key = [(sr_gp[offset + i] * (i+1)) % N for i in range(len(CIPHER))]
    for mode in ['SUB', 'ADD', 'BEAU']:
        plain = decrypt(CIPHER, key, mode)
        words = extract_words(plain)
        matches, matched = count_matches(words)
        if matches > best_pos:
            best_pos = matches
        if matches >= 12:
            text = ' '.join(words)
            print(f"  POS_MULT off={offset} {mode}: {matches}/19 → {text}")

print(f"  POS BEST: {best_pos}/19")
outf.write(f"  POS BEST: {best_pos}/19\n")

# ═══════════════════════════════════════════════════════════════════
# 10. FIBONACCI-INDEXED RUNNING KEY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("10. FIBONACCI-INDEXED KEY FROM SR")
print("="*80)
outf.write("\n10. FIBONACCI-INDEXED\n")

# Generate fibonacci sequence
fib = [0, 1]
while fib[-1] < len(sr_gp) * 2:
    fib.append(fib[-1] + fib[-2])

# Key[i] = SR_GP[fib[i] mod len(sr_gp)]
fib_key = [sr_gp[fib[i] % len(sr_gp)] for i in range(len(CIPHER))]
for mode in ['SUB', 'ADD', 'BEAU']:
    plain = decrypt(CIPHER, fib_key, mode)
    words = extract_words(plain)
    matches, matched = count_matches(words)
    if matches >= 10:
        text = ' '.join(words)
        print(f"  FIB {mode}: {matches}/19 → {text}")

# Key[i] = fib[i] mod 29 (fibonacci values directly as key)
fib_direct_key = [fib[i] % N for i in range(len(CIPHER))]
for mode in ['SUB', 'ADD', 'BEAU']:
    plain = decrypt(CIPHER, fib_direct_key, mode)
    words = extract_words(plain)
    matches, matched = count_matches(words)
    if matches >= 10:
        text = ' '.join(words)
        print(f"  FIB_DIRECT {mode}: {matches}/19 → {text}")

# ═══════════════════════════════════════════════════════════════════
# 11. GP INDEX OF EACH SR LETTER SQUARED
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("11. SR GP INDEX SQUARED AS KEY")
print("="*80)
outf.write("\n11. GP INDEX SQUARED\n")

sr_sq_key = [(v * v) % N for v in sr_gp]
b = test_key("SR_SQUARED", sr_sq_key, threshold=11)
print(f"  BEST: {b}/19")

# Also cubed
sr_cube_key = [(v * v * v) % N for v in sr_gp]
b = test_key("SR_CUBED", sr_cube_key, threshold=11)
print(f"  CUBED BEST: {b}/19")

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("OVERALL SUMMARY")
print("="*80)
print(f"Best: {best_overall[0]}/19 from {best_overall[1]}")
print(f"  {best_overall[2]}")
print(f"  Matches: {', '.join(best_overall[3])}")
outf.write(f"\nBest: {best_overall[0]}/19 from {best_overall[1]}\n  {best_overall[2]}\n")
outf.close()
print("\nResults saved to p54_creative_results.txt")
print("DONE")
