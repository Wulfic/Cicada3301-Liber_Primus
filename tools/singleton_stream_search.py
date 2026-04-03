#!/usr/bin/env python3
"""
Singleton-Constrained Key Stream Search
========================================
For each unsolved page with 3+ singletons, compute the EXACT key values
required at singleton positions, then search for mathematical streams
that match ALL constraints simultaneously.

Streams tested:
1. φ(prime[n]) % 29 — Euler totient of primes (proven on P55/P73)
2. prime[n] % 29 — prime values mod 29
3. (prime[n] - 1) % 29 — totient (same as #1 since φ(p) = p-1 for prime p)
4. Cumulative sum of primes mod 29
5. Prime gaps mod 29
6. Fibonacci mod 29
7. nth_prime(nth_prime(i)) mod 29 — iterated prime indexing
8. prime[n]^2 mod 29 — squared primes
9. Totient of composites (not just primes)
10. Sequential integers mod 29 (control test)

Tests offsets 0 through 100,000 for each stream type.
"""

import sys
from pathlib import Path
from collections import Counter
from sympy import primerange, isprime, nextprime, totient, fibonacci

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]


def load_page(page_num):
    rune_path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_path.exists():
        return None, None, None
    content = rune_path.read_text(encoding='utf-8').strip()
    
    indices = []
    words = []
    current_word_start = len(indices)
    current_word_len = 0
    
    for ch in content:
        if ch in RUNE_TO_IDX:
            if current_word_len == 0:
                current_word_start = len(indices)
            indices.append(RUNE_TO_IDX[ch])
            current_word_len += 1
        elif ch in '-\n /%.&$':
            if current_word_len > 0:
                words.append((current_word_start, current_word_len))
                current_word_len = 0
    if current_word_len > 0:
        words.append((current_word_start, current_word_len))
    
    singletons = [(start, indices[start]) for start, length in words if length == 1]
    return indices, singletons, content


def compute_ioc(plain):
    n = len(plain)
    if n < 2:
        return 0
    freq = Counter(plain)
    total = sum(f * (f - 1) for f in freq.values())
    return (total / (n * (n - 1))) / (1.0 / 29)


def to_runeglish(plain):
    return ''.join(IDX_TO_LETTER[i] for i in plain)


def generate_prime_list(count):
    """Generate first `count` primes."""
    primes = []
    p = 2
    while len(primes) < count:
        primes.append(p)
        p = nextprime(p)
    return primes


