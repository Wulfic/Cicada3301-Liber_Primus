"""Comprehensive attack v3:
1. BM-22 LFSR extension from P19 key stream → decrypt P19 remainder + cross-page
2. Single-rune word constraint attack (each 1-rune word = I(10) or A(24))
3. Key length 53 Vigenère on P18
4. P20 non-prime stream shift analysis
5. Key stream mathematical pattern search
"""
import os, sys, itertools
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
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                runes = [GP[c] for c in raw if c in GP]
                # Get word structure with positions
                words = []
                pos = 0
                current = []
                start = pos
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
    return None, None

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1))

def modinv(a, m=29):
    if a == 0: return None
    g, x, _ = _egcd(a % m, m)
    if g != 1: return None
    return x % m

def _egcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = _egcd(b % a, a)
    return g, y - (b // a) * x, x

def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def berlekamp_massey(seq, mod=29):
    n = len(seq)
    C = [1]
    B = [1]
    L = 0; m = 1; b = 1
    for i in range(n):
        d = seq[i]
        for j in range(1, len(C)):
            if i - j >= 0:
                d = (d + C[j] * seq[i - j]) % mod
        if d == 0:
            m += 1
        else:
            T = list(C)
            inv_b = modinv(b, mod)
            if inv_b is None: m += 1; continue
            coeff = (mod - d * inv_b % mod) % mod
            while len(C) < len(B) + m: C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] + coeff * B[j]) % mod
            if 2 * L <= i:
                L = i + 1 - L; B = T; b = d; m = 1
            else:
                m += 1
    return L, C

def lfsr_extend(C, seed, length, mod=29):
    """Extend LFSR sequence given connection polynomial and seed."""
    seq = list(seed)
    L = len(C) - 1  # degree
    while len(seq) < length:
        val = 0
        for j in range(1, L + 1):
            if len(seq) - j >= 0:
                val = (val - C[j] * seq[len(seq) - j]) % mod
        seq.append(val)
    return seq

def count_english_words(text_str):
    """Count occurrences of common English/OE words."""
    common = {'THE','AND','OF','TO','IN','IS','IT','THAT','WAS','FOR','ON','ARE','WITH',
              'AS','AT','BE','THIS','FROM','OR','AN','BY','NOT','BUT','WHAT','ALL','WERE',
              'WHEN','WE','THERE','CAN','BEEN','HAS','HER','ONE','OUR','OUT','YOU','HAD',
              'HIS','THEIR','WILL','EACH','MAKE','HOW','THEM','THEN','THAN','ITS','HIM',
              'SOME','INTO','HER','TWO','WAY','COULD','NO','MY','DO','DID','GET','HAS',
              'HAVE','HE','SHE','THEY','WHO','IF','SO','UP','ABOUT','WHICH','GO','ME',
              'SEE','KNOW','JUST','ALSO','COME','LIKE','TIME','VERY','YOUR','OVER','SUCH',
              'A','I','WITHIN','PATH','DEEP','WEB'}
    words = text_str.upper().split()
    return sum(1 for w in words if w in common)

PRIMES = primes_up_to(100000)

# === Load all unsolved pages ===
print("Loading unsolved pages...")
pages = {}
for pg in range(18, 55):
    runes, words = load_page(pg)
    if runes:
        pages[pg] = {'runes': runes, 'words': words, 'n': len(runes)}
        # Find single-rune words and their stream positions
        single_rune = [(start, word[0]) for start, word in words if len(word) == 1]
        pages[pg]['singles'] = single_rune
        
print(f"Loaded {len(pages)} pages")

# === P19 data ===
KNOWN_PLAIN_19 = [4,18,24,4,4,24,21,10,21,2,18,13,4,10,19,18,15,9,1,19,17,18,4,15,7,10,20,20,15,8,3,7,24,13,24,2,16,3,2,18,23,12,4]
cipher19 = pages[19]['runes']
key_stream_43 = [(KNOWN_PLAIN_19[i] - cipher19[i]) % 29 for i in range(43)]

