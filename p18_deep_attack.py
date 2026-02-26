#!/usr/bin/env python3
"""
P18 Deep Attack — Exploit periodic IoC peaks and autocorrelation signals.
Also test all pages with elevated periodic IoC using Vigenère key recovery.

Strategy:
  Phase 1: Full periodic IoC + autocorrelation scan (all periods/lags)
  Phase 2: Vigenère frequency analysis key recovery per-column
  Phase 3: Mutual IoC relative key discovery
  Phase 4: Known keyword tests (YAHEOOPYJ, P63 terms, DIVINITY, etc.)
  Phase 5: Autokey with best seeds
  Phase 6: Apply best methods to all pages with IoC peaks (P26, P29, etc.)
  Phase 7: Key chaining test (P18 plaintext → P19 key?)
"""
import os, sys, math
from collections import Counter
from itertools import product

# ─── CORRECT GP MAPPING ───
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11  # ᛄ alias
MOD = 29

GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English letter → GP index (no-digraph convention)
ENG_TO_GP = {
    'A':24, 'B':17, 'C':5, 'D':23, 'E':18, 'F':0, 'G':6, 'H':8,
    'I':10, 'J':11, 'K':5, 'L':20, 'M':19, 'N':9, 'O':3, 'P':13,
    'Q':5, 'R':4, 'S':15, 'T':16, 'U':1, 'V':1, 'W':7, 'X':14,
    'Y':26, 'Z':15
}

# Expected English-GP frequency distribution (no-digraph, normalized to sum=1)
# Based on standard English letter frequencies, V→U, K→C, Q→C, Z→S
ENG_FREQ_26 = {
    'A':8.167, 'B':1.492, 'C':2.782, 'D':4.253, 'E':12.702, 'F':2.228,
    'G':2.015, 'H':6.094, 'I':6.966, 'J':0.153, 'K':0.772, 'L':4.025,
    'M':2.406, 'N':6.749, 'O':7.507, 'P':1.929, 'Q':0.095, 'R':5.987,
    'S':6.327, 'T':9.056, 'U':2.758, 'V':0.978, 'W':2.360, 'X':0.150,
    'Y':1.974, 'Z':0.074
}

# Build GP frequency distribution (no-digraph)
GP_EXPECTED = [0.0] * 29
for letter, freq in ENG_FREQ_26.items():
    gp_idx = ENG_TO_GP[letter]
    GP_EXPECTED[gp_idx] += freq
total = sum(GP_EXPECTED)
GP_EXPECTED = [f/total for f in GP_EXPECTED]

# Also build WITH-DIGRAPH expected distribution
# TH: ~3.56% of bigrams → ~1.52% per position
# NG: ~0.95% per position
# EA: ~0.95% per position
# Others: rare
GP_EXPECTED_DIGRAPH = GP_EXPECTED.copy()
# Reduce T and H, add to TH
GP_EXPECTED_DIGRAPH[16] -= 0.015  # T reduced by TH absorption
GP_EXPECTED_DIGRAPH[8] -= 0.015   # H reduced by TH absorption
GP_EXPECTED_DIGRAPH[2] = 0.015    # TH rune
# Reduce N and G, add to NG
GP_EXPECTED_DIGRAPH[9] -= 0.007
GP_EXPECTED_DIGRAPH[6] -= 0.007
GP_EXPECTED_DIGRAPH[21] = 0.010   # NG rune
# Reduce E and A for EA, AE
GP_EXPECTED_DIGRAPH[18] -= 0.005
GP_EXPECTED_DIGRAPH[24] -= 0.005
GP_EXPECTED_DIGRAPH[28] = 0.006   # EA rune
GP_EXPECTED_DIGRAPH[25] = 0.002   # AE rune
# Normalize
for i in range(29):
    GP_EXPECTED_DIGRAPH[i] = max(0.001, GP_EXPECTED_DIGRAPH[i])
total = sum(GP_EXPECTED_DIGRAPH)
GP_EXPECTED_DIGRAPH = [f/total for f in GP_EXPECTED_DIGRAPH]