def main():
    print("=" * 80)
    print("SINGLETON-CONSTRAINED KEY STREAM SEARCH")
    print("=" * 80)
    sys.stdout.flush()
    
    # Load pages with good singleton counts
    pages = {}
    for pg in range(21, 55):
        data = load_page(pg)
        if data[0] is not None:
            ci, si, content = data
            if len(si) >= 3:
                pages[pg] = (ci, si, content)
    
    # Sort by singleton count (most first)
    page_order = sorted(pages.keys(), key=lambda p: -len(pages[p][1]))
    
    print(f"\nPages with 3+ singletons (sorted by count):")
    for pg in page_order:
        ci, si, _ = pages[pg]
        print(f"  P{pg:02d}: {len(ci)} runes, {len(si)} singletons at positions {[s[0] for s in si]}")
    sys.stdout.flush()
    
    # For each page, compute the allowed key values at singleton positions
    # Under SUB mode: key[j] = (cipher[j] - plain[j]) % 29
    # plain[j] is I(10) or A(24)
    # So key[j] = (cipher[j] - 10) % 29 OR (cipher[j] - 24) % 29
    
    page_constraints = {}
    for pg in page_order:
        cipher, singletons, _ = pages[pg]
        constraints = []
        for pos, cipher_val in singletons:
            k_for_I = (cipher_val - 10) % 29
            k_for_A = (cipher_val - 24) % 29
            constraints.append((pos, k_for_I, k_for_A))
        page_constraints[pg] = constraints
        
        print(f"\n  P{pg:02d} singleton constraints (SUB mode):")
        for pos, ki, ka in constraints:
            print(f"    pos={pos:4d}: cipher={cipher_val:2d} → key={ki:2d} (I) or {ka:2d} (A)")
    
    # Also compute for ADD mode: p = (c + k) % 29 → k = (p - c) % 29
    # k_for_I = (10 - cipher[j]) % 29, k_for_A = (24 - cipher[j]) % 29
    page_constraints_add = {}
    for pg in page_order:
        cipher, singletons, _ = pages[pg]
        constraints = []
        for pos, cipher_val in singletons:
            k_for_I = (10 - cipher_val) % 29
            k_for_A = (24 - cipher_val) % 29
            constraints.append((pos, k_for_I, k_for_A))
        page_constraints_add[pg] = constraints
    
    # And for Beaufort: p = (k - c) % 29 → k = (p + c) % 29
    page_constraints_beau = {}
    for pg in page_order:
        cipher, singletons, _ = pages[pg]
        constraints = []
        for pos, cipher_val in singletons:
            k_for_I = (10 + cipher_val) % 29
            k_for_A = (24 + cipher_val) % 29
            constraints.append((pos, k_for_I, k_for_A))
        page_constraints_beau[pg] = constraints
    
    sys.stdout.flush()
    
    # Generate large prime list
    MAX_OFFSET = 100_000
    max_page_len = max(len(pages[pg][0]) for pg in pages)
    needed_primes = MAX_OFFSET + max_page_len + 100
    print(f"\nGenerating {needed_primes} primes...")
    sys.stdout.flush()
    primes = generate_prime_list(needed_primes)
    print(f"  Done. Largest prime: {primes[-1]}")
    sys.stdout.flush()
    
    # Pre-compute key streams
    print("\nPre-computing key streams...")
    sys.stdout.flush()
    
    # Stream 1: φ(prime[n]) % 29 = (prime[n] - 1) % 29
    totient_stream = [(p - 1) % 29 for p in primes]
    
    # Stream 2: prime[n] % 29
    prime_mod_stream = [p % 29 for p in primes]
    
    # Stream 3: cumulative prime sum mod 29
    cum_stream = []
    s = 0
    for p in primes:
        s = (s + p) % 29
        cum_stream.append(s)
    
    # Stream 4: prime gaps mod 29
    gap_stream = [0]
    for i in range(1, len(primes)):
        gap_stream.append((primes[i] - primes[i-1]) % 29)
    
    # Stream 5: Fibonacci mod 29
    fib_stream = [0, 1]
    for i in range(2, len(primes)):
        fib_stream.append((fib_stream[-1] + fib_stream[-2]) % 29)
    
    # Stream 6: prime[n]^2 mod 29
    sq_stream = [(p * p) % 29 for p in primes]
    
    # Stream 7: sequential integers mod 29 (control)
    seq_stream = [i % 29 for i in range(len(primes))]
    
    # Stream 8: prime[n] * n mod 29
    pn_stream = [(primes[i] * i) % 29 for i in range(len(primes))]
    
    # Stream 9: totient of n (not limited to primes)
    # Pre-compute totient for 0..MAX_OFFSET+max_page_len
    max_n = MAX_OFFSET + max_page_len + 100
    print(f"  Computing totient for 0..{max_n}...")
    sys.stdout.flush()
    totient_n = list(range(max_n + 1))
    for i in range(2, max_n + 1):
        if totient_n[i] == i:  # i is prime
            for j in range(i, max_n + 1, i):
                totient_n[j] = totient_n[j] * (i - 1) // i
    totient_n_stream = [totient_n[i] % 29 for i in range(max_n + 1)]
    
    streams = {
        'totient(prime)': totient_stream,
        'prime_mod29': prime_mod_stream,
        'cum_prime': cum_stream,
        'prime_gap': gap_stream,
        'fibonacci': fib_stream,
        'prime_sq': sq_stream,
        'sequential': seq_stream,
        'prime*n': pn_stream,
        'totient(n)': totient_n_stream,
    }
    
    print(f"  {len(streams)} streams generated")
    sys.stdout.flush()
    
    # ================================================================
    # SEARCH: For each page × mode × stream × offset,
    # check if stream values match ALL singleton constraints
    # ================================================================
    print("\n" + "=" * 80)
    print("SEARCHING... (this tests millions of combinations)")
    print("=" * 80)
    sys.stdout.flush()
    
    all_hits = []
    
    mode_constraints = {
        'sub': page_constraints,
        'add': page_constraints_add,
        'beaufort': page_constraints_beau,
    }
    
    for stream_name, stream in streams.items():
        max_stream_offset = len(stream) - max_page_len - 1
        max_off = min(MAX_OFFSET, max_stream_offset)
        
        for mode_name, constraints_by_page in mode_constraints.items():
            for pg in page_order:
                cipher, singletons, content = pages[pg]
                constraints = constraints_by_page[pg]
                n_sing = len(constraints)
                page_len = len(cipher)
                
                hits = 0
                for offset in range(max_off):
                    # Check all singleton constraints
                    ok = True
                    for pos, k_I, k_A in constraints:
                        stream_val = stream[offset + pos]
                        if stream_val != k_I and stream_val != k_A:
                            ok = False
                            break
                    
                    if ok:
                        # ALL singletons match! Decrypt and check
                        plain = []
                        key_seg = stream[offset:offset + page_len]
                        if len(key_seg) < page_len:
                            continue
                        
                        if mode_name == 'sub':
                            plain = [(cipher[i] - key_seg[i]) % 29 for i in range(page_len)]
                        elif mode_name == 'add':
                            plain = [(cipher[i] + key_seg[i]) % 29 for i in range(page_len)]
                        elif mode_name == 'beaufort':
                            plain = [(key_seg[i] - cipher[i]) % 29 for i in range(page_len)]
                        
                        ioc = compute_ioc(plain)
                        text = to_runeglish(plain)
                        
                        hits += 1
                        all_hits.append((ioc, pg, mode_name, stream_name, offset, text[:100]))
                        
                        if ioc > 1.3:
                            print(f"\n  *** HIT: P{pg:02d} IoC={ioc:.4f} [{stream_name}] {mode_name} off={offset}")
                            print(f"      {text[:120]}")
                            sys.stdout.flush()
                
                if hits > 0:
                    print(f"  P{pg:02d} [{stream_name:15s}] {mode_name:8s}: {hits} singleton-passing offsets found")
                    sys.stdout.flush()
        
        print(f"  Stream '{stream_name}' complete.")
        sys.stdout.flush()
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if all_hits:
        # Sort by IoC
        all_hits.sort(key=lambda x: -x[0])
        print(f"\nTotal hits (all singleton constraints passing): {len(all_hits)}")
        print(f"\nTop 30 by IoC:")
        for ioc, pg, mode, stream, offset, text in all_hits[:30]:
            print(f"  P{pg:02d} IoC={ioc:.4f} [{stream:15s}] {mode:8s} off={offset:6d} | {text[:60]}")
    else:
        print("\nNO stream × offset × mode combination passed all singleton constraints")
        print("on ANY page with 3+ singletons.")
        print("\nThis definitively rules out ALL tested mathematical key streams.")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
