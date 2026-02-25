"""
P18 SOLVER v2 - Advanced key recovery for Vigenère key length 53
Approaches:
1. Mathematical key derivation (primes, totient, etc.)
2. Bigram fitness hill-climbing
3. Single-rune word constrained search
4. Known phrase cribs
"""
import os, math
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
    return runes, words

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1))

def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i): sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

PRIMES = primes_up_to(100000)
KLEN = 53

cipher, words = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

# === Build bigram score table from English ===
# GP bigram frequencies for English text (approximate)
# Most common bigrams in English: TH, HE, IN, ER, AN, RE, ON, AT, EN, ND, TI, ES, OR, TE, OF, ED, IS, IT, AL, AR
# In GP: TH=single rune(2), HE=H(8)+E(18), IN=I(10)+N(9), ER=E(18)+R(4), etc.

# Simple scoring: frequency of common English GP bigrams
# I'll use a correlation with expected monogram frequencies as primary metric
eng_gp_freq = [0.0] * 29
eng_gp_freq[0] = 0.022   # F
eng_gp_freq[1] = 0.038   # U (+V)
eng_gp_freq[2] = 0.035   # TH
eng_gp_freq[3] = 0.075   # O
eng_gp_freq[4] = 0.060   # R
eng_gp_freq[5] = 0.036   # C (+K)
eng_gp_freq[6] = 0.020   # G
eng_gp_freq[7] = 0.024   # W
eng_gp_freq[8] = 0.061   # H
eng_gp_freq[9] = 0.067   # N
eng_gp_freq[10] = 0.070  # I
eng_gp_freq[11] = 0.002  # J
eng_gp_freq[12] = 0.005  # EO
eng_gp_freq[13] = 0.019  # P
eng_gp_freq[14] = 0.002  # X
eng_gp_freq[15] = 0.063  # S
eng_gp_freq[16] = 0.056  # T (not TH)
eng_gp_freq[17] = 0.015  # B
eng_gp_freq[18] = 0.127  # E
eng_gp_freq[19] = 0.024  # M
eng_gp_freq[20] = 0.040  # L
eng_gp_freq[21] = 0.015  # NG
eng_gp_freq[22] = 0.003  # OE
eng_gp_freq[23] = 0.043  # D
eng_gp_freq[24] = 0.082  # A
eng_gp_freq[25] = 0.003  # AE
eng_gp_freq[26] = 0.020  # Y
eng_gp_freq[27] = 0.003  # IA
eng_gp_freq[28] = 0.003  # EA
total_f = sum(eng_gp_freq)
eng_gp_freq = [f/total_f for f in eng_gp_freq]

common_words = {'THE','AND','OF','TO','IN','IS','IT','THAT','WAS','FOR','ON','ARE','WITH',
                'AS','AT','BE','THIS','FROM','OR','AN','BY','NOT','BUT','WHAT','ALL','A','I',
                'HE','SHE','THEY','WE','YOU','HIS','HER','ITS','OUR','THEIR','WHO','WHICH',
                'HAS','HAD','HAVE','BEEN','ONE','EACH','LIKE','DO','SO','IF','NO','MY','UP',
                'ABOUT','OUT','THEM','THEN','INTO','SOME','THAN','OVER','SUCH','ALSO','COME',
                'TIME','VERY','YOUR','EACH','MAKE','HOW','THERE','WHEN','COULD','THESE',
                'WOULD','OTHER','MORE','AFTER','MANY','WILL','SHALL','WITHIN','DEEP','WEB',
                'THROUGH','BETWEEN','KNOW','WISDOM','YET','NOW','HERE','ONLY','SEEK','FIND',
                'SEE','LIFE','DEATH','SELF','BEING','MIND','TRUTH','REALITY'}

# =====================================================================
# ATTACK 1: Mathematical key derivation
# =====================================================================
print("\n" + "="*80)
print("ATTACK 1: Mathematical key derivation")
print("="*80)

results = []

for offset in range(0, 200):
    for name, key_fn in [
        (f"prime[i+{offset}]%29", lambda i, o=offset: PRIMES[i+o] % 29),
        (f"totient(prime[i+{offset}])%29", lambda i, o=offset: totient(PRIMES[i+o]) % 29),
        (f"(prime[i+{offset}]-1)%29", lambda i, o=offset: (PRIMES[i+o]-1) % 29),
        (f"cumsum_prime_from_{offset}%29", lambda i, o=offset: sum(PRIMES[o:o+i+1]) % 29),
        (f"prime[i+{offset}]*prime[i+{offset}+1]%29", lambda i, o=offset: (PRIMES[i+o]*PRIMES[i+o+1]) % 29),
    ]:
        key = [key_fn(i) for i in range(KLEN)]
        
        for mode, fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29), ("BEAU", lambda c,k: (k-c)%29)]:
            dec = [fn(cipher[i], key[i%KLEN]) for i in range(N)]
            ic = ioc(dec) * 29
            if ic > 1.4:
                # Count words
                dw = []
                for start, word in words:
                    wd = [dec[start+j] for j in range(len(word))]
                    dw.append(''.join(LAT[v] for v in wd))
                wc = sum(1 for w in dw if w.upper() in common_words)
                results.append((ic, wc, name, mode, key[:10], ' '.join(dw[:20])))

