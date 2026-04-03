#!/usr/bin/env python3
"""
GF(29) LFSR solver for Liber Primus unsolved pages.

Optimized approach using linear algebra over GF(29):
- For LFSR of length L, s_n is a LINEAR function of (s_0,...,s_{L-1})
- Single-rune words give s_{pos} ∈ {val_I, val_A} constraints
- Instead of brute-forcing initial states, solve linear systems
- For L unknowns, pick L constraints (2^L I/A combinations), solve, check rest
"""

import sys, json, itertools, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
MOD = 29
I_IDX = 10
A_IDX = 24

# English word sets
COMMON_WORDS = {'THE','AND','OF','TO','IN','IS','IT','THAT','FOR','WAS','ON','ARE','AS',
    'WITH','HIS','THEY','BE','AT','ONE','HAVE','THIS','FROM','OR','HAD','BY',
    'NOT','BUT','SOME','WHAT','THERE','WE','CAN','OUT','OTHER','WERE','ALL',
    'YOUR','WHEN','UP','USE','HOW','SAID','AN','EACH','WHICH','DO','THEIR',
    'IF','WILL','WAY','ABOUT','MANY','THEN','THEM','WOULD','LIKE','SO',
    'THESE','HER','LONG','MAKE','THING','SEE','HIM','TWO','HAS','LOOK',
    'MORE','DAY','COULD','GO','COME','DID','MY','NO','MOST','WHO','OVER',
    'KNOW','THAN','CALL','FIRST','MAY','DOWN','SIDE','BEEN','NOW','FIND',
    'HEAD','STAND','OWN','PAGE','SHOULD','THROUGH','WORLD','EVERY','DOES',
    'GOD','LIFE','MAN','SELF','BEING','SOUL','TRUTH','DIVINE','WISDOM',
    'MIND','POWER','NATURE','SPIRIT','LIGHT','DARK','EARTH','FIRE','WATER',
    'AIR','VOID','FORM','LOVE','DEATH','SEEK','PATH','I','A','WITHIN','WITHOUT'}

def mod_inv(a, m=MOD):
    if a % m == 0: return None
    g, x, _ = extended_gcd(a % m, m)
    return x % m if g == 1 else None

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def load_runes(page_num):
    rune_file = ROOT / f"pages/page_{page_num:02d}/runes.txt"
    if not rune_file.exists(): return None, None
    text = rune_file.read_text(encoding='utf-8').strip()
    RUNE_TO_IDX = {
        'ᚠ':0,'ᚢ':1,'ᚦ':2,'ᚩ':3,'ᚱ':4,'ᚳ':5,'ᚷ':6,'ᚹ':7,
        'ᚻ':8,'ᚾ':9,'ᛁ':10,'ᛂ':11,'ᛇ':12,'ᛈ':13,'ᛉ':14,'ᛋ':15,
        'ᛏ':16,'ᛒ':17,'ᛖ':18,'ᛗ':19,'ᛚ':20,'ᛝ':21,'ᛟ':22,'ᛞ':23,
        'ᚪ':24,'ᚫ':25,'ᚣ':26,'ᛡ':27,'ᛠ':28,'ᛄ':11,
    }
    rune_indices = []
    word_lengths = []
    current_word_len = 0
    for ch in text:
        if ch in RUNE_TO_IDX:
            rune_indices.append(RUNE_TO_IDX[ch])
            current_word_len += 1
        elif ch in ('-', '•', '\n', ' ', '/'):
            if current_word_len > 0:
                word_lengths.append(current_word_len)
                current_word_len = 0
        elif ch == '.':
            if current_word_len > 0:
                word_lengths.append(current_word_len)
                current_word_len = 0
    if current_word_len > 0:
        word_lengths.append(current_word_len)
    return rune_indices, word_lengths

def get_single_rune_positions(word_lengths):
    positions = []
    pos = 0
    for wlen in word_lengths:
        if wlen == 1: positions.append(pos)
        pos += wlen
    return positions

def ioc(values):
    if len(values) < 2: return 0
    c = Counter(values)
    n = len(values)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)/MOD) if n > 1 else 0