# Common English words for scoring
COMMON_WORDS = set(["THE","AND","FOR","ARE","NOT","YOU","ALL","HER","WAS","ONE",
    "OUR","OUT","HAS","HIS","HOW","MAN","NEW","NOW","OLD","SEE","WAY","WHO",
    "DID","GET","HIM","LET","SAY","SHE","TOO","USE","BUT","CAN","HAD","HER",
    "WAS","HIS","ITS","MAY","OUR","SAY","TWO","WILL","EACH","MAKE","LIKE",
    "LONG","LOOK","MANY","SOME","THEM","THAN","BEEN","HAVE","FROM","INTO",
    "WITH","THAT","THIS","WHAT","WHEN","THEY","BEEN","COME","MADE","FIND",
    "MORE","BACK","ONLY","JUST","OVER","SUCH","ALSO","TAKE","THAN","THEM",
    "VERY","AFTER","AGAIN","BEING","GREAT","THEIR","THESE","THOSE","UNDER",
    "ABOUT","COULD","EVERY","FIRST","SHALL","THERE","THINK","THOSE","WHERE",
    "WHICH","WHILE","WORLD","WOULD","AFTER","MIGHT","NEVER","STILL","TRUTH",
    "KNOW","MUST","SELF","SOUL","MIND","LIFE","DEAD","FEAR","FIRE","FORM",
    "GOOD","LORD","KING","WISE","WORD","WORK"])

def load_runes(page_num):
    """Load runes from page file, return GP indices."""
    base = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num}"
    rune_file = os.path.join(base, "runes.txt")
    if not os.path.exists(rune_file):
        return None
    with open(rune_file, 'r', encoding='utf-8') as f:
        text = f.read()
    indices = []
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            indices.append(GP_RUNE_TO_IDX[ch])
    return indices

def ioc(vals):
    """Index of Coincidence, normalized so random=1.0, English~1.73"""
    if len(vals) < 2:
        return 0
    c = Counter(vals)
    n = len(vals)
    ic = sum(v*(v-1) for v in c.values()) / (n*(n-1))
    return ic * MOD  # normalized

def chi_squared(observed_counts, expected_freq, n):
    """Chi-squared against expected frequency distribution."""
    chi2 = 0
    for i in range(MOD):
        expected = expected_freq[i] * n
        obs = observed_counts.get(i, 0)
        if expected > 0:
            chi2 += (obs - expected)**2 / expected
    return chi2

def decrypt_sub(cipher, key):
    """Vigenère SUB: plain = (cipher - key) mod 29"""
    return [(c - key[i % len(key)]) % MOD for i, c in enumerate(cipher)]

def decrypt_add(cipher, key):
    """Vigenère ADD: plain = (cipher + key) mod 29"""
    return [(c + key[i % len(key)]) % MOD for i, c in enumerate(cipher)]

def decrypt_beaufort(cipher, key):
    """Beaufort: plain = (key - cipher) mod 29"""
    return [(key[i % len(key)] - c) % MOD for i, c in enumerate(cipher)]

def to_text(indices):
    """Convert GP indices to text using letter names."""
    return ''.join(GP_LETTERS[i] for i in indices)

def word_score(text):
    """Count common English words in text."""
    score = 0
    text_upper = text.upper()
    for w in COMMON_WORDS:
        count = 0
        start = 0
        while True:
            pos = text_upper.find(w, start)
            if pos == -1:
                break
            count += 1
            start = pos + 1
        score += count * len(w)
    return score

def autokey_decrypt_sub(cipher, seed_key):
    """Autokey SUB: key extends with plaintext."""
    plain = []
    for i, c in enumerate(cipher):
        if i < len(seed_key):
            k = seed_key[i]
        else:
            k = plain[i - len(seed_key)]
        plain.append((c - k) % MOD)
    return plain

def autokey_decrypt_add(cipher, seed_key):
    """Autokey ADD: key extends with plaintext."""
    plain = []
    for i, c in enumerate(cipher):
        if i < len(seed_key):
            k = seed_key[i]
        else:
            k = plain[i - len(seed_key)]
        plain.append((c + k) % MOD)
    return plain

# ═══════════════════════════════════════════════════════════════════════
print("="*80)
print("P18 DEEP ATTACK")
print("="*80)

p18 = load_runes(18)
print(f"P18: {len(p18)} runes")

# ─── PHASE 1: Full periodic IoC scan ───
print("\n" + "="*80)
print("PHASE 1: Full periodic IoC scan (periods 2-130)")
print("="*80)

