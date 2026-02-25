"""
P18 SOLVER v9 - LFSR Key Recovery
The key might follow a linear recurrence (LFSR) over GF(29).
Use the 31 confirmed key values to find the LFSR degree and coefficients,
then predict the 22 unknown values.

Also tests: the key as a RUNNING key (autokey) where after initial primer,
key[i] = plaintext[i-53].
"""
import os, sys
from collections import Counter

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

def modinv(a, m=MOD):
    """Modular inverse using extended Euclidean algorithm."""
    if a == 0: return None
    g, x, _ = extended_gcd(a % m, m)
    if g != 1: return None
    return x % m

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def gauss_solve_gf(matrix, rhs, mod=MOD):
    """Solve Ax = b over GF(mod). Returns x or None if no solution."""
    n = len(matrix)  # equations
    m = len(matrix[0])  # unknowns
    
    # Augmented matrix
    aug = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    
    pivot_cols = []
    row = 0
    for col in range(m):
        # Find pivot
        pivot = None
        for r in range(row, n):
            if aug[r][col] % mod != 0:
                pivot = r
                break
        if pivot is None:
            continue
        
        # Swap
        aug[row], aug[pivot] = aug[pivot], aug[row]
        pivot_cols.append(col)
        
        # Scale pivot row
        inv = modinv(aug[row][col], mod)
        if inv is None: continue
        aug[row] = [(v * inv) % mod for v in aug[row]]
        
        # Eliminate
        for r in range(n):
            if r != row and aug[r][col] != 0:
                factor = aug[r][col]
                aug[r] = [(aug[r][j] - factor * aug[row][j]) % mod for j in range(m + 1)]
        
        row += 1
    
    # Check consistency
    for r in range(row, n):
        if aug[r][m] % mod != 0:
            return None  # Inconsistent
    
    # Extract solution (assuming unique solution for the pivot columns)
    solution = [0] * m
    for i, col in enumerate(pivot_cols):
        solution[col] = aug[i][m] % mod
    
    return solution

cipher, words = load_page(18)
N = len(cipher)

# 31 confirmed key values (WITHOUT Component B which was from dictionary matching)
# Using ONLY the original 31 from word-matching
confirmed_original = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}

# Also include Component B solution
confirmed = dict(confirmed_original)
confirmed[23] = 2
confirmed[24] = 5
confirmed[25] = 5

# Get the key values in order (None for unknown)
key_known = [confirmed.get(i) for i in range(KLEN)]
print("Known key values:")
for i in range(KLEN):
    if key_known[i] is not None:
        print(f"  key[{i}] = {key_known[i]} ({LAT[key_known[i]]})")

# Find runs of consecutive known values
runs = []
start = None
for i in range(KLEN):
    if key_known[i] is not None:
        if start is None: start = i
    else:
        if start is not None:
            runs.append((start, i - 1))
            start = None
if start is not None:
    runs.append((start, KLEN - 1))

print(f"\nConsecutive known runs: {runs}")
for s, e in runs:
    vals = [key_known[i] for i in range(s, e+1)]
    print(f"  [{s}-{e}]: {vals}")

print(f"\n{'='*80}")
print(f"Phase 1: LFSR degree search")
print(f"{'='*80}")

# For each degree D, check if key[n] = sum(c_i * key[n-i]) for i=1..D
# Using the consecutive runs to form equations
# key[n] = c1*key[n-1] + c2*key[n-2] + ... + cD*key[n-D] (mod 29)

best_lfsr = None
best_degree = None

