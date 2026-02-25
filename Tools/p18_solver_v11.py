"""
P18 SOLVER v11 - Fresh analysis with frequency + word matching
CONFIRMED: dashes ARE word separators in LP rune text!
CONFIRMED: SOLUTION.md "BEING OF ALL..." is WRONG (misaligns word boundaries)

This means:
1. The repeating key model (period 53) is likely correct (IoC=1.860)
2. Word matching against dash-separated chunks IS the right approach
3. Need to independently verify the 34 confirmed key values via frequency analysis

Strategy:
1. Column-level frequency analysis (chi-squared) for all 53 columns
2. Cross-validate with previously confirmed word matches
3. Identify where freq analysis disagrees with word matching
4. Build a comprehensive key with confidence levels
"""
import os, sys
from collections import Counter
import math

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    words, current, start, pos = [], [], 0, 0
    for c in raw:
        if c in GP:
            if not current: start = pos
            current.append(GP[c]); pos += 1
        elif current:
            words.append((start, list(current))); current = []
    if current: words.append((start, list(current)))
    return runes, words

cipher, words = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")
print(f"Word lengths: {[len(w) for _,w in words]}")

# English letter frequencies in Gematria Primus (29-alphabet)
# Based on analysis of solved LP pages
ENG_FREQ = [0.022, 0.038, 0.035, 0.075, 0.060, 0.036, 0.020, 0.024,
            0.061, 0.067, 0.070, 0.002, 0.005, 0.019, 0.002, 0.063,
            0.056, 0.015, 0.127, 0.024, 0.040, 0.015, 0.003, 0.043,
            0.082, 0.003, 0.020, 0.003, 0.003]

# =======================================================================
# Phase 1: Column frequency analysis
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 1: Column-level frequency analysis (chi-squared)")
print(f"{'='*80}")

# Build columns
cols = [[] for _ in range(KLEN)]
for i in range(N):
    cols[i % KLEN].append(cipher[i])

# For each column, test all 29 shifts and rank by chi-squared
def chi_squared(observed_counts, n, expected_freq):
    """Chi-squared statistic for goodness-of-fit."""
    chi2 = 0
    for i in range(MOD):
        observed = observed_counts.get(i, 0)
        expected = n * expected_freq[i]
        if expected > 0:
            chi2 += (observed - expected)**2 / expected
    return chi2

def freq_score(observed_counts, n, expected_freq):
    """Correlation score (higher = better fit)."""
    score = 0
    for i in range(MOD):
        observed = observed_counts.get(i, 0) / n
        score += observed * expected_freq[i]
    return score

best_shifts = []
for b in range(KLEN):
    col = cols[b]
    results = []
    for s in range(MOD):
        dec = [(v - s) % MOD for v in col]
        counts = Counter(dec)
        # Chi-squared (lower = better)
        chi2 = chi_squared(counts, len(col), ENG_FREQ)
        # Correlation (higher = better)
        corr = freq_score(counts, len(col), ENG_FREQ)
        results.append((s, chi2, corr))
    
    # Sort by correlation (descending)
    results.sort(key=lambda x: -x[2])
    best_shifts.append(results)
    
    print(f"  Col {b:2d} ({len(col)} vals): Best shifts: ", end="")
    for rank in range(min(3, len(results))):
        s, chi2, corr = results[rank]
        print(f"  {s}({LAT[s]})[corr={corr:.4f}]", end="")
    print()

# =======================================================================
# Phase 2: Compare with previously confirmed values
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 2: Cross-validation with word-matching confirmed values") 
print(f"{'='*80}")

confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}

for b in range(KLEN):
    freq_best = best_shifts[b][0][0]
    freq_best_corr = best_shifts[b][0][2]
    
    if b in confirmed:
        conf_val = confirmed[b]
        # Find rank of confirmed value
        rank = next(i for i, (s, _, _) in enumerate(best_shifts[b]) if s == conf_val)
        conf_corr = next(corr for s, _, corr in best_shifts[b] if s == conf_val)
        
        agree = "AGREE" if freq_best == conf_val else f"DISAGREE (freq={freq_best}/{LAT[freq_best]}, wm={conf_val}/{LAT[conf_val]})"
        if rank > 0:
            agree += f" [confirmed={rank+1}th best by freq, gap={freq_best_corr-conf_corr:.4f}]"
        print(f"  Col {b:2d}: {agree}")
    else:
        print(f"  Col {b:2d}: UNDETERMINED - freq suggests {freq_best} ({LAT[freq_best]}) [corr={freq_best_corr:.4f}]")