# Also try: key[i] = pow(g, i, 29) for various generators
for g in range(2, 29):
    key = [pow(g, i, 29) for i in range(KLEN)]
    for mode, fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29)]:
        dec = [fn(cipher[i], key[i%KLEN]) for i in range(N)]
        ic = ioc(dec) * 29
        if ic > 1.4:
            dw = []
            for start, word in words:
                wd = [dec[start+j] for j in range(len(word))]
                dw.append(''.join(LAT[v] for v in wd))
            wc = sum(1 for w in dw if w.upper() in common_words)
            results.append((ic, wc, f"pow({g},i,29)", mode, key[:10], ' '.join(dw[:20])))

# key[i] = (A*i + B) % 29
for A in range(29):
    for B in range(29):
        key = [(A*i + B) % 29 for i in range(KLEN)]
        for mode, fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29)]:
            dec = [fn(cipher[i], key[i%KLEN]) for i in range(N)]
            ic = ioc(dec) * 29
            if ic > 1.5:
                dw = []
                for start, word in words:
                    wd = [dec[start+j] for j in range(len(word))]
                    dw.append(''.join(LAT[v] for v in wd))
                wc = sum(1 for w in dw if w.upper() in common_words)
                results.append((ic, wc, f"({A}*i+{B})%29", mode, key[:10], ' '.join(dw[:20])))

# key[i] = (A*i^2 + B*i + C) % 29
for A in range(29):
    for B in range(29):
        key = [(A*i*i + B*i) % 29 for i in range(KLEN)]
        for mode, fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29)]:
            dec = [fn(cipher[i], key[i%KLEN]) for i in range(N)]
            ic = ioc(dec) * 29
            if ic > 1.5:
                dw = []
                for start, word in words:
                    wd = [dec[start+j] for j in range(len(word))]
                    dw.append(''.join(LAT[v] for v in wd))
                wc = sum(1 for w in dw if w.upper() in common_words)
                results.append((ic, wc, f"({A}*i^2+{B}*i)%29", mode, key[:10], ' '.join(dw[:20])))

results.sort(key=lambda x: (-x[0], -x[1]))
print(f"Found {len(results)} results with IoC > threshold")
for ic, wc, name, mode, key10, text in results[:20]:
    print(f"  IoC={ic:.3f} words={wc} {name} {mode}: key[:10]={key10}")
    print(f"    {text}")

# =====================================================================
# ATTACK 2: Bigram hill-climbing starting from frequency key
# =====================================================================
print("\n" + "="*80)
print("ATTACK 2: Bigram score hill-climbing")
print("="*80)

# Build bigram log-probability table
# Common English bigrams in GP encoding
bigram_bonus = {}
common_bigrams = [
    # TH is a single rune (2), so THE = TH(2), E(18) and THAT = TH(2), A(24), T(16)
    (2, 18, 3.0),   # TH-E
    (8, 18, 2.5),   # H-E
    (10, 9, 2.0),   # I-N
    (18, 4, 2.0),   # E-R
    (24, 9, 2.0),   # A-N
    (4, 18, 2.0),   # R-E
    (3, 9, 1.5),    # O-N
    (24, 16, 1.5),  # A-T
    (18, 9, 1.5),   # E-N
    (9, 23, 1.5),   # N-D
    (16, 10, 1.5),  # T-I
    (18, 15, 1.5),  # E-S
    (3, 4, 1.5),    # O-R
    (16, 18, 1.5),  # T-E
    (3, 0, 1.5),    # O-F
    (18, 23, 1.5),  # E-D
    (10, 15, 1.5),  # I-S
    (10, 16, 1.5),  # I-T
    (24, 20, 1.5),  # A-L
    (24, 4, 1.5),   # A-R
    (15, 16, 1.5),  # S-T
    (9, 18, 1.5),   # N-E
    (2, 24, 1.5),   # TH-A
    (2, 10, 1.5),   # TH-I
    (2, 3, 1.0),    # TH-O
    (2, 18, 1.0),   # TH-E (dup)
    (15, 18, 1.0),  # S-E
    (20, 18, 1.0),  # L-E
    (20, 10, 1.0),  # L-I
    (9, 3, 1.0),    # N-O
    (23, 18, 1.0),  # D-E
    (24, 15, 1.0),  # A-S
    (0, 3, 1.0),    # F-O
    (7, 10, 1.0),   # W-I
    (7, 24, 1.0),   # W-A
    (17, 18, 1.0),  # B-E
]
for a, b, score in common_bigrams:
    bigram_bonus[(a,b)] = bigram_bonus.get((a,b), 0) + score

