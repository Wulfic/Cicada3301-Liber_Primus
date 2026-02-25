#!/usr/bin/env python3
"""
Intensive attack on smallest unsolved pages (49, 54, 22)
and verification of P17 claimed solution.
Also tests P54 with P55-like totient methods.
"""

import os, sys, math
from collections import Counter
from itertools import product

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

def decode_to_runeglish(shifts):
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
             'PRIMES','CONSUMPTION','CIRCUMFERENCE','UNTO','DARKNESS','LIGHT']
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

def parse_shifts(rune_text):
    shifts = []
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            shifts.append(RUNE_TO_SHIFT[ch])
    return shifts

def parse_words(rune_text):
    words = []
    current = []
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            current.append(RUNE_TO_SHIFT[ch])
        elif ch in '-\u2022. \n\t':
            if current:
                words.append(current)
                current = []
    if current:
        words.append(current)
    return words

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
    
    print("=" * 80)
    print("INTENSIVE SMALL PAGE ATTACK")
    print("=" * 80)
    
    # ==================== VERIFY PAGE 17 ====================
    print("\n--- VERIFY PAGE 17 (claimed: Vigenere reversed, key YAHEOOPYJ) ---")
    rt17 = load_page(pages_dir, 17)
    if rt17:
        cipher17 = parse_shifts(rt17)
        print(f"Page 17: {len(cipher17)} runes")
        
        # Try claimed key YAHEOOPYJ
        # Map to shifts: Y=26, A=24, H=8, E=18, O=3, O=3, P=13, Y=26, J=11
        key_str = 'YAHEOOPYJ'
        key_map = {'Y':26,'A':24,'H':8,'E':18,'O':3,'P':13,'J':11,'F':0,'U':1,
                   'TH':2,'R':4,'C':5,'G':6,'W':7,'N':9,'I':10,'X':14,'S':15,
                   'T':16,'B':17,'M':19,'L':20,'D':23}
        key = [key_map.get(c, 0) for c in key_str]
        period = len(key)
        
        # Try sub, beaufort, add modes
        for mode_name, mode_func in modes.items():
            plain = [mode_func(cipher17[i], key[i % period]) for i in range(len(cipher17))]
            ioc = calc_ioc(plain)
            text = decode_to_runeglish(plain)
            s = score_text(text)
            print(f"  {mode_name}: IoC={ioc:.3f} score={s}")
            print(f"  Text: {text[:200]}")
        
        # Also try reversed cipher
        cipher17_rev = cipher17[::-1]
        for mode_name, mode_func in modes.items():
            plain = [mode_func(cipher17_rev[i], key[i % period]) for i in range(len(cipher17_rev))]
            ioc = calc_ioc(plain)
            text = decode_to_runeglish(plain)
            s = score_text(text)
            print(f"  reversed+{mode_name}: IoC={ioc:.3f} score={s}")
            print(f"  Text: {text[:200]}")
        
        # Column IoC for period 9
        for p in [9, 3, 6, 18, 27]:
            columns = [[] for _ in range(p)]
            for i, s in enumerate(cipher17):
                columns[i % p].append(s)
            col_iocs = [calc_ioc(col) for col in columns if len(col) >= 3]
            avg = sum(col_iocs) / len(col_iocs) if col_iocs else 0
            print(f"  Period {p} column IoC: avg={avg:.3f} ({[f'{x:.2f}' for x in col_iocs[:5]]}...)")
    
    # ==================== PAGE 54 INTENSIVE ====================
    print("\n" + "=" * 80)
    print("PAGE 54 INTENSIVE (73 runes, immediately before solved P55)")
    print("=" * 80)
    
    rt54 = load_page(pages_dir, 54)
    if rt54:
        cipher54 = parse_shifts(rt54)
        words54 = parse_words(rt54)
        n54 = len(cipher54)
        print(f"Page 54: {n54} runes, {len(words54)} words")
        print(f"Words: {[len(w) for w in words54]}")
        print(f"Raw IoC: {calc_ioc(cipher54):.3f}")
        
        # Test A: Totient stream with various offsets (P55-like)
        print("\n  Test A: Totient stream with offsets 0-200")
        best_a = []
        for offset in range(300):
            for mode_name, mode_func in modes.items():
                stream = TOTIENTS[offset:offset+n54]
                if len(stream) < n54: continue
                plain = [mode_func(cipher54[i], stream[i]) for i in range(n54)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    best_a.append((ioc, s, offset, mode_name, text[:100]))
        
        if best_a:
            best_a.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, off, mode, text in best_a[:10]:
                print(f"    offset={off} {mode}: IoC={ioc:.3f} score={s}")
                print(f"      {text}")
        else:
            print("    No hits with IoC > 1.3")
        
        # Test B: Brute force ALL 29^2 Vigenere period-2 keys
        print("\n  Test B: Vigenere period 2 (841 keys)")
        best_b = []
        for k0 in range(29):
            for k1 in range(29):
                for mode_name, mode_func in modes.items():
                    plain = [mode_func(cipher54[i], [k0,k1][i%2]) for i in range(n54)]
                    ioc = calc_ioc(plain)
                    if ioc > 1.4:
                        text = decode_to_runeglish(plain)
                        s = score_text(text)
                        best_b.append((ioc, s, k0, k1, mode_name, text[:100]))
        
        if best_b:
            best_b.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, k0, k1, mode, text in best_b[:5]:
                print(f"    key=[{k0},{k1}] {mode}: IoC={ioc:.3f} score={s}")
                print(f"      {text}")
        else:
            print("    No hits with IoC > 1.4")
        
        # Test C: Vigenere period 3 (24389 keys)
        print("\n  Test C: Vigenere period 3 (24389 keys)")
        best_c = []
        for k0 in range(29):
            for k1 in range(29):
                for k2 in range(29):
                    key = [k0, k1, k2]
                    for mode_name, mode_func in modes.items():
                        plain = [mode_func(cipher54[i], key[i%3]) for i in range(n54)]
                        ioc = calc_ioc(plain)
                        if ioc > 1.5:
                            text = decode_to_runeglish(plain)
                            s = score_text(text)
                            best_c.append((ioc, s, key[:], mode_name, text[:100]))
        
        if best_c:
            best_c.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, key, mode, text in best_c[:5]:
                print(f"    key={key} {mode}: IoC={ioc:.3f} score={s}")
                print(f"      {text}")
        else:
            print("    No hits with IoC > 1.5")
        
        # Test D: Autokey with multi-character seeds (length 1-3)
        print("\n  Test D: Autokey with seeds length 1-3, sub/beaufort")
        best_d = []
        # Plaintext autokey: key[i] = seed[i] for i < len(seed), then key[i] = plain[i-len(seed)]
        for seed_len in range(1, 4):
            # Sample seed values to keep it tractable
            if seed_len == 1:
                seeds = [[s] for s in range(29)]
            elif seed_len == 2:
                seeds = [[s1, s2] for s1 in range(29) for s2 in range(29)]
            elif seed_len == 3:
                # Sample: all (a,a,a), (a,b,a), and random
                seeds = [[a,b,c] for a in range(29) for b in range(0,29,4) for c in range(0,29,4)]
            
            for seed in seeds:
                sl = len(seed)
                for mode_name, mode_func in [('sub', lambda c,k:(c-k)%29), ('beaufort', lambda c,k:(k-c)%29)]:
                    plain = []
                    for i in range(n54):
                        if i < sl:
                            k = seed[i]
                        else:
                            k = plain[i - sl]
                        p = mode_func(cipher54[i], k)
                        plain.append(p)
                    
                    ioc = calc_ioc(plain)
                    if ioc > 1.4:
                        text = decode_to_runeglish(plain)
                        s = score_text(text)
                        best_d.append((ioc, s, seed[:], mode_name, text[:100]))
        
        if best_d:
            best_d.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, seed, mode, text in best_d[:5]:
                print(f"    seed={seed} {mode}: IoC={ioc:.3f} score={s}")
                print(f"      {text}")
        else:
            print("    No hits")
        
        # Test E: P55 continues backward? If P55 starts at prime index 0, 
        # maybe P54 would use a negative offset, i.e. primes from a different range
        # Or P54+P55 is one continuous text
        print("\n  Test E: P54 as continuation/prefix of P55 totient stream")
        rt55 = load_page(pages_dir, 55)
        if rt55:
            c55 = parse_shifts(rt55)
            # Concatenate P54 + P55
            combined = cipher54 + c55
            for mode_name, mode_func in modes.items():
                stream = TOTIENTS[:len(combined)]
                plain = [mode_func(combined[i], stream[i]) for i in range(len(combined))]
                ioc_all = calc_ioc(plain)
                ioc54 = calc_ioc(plain[:n54])
                ioc55 = calc_ioc(plain[n54:])
                text = decode_to_runeglish(plain)
                if ioc_all > 1.2 or ioc55 > 1.4:
                    print(f"    P54+P55 {mode_name}: IoC_all={ioc_all:.3f} IoC54={ioc54:.3f} IoC55={ioc55:.3f}")
                    print(f"      P54 text: {text[:150]}")
                    print(f"      P55 text: {text[n54:n54+150]}")
        
        # Test F: Various number-theoretic streams
        print("\n  Test F: Various streams on P54")
        fib = [1, 1]
        for _ in range(200): fib.append(fib[-1]+fib[-2])
        
        test_streams = {
            'totient': TOTIENTS[:n54],
            'prime_mod29': [p % 29 for p in PRIMES[:n54]],
            'fibonacci': [f % 29 for f in fib[:n54]],
            'squares': [i*i % 29 for i in range(n54)],
            'cubes': [i*i*i % 29 for i in range(n54)],
            'triangular': [i*(i+1)//2 % 29 for i in range(n54)],
            'factorial_mod29': None,
            'prime_gaps': None,
            'twin_prime': None,
        }
        
        # Compute factorial mod 29
        facts = [1]
        for i in range(1, n54+1):
            facts.append(facts[-1] * i % 29)
        test_streams['factorial_mod29'] = facts[:n54]
        
        # Prime gaps
        gaps = [PRIMES[i+1] - PRIMES[i] for i in range(n54)]
        test_streams['prime_gaps'] = [g % 29 for g in gaps]
        
        # Twin prime indicator
        test_streams['twin_prime'] = [1 if PRIMES[i+1]-PRIMES[i]==2 else 0 for i in range(n54)]
        
        # Sigma (sum of divisors)
        def sigma(n):
            s = 0
            for i in range(1, n+1):
                if n % i == 0: s += i
            return s
        test_streams['sigma'] = [sigma(PRIMES[i]) % 29 for i in range(n54)]  # sigma(prime) = prime + 1
        
        # Mobius-like: (-1)^i alternating
        test_streams['alternating'] = [i % 2 for i in range(n54)]
        test_streams['alternating14'] = [14 * (i%2) for i in range(n54)]  # 0 or 14 (half of 29)
        
        for sname, stream in test_streams.items():
            if stream is None: continue
            for mode_name, mode_func in modes.items():
                plain = [mode_func(cipher54[i], stream[i]) for i in range(n54)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"    {sname}/{mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"      {text[:100]}")
    
    # ==================== PAGE 49 INTENSIVE ====================
    print("\n" + "=" * 80)
    print("PAGE 49 INTENSIVE (66 runes)")
    print("=" * 80)
    
    rt49 = load_page(pages_dir, 49)
    if rt49:
        cipher49 = parse_shifts(rt49)
        words49 = parse_words(rt49)
        n49 = len(cipher49)
        print(f"Page 49: {n49} runes, {len(words49)} words")
        print(f"Words: {[len(w) for w in words49]}")
        print(f"Raw IoC: {calc_ioc(cipher49):.3f}")
        
        # Identify single-rune words and their positions
        pos = 0
        single_rune_info = []
        for word in words49:
            if len(word) == 1:
                single_rune_info.append((pos, word[0]))
            pos += len(word)
        print(f"Single-rune words: {single_rune_info}")
        
        # Test A: All Caesar shifts
        print("\n  Test A: Caesar (29 shifts)")
        for shift in range(29):
            for mode_name, mode_func in modes.items():
                plain = [mode_func(c, shift) for c in cipher49]
                ioc = calc_ioc(plain)
                if ioc > 1.2:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"    shift={shift} {mode_name}: IoC={ioc:.3f} score={s} -> {text[:100]}")
        
        # Test B: Vigenere period 2 (841)
        print("\n  Test B: Vigenere period 2")
        best_b = []
        for k0 in range(29):
            for k1 in range(29):
                for mode_name, mode_func in modes.items():
                    plain = [mode_func(cipher49[i], [k0,k1][i%2]) for i in range(n49)]
                    ioc = calc_ioc(plain)
                    if ioc > 1.4:
                        text = decode_to_runeglish(plain)
                        s = score_text(text)
                        best_b.append((ioc, s, k0, k1, mode_name, text[:100]))
        if best_b:
            best_b.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, k0, k1, mode, text in best_b[:5]:
                print(f"    key=[{k0},{k1}] {mode}: IoC={ioc:.3f} score={s} -> {text[:80]}")
        else:
            print("    No hits")
        
        # Test C: Vigenere period 3 (24389)
        print("\n  Test C: Vigenere period 3")
        best_c = []
        for k0 in range(29):
            for k1 in range(29):
                for k2 in range(29):
                    key = [k0, k1, k2]
                    for mode_name, mode_func in modes.items():
                        plain = [mode_func(cipher49[i], key[i%3]) for i in range(n49)]
                        ioc = calc_ioc(plain)
                        if ioc > 1.5:
                            text = decode_to_runeglish(plain)
                            s = score_text(text)
                            best_c.append((ioc, s, key[:], mode_name, text[:100]))
        if best_c:
            best_c.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, key, mode, text in best_c[:5]:
                print(f"    key={key} {mode}: IoC={ioc:.3f} score={s} -> {text[:80]}")
        else:
            print("    No hits")
        
        # Test D: Totient stream with various offsets
        print("\n  Test D: Totient/prime stream offsets 0-500")
        best_d = []
        for offset in range(500):
            for mode_name, mode_func in modes.items():
                stream = TOTIENTS[offset:offset+n49]
                if len(stream) < n49: continue
                plain = [mode_func(cipher49[i], stream[i]) for i in range(n49)]
                ioc = calc_ioc(plain)
                if ioc > 1.35:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    best_d.append((ioc, s, offset, mode_name, text[:100]))
        if best_d:
            best_d.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, off, mode, text in best_d[:5]:
                print(f"    offset={off} {mode}: IoC={ioc:.3f} score={s} -> {text[:80]}")
        else:
            print("    No hits")
        
        # Test E: Autokey with seeds 1-3
        print("\n  Test E: Autokey seeds 1-2")
        best_e = []
        for seed_len in [1, 2]:
            if seed_len == 1:
                seeds = [[s] for s in range(29)]
            else:
                seeds = [[s1,s2] for s1 in range(29) for s2 in range(29)]
            
            for seed in seeds:
                sl = len(seed)
                for mode_name, mode_func in [('sub', lambda c,k:(c-k)%29), ('beaufort', lambda c,k:(k-c)%29)]:
                    plain = []
                    for i in range(n49):
                        k = seed[i] if i < sl else plain[i-sl]
                        p = mode_func(cipher49[i], k)
                        plain.append(p)
                    ioc = calc_ioc(plain)
                    if ioc > 1.4:
                        text = decode_to_runeglish(plain)
                        s = score_text(text)
                        best_e.append((ioc, s, seed[:], mode_name, text[:100]))
        if best_e:
            best_e.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, seed, mode, text in best_e[:5]:
                print(f"    seed={seed} {mode}: IoC={ioc:.3f} score={s} -> {text[:80]}")
        else:
            print("    No hits")
    
    # ==================== PAGE 22 INTENSIVE ====================
    print("\n" + "=" * 80)
    print("PAGE 22 INTENSIVE (131 runes, Friedman ~19)")
    print("=" * 80)
    
    rt22 = load_page(pages_dir, 22)
    if rt22:
        cipher22 = parse_shifts(rt22)
        words22 = parse_words(rt22)
        n22 = len(cipher22)
        print(f"Page 22: {n22} runes, {len(words22)} words")
        print(f"Words: {[len(w) for w in words22]}")
        print(f"Raw IoC: {calc_ioc(cipher22):.3f}")
        
        # Test A: Column IoC scan for periods 2-40
        print("\n  Test A: Column IoC for periods 2-40")
        for period in range(2, 41):
            cols = [[] for _ in range(period)]
            for i, s in enumerate(cipher22):
                cols[i % period].append(s)
            col_iocs = [calc_ioc(c) for c in cols if len(c) >= 5]
            if not col_iocs: continue
            avg = sum(col_iocs) / len(col_iocs)
            if avg > 1.15:
                min_col = min(len(c) for c in cols)
                print(f"    Period {period}: avg={avg:.3f} min_col_len={min_col}")
        
        # Test B: Vigenere period 2-3 brute force
        print("\n  Test B: Vigenere period 2 brute force")
        best_b = []
        for k0 in range(29):
            for k1 in range(29):
                for mode_name, mode_func in modes.items():
                    plain = [mode_func(cipher22[i], [k0,k1][i%2]) for i in range(n22)]
                    ioc = calc_ioc(plain)
                    if ioc > 1.3:
                        text = decode_to_runeglish(plain)
                        s = score_text(text)
                        best_b.append((ioc, s, [k0,k1], mode_name, text[:100]))
        if best_b:
            best_b.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, key, mode, text in best_b[:3]:
                print(f"    key={key} {mode}: IoC={ioc:.3f} score={s}")
        else:
            print("    No hits")
        
        # Test C: Totient stream offsets 0-500
        print("\n  Test C: Totient stream offsets")
        best_c = []
        for offset in range(500):
            for mode_name, mode_func in modes.items():
                stream = TOTIENTS[offset:offset+n22]
                if len(stream) < n22: continue
                plain = [mode_func(cipher22[i], stream[i]) for i in range(n22)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    best_c.append((ioc, s, offset, mode_name, text[:100]))
        if best_c:
            best_c.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, off, mode, text in best_c[:5]:
                print(f"    offset={off} {mode}: IoC={ioc:.3f} score={s} -> {text[:80]}")
        else:
            print("    No hits")
        
        # Test D: Autokey all seeds 0-28
        print("\n  Test D: Autokey all seeds")
        best_d = []
        for seed in range(29):
            for mode_name, mode_func in [('sub', lambda c,k:(c-k)%29), ('beaufort', lambda c,k:(k-c)%29)]:
                plain = []
                for i in range(n22):
                    k = seed if i == 0 else plain[i-1]
                    p = mode_func(cipher22[i], k)
                    plain.append(p)
                ioc = calc_ioc(plain)
                if ioc > 1.2:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    best_d.append((ioc, s, seed, mode_name, text[:100]))
        if best_d:
            best_d.sort(key=lambda x: x[0], reverse=True)
            for ioc, s, seed, mode, text in best_d[:5]:
                print(f"    seed={seed} {mode}: IoC={ioc:.3f} score={s} -> {text[:80]}")
        else:
            print("    No hits")
    
    # ==================== VIGENERE WITH CICADA KEYWORDS ====================
    print("\n" + "=" * 80)
    print("KEYWORD VIGENERE ON PAGES 49, 54, 22")
    print("Testing known Cicada-related keywords as Vigenere keys")
    print("=" * 80)
    
    keyword_list = [
        'DIVINITY', 'PRIMES', 'WISDOM', 'TRUTH', 'INSTAR', 'PILGRIM',
        'CONSUMPTION', 'CIRCUMFERENCE', 'CICADA', 'LIBER', 'PRIMUS',
        'WARNING', 'DARKNESS', 'LIGHT', 'FOLLOW', 'WHITE', 'RABBIT',
        'DEEP', 'WEB', 'PARABLE', 'MOBIUS', 'SHADOW', 'TOTIENT',
        'PRIME', 'GOLDEN', 'RATIO', 'FIBONACCI', 'SACRED', 'GEOMETRY',
        'THREE', 'THREE01', 'WELCOME', 'END', 'BEGIN', 'UNSEEING',
        'RO', 'LOSS', 'INSTRUCTION', 'COMMAND', 'KOAN', 'AN',
        'CABAL', 'SECT', 'GEMATRIA', 'EMERGENCE', 'ADEPT', 'INITIATE',
        'FREEDOM', 'LIBERTY', 'YAHEOOPYJ',
    ]
    
    # Map English letter to GP shift
    ENGLISH_TO_SHIFT = {
        'A':24, 'B':17, 'C':5, 'D':23, 'E':18, 'F':0, 'G':6, 'H':8,
        'I':10, 'J':11, 'K':5, 'L':20, 'M':19, 'N':9, 'O':3, 'P':13,
        'Q':5, 'R':4, 'S':15, 'T':16, 'U':1, 'V':1, 'W':7, 'X':14,
        'Y':26, 'Z':14
    }
    
    test_pages = {49: cipher49 if rt49 else [], 54: cipher54 if rt54 else [], 22: cipher22 if rt22 else []}
    
    for keyword in keyword_list:
        key = [ENGLISH_TO_SHIFT.get(c, 0) for c in keyword.upper()]
        period = len(key)
        
        for pnum, cipher in test_pages.items():
            if not cipher: continue
            n = len(cipher)
            for mode_name, mode_func in modes.items():
                plain = [mode_func(cipher[i], key[i % period]) for i in range(n)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"  P{pnum} '{keyword}' {mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    {text[:120]}")
    
    # ==================== VIGENERE PERIOD 4-5 ON P49 ====================
    print("\n" + "=" * 80)
    print("P49: Vigenere period 4 hill climb")
    print("=" * 80)
    
    if rt49:
        cipher = cipher49
        n = len(cipher)
        # For period 4, optimize each column separately
        for period in [4, 5, 6, 7]:
            for mode_name, mode_func in modes.items():
                best_key = []
                for col in range(period):
                    col_data = [cipher[i] for i in range(col, n, period)]
                    best_shift = 0
                    best_ioc = 0
                    for shift in range(29):
                        decrypted = [mode_func(c, shift) for c in col_data]
                        ioc = calc_ioc(decrypted)
                        if ioc > best_ioc:
                            best_ioc = ioc
                            best_shift = shift
                    best_key.append(best_shift)
                
                plain = [mode_func(cipher[i], best_key[i % period]) for i in range(n)]
                ioc_full = calc_ioc(plain)
                text = decode_to_runeglish(plain)
                s = score_text(text)
                if ioc_full > 1.2 or s > 150:
                    print(f"  period={period} {mode_name} key={best_key}: IoC={ioc_full:.3f} score={s}")
                    print(f"    {text[:120]}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