# =======================================================================
# Phase 3: Build key using freq analysis + word matching
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 3: Build best-estimate key")
print(f"{'='*80}")

# Use confirmed values where freq agrees, investigate disagreements
key_estimate = [0] * KLEN
confidence = [''] * KLEN

for b in range(KLEN):
    freq_best = best_shifts[b][0][0]
    if b in confirmed:
        conf_val = confirmed[b]
        rank = next(i for i, (s, _, _) in enumerate(best_shifts[b]) if s == conf_val)
        if rank == 0:
            key_estimate[b] = conf_val
            confidence[b] = 'HIGH'
        else:
            # Disagreement - use confirmed for now but flag
            key_estimate[b] = conf_val
            confidence[b] = f'DISPUTED(freq_rank={rank+1})'
    else:
        key_estimate[b] = freq_best
        confidence[b] = 'FREQ_ONLY'

print(f"Key estimate: {key_estimate}")
print(f"Key (LAT): {''.join(LAT[v] for v in key_estimate)}")
print(f"\nConfidence per bucket:")
for b in range(KLEN):
    print(f"  [{b:2d}] = {key_estimate[b]:2d} ({LAT[key_estimate[b]]:>2s}) [{confidence[b]}]")

# =======================================================================
# Phase 4: Decrypt and analyze words
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 4: Full decryption with estimated key")
print(f"{'='*80}")

dec = [(cipher[i] - key_estimate[i % KLEN]) % MOD for i in range(N)]
full_text = ''.join(LAT[v] for v in dec)

# Load dictionary
WORDLIST = set()
try:
    with open('Tools/english_words.txt', 'r') as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 1: WORDLIST.add(w)
    print(f"  Loaded {len(WORDLIST)} dictionary words")
except:
    WORDLIST = set('A I AM AN AS AT BE BY DO GO HE IF IN IS IT ME MY NO OF OH OK ON OR SO TO UP US WE THE AND FOR ARE BUT NOT YOU ALL ANY CAN HER WAS ONE OUR OUT HAD HAS HIS HOW ITS LET MAY NEW NOW OLD SEE WAY WHO BOY DID GET HIM HIS PUT SAY SHE TOO USE DAD MOM THAT WITH HAVE THIS WILL YOUR FROM THEY BEEN CALL CAME COME EACH FIND FIRST GIVE GOOD GREAT HERE JUST KNOW LIKE LONG LOOK MAKE MANY MOST MUCH NAME NEVER OVER PART SOME TELL THEM THEN THEY THING THINK THOSE THREE TIME TURN VERY WANT WHAT WHEN WHICH WHILE WILL WITH WORD WORK WORLD WOULD WRITE YEAR ABOUT AFTER AGAIN BEING COULD EVERY FIRST FOUND GREAT HOUSE LARGE LIGHT MIGHT NEVER OTHER RIGHT SHALL SMALL SOUND STILL THEIR THERE THESE THINK THREE WHERE WHICH WORLD WOULD WRITE YOUNG BEFORE CHANGE FOLLOW NUMBER SHOULD THOUGHT THROUGH TRUTH FAITH LEARN LIAR PUBLIC THIRD LENGTH DEATH BIRTH EARTH SOUTH NORTH YOUTH WORTH MOUTH FATHER MOTHER WISDOM WITHIN SACRED DIVINE SPIRIT PRIMES CIPHER LIGHT ABOVE BELOW POWER ORDER BEING'.split())
    print(f"  Using fallback word list ({len(WORDLIST)} words)")