def decrypt(cipher, ks, mode='sub'):
    if mode == 'sub': return [(c-k)%MOD for c,k in zip(cipher,ks)]
    elif mode == 'add': return [(c+k)%MOD for c,k in zip(cipher,ks)]
    elif mode == 'beaufort': return [(k-c)%MOD for c,k in zip(cipher,ks)]

def to_text(indices):
    return ''.join(GP_LETTERS[i] for i in indices)

def count_words(plain_indices, word_lengths):
    words = []
    pos = 0
    for wlen in word_lengths:
        word = to_text(plain_indices[pos:pos+wlen])
        words.append(word)
        pos += wlen
    matches = sum(1 for w in words if w.upper() in COMMON_WORDS)
    return matches, len(words), words

def get_keystream_constraints(cipher, single_positions, mode):
    """For each single-rune position, compute the two possible keystream values."""
    constraints = []
    for pos in single_positions:
        c = cipher[pos]
        if mode == 'sub':    # plain=(c-k)%29 → for I: k=(c-10)%29, for A: k=(c-24)%29
            constraints.append((pos, (c-I_IDX)%MOD, (c-A_IDX)%MOD))
        elif mode == 'beaufort':  # plain=(k-c)%29 → for I: k=(10+c)%29, for A: k=(24+c)%29
            constraints.append((pos, (I_IDX+c)%MOD, (A_IDX+c)%MOD))
        elif mode == 'add':   # plain=(c+k)%29 → for I: k=(10-c)%29, for A: k=(24-c)%29
            constraints.append((pos, (I_IDX-c)%MOD, (A_IDX-c)%MOD))
    return constraints

# ============================================================
# LFSR basis computation
# ============================================================

def lfsr_basis_vectors(coeffs, n_runes):
    """For LFSR s_n = sum(coeffs[j]*s_{n-L+j}) mod 29, j=0..L-1
    Compute s_n as linear combination of initial state: s_n = sum(alpha[n][j] * s_j)
    Returns alpha[n] for n = 0..n_runes-1
    """
    L = len(coeffs)
    # alpha[n] = vector of length L such that s_n = sum(alpha[n][j] * s_j) mod 29
    alpha = [[0]*L for _ in range(n_runes)]
    for j in range(L):
        alpha[j][j] = 1
    for n in range(L, n_runes):
        for j in range(L):
            alpha[n][j] = sum(coeffs[k] * alpha[n-L+k][j] for k in range(L)) % MOD
    return alpha

def solve_linear_gf29(matrix, rhs):
    """Solve matrix * x = rhs over GF(29). Returns x or None if no solution."""
    n = len(matrix)
    # Augmented matrix
    aug = [(list(row) + [r]) for row, r in zip(matrix, rhs)]
    # Gaussian elimination
    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if aug[row][col] % MOD != 0:
                pivot = row
                break
        if pivot is None: return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        inv = mod_inv(aug[col][col])
        if inv is None: return None
        aug[col] = [(x * inv) % MOD for x in aug[col]]
        for row in range(n):
            if row != col and aug[row][col] != 0:
                factor = aug[row][col]
                aug[row] = [(aug[row][j] - factor * aug[col][j]) % MOD for j in range(n+1)]
    return [aug[i][n] % MOD for i in range(n)]