# =====================================================================
# ATTACK 1: BM-22 LFSR extension on P19
# =====================================================================
print("\n" + "="*80)
print("ATTACK 1: Berlekamp-Massey LFSR extension (L=22)")
print("="*80)

L, C = berlekamp_massey(key_stream_43)
print(f"BM complexity: {L}, polynomial degree: {len(C)-1}")

# Extend to enough length for largest page
max_len = max(p['n'] for p in pages.values()) + 10000
ext_key = lfsr_extend(C, key_stream_43, max_len)

# Verify: first 43 should match
assert ext_key[:43] == key_stream_43, "LFSR extension doesn't match seed!"

# Decrypt P19 remainder
plain19 = [(cipher19[i] + ext_key[i]) % 29 for i in range(len(cipher19))]
ic19 = ioc(plain19) * 29
words19_dec = []
for start, word in pages[19]['words']:
    word_dec = [plain19[start + j] for j in range(len(word))]
    words19_dec.append(''.join(LAT[v] for v in word_dec))
print(f"\nP19 full with BM-22 LFSR: IoC*29 = {ic19:.3f}")
print(f"Words: {' '.join(words19_dec[:25])}")

# If P19 remainder looks good, also try on other pages
# Try different offsets of the extended key stream on all pages
hit_count = 0
for pg_num, pg_data in sorted(pages.items()):
    if pg_num == 19: continue
    n = pg_data['n']
    best_ic = 0
    best_off = 0
    best_mode = ''
    
    for offset in range(0, min(2000, max_len - n)):
        key = ext_key[offset:offset+n]
        for mode_name, fn in [("ADD", lambda c,k: (c+k)%29), ("SUB", lambda c,k: (c-k)%29)]:
            dec = [fn(pg_data['runes'][i], key[i]) for i in range(n)]
            ic_val = ioc(dec) * 29
            if ic_val > best_ic:
                best_ic = ic_val
                best_off = offset
                best_mode = mode_name
    
    if best_ic > 1.3:
        key = ext_key[best_off:best_off+n]
        if best_mode == "ADD":
            dec = [(pg_data['runes'][i] + key[i]) % 29 for i in range(n)]
        else:
            dec = [(pg_data['runes'][i] - key[i]) % 29 for i in range(n)]
        text = ''.join(LAT[v] for v in dec[:80])
        print(f"  *** P{pg_num:02d} off={best_off} {best_mode}: IoC*29={best_ic:.3f} | {text[:60]}")
        hit_count += 1
    
if hit_count == 0:
    print("  No pages showed IoC > 1.3 with BM-22 extended key stream (offsets 0-2000)")

# =====================================================================
# ATTACK 2: Single-rune word constraint attack
# =====================================================================
print("\n" + "="*80)
print("ATTACK 2: Single-rune word constraints")
print("="*80)