for degree in range(1, 27):
    # Build system of equations from known consecutive values
    equations = []
    rhs_vals = []
    
    for run_start, run_end in runs:
        run_len = run_end - run_start + 1
        if run_len <= degree:
            continue
        # Each position from run_start + degree to run_end gives one equation
        for pos in range(run_start + degree, run_end + 1):
            row = []
            for d in range(1, degree + 1):
                row.append(key_known[pos - d])
            equations.append(row)
            rhs_vals.append(key_known[pos])
    
    if len(equations) < degree:
        print(f"  Degree {degree}: not enough equations ({len(equations)} < {degree})")
        continue
    
    # Solve the system
    coeffs = gauss_solve_gf(equations, rhs_vals)
    
    if coeffs is None:
        print(f"  Degree {degree}: INCONSISTENT ({len(equations)} equations)")
        continue
    
    # Verify against ALL known positions (not just those used to build the system)
    # Generate full key from initial conditions using the LFSR
    # Need initial conditions: key[0]..key[degree-1]
    # But some of these might be unknown. Try to generate from known values.
    
    # First check: verify the coefficients against the training equations
    n_correct = 0
    n_total = 0
    for eq_idx, (row, target) in enumerate(zip(equations, rhs_vals)):
        predicted = sum(row[i] * coeffs[i] for i in range(degree)) % MOD
        if predicted == target:
            n_correct += 1
        n_total += 1
    
    if n_correct == n_total:
        print(f"  Degree {degree}: ALL {n_total} training equations satisfied! Coeffs: {coeffs}")
        
        # Now try to generate the FULL key
        # Start from the longest known run and extend in both directions
        # Find the longest run
        longest_run = max(runs, key=lambda r: r[1]-r[0]+1)
        lr_start, lr_end = longest_run
        
        # Initialize key from known values in the longest run
        full_key = [None] * KLEN
        for i in range(lr_start, lr_end + 1):
            full_key[i] = key_known[i]
        
        # Extend forward
        for i in range(lr_end + 1, KLEN):
            val = 0
            all_known = True
            for d in range(1, degree + 1):
                prev_idx = i - d
                if prev_idx < 0 or full_key[prev_idx] is None:
                    all_known = False
                    break
                val = (val + coeffs[d-1] * full_key[prev_idx]) % MOD
            if all_known:
                full_key[i] = val
        
        # Extend backward using the inverse recurrence
        # key[n-D] = (key[n] - sum(c_i * key[n-i], i=1..D-1)) / c_D (mod 29)
        # This requires c_D to be invertible
        if coeffs[degree-1] != 0:
            cD_inv = modinv(coeffs[degree-1])
            if cD_inv is not None:
                for i in range(lr_start - 1, -1, -1):
                    # key[i] from key[i+1], ..., key[i+D]
                    # key[i+D] = c1*key[i+D-1] + ... + cD*key[i]
                    # So: cD*key[i] = key[i+D] - c1*key[i+D-1] - ... - c(D-1)*key[i+1]
                    target_idx = i + degree
                    if target_idx >= KLEN or full_key[target_idx] is None:
                        continue
                    val = full_key[target_idx]
                    all_known = True
                    for d in range(1, degree):
                        check_idx = i + degree - d
                        if check_idx >= KLEN or full_key[check_idx] is None:
                            all_known = False
                            break
                        val = (val - coeffs[d-1] * full_key[check_idx]) % MOD
                    if all_known:
                        full_key[i] = (val * cD_inv) % MOD
        
        # Also try wrapping around (the LFSR is periodic with period 53)
        # So we can extend past KLEN and wrap indices
        for iteration in range(3):  # Multiple passes to fill gaps
            for i in range(KLEN):
                if full_key[i] is not None:
                    continue
                # Try forward relation
                val = 0
                all_known = True
                for d in range(1, degree + 1):
                    prev_idx = (i - d) % KLEN
                    if full_key[prev_idx] is None:
                        all_known = False
                        break
                    val = (val + coeffs[d-1] * full_key[prev_idx]) % MOD
                if all_known:
                    full_key[i] = val
                    continue
                
                # Try backward relation
                if coeffs[degree-1] != 0 and cD_inv is not None:
                    target_idx = (i + degree) % KLEN
                    if full_key[target_idx] is not None:
                        val = full_key[target_idx]
                        all_known = True
                        for d in range(1, degree):
                            check_idx = (i + degree - d) % KLEN
                            if full_key[check_idx] is None:
                                all_known = False
                                break
                            val = (val - coeffs[d-1] * full_key[check_idx]) % MOD
                        if all_known:
                            full_key[i] = (val * cD_inv) % MOD
        
        # Check how many positions filled
        filled = sum(1 for v in full_key if v is not None)
        print(f"    Generated {filled}/53 key values")
        
        # Verify against ALL originally confirmed values
        mismatches = 0
        for pos, val in confirmed.items():
            if full_key[pos] is not None and full_key[pos] != val:
                mismatches += 1
                print(f"    MISMATCH at pos {pos}: generated {full_key[pos]}, confirmed {val}")
        
        if mismatches == 0 and filled == KLEN:
            print(f"    *** FULL KEY RECOVERED WITH ZERO MISMATCHES! ***")
            best_lfsr = list(full_key)
            best_degree = degree
            break
        elif mismatches == 0:
            print(f"    Consistent so far ({filled}/53 filled, 0 mismatches)")
            if filled > (best_degree or 0):
                best_lfsr = list(full_key)
                best_degree = degree
    else:
        if n_total > 0:
            print(f"  Degree {degree}: {n_correct}/{n_total} correct")

