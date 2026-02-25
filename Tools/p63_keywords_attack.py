#!/usr/bin/env python3
"""
Comprehensive keyword attack using P63 grid keywords with CORRECT GP digraph mappings,
plus prime-position extraction + Deor running key method from P20.
Tests ALL unsolved pages (18-54).
"""

import os, sys, math
from collections import Counter

RUNE_TO_SHIFT = {
    '\u16a0': 0, '\u16a2': 1, '\u16a6': 2, '\u16a9': 3, '\u16b1': 4,
    '\u16b3': 5, '\u16b7': 6, '\u16b9': 7, '\u16bb': 8, '\u16be': 9,
    '\u16c1': 10, '\u16c2': 11, '\u16c7': 12, '\u16c8': 13, '\u16c9': 14,
    '\u16cb': 15, '\u16cf': 16, '\u16d2': 17, '\u16d6': 18, '\u16d7': 19,
    '\u16da': 20, '\u16dd': 21, '\u16df': 22, '\u16de': 23, '\u16aa': 24,
    '\u16ab': 25, '\u16a3': 26, '\u16e1': 27, '\u16e0': 28, '\u16c4': 11
}

SHIFT_TO_ENGLISH = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X', 15: 'S',
    16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG', 22: 'OE', 23: 'D',
    24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

def calc_ioc(shifts):
    if len(shifts) < 2: return 0
    freq = Counter(shifts)
    n = len(shifts)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

def decode(shifts):
    return ''.join(SHIFT_TO_ENGLISH.get(s, '?') for s in shifts)

def score_text(text):
    t = text.upper()
    bigrams = ['TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','ES','OR',
               'TE','ED','IS','IT','AL','AR','ST','TO','HA','OU','SE','WH']
    score = sum(t.count(bg) * 10 for bg in bigrams)
    words = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','WAS','ONE','OUR',
             'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','SOME',
             'WHEN','WHAT','THERE','WHICH','SHALL','EACH','FIND','WISDOM','TRUTH',
             'WITHIN','DEEP','PAGE','DUTY','PILGRIM','SEEK','WARNING','DIVINITY',
             'INSTAR','UNTO','DARKNESS','LIGHT','VOID','FORM','SHADOW','CABAL',
             'LOSS','KOAN','PARABLE','PRIMES','PRIME','CIRCUMFER']
    for w in words: score += t.count(w) * len(w) * 5
    return score

def sieve_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        if all(c % p for p in primes if p*p <= c):
            primes.append(c)
        c += 1
    return primes

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def parse_shifts(rune_text):
    shifts = []
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            shifts.append(RUNE_TO_SHIFT[ch])
    return shifts

