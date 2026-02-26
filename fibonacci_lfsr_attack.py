#!/usr/bin/env python3
"""
Fibonacci-spiral prime ordering + LFSR keystream attack on Liber Primus.
Tests genuinely novel approaches based on page 15 grid discovery.
"""
import sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GP_RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GP_NAMES = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}

def sieve_primes(n):
    """Generate primes up to n."""
    if n < 2: return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

def nth_prime(n):
    """Get the n-th prime (0-indexed: nth_prime(0)=2)."""
    if n < 0: return 2
    limit = max(100, int(n * 15))
    primes = sieve_primes(limit)
    while len(primes) <= n:
        limit *= 2
        primes = sieve_primes(limit)
    return primes[n]

def load_page(page_num):
    """Load runes from a page file."""
    base = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"
    path = os.path.join(base, f"page_{page_num:02d}", "runes.txt")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    runes = [RUNE_TO_IDX[c] for c in text if c in RUNE_TO_IDX]
    return runes

def ioc(values):
    if len(values) < 2: return 0.0
    from collections import Counter
    c = Counter(values)
    n = len(values)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1) / 29.0) if n > 1 else 0

def decrypt(cipher, key, mode):
    """Decrypt using ADD, SUB, or BEAUFORT mode."""
    result = []
    for i, c in enumerate(cipher):
        k = key[i % len(key)] if isinstance(key, (list, tuple)) else key[i]
        if mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'beaufort':
            result.append((k - c) % 29)
    return result

def decrypt_stream(cipher, keystream, mode):
    """Decrypt with a non-repeating keystream."""
    result = []
    for i in range(min(len(cipher), len(keystream))):
        c = cipher[i]
        k = keystream[i]
        if mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'beaufort':
            result.append((k - c) % 29)
    return result

def decrypt_fskip(cipher, keystream, mode):
    """Decrypt with F-skip: when cipher rune=0 (F), output 0 and don't advance key."""
    result = []
    ki = 0
    for c in cipher:
        if c == 0:
            result.append(0)
        else:
            if ki >= len(keystream):
                break
            k = keystream[ki]
            if mode == 'add':
                result.append((c + k) % 29)
            elif mode == 'sub':
                result.append((c - k) % 29)
            elif mode == 'beaufort':
                result.append((k - c) % 29)
            ki += 1
    return result

def vals_to_text(vals):
    return ''.join(GP_NAMES[v] for v in vals)

def word_score(vals):
    """Simple English word scoring."""
    text = vals_to_text(vals).upper()
    score = 0
    words = ["THE","AND","FOR","ARE","BUT","NOT","YOU","ALL","CAN","HER","WAS","ONE","OUR",
             "OUT","HIS","HAS","ITS","WHO","OIL","SIT","NOW","OLD","DID","GET","HAS","HIM",
             "HOW","MAN","NEW","WAY","MAY","DAY","TOO","ANY","THAT","WITH","HAVE","THIS",
             "WILL","YOUR","FROM","THEY","BEEN","CALL","SOME","INTO","TIME","VERY",
             "WHEN","COME","MAKE","LIKE","LONG","OVER","SUCH","TAKE","THAN","THEM","GOOD",
             "KNOW","WELL","THEN","MOST","ONLY","TELL","ALSO","BACK","WOULD","THERE","THEIR",
             "WHAT","ABOUT","WHICH","COULD","OTHER","WERE","MORE","AFTER","THOSE","THINK",
             "SHOULD","THESE","PEOPLE","BECAUSE","SACRED","PRIME","PRIMES","TOTIENT","DIVINITY",
             "CIRCUMFERENCE","WISDOM","LOSS","VOID","EMERGENCE","TRUTH","PATH","LIGHT","DARKNESS",
             "KNOW","SELF","CONSCIOUSNESS","BEING","NUMBER","NUMBERS","FUNCTION","ENCRYPT"]
    for w in words:
        if w in text:
            score += len(w)
    return score

# Generate large prime list
ALL_PRIMES = sieve_primes(200000)
PRIME_SET = set(ALL_PRIMES)

# Load all unsolved pages
PAGES = {}
for pn in range(17, 55):
    data = load_page(pn)
    if data:
        PAGES[pn] = data

print(f"Loaded {len(PAGES)} unsolved pages")

