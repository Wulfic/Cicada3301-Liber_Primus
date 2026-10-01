#!/usr/bin/env python3
"""
LFSR solver with HARD single-rune word constraint using linear algebra.
For LFSR(d), precompute the state-to-keystream mapping at singleton positions,
then solve/verify linear systems instead of brute-forcing all initial states.

For LFSR(2): only 29^2=841 tap combos to search (not 29^4=707K).
For LFSR(3): only 29^3=24389 tap combos.
"""

import sys, os, math, time
from collections import Counter
from pathlib import Path
from itertools import product

N = 29

RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP = {r: i for i, r in enumerate(RUNES)}
SEPS = set(".-\u2022 \n")

# Modular inverse table for GF(29)
INV29 = [0]*N
for i in range(1, N):
    INV29[i] = pow(i, N-2, N)

def load_page(page_num):
    path = Path(f"pages/page_{page_num:02d}/runes.txt")
    if not path.exists(): return None, None
    text = path.read_text(encoding='utf-8')
    words = []; current = []
    for ch in text:
        if ch in GP: current.append(GP[ch])
        elif ch in SEPS:
            if current: words.append(current); current = []
    if current: words.append(current)
    flat = [r for w in words for r in w]
    return flat, words

def ioc(vals):
    n = len(vals)
    if n < 2: return 0.0
    freq = Counter(vals)
    return sum(f*(f-1) for f in freq.values()) * N / (n*(n-1))

ENGLISH_BIGRAMS = {
    (16,8): 50, (8,18): 40, (10,9): 30, (18,4): 25, (24,9): 30,
    (9,23): 25, (16,10): 20, (22,0): 15, (10,16): 18, (10,15): 15,
    (24,20): 15, (15,16): 20, (18,9): 15, (22,9): 12, (24,16): 18,
    (16,18): 15, (8,24): 12, (18,15): 12, (10,9): 30, (3,0): 12,
    (0,3): 10, (4,18): 10, (24,4): 10, (16,3): 10,
}

def bigram_score(vals):
    return sum(ENGLISH_BIGRAMS.get((vals[i], vals[i+1]), 0) for i in range(len(vals)-1))

def get_single_positions(flat, words):
    pos = 0; singles = []
    for w in words:
        if len(w) == 1:
            singles.append((pos, flat[pos]))
        pos += len(w)
    return singles

def mat_mul(A, B, n=N):
    """Multiply two dxd matrices mod n."""
    d = len(A)
    return [[(sum(A[i][k]*B[k][j] for k in range(d))) % n for j in range(d)] for i in range(d)]

def mat_pow(M, exp, n=N):
    """Matrix exponentiation mod n."""
    d = len(M)
    result = [[1 if i==j else 0 for j in range(d)] for i in range(d)]
    base = [row[:] for row in M]
    while exp > 0:
        if exp & 1:
            result = mat_mul(result, base, n)
        base = mat_mul(base, base, n)
        exp >>= 1
    return result

def lfsr_ks_full(init, taps, length):
    """Generate full LFSR keystream."""
    d = len(init); st = list(init); ks = []
    for _ in range(length):
        ks.append(st[0])
        nv = sum(t*s for t,s in zip(taps, st)) % N
        st = st[1:] + [nv]
    return ks

def decrypt(flat, ks, mode):
    if mode == "sub": return [(flat[i] - ks[i]) % N for i in range(len(flat))]
    elif mode == "add": return [(flat[i] + ks[i]) % N for i in range(len(flat))]
    else: return [(ks[i] - flat[i]) % N for i in range(len(flat))]

def words_to_text(flat, words, ks, mode):
    plain = decrypt(flat, ks, mode)
    pos = 0; result = []
    for w in words:
        rg = ''.join(RUNEGLISH[plain[pos+i]] for i in range(len(w)))
        result.append(rg)
        pos += len(w)
    return ' '.join(result)

def ks_values_for_mode(singles, mode):
    """For each singleton, compute the 2 possible keystream values (I=10 or A=24)."""
    result = []
    for pos, cv in singles:
        if mode == "sub":
            v_i = (cv - 10) % N  # plain = cipher - ks => ks = cipher - plain
            v_a = (cv - 24) % N
        elif mode == "add":
            v_i = (10 - cv) % N  # plain = cipher + ks => ks = plain - cipher
            v_a = (24 - cv) % N
        else:  # beaufort
            v_i = (cv + 10) % N  # plain = ks - cipher => ks = plain + cipher
            v_a = (cv + 24) % N
        result.append((pos, v_i, v_a))
    return result