def search_lfsr_algebraic(cipher, word_lengths, single_positions, n_runes, page_num, L_range=(1,5)):
    """Algebraic LFSR search using linear constraints from single-rune words."""
    constraints_by_mode = {}
    for mode in ['sub', 'beaufort', 'add']:
        constraints_by_mode[mode] = get_keystream_constraints(cipher, single_positions, mode)
    
    n_con = len(single_positions)
    results = []
    
    for L in range(L_range[0], min(L_range[1]+1, n_con+1)):
        print(f"\n  LFSR L={L}: testing {MOD}^{L} = {MOD**L} polynomials...")
        t0 = time.time()
        best = (0, None)
        full_matches = 0
        
        # Iterate over all feedback polynomials
        coeff_range = list(range(MOD))
        
        for poly_vals in itertools.product(coeff_range, repeat=L):
            coeffs = list(poly_vals)
            # Compute basis vectors
            alpha = lfsr_basis_vectors(coeffs, n_runes)
            
            for mode in ['sub', 'beaufort', 'add']:
                cons = constraints_by_mode[mode]
                # Use first L constraints to build system
                # For each of 2^L I/A combos for first L constraints:
                first_L = cons[:L]
                rest = cons[L:]
                
                for ia_bits in range(1 << L):
                    # Build linear system
                    matrix = []
                    rhs = []
                    for idx, (pos, k_I, k_A) in enumerate(first_L):
                        matrix.append(alpha[pos][:])
                        if (ia_bits >> idx) & 1:
                            rhs.append(k_A)
                        else:
                            rhs.append(k_I)
                    
                    # Solve for initial state
                    init = solve_linear_gf29(matrix, rhs)
                    if init is None:
                        continue
                    
                    # Check remaining constraints
                    total_match = L  # first L are matched by construction
                    for pos, k_I, k_A in rest:
                        val = sum(alpha[pos][j] * init[j] for j in range(L)) % MOD
                        if val == k_I or val == k_A:
                            total_match += 1
                    
                    if total_match > best[0]:
                        best = (total_match, (coeffs, init, mode, total_match))
                    
                    if total_match == n_con:
                        full_matches += 1
                        # Generate full keystream and evaluate
                        ks = []
                        for n in range(n_runes):
                            ks.append(sum(alpha[n][j] * init[j] for j in range(L)) % MOD)
                        plain = decrypt(cipher, ks, mode)
                        ic = ioc(plain)
                        wm, tw, words = count_words(plain, word_lengths)
                        
                        if ic > 1.3 or wm >= 3:
                            txt = to_text(plain[:60])
                            matched = [w for w in words if w.upper() in COMMON_WORDS]
                            print(f"    ★ L={L} poly={coeffs} init={init} {mode}: "
                                  f"IoC={ic:.4f} words={wm}/{tw} | {txt}")
                            if matched:
                                print(f"      Matched: {matched[:15]}")
                            results.append((ic, wm, f"LFSR L={L} poly={coeffs} init={init} {mode}", plain, words))
        
        elapsed = time.time() - t0
        m, params = best
        print(f"    Time: {elapsed:.1f}s. Full constraint matches: {full_matches}. Best: {m}/{n_con}")
        if params:
            coeffs, init, mode, _ = params
            print(f"    Best params: poly={coeffs} init={init} {mode}")
    
    return results

# ============================================================
# Simpler keystream types
# ============================================================

def search_affine(cipher, word_lengths, single_positions, n_runes):
    """k_i = (a*i + b) % 29"""
    print(f"\n  Affine keystream: k_i = (a*i + b) % 29")
    results = []
    best = (0, None)
    
    for mode in ['sub', 'beaufort', 'add']:
        cons = get_keystream_constraints(cipher, single_positions, mode)
        for a in range(MOD):
            for b in range(MOD):
                matches = 0
                for pos, k_I, k_A in cons:
                    val = (a * pos + b) % MOD
                    if val == k_I or val == k_A:
                        matches += 1
                if matches > best[0]:
                    best = (matches, (a, b, mode))
                if matches == len(cons):
                    ks = [(a*i+b)%MOD for i in range(n_runes)]
                    plain = decrypt(cipher, ks, mode)
                    ic = ioc(plain)
                    wm, tw, words = count_words(plain, word_lengths)
                    if ic > 1.3 or wm >= 3:
                        txt = to_text(plain[:60])
                        print(f"    ★ a={a} b={b} {mode}: IoC={ic:.4f} words={wm}/{tw} | {txt}")
                        results.append((ic, wm, f"affine a={a} b={b} {mode}", plain, words))
    
    m, params = best
    print(f"    Best: {m}/{len(single_positions)} matches" + (f" params={params}" if params else ""))
    return results

