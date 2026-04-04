#!/usr/bin/env python3
"""
LFSR Degree 4 Algebraic Solver — OPTIMIZED
===========================================
Key optimization: precompute T^sp OUTSIDE the I/A combo loop (16x speedup).
Tests all 29^4 = 707,281 tap vectors against P28 (12 singletons).

Runtime estimate: ~18-25 minutes for P28 x 3 modes.

Records output to data/lfsr4_results.txt.
"""

import sys, time, itertools
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"
OUT_FILE  = BASE / "data" / "lfsr4_results.txt"

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

def load_page(page_num):
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
    sp = []
    pos = 0
    for w in words:
        if len(w) == 1:
            sp.append(pos)
        pos += len(w)
    return flat, word_sizes, sp

def ext_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = ext_gcd(b % a, a)
    return g, y - (b//a)*x, x

def mod_inv(a, m=M):
    a = a % m
    if a == 0: return None
    g, x, _ = ext_gcd(a, m)
    return x % m if g == 1 else None

def mat_mul(A, B, m=M):
    n = 4
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if A[i][k] == 0: continue
            ak = A[i][k]
            for j in range(n):
                C[i][j] = (C[i][j] + ak * B[k][j]) % m
    return C

def mat_pow(T, p, m=M):
    n = 4
    result = [[1 if i==j else 0 for j in range(n)] for i in range(n)]
    base   = [row[:] for row in T]
    while p > 0:
        if p & 1:
            result = mat_mul(result, base, m)
        base = mat_mul(base, base, m)
        p >>= 1
    return result

def solve_linear_gf(A_mat, b_vec, m=M):
    n = 4
    aug = [list(A_mat[i]) + [b_vec[i]] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] % m), None)
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        inv = mod_inv(aug[col][col], m)
        if inv is None:
            return None
        for j in range(col, n+1):
            aug[col][j] = (aug[col][j] * inv) % m
        for row in range(n):
            if row == col: continue
            factor = aug[row][col]
            if factor == 0: continue
            for j in range(col, n+1):
                aug[row][j] = (aug[row][j] - factor * aug[col][j]) % m
    return [aug[i][n] for i in range(n)]

def lfsr_stream(state, taps, length, m=M):
    c1, c2, c3, c4 = taps
    s = list(state)
    out = list(s)
    for _ in range(length - 4):
        nv = (c1*s[-1] + c2*s[-2] + c3*s[-3] + c4*s[-4]) % m
        s.append(nv)
        out.append(nv)
    return out

LP_WORDS = {'THE','AND','FOR','ARE','NOT','ALL','THIS','THAT','WITH','HAVE',
            'SELF','TRUTH','SEEK','WITHIN','SACRED','HOLY','WISDOM','PATH',
            'BEING','EACH','KNOW','FOLLOW','INSTRUCTION','WELCOME','PILGRIM',
            'WILL','EVERY','DEEP','ABOVE','SAME','OTHER','SONG','LAW',
            'ONE','YOUR','DIVINE','CONSUME','PRESERVE','ADHERE','FROM',
            'A','I','YOU','HAS','CAN','LET','ITS','WHO','TO','OF','IS'}

def score_text(plain, word_sizes):
    score = 0
    pos = 0
    for s in word_sizes:
        w = ''.join(IDX_TO[x] for x in plain[pos:pos+s] if 0 <= x < 29)
        pos += s
        if w in LP_WORDS:
            score += len(w) * 4 + 8
        else:
            # Partial: check for common trigrams/substrings
            for lw in ['THE','AND','ING','ION','YOU','FOR','ARE','THAT','HAVE','WILL']:
                if lw in w:
                    score += 2
    return score

def ioc(values):
    if len(values) < 2: return 0.0
    c = Counter(values)
    n = len(values)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

# --- main ---

TARGET_PAGES = [28, 21, 24, 29, 30]

