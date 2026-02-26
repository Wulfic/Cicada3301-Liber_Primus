#!/usr/bin/env python3
"""
Global stream attack + inter-page operations + prime-domain cipher.
Tests whether pages form one continuous stream with a global key.
"""
import sys, io, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GP_RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GP_NAMES = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}

def sieve_primes(n):
    if n < 2: return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

ALL_PRIMES = sieve_primes(500000)

def load_page(page_num):
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
    c = Counter(values)
    n = len(values)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1) / 29.0)

def vals_to_text(vals):
    return ''.join(GP_NAMES[v] for v in vals)

def word_score(vals):
    text = vals_to_text(vals).upper()
    score = 0
    words = ["THE","AND","FOR","ARE","BUT","NOT","YOU","ALL","CAN","WAS","ONE","OUR",
             "OUT","HIS","HAS","WHO","NOW","DID","GET","HIM","HOW","NEW","WAY","MAY",
             "THAT","WITH","HAVE","THIS","WILL","YOUR","FROM","THEY","BEEN","SOME",
             "INTO","TIME","VERY","WHEN","COME","MAKE","LIKE","LONG","OVER","SUCH",
             "KNOW","WELL","THEN","MOST","ONLY","WOULD","THERE","THEIR","WHAT","ABOUT",
             "WHICH","COULD","OTHER","WERE","MORE","AFTER","THINK","SHOULD","THESE",
             "SACRED","PRIME","PRIMES","TOTIENT","DIVINITY","CIRCUMFERENCE","WISDOM",
             "LOSS","VOID","EMERGENCE","TRUTH","PATH","CONSCIOUSNESS","NUMBER","ENCRYPT"]
    for w in words:
        if w in text:
            score += len(w)
    return score

# Load all pages
PAGES = {}
for pn in range(17, 55):
    data = load_page(pn)
    if data:
        PAGES[pn] = data

print(f"Loaded {len(PAGES)} pages")

# ============================================================================
# SECTION 1: Global concatenated stream with totient keystream
# ============================================================================
print("\n" + "="*80)
print("SECTION 1: Concatenated pages as one stream")
print("="*80)

# Concatenate pages in order
page_order = sorted(PAGES.keys())
concat = []
page_offsets = {}
for pn in page_order:
    page_offsets[pn] = len(concat)
    concat.extend(PAGES[pn])

print(f"Total concatenated runes: {len(concat)}")
print(f"Page offsets: {[(pn, page_offsets[pn]) for pn in page_order[:10]]}...")

# Generate totient keystream: k[i] = (prime[i] - 1) % 29
tot_key = [(ALL_PRIMES[i] - 1) % 29 for i in range(len(concat) + 1000)]
prime_key = [ALL_PRIMES[i] % 29 for i in range(len(concat) + 1000)]

modes = ['add', 'sub', 'beaufort']

# Test with offset 0 (pages 17+ start from prime[0])
for mode in modes:
    plain = [(concat[i] + tot_key[i]) % 29 if mode == 'add' else 
             (concat[i] - tot_key[i]) % 29 if mode == 'sub' else 
             (tot_key[i] - concat[i]) % 29 for i in range(len(concat))]
    # Check IoC per page
    for pn in page_order:
        start = page_offsets[pn]
        end = start + len(PAGES[pn])
        page_plain = plain[start:end]
        ic = ioc(page_plain)
        ws = word_score(page_plain)
        if ic > 1.25 or ws > 10:
            print(f"  P{pn} {mode} offset=0: IoC={ic:.4f} ws={ws} {vals_to_text(page_plain[:25])}")

