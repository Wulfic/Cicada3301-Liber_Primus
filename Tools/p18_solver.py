"""
P18 DEDICATED SOLVER
Key length 53 confirmed (IoC*29 = 1.860, far above any other length).
Now: find the actual key using proper frequency analysis + English validation.
"""
import os
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    path = f'LiberPrimus/pages/page_{pg:02d}/runes.txt'
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    words = []
    current = []
    start = 0
    pos = 0
    for c in raw:
        if c in GP:
            if not current:
                start = pos
            current.append(GP[c])
            pos += 1
        elif current:
            words.append((start, current))
            current = []
    if current:
        words.append((start, current))
    return runes, words, raw

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1))

cipher, words, raw = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

# === REFERENCE FREQUENCY from solved pages ===
# Load solved pages to get English GP frequency distribution
solved_pages = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74]
all_solved_runes = []
for pg in solved_pages:
    path = f'LiberPrimus/pages/page_{pg:02d}/runes.txt'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        runes = [GP[c] for c in text if c in GP]
        all_solved_runes.extend(runes)

# These are CIPHER runes from solved pages. We need PLAINTEXT runes.
# Actually, the solved pages' rune files contain ciphertext... we need the decrypted plaintext
# Let me check if there are plaintext files

# Actually, let's derive the reference distribution differently.
# For English text encoded in GP:
# Letter frequencies: E=12.7%, T=9.1%, A=8.2%, O=7.5%, I=7.0%, N=6.7%, S=6.3%, H=6.1%, R=6.0% ...
# GP encoding: Digraphs TH=2, NG=21, EO=12, OE=22, EA=28, AE=25, IA=27
# But in GP, the digraphs TH and NG absorb letter pairs, changing frequencies significantly.

# Let me use a simpler approach: chi-squared against each possible shift
# For each column, try all 29 shifts and pick the one that gives highest IoC
# (since the correct shift will make the column look like English GP)

# Better approach: use KNOWN SOLUTION to get reference distribution
# P55/73 was solved. Let me use its decrypted text...
# Actually, let me just use the mutual IoC method between columns

KLEN = 53

# Split cipher into columns
columns = [[] for _ in range(KLEN)]
for i in range(N):
    columns[i % KLEN].append(cipher[i])

# Method 1: Mutual Information / Kasiski
# For each pair of columns, find the relative shift that maximizes mutual IoC
print("\n=== Column IoC analysis ===")
for i in range(min(10, KLEN)):
    print(f"  Col {i}: {len(columns[i])} runes, IoC*29={ioc(columns[i])*29:.3f}")

# Method 2: Try ALL possible keys for each column
# Use a scoring function that measures English-likeness

# Reference: from the decrypted P55/73 and other solved pages
# Let me construct an expected frequency from the GP letter mapping
# English letter freqs (simplified):
eng_letter_freq = {
    'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070, 'N': 0.067,
    'S': 0.063, 'H': 0.061, 'R': 0.060, 'D': 0.043, 'L': 0.040, 'C': 0.028,
    'U': 0.028, 'M': 0.024, 'W': 0.024, 'F': 0.022, 'G': 0.020, 'Y': 0.020,
    'P': 0.019, 'B': 0.015, 'V': 0.010, 'K': 0.008, 'J': 0.002, 'X': 0.002,
    'Q': 0.001, 'Z': 0.001
}

# Map to GP indices (approximate, ignoring digraphs for now):
# F=0, U=1, TH=2, O=3, R=4, C=5, G=6, W=7, H=8, N=9, I=10, J=11,
# EO=12, P=13, X=14, S=15, T=16, B=17, E=18, M=19, L=20, NG=21, OE=22,
# D=23, A=24, AE=25, Y=26, IA=27, EA=28

# Approximate GP frequency (monographic, from English, roughly):
# This is inexact because digraphs change things, but good enough for shift detection
gp_freq = [0.0] * 29
gp_freq[0] = 0.022  # F
gp_freq[1] = 0.028  # U (+ V mapped to U)
gp_freq[2] = 0.035  # TH (very common digraph)
gp_freq[3] = 0.075  # O
gp_freq[4] = 0.060  # R
gp_freq[5] = 0.036  # C (+ K mapped to C)
gp_freq[6] = 0.020  # G
gp_freq[7] = 0.024  # W
gp_freq[8] = 0.061  # H
gp_freq[9] = 0.067  # N
gp_freq[10] = 0.070  # I
gp_freq[11] = 0.002  # J
gp_freq[12] = 0.005  # EO (rare digraph)
gp_freq[13] = 0.019  # P
gp_freq[14] = 0.002  # X
gp_freq[15] = 0.063  # S
gp_freq[16] = 0.091  # T
gp_freq[17] = 0.015  # B
gp_freq[18] = 0.127  # E
gp_freq[19] = 0.024  # M
gp_freq[20] = 0.040  # L
gp_freq[21] = 0.015  # NG (digraph)
gp_freq[22] = 0.003  # OE (rare digraph)
gp_freq[23] = 0.043  # D
gp_freq[24] = 0.082  # A
gp_freq[25] = 0.003  # AE (rare digraph)
gp_freq[26] = 0.020  # Y
gp_freq[27] = 0.003  # IA (rare digraph)
gp_freq[28] = 0.003  # EA (rare digraph)