def search_quadratic(cipher, word_lengths, single_positions, n_runes):
    """k_i = (a*i^2 + b*i + c) % 29"""
    print(f"\n  Quadratic keystream: k_i = (a*i^2 + b*i + c) % 29")
    results = []
    best = (0, None)
    n_con = len(single_positions)
    
    for mode in ['sub', 'beaufort', 'add']:
        cons = get_keystream_constraints(cipher, single_positions, mode)
        for a in range(1, MOD):
            for b in range(MOD):
                for c in range(MOD):
                    matches = 0
                    for pos, k_I, k_A in cons:
                        val = (a*pos*pos + b*pos + c) % MOD
                        if val == k_I or val == k_A: matches += 1
                    if matches > best[0]:
                        best = (matches, (a,b,c,mode))
                    if matches == n_con and n_con >= 3:
                        ks = [(a*i*i+b*i+c)%MOD for i in range(n_runes)]
                        plain = decrypt(cipher, ks, mode)
                        ic = ioc(plain)
                        wm, tw, words = count_words(plain, word_lengths)
                        if ic > 1.3 or wm >= 3:
                            txt = to_text(plain[:60])
                            print(f"    ★ a={a} b={b} c={c} {mode}: IoC={ic:.4f} words={wm}/{tw} | {txt}")
                            results.append((ic, wm, f"quad a={a} b={b} c={c} {mode}", plain, words))
    
    m, params = best
    print(f"    Best: {m}/{n_con} matches" + (f" params={params}" if params else ""))
    return results

def search_power(cipher, word_lengths, single_positions, n_runes):
    """k_i = (mult * base^i + off) % 29"""
    print(f"\n  Power/geometric keystream: k_i = (mult * base^i + off) % 29")
    results = []
    best = (0, None)
    n_con = len(single_positions)
    
    for mode in ['sub', 'beaufort', 'add']:
        cons = get_keystream_constraints(cipher, single_positions, mode)
        for base in range(2, MOD):
            # Precompute base powers at constraint positions
            powers = {}
            val = 1
            max_pos = max(p for p,_,_ in cons) + 1
            bp = [0] * max_pos
            v = 1
            for i in range(max_pos):
                bp[i] = v
                v = (v * base) % MOD
            
            for mult in range(1, MOD):
                for off in range(MOD):
                    matches = 0
                    for pos, k_I, k_A in cons:
                        val = (mult * bp[pos] + off) % MOD
                        if val == k_I or val == k_A: matches += 1
                    if matches > best[0]:
                        best = (matches, (base, mult, off, mode))
                    if matches == n_con and n_con >= 4:
                        ks = []
                        v = mult
                        for i in range(n_runes):
                            ks.append((v + off) % MOD)
                            v = (v * base) % MOD
                        plain = decrypt(cipher, ks, mode)
                        ic = ioc(plain)
                        wm, tw, words = count_words(plain, word_lengths)
                        if ic > 1.3 or wm >= 3:
                            txt = to_text(plain[:60])
                            print(f"    ★ base={base} mult={mult} off={off} {mode}: IoC={ic:.4f} words={wm}/{tw} | {txt}")
                            results.append((ic, wm, f"power base={base} mult={mult} off={off} {mode}", plain, words))
    
    m, params = best
    print(f"    Best: {m}/{n_con} matches" + (f" params={params}" if params else ""))
    return results