# Test with various global offsets (starting from prime[offset])
print("\nTesting global offsets...")
best1 = []
for offset in list(range(0, 2000, 10)) + [167, 761, 131, 3301, 1033]:
    if offset + len(concat) >= len(ALL_PRIMES): continue
    for mode in modes:
        # Per-page IoC check (fast)
        for pn in page_order[:5]:  # Quick check on first 5 pages
            start = page_offsets[pn]
            end = start + len(PAGES[pn])
            page_cipher = concat[start:end]
            page_plain = []
            for i, c in enumerate(page_cipher):
                k = tot_key[offset + start + i]
                if mode == 'add': page_plain.append((c + k) % 29)
                elif mode == 'sub': page_plain.append((c - k) % 29)
                else: page_plain.append((k - c) % 29)
            ic = ioc(page_plain)
            if ic > 1.35:
                ws = word_score(page_plain)
                best1.append((ic, ws, pn, offset, mode, page_plain[:25]))

best1.sort(reverse=True)
print(f"Results: {len(best1)}")
for ic, ws, pn, off, mode, plain in best1[:15]:
    print(f"  P{pn} offset={off} {mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# Also test: reverse page order
concat_rev = []
for pn in reversed(page_order):
    concat_rev.extend(PAGES[pn])

for mode in modes:
    plain = [(concat_rev[i] + tot_key[i]) % 29 if mode == 'add' else 
             (concat_rev[i] - tot_key[i]) % 29 if mode == 'sub' else 
             (tot_key[i] - concat_rev[i]) % 29 for i in range(len(concat_rev))]
    ic = ioc(plain)
    ws = word_score(plain)
    if ic > 1.10 or ws > 15:
        print(f"  Reversed concat {mode}: IoC={ic:.4f} ws={ws}")

# ============================================================================
# SECTION 2: Inter-page XOR / subtraction
# ============================================================================
print("\n" + "="*80)
print("SECTION 2: Inter-page operations (XOR, subtract, add)")
print("="*80)

# Test pairs of pages: use one page as key for another
# Focus on pages of SAME LENGTH
page_lens = {}
for pn in page_order:
    n = len(PAGES[pn])
    page_lens.setdefault(n, []).append(pn)

print("Pages grouped by length:")
for n, pns in sorted(page_lens.items()):
    if len(pns) > 1:
        print(f"  n={n}: pages {pns}")

best2 = []
for pn1 in page_order:
    for pn2 in page_order:
        if pn1 >= pn2: continue
        d1 = PAGES[pn1]
        d2 = PAGES[pn2]
        n = min(len(d1), len(d2))
        if n < 50: continue
        
        # XOR: (d1[i] + d2[i]) % 29 — "additive XOR" in mod-29
        result_add = [(d1[i] + d2[i]) % 29 for i in range(n)]
        ic = ioc(result_add)
        if ic > 1.25:
            ws = word_score(result_add)
            best2.append((ic, ws, f"P{pn1}+P{pn2}", 'add', result_add[:25]))
        
        # SUB: (d1[i] - d2[i]) % 29
        result_sub = [(d1[i] - d2[i]) % 29 for i in range(n)]
        ic = ioc(result_sub)
        if ic > 1.25:
            ws = word_score(result_sub)
            best2.append((ic, ws, f"P{pn1}-P{pn2}", 'sub', result_sub[:25]))

best2.sort(reverse=True)
print(f"\nResults: {len(best2)}")
for ic, ws, desc, mode, plain in best2[:15]:
    print(f"  {desc} ({mode}): IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 3: Prime-domain cipher
# ============================================================================
print("\n" + "="*80)
print("SECTION 3: Operations in prime-value domain")
print("="*80)

# Instead of mod-29 arithmetic on GP indices, operate on GP PRIME VALUES
# Then convert back to indices
prime_to_idx = {p: i for i, p in enumerate(GP_PRIMES)}

best3 = []
for pn in page_order:
    cipher = PAGES[pn]
    cipher_primes = [GP_PRIMES[c] for c in cipher]
    n = len(cipher)
    
    # Method A: Subtract sequential primes in prime domain
    # result_prime = (cipher_prime[i] - prime[i]) mapped back to GP
    for start in [0, 1, 5, 10, 17, 20, 29, 47]:
        result = []
        valid = True
        for i in range(n):
            cp = cipher_primes[i]
            sp = ALL_PRIMES[start + i]
            # How to combine? Try: (cp - sp) mod (some value)
            # The GP primes are {2,3,5,...,109}. Not a regular field.
            # Try: (cp * inverse(sp)) mod 113 (next prime > 109)
            # Or: index of (cp XOR sp) in GP primes
            # Or: look up (cp - sp) % 113 closest GP prime
            diff = (cp - sp) % 113
            # Find closest GP prime
            if diff in prime_to_idx:
                result.append(prime_to_idx[diff])
            else:
                # Map to nearest GP prime
                result.append(diff % 29)
        
        ic = ioc(result)
        if ic > 1.25:
            ws = word_score(result)
            best3.append((ic, ws, pn, f"prime_sub_start={start}", result[:25]))
    
    # Method B: XOR cipher prime with sequential prime, find in GP
    for start in [0, 1, 5, 10, 17, 29]:
        result = []
        for i in range(n):
            xval = cipher_primes[i] ^ ALL_PRIMES[start + i]
            if xval in prime_to_idx:
                result.append(prime_to_idx[xval])
            else:
                result.append(xval % 29)
        ic = ioc(result)
        if ic > 1.25:
            ws = word_score(result)
            best3.append((ic, ws, pn, f"prime_xor_start={start}", result[:25]))

    # Method C: Multiplicative in prime domain
    # cipher_prime / key_prime in some modular sense
    for k_prime in GP_PRIMES:
        # (cipher_prime * modular_inverse(k_prime, 29)) mod 29... but this is just a fixed mapping
        pass  # Skip, just a substitution cipher

best3.sort(reverse=True)
print(f"Results: {len(best3)}")
for ic, ws, pn, desc, plain in best3[:15]:
    print(f"  P{pn} {desc}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 4: P00+P17 relationship (P00 is subset of P17)
# ============================================================================
print("\n" + "="*80)
print("SECTION 4: P00 and P17 relationship analysis")
print("="*80)

p00 = load_page(0)
p17 = load_page(17)
if p00 and p17:
    # P00 first 262 runes = P17 first 262 runes (known)
    # What about the rest of P17 (262-728)?
    print(f"P00: {len(p00)} runes, P17: {len(p17)} runes")
    match = sum(1 for i in range(min(len(p00), len(p17))) if p00[i] == p17[i])
    print(f"Matching runes (first {min(len(p00),len(p17))}): {match}")
    
    # If P00 is all of P17's content, the "extra" 467 runes of P17 might be key material
    extra_p17 = p17[len(p00):]
    print(f"Extra P17 runes (after P00): {len(extra_p17)}")
    if extra_p17:
        ic_extra = ioc(extra_p17)
        print(f"Extra P17 IoC: {ic_extra:.4f}")
        # Try using extra P17 as key for unsolved pages
        for pn in [18, 19, 20, 21, 22]:
            if pn not in PAGES: continue
            cipher = PAGES[pn]
            n = min(len(cipher), len(extra_p17))
            for mode in ['add', 'sub', 'beaufort']:
                plain = [(cipher[i] + extra_p17[i]) % 29 if mode == 'add' else
                         (cipher[i] - extra_p17[i]) % 29 if mode == 'sub' else
                         (extra_p17[i] - cipher[i]) % 29 for i in range(n)]
                ic = ioc(plain)
                ws = word_score(plain)
                if ic > 1.15 or ws > 5:
                    print(f"  P{pn} extra_P17/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain[:25])}")

# ============================================================================
# SECTION 5: Totient stream with F-skip variations
# ============================================================================
print("\n" + "="*80)
print("SECTION 5: Totient stream with F-skip on ALL pages")
print("="*80)

best5 = []
for pn in page_order:
    cipher = PAGES[pn]
    n = len(cipher)
    
    # Count F runes  
    f_count = sum(1 for c in cipher if c == 0)
    non_f = n - f_count
    
    for start in range(0, 300, 1):
        if start + non_f >= len(ALL_PRIMES): continue
        key = [(ALL_PRIMES[start + i] - 1) % 29 for i in range(non_f + 10)]
        
        for mode in ['add', 'sub', 'beaufort']:
            # F-skip decrypt
            result = []
            ki = 0
            for c in cipher:
                if c == 0:
                    result.append(0)  # F stays F
                else:
                    k = key[ki] if ki < len(key) else 0
                    if mode == 'add': result.append((c + k) % 29)
                    elif mode == 'sub': result.append((c - k) % 29)
                    else: result.append((k - c) % 29)
                    ki += 1
            
            ic = ioc(result)
            if ic > 1.35:
                ws = word_score(result)
                best5.append((ic, ws, pn, f"tot_fskip_start={start}", mode, result[:25]))

best5.sort(reverse=True)
print(f"Results (IoC > 1.35): {len(best5)}")
for ic, ws, pn, desc, mode, plain in best5[:20]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 6: Differential analysis between adjacent pages
# ============================================================================
print("\n" + "="*80)
print("SECTION 6: Differential analysis (page[n] - page[n-1])")
print("="*80)

# What if (page[n][i] - page[n-1][i]) % 29 reveals something?
best6 = []
for idx in range(1, len(page_order)):
    pn_prev = page_order[idx - 1]
    pn_curr = page_order[idx]
    d_prev = PAGES[pn_prev]
    d_curr = PAGES[pn_curr]
    n = min(len(d_prev), len(d_curr))
    if n < 50: continue
    
    diff = [(d_curr[i] - d_prev[i]) % 29 for i in range(n)]
    ic = ioc(diff)
    ws = word_score(diff)
    if ic > 1.15 or ws > 5:
        best6.append((ic, ws, f"P{pn_curr}-P{pn_prev}", diff[:25]))

best6.sort(reverse=True)
print(f"Results: {len(best6)}")
for ic, ws, desc, plain in best6[:10]:
    print(f"  {desc}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 7: Totient with prime[i] instead of (prime[i]-1)
# ============================================================================
print("\n" + "="*80)
print("SECTION 7: Prime stream (not totient) with exhaustive offset search")
print("="*80)

# key[i] = prime[start+i] % 29 (not totient!)
best7 = []
for pn in page_order:
    cipher = PAGES[pn]
    n = len(cipher)
    
    for start in range(0, 500):
        if start + n >= len(ALL_PRIMES): continue
        key = [ALL_PRIMES[start + i] % 29 for i in range(n)]
        
        for mode in ['add', 'sub', 'beaufort']:
            plain = [(cipher[i] + key[i]) % 29 if mode == 'add' else
                     (cipher[i] - key[i]) % 29 if mode == 'sub' else
                     (key[i] - cipher[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > 1.35:
                ws = word_score(plain)
                best7.append((ic, ws, pn, f"prime_start={start}(p={ALL_PRIMES[start]})", mode, plain[:25]))

best7.sort(reverse=True)
print(f"Results (IoC > 1.35): {len(best7)}")
for ic, ws, pn, desc, mode, plain in best7[:20]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 8: Global stream as prime indices × page multiplier
# ============================================================================
print("\n" + "="*80)
print("SECTION 8: Page-specific prime multiplier")
print("="*80)

# For each page, key[i] = (prime[i] * page_num) % 29
# Or key[i] = (prime[i] + page_num) % 29
best8 = []
for pn in page_order:
    cipher = PAGES[pn]
    n = len(cipher)
    
    # Multiplicative: key[i] = (prime[i] * pn) % 29
    key_mult = [(ALL_PRIMES[i] * pn) % 29 for i in range(n)]
    # Additive: key[i] = (prime[i] + pn) % 29
    key_add = [(ALL_PRIMES[i] + pn) % 29 for i in range(n)]
    # Totient mult: key[i] = ((prime[i]-1) * pn) % 29
    key_tot_mult = [((ALL_PRIMES[i]-1) * pn) % 29 for i in range(n)]
    # Mixed: key[i] = (prime[i] * GP_PRIMES[pn % 29]) % 29
    gp_mult = GP_PRIMES[pn % 29]
    key_gp = [(ALL_PRIMES[i] * gp_mult) % 29 for i in range(n)]
    
    for key, kname in [(key_mult, f"prime*{pn}"), (key_add, f"prime+{pn}"), 
                        (key_tot_mult, f"tot*{pn}"), (key_gp, f"prime*GP[{pn%29}]={gp_mult}")]:
        for mode in ['add', 'sub', 'beaufort']:
            plain = [(cipher[i] + key[i]) % 29 if mode == 'add' else
                     (cipher[i] - key[i]) % 29 if mode == 'sub' else
                     (key[i] - cipher[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > 1.30:
                ws = word_score(plain)
                best8.append((ic, ws, pn, kname, mode, plain[:25]))

best8.sort(reverse=True)
print(f"Results (IoC > 1.30): {len(best8)}")
for ic, ws, pn, desc, mode, plain in best8[:15]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 9: EulerTotient(n) for n=1,2,3,... as keystream
# ============================================================================
print("\n" + "="*80)
print("SECTION 9: Euler totient function φ(n) for sequential n")
print("="*80)

# φ(1)=1, φ(2)=1, φ(3)=2, φ(4)=2, φ(5)=4, φ(6)=2, φ(7)=6, ...
def euler_totient_sieve(limit):
    phi = list(range(limit))
    for i in range(2, limit):
        if phi[i] == i:  # i is prime
            for j in range(i, limit, i):
                phi[j] -= phi[j] // i
    return phi

phi = euler_totient_sieve(20000)
phi_key = [phi[i] % 29 for i in range(1, 20000)]

best9 = []
for pn in page_order:
    cipher = PAGES[pn]
    n = len(cipher)
    
    for start in range(0, 2000, 5):
        key = phi_key[start:start+n]
        if len(key) < n: continue
        for mode in ['add', 'sub', 'beaufort']:
            plain = [(cipher[i] + key[i]) % 29 if mode == 'add' else
                     (cipher[i] - key[i]) % 29 if mode == 'sub' else
                     (key[i] - cipher[i]) % 29 for i in range(n)]
            ic = ioc(plain)
            if ic > 1.35:
                ws = word_score(plain)
                best9.append((ic, ws, pn, f"phi({start+1}..{start+n})", mode, plain[:25]))

best9.sort(reverse=True)
print(f"Results (IoC > 1.35): {len(best9)}")
for ic, ws, pn, desc, mode, plain in best9[:15]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 10: Möbius function μ(n) as keystream
# ============================================================================
print("\n" + "="*80)
print("SECTION 10: Möbius function μ(n) as keystream")
print("="*80)

def mobius_sieve(limit):
    mu = [0] * limit
    mu[1] = 1
    is_prime = [True] * limit
    primes = []
    for i in range(2, limit):
        if is_prime[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p >= limit: break
            is_prime[i * p] = False
            if i % p == 0:
                mu[i * p] = 0
                break
            else:
                mu[i * p] = -mu[i]
    return mu

mu = mobius_sieve(20000)
# Map μ: -1→28, 0→0, 1→1 (mod 29)
mu_key = [(mu[i] % 29) for i in range(1, 20000)]

# Also cumulative Möbius (Mertens function)
mertens = [0]
for i in range(1, 20000):
    mertens.append(mertens[-1] + mu[i])
mertens_key = [m % 29 for m in mertens[1:]]

best10 = []
for pn in page_order:
    cipher = PAGES[pn]
    n = len(cipher)
    
    for key, kname in [(mu_key, 'mobius'), (mertens_key, 'mertens')]:
        for start in range(0, 1000, 10):
            ks = key[start:start+n]
            if len(ks) < n: continue
            for mode in ['add', 'sub', 'beaufort']:
                plain = [(cipher[i] + ks[i]) % 29 if mode == 'add' else
                         (cipher[i] - ks[i]) % 29 if mode == 'sub' else
                         (ks[i] - cipher[i]) % 29 for i in range(n)]
                ic = ioc(plain)
                if ic > 1.35:
                    ws = word_score(plain)
                    best10.append((ic, ws, pn, f"{kname}(start={start})", mode, plain[:25]))

best10.sort(reverse=True)
print(f"Results (IoC > 1.35): {len(best10)}")
for ic, ws, pn, desc, mode, plain in best10[:15]:
    print(f"  P{pn} {desc}/{mode}: IoC={ic:.4f} ws={ws} {vals_to_text(plain)}")

# ============================================================================
# SECTION 11: Comprehensive P19 key analysis — find mathematical source
# ============================================================================
print("\n" + "="*80)
print("SECTION 11: P19 key - match against mathematical sequences")
print("="*80)

P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 21, 1, 10, 24]

# Test: is P19 key = (some_constant * prime[i]) % 29?
for c in range(1, 29):
    match_count = 0
    for i in range(47):
        expected = (c * ALL_PRIMES[i]) % 29
        if expected == P19_KEY[i]:
            match_count += 1
    if match_count > 5:
        print(f"  c*prime mod 29, c={c}: {match_count}/47 matches")

# Test: is P19 key = (prime[i] * prime[i+k]) % 29?
for k in range(1, 50):
    match = sum(1 for i in range(47) if (ALL_PRIMES[i] * ALL_PRIMES[i+k]) % 29 == P19_KEY[i])
    if match > 5:
        print(f"  prime[i]*prime[i+{k}] mod 29: {match}/47 matches")

# Test: is P19 key = phi(prime[i]) % 29?
for start in range(500):
    match = sum(1 for i in range(47) if (ALL_PRIMES[start+i] - 1) % 29 == P19_KEY[i])
    if match > 5:
        print(f"  phi(prime[{start}+i]) mod 29: {match}/47 matches")

# Test: is P19 key = prime[i+k] % 29?  
for start in range(500):
    match = sum(1 for i in range(47) if ALL_PRIMES[start+i] % 29 == P19_KEY[i])
    if match > 5:
        print(f"  prime[{start}+i] mod 29: {match}/47 matches")

# Test: is P19 key = phi(n) for sequential n?
for start in range(2000):
    match = sum(1 for i in range(47) if phi[start+i+1] % 29 == P19_KEY[i])
    if match > 5:
        print(f"  phi({start+1}+i) mod 29: {match}/47 matches")

# Test: is P19 key = mu(n) or mertens(n)?
for start in range(1000):
    match_mu = sum(1 for i in range(47) if mu[start+i+1] % 29 == P19_KEY[i])
    match_me = sum(1 for i in range(47) if mertens[start+i+1] % 29 == P19_KEY[i])
    if match_mu > 5:
        print(f"  mu({start+1}+i) mod 29: {match_mu}/47 matches")
    if match_me > 5:
        print(f"  mertens({start+1}+i) mod 29: {match_me}/47 matches")

# Test: is P19 key = (a*i + b) % 29 for some linear relation?
for a in range(29):
    for b in range(29):
        match = sum(1 for i in range(47) if (a * i + b) % 29 == P19_KEY[i])
        if match > 8:
            print(f"  ({a}*i + {b}) mod 29: {match}/47 matches")

# Test: quadratic (a*i^2 + b*i + c) % 29
for a in range(29):
    for b in range(29):
        for c in range(29):
            match = sum(1 for i in range(47) if (a*i*i + b*i + c) % 29 == P19_KEY[i])
            if match > 12:
                print(f"  ({a}*i²+{b}*i+{c}) mod 29: {match}/47 matches")

print("\n\nDONE")