# Normalize
total = sum(gp_freq)
gp_freq = [f/total for f in gp_freq]

def chi_squared(observed_counts, n, expected_freq):
    """Chi-squared statistic (lower = better fit)"""
    score = 0
    for i in range(29):
        expected = n * expected_freq[i]
        if expected > 0:
            score += (observed_counts.get(i, 0) - expected) ** 2 / expected
    return score

def correlation_score(observed_counts, n, expected_freq):
    """Correlation between observed and expected (higher = better)"""
    if n == 0: return 0
    obs_freq = [observed_counts.get(i, 0) / n for i in range(29)]
    # Dot product
    return sum(obs_freq[i] * expected_freq[i] for i in range(29))

# === Find best key for each column using EACH method ===
print("\n=== Finding key for each column ===")

for mode_name, decrypt_fn in [
    ("SUB (cipher - key)", lambda c, k: (c - k) % 29),
    ("ADD (cipher + key)", lambda c, k: (c + k) % 29),
    ("BEAUFORT (key - cipher)", lambda c, k: (k - c) % 29),
]:
    print(f"\n--- Mode: {mode_name} ---")
    
    key = []
    for col_idx in range(KLEN):
        col = columns[col_idx]
        n = len(col)
        
        best_shift = 0
        best_score = -999
        
        for shift in range(29):
            dec = [decrypt_fn(v, shift) for v in col]
            counts = Counter(dec)
            score = correlation_score(counts, n, gp_freq)
            if score > best_score:
                best_score = score
                best_shift = shift
        
        key.append(best_shift)
    
    # Decrypt full text with this key
    decrypted = [decrypt_fn(cipher[i], key[i % KLEN]) for i in range(N)]
    full_ic = ioc(decrypted) * 29
    
    # Build words
    dec_words = []
    for start, word in words:
        wd = [decrypted[start + j] for j in range(len(word))]
        dec_words.append(''.join(LAT[v] for v in wd))
    
    text = ''.join(LAT[v] for v in decrypted)
    
    print(f"Key: {key}")
    print(f"IoC*29: {full_ic:.3f}")
    print(f"Text: {text[:200]}")
    print(f"Words: {' '.join(dec_words[:30])}")
    
    # Count recognizable English words
    common_words = {'THE','AND','OF','TO','IN','IS','IT','THAT','WAS','FOR','ON','ARE','WITH',
                    'AS','AT','BE','THIS','FROM','OR','AN','BY','NOT','BUT','WHAT','ALL','A','I',
                    'HE','SHE','THEY','WE','YOU','HIS','HER','ITS','OUR','THEIR','WHO','WHICH',
                    'HAS','HAD','HAVE','BEEN','ONE','EACH','LIKE','DO','SO','IF','NO','MY','UP',
                    'ABOUT','OUT','THEM','THEN','INTO','SOME','THAN','OVER','SUCH','ALSO','COME',
                    'TIME','VERY','YOUR','EACH','MAKE','HOW','THERE','WHEN','COULD','THESE',
                    'WOULD','OTHER','MORE','AFTER','MANY','WILL','SHALL','WITHIN','DEEP','WEB',
                    'THROUGH','BETWEEN','KNOW','WISDOM','TRUTH','BEING','MIND','SELF','REMEMBER',
                    'CONSCIOUSNESS','ILLUSION','REALITY','EXISTENCE','DARKNESS','LIGHT','YET',
                    'NOW','HERE','ONLY','SEEK','FIND','SEE','CONSUME','DATA','LIFE','DEATH',
                    'POWER','ORDER','CHAOS','PRIME','PRIMES','NUMBER','NUMBERS','PATH'}
    
    word_hits = sum(1 for w in dec_words if w.upper() in common_words)
    print(f"English word hits: {word_hits}/{len(dec_words)}")

# === Now try with F-skip rule ===
print("\n" + "="*80)
print("F-SKIP VIGENERE on P18 with key length 53")
print("="*80)