# ============================================================================
# SECTION 1: Fibonacci-indexed primes as keystream
# ============================================================================
print("\n" + "="*80)
print("SECTION 1: Fibonacci-indexed primes as keystream")
print("="*80)

# Generate Fibonacci numbers
def fibonacci_seq(n):
    fibs = [0, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

fibs = fibonacci_seq(40)  # 0,1,1,2,3,5,8,13,21,34,55,89,...

# Method A: Use primes at Fibonacci indices
# p_0=2, p_1=3, p_1=3, p_2=5, p_3=7, p_5=13, p_8=23, p_13=43, ...
fib_primes = []
for f in fibs[:30]:
    fib_primes.append(nth_prime(f))

print(f"Fibonacci-indexed primes: {fib_primes[:20]}")
print(f"  mod 29: {[p % 29 for p in fib_primes[:20]]}")
print(f"  totient mod 29: {[(p-1) % 29 for p in fib_primes[:20]]}")

# Test both prime mod 29 and totient mod 29 as keystreams
keystreams = {
    'fib_prime_mod29': [p % 29 for p in fib_primes],
    'fib_totient_mod29': [(p-1) % 29 for p in fib_primes],
    'fib_prime_gp': [GP_PRIMES.index(p) if p in GP_PRIMES else p % 29 for p in fib_primes],
}

# Also generate enough primes for position-indexed Fibonacci
fib_primes_long = []
for f in fibonacci_seq(50)[:40]:
    fib_primes_long.append(nth_prime(min(f, 10000)))

keystreams['fib_prime_long_mod29'] = [p % 29 for p in fib_primes_long]
keystreams['fib_totient_long_mod29'] = [(p-1) % 29 for p in fib_primes_long]

# Method B: Page 15 spiral order specifically
# The grid spiral gives Fibonacci order: 0,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987
# These are the ORDINAL positions of primes. The primes at those positions are:
spiral_fibs = [0,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987]
spiral_primes = [nth_prime(f) for f in spiral_fibs]
print(f"\nSpiral-ordered primes: {spiral_primes}")
print(f"  mod 29: {[p % 29 for p in spiral_primes]}")

keystreams['spiral_primes_mod29'] = [p % 29 for p in spiral_primes]
keystreams['spiral_totient_mod29'] = [(p-1) % 29 for p in spiral_primes]

# Method C: Use Fibonacci numbers themselves as the keystream
keystreams['fibonacci_mod29'] = [f % 29 for f in fibonacci_seq(50)]
keystreams['fibonacci_totient_mod29'] = [(f - 1) % 29 for f in fibonacci_seq(50) if f > 0]

best_results = []
modes = ['add', 'sub', 'beaufort']
test_pages = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]

for ks_name, ks in keystreams.items():
    for pn in test_pages:
        if pn not in PAGES: continue
        cipher = PAGES[pn]
        for mode in modes:
            plain = decrypt_stream(cipher, ks, mode)
            if len(plain) < 10: continue
            ic = ioc(plain)
            ws = word_score(plain)
            if ic > 1.25 or ws > 20:
                best_results.append((ic, ws, pn, ks_name, mode, plain[:30]))
            # Also try with F-skip
            plain_fs = decrypt_fskip(cipher, ks, mode)
            if len(plain_fs) < 10:
                continue
            ic_fs = ioc(plain_fs)
            ws_fs = word_score(plain_fs)
            if ic_fs > 1.25 or ws_fs > 20:
                best_results.append((ic_fs, ws_fs, pn, ks_name+"_fskip", mode, plain_fs[:30]))