for pg_num, pg_data in sorted(pages.items()):
    singles = pg_data['singles']
    if len(singles) < 3: continue
    
    n_singles = len(singles)
    cipher = pg_data['runes']
    n = pg_data['n']
    
    print(f"\nP{pg_num:02d}: {n} runes, {n_singles} single-rune words")
    for pos, val in singles[:10]:
        # If plaintext = I(10): key = (val - 10) % 29 = (cipher[pos] - 10) % 29
        # If plaintext = A(24): key = (val - 24) % 29 = (cipher[pos] - 24) % 29
        kI_add = (val - 10) % 29  # for ADD mode
        kA_add = (val - 24) % 29
        kI_sub = (10 - val) % 29  # for SUB mode
        kA_sub = (24 - val) % 29
        print(f"  pos={pos:4d} cipher={val:2d}({LAT[val]:3s}) | ADD: key_if_I={kI_add:2d} key_if_A={kA_add:2d} | SUB: key_if_I={kI_sub:2d} key_if_A={kA_sub:2d}")
    
    # For each candidate key length, check consistency
    # Test key lengths from community hints (primes up to 100)
    candidate_klens = [k for k in PRIMES if 2 <= k <= 200]
    
    best_klen_results = []
    
    for klen in candidate_klens:
        # Group singles by position mod klen
        groups = {}
        for pos, val in singles:
            bucket = pos % klen
            if bucket not in groups:
                groups[bucket] = []
            groups[bucket].append((pos, val))
        
        # For ADD mode: key[pos%klen] = (cipher[pos] - plain[pos]) % 29
        # Each single can be I(10) or A(24), so key = (cipher - 10) or (cipher - 24) % 29
        # Check if any bucket has >1 singles with a consistent key value
        
        for mode_name, key_fn_I, key_fn_A in [
            ("ADD", lambda v: (v-10)%29, lambda v: (v-24)%29),
            ("SUB", lambda v: (10-v)%29, lambda v: (24-v)%29),
            ("BEAUFORT", lambda v: (v-10)%29, lambda v: (v-24)%29),
        ]:
            consistent_any = True  # Can ALL buckets have at least one consistent assignment?
            n_constrained = 0
            n_consistent = 0
            determined_keys = {}  # bucket -> set of possible key values
            
            for bucket, items in groups.items():
                if len(items) == 1:
                    # Single entry: two possible key values
                    v = items[0][1]
                    determined_keys[bucket] = {key_fn_I(v), key_fn_A(v)}
                    n_constrained += 1
                    n_consistent += 1
                else:
                    # Multiple entries: find key values consistent with all entries
                    possible_keys = set(range(29))
                    for pos, v in items:
                        entry_keys = {key_fn_I(v), key_fn_A(v)}
                        possible_keys &= entry_keys
                    
                    if possible_keys:
                        determined_keys[bucket] = possible_keys
                        n_constrained += len(items)
                        n_consistent += len(items)
                    else:
                        # Check if any consistent I/A assignment exists
                        # For 2 entries: 4 combos; for 3: 8 combos; etc.
                        found = False
                        for assignment in itertools.product([10, 24], repeat=len(items)):
                            keys = set()
                            for (pos, v), plain in zip(items, assignment):
                                if plain == 10:
                                    keys.add(key_fn_I(v))
                                else:
                                    keys.add(key_fn_A(v))
                            if len(keys) == 1:
                                determined_keys[bucket] = keys
                                n_constrained += len(items)
                                n_consistent += len(items)
                                found = True
                                break
                        if not found:
                            consistent_any = False
                            n_constrained += len(items)
            
            if n_constrained >= 3 and consistent_any:
                # All constraints satisfied! Try to decrypt
                # For buckets with single determined key, use it
                # For buckets with 2 possible keys, try both
                
                # Quick check: how many buckets are fully determined (1 key)?
                fully_determined = sum(1 for k, v in determined_keys.items() if len(v) == 1)
                total_buckets = len(determined_keys)
                
                if fully_determined >= 3 or (n_singles >= 5 and total_buckets >= 3):
                    best_klen_results.append({
                        'klen': klen,
                        'mode': mode_name,
                        'n_consistent': n_consistent,
                        'n_constrained': n_constrained,
                        'fully_det': fully_determined,
                        'total_buckets': total_buckets,
                        'keys': determined_keys
                    })
    
    # Sort by utility: more fully determined keys is better
    best_klen_results.sort(key=lambda x: (-x['fully_det'], -x['n_consistent']))
    
    if best_klen_results:
        print(f"  Top consistent key lengths:")
        for r in best_klen_results[:5]:
            print(f"    klen={r['klen']:3d} {r['mode']:8s} fully_det={r['fully_det']}/{r['total_buckets']} buckets, {r['n_consistent']}/{r['n_constrained']} singles consistent")
    else:
        print(f"  No consistent key lengths found (all have contradictions)")

# =====================================================================
# ATTACK 3: Key length 53 on P18
# =====================================================================
print("\n" + "="*80)
print("ATTACK 3: Vigenère key length 53 on P18")
print("="*80)

