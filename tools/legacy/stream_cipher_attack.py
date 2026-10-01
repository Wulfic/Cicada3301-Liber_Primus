#!/usr/bin/env python3
"""
Systematic stream cipher attack on ALL unsolved pages.
Tests:
  1. P56-style totient stream: plain = (cipher - (p_i - 1)) % 29
  2. Prime stream: plain = (cipher - p_i) % 29  
  3. Prime totient with offset and starting prime variations
  4. Fibonacci-indexed primes
  5. Single-rune word constraint validation
  6. Berlekamp-Massey on partial keystream from single-rune cribs
"""

import sys, os, math, json
from collections import Counter
from pathlib import Path
from itertools import product

N = 29

RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP = {r: i for i, r in enumerate(RUNES)}
SEPS = set(".-\u2022 \n")

def sieve_primes(limit):
    is_p = [True]*(limit+1); is_p[0]=is_p[1]=False
    for i in range(2, int(limit**0.5)+1):
        if is_p[i]:
            for j in range(i*i, limit+1, i): is_p[j]=False
    return [x for x in range(limit+1) if is_p[x]]

PRIMES = sieve_primes(100000)  # way more than enough

def load_page(page_num):
    """Load runes and word structure for a page."""
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

def bigram_score(vals):
    GOOD = {(16,8),(8,18),(10,9),(18,4),(24,9),(9,23),(16,10),(22,0),(10,16),(10,15)}
    return sum(1 for i in range(len(vals)-1) if (vals[i],vals[i+1]) in GOOD)

# Key insight from community: single-rune words MUST be I(10) or A(24)
def single_rune_check(flat, words, keystream, mode="sub"):
    """Check how many single-rune words decrypt to I or A."""
    pos = 0; hits = 0; total = 0
    for w in words:
        if len(w) == 1:
            total += 1
            c = flat[pos]
            k = keystream[pos] if pos < len(keystream) else 0
            if mode == "sub": p = (c - k) % N
            elif mode == "add": p = (c + k) % N
            else: p = (k - c) % N
            if p in (10, 24): hits += 1
        pos += len(w)
    return hits, total

def score_decrypt(flat, words, keystream, mode="sub"):
    """Combined score: IoC + bigrams + single-rune constraint."""
    if mode == "sub": plain = [(flat[i] - keystream[i]) % N for i in range(len(flat))]
    elif mode == "add": plain = [(flat[i] + keystream[i]) % N for i in range(len(flat))]
    else: plain = [(keystream[i] - flat[i]) % N for i in range(len(flat))]
    
    ic = ioc(plain)
    bg = bigram_score(plain)
    sr_hits, sr_total = single_rune_check(flat, words, keystream, mode)
    
    return ic, bg, sr_hits, sr_total, plain

# ── Stream generators ──────────────────────────────────────────────────────

def totient_stream(start_idx=0, length=2000):
    """phi(p_i) = p_i - 1 for prime sequence starting at index start_idx"""
    return [(PRIMES[start_idx + i] - 1) % N for i in range(length)]

def prime_mod_stream(start_idx=0, length=2000):
    """p_i mod 29"""
    return [PRIMES[start_idx + i] % N for i in range(length)]

def prime_minus_stream(start_idx=0, length=2000, sub=1):
    """(p_i - sub) mod 29"""
    return [(PRIMES[start_idx + i] - sub) % N for i in range(length)]

def fibonacci_prime_stream(length=2000):
    """Primes indexed by Fibonacci numbers: p_{fib(i)}"""
    fibs = [0, 1]
    while fibs[-1] < len(PRIMES):
        fibs.append(fibs[-1] + fibs[-2])
    ks = []
    for i in range(length):
        idx = fibs[i] if i < len(fibs) and fibs[i] < len(PRIMES) else i
        ks.append((PRIMES[idx] - 1) % N)
    return ks

def cumulative_totient_stream(start_idx=0, length=2000):
    """Running sum of totients mod 29: sum(phi(p_j) for j=0..i) mod 29"""
    s = 0; ks = []
    for i in range(length):
        s = (s + PRIMES[start_idx + i] - 1) % N
        ks.append(s)
    return ks

def prime_gap_stream(start_idx=0, length=2000):
    """p_{i+1} - p_i mod 29"""
    return [(PRIMES[start_idx + i + 1] - PRIMES[start_idx + i]) % N for i in range(length)]

# ── LFSR over GF(29) ──────────────────────────────────────────────────────

def lfsr_keystream(init, taps, length):
    n = len(init); state = list(init); ks = []
    for _ in range(length):
        ks.append(state[0])
        nv = sum(t*s for t,s in zip(taps, state)) % N
        state = state[1:] + [nv]
    return ks

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def mod_inv(a, m=N):
    g, x, _ = extended_gcd(a % m, m)
    return x % m if g == 1 else None

