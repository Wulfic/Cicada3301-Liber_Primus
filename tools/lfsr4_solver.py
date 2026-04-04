#!/usr/bin/env python3
"""
LFSR Degree 4 Algebraic Solver for Liber Primus
=================================================
Testing LFSR of degree 4 over GF(29) on P28 (12 singletons = strongest constraint).

LFSR recurrence: key[n] = c1*key[n-1] + c2*key[n-2] + c3*key[n-3] + c4*key[n-4] (mod 29)
Initial state: key[0..3]
Output: key[4], key[5], ... (or from key[0])

Strategy:
1. Enumerate all c1,c2,c3,c4 ∈ {0..28}^4 = 707,281 tap vectors
2. For each tap, compute T^k matrices for singleton positions (k = offset of singleton)
3. In GF(29), each singleton at pos k gives: [T^k * s0]_0 ∈ {I_val, A_val}
4. Pick first 4 singletons, enumerate 2^4=16 I/A combos → solve 4×4 linear system for s0
5. Check if remaining 8 singletons are satisfied
6. If yes: decrypt full page and check English

Also test P21-30 (fewer singletons, but still useful).

Optimization: skip c=(0,0,0,0) and c=(1,0,0,0) (trivial or degenerate LFSRs).
"""

import sys, time, itertools
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28),
]}
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
           'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
M = 29
I_IDX, A_IDX = 10, 24

def load_runes_with_positions(page_num):
    """Load runes and track word positions/singleton info."""
    path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not path.exists():
        return None, None, None
    with open(path, encoding='utf-8') as f:
        text = f.read()
    words = []; current = []
    seps = set('-. \n\r\t\u2022/')
    for ch in text:
        if ch in RUNE_TO_IDX:
            current.append(RUNE_TO_IDX[ch])
        elif ch in seps:
            if current:
                words.append(tuple(current))
                current = []
    if current:
        words.append(tuple(current))
    flat = [r for w in words for r in w]
    word_sizes = [len(w) for w in words]
    # Find singleton positions in flat
    singleton_pos = []
    pos = 0
    for w in words:
        if len(w) == 1:
            singleton_pos.append(pos)
        pos += len(w)
    return flat, word_sizes, singleton_pos

def ioc(values):
    if len(values) < 2: return 0.0
    c = Counter(values)
    n = len(values)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def mod_inv(a, m=M):
    """Modular inverse in GF(29)."""
    if a % m == 0: return None
    g, x, _ = ext_gcd(a % m, m)
    return x % m if g == 1 else None