# Check each word
n_match = 0
for wi, (start, wrunes) in enumerate(words):
    vals = dec[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    
    # Check word membership
    is_match = txt.upper() in WORDLIST
    marker = "Y" if is_match else " "
    if is_match: n_match += 1
    
    # Check bucket confidence
    buckets = [(start + j) % KLEN for j in range(len(wrunes))]
    confs = [confidence[b] for b in buckets]
    has_disputed = any('DISPUTED' in c for c in confs)
    has_freq_only = any('FREQ_ONLY' in c for c in confs)
    
    status = ""
    if has_disputed: status += " [HAS_DISPUTED]"
    if has_freq_only: status += " [HAS_FREQ_ONLY]"
    
    print(f"  {marker} w{wi:2d} (pos {start:3d}-{start+len(wrunes)-1:3d}, buckets={buckets}): '{txt}'{status}")

print(f"\n  Total word matches: {n_match}/{len(words)}")

# =======================================================================
# Phase 5: Test with ALL freq-suggested values (override confirmed)
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 5: Pure frequency-analysis key (ignoring word matching)")
print(f"{'='*80}")

freq_key = [best_shifts[b][0][0] for b in range(KLEN)]
dec_freq = [(cipher[i] - freq_key[i % KLEN]) % MOD for i in range(N)]

n_match_freq = 0
for wi, (start, wrunes) in enumerate(words):
    vals = dec_freq[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    is_match = txt.upper() in WORDLIST
    marker = "Y" if is_match else " "
    if is_match: n_match_freq += 1
    print(f"  {marker} w{wi:2d}: '{txt}'")

print(f"\n  Freq-only matches: {n_match_freq}/{len(words)}")
print(f"  Freq key: {freq_key}")

# =======================================================================
# Phase 6: Check the 13 non-English words more carefully
# =======================================================================
print(f"\n{'='*80}")
print(f"Phase 6: Analysis of non-English words with confirmed keys")
print(f"{'='*80}")

# For each non-English word whose buckets are ALL confirmed,
# check what ALL 29 possible shifts would produce for each bucket
# to see if there's a nearby English word

for wi, (start, wrunes) in enumerate(words):
    buckets = [(start + j) % KLEN for j in range(len(wrunes))]
    all_confirmed = all(b in confirmed for b in buckets)
    
    if not all_confirmed:
        continue
    
    vals = dec[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals).upper()
    
    if txt in WORDLIST:
        continue  # Skip matching words
    
    # This word has ALL confirmed buckets but doesn't match
    print(f"\n  w{wi:2d} (pos {start}, {len(wrunes)} runes, buckets={buckets}): '{txt}'")
    print(f"    Cipher: {[cipher[start+j] for j in range(len(wrunes))]}")
    print(f"    Key: {[key_estimate[b] for b in buckets]}")
    print(f"    Dec: {vals}")
    
    # For each bucket in this word, list all words that CONFIRMED that value
    for j, b in enumerate(buckets):
        # Find other words using this bucket
        other_words = []
        for wi2, (start2, wrunes2) in enumerate(words):
            if wi2 == wi: continue
            for j2 in range(len(wrunes2)):
                if (start2 + j2) % KLEN == b:
                    vals2 = dec[start2:start2+len(wrunes2)]
                    txt2 = ''.join(LAT[v] for v in vals2).upper()
                    is_m = txt2 in WORDLIST
                    other_words.append((wi2, txt2, is_m))
                    break
        confirming = [(wi2, txt2) for wi2, txt2, is_m in other_words if is_m]
        non_confirming = [(wi2, txt2) for wi2, txt2, is_m in other_words if not is_m]
        print(f"    Bucket {b} (key={key_estimate[b]}): confirmed by {len(confirming)} words: {confirming[:3]}")
        if non_confirming:
            print(f"      Also fails for: {non_confirming[:3]}")

    # Try all possible English words of this length
    rune_len = len(wrunes)
    if rune_len <= 6:
        matching_dict_words = [w for w in WORDLIST if len(text_to_gp_len(w)) == rune_len]
        # For each, compute what key values would be needed
        alternatives = []
        for dw in matching_dict_words[:200]:  # Limit search
            gp_vals = text_to_gp_safe(dw)
            if gp_vals and len(gp_vals) == rune_len:
                needed_keys = [(cipher[start+j] - gp_vals[j]) % MOD for j in range(rune_len)]
                # Check if any needed key differs from confirmed by only 1-2 buckets
                n_diff = sum(1 for j, nb in enumerate(zip(needed_keys, [key_estimate[buckets[j]] for j in range(rune_len)])) if nb[0] != nb[1])
                if n_diff <= 2:
                    alternatives.append((dw, needed_keys, n_diff))
        
        if alternatives:
            alternatives.sort(key=lambda x: x[2])
            print(f"    Nearest dict words: {alternatives[:5]}")

def text_to_gp_len(text):
    """Estimate GP length of English text."""
    n = 0
    text = text.upper()
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in {'TH','NG','EO','OE','EA','AE','IA'}:
            n += 1; i += 2
        elif text[i].isalpha():
            n += 1; i += 1
        else:
            i += 1
    return 'x' * n

def text_to_gp_safe(text):
    """Convert English text to GP values. Returns None if impossible."""
    DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
    ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
              'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
              'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
    result = []
    i = 0
    text = text.upper()
    while i < len(text):
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in DIGRAPHS:
                result.append(DIGRAPHS[di])
                i += 2
                continue
        if text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
        else:
            return None
        i += 1
    return result

print(f"\n=== DONE ===")
