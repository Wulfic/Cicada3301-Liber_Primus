"""Determine the correct P19 key period and missing key values.
We KNOW key[0:43] from verified plaintext.
We need to find key[43:46] (if period is 47) or determine if period is 43."""

import os
from collections import Counter
from itertools import product

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# Expected GP frequency distribution (from solved pages)
# Approximate frequencies from English text mapped to GP
GP_FREQ = {0:0.02, 1:0.03, 2:0.03, 3:0.08, 4:0.06, 5:0.03, 6:0.02, 7:0.02,
            8:0.06, 9:0.07, 10:0.07, 11:0.001, 12:0.01, 13:0.02, 14:0.002,
            15:0.06, 16:0.09, 17:0.02, 18:0.13, 19:0.02, 20:0.04, 21:0.02,
            22:0.01, 23:0.04, 24:0.08, 25:0.01, 26:0.02, 27:0.01, 28:0.03}

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"Cipher length: {N}")

# Verified key values for positions 0-42
KNOWN_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23]
print(f"Known key positions: 0-{len(KNOWN_KEY)-1} ({len(KNOWN_KEY)} values)")

# === TEST 1: Frequency analysis for each candidate period ===
print("\n" + "="*80)
print("TEST 1: Chi-squared analysis for candidate key periods")
print("="*80)

def chi_sq(observed_counts, total, expected_freq):
    """Chi-squared test against expected distribution."""
    chi = 0
    for v in range(29):
        obs = observed_counts.get(v, 0)
        exp = expected_freq.get(v, 0.001) * total
        if exp > 0:
            chi += (obs - exp)**2 / exp
    return chi

results = []
for period in range(10, 60):
    total_chi = 0
    for kpos in range(period):
        positions = list(range(kpos, N, period))
        if not positions:
            continue
        # Use known key if available
        if kpos < len(KNOWN_KEY):
            key_val = KNOWN_KEY[kpos]
        else:
            # For unknown key positions, try all 29 values and pick best
            best_chi = float('inf')
            best_val = 0
            for k in range(29):
                decrypted = [(cipher[p] + k) % 29 for p in positions]
                counts = Counter(decrypted)
                chi = chi_sq(counts, len(positions), GP_FREQ)
                if chi < best_chi:
                    best_chi = chi
                    best_val = k
            key_val = best_val
        
        decrypted = [(cipher[p] + key_val) % 29 for p in positions]
        counts = Counter(decrypted)
        chi = chi_sq(counts, len(positions), GP_FREQ)
        total_chi += chi
    
    avg_chi = total_chi / period
    results.append((period, avg_chi))

results.sort(key=lambda x: x[1])
print("Top 15 periods by average chi-squared (lower = better fit to English):")
for period, chi in results[:15]:
    marker = " <-- CANDIDATE" if period in [43, 47] else ""
    print(f"  Period {period:3d}: avg chi-sq = {chi:8.2f}{marker}")

# === TEST 2: For period 47, find optimal key[43:46] ===
print("\n" + "="*80)
print("TEST 2: Optimal key values for positions 43-46 (period 47)")
print("="*80)

best_keys = {}
for kpos in [43, 44, 45, 46]:
    positions = list(range(kpos, N, 47))
    n_pos = len(positions)
    
    best_val = 0
    best_chi = float('inf')
    all_results = []
    
    for k in range(29):
        decrypted = [(cipher[p] + k) % 29 for p in positions]
        counts = Counter(decrypted)
        chi = chi_sq(counts, n_pos, GP_FREQ)
        all_results.append((k, chi))
        if chi < best_chi:
            best_chi = chi
            best_val = k
    
    all_results.sort(key=lambda x: x[1])
    best_keys[kpos] = best_val
    print(f"\n  Key position {kpos} ({n_pos} cipher positions):")
    for k, chi in all_results[:5]:
        marker = " ← OLD VALUE" if k == 28 else ""
        marker2 = " ← BEST" if k == best_val else ""
        print(f"    key={k:2d} ({LATIN[k]:3s}): chi-sq={chi:8.2f}{marker}{marker2}")

print(f"\nOptimal key[43:46] = [{best_keys[43]}, {best_keys[44]}, {best_keys[45]}, {best_keys[46]}]")
print(f"Old key[43:46] = [28, 28, 28, 28]")

# === TEST 3: Full decryption with optimal key ===
print("\n" + "="*80)
print("TEST 3: Full decryption with optimized key (period 47)")
print("="*80)

full_key = KNOWN_KEY + [best_keys[43], best_keys[44], best_keys[45], best_keys[46]]
print(f"Full key: {full_key}")

decrypted = [(cipher[i] + full_key[i % 47]) % 29 for i in range(N)]

# Parse into words
words = []
current = []
for c in raw:
    if c in GP:
        current.append(GP[c])
    elif current:
        words.append(current)
        current = []
if current:
    words.append(current)

pos = 0
dec_words = []
for word in words:
    n = len(word)
    word_dec = decrypted[pos:pos+n]
    word_lat = ''.join(LATIN[v] for v in word_dec)
    dec_words.append(word_lat)
    pos += n