# Rare/unlikely bigrams penalty
rare_runes = {11, 12, 14, 22, 25, 27, 28}  # J, EO, X, OE, AE, IA, EA

def bigram_score(decrypted):
    """Score decrypted text using bigram frequencies."""
    score = 0
    for i in range(len(decrypted) - 1):
        pair = (decrypted[i], decrypted[i+1])
        score += bigram_bonus.get(pair, 0)
        # Penalize rare runes
        if decrypted[i] in rare_runes:
            score -= 0.3
    return score

def word_score(decrypted, word_list):
    """Score by number of recognized English words."""
    dw = []
    for start, word in word_list:
        wd = [decrypted[start+j] for j in range(len(word))]
        dw.append(''.join(LAT[v] for v in wd))
    return sum(1 for w in dw if w.upper() in common_words)

for mode_name, decrypt_fn in [
    ("SUB", lambda c,k: (c-k)%29),
    ("ADD", lambda c,k: (c+k)%29),
    ("BEAUFORT", lambda c,k: (k-c)%29),
]:
    # Initialize key using frequency correlation
    columns = [[] for _ in range(KLEN)]
    for i in range(N): columns[i%KLEN].append(cipher[i])
    
    key = [0] * KLEN
    for col_idx in range(KLEN):
        col = columns[col_idx]
        n = len(col)
        best_shift = 0
        best_score = -999
        for shift in range(29):
            dec = [decrypt_fn(v, shift) for v in col]
            counts = Counter(dec)
            score = sum(counts.get(i,0)/n * eng_gp_freq[i] for i in range(29))
            if score > best_score:
                best_score = score
                best_shift = shift
        key[col_idx] = best_shift
    
    dec = [decrypt_fn(cipher[i], key[i%KLEN]) for i in range(N)]
    init_bscore = bigram_score(dec)
    init_wscore = word_score(dec, words)
    
    # Hill climb using bigram score
    improved = True
    while improved:
        improved = False
        for pos in range(KLEN):
            old_val = key[pos]
            best_val = old_val
            best_bs = bigram_score([decrypt_fn(cipher[i], key[i%KLEN]) for i in range(N)])
            
            for val in range(29):
                if val == old_val: continue
                key[pos] = val
                dec = [decrypt_fn(cipher[i], key[i%KLEN]) for i in range(N)]
                bs = bigram_score(dec)
                if bs > best_bs:
                    best_bs = bs
                    best_val = val
            
            key[pos] = best_val
            if best_val != old_val:
                improved = True
    
    dec = [decrypt_fn(cipher[i], key[i%KLEN]) for i in range(N)]
    final_ic = ioc(dec) * 29
    final_ws = word_score(dec, words)
    final_bs = bigram_score(dec)
    
    dw = []
    for start, word in words:
        wd = [dec[start+j] for j in range(len(word))]
        dw.append(''.join(LAT[v] for v in wd))
    
    text = ''.join(LAT[v] for v in dec)
    
    print(f"\n{mode_name}: IoC={final_ic:.3f} bigram={final_bs:.1f} words={final_ws}/{len(dw)} (init words={init_wscore})")
    print(f"Key: {key}")
    print(f"Words: {' '.join(dw[:35])}")
    print(f"Text: {text[:250]}")

# =====================================================================
# ATTACK 3: Apply key length 53 to ALL other unsolved pages too
# =====================================================================
print("\n" + "="*80)
print("ATTACK 3: Key length 53 scan on ALL unsolved pages")
print("="*80)

for pg in range(18, 55):
    runes, pg_words = load_page(pg)
    if not runes: continue
    n = len(runes)
    
    # Split into columns with key length 53
    cols = [[] for _ in range(53)]
    for i in range(n): cols[i%53].append(runes[i])
    
    avg_ic = sum(ioc(c)*29 for c in cols if len(c) >= 2) / max(1, sum(1 for c in cols if len(c) >= 2))
    
    if avg_ic > 1.3 and pg != 18:
        print(f"  P{pg:02d}: {n} runes, avg col IoC*29 = {avg_ic:.3f} ***")
    elif pg == 18:
        continue  # Already working on P18
    
    # Also scan other prime key lengths for each page
    best_kl = 0
    best_ic = 0
    for kl in [k for k in PRIMES[:50] if 2 <= k <= 200]:
        cols_k = [[] for _ in range(kl)]
        for i in range(n): cols_k[i%kl].append(runes[i])
        filled = [c for c in cols_k if len(c) >= 2]
        if not filled: continue
        avg = sum(ioc(c)*29 for c in filled) / len(filled)
        if avg > best_ic:
            best_ic = avg
            best_kl = kl
    
    if best_ic > 1.3:
        print(f"  P{pg:02d}: {n} runes, BEST klen={best_kl}, avg col IoC*29 = {best_ic:.3f}")

print("\n=== DONE ===")