period_iocs = []
for k in range(2, min(131, len(p18)//2)):
    columns = [[] for _ in range(k)]
    for i, v in enumerate(p18):
        columns[i % k].append(v)
    col_iocs = [ioc(col) for col in columns if len(col) >= 2]
    avg_ioc = sum(col_iocs) / len(col_iocs) if col_iocs else 0
    period_iocs.append((k, avg_ioc))

period_iocs.sort(key=lambda x: -x[1])
print("\nTop 20 periods by column IoC:")
for k, ic in period_iocs[:20]:
    n_per_col = len(p18) // k
    print(f"  k={k:3d}  IoC={ic:.3f}  (runes/col={n_per_col})")

# Check if multiples of the best period are also elevated
best_k = period_iocs[0][0]
print(f"\nBest period: k={best_k}")
print(f"Checking multiples and divisors of {best_k}:")
for k, ic in sorted(period_iocs, key=lambda x: x[0]):
    if k % best_k == 0 or best_k % k == 0 or k == best_k:
        print(f"  k={k:3d}  IoC={ic:.3f}")

# ─── PHASE 2: Full autocorrelation scan ───
print("\n" + "="*80)
print("PHASE 2: Full autocorrelation scan (lags 1-130)")
print("="*80)

auto_results = []
for lag in range(1, min(131, len(p18))):
    matches = sum(1 for i in range(len(p18)-lag) if p18[i] == p18[i+lag])
    n_pairs = len(p18) - lag
    expected = n_pairs / MOD
    ratio = matches / expected if expected > 0 else 0
    auto_results.append((lag, ratio, matches, expected))

auto_results.sort(key=lambda x: -x[1])
print("\nTop 20 autocorrelation peaks:")
for lag, ratio, matches, exp in auto_results[:20]:
    print(f"  lag={lag:3d}  ratio={ratio:.3f}  matches={matches}/{int(exp):.0f}expected")

# Check if best period shows in autocorrelation pattern
print(f"\nAutocorrelation at multiples of k={best_k}:")
for mult in range(1, 7):
    lag = best_k * mult
    if lag < len(p18):
        for l, r, m, e in auto_results:
            if l == lag:
                print(f"  lag={lag} (={best_k}×{mult})  ratio={r:.3f}  matches={m}")
                break

# ─── PHASE 3: Vigenère frequency analysis key recovery ───
print("\n" + "="*80)
print("PHASE 3: Vigenère frequency analysis key recovery")
print("="*80)

def freq_analysis_attack(cipher, period, expected_freq, mode_name, decrypt_fn):
    """
    For given period, find best key via column-by-column frequency analysis.
    """
    n = len(cipher)
    columns = [[] for _ in range(period)]
    # Track original positions for each column
    for i, v in enumerate(cipher):
        columns[i % period].append(v)
    
    best_key = []
    col_details = []
    
    for col_idx in range(period):
        col = columns[col_idx]
        best_shift = 0
        best_chi2 = float('inf')
        shift_scores = []
        
        for shift in range(MOD):
            # Apply shift to column
            if mode_name == "SUB":
                shifted = [(v - shift) % MOD for v in col]
            elif mode_name == "ADD":
                shifted = [(v + shift) % MOD for v in col]
            else:  # BEAUFORT
                shifted = [(shift - v) % MOD for v in col]
            
            counts = Counter(shifted)
            chi2 = chi_squared(counts, expected_freq, len(col))
            shift_scores.append((chi2, shift))
            
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift
        
        shift_scores.sort()
        best_key.append(best_shift)
        # Save top 3 candidates per column
        col_details.append(shift_scores[:3])
    
    # Decrypt with recovered key
    if mode_name == "SUB":
        plaintext = decrypt_sub(cipher, best_key)
    elif mode_name == "ADD":
        plaintext = decrypt_add(cipher, best_key)
    else:
        plaintext = decrypt_beaufort(cipher, best_key)
    
    text = to_text(plaintext)
    ic = ioc(plaintext)
    ws = word_score(text)
    
    return best_key, plaintext, text, ic, ws, col_details

# Test top 10 periods
test_periods = [k for k, _ in period_iocs[:10]]
# Also add specific periods of interest
for extra in [9, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
    if extra not in test_periods and extra < len(p18)//2:
        test_periods.append(extra)

print(f"\nTesting periods: {sorted(test_periods)}")

best_overall = []

for period in sorted(test_periods):
    for mode_name in ["SUB", "ADD", "BEAUFORT"]:
        for freq_name, freq in [("nodigraph", GP_EXPECTED), ("digraph", GP_EXPECTED_DIGRAPH)]:
            decrypt_fn = {"SUB": decrypt_sub, "ADD": decrypt_add, "BEAUFORT": decrypt_beaufort}[mode_name]
            key, plain, text, ic, ws, details = freq_analysis_attack(
                p18, period, freq, mode_name, decrypt_fn)
            
            if ic > 1.25 or ws > 30:
                best_overall.append((ic, ws, period, mode_name, freq_name, key, text[:80]))
                if ic > 1.35:
                    print(f"\n  *** k={period} {mode_name} {freq_name}: IoC={ic:.3f} wscore={ws}")
                    print(f"      Key: {key}")
                    print(f"      Text: {text[:100]}")

# ─── PHASE 3b: Mutual IoC relative key recovery ───
print("\n" + "="*80)
print("PHASE 3b: Mutual IoC relative key recovery")
print("="*80)

def mutual_ioc_attack(cipher, period):
    """Determine relative key using mutual IoC between columns."""
    n = len(cipher)
    columns = [[] for _ in range(period)]
    for i, v in enumerate(cipher):
        columns[i % period].append(v)
    
    # For each pair of adjacent columns, find best relative shift
    relative_shifts = [0]  # Column 0 shift = 0 (arbitrary)
    
    for j in range(1, period):
        best_shift = 0
        best_mic = 0
        col0 = columns[0]
        colj = columns[j]
        
        for s in range(MOD):
            # Compute mutual IoC between col0 and colj shifted by s
            c0 = Counter(col0)
            cj = Counter((v + s) % MOD for v in colj)
            mic = sum(c0.get(r, 0) * cj.get(r, 0) for r in range(MOD))
            mic /= (len(col0) * len(colj))
            
            if mic > best_mic:
                best_mic = mic
                best_shift = s
        
        relative_shifts.append(best_shift)
    
    # Now try all 29 absolute shifts for column 0
    best_results = []
    for abs_shift in range(MOD):
        key = [(abs_shift + rs) % MOD for rs in relative_shifts]
        
        for mode_name, decrypt_fn in [("SUB", decrypt_sub), ("ADD", decrypt_add), ("BEAUFORT", decrypt_beaufort)]:
            plain = decrypt_fn(cipher, key)
            text = to_text(plain)
            ic = ioc(plain)
            ws = word_score(text)
            best_results.append((ic, ws, mode_name, key, text[:80]))
    
    best_results.sort(key=lambda x: (-x[0], -x[1]))
    return best_results[:5]

for period in [period_iocs[0][0], period_iocs[1][0], period_iocs[2][0]]:
    if period > 50:
        continue
    print(f"\n  Period k={period}:")
    results = mutual_ioc_attack(p18, period)
    for ic, ws, mode, key, text in results:
        if ic > 1.2 or ws > 20:
            print(f"    {mode}: IoC={ic:.3f} wscore={ws}")
            print(f"    Key: {key}")
            print(f"    Text: {text}")

# ─── PHASE 4: Known keyword tests ───
print("\n" + "="*80)
print("PHASE 4: Known keyword tests")
print("="*80)

# YAHEOOPYJ from P17
YAHEOOPYJ = [26, 24, 8, 18, 3, 3, 13, 26, 11]  # Y,A,H,E,O,O,P,Y,J

# P63 grid terms
VOID = [1, 3, 10, 23]  # U(V),O,I,D
AETHEREAL = [24,18,16,8,18,4,18,24,20]  # A,E,T,H,E,R,E,A,L
CARNAL = [5,24,4,9,24,20]  # C,A,R,N,A,L
ANALOG = [24,9,24,20,3,6]  # A,N,A,L,O,G
MOURNFUL = [19,3,1,4,9,0,1,20]  # M,O,U,R,N,F,U,L
SUOID = [15,1,3,10,23]  # S,U,O,I,D
MOBIUS = [19,3,17,10,1,15]  # M,O,B,I,U,S
OBSCURA = [3,17,15,5,1,4,24]  # O,B,S,C,U,R,A
CABAL = [5,24,17,24,20]  # C,A,B,A,L
DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]

# P19 key (first 47 values)
P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 
           27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 
           5, 22, 18, 4, 5, 18, 23, 21, 1, 10, 24]

keywords = {
    "YAHEOOPYJ": YAHEOOPYJ,
    "YAHEOOPYJ×2": YAHEOOPYJ + YAHEOOPYJ,
    "VOID": VOID,
    "AETHEREAL": AETHEREAL,
    "CARNAL": CARNAL,
    "ANALOG": ANALOG,
    "MOURNFUL": MOURNFUL,
    "SUOID": SUOID,
    "MOBIUS": MOBIUS,
    "OBSCURA": OBSCURA,
    "CABAL": CABAL,
    "DIVINITY": DIVINITY,
    "P19_KEY": P19_KEY,
    "VOIDCARNAL": VOID+CARNAL,
    "AETHEREALVOID": AETHEREAL+VOID,
    "AETHEREALCABAL": AETHEREAL+CABAL,
}

# Also test shifted YAHEOOPYJ
for shift_val in range(1, 29):
    shifted = [(v + shift_val) % MOD for v in YAHEOOPYJ]
    keywords[f"YAHEOOPYJ+{shift_val}"] = shifted

best_keyword_results = []
for name, key in keywords.items():
    for mode_name, decrypt_fn in [("SUB", decrypt_sub), ("ADD", decrypt_add), ("BEAUFORT", decrypt_beaufort)]:
        plain = decrypt_fn(p18, key)
        text = to_text(plain)
        ic = ioc(plain)
        ws = word_score(text)
        
        if ic > 1.20 or ws > 25:
            best_keyword_results.append((ic, ws, name, mode_name, text[:80]))
            if ic > 1.3 or ws > 35:
                print(f"  *** {name} {mode_name}: IoC={ic:.3f} wscore={ws}")
                print(f"      Text: {text[:100]}")

best_keyword_results.sort(key=lambda x: (-x[0], -x[1]))
print(f"\nTop 10 keyword results:")
for ic, ws, name, mode, text in best_keyword_results[:10]:
    print(f"  {name} {mode}: IoC={ic:.3f} wscore={ws}  Text={text[:60]}")

# ─── PHASE 5: Autokey with best seeds ───
print("\n" + "="*80)
print("PHASE 5: Autokey cipher tests")
print("="*80)

autokey_seeds = {
    "YAHEOOPYJ": YAHEOOPYJ,
    "DIVINITY": DIVINITY,
    "VOID": VOID,
    "AETHEREAL": AETHEREAL,
}

best_autokey = []
for name, seed in autokey_seeds.items():
    for mode_name, ak_fn in [("AK_SUB", autokey_decrypt_sub), ("AK_ADD", autokey_decrypt_add)]:
        plain = ak_fn(p18, seed)
        text = to_text(plain)
        ic = ioc(plain)
        ws = word_score(text)
        best_autokey.append((ic, ws, name, mode_name, text[:60]))
        if ic > 1.3 or ws > 30:
            print(f"  *** {name} {mode_name}: IoC={ic:.3f} wscore={ws}")
            print(f"      Text: {text[:100]}")

# Also try autokey with ciphertext feedback (cipher autokey)
for name, seed in list(autokey_seeds.items())[:4]:
    for mode_name in ["CAK_SUB", "CAK_ADD"]:
        plain = []
        for i, c in enumerate(p18):
            if i < len(seed):
                k = seed[i]
            else:
                k = p18[i - len(seed)]  # Use ciphertext as key
            if mode_name == "CAK_SUB":
                plain.append((c - k) % MOD)
            else:
                plain.append((c + k) % MOD)
        text = to_text(plain)
        ic = ioc(plain)
        ws = word_score(text)
        best_autokey.append((ic, ws, name, mode_name, text[:60]))

best_autokey.sort(key=lambda x: (-x[0], -x[1]))
print(f"\nTop 5 autokey results:")
for ic, ws, name, mode, text in best_autokey[:5]:
    print(f"  {name} {mode}: IoC={ic:.3f} wscore={ws}  Text={text}")

# ─── PHASE 6: Brute force small periods (k=2,3,4,5) ───
print("\n" + "="*80)
print("PHASE 6: Exhaustive brute force for small periods")
print("="*80)

for k in [2, 3, 4, 5]:
    print(f"\n  Period k={k}: testing {29**k} keys...")
    best_for_k = []
    
    for key_tuple in product(range(MOD), repeat=k):
        key = list(key_tuple)
        for mode_name, decrypt_fn in [("SUB", decrypt_sub), ("ADD", decrypt_add)]:
            plain = decrypt_fn(p18, key)
            ic = ioc(plain)
            if ic > 1.40:  # Only compute text for high IoC
                text = to_text(plain)
                ws = word_score(text)
                if ws > 40 or ic > 1.55:
                    best_for_k.append((ic, ws, key, mode_name, text[:80]))
    
    best_for_k.sort(key=lambda x: (-x[0], -x[1]))
    if best_for_k:
        print(f"  Found {len(best_for_k)} candidates with IoC>1.4")
        for ic, ws, key, mode, text in best_for_k[:3]:
            print(f"    k={key} {mode}: IoC={ic:.3f} wscore={ws}  Text={text[:60]}")
    else:
        print(f"  No candidates with IoC>1.4")

# ─── PHASE 7: Column-by-column with top-N candidates (for k=20) ───
print("\n" + "="*80)
print("PHASE 7: Column-by-column beam search (k=20)")
print("="*80)

def beam_search_attack(cipher, period, beam_width=5):
    """Column-by-column attack with beam search."""
    n = len(cipher)
    columns = [[] for _ in range(period)]
    col_positions = [[] for _ in range(period)]
    for i, v in enumerate(cipher):
        columns[i % period].append(v)
        col_positions[i % period].append(i)
    
    # For each column, rank all 29 shifts by chi-squared
    col_rankings = []
    for col_idx in range(period):
        col = columns[col_idx]
        shifts = []
        for shift in range(MOD):
            shifted = [(v - shift) % MOD for v in col]  # SUB mode
            counts = Counter(shifted)
            chi2 = chi_squared(counts, GP_EXPECTED, len(col))
            shifts.append((chi2, shift))
        shifts.sort()
        col_rankings.append(shifts)
    
    # Beam search: keep top beam_width candidates at each column
    for freq_name, freq in [("nodigraph", GP_EXPECTED), ("digraph", GP_EXPECTED_DIGRAPH)]:
        for mode_name in ["SUB", "ADD", "BEAUFORT"]:
            # Re-rank with this frequency
            col_rankings = []
            for col_idx in range(period):
                col = columns[col_idx]
                shifts = []
                for shift in range(MOD):
                    if mode_name == "SUB":
                        shifted = [(v - shift) % MOD for v in col]
                    elif mode_name == "ADD":
                        shifted = [(v + shift) % MOD for v in col]
                    else:
                        shifted = [(shift - v) % MOD for v in col]
                    counts = Counter(shifted)
                    chi2 = chi_squared(counts, freq, len(col))
                    shifts.append((chi2, shift))
                shifts.sort()
                col_rankings.append(shifts)
            
            # Take top candidate per column (greedy)
            key = [col_rankings[i][0][1] for i in range(period)]
            
            if mode_name == "SUB":
                plain = decrypt_sub(cipher, key)
            elif mode_name == "ADD":
                plain = decrypt_add(cipher, key)
            else:
                plain = decrypt_beaufort(cipher, key)
            
            text = to_text(plain)
            ic = ioc(plain)
            ws = word_score(text)
            
            if ic > 1.25 or ws > 30:
                print(f"\n  Beam k={period} {mode_name} {freq_name}: IoC={ic:.3f} wscore={ws}")
                print(f"  Key: {key}")
                print(f"  Text: {text[:120]}")
            
            # Also try top-2 per column (2^20 = 1M, manageable)
            # Actually 2^20 = 1,048,576 — let's use top 2 for first 10 columns, top 1 for rest
            from itertools import product as iprod
            if period <= 20:
                # Try top 3 for each column independently (3*20*29 = near nothing)
                for col_idx in range(period):
                    for rank in range(min(3, MOD)):
                        test_key = key.copy()
                        test_key[col_idx] = col_rankings[col_idx][rank][1]
                        if mode_name == "SUB":
                            p = decrypt_sub(cipher, test_key)
                        elif mode_name == "ADD":
                            p = decrypt_add(cipher, test_key)
                        else:
                            p = decrypt_beaufort(cipher, test_key)
                        t = to_text(p)
                        ic2 = ioc(p)
                        ws2 = word_score(t)
                        if (ic2 > ic + 0.1 or ws2 > ws + 20):
                            print(f"    Improved col {col_idx} rank {rank}: IoC={ic2:.3f} wscore={ws2}")
                            print(f"    Text: {t[:100]}")

beam_search_attack(p18, best_k)

# ─── PHASE 8: Test across ALL pages with elevated IoC ───
print("\n" + "="*80)
print("PHASE 8: Frequency analysis across all elevated-IoC pages")
print("="*80)

target_pages = [
    (18, 20), (26, 17), (29, 24), (30, 17), (35, 26),
    (23, 31), (22, 11), (36, 18), (51, 14), (52, 15),
    (21, 61),  # From autocorrelation
]

for page_num, period in target_pages:
    if page_num == 18:
        continue  # Already done
    cipher = load_runes(page_num)
    if cipher is None:
        continue
    
    for mode_name in ["SUB", "ADD", "BEAUFORT"]:
        for freq_name, freq in [("nodigraph", GP_EXPECTED)]:
            decrypt_fn = {"SUB": decrypt_sub, "ADD": decrypt_add, "BEAUFORT": decrypt_beaufort}[mode_name]
            key, plain, text, ic, ws, details = freq_analysis_attack(
                cipher, period, freq, mode_name, decrypt_fn)
            
            if ic > 1.30 or ws > 40:
                print(f"\n  *** P{page_num} k={period} {mode_name}: IoC={ic:.3f} wscore={ws}")
                print(f"      Key: {key}")
                print(f"      Text: {text[:100]}")

# ─── PHASE 9: Investigate autocorrelation structure ───
print("\n" + "="*80)
print("PHASE 9: P18 structural analysis (lag patterns)")
print("="*80)

# Check if P18 at positions 0-86 matches 86+:174
seg1 = p18[0:86]
seg2 = p18[86:172]
seg3 = p18[172:258]

matches_12 = sum(1 for a, b in zip(seg1, seg2) if a == b)
matches_23 = sum(1 for a, b in zip(seg2, seg3) if a == b)
matches_13 = sum(1 for a, b in zip(seg1, seg3) if a == b)
print(f"  Segment matches at period 86:")
print(f"    seg[0:86] vs seg[86:172]: {matches_12}/86 = {matches_12/86:.1%}")
print(f"    seg[86:172] vs seg[172:258]: {matches_23}/86 = {matches_23/86:.1%}")
print(f"    seg[0:86] vs seg[172:258]: {matches_13}/86 = {matches_13/86:.1%}")
print(f"    Expected random: {86/29:.1f}/86 = {1/29:.1%}")

# Check period 60
seg1_60 = p18[0:60]
seg2_60 = p18[60:120]
seg3_60 = p18[120:180]
seg4_60 = p18[180:240]
m12 = sum(1 for a, b in zip(seg1_60, seg2_60) if a == b)
m23 = sum(1 for a, b in zip(seg2_60, seg3_60) if a == b)
m34 = sum(1 for a, b in zip(seg3_60, seg4_60) if a == b)
m13 = sum(1 for a, b in zip(seg1_60, seg3_60) if a == b)
print(f"\n  Segment matches at period 60:")
print(f"    seg[0:60] vs seg[60:120]: {m12}/60")
print(f"    seg[60:120] vs seg[120:180]: {m23}/60")
print(f"    seg[120:180] vs seg[180:240]: {m34}/60")
print(f"    seg[0:60] vs seg[120:180]: {m13}/60")
print(f"    Expected random: {60/29:.1f}/60")

# Check if the autocorrelation pattern reveals a running key with repeated text
# Compute position-specific match rates
print(f"\n  Detailed lag analysis (matches at each position):")
for lag in [20, 40, 60, 80, 86]:
    matches = sum(1 for i in range(len(p18)-lag) if p18[i] == p18[i+lag])
    expected = (len(p18)-lag) / MOD
    print(f"    lag={lag}: {matches} matches / {expected:.1f} expected = {matches/expected:.3f}×")

# ─── PHASE 10: Key chaining P18→P19 ───
print("\n" + "="*80)
print("PHASE 10: Key chaining hypothesis")
print("="*80)

p19 = load_runes(19)

# Hypothesis: P18 plaintext serves as a key for P19
# We know P19 key (first 47 values)
# If P18 plaintext IS the key source, then first 47 characters of P18 plaintext
# should match the P19 key

# For each cipher mode on P18, check if the resulting plaintext's P19-relevant
# positions match the P19 key
print("Testing: Does any P18 decryption produce the P19 key?")
print(f"P19 key (first 20): {P19_KEY[:20]}")

# P18 is 260 runes. If P18 plaintext is used cyclically as P19's key (271 runes),
# we'd need P18 plaintext to be at least 271 runes (or cycle within 260).
# Actually if P18 length = 260 and P19 key period = 47, maybe positions 0-46 of
# P18 plaintext = P19 key?

# Test: For each simple shift/mode on P18, extract first 47 plaintext values
# and compare to P19 key
print("\nSimple shift scan (P18 Caesar → P19 key match):")
for shift in range(MOD):
    for mode in ["SUB", "ADD"]:
        if mode == "SUB":
            ptxt = [(c - shift) % MOD for c in p18]
        else:
            ptxt = [(c + shift) % MOD for c in p18]
        
        # Compare first 47 values to P19 key
        match47 = sum(1 for i in range(47) if ptxt[i] == P19_KEY[i])
        if match47 > 10:
            print(f"  shift={shift} {mode}: {match47}/47 matches")

# Deeper: if P18 uses Vigenère with unknown key K, then:
# P18_plain[i] = (P18_cipher[i] - K[i % period]) mod 29
# P19_key[j] = P18_plain[j] (if chaining)
# So: P19_key[j] = (P18_cipher[j] - K[j % period]) mod 29
# Therefore: K[j % period] = (P18_cipher[j] - P19_key[j]) mod 29

# If key period divides 47, we can uniquely determine K!
print("\nDeriving P18 key from P19 key (key chaining hypothesis):")
for period in range(1, 48):
    if 47 % period != 0 and period > 47:
        continue
    
    # Derive key from constraint: K[j % period] = (P18_cipher[j] - P19_key[j]) mod 29
    key_slots = [[] for _ in range(period)]
    for j in range(47):  # We know 47 P19 key values
        slot = j % period
        k_val = (p18[j] - P19_KEY[j]) % MOD
        key_slots[slot].append(k_val)
    
    # Check consistency: all values in each slot should be the same
    consistent = True
    key = []
    for slot in range(period):
        if len(key_slots[slot]) == 0:
            consistent = False
            break
        if len(set(key_slots[slot])) != 1:
            consistent = False
            break
        key.append(key_slots[slot][0])
    
    if consistent:
        # We found a consistent key! Decrypt full P18
        plain = decrypt_sub(p18, key)
        text = to_text(plain)
        ic = ioc(plain)
        ws = word_score(text)
        print(f"\n  *** CONSISTENT key found at period {period}!")
        print(f"      Key: {key}")
        print(f"      IoC: {ic:.3f}  Word Score: {ws}")
        print(f"      Text: {text[:120]}")
        
        # Verify: does this plaintext extend as P19 key for positions 47+?
        if len(plain) >= 271:
            # Use P18 plaintext as P19 key
            p19_plain = decrypt_sub(p19, plain[:271])
            p19_text = to_text(p19_plain)
            p19_ic = ioc(p19_plain)
            p19_ws = word_score(p19_text)
            print(f"      P19 decrypted with P18 plaintext: IoC={p19_ic:.3f} ws={p19_ws}")
            print(f"      P19 text: {p19_text[:120]}")

# Also try ADD mode
print("\nDeriving P18 key from P19 key (ADD mode):")
for period in range(1, 48):
    key_slots = [[] for _ in range(period)]
    for j in range(47):
        slot = j % period
        # P18_plain = (P18_cipher + K) mod 29 → K = (P19_key - P18_cipher) mod 29
        k_val = (P19_KEY[j] - p18[j]) % MOD
        key_slots[slot].append(k_val)
    
    consistent = True
    key = []
    for slot in range(period):
        if len(key_slots[slot]) == 0 or len(set(key_slots[slot])) != 1:
            consistent = False
            break
        key.append(key_slots[slot][0])
    
    if consistent:
        plain = decrypt_add(p18, key)
        text = to_text(plain)
        ic = ioc(plain)
        ws = word_score(text)
        print(f"\n  *** CONSISTENT ADD key found at period {period}!")
        print(f"      Key: {key}")
        print(f"      IoC: {ic:.3f}  Word Score: {ws}")
        print(f"      Text: {text[:120]}")

# ─── PHASE 11: Near-miss analysis ───
print("\n" + "="*80)
print("PHASE 11: P18 key derived from P19 key (non-periodic)")
print("="*80)

# Even if key is non-periodic, we can derive the first 47 key values
# and check if the resulting P18 partial plaintext looks like English
derived_key_sub = [(p18[j] - P19_KEY[j]) % MOD for j in range(47)]
derived_key_add = [(P19_KEY[j] - p18[j]) % MOD for j in range(47)]

print(f"Derived key (SUB): {derived_key_sub}")
partial_plain_sub = [(p18[j] - derived_key_sub[j]) % MOD for j in range(47)]
text_sub = to_text(partial_plain_sub)
print(f"P18 partial plaintext (SUB, first 47): {text_sub}")
print(f"  This should equal P19 key as text: {to_text(P19_KEY)}")

# The derived key IS the difference between P18 cipher and P19 key
# If P18 uses a Vigenère key K, then: P18_cipher = (P18_plain + K) mod 29 (or - K)
# And if P18_plain = P19_key, then K = P18_cipher - P19_key
# Check if the derived key has any structure (periodic, LFSR, prime-based...)
print(f"\nDerived key (assuming P18_sub_K=P19_key): {derived_key_sub}")
# Check if it's a keyword
text_key = to_text(derived_key_sub)
print(f"As text: {text_key}")
ic_key = ioc(derived_key_sub)
print(f"Key IoC: {ic_key:.3f}")

# Check if it repeats
for p in range(1, 24):
    matches = sum(1 for i in range(p, 47) if derived_key_sub[i] == derived_key_sub[i % p])
    total = 47 - p
    ratio = matches / total
    if ratio > 0.6:
        print(f"  Period {p}: {matches}/{total} matches = {ratio:.1%}")

print(f"\nDerived key (assuming P18_add_K=P19_key): {derived_key_add}")
text_key_add = to_text(derived_key_add)
print(f"As text: {text_key_add}")

# ─── SUMMARY ───
print("\n" + "="*80)
print("SUMMARY OF BEST RESULTS")
print("="*80)

# Collect and sort all results
best_overall.sort(key=lambda x: (-x[0], -x[1]))
if best_overall:
    print("\nTop frequency analysis results:")
    for ic, ws, period, mode, freq, key, text in best_overall[:10]:
        print(f"  k={period} {mode} {freq}: IoC={ic:.3f} wscore={ws}")
        print(f"    Text: {text}")

print("\nDONE")