best_results.sort(reverse=True)
print(f"\nResults above threshold: {len(best_results)}")
for ic, ws, pn, ks_name, mode, plain in best_results[:20]:
    print(f"  P{pn} {ks_name}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 2: P56-style totient stream from different starting primes
# ============================================================================
print("\n" + "="*80)
print("SECTION 2: Totient stream from different starting primes")
print("="*80)

# P56 uses sequential primes starting from 2: key[i] = (prime[i] - 1) % 29
# What if other pages start from a DIFFERENT prime?
# E.g., page N might start from the N-th prime, or from prime(N*29), etc.

best2 = []
# Test starting from prime at index 0 through 500
for start_idx in range(0, 500):
    key = [(ALL_PRIMES[start_idx + i] - 1) % 29 for i in range(2000)]
    for pn in test_pages:
        if pn not in PAGES: continue
        cipher = PAGES[pn]
        n = len(cipher)
        if start_idx + n > len(ALL_PRIMES): break
        for mode in modes:
            plain = decrypt_stream(cipher, key, mode)
            ic = ioc(plain)
            if ic > 1.30:
                ws = word_score(plain)
                best2.append((ic, ws, pn, f"tot_start={start_idx}(p={ALL_PRIMES[start_idx]})", mode, plain[:30]))
            # F-skip
            plain_fs = decrypt_fskip(cipher, key, mode)
            if len(plain_fs) >= 10:
                ic_fs = ioc(plain_fs)
                if ic_fs > 1.30:
                    ws_fs = word_score(plain_fs)
                    best2.append((ic_fs, ws_fs, pn, f"tot_start={start_idx}(p={ALL_PRIMES[start_idx]})_fskip", mode, plain_fs[:30]))

best2.sort(reverse=True)
print(f"\nResults above IoC 1.30: {len(best2)}")
for ic, ws, pn, desc, mode, plain in best2[:20]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 3: LFSR keystream generation
# ============================================================================
print("\n" + "="*80)
print("SECTION 3: LFSR keystream generation")
print("="*80)

def lfsr_keystream(taps, init_state, length, nbits=5):
    """Generate LFSR keystream mod 29.
    taps: list of bit positions that feed back (0-indexed from MSB)
    init_state: initial register value
    length: number of mod-29 values to generate
    nbits: register width
    """
    state = init_state & ((1 << nbits) - 1)
    if state == 0:
        state = 1
    keystream = []
    bits = []
    for _ in range(length * nbits + nbits * 10):
        bits.append(state & 1)
        feedback = 0
        for t in taps:
            feedback ^= (state >> t) & 1
        state = ((state >> 1) | (feedback << (nbits - 1))) & ((1 << nbits) - 1)
    
    # Convert bits to mod-29 values
    for i in range(0, len(bits) - nbits + 1, nbits):
        val = 0
        for j in range(nbits):
            val = (val << 1) | bits[i + j]
        keystream.append(val % 29)
        if len(keystream) >= length:
            break
    return keystream

# Test various LFSR configurations
# Focus on smaller registers that could produce useful keystreams
best3 = []
target_pages = [17, 18, 19, 20, 21, 22, 24, 25, 26, 29, 32, 43, 44, 50, 54]

print("Testing LFSR with 5-bit registers...")
for nbits in [5, 6, 7]:
    max_taps = nbits
    # Generate all 2-tap polynomials
    for t1 in range(max_taps):
        for t2 in range(t1 + 1, max_taps):
            taps = [t1, t2]
            for init in [1, 3, 7, 13, 17, 23, 29]:
                ks = lfsr_keystream(taps, init, 2000, nbits)
                if len(ks) < 50: continue
                for pn in target_pages:
                    if pn not in PAGES: continue
                    cipher = PAGES[pn]
                    for mode in modes:
                        plain = decrypt_stream(cipher, ks, mode)
                        ic = ioc(plain)
                        if ic > 1.30:
                            ws = word_score(plain)
                            best3.append((ic, ws, pn, f"LFSR({nbits}bit,taps={taps},init={init})", mode, plain[:30]))

print(f"  5-7 bit results: {len(best3)}")

# Also test with prime-derived LFSR polynomials
# Missing primes hypothesis: 73-1223 (about 200 primes missing from telnet)
# These could define tap positions
print("Testing LFSR with prime-derived taps...")
prime_taps_candidates = [
    [2, 3],         # Simplest primes
    [2, 5],
    [3, 5],
    [2, 3, 5],
    [2, 7],
    [3, 7],
    [5, 7],
    [2, 3, 5, 7],
    [2, 11],
    [3, 11],
    [7, 11],
    [2, 3, 7],
    [2, 5, 7],
    [3, 5, 7],
    [2, 3, 11],
    [1, 4],         # From GP (F=0, TH=2, R=4)
    [0, 2, 4],
    [4, 8],         # From page-relevant numbers
    [4, 7, 8],      # 
]

for nbits in [8, 10, 12, 16]:
    for taps in prime_taps_candidates:
        valid_taps = [t for t in taps if t < nbits]
        if len(valid_taps) < 2: continue
        for init in [1, 3, 7, 29, 47, 131, 167, 761]:
            actual_init = init & ((1 << nbits) - 1)
            if actual_init == 0: continue
            ks = lfsr_keystream(valid_taps, actual_init, 2000, nbits)
            if len(ks) < 50: continue
            for pn in target_pages:
                if pn not in PAGES: continue
                cipher = PAGES[pn]
                for mode in modes:
                    plain = decrypt_stream(cipher, ks, mode)
                    ic = ioc(plain)
                    if ic > 1.35:
                        ws = word_score(plain)
                        best3.append((ic, ws, pn, f"LFSR({nbits}bit,taps={valid_taps},init={actual_init})", mode, plain[:30]))

best3.sort(reverse=True)
print(f"\nTotal LFSR results above threshold: {len(best3)}")
for ic, ws, pn, desc, mode, plain in best3[:20]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 4: Cookie primes 167/761 as cipher parameters
# ============================================================================
print("\n" + "="*80)
print("SECTION 4: Cookie primes 167/761 as cipher parameters")
print("="*80)

best4 = []

# 167 and 761 are palindromic primes
# Try various uses:
# A) As multiplicative key: (cipher * 167) mod 29
# B) As additive offset to prime stream
# C) As LFSR seed
# D) As period for Vigenère

for pn in test_pages:
    if pn not in PAGES: continue
    cipher = PAGES[pn]
    n = len(cipher)
    
    # Multiplicative: cipher[i] * k mod 29
    for k in [167 % 29, 761 % 29, (167 * 761) % 29]:
        plain = [(c * k) % 29 for c in cipher]
        ic = ioc(plain)
        if ic > 1.2:
            best4.append((ic, word_score(plain), pn, f"mult_k={k}", '', plain[:30]))
    
    # Additive offset to prime stream
    for offset in [167, 761]:
        key = [(ALL_PRIMES[i] + offset) % 29 for i in range(n)]
        for mode in modes:
            plain = decrypt_stream(cipher, key, mode)
            ic = ioc(plain)
            if ic > 1.25:
                ws = word_score(plain)
                best4.append((ic, ws, pn, f"prime+{offset}", mode, plain[:30]))
        # Totient + offset
        key = [(ALL_PRIMES[i] - 1 + offset) % 29 for i in range(n)]
        for mode in modes:
            plain = decrypt_stream(cipher, key, mode)
            ic = ioc(plain)
            if ic > 1.25:
                ws = word_score(plain)
                best4.append((ic, ws, pn, f"tot+{offset}", mode, plain[:30]))

    # As affine parameters: (a*cipher + b) mod 29
    a_vals = [167 % 29, 761 % 29]
    b_vals = [0, 167 % 29, 761 % 29, (167+761) % 29]
    for a in a_vals:
        for b in b_vals:
            # Check if a is coprime with 29
            if a == 0: continue
            plain = [(a * c + b) % 29 for c in cipher]
            ic = ioc(plain)
            if ic > 1.2:
                best4.append((ic, word_score(plain), pn, f"affine(a={a},b={b})", '', plain[:30]))

best4.sort(reverse=True)
print(f"Results: {len(best4)}")
for ic, ws, pn, desc, mode, plain in best4[:15]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 5: Totient stream with page-specific starting prime
# ============================================================================
print("\n" + "="*80)
print("SECTION 5: Page-number-derived starting prime")
print("="*80)

best5 = []

# What if each page uses (prime[page_num + i] - 1) % 29?
# Or prime[page_num * k + i] for various k?
for pn in test_pages:
    if pn not in PAGES: continue
    cipher = PAGES[pn]
    n = len(cipher)
    
    # Try start = page_num, page_num*2, page_num*3, etc.
    for mult in [1, 2, 3, 5, 7, 11, 13, 29]:
        start = pn * mult
        if start + n >= len(ALL_PRIMES): continue
        key = [(ALL_PRIMES[start + i] - 1) % 29 for i in range(n)]
        for mode in modes:
            plain = decrypt_stream(cipher, key, mode)
            ic = ioc(plain)
            if ic > 1.30:
                ws = word_score(plain)
                best5.append((ic, ws, pn, f"tot(start={start}=P{pn}*{mult})", mode, plain[:30]))
            # Also with just primes (not totient)
            key2 = [ALL_PRIMES[start + i] % 29 for i in range(n)]
            plain2 = decrypt_stream(cipher, key2, mode)
            ic2 = ioc(plain2)
            if ic2 > 1.30:
                ws2 = word_score(plain2)
                best5.append((ic2, ws2, pn, f"prime(start={start}=P{pn}*{mult})", mode, plain2[:30]))
    
    # Try start = GP_PRIMES[page_num % 29]
    gp_idx = pn % 29
    gp_prime = GP_PRIMES[gp_idx]
    # Find index of this prime in ALL_PRIMES
    if gp_prime in PRIME_SET:
        start = ALL_PRIMES.index(gp_prime)
        if start + n < len(ALL_PRIMES):
            key = [(ALL_PRIMES[start + i] - 1) % 29 for i in range(n)]
            for mode in modes:
                plain = decrypt_stream(cipher, key, mode)
                ic = ioc(plain)
                if ic > 1.30:
                    ws = word_score(plain)
                    best5.append((ic, ws, pn, f"tot_gp(gp[{gp_idx}]={gp_prime})", mode, plain[:30]))

best5.sort(reverse=True)
print(f"Results: {len(best5)}")
for ic, ws, pn, desc, mode, plain in best5[:20]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 6: Interleaved / spiral reading order
# ============================================================================
print("\n" + "="*80)
print("SECTION 6: Transposition - spiral/zigzag/diagonal reading")
print("="*80)

best6 = []

def spiral_read(data, width):
    """Read data in spiral order if arranged in grid of given width."""
    n = len(data)
    height = (n + width - 1) // width
    # Pad with -1
    grid = []
    idx = 0
    for r in range(height):
        row = []
        for c in range(width):
            if idx < n:
                row.append(data[idx])
            else:
                row.append(-1)
            idx += 1
        grid.append(row)
    
    result = []
    top, bottom, left, right = 0, height - 1, 0, width - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            if grid[top][c] >= 0: result.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            if grid[r][right] >= 0: result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if grid[bottom][c] >= 0: result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if grid[r][left] >= 0: result.append(grid[r][left])
            left += 1
    return result

def diagonal_read(data, width):
    """Read data diagonally from grid."""
    n = len(data)
    height = (n + width - 1) // width
    grid = []
    idx = 0
    for r in range(height):
        row = []
        for c in range(width):
            if idx < n:
                row.append(data[idx])
            else:
                row.append(-1)
            idx += 1
        grid.append(row)
    
    result = []
    for d in range(height + width - 1):
        for r in range(max(0, d - width + 1), min(d + 1, height)):
            c = d - r
            if c < width and grid[r][c] >= 0:
                result.append(grid[r][c])
    return result

# Test spiral and diagonal reordering + totient decryption on P18
target_widths = [4, 5, 10, 13, 20, 26, 29, 47]
for pn in [17, 18, 20, 25, 32, 40, 44, 50]:
    if pn not in PAGES: continue
    cipher = PAGES[pn]
    n = len(cipher)
    
    for width in target_widths:
        if width > n: continue
        # Spiral read
        spiraled = spiral_read(cipher, width)
        ic = ioc(spiraled)  # Should be same as original
        # After spiral, try totient decrypt
        key = [(ALL_PRIMES[i] - 1) % 29 for i in range(len(spiraled))]
        for mode in modes:
            plain = decrypt_stream(spiraled, key, mode)
            ic_p = ioc(plain)
            if ic_p > 1.25:
                ws = word_score(plain)
                best6.append((ic_p, ws, pn, f"spiral_w={width}+tot", mode, plain[:30]))
        
        # Diagonal read
        diag = diagonal_read(cipher, width)
        key = [(ALL_PRIMES[i] - 1) % 29 for i in range(len(diag))]
        for mode in modes:
            plain = decrypt_stream(diag, key, mode)
            ic_p = ioc(plain)
            if ic_p > 1.25:
                ws = word_score(plain)
                best6.append((ic_p, ws, pn, f"diag_w={width}+tot", mode, plain[:30]))

best6.sort(reverse=True)
print(f"Results: {len(best6)}")
for ic, ws, pn, desc, mode, plain in best6[:15]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 7: P18 deep k=20 analysis with totient/LFSR hybrid
# ============================================================================
print("\n" + "="*80)
print("SECTION 7: P18 deep k=20 analysis")
print("="*80)

if 18 in PAGES:
    cipher = PAGES[18]
    n = len(cipher)
    k = 20
    
    # Column 9 has IoC=5.21! What rune values appear there?
    cols = [[] for _ in range(k)]
    for i, c in enumerate(cipher):
        cols[i % k].append(c)
    
    print(f"P18 k=20 column analysis:")
    for col_idx in range(k):
        from collections import Counter
        cnt = Counter(cols[col_idx])
        ic = ioc(cols[col_idx])
        most_common = cnt.most_common(3)
        print(f"  Col {col_idx:2d}: n={len(cols[col_idx]):2d} IoC={ic:.2f} top3={most_common}")
    
    # Column 9 with IoC=5.21 — probably has a dominant rune value
    # If we know the plaintext at those positions, we can determine the key at position 9
    
    # Test: what if the key at each position is totient(prime[col_idx])?
    # i.e., a 20-value key where key[j] = (prime[j]-1) % 29
    prime_key_20 = [(ALL_PRIMES[j] - 1) % 29 for j in range(20)]
    print(f"\nPrime-derived key (period 20): {prime_key_20}")
    for mode in modes:
        plain = decrypt(cipher, prime_key_20, mode)
        ic_p = ioc(plain)
        ws = word_score(plain)
        print(f"  {mode}: IoC={ic_p:.4f} ws={ws} {vals_to_text(plain[:30])}")
    
    # What if we use primes starting from a different index?
    for start in range(0, 100):
        pk = [(ALL_PRIMES[start + j] - 1) % 29 for j in range(20)]
        for mode in modes:
            plain = decrypt(cipher, pk, mode)
            ic_p = ioc(plain)
            if ic_p > 1.35:
                ws = word_score(plain)
                print(f"  start={start} {mode}: IoC={ic_p:.4f} ws={ws} {vals_to_text(plain[:30])}")
    
    # What about key = sorted GP primes mod 20?
    # Or key derived from page 15 grid?
    # Test: key at position j = the j-th Fibonacci number mod 29
    fib_key_20 = [fibonacci_seq(25)[j] % 29 for j in range(20)]
    print(f"\nFibonacci key (period 20): {fib_key_20}")
    for mode in modes:
        plain = decrypt(cipher, fib_key_20, mode)
        ic_p = ioc(plain)
        ws = word_score(plain)
        print(f"  {mode}: IoC={ic_p:.4f} ws={ws} {vals_to_text(plain[:30])}")

# ============================================================================
# SECTION 8: Cumulative prime product / sum streams
# ============================================================================
print("\n" + "="*80)
print("SECTION 8: Cumulative prime streams")
print("="*80)

best8 = []

# Key[i] = (product of first i primes) mod 29 = primorial mod 29
cum_prod = [1]
for p in ALL_PRIMES[:2000]:
    cum_prod.append((cum_prod[-1] * p) % 29)

# Key[i] = (sum of first i primes) mod 29
cum_sum = [0]
s = 0
for p in ALL_PRIMES[:2000]:
    s += p
    cum_sum.append(s % 29)

# Key[i] = prime[i]^2 mod 29
prime_sq = [p * p % 29 for p in ALL_PRIMES[:2000]]

# Key[i] = prime[i] * prime[i+1] mod 29
prime_prod_adj = [ALL_PRIMES[i] * ALL_PRIMES[i+1] % 29 for i in range(1999)]

# Key[i] = prime[i] XOR prime[i+1] mod 29
prime_xor = [(ALL_PRIMES[i] ^ ALL_PRIMES[i+1]) % 29 for i in range(1999)]

stream_keys = {
    'primorial': cum_prod[1:],
    'cum_sum': cum_sum[1:],
    'prime_sq': prime_sq,
    'adj_prod': prime_prod_adj,
    'prime_xor': prime_xor,
}

for sk_name, sk in stream_keys.items():
    for pn in test_pages:
        if pn not in PAGES: continue
        cipher = PAGES[pn]
        for mode in modes:
            plain = decrypt_stream(cipher, sk, mode)
            if len(plain) < 10: continue
            ic = ioc(plain)
            if ic > 1.30:
                ws = word_score(plain)
                best8.append((ic, ws, pn, sk_name, mode, plain[:30]))
            # F-skip
            plain_fs = decrypt_fskip(cipher, sk, mode)
            if len(plain_fs) >= 10:
                ic_fs = ioc(plain_fs)
                if ic_fs > 1.30:
                    ws_fs = word_score(plain_fs)
                    best8.append((ic_fs, ws_fs, pn, sk_name+"_fskip", mode, plain_fs[:30]))

best8.sort(reverse=True)
print(f"Results: {len(best8)}")
for ic, ws, pn, desc, mode, plain in best8[:15]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 9: Vigenère with prime-length key exhaustive for P18
# ============================================================================
print("\n" + "="*80)
print("SECTION 9: P18 brute-force k=20 with column frequency attack")
print("="*80)

if 18 in PAGES:
    cipher = PAGES[18]
    n = len(cipher)
    k = 20
    
    # For each column, find ALL shift values that make that column's
    # most-frequent rune map to common English letters (E=18, T=16, A=24, O=3, I=10, N=9, S=15, H=8)
    common_plains = [18, 16, 24, 3, 10, 9, 15, 8, 4, 20]  # E,T,A,O,I,N,S,H,R,L in GP
    
    cols = [[] for _ in range(k)]
    for i, c in enumerate(cipher):
        cols[i % k].append(c)
    
    from collections import Counter
    candidate_shifts = []
    for col_idx in range(k):
        cnt = Counter(cols[col_idx])
        most_common_cipher = cnt.most_common(1)[0][0]
        shifts = set()
        for p in common_plains:
            # For SUB: p = (c - key) % 29 => key = (c - p) % 29
            shifts.add((most_common_cipher - p) % 29)
            # For ADD: p = (c + key) % 29 => key = (p - c) % 29
            shifts.add((p - most_common_cipher) % 29)
        candidate_shifts.append(list(shifts))
    
    print(f"Candidate shifts per column: {[len(s) for s in candidate_shifts]}")
    
    # Try top-2 from frequency analysis and all combos
    top2_shifts = []
    for col_idx in range(k):
        cnt = Counter(cols[col_idx])
        top2_cipher = [v for v, _ in cnt.most_common(2)]
        shifts = set()
        for mc in top2_cipher:
            for p in [18, 16, 24]:  # E, T, A only
                shifts.add((mc - p) % 29)  # SUB key
        top2_shifts.append(list(shifts)[:6])
    
    # Check total combos
    total = 1
    for s in top2_shifts:
        total *= len(s)
    print(f"Total top-2 combos: {total}")
    
    if total < 5000000:
        best_p18 = []
        # Generate all combos
        import itertools
        count = 0
        for combo in itertools.product(*top2_shifts):
            key = list(combo)
            plain = decrypt(cipher, key, 'sub')
            ic_p = ioc(plain)
            if ic_p > 1.4:
                ws = word_score(plain)
                best_p18.append((ic_p, ws, key, 'sub', plain[:40]))
            count += 1
            if count % 1000000 == 0:
                print(f"  {count}/{total} checked...")
        
        best_p18.sort(reverse=True)
        print(f"\nP18 k=20 exhaustive results (IoC>1.4): {len(best_p18)}")
        for ic_p, ws, key, mode, plain in best_p18[:10]:
            print(f"  IoC={ic_p:.4f} ws={ws} key={key} {vals_to_text(plain)}")

# ============================================================================
# SECTION 10: Test P19 known key against all pages (first 47 positions)
# ============================================================================
print("\n" + "="*80)
print("SECTION 10: P19 key applied to other pages")
print("="*80)

P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 21, 1, 10, 24]

best10 = []
for pn in test_pages:
    if pn not in PAGES or pn == 19: continue
    cipher = PAGES[pn]
    
    for mode in modes:
        # First 47 only (non-cycling)
        plain_47 = decrypt_stream(cipher[:47], P19_KEY, mode)
        ic_47 = ioc(plain_47) if len(plain_47) > 5 else 0
        ws_47 = word_score(plain_47)
        
        # Cycling
        plain_cyc = decrypt(cipher, P19_KEY, mode)
        ic_cyc = ioc(plain_cyc)
        ws_cyc = word_score(plain_cyc)
        
        if ic_47 > 1.5 or ws_47 > 15 or ic_cyc > 1.15:
            best10.append((max(ic_47, ic_cyc), ws_47, ws_cyc, pn, mode, plain_47[:20], ic_47, ic_cyc))

best10.sort(reverse=True)
print(f"Results: {len(best10)}")
for ic_max, ws47, wsc, pn, mode, p47, ic47, icc in best10[:15]:
    print(f"  P{pn} {mode}: first47_IoC={ic47:.4f} ws47={ws47} cyc_IoC={icc:.4f} wsc={wsc} {vals_to_text(p47)}")

print("\n\nDONE")