with open(OUT_FILE, 'w', encoding='utf-8') as log:
    def prnt(*args):
        s = ' '.join(str(a) for a in args)
        print(s)
        log.write(s + '\n')
        log.flush()

    prnt("="*60)
    prnt("LFSR-4 Algebraic Solver — Optimized Build")
    prnt(f"Testing pages: {TARGET_PAGES}")
    prnt(f"Start: {time.strftime('%H:%M:%S')}")
    prnt("="*60)

    for target_page in TARGET_PAGES:
        flat, word_sizes, sp = load_page(target_page)
        if flat is None:
            prnt(f"P{target_page}: not found"); continue
        ns = len(sp)
        prnt(f"\nP{target_page}: {len(flat)} runes, {ns} singletons at {sp}")
        if ns < 4:
            prnt("  Skipping — fewer than 4 singletons"); continue

        # For sub mode: key[pos] that decripts cipher[pos] to I or A
        solve_n = min(4, ns)  # use first 4 to solve 4x4 system
        verify_n = ns - solve_n

        best_score = 30
        solutions  = []

        for mode in ['sub', 'add', 'beaufort']:
            prnt(f"\n  Mode={mode}, {time.strftime('%H:%M:%S')}")
            t0 = time.time()
            tested = 0

            # Precompute singleton I/A key values for this mode
            def key_val(sp_i, plain_val):
                c = flat[sp_i]
                if mode == 'sub':    return (c - plain_val) % M
                elif mode == 'add':  return (plain_val - c) % M
                else:                return (plain_val + c) % M

            s_ia = [( key_val(sp_i, I_IDX), key_val(sp_i, A_IDX) ) for sp_i in sp]

            for c1 in range(M):
                if tested > 0 and c1 % 5 == 0:
                    el = time.time() - t0
                    rate = tested / el if el > 0 else 1
                    eta  = (M**4 - tested) / rate / 60
                    prnt(f"    c1={c1}: tested {tested:,}, {el:.0f}s, ETA ~{eta:.1f}min, sols={len(solutions)}")
                for c2 in range(M):
                    for c3 in range(M):
                        for c4 in range(M):
                            tested += 1
                            T = [[c1,c2,c3,c4],[1,0,0,0],[0,1,0,0],[0,0,1,0]]

                            # === KEY OPTIMIZATION ===
                            # Precompute T^sp for each singleton position OUTSIDE combo loop
                            rows = []       # rows[i] = first row of T^(sp[i])
                            for i in range(ns):
                                Tp  = mat_pow(T, sp[i])
                                rows.append(Tp[0])  # first row

                            # Now enumerate 2^solve_n I/A combinations
                            for combo in itertools.product(range(2), repeat=solve_n):
                                # Build 4x4 system from first solve_n singletons
                                A_m = [rows[i] for i in range(solve_n)]
                                b_v = [s_ia[i][combo[i]] for i in range(solve_n)]

                                sol = solve_linear_gf(A_m, b_v)
                                if sol is None:
                                    continue

                                # Verify remaining singletons
                                ok = True
                                for i in range(solve_n, ns):
                                    predicted = sum(rows[i][j] * sol[j] for j in range(4)) % M
                                    if predicted != s_ia[i][0] and predicted != s_ia[i][1]:
                                        ok = False
                                        break
                                if not ok:
                                    continue

                                # Full decryption
                                stream = lfsr_stream(sol, (c1,c2,c3,c4), len(flat))
                                if mode == 'sub':
                                    plain = [(flat[k] - stream[k]) % M for k in range(len(flat))]
                                elif mode == 'add':
                                    plain = [(flat[k] + stream[k]) % M for k in range(len(flat))]
                                else:
                                    plain = [(stream[k] - flat[k]) % M for k in range(len(flat))]

                                sc    = score_text(plain, word_sizes)
                                ioc_v = ioc(plain)
                                text  = ''.join(IDX_TO[x] if 0 <= x < 29 else '?' for x in plain)

                                prnt(f"\n  *** CANDIDATE ***")
                                prnt(f"  Page={target_page} mode={mode} taps=({c1},{c2},{c3},{c4}) state={sol}")
                                prnt(f"  IoC={ioc_v:.4f}  score={sc}")
                                prnt(f"  Text[:120]: {text[:120]}")
                                solutions.append((sc, ioc_v, mode, c1,c2,c3,c4, sol, text[:200]))

            elapsed = time.time() - t0
            prnt(f"  Done {mode}: {tested:,} tested in {elapsed:.1f}s, {len(solutions)} candidates")

        if solutions:
            prnt(f"\nTop candidates for P{target_page}:")
            for item in sorted(solutions, reverse=True)[:5]:
                prnt(f"  score={item[0]} IoC={item[1]:.4f} mode={item[2]} taps={item[3:7]} text={item[8][:80]}")

prnt(f"\nFinished all pages at {time.strftime('%H:%M:%S')}")