def solve_lfsr2_algebraic(singles_ks, nr, taps_c0, taps_c1):
    """
    For LFSR(2) with given taps (c0, c1):
      s[n+2] = c0*s[n] + c1*s[n+1] (mod 29)
    
    The transition matrix M = [[0, 1], [c0, c1]].
    s[n] = (M^n)[0][0]*s0 + (M^n)[0][1]*s1.
    
    For each singleton, ks[pos] must be one of 2 values.
    Use first 2 singletons to solve for s0,s1, then verify rest.
    Returns list of valid (s0, s1) tuples.
    """
    M = [[0, 1], [taps_c0, taps_c1]]
    
    # Precompute coefficients: ks[pos] = a_pos*s0 + b_pos*s1 (mod 29)
    coeffs = []
    for pos, v_i, v_a in singles_ks:
        Mp = mat_pow(M, pos)
        a, b = Mp[0][0] % N, Mp[0][1] % N
        coeffs.append((a, b, v_i, v_a))
    
    solutions = []
    # Use first 2 singletons to solve, then verify the rest
    a0, b0, vi0, va0 = coeffs[0]
    a1, b1, vi1, va1 = coeffs[1]
    
    for v0 in (vi0, va0):
        for v1 in (vi1, va1):
            # System: a0*s0 + b0*s1 = v0, a1*s0 + b1*s1 = v1
            det = (a0*b1 - a1*b0) % N
            if det == 0:
                # Singular — try all s0 or skip
                if a0 == 0 and b0 == 0:
                    if v0 != 0: continue
                    # Any (s0, s1) works for first eq — need more constraints
                    # Fall through to brute force s0,s1 for this case
                    for s0 in range(N):
                        for s1 in range(N):
                            valid = True
                            for a, b, vi, va in coeffs:
                                val = (a*s0 + b*s1) % N
                                if val != vi and val != va:
                                    valid = False; break
                            if valid:
                                solutions.append((s0, s1))
                    continue
                else:
                    # Determinant is 0 but row isn't zero — check consistency
                    # Try to find solutions along the null space
                    continue
            
            inv_det = INV29[det]
            s0 = (inv_det * (b1*v0 - b0*v1)) % N
            s1 = (inv_det * (a0*v1 - a1*v0)) % N
            
            # Verify against ALL constraints
            valid = True
            for a, b, vi, va in coeffs[2:]:
                val = (a*s0 + b*s1) % N
                if val != vi and val != va:
                    valid = False; break
            if valid:
                solutions.append((s0, s1))
    
    return solutions

def solve_lfsr3_algebraic(singles_ks, nr, c0, c1, c2):
    """
    For LFSR(3) with taps (c0, c1, c2):
      s[n+3] = c0*s[n] + c1*s[n+1] + c2*s[n+2] (mod 29)
    
    Transition matrix M = [[0,1,0],[0,0,1],[c0,c1,c2]].
    s[n] = (M^n)[0][0]*s0 + (M^n)[0][1]*s1 + (M^n)[0][2]*s2.
    """
    M = [[0,1,0],[0,0,1],[c0,c1,c2]]
    
    coeffs = []
    for pos, v_i, v_a in singles_ks:
        Mp = mat_pow(M, pos)
        a, b, c = Mp[0][0] % N, Mp[0][1] % N, Mp[0][2] % N
        coeffs.append((a, b, c, v_i, v_a))
    
    solutions = []
    # Use first 3 singletons to solve, verify rest
    if len(coeffs) < 3: return solutions
    
    a0,b0,c0_,vi0,va0 = coeffs[0]
    a1,b1,c1_,vi1,va1 = coeffs[1]
    a2,b2,c2_,vi2,va2 = coeffs[2]
    
    for v0 in (vi0, va0):
        for v1 in (vi1, va1):
            for v2 in (vi2, va2):
                # 3x3 system: solve for s0, s1, s2
                # Using Cramer's rule
                mat = [[a0,b0,c0_],[a1,b1,c1_],[a2,b2,c2_]]
                rhs = [v0, v1, v2]
                
                # Compute determinant
                det = (a0*(b1*c2_ - b2*c1_) - b0*(a1*c2_ - a2*c1_) + c0_*(a1*b2 - a2*b1)) % N
                if det == 0: continue
                
                inv_det = INV29[det]
                
                # Cramer's rule
                s0 = (inv_det * (v0*(b1*c2_ - b2*c1_) - b0*(v1*c2_ - v2*c1_) + c0_*(v1*b2 - v2*b1))) % N
                s1 = (inv_det * (a0*(v1*c2_ - v2*c1_) - v0*(a1*c2_ - a2*c1_) + c0_*(a1*v2 - a2*v1))) % N
                s2 = (inv_det * (a0*(b1*v2 - b2*v1) - b0*(a1*v2 - a2*v1) + v0*(a1*b2 - a2*b1))) % N
                
                # Verify against ALL remaining constraints
                valid = True
                for a, b, c, vi, va in coeffs[3:]:
                    val = (a*s0 + b*s1 + c*s2) % N
                    if val != vi and val != va:
                        valid = False; break
                if valid:
                    solutions.append((s0, s1, s2))
    
    return solutions