if 18 in pages:
    p18 = pages[18]
    c18 = p18['runes']
    n18 = p18['n']
    print(f"P18: {n18} runes")
    
    # With key length 53, we can do frequency analysis on each column
    klen = 53
    columns = [[] for _ in range(klen)]
    for i in range(n18):
        columns[i % klen].append(c18[i])
    
    # For each column, find the shift that maximizes fit to English GP distribution
    # English GP distribution from solved pages (approximate):
    # The most common runes in solved English GP text
    # A(24), E(18), T(16), N(9), I(10), O(3), S(15), H(8), R(4) are frequent
    # Using expected frequencies for GP-encoded English
    eng_freq_29 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    # Let me derive from the known solved text frequencies
    # Use a simpler metric: IoC of the column (should be high if klen is correct)
    col_iocs = []
    for col in columns:
        if len(col) >= 2:
            col_iocs.append(ioc(col) * 29)
    
    avg_ioc = sum(col_iocs) / len(col_iocs) if col_iocs else 0
    print(f"  Key length 53: avg column IoC*29 = {avg_ioc:.3f}")
    print(f"  (English ≈ 1.7, random ≈ 1.0)")
    
    if avg_ioc > 1.2:
        print(f"  PROMISING! Above random threshold")
        # Find best shift per column
        for mode_name in ['SUB', 'ADD']:
            key = []
            for col_idx, col in enumerate(columns):
                best_shift = 0
                best_ic = 0
                for shift in range(29):
                    if mode_name == 'SUB':
                        dec_col = [(v - shift) % 29 for v in col]
                    else:
                        dec_col = [(v + shift) % 29 for v in col]
                    # Use single-letter frequency as metric: maximize A, E, T 
                    score = sum(1 for v in dec_col if v in {24, 18, 16, 9, 10, 3, 15, 8, 4})
                    if score > best_ic:
                        best_ic = score
                        best_shift = shift
                key.append(best_shift)
            
            # Decrypt with this key
            dec = [(c18[i] - key[i%klen]) % 29 if mode_name == 'SUB' else (c18[i] + key[i%klen]) % 29 for i in range(n18)]
            full_ic = ioc(dec) * 29
            text = ''.join(LAT[v] for v in dec[:100])
            words_dec = []
            for start, word in p18['words']:
                wd = [dec[start+j] for j in range(len(word))]
                words_dec.append(''.join(LAT[v] for v in wd))
            print(f"  {mode_name} best-shift: IoC*29={full_ic:.3f}")
            print(f"  Text: {text[:80]}")
            print(f"  Words: {' '.join(words_dec[:15])}")
    else:
        print(f"  NOT promising (avg IoC near random)")
    
    # Also try other prime key lengths
    print(f"\n  Scanning all prime key lengths 2-150:")
    klen_results = []
    for kl in [k for k in PRIMES if 2 <= k <= 150]:
        cols = [[] for _ in range(kl)]
        for i in range(n18):
            cols[i % kl].append(c18[i])
        ic_avg = sum(ioc(c)*29 for c in cols if len(c) >= 2) / sum(1 for c in cols if len(c) >= 2)
        klen_results.append((ic_avg, kl))
    
    klen_results.sort(reverse=True)
    print(f"  Top 15 key lengths by avg column IoC*29:")
    for ic_val, kl in klen_results[:15]:
        print(f"    klen={kl:3d}: avg IoC*29 = {ic_val:.4f}")

# =====================================================================
# ATTACK 4: P20 shift analysis on non-prime stream
# =====================================================================
print("\n" + "="*80)
print("ATTACK 4: P20 non-prime stream shift analysis")
print("="*80)