if best_lfsr and all(v is not None for v in best_lfsr):
    print(f"\n{'='*80}")
    print(f"LFSR KEY FOUND! Degree {best_degree}")
    print(f"{'='*80}")
    
    key = best_lfsr
    print(f"Full key: {key}")
    print(f"Key (LAT): {''.join(LAT[v] for v in key)}")
    
    # Decrypt
    dec = [(cipher[i] - key[i % KLEN]) % MOD for i in range(N)]
    full_text = ''.join(LAT[v] for v in dec)
    
    # IoC
    counts = Counter(dec)
    ioc = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
    
    print(f"IoC*29: {ioc:.3f}")
    print(f"Text:\n{full_text}")
    
    # Word matches
    WORDLIST = set('A I THE AND OF TO IN IS IT THAT WAS FOR ON ARE WITH AS AT BE THIS FROM OR AN BY NOT BUT WHAT ALL HE SHE THEY WE YOU HIS HER ITS OUR THEIR WHO WHICH HAS HAD HAVE BEEN ONE DO IF NO MY UP SO THEM THEN INTO SOME THAN THERE THESE THOSE WHEN COULD WOULD OTHER MORE WILL SHALL FIND LEARN LIAR THIRD LENGTH PUBLIC'.split())
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals).upper()
        marker = "Y" if txt in WORDLIST else " "
        print(f"  {marker} w{wi}: '{txt}'")
else:
    print(f"\nNo complete LFSR key found. Trying extended approaches...")
    
    # Phase 2: Test with the PARTIAL LFSR key + hill-climbing for gaps
    if best_lfsr:
        print(f"\nBest partial LFSR (degree {best_degree}): {sum(1 for v in best_lfsr if v is not None)}/53 values")
        for i in range(KLEN):
            if best_lfsr[i] is not None:
                status = "confirmed" if i in confirmed else "PREDICTED"
                print(f"  key[{i}] = {best_lfsr[i]} ({LAT[best_lfsr[i]]}) [{status}]")
            else:
                print(f"  key[{i}] = ? [UNKNOWN]")

print(f"\n{'='*80}")
print(f"Phase 2: Autokey test")
print(f"{'='*80}")

# Autokey SUB: dec[i] = (cipher[i] - key_eff[i]) % 29
# where key_eff[i] = primer[i] for i < 53
# and key_eff[i] = dec[i - 53] for i >= 53
# So for i >= 53: dec[i] = (cipher[i] - dec[i-53]) % 29

# With 31 confirmed primer values, try autokey with partial primer
# Fill unknown primer values with frequency-analysis guess
eng_freq = [0.022,0.038,0.035,0.075,0.060,0.036,0.020,0.024,0.061,0.067,0.070,
            0.002,0.005,0.019,0.002,0.063,0.056,0.015,0.127,0.024,0.040,0.015,
            0.003,0.043,0.082,0.003,0.020,0.003,0.003]

# Test autokey with the confirmed keys as primer
primer = [0] * KLEN
for b, v in confirmed.items():
    primer[b] = v

# Fill unknown positions with frequency analysis
cols = [[] for _ in range(KLEN)]
for i in range(N): cols[i%KLEN].append(cipher[i])

for b in range(KLEN):
    if b in confirmed: continue
    best_shift = 0; best_score = -1
    for s in range(MOD):
        dec_col = [(v-s)%MOD for v in cols[b]]
        score = sum(eng_freq[v] for v in dec_col)
        if score > best_score: best_score = score; best_shift = s
    primer[b] = best_shift