def main():
    os.chdir(Path(__file__).parent.parent)

    # Find pages with most singles
    all_pages = []
    for pn in range(56):
        flat, words = load_page(pn)
        if not flat: continue
        singles = get_single_positions(flat, words)
        if len(singles) >= 3:
            all_pages.append((pn, len(flat), singles, flat, words))
    
    all_pages.sort(key=lambda x: -len(x[2]))
    
    print("Pages sorted by single-rune word count:")
    for pn, nr, singles, _, _ in all_pages[:20]:
        print(f"  P{pn:02d}: {nr} runes, {len(singles)} singles at {[s[0] for s in singles]}")
    
    modes = ["sub", "add", "beaufort"]
    
    # ========== LFSR(2) ALGEBRAIC SOLVE ==========
    print(f"\n{'='*70}")
    print("LFSR(2) ALGEBRAIC SOLVE — 29^2 = 841 tap combos per page per mode")
    print(f"{'='*70}")
    
    for pn, nr, singles, flat, words in all_pages[:10]:
        print(f"\n--- P{pn:02d} ({nr} runes, {len(singles)} singles) ---")
        t0 = time.time()
        hits = []
        
        for mode in modes:
            sks = ks_values_for_mode(singles, mode)
            for c0 in range(N):
                for c1 in range(N):
                    sols = solve_lfsr2_algebraic(sks, nr, c0, c1)
                    for s0, s1 in sols:
                        ks = lfsr_ks_full([s0, s1], [c0, c1], nr)
                        plain = decrypt(flat, ks, mode)
                        ic = ioc(plain)
                        bg = bigram_score(plain)
                        hits.append({
                            'degree': 2,
                            'state': (s0, s1), 'taps': (c0, c1), 'mode': mode,
                            'ioc': ic, 'bg': bg,
                            'score': ic*100 + bg*0.5,
                            'text': words_to_text(flat, words, ks, mode)[:100],
                        })
        
        dt = time.time() - t0
        print(f"  Time: {dt:.1f}s | Candidates: {len(hits)}")
        hits.sort(key=lambda x: -x['score'])
        for r in hits[:10]:
            print(f"  [{r['mode']:8s}] s=({r['state'][0]:2d},{r['state'][1]:2d}) t=({r['taps'][0]:2d},{r['taps'][1]:2d}) IoC={r['ioc']:.4f} bg={r['bg']:4d} score={r['score']:.1f}")
            print(f"    -> {r['text']}")
    
    # ========== LFSR(3) ALGEBRAIC SOLVE ==========
    print(f"\n{'='*70}")
    print("LFSR(3) ALGEBRAIC SOLVE — 29^3 = 24389 tap combos per page per mode")
    print(f"{'='*70}")
    
    for pn, nr, singles, flat, words in all_pages[:8]:
        if len(singles) < 4: continue  # need 4+ for overdetermined LFSR(3)
        print(f"\n--- P{pn:02d} ({nr} runes, {len(singles)} singles) ---")
        t0 = time.time()
        hits = []
        
        for mode in modes:
            sks = ks_values_for_mode(singles, mode)
            for c0 in range(N):
                for c1 in range(N):
                    for c2 in range(N):
                        sols = solve_lfsr3_algebraic(sks, nr, c0, c1, c2)
                        for s0, s1, s2 in sols:
                            ks = lfsr_ks_full([s0, s1, s2], [c0, c1, c2], nr)
                            plain = decrypt(flat, ks, mode)
                            ic = ioc(plain)
                            bg = bigram_score(plain)
                            hits.append({
                                'degree': 3,
                                'state': (s0, s1, s2), 'taps': (c0, c1, c2),
                                'mode': mode, 'ioc': ic, 'bg': bg,
                                'score': ic*100 + bg*0.5,
                                'text': words_to_text(flat, words, ks, mode)[:100],
                            })
        
        dt = time.time() - t0
        print(f"  Time: {dt:.1f}s | Candidates: {len(hits)}")
        hits.sort(key=lambda x: -x['score'])
        for r in hits[:10]:
            t = r['taps']
            s = r['state']
            print(f"  [{r['mode']:8s}] s=({s[0]:2d},{s[1]:2d},{s[2]:2d}) t=({t[0]:2d},{t[1]:2d},{t[2]:2d}) IoC={r['ioc']:.4f} bg={r['bg']:4d} score={r['score']:.1f}")
            print(f"    -> {r['text']}")
    
    # ========== LFSR(4) ALGEBRAIC — Top pages only ==========
    print(f"\n{'='*70}")
    print("LFSR(4) ALGEBRAIC SOLVE — 29^4 = 707281 taps (top 3 pages only)")
    print(f"{'='*70}")
    
    for pn, nr, singles, flat, words in all_pages[:3]:
        if len(singles) < 5: continue
        print(f"\n--- P{pn:02d} ({nr} runes, {len(singles)} singles) ---")
        t0 = time.time()
        hits = []
        checked = 0
        
        for mode in modes:
            sks = ks_values_for_mode(singles, mode)
            # LFSR(4): M = [[0,1,0,0],[0,0,1,0],[0,0,0,1],[c0,c1,c2,c3]]
            # Use first 4 singletons to solve, verify rest
            # Need at least 5 singletons for overdetermined system
            
            for c0 in range(N):
                for c1 in range(N):
                    for c2 in range(N):
                        for c3 in range(N):
                            checked += 1
                            M = [[0,1,0,0],[0,0,1,0],[0,0,0,1],[c0,c1,c2,c3]]
                            
                            # Compute coefficients for first 4 singletons
                            coeffs = []
                            for pos, v_i, v_a in sks[:4]:
                                Mp = mat_pow(M, pos)
                                coeffs.append((Mp[0][0]%N, Mp[0][1]%N, Mp[0][2]%N, Mp[0][3]%N, v_i, v_a))
                            
                            # Rest for verification
                            verify_coeffs = []
                            for pos, v_i, v_a in sks[4:]:
                                Mp = mat_pow(M, pos)
                                verify_coeffs.append((Mp[0][0]%N, Mp[0][1]%N, Mp[0][2]%N, Mp[0][3]%N, v_i, v_a))
                            
                            # Try all 2^4=16 I/A assignments for first 4 singletons
                            for bits in range(16):
                                vs = []
                                for j in range(4):
                                    vs.append(coeffs[j][4] if (bits>>j)&1 else coeffs[j][5])
                                
                                # Build 4x4 matrix and solve
                                A = [[coeffs[j][k] for k in range(4)] for j in range(4)]
                                
                                # Gaussian elimination mod 29
                                aug = [A[j][:] + [vs[j]] for j in range(4)]
                                ok = True
                                for col in range(4):
                                    # Find pivot
                                    pivot = -1
                                    for row in range(col, 4):
                                        if aug[row][col] % N != 0:
                                            pivot = row; break
                                    if pivot == -1: ok = False; break
                                    aug[col], aug[pivot] = aug[pivot], aug[col]
                                    inv = INV29[aug[col][col] % N]
                                    for k in range(5):
                                        aug[col][k] = (aug[col][k] * inv) % N
                                    for row in range(4):
                                        if row == col: continue
                                        f = aug[row][col]
                                        for k in range(5):
                                            aug[row][k] = (aug[row][k] - f*aug[col][k]) % N
                                
                                if not ok: continue
                                sol = [aug[j][4] for j in range(4)]
                                
                                # Verify against remaining singletons
                                valid = True
                                for a, b, c, d, vi, va in verify_coeffs:
                                    val = (a*sol[0] + b*sol[1] + c*sol[2] + d*sol[3]) % N
                                    if val != vi and val != va:
                                        valid = False; break
                                if not valid: continue
                                
                                # Reconstruct full keystream
                                ks = lfsr_ks_full(sol, [c0,c1,c2,c3], nr)
                                plain = decrypt(flat, ks, mode)
                                ic = ioc(plain)
                                bg = bigram_score(plain)
                                hits.append({
                                    'degree': 4, 'state': tuple(sol),
                                    'taps': (c0,c1,c2,c3), 'mode': mode,
                                    'ioc': ic, 'bg': bg,
                                    'score': ic*100 + bg*0.5,
                                    'text': words_to_text(flat, words, ks, mode)[:100],
                                })
                    if c1 == 0 and checked % 50000 == 0:
                        elapsed = time.time() - t0
                        print(f"    checked {checked:,} taps ... {len(hits)} hits ({elapsed:.0f}s)")
        
        dt = time.time() - t0
        print(f"  Time: {dt:.1f}s | Checked: {checked:,} | Candidates: {len(hits)}")
        hits.sort(key=lambda x: -x['score'])
        for r in hits[:10]:
            t = r['taps']
            s = r['state']
            print(f"  [{r['mode']:8s}] s={s} t={t} IoC={r['ioc']:.4f} bg={r['bg']:4d} score={r['score']:.1f}")
            print(f"    -> {r['text']}")
    
    print("\n" + "="*70)
    print("ALL LFSR TESTS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