def load_page(pages_dir, p):
    path = os.path.join(pages_dir, f'page_{p:02d}', 'runes.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    PRIMES = sieve_primes(3000)
    TOTIENTS = [(p - 1) % 29 for p in PRIMES]
    
    modes = {
        'sub': lambda c, k: (c - k) % 29,
        'beaufort': lambda c, k: (k - c) % 29,
        'add': lambda c, k: (c + k) % 29,
    }
    
    # P63 grid keywords with CORRECT GP digraph-aware mappings
    # From KEY_HINTS_FOR_UNSOLVED_PAGES.md
    KEYWORDS = {
        'SUOID':     [15, 1, 3, 10, 23],
        'VOID':      [1, 3, 10, 23],
        'MOBIUS':     [19, 3, 17, 10, 1, 15],
        'AETHEREAL':  [24, 18, 2, 18, 4, 18, 24, 20],  # TH is digraph!
        'CARNAL':    [5, 24, 4, 9, 24, 20],
        'OBSCURA':   [3, 17, 15, 5, 1, 4, 24],
        'SHADOWS':   [15, 8, 24, 23, 3, 7, 15],
        'CABAL':     [5, 24, 17, 24, 20],
        'MOURNFUL':  [19, 3, 1, 4, 9, 0, 1, 20],  # M,O,U,R,N,F,U,L
        'ANALOG':    [24, 9, 24, 20, 3, 6],  # A,N,A,L,O,G
        'FORM':      [0, 3, 4, 19],  # F,O,R,M
        'BUFFERS':   [17, 1, 0, 0, 18, 4, 15],  # B,U,F,F,E,R,S
        'DIVINITY':  [23, 10, 1, 10, 9, 10, 16, 26],  # D,I,V,I,N,I,T,Y
        'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
        'YAHEOOPYJ': [26, 24, 8, 18, 3, 3, 13, 26, 11],
        'PRIMES':    [13, 4, 10, 19, 18, 15],
        'WISDOM':    [7, 10, 15, 23, 3, 19],
        'TRUTH':     [16, 4, 1, 2, 8],  # T,R,U,TH,H? or T,R,U,TH
        'TRUTH2':    [16, 4, 1, 16, 8],  # T,R,U,T,H (no digraph)
        'INSTAR':    [10, 9, 15, 16, 24, 4],
        'PILGRIM':   [13, 10, 20, 6, 4, 10, 19],
        'CONSUMPTION': [5, 3, 9, 15, 1, 19, 13, 16, 10, 3, 9],
        'CIRCUMFERENCE': [5, 10, 4, 5, 1, 19, 0, 18, 4, 18, 9, 5, 18],
        'WARNING':   [7, 24, 4, 9, 10, 21],  # W,A,R,N,I,NG
        'CICADA':    [5, 10, 5, 24, 23, 24],
        'LIBER':     [20, 10, 17, 18, 4],
        'LOSS':      [20, 3, 15, 15],
        'KOAN':      [5, 3, 24, 9],  # K=C=5
        'DEEP':      [23, 18, 18, 13],
        'END':       [18, 9, 23],
        'EMERGENCE': [18, 19, 18, 4, 6, 18, 9, 5, 18],
        'ADEPT':     [24, 23, 18, 13, 16],
    }
    
    # Load all pages 18-54
    pages = {}
    for p in range(18, 55):
        rt = load_page(pages_dir, p)
        if rt:
            shifts = parse_shifts(rt)
            if len(shifts) > 20:
                pages[p] = shifts
    
    print("=" * 80)
    print("P63 GRID KEYWORDS ON ALL UNSOLVED PAGES (18-54)")
    print(f"Testing {len(KEYWORDS)} keywords x {len(pages)} pages x 3 modes")
    print("=" * 80)
    
    all_hits = []
    
    for kw_name, key in KEYWORDS.items():
        period = len(key)
        for page_num in sorted(pages.keys()):
            cipher = pages[page_num]
            n = len(cipher)
            for mode_name, mode_func in modes.items():
                plain = [mode_func(cipher[i], key[i % period]) for i in range(n)]
                ioc = calc_ioc(plain)
                if ioc > 1.35:
                    text = decode(plain)
                    s = score_text(text)
                    all_hits.append((ioc, s, page_num, kw_name, mode_name, text[:150]))
                    if ioc > 1.5:
                        print(f"  *** P{page_num} '{kw_name}' {mode_name}: IoC={ioc:.3f} score={s}")
                        print(f"      {text[:150]}")
    
    # Show top hits
    if all_hits:
        all_hits.sort(key=lambda x: (x[0], x[1]), reverse=True)
        print(f"\nTop 20 results (IoC > 1.35):")
        for i, (ioc, s, pn, kw, mode, text) in enumerate(all_hits[:20]):
            print(f"  {i+1}. P{pn} '{kw}' {mode}: IoC={ioc:.3f} score={s}")
            print(f"     {text[:120]}")
    else:
        print("\nNo hits with IoC > 1.35")
    
    # ==================== PRIME POSITION EXTRACTION ====================
    print("\n" + "=" * 80)
    print("PRIME POSITION EXTRACTION + RUNNING KEY")
    print("Extract runes at prime-indexed positions, try Beaufort with Deor/etc")
    print("=" * 80)
    
    # Load Deor poem as key
    deor_path = os.path.join(repo_dir, 'LiberPrimus', 'reference', 'research', 'deor.txt')
    deor_shifts = []
    if os.path.exists(deor_path):
        with open(deor_path, 'r', encoding='utf-8') as f:
            deor_text = f.read()
        deor_shifts = parse_shifts(deor_text)
        print(f"Deor poem loaded: {len(deor_shifts)} rune shifts")
    else:
        # Try other paths
        for candidate in ['deor.txt', 'Deor.txt', 'deor_poem.txt']:
            p = os.path.join(repo_dir, 'LiberPrimus', 'reference', 'research', candidate)
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    deor_shifts = parse_shifts(f.read())
                print(f"Deor from {candidate}: {len(deor_shifts)} shifts")
                break
    
    if not deor_shifts:
        # Search for deor file
        print("Searching for Deor file...")
        for root, dirs, files in os.walk(repo_dir):
            for fn in files:
                if 'deor' in fn.lower():
                    fp = os.path.join(root, fn)
                    print(f"  Found: {fp}")
                    try:
                        with open(fp, 'r', encoding='utf-8') as f:
                            content = f.read()
                        ds = parse_shifts(content)
                        if len(ds) > len(deor_shifts):
                            deor_shifts = ds
                            print(f"    {len(ds)} rune shifts extracted")
                    except: pass
    
    for page_num in sorted(pages.keys()):
        cipher = pages[page_num]
        n = len(cipher)
        
        # Extract runes at prime positions (0-indexed)
        prime_runes = []
        prime_positions = []
        non_prime_runes = []
        for i in range(n):
            if is_prime(i):
                prime_runes.append(cipher[i])
                prime_positions.append(i)
            else:
                non_prime_runes.append(cipher[i])
        
        if len(prime_runes) < 10: continue
        
        # Check IoC of prime-position runes
        ioc_prime = calc_ioc(prime_runes)
        ioc_nonprime = calc_ioc(non_prime_runes)
        
        if ioc_prime > 1.15 or ioc_nonprime > 1.15:
            print(f"\n  P{page_num}: {n} runes, {len(prime_runes)} prime-pos, {len(non_prime_runes)} non-prime")
            print(f"    IoC prime-pos: {ioc_prime:.3f}, IoC non-prime: {ioc_nonprime:.3f}")
        
        # Try Beaufort with Deor on prime-position runes
        if deor_shifts and len(prime_runes) > 10:
            for mode_name, mode_func in modes.items():
                plain = [mode_func(prime_runes[i], deor_shifts[i % len(deor_shifts)]) 
                         for i in range(len(prime_runes))]
                ioc = calc_ioc(plain)
                if ioc > 1.4:
                    text = decode(plain)
                    s = score_text(text)
                    print(f"    Prime-pos + Deor {mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"      {text[:120]}")
            
            # Also try on non-prime runes
            for mode_name, mode_func in modes.items():
                plain = [mode_func(non_prime_runes[i], deor_shifts[i % len(deor_shifts)]) 
                         for i in range(len(non_prime_runes))]
                ioc = calc_ioc(plain)
                if ioc > 1.4:
                    text = decode(plain)
                    s = score_text(text)
                    print(f"    Non-prime + Deor {mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"      {text[:120]}")
        
        # Try totient stream on prime-position runes
        for mode_name, mode_func in modes.items():
            plain = [mode_func(prime_runes[i], TOTIENTS[i]) for i in range(len(prime_runes))]
            ioc = calc_ioc(plain)
            if ioc > 1.4:
                text = decode(plain)
                s = score_text(text)
                print(f"    Prime-pos + totient {mode_name}: IoC={ioc:.3f} score={s}")
                print(f"      {text[:120]}")
    
    # ==================== CAESAR + TRANSPOSITION (P31-54) ====================
    print("\n" + "=" * 80)
    print("CAESAR SHIFTS ON ALL PAGES (looking for high IoC after simple shift)")
    print("=" * 80)
    
    for page_num in sorted(pages.keys()):
        cipher = pages[page_num]
        n = len(cipher)
        
        for shift in range(29):
            for mode_name, mode_func in modes.items():
                plain = [mode_func(c, shift) for c in cipher]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode(plain)
                    s = score_text(text)
                    print(f"  P{page_num} Caesar shift={shift} {mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    {text[:120]}")
    
    # ==================== P32 NUMERIC GRID ANALYSIS ====================
    print("\n" + "=" * 80)
    print("P32 NUMERIC GRID ANALYSIS")
    print("=" * 80)
    
    grid = [
        [3258, 3222, 3152, 3038],
        [3278, 3299, 3298, 2838],
        [3288, 3294, 3296, 2472],
        [4516, 1206,  708, 1820],
    ]
    
    print("Grid mod 29:")
    for row in grid:
        vals = [v % 29 for v in row]
        letters = [decode([v]) for v in vals]
        print(f"  {vals} -> {''.join(letters)}")
    
    print("\nGrid mod various:")
    for mod in [29, 26, 37, 41, 43, 47]:
        flat = [v % mod for row in grid for v in row]
        print(f"  mod {mod}: {flat}")
    
    print("\nDifferences between adjacent values:")
    for row in grid:
        diffs = [row[i+1] - row[i] for i in range(len(row)-1)]
        print(f"  {diffs}")
    
    print("\nRow differences (row n+1 - row n):")
    for i in range(3):
        diffs = [grid[i+1][j] - grid[i][j] for j in range(4)]
        print(f"  Row {i+1}-{i}: {diffs}")
    
    print("\nRow sums, products mod 29:")
    for i, row in enumerate(grid):
        s = sum(row)
        p = 1
        for v in row: p = (p * v) % 29
        print(f"  Row {i}: sum={s} ({s%29}) prod_mod29={p}")
    
    # Could these be positions in combined LP text?
    print("\nAs positions in combined rune text:")
    all_shifts_combined = []
    for p in range(1, 75):
        rt = load_page(pages_dir, p)
        if rt:
            all_shifts_combined.extend(parse_shifts(rt))
    total_runes = len(all_shifts_combined)
    print(f"Total runes in LP: {total_runes}")
    
    for row in grid:
        chars = []
        for pos in row:
            if pos < total_runes:
                chars.append(decode([all_shifts_combined[pos]]))
            else:
                chars.append(f"[{pos}>max]")
        print(f"  {row} -> {chars}")
    
    # Try as GP prime indices
    print("\nAs GP prime indices (lookup prime value):")
    GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    for row in grid:
        for v in row:
            # Is v a GP prime?
            if v in GP_PRIMES:
                idx = GP_PRIMES.index(v)
                print(f"    {v} is GP prime #{idx} = {SHIFT_TO_ENGLISH[idx]}")
    
    # Factor analysis
    print("\nPrime factorization:")
    def factorize(n):
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    for row in grid:
        for v in row:
            f = factorize(v)
            gp_factors = [x for x in f if x in GP_PRIMES]
            print(f"    {v} = {' x '.join(map(str, f))}" + 
                  (f" (GP: {gp_factors})" if gp_factors else ""))
    
    # ==================== TOTIENT STREAM WITH F-SKIP VARIANTS ====================
    print("\n" + "=" * 80)
    print("TOTIENT STREAM WITH F-SKIP VARIANTS ON ALL PAGES")
    print("The P55 solution skips F runes when counting key position.")
    print("Try this on other pages with sub mode.")
    print("=" * 80)
    
    for page_num in sorted(pages.keys()):
        cipher = pages[page_num]
        n = len(cipher)
        
        # Standard totient with F-skip (P55 method)
        plain = []
        key_idx = 0
        for i in range(n):
            p = (cipher[i] - TOTIENTS[key_idx]) % 29
            plain.append(p)
            if p != 0:  # Skip F (value 0)
                key_idx += 1
            # Always increment (for comparison)
        
        ioc = calc_ioc(plain)
        if ioc > 1.25:
            text = decode(plain)
            s = score_text(text)
            print(f"  P{page_num} totient+F-skip: IoC={ioc:.3f} score={s}")
            print(f"    {text[:120]}")
        
        # Also try WITHOUT f-skip
        plain2 = [(cipher[i] - TOTIENTS[i]) % 29 for i in range(n)]
        ioc2 = calc_ioc(plain2)
        if ioc2 > 1.25:
            text = decode(plain2)
            s = score_text(text)
            print(f"  P{page_num} totient (no skip): IoC={ioc2:.3f} score={s}")
            print(f"    {text[:120]}")
        
        # Beaufort totient with F-skip
        plain3 = []
        key_idx = 0
        for i in range(n):
            p = (TOTIENTS[key_idx] - cipher[i]) % 29
            plain3.append(p)
            if p != 0:
                key_idx += 1
        
        ioc3 = calc_ioc(plain3)
        if ioc3 > 1.25:
            text = decode(plain3)
            s = score_text(text)
            print(f"  P{page_num} beaufort+F-skip: IoC={ioc3:.3f} score={s}")
            print(f"    {text[:120]}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