for mode_name, decrypt_fn in [
    ("SUB", lambda c, k: (c - k) % 29),
    ("ADD", lambda c, k: (c + k) % 29),
    ("BEAUFORT", lambda c, k: (k - c) % 29),
]:
    # First pass: try each column independently (ignoring F-skip for column assignment)
    # Then: refine with F-skip
    
    # Without F-skip first (already done above), now WITH F-skip:
    # F-skip: when decrypted value = 0 (F), key index doesn't advance
    
    # We need to search the key itself. With F-skip, the column assignment changes
    # depending on the key, so we can't do simple column frequency analysis.
    # Instead, let's use the key found WITHOUT f-skip as a starting point.
    
    # Brute force isn't feasible for 29^53. But we can iterate:
    # 1. Start with non-f-skip key
    # 2. Decrypt with f-skip
    # 3. Re-derive key from the f-skip decryption
    # 4. Repeat until stable
    
    # Actually, for F-skip, let me try the non-f-skip key and just apply f-skip decryption
    key = []
    for col_idx in range(KLEN):
        col = columns[col_idx]
        n = len(col)
        best_shift = 0
        best_score = -999
        for shift in range(29):
            dec = [decrypt_fn(v, shift) for v in col]
            counts = Counter(dec)
            score = correlation_score(counts, n, gp_freq)
            if score > best_score:
                best_score = score
                best_shift = shift
        key.append(best_shift)
    
    # Apply with F-skip
    decrypted_fskip = []
    ki = 0
    for i in range(N):
        dec_val = decrypt_fn(cipher[i], key[ki % KLEN])
        decrypted_fskip.append(dec_val)
        if dec_val != 0:  # F-skip: only advance key when result != F
            ki += 1
    
    full_ic_fskip = ioc(decrypted_fskip) * 29
    
    dec_words_fskip = []
    for start, word in words:
        wd = [decrypted_fskip[start + j] for j in range(len(word))]
        dec_words_fskip.append(''.join(LAT[v] for v in wd))
    
    text_fskip = ''.join(LAT[v] for v in decrypted_fskip)
    
    word_hits_fskip = sum(1 for w in dec_words_fskip if w.upper() in common_words)
    print(f"\n{mode_name} with F-skip: IoC*29={full_ic_fskip:.3f}, word_hits={word_hits_fskip}/{len(dec_words_fskip)}")
    if word_hits_fskip > 2:
        print(f"  Words: {' '.join(dec_words_fskip[:30])}")
        print(f"  Text: {text_fskip[:200]}")

# === Global search: try ALL 29^1 refinements of each key position ===
print("\n" + "="*80)
print("KEY REFINEMENT: hill-climbing on each position")
print("="*80)

for mode_name, decrypt_fn in [
    ("SUB", lambda c, k: (c - k) % 29),
    ("ADD", lambda c, k: (c + k) % 29),  
]:
    # Start with best key from frequency analysis
    key = []
    for col_idx in range(KLEN):
        col = columns[col_idx]
        n = len(col)
        best_shift = 0
        best_score = -999
        for shift in range(29):
            dec = [decrypt_fn(v, shift) for v in col]
            counts = Counter(dec)
            score = correlation_score(counts, n, gp_freq)
            if score > best_score:
                best_score = score
                best_shift = shift
        key.append(best_shift)
    
    # Hill-climb: for each position, try all 29 values and pick the one
    # that maximizes number of recognized words
    improved = True
    iteration = 0
    while improved and iteration < 5:
        improved = False
        iteration += 1
        for pos in range(KLEN):
            best_val = key[pos]
            best_wc = -1
            
            for val in range(29):
                key[pos] = val
                dec = [decrypt_fn(cipher[i], key[i % KLEN]) for i in range(N)]
                
                dw = []
                for start, word in words:
                    wd = [dec[start + j] for j in range(len(word))]
                    dw.append(''.join(LAT[v] for v in wd))
                
                wc = sum(1 for w in dw if w.upper() in common_words)
                if wc > best_wc:
                    best_wc = wc
                    best_val = val
            
            if best_val != key[pos]:
                key[pos] = best_val
                improved = True
            else:
                key[pos] = best_val
    
    dec = [decrypt_fn(cipher[i], key[i % KLEN]) for i in range(N)]
    full_ic = ioc(dec) * 29
    
    dw = []
    for start, word in words:
        wd = [dec[start + j] for j in range(len(word))]
        dw.append(''.join(LAT[v] for v in wd))
    
    wc = sum(1 for w in dw if w.upper() in common_words)
    text = ''.join(LAT[v] for v in dec)
    
    print(f"\n{mode_name} hill-climbed: IoC*29={full_ic:.3f}, word_hits={wc}/{len(dw)}")
    print(f"Key: {key}")
    print(f"Words: {' '.join(dw[:30])}")
    print(f"Text: {text[:200]}")

print("\n=== P18 SOLVER COMPLETE ===")