def ext_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = ext_gcd(b % a, a)
    return g, y - (b//a)*x, x

def mat_mul(A, B, m=M):
    """4×4 matrix multiplication mod m."""
    n = len(A)
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if A[i][k] == 0: continue
            for j in range(n):
                C[i][j] = (C[i][j] + A[i][k] * B[k][j]) % m
    return C

def mat_pow(T, p, m=M):
    """Matrix power T^p mod m using repeated squaring."""
    n = len(T)
    result = [[1 if i==j else 0 for j in range(n)] for i in range(n)]  # identity
    base = [row[:] for row in T]
    while p > 0:
        if p & 1:
            result = mat_mul(result, base, m)
        base = mat_mul(base, base, m)
        p >>= 1
    return result

def make_companion(c1, c2, c3, c4, m=M):
    """Companion matrix for LFSR with taps c1,c2,c3,c4."""
    return [
        [c1 % m, c2 % m, c3 % m, c4 % m],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
    ]

def solve_linear_gf(A, b, m=M):
    """Gaussian elimination in GF(m). Returns solution or None if no unique solution."""
    n = len(b)
    # Augmented matrix [A | b]
    aug = [list(A[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if aug[row][col] % m != 0:
                pivot = row
                break
        if pivot is None:
            return None  # singular
        aug[col], aug[pivot] = aug[pivot], aug[col]
        # Scale pivot row
        inv = mod_inv(aug[col][col], m)
        if inv is None:
            return None
        for j in range(col, n+1):
            aug[col][j] = (aug[col][j] * inv) % m
        # Eliminate
        for row in range(n):
            if row == col: continue
            factor = aug[row][col]
            if factor == 0: continue
            for j in range(col, n+1):
                aug[row][j] = (aug[row][j] - factor * aug[col][j]) % m
    return [aug[i][n] for i in range(n)]

def score_text(plain, word_sizes):
    LP = {'THE','AND','FOR','ARE','NOT','YOU','ALL','THIS','THAT','WITH','HAVE',
          'SELF','TRUTH','SEEK','WITHIN','SACRED','HOLY','WISDOM','PATH','BEING',
          'EACH','KNOW','FOLLOW','INSTRUCTION','WELCOME','PILGRIM','END','EMERGE',
          'WILL','EVERY','DEEP','ABOVE','SAME','OTHER','SONG','LAW','COMMAND',
          'ONE','YOUR','DIVINE','CONSUME','PRESERVE','ADHERE','FOLLOW','FROM',
          'A','I'}
    words_text = []
    pos = 0
    for s in word_sizes:
        w = ''.join(IDX_TO[x] for x in plain[pos:pos+s] if 0 <= x < 29)
        words_text.append(w)
        pos += s
    return sum(len(w) * 4 for w in words_text if w in LP) + \
           sum(4 for w in words_text for lw in LP if len(lw) >= 3 and lw in w)

def lfsr_generate(state, c1, c2, c3, c4, length, m=M):
    """Generate LFSR output of given length."""
    s = list(state)  # [key[0], key[1], key[2], key[3]]
    out = list(s)
    for _ in range(length - 4):
        next_val = (c1*s[-1] + c2*s[-2] + c3*s[-3] + c4*s[-4]) % m
        s.append(next_val)
        out.append(next_val)
    return out

# ======================================================
# Run LFSR-4 solver on pages with high singleton count
# ======================================================
TARGET_PAGES = [28]  # P28 has 12 singletons (best constraint)
# Also try P21 (7), P24 (9), P25 (0 — skip), P26 (4), P27 (3), P29 (8), P30 (8)

for target_page in TARGET_PAGES:
    flat, word_sizes, singleton_pos = load_runes_with_positions(target_page)
    if flat is None:
        print(f"P{target_page}: could not load")
        continue
    
    n = len(flat)
    ns = len(singleton_pos)
    print(f"\nP{target_page}: {n} runes, {ns} singletons at positions {singleton_pos}")
    
    if ns < 4:
        print(f"Too few singletons for degree-4 constraint (need >= 4)")
        continue
    
    # Compute I/A key values for each singleton position
    # key[pos] = (flat[pos] - I) % 29 OR (flat[pos] - A) % 29
    singleton_ia = []
    for sp in singleton_pos:
        i_key = (flat[sp] - I_IDX) % M
        a_key = (flat[sp] - A_IDX) % M
        singleton_ia.append((i_key, a_key))
    
    print(f"Singleton key options (I/A): {singleton_ia[:6]}...")
    
    # Number of singletons to use for solving vs. verification
    solve_n = 4  # Use first 4 to solve 4×4 linear system
    verify_n = ns - solve_n  # Use rest for verification
    
    print(f"Using first {solve_n} singletons to solve, {verify_n} for verification")
    
    solutions_found = []
    
    t0 = time.time()
    tested = 0
    
    # Test all tap vectors c1,c2,c3,c4 ∈ {0..28}^4
    # OPTIMIZATION: skip all-zero taps and filter by primality?
    # Actually, we'll just iterate — with early termination
    
    # Test modes: sub (plain = cipher - key), add (plain = cipher + key), beaufort (plain = key - cipher)
    for mode in ['sub', 'add', 'beaufort']:
        if mode == 'sub':
            key_for_singleton = lambda sp, val: (flat[sp] - val) % M
        elif mode == 'add':
            key_for_singleton = lambda sp, val: (val - flat[sp]) % M
        else:  # beaufort: key - cipher = plain
            key_for_singleton = lambda sp, val: (val + flat[sp]) % M
        
        # Recompute singleton_ia for this mode
        s_ia = []
        for sp in singleton_pos:
            s_ia.append((key_for_singleton(sp, I_IDX), key_for_singleton(sp, A_IDX)))
        
        # Iterate over tap vectors
        for c1 in range(M):
            for c2 in range(M):
                for c3 in range(M):
                    for c4 in range(M):
                        tested += 1
                        if tested % 1000000 == 0:
                            elapsed = time.time() - t0
                            print(f"  [{mode}] Tested {tested:,} taps in {elapsed:.1f}s, {len(solutions_found)} solutions")
                        
                        # Build companion matrix
                        T = make_companion(c1, c2, c3, c4)
                        
                        # For each I/A combination of the first solve_n singletons:
                        for combo in itertools.product(range(2), repeat=solve_n):
                            # combo[j] ∈ {0,1} means I or A for j-th singleton (among first solve_n)
                            
                            # Build linear system: for each of first solve_n singletons at position p,
                            # the KEY output at position p is: [T^p * s0]_0 = desired_key
                            # where s0 = [key[3], key[2], key[1], key[0]] (initial state columns)
                            
                            # Compute T^(p-0) for each singleton position p
                            # State s0 = [key[0], key[1], key[2], key[3]]
                            # After p steps: s[p] = T^p * s[0]
                            # Output = first row of T^p dotted with s0
                            
                            A_mat = []
                            b_vec = []
                            
                            valid_combo = True
                            for j in range(solve_n):
                                sp = singleton_pos[j]
                                desired_key = s_ia[j][combo[j]]  # I or A key value
                                
                                Tp = mat_pow(T, sp)
                                # Output row (generates key[sp] from initial state)
                                row = Tp[0]  # first row
                                
                                A_mat.append(row)
                                b_vec.append(desired_key)
                            
                            # Solve 4×4 system
                            sol = solve_linear_gf(A_mat, b_vec)
                            if sol is None:
                                continue  # singular system
                            
                            s0 = sol  # initial state [key[0], key[1], key[2], key[3]]
                            
                            # Generate full LFSR sequence
                            try:
                                key_stream = lfsr_generate(s0, c1, c2, c3, c4, n)
                            except:
                                continue
                            
                            if len(key_stream) < n:
                                continue
                            
                            # Verify ALL singleton constraints
                            all_ok = True
                            for j in range(ns):
                                sp = singleton_pos[j]
                                ks = key_stream[sp]
                                if mode == 'sub':
                                    plain_val = (flat[sp] - ks) % M
                                elif mode == 'add':
                                    plain_val = (flat[sp] + ks) % M
                                else:
                                    plain_val = (ks - flat[sp]) % M
                                if plain_val not in (I_IDX, A_IDX):
                                    all_ok = False
                                    break
                            
                            if not all_ok:
                                continue
                            
                            # *** CANDIDATE FOUND ***
                            if mode == 'sub':
                                plain = [(flat[i] - key_stream[i]) % M for i in range(n)]
                            elif mode == 'add':
                                plain = [(flat[i] + key_stream[i]) % M for i in range(n)]
                            else:
                                plain = [(key_stream[i] - flat[i]) % M for i in range(n)]
                            
                            score = score_text(plain, word_sizes)
                            iv = ioc(plain)
                            text = ' '.join(''.join(IDX_TO[x] for x in plain[sum(word_sizes[:i]):sum(word_sizes[:i+1])]) 
                                            for i in range(min(20, len(word_sizes))))
                            
                            result = {
                                'mode': mode,
                                'taps': (c1, c2, c3, c4),
                                'state': s0,
                                'score': score,
                                'ioc': iv,
                                'text': text[:200]
                            }
                            solutions_found.append(result)
                            print(f"\n*** CANDIDATE FOUND ***")
                            print(f"  Mode: {mode}, Taps: ({c1},{c2},{c3},{c4}), State: {s0}")
                            print(f"  Score: {score}, IoC: {iv:.4f}")
                            print(f"  Text: {text[:150]}")
        
        elapsed = time.time() - t0
        print(f"\n[{mode}] Completed: {tested:,} taps tested in {elapsed:.1f}s")
        print(f"Total solutions found so far: {len(solutions_found)}")

print(f"\nFINAL: {len(solutions_found)} total solutions across all modes")
if solutions_found:
    solutions_found.sort(key=lambda x: -x['score'])
    print("Top 5:")
    for s in solutions_found[:5]:
        print(f"  [{s['mode']} taps={s['taps']}]: score={s['score']}, IoC={s['ioc']:.4f}")
        print(f"  {s['text'][:100]}")