if 20 in pages:
    p20 = pages[20]
    c20 = p20['runes']
    n20 = p20['n']
    
    prime_vals = set(PRIMES[:10])  # {2,3,5,7,11,13,17,19,23,29} intersect {0..28}
    prime_vals = {v for v in prime_vals if v < 29}  # {2,3,5,7,11,13,17,19,23}
    
    # Split into prime-value and non-prime-value positions
    np_stream = [(i, c20[i]) for i in range(n20) if c20[i] not in prime_vals]
    np_vals = [v for _, v in np_stream]
    
    print(f"P20: {n20} total runes, {len(np_vals)} non-prime-value runes")
    
    # Try shifts -10 to +10
    for shift in range(-14, 15):
        shifted = [(v + shift) % 29 for v in np_vals]
        ic_val = ioc(shifted) * 29
        text = ''.join(LAT[v] for v in shifted[:60])
        
        # Count THE, AND, etc.
        # Build words from shifted values using the original word structure
        # Actually, the non-prime stream is interleaved, so word boundaries don't directly apply
        # Let's just count 3-grams that spell common words
        trigrams = {}
        for i in range(len(shifted) - 2):
            tri = (shifted[i], shifted[i+1], shifted[i+2])
            trigrams[tri] = trigrams.get(tri, 0) + 1
        
        # THE = T(16), H(8), E(18)
        the_count = trigrams.get((16, 8, 18), 0)
        # AND = A(24), N(9), D(23)
        and_count = trigrams.get((24, 9, 23), 0)
        
        if the_count > 2 or and_count > 1 or ic_val > 1.5:
            print(f"  shift={shift:+3d}: IoC*29={ic_val:.3f} THE={the_count} AND={and_count} | {text[:50]}")
    
    # Now try: what if BOTH streams need shift?
    p_stream = [(i, c20[i]) for i in range(n20) if c20[i] in prime_vals]
    p_vals = [v for _, v in p_stream]
    
    print(f"\n  Prime-value stream: {len(p_vals)} runes")
    # The prime values are {2,3,5,7,11,13,17,19,23}
    # If we map these to sequential 0-8, what's the IoC?
    prime_list = sorted(prime_vals)
    prime_map = {p: i for i, p in enumerate(prime_list)}
    mapped = [prime_map[v] for v in p_vals]
    ic_mapped = ioc(mapped) * 9  # normalize to 9-letter alphabet
    print(f"  Mapped prime values IoC*9: {ic_mapped:.3f} (random=1.0)")
    
    # What if the prime-value runes encode a different message using only 9 symbols?
    # This could be a substitution cipher over a 9-symbol alphabet
    # Try: each prime maps to one of the 9 most common English letters
    # Most common in English: E, T, A, O, I, N, S, H, R
    # In GP: E=18, T=16, A=24, O=3, I=10, N=9, S=15, H=8, R=4

# =====================================================================
# ATTACK 5: Mathematical patterns in P19 key stream
# =====================================================================
print("\n" + "="*80)
print("ATTACK 5: Key stream pattern analysis")
print("="*80)

ks = key_stream_43
print(f"Key stream: {ks}")