# Print continuous text with spaces
full_text = ' '.join(dec_words)
print(f"Decrypted text (optimized key):")
# Wrap at 80 chars
for i in range(0, len(full_text), 80):
    print(f"  {full_text[i:i+80]}")

# === TEST 4: Try period 43 ===
print("\n" + "="*80)
print("TEST 4: Full decryption with period 43 (first 43 key values only)")
print("="*80)

key43 = KNOWN_KEY[:43]
dec43 = [(cipher[i] + key43[i % 43]) % 29 for i in range(N)]

pos = 0
dec_words43 = []
for word in words:
    n = len(word)
    word_dec = dec43[pos:pos+n]
    word_lat = ''.join(LATIN[v] for v in word_dec)
    dec_words43.append(word_lat)
    pos += n

full_text43 = ' '.join(dec_words43)
print(f"Decrypted text (period 43):")
for i in range(0, len(full_text43), 80):
    print(f"  {full_text43[i:i+80]}")

# === TEST 5: IoC comparison ===
print("\n" + "="*80)
print("TEST 5: Index of Coincidence comparison")
print("="*80)

def ioc(values):
    n = len(values)
    if n < 2:
        return 0
    counts = Counter(values)
    return sum(c * (c-1) for c in counts.values()) / (n * (n-1))

print(f"  Cipher IoC: {ioc(cipher):.4f}")
print(f"  Optimized key (p=47) IoC: {ioc(decrypted):.4f}")
print(f"  Period 43 IoC: {ioc(dec43):.4f}")
print(f"  Expected English GP IoC: ~1.73 (normalized to 29)")

# Normalized IoC (multiply by 29)
print(f"  Cipher IoC*29: {ioc(cipher)*29:.4f}")
print(f"  Optimized key (p=47) IoC*29: {ioc(decrypted)*29:.4f}")
print(f"  Period 43 IoC*29: {ioc(dec43)*29:.4f}")

# === TEST 6: Brute force key[43:46] for English word detection ===
print("\n" + "="*80)
print("TEST 6: English word detection for key[43:46] candidates")
print("="*80)

# Common English words in GP
COMMON_WORDS = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS',
                'ONE','OUR','OUT','HAS','HIS','HOW','WHO','ITS','MAY','NEW','NOW',
                'OLD','SEE','WAY','DAY','DID','GET','HAS','HIM','HIS','LET',
                'SAY','SHE','TOO','USE','THIS','THAT','WITH','HAVE','FROM','THEY',
                'BEEN','HAVE','MANY','SOME','THEM','THAN','EACH','MAKE','LIKE',
                'LONG','LOOK','MANY','MOST','OVER','SUCH','TAKE','THAN','WHAT',
                'WHEN','WILL','INTO','PATH','SHOW','RUNE','SELF','MIND','SOUL',
                'SEEK','FIND','KNOW','WISDOM','TRUTH','LIGHT','DARKNESS',
                'PRIME','PRIMES','NUMBER','NUMBERS','WITHIN','WITHOUT','SACRED'}

def score_english(text_words):
    """Score decoded text based on English word detection."""
    words_upper = [w.upper() for w in text_words]
    matched = sum(1 for w in words_upper if w in COMMON_WORDS)
    return matched

# Try top candidates from frequency analysis
print("Testing top 3 candidates for each of positions 43-46:")
top_candidates = {}
for kpos in [43, 44, 45, 46]:
    positions = list(range(kpos, N, 47))
    all_results = []
    for k in range(29):
        decrypted_test = [(cipher[p] + k) % 29 for p in positions]
        counts = Counter(decrypted_test)
        chi = chi_sq(counts, len(positions), GP_FREQ)
        all_results.append((k, chi))
    all_results.sort(key=lambda x: x[1])
    top_candidates[kpos] = [x[0] for x in all_results[:5]]

print(f"  Pos 43 top: {top_candidates[43]}")
print(f"  Pos 44 top: {top_candidates[44]}")
print(f"  Pos 45 top: {top_candidates[45]}")
print(f"  Pos 46 top: {top_candidates[46]}")

# Try all combos of top 5
best_score = 0
best_combo = None
for k43 in top_candidates[43]:
    for k44 in top_candidates[44]:
        for k45 in top_candidates[45]:
            for k46 in top_candidates[46]:
                test_key = KNOWN_KEY + [k43, k44, k45, k46]
                dec = [(cipher[i] + test_key[i % 47]) % 29 for i in range(N)]
                # Build words
                pos = 0
                wds = []
                for word in words:
                    n = len(word)
                    word_dec = dec[pos:pos+n]
                    word_lat = ''.join(LATIN[v] for v in word_dec)
                    wds.append(word_lat)
                    pos += n
                score = score_english(wds)
                if score > best_score:
                    best_score = score
                    best_combo = (k43, k44, k45, k46)
                    best_text = ' '.join(wds)

if best_combo:
    print(f"\nBest combo: key[43:46] = {list(best_combo)} = {''.join(LATIN[v] for v in best_combo)}")
    print(f"Score: {best_score} English words matched")
    print(f"Text:")
    for i in range(0, len(best_text), 80):
        print(f"  {best_text[i:i+80]}")