# Test autokey SUB
dec_autokey = [0] * N
for i in range(N):
    if i < KLEN:
        dec_autokey[i] = (cipher[i] - primer[i]) % MOD
    else:
        dec_autokey[i] = (cipher[i] - dec_autokey[i - KLEN]) % MOD

counts = Counter(dec_autokey)
ioc_autokey = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
text_autokey = ''.join(LAT[v] for v in dec_autokey)
print(f"Autokey SUB IoC*29: {ioc_autokey:.3f}")
print(f"Text: {text_autokey[:200]}...")

# Test autokey ADD
dec_autokey_add = [0] * N
for i in range(N):
    if i < KLEN:
        dec_autokey_add[i] = (cipher[i] - primer[i]) % MOD
    else:
        dec_autokey_add[i] = (cipher[i] + dec_autokey_add[i - KLEN]) % MOD

counts = Counter(dec_autokey_add)
ioc_add = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
print(f"Autokey ADD IoC*29: {ioc_add:.3f}")

# Test autokey with KEY feedback (key_eff[i] = cipher[i-53] for i >= 53)
dec_cipher_fb = [0] * N
for i in range(N):
    if i < KLEN:
        key_val = primer[i]
    else:
        key_val = cipher[i - KLEN]
    dec_cipher_fb[i] = (cipher[i] - key_val) % MOD

counts = Counter(dec_cipher_fb)
ioc_cfb = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
print(f"Cipher feedback IoC*29: {ioc_cfb:.3f}")

print(f"\n{'='*80}")
print(f"Phase 3: Key as linear function of position")
print(f"{'='*80}")

# Test if key[i] = some polynomial in i modulo 29
# Degree 0: constant - clearly not, values differ
# Degree 1: key[i] = a*i + b mod 29
# Degree 2: key[i] = a*i^2 + b*i + c mod 29

for poly_deg in range(1, 6):
    # Build system from confirmed values
    matrix = []
    rhs = []
    for pos, val in sorted(confirmed.items()):
        row = [(pos**p) % MOD for p in range(poly_deg + 1)]
        matrix.append(row)
        rhs.append(val)
    
    # Solve
    if len(matrix) >= poly_deg + 1:
        coeffs = gauss_solve_gf(matrix[:poly_deg+1], rhs[:poly_deg+1])
        if coeffs:
            # Verify against ALL confirmed
            n_match = 0
            for pos, val in confirmed.items():
                predicted = sum(coeffs[p] * (pos**p) for p in range(poly_deg+1)) % MOD
                if predicted == val: n_match += 1
            print(f"  Poly degree {poly_deg}: {n_match}/{len(confirmed)} matches, coeffs={coeffs}")
        else:
            print(f"  Poly degree {poly_deg}: no solution")

print(f"\n{'='*80}")
print(f"Phase 4: Key as function of primes")
print(f"{'='*80}")

# Test key[i] = prime[i+offset] mod 29
def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(n+1) if is_prime[i]]

primes = sieve_primes(10000)

for offset in range(200):
    if offset + KLEN > len(primes): break
    match = 0
    for pos, val in confirmed.items():
        if primes[pos + offset] % MOD == val:
            match += 1
    if match > len(confirmed) * 0.3:  # More than 30% match
        print(f"  Offset {offset}: {match}/{len(confirmed)} matches (primes mod 29)")

# Test key[i] = totient(prime[i+offset]) mod 29
def totient(n):
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

for offset in range(200):
    if offset + KLEN > len(primes): break
    match = 0
    for pos, val in confirmed.items():
        if totient(primes[pos + offset]) % MOD == val:
            match += 1
    if match > len(confirmed) * 0.3:
        print(f"  Offset {offset}: {match}/{len(confirmed)} matches (totient mod 29)")

# Test key[i] = cumulative sum of primes mod 29
cumsum = [0]
for p in primes:
    cumsum.append((cumsum[-1] + p) % MOD)

for offset in range(200):
    if offset + KLEN >= len(cumsum): break
    match = 0
    for pos, val in confirmed.items():
        if cumsum[pos + offset] == val:
            match += 1
    if match > len(confirmed) * 0.3:
        print(f"  Offset {offset}: {match}/{len(confirmed)} matches (cumsum primes mod 29)")

print(f"\n=== DONE ===")