# Check: key[i] = f(prime[i]) mod 29 for various f
print("\nChecking key[i] vs prime[i] relationships:")
for name, fn in [
    ("prime[i] mod 29", lambda i: PRIMES[i] % 29),
    ("prime[i+1] mod 29", lambda i: PRIMES[i+1] % 29),
    ("prime[i]*2 mod 29", lambda i: (PRIMES[i]*2) % 29),
    ("prime[i]*3 mod 29", lambda i: (PRIMES[i]*3) % 29),
    ("prime[i]^2 mod 29", lambda i: (PRIMES[i]**2) % 29),
    ("(prime[i]+prime[i+1]) mod 29", lambda i: (PRIMES[i]+PRIMES[i+1]) % 29),
    ("prime[i]*prime[i+1] mod 29", lambda i: (PRIMES[i]*PRIMES[i+1]) % 29),
    ("cumsum_prime[i] mod 29", lambda i: sum(PRIMES[:i+1]) % 29),
    ("(prime[i]-1) mod 29", lambda i: (PRIMES[i]-1) % 29),
    ("pow(2,i,29)", lambda i: pow(2,i,29)),
    ("pow(3,i,29)", lambda i: pow(3,i,29)),
    ("pow(5,i,29)", lambda i: pow(5,i,29)),
    ("pow(7,i,29)", lambda i: pow(7,i,29)),
    ("pow(11,i,29)", lambda i: pow(11,i,29)),
    ("pow(13,i,29)", lambda i: pow(13,i,29)),
    ("pow(17,i,29)", lambda i: pow(17,i,29)),
    ("pow(19,i,29)", lambda i: pow(19,i,29)),
    ("i*i mod 29", lambda i: (i*i) % 29),
    ("i*(i+1)/2 mod 29", lambda i: (i*(i+1)//2) % 29),
    ("fibonacci(i) mod 29", lambda i: _fib(i) % 29),
]:
    gen = [fn(i) for i in range(43)]
    matches = sum(1 for i in range(43) if gen[i] == ks[i])
    if matches >= 5:
        print(f"  {name}: {matches}/43 matches")
        # Show first few
        diffs = [(ks[i] - gen[i]) % 29 for i in range(10)]
        print(f"    diff[:10]: {diffs}")

# Also check: key[i] = (some_constant + f(i)) mod 29
print("\nChecking key[i] = (C + f(i)) mod 29:")
for name, fn in [
    ("prime[i]", lambda i: PRIMES[i] % 29),
    ("cumsum_prime[i]", lambda i: sum(PRIMES[:i+1]) % 29),
    ("i*i", lambda i: (i*i) % 29),
    ("(i+1)*(i+2)/2", lambda i: ((i+1)*(i+2)//2) % 29),
]:
    for C in range(29):
        gen = [(C + fn(i)) % 29 for i in range(43)]
        matches = sum(1 for i in range(43) if gen[i] == ks[i])
        if matches >= 8:
            print(f"  C={C} + {name}: {matches}/43 matches")

# Check key[i] = (A * f(i) + B) mod 29 for various A, B
print("\nChecking key[i] = (A * prime[i] + B) mod 29:")
for A in range(1, 29):
    for B in range(29):
        gen = [(A * PRIMES[i] + B) % 29 for i in range(43)]
        matches = sum(1 for i in range(43) if gen[i] == ks[i])
        if matches >= 6:
            print(f"  A={A}, B={B}: {matches}/43 matches")
            break  # Just show first B for each A that works

def _fib(n):
    if n <= 0: return 0
    if n == 1: return 1
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a+b
    return b

# =====================================================================
# ATTACK 6: Try known cipher text patterns
# =====================================================================
print("\n" + "="*80)  
print("ATTACK 6: Known plaintext cribs on all pages")
print("="*80)

# Common Liber Primus phrases that might appear
cribs = [
    # "AN END" = A(24),N(9),E(18),N(9),D(23)
    [24, 9, 18, 9, 23],
    # "THE" = T(16),H(8),E(18)
    [16, 8, 18],
    # "WITHIN" = W(7),I(10),TH(2),I(10),N(9)
    [7, 10, 2, 10, 9],
    # "CONSUMPTION" = C(5),O(3),N(9),S(15),U(1),M(19),P(13),T(16),I(10),O(3),N(9)
    [5, 3, 9, 15, 1, 19, 13, 16, 10, 3, 9],
    # "WISDOM" = W(7),I(10),S(15),D(23),O(3),M(19)
    [7, 10, 15, 23, 3, 19],
    # "PRIME" = P(13),R(4),I(10),M(19),E(18)
    [13, 4, 10, 19, 18],
    # "DEOR" = D(23),EO(12),R(4)
    [23, 12, 4],
]

for pg_num, pg_data in sorted(pages.items()):
    cipher = pg_data['runes']
    n = pg_data['n']
    
    for crib in cribs:
        crib_len = len(crib)
        for pos in range(n - crib_len + 1):
            for mode in ['SUB', 'ADD']:
                if mode == 'SUB':
                    key_vals = [(cipher[pos+j] - crib[j]) % 29 for j in range(crib_len)]
                else:
                    key_vals = [(crib[j] - cipher[pos+j]) % 29 for j in range(crib_len)]
                
                # Check if key_vals could be part of some pattern
                # Simple: all same (Caesar)
                if len(set(key_vals)) == 1:
                    shift = key_vals[0]
                    dec_full = [(cipher[i] - shift) % 29 if mode == 'SUB' else (cipher[i] + shift) % 29 for i in range(n)]
                    ic_val = ioc(dec_full) * 29
                    if ic_val > 1.3:
                        text = ''.join(LAT[v] for v in dec_full[:60])
                        crib_text = ''.join(LAT[v] for v in crib)
                        print(f"  P{pg_num:02d} pos={pos} {mode} shift={shift}: IoC={ic_val:.3f} crib={crib_text} | {text[:50]}")

print("\n=== DONE ===")