def berlekamp_massey_gf29(seq):
    """BM algorithm over GF(29)."""
    n = len(seq)
    c = [0]*(n+1); b = [0]*(n+1); c[0]=1; b[0]=1
    L=0; m=1; bb=1
    for i in range(n):
        d = seq[i]
        for j in range(1, L+1): d = (d + c[j]*seq[i-j]) % N
        d %= N
        if d == 0: m += 1
        elif 2*L <= i:
            t = list(c)
            inv_bb = mod_inv(bb)
            if inv_bb is None: return None
            coeff = (d * inv_bb) % N
            for j in range(m, n+1):
                if j-m < len(b): c[j] = (c[j] - coeff*b[j-m]) % N
            L = i+1-L; b = list(t); bb = d; m = 1
        else:
            inv_bb = mod_inv(bb)
            if inv_bb is None: return None
            coeff = (d * inv_bb) % N
            for j in range(m, n+1):
                if j-m < len(b): c[j] = (c[j] - coeff*b[j-m]) % N
            m += 1
    return c[:L+1], L

# ── Main tests ──────────────────────────────────────────────────────────────

def main():
    os.chdir(Path(__file__).parent.parent)
    
    # Test ALL unsolved pages
    unsolved = list(range(0, 56))  # Pages 0-55
    # Exclude truly solved ones from session data
    solved = {1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17}  # solved via Vigenere etc
    unsolved = [p for p in unsolved if p not in solved]
    
    print("=" * 80)
    print("SYSTEMATIC STREAM CIPHER ATTACK ON UNSOLVED PAGES")
    print("=" * 80)
    
    # Define all stream generators to try
    streams = {}
    for si in range(10):  # starting prime index 0-9
        streams[f"totient_s{si}"] = lambda l, s=si: totient_stream(s, l)
        streams[f"prime_mod_s{si}"] = lambda l, s=si: prime_mod_stream(s, l)
    
    streams["cumul_totient_s0"] = lambda l: cumulative_totient_stream(0, l)
    streams["cumul_totient_s1"] = lambda l: cumulative_totient_stream(1, l)
    streams["prime_gap_s0"] = lambda l: prime_gap_stream(0, l)
    streams["prime_gap_s1"] = lambda l: prime_gap_stream(1, l)
    
    # p_i - 2, p_i - 3 variants
    for sub in [2, 3]:
        streams[f"prime_minus{sub}_s0"] = lambda l, s=sub: prime_minus_stream(0, l, s)
    
    modes = ["sub", "add", "beaufort"]
    
    results = []
    
    for page_num in unsolved:
        flat, words = load_page(page_num)
        if not flat or len(flat) < 10:
            continue
        
        n_runes = len(flat)
        n_singles = sum(1 for w in words if len(w) == 1)
        
        best_for_page = None
        
        for stream_name, stream_fn in streams.items():
            ks = stream_fn(n_runes)
            for mode in modes:
                ic, bg, sr_h, sr_t, plain = score_decrypt(flat, words, ks, mode)
                
                combined = ic + bg * 0.1 + (sr_h / max(sr_t, 1)) * 5
                
                if combined > 2.0 or ic > 1.5:
                    entry = {
                        'page': page_num, 'stream': stream_name, 'mode': mode,
                        'ioc': ic, 'bigrams': bg, 'singles': f"{sr_h}/{sr_t}",
                        'combined': combined,
                        'sample': ''.join(RUNEGLISH[p] for p in plain[:50]),
                    }
                    results.append(entry)
                    
                    if best_for_page is None or combined > best_for_page['combined']:
                        best_for_page = entry
        
        if best_for_page:
            print(f"P{page_num:02d} ({n_runes}r, {n_singles}s) BEST: {best_for_page['stream']} {best_for_page['mode']} "
                  f"IoC={best_for_page['ioc']:.4f} bg={best_for_page['bigrams']} s={best_for_page['singles']} "
                  f"c={best_for_page['combined']:.3f}")
            print(f"    -> {best_for_page['sample'][:60]}")
        else:
            print(f"P{page_num:02d} ({n_runes}r, {n_singles}s) -- no hits above threshold")
    
    # ── LFSR(2) brute force on promising pages ──
    print("\n" + "=" * 80)
    print("LFSR(2) BRUTE FORCE ON SELECT PAGES")
    print("=" * 80)
    
    # Pick pages with most single-rune words (best crib opportunities)
    page_singles = []
    for page_num in unsolved:
        flat, words = load_page(page_num)
        if not flat: continue
        n_singles = sum(1 for w in words if len(w) == 1)
        if n_singles >= 3:
            page_singles.append((page_num, len(flat), n_singles))
    
    page_singles.sort(key=lambda x: -x[2])
    print(f"\nPages with most single-rune words:")
    for pn, nr, ns in page_singles[:20]:
        print(f"  P{pn:02d}: {nr} runes, {ns} single-rune words")
    
    # Test LFSR(2) on top 3 pages with most singles
    for pn, nr, ns in page_singles[:3]:
        flat, words = load_page(pn)
        print(f"\n--- LFSR(2) on P{pn:02d} ({nr} runes) ---")
        
        best_lfsr = []
        for s0 in range(N):
            for s1 in range(N):
                for c0 in range(N):
                    for c1 in range(N):
                        ks = lfsr_keystream([s0,s1], [c0,c1], nr)
                        for mode in modes:
                            ic, bg, sr_h, sr_t, plain = score_decrypt(flat, words, ks, mode)
                            combined = ic + bg*0.1 + (sr_h/max(sr_t,1))*5
                            if combined > 3.0:
                                best_lfsr.append({
                                    'state': (s0,s1), 'taps': (c0,c1), 'mode': mode,
                                    'ioc': ic, 'bg': bg, 'singles': f"{sr_h}/{sr_t}",
                                    'combined': combined,
                                    'sample': ''.join(RUNEGLISH[p] for p in plain[:60]),
                                })
            if s0 % 5 == 0:
                print(f"  s0={s0}/28 ... {len(best_lfsr)} hits")
        
        best_lfsr.sort(key=lambda x: -x['combined'])
        print(f"\n  Top 10 LFSR(2) for P{pn:02d}:")
        for r in best_lfsr[:10]:
            print(f"    state={r['state']} taps={r['taps']} {r['mode']} IoC={r['ioc']:.4f} bg={r['bg']} s={r['singles']} c={r['combined']:.3f}")
            print(f"      -> {r['sample'][:60]}")
    
    # ── Single-rune crib-drag + BM ──
    print("\n" + "=" * 80)
    print("SINGLE-RUNE CRIB DRAG + BERLEKAMP-MASSEY")
    print("=" * 80)
    
    for pn, nr, ns in page_singles[:5]:
        if ns < 5: continue
        flat, words = load_page(pn)
        
        # Get single-rune positions
        pos = 0; single_positions = []
        for w in words:
            if len(w) == 1:
                single_positions.append((pos, flat[pos]))
            pos += len(w)
        
        print(f"\nP{pn:02d}: {ns} singles at positions: {[sp[0] for sp in single_positions]}")
        
        # For each mode, try all I/A combos for the first 8 singles
        max_combos = min(ns, 8)
        for mode in modes:
            best_bm = None
            for combo in product([10, 24], repeat=max_combos):
                # Extract keystream values
                ks_known = {}
                for i, (spos, sval) in enumerate(single_positions[:max_combos]):
                    if mode == "sub": ks_known[spos] = (sval - combo[i]) % N
                    elif mode == "add": ks_known[spos] = (combo[i] - sval) % N
                    else: ks_known[spos] = (sval + combo[i]) % N
                
                # Try BM on the known values (need consecutive for this to work)
                # Check for any consecutive runs
                sorted_pos = sorted(ks_known.keys())
                for run_start in range(len(sorted_pos)):
                    # Find longest consecutive run from run_start
                    consec = [ks_known[sorted_pos[run_start]]]
                    for j in range(run_start+1, len(sorted_pos)):
                        if sorted_pos[j] == sorted_pos[j-1] + 1:
                            consec.append(ks_known[sorted_pos[j]])
                        else:
                            break
                    
                    if len(consec) >= 4:
                        result = berlekamp_massey_gf29(consec)
                        if result:
                            poly, lfsr_len = result
                            if 1 <= lfsr_len <= len(consec)//2:
                                # Reconstruct full keystream
                                # Need to start from position 0, not sorted_pos[run_start]
                                # This is tricky without knowing the full initial state
                                pass
            
            # Instead of BM on sparse data, try interpolation approach:
            # For LFSR of degree d, if we know ks at positions p1...pk,
            # and k >= 2d, we can set up a system of equations
            # But positions may not be consecutive, making this hard.
            
            # Simpler: just check which stream generators match the single-rune constraints
            for stream_name, stream_fn in streams.items():
                ks = stream_fn(nr)
                sr_h, sr_t = single_rune_check(flat, words, ks, mode)
                if sr_h == sr_t and sr_t >= 3:
                    ic, bg, _, _, plain = score_decrypt(flat, words, ks, mode)
                    print(f"  P{pn:02d} {stream_name} {mode}: ALL {sr_t} singles match! "
                          f"IoC={ic:.4f} bg={bg}")
                    print(f"    -> {''.join(RUNEGLISH[p] for p in plain[:50])}")

    print("\nDone.")

if __name__ == "__main__":
    main()