def search_totient_prime_lfsr(cipher, word_lengths, single_positions, n_runes):
    """Test P56-style: k_i = phi(prime_i) % 29 with various orderings/offsets"""
    import sympy
    print(f"\n  Totient-prime stream (P56-style) with extended offsets...")
    
    # Generate lots of primes
    primes_list = list(sympy.primerange(2, 50000))
    results = []
    best = (0, None)
    n_con = len(single_positions)
    
    for mode in ['sub', 'beaufort', 'add']:
        cons = get_keystream_constraints(cipher, single_positions, mode)
        
        # Test offsets 0..5000
        for offset in range(0, 5001):
            if offset + n_runes > len(primes_list):
                break
            # totient stream
            matches_tot = 0
            matches_idx = 0
            matches_prime = 0
            for pos, k_I, k_A in cons:
                p = primes_list[offset + pos]
                phi_val = (p - 1) % MOD
                idx_val = (offset + pos) % MOD
                p_val = p % MOD
                if phi_val == k_I or phi_val == k_A: matches_tot += 1
                if idx_val == k_I or idx_val == k_A: matches_idx += 1
                if p_val == k_I or p_val == k_A: matches_prime += 1
            
            for matches, stype in [(matches_tot, 'totient'), (matches_idx, 'idx'), (matches_prime, 'prime')]:
                if matches > best[0]:
                    best = (matches, (offset, stype, mode))
                if matches == n_con and n_con >= 4:
                    if stype == 'totient':
                        ks = [(primes_list[offset+i]-1)%MOD for i in range(n_runes)]
                    elif stype == 'idx':
                        ks = [(offset+i)%MOD for i in range(n_runes)]
                    else:
                        ks = [primes_list[offset+i]%MOD for i in range(n_runes)]
                    plain = decrypt(cipher, ks, mode)
                    ic = ioc(plain)
                    wm, tw, words = count_words(plain, word_lengths)
                    if ic > 1.3 or wm >= 3:
                        txt = to_text(plain[:60])
                        print(f"    ★ offset={offset} {stype} {mode}: IoC={ic:.4f} words={wm}/{tw} | {txt}")
                        results.append((ic, wm, f"prime_off{offset}_{stype}_{mode}", plain, words))
    
    m, params = best
    print(f"    Best: {m}/{n_con} matches" + (f" params={params}" if params else ""))
    return results

# ============================================================
# Main
# ============================================================

def search_page(page_num):
    cipher, word_lengths = load_runes(page_num)
    if cipher is None:
        print(f"Page {page_num}: no rune file")
        return
    
    single_positions = get_single_rune_positions(word_lengths)
    n_runes = len(cipher)
    n_con = len(single_positions)
    
    print(f"\n{'='*100}")
    print(f"PAGE {page_num} — {n_runes} runes, {len(word_lengths)} words, "
          f"{n_con} single-rune words at {single_positions}")
    
    # Show constraint values
    for mode in ['sub', 'beaufort']:
        cons = get_keystream_constraints(cipher, single_positions, mode)
        pairs = [(f"pos{p}: c={cipher[p]}({GP_LETTERS[cipher[p]]}) → k={kI}(I)/{kA}(A)") for p,kI,kA in cons]
        print(f"  [{mode}] {'; '.join(pairs[:6])}")
    print(f"{'='*100}")
    
    if n_con < 2:
        print(f"  Only {n_con} single-rune words, skipping")
        return
    
    all_results = []
    
    # 1. Affine
    all_results.extend(search_affine(cipher, word_lengths, single_positions, n_runes))
    
    # 2. Quadratic (only if manageable)
    if n_con >= 3:
        all_results.extend(search_quadratic(cipher, word_lengths, single_positions, n_runes))
    
    # 3. Power/geometric
    all_results.extend(search_power(cipher, word_lengths, single_positions, n_runes))
    
    # 4. LFSR L=1..4 (algebraic)
    max_L = min(4, n_con)
    if n_con >= 7:
        max_L = 5  # can afford L=5 for pages with many constraints
    all_results.extend(search_lfsr_algebraic(cipher, word_lengths, single_positions, n_runes, page_num, (1, max_L)))
    
    # 5. Totient-prime streams with extended offset search
    try:
        all_results.extend(search_totient_prime_lfsr(cipher, word_lengths, single_positions, n_runes))
    except ImportError:
        print("  (sympy not available, skipping prime stream test)")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"TOP RESULTS FOR PAGE {page_num}:")
    all_results.sort(key=lambda x: (-x[1], -x[0]))
    for ic, wm, desc, plain, words in all_results[:10]:
        txt = to_text(plain[:70])
        matched = [w for w in words if w.upper() in COMMON_WORDS]
        print(f"  IoC={ic:.4f} words={wm}/{len(words)} — {desc}")
        print(f"    {txt}")
        if matched: print(f"    Matched: {matched[:15]}")
    if not all_results:
        print("  No results with IoC > 1.3 or ≥3 word matches")

def main():
    # P28 has 12 single-rune words (best), P24 has 9, P21 has 7
    pages = [28, 24, 21]
    for pnum in pages:
        search_page(pnum)
        print()

if __name__ == '__main__':
    main()
