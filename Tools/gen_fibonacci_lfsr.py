#!/usr/bin/env python3
"""
Generalized Fibonacci LFSR Cipher Tester
=========================================
P32's grid explicitly encodes Fibonacci via 3301-prime mapping.
Fibonacci LFSR: k[n] = (k[n-1] + k[n-2]) mod 29 with arbitrary seeds.
Also tests higher-order recurrences: k[n] = (k[n-1] + k[n-p]) mod 29.

Additionally tests AUTOKEY with various cribs positioned at different offsets.
"""
import sys, os
from pathlib import Path
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,
    '\u16B7':6,'\u16B9':7,'\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,
    '\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,
    '\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,
    '\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
           'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,
          'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'R':4,'S':15,
          'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26}
GP_FREQ = {0:2.2,1:2.8,2:3.7,3:7.5,4:6.0,5:2.8,6:2.0,7:2.4,8:6.1,
           9:6.7,10:7.0,11:0.15,12:0.5,13:1.9,14:0.15,15:6.3,16:9.1,
           17:1.5,18:12.7,19:2.4,20:4.0,21:0.5,22:0.5,23:4.3,24:8.2,
           25:0.5,26:2.0,27:0.5,28:0.5}

def load_runes(page_num):
    base = Path(__file__).parent.parent / "LiberPrimus" / "pages" / f"page_{page_num:02d}"
    rune_file = base / "runes.txt"
    if not rune_file.exists():
        return []
    text = rune_file.read_text(encoding='utf-8')
    return [GP[ch] for ch in text if ch in GP]

def ioc(indices):
    if len(indices) < 2:
        return 0
    n = len(indices)
    counts = Counter(indices)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1)) * 29

def score_english(indices):
    if not indices:
        return 0
    total = len(indices)
    counts = Counter(indices)
    chi2 = 0
    for i in range(29):
        observed = counts.get(i, 0)
        expected = GP_FREQ.get(i, 1.0) * total / 100.0
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    return max(0, 200 - chi2)

def indices_to_text(indices):
    return ''.join(IDX2LAT[i] for i in indices)

def text_to_indices(text):
    """Convert English text to GP indices."""
    result = []
    i = 0
    while i < len(text):
        # Check digraphs first
        if i + 1 < len(text):
            di = text[i:i+2].upper()
            if di == 'TH':
                result.append(2); i += 2; continue
            elif di == 'NG':
                result.append(21); i += 2; continue
            elif di == 'OE':
                result.append(22); i += 2; continue
            elif di == 'AE':
                result.append(25); i += 2; continue
            elif di == 'IA':
                result.append(27); i += 2; continue
            elif di == 'EA':
                result.append(28); i += 2; continue
            elif di == 'EO':
                result.append(12); i += 2; continue
        ch = text[i].upper()
        if ch in ENG2GP:
            result.append(ENG2GP[ch])
        i += 1
    return result

# ── Generalized Fibonacci LFSR ──────────────────────────────────

def gen_fib_lfsr(a, b, n, mod=29):
    """Generate n values of generalized Fibonacci: k[i] = (k[i-1] + k[i-2]) mod 29."""
    seq = [a % mod, b % mod]
    for _ in range(n - 2):
        seq.append((seq[-1] + seq[-2]) % mod)
    return seq

def gen_tribonacci(a, b, c, n, mod=29):
    """k[i] = (k[i-1] + k[i-2] + k[i-3]) mod 29."""
    seq = [a % mod, b % mod, c % mod]
    for _ in range(n - 3):
        seq.append((seq[-1] + seq[-2] + seq[-3]) % mod)
    return seq

def gen_lfsr_lag(seeds, lag, n, mod=29):
    """k[i] = (k[i-1] + k[i-lag]) mod 29 for general lag."""
    seq = list(s % mod for s in seeds)
    while len(seq) < n:
        if len(seq) >= lag:
            seq.append((seq[-1] + seq[-lag]) % mod)
        else:
            seq.append(0)
    return seq[:n]

def decrypt(cipher, key_stream, mode='SUB'):
    result = []
    for i, c in enumerate(cipher):
        k = key_stream[i]
        if mode == 'SUB':
            result.append((c - k) % 29)
        elif mode == 'ADD':
            result.append((c + k) % 29)
        elif mode == 'BEAU':
            result.append((k - c) % 29)
    return result

def decrypt_fskip(cipher, key_stream, mode='SUB'):
    result = []
    ki = 0
    for c in cipher:
        if c == 0:
            result.append(0)
        else:
            k = key_stream[ki] if ki < len(key_stream) else 0
            if mode == 'SUB':
                result.append((c - k) % 29)
            elif mode == 'ADD':
                result.append((c + k) % 29)
            elif mode == 'BEAU':
                result.append((k - c) % 29)
            ki += 1
    return result

# ── Autokey Cipher Testing ──────────────────────────────────────

def autokey_decrypt_plaintext(cipher, seed_key, mode='SUB'):
    """Autokey where key extends with plaintext values."""
    plain = []
    key = list(seed_key)
    for i, c in enumerate(cipher):
        if i < len(key):
            k = key[i]
        else:
            k = plain[i - len(seed_key)]
        if mode == 'SUB':
            p = (c - k) % 29
        elif mode == 'ADD':
            p = (c + k) % 29
        elif mode == 'BEAU':
            p = (k - c) % 29
        plain.append(p)
    return plain

def autokey_decrypt_ciphertext(cipher, seed_key, mode='SUB'):
    """Autokey where key extends with ciphertext values."""
    plain = []
    key = list(seed_key)
    for i, c in enumerate(cipher):
        if i < len(key):
            k = key[i]
        else:
            k = cipher[i - len(seed_key)]
        if mode == 'SUB':
            p = (c - k) % 29
        elif mode == 'ADD':
            p = (c + k) % 29
        elif mode == 'BEAU':
            p = (k - c) % 29
        plain.append(p)
    return plain

# ── Main Tests ──────────────────────────────────────────────────

def test_gen_fibonacci(cipher, page_num):
    """Test all 841 seed pairs for generalized Fibonacci LFSR."""
    n = len(cipher)
    best = []
    
    for a in range(29):
        for b in range(29):
            key = gen_fib_lfsr(a, b, n)
            for mode in ['SUB', 'ADD', 'BEAU']:
                plain = decrypt(cipher, key, mode)
                ic = ioc(plain)
                sc = score_english(plain)
                if ic > 1.3 or sc > 100:
                    text = indices_to_text(plain[:60])
                    best.append((sc, ic, f"GenFib({a},{b}) {mode}", text))
                
                # F-skip
                plain_fs = decrypt_fskip(cipher, key, mode)
                ic_fs = ioc(plain_fs)
                sc_fs = score_english(plain_fs)
                if ic_fs > 1.3 or sc_fs > 100:
                    text_fs = indices_to_text(plain_fs[:60])
                    best.append((sc_fs, ic_fs, f"GenFib({a},{b}) {mode} F-skip", text_fs))
    
    return best

def test_gen_fibonacci_sampled(cipher, page_num):
    """Quick screen: test all 841 seed pairs, SUB mode only, check IoC > 1.5."""
    n = len(cipher)
    hits = []
    
    for a in range(29):
        for b in range(29):
            key = gen_fib_lfsr(a, b, n)
            # Test all 3 modes
            for mode in ['SUB', 'ADD', 'BEAU']:
                plain = decrypt(cipher, key, mode)
                ic = ioc(plain)
                if ic > 1.5:
                    sc = score_english(plain)
                    text = indices_to_text(plain[:80])
                    hits.append((sc, ic, f"GenFib({a},{b}) {mode}", text))
    
    return hits

def test_autokey_with_cribs(cipher, page_num):
    """Test autokey with known Cicada cribs at various positions."""
    cribs = [
        "THE", "AN", "A", "SOME", "WISDOM", "TRUTH", "DIVINITY", 
        "SACRED", "PRIMES", "LOSS", "ALL", "WITHIN", "KNOWLEDGE",
        "INSTRUCTION", "PARABLE", "QUESTION", "DISCOVER", 
        "BEING", "CONSCIOUSNESS", "PROGRAM", "CODE", "ONE",
        "WELCOME", "PILGRIM", "COMMAND", "PASSAGE", "UNTO",
        "EMERGE", "SHED", "CIRCUMFERENCE", "INSTAR",
        "CHAPTER", "INTUS", "LIBER",
        "WARNING", "CONSUMPTION", "FOLLY"
    ]
    
    best = []
    
    for crib_text in cribs:
        crib = text_to_indices(crib_text)
        if not crib:
            continue
        
        # Try placing crib at position 0 (most common for Cicada page starts)
        for start_pos in [0]:
            for mode in ['SUB', 'ADD', 'BEAU']:
                # If crib is at start, the initial key is: k[i] = (cipher[i] - crib[i]) mod 29
                seed = []
                for i in range(len(crib)):
                    if start_pos + i < len(cipher):
                        c = cipher[start_pos + i]
                        p = crib[i]
                        if mode == 'SUB':
                            seed.append((c - p) % 29)
                        elif mode == 'ADD':
                            seed.append((p - c) % 29)  # reverse
                        elif mode == 'BEAU':
                            seed.append((c + p) % 29)
                
                if not seed:
                    continue
                
                # Try plaintext autokey from this seed
                plain_pk = autokey_decrypt_plaintext(cipher, seed, mode)
                ic_pk = ioc(plain_pk)
                sc_pk = score_english(plain_pk)
                if ic_pk > 1.3 or sc_pk > 100:
                    text_pk = indices_to_text(plain_pk[:80])
                    best.append((sc_pk, ic_pk, f"Autokey-PT crib='{crib_text}' {mode}", text_pk))
                
                # Try ciphertext autokey
                plain_ck = autokey_decrypt_ciphertext(cipher, seed, mode)
                ic_ck = ioc(plain_ck)
                sc_ck = score_english(plain_ck)
                if ic_ck > 1.3 or sc_ck > 100:
                    text_ck = indices_to_text(plain_ck[:80])
                    best.append((sc_ck, ic_ck, f"Autokey-CT crib='{crib_text}' {mode}", text_ck))
    
    return best

def test_higher_order_lfsr(cipher, page_num):
    """Test tribonacci and higher-order LFSRs with sampled seeds."""
    n = len(cipher)
    best = []
    
    # Tribonacci: sample some seed triples
    for a in range(0, 29, 3):
        for b in range(0, 29, 3):
            for c in range(0, 29, 3):
                key = gen_tribonacci(a, b, c, n)
                for mode in ['SUB', 'ADD']:
                    plain = decrypt(cipher, key, mode)
                    ic = ioc(plain)
                    if ic > 1.5:
                        sc = score_english(plain)
                        text = indices_to_text(plain[:60])
                        best.append((sc, ic, f"Tribonacci({a},{b},{c}) {mode}", text))
    
    # Lag-p Fibonacci: k[n] = (k[n-1] + k[n-p]) mod 29 for p=3..8
    for lag in range(3, 9):
        for a in range(0, 29, 4):
            for b in range(0, 29, 4):
                seeds = [a, b] + [0] * (lag - 2)
                seeds[lag-1] = 1  # Ensure non-trivial
                key = gen_lfsr_lag(seeds, lag, n)
                for mode in ['SUB', 'ADD']:
                    plain = decrypt(cipher, key, mode)
                    ic = ioc(plain)
                    if ic > 1.5:
                        sc = score_english(plain)
                        text = indices_to_text(plain[:60])
                        best.append((sc, ic, f"LFSR-lag{lag}({a},{b}) {mode}", text))
    
    return best

def test_multiplicative_fib(cipher, page_num):
    """Test k[n] = (a*k[n-1] + b*k[n-2]) mod 29 for various a,b."""
    n = len(cipher)
    best = []
    
    for mult_a in range(1, 29):
        for mult_b in range(1, 29):
            # Fixed seeds (1, 1) to keep space manageable
            seq = [1, 1]
            for _ in range(n - 2):
                seq.append((mult_a * seq[-1] + mult_b * seq[-2]) % 29)
            
            for mode in ['SUB', 'ADD']:
                plain = decrypt(cipher, seq, mode)
                ic = ioc(plain)
                if ic > 1.5:
                    sc = score_english(plain)
                    text = indices_to_text(plain[:60])
                    best.append((sc, ic, f"MultFib(a={mult_a},b={mult_b}) {mode}", text))
    
    return best

# ── Main ──────────────────────────────────────────────────────────

def main():
    # Focus on large pages for statistical reliability
    test_pages = [32, 44, 50, 20, 40]
    
    for page in test_pages:
        cipher = load_runes(page)
        if not cipher or len(cipher) < 50:
            continue
        
        print(f"\n{'='*70}")
        print(f"PAGE {page:02d} ({len(cipher)} runes)")
        print(f"{'='*70}")
        
        all_results = []
        
        # 1. Generalized Fibonacci (all 841 seeds, IoC > 1.5 threshold)
        print(f"  [1/5] Generalized Fibonacci LFSR (841 seeds × 3 modes)...")
        results = test_gen_fibonacci_sampled(cipher, page)
        all_results.extend(results)
        print(f"    → {len(results)} hits")
        
        # 2. Autokey with cribs
        print(f"  [2/5] Autokey with cribs...")
        results = test_autokey_with_cribs(cipher, page)
        all_results.extend(results)
        print(f"    → {len(results)} hits")
        
        # 3. Higher-order LFSR (tribonacci, lag-p)
        print(f"  [3/5] Higher-order LFSR...")
        results = test_higher_order_lfsr(cipher, page)
        all_results.extend(results)
        print(f"    → {len(results)} hits")
        
        # 4. Multiplicative Fibonacci
        print(f"  [4/5] Multiplicative Fibonacci (28×28 multiplier pairs)...")
        results = test_multiplicative_fib(cipher, page)
        all_results.extend(results)
        print(f"    → {len(results)} hits")
        
        # 5. Full generalized Fibonacci with F-skip (if page is smaller)
        if len(cipher) < 500:
            print(f"  [5/5] Full GenFib with F-skip...")
            results = test_gen_fibonacci(cipher, page)
            all_results.extend(results)
            print(f"    → {len(results)} hits")
        else:
            print(f"  [5/5] Skipped full F-skip scan (page too large)")
        
        if all_results:
            all_results.sort(key=lambda x: (-x[1], -x[0]))  # Sort by IoC descending
            print(f"\n  *** TOP RESULTS FOR PAGE {page:02d} ***")
            for sc, ic, desc, text in all_results[:15]:
                print(f"    IoC={ic:.3f} Score={sc:.1f} | {desc}")
                print(f"      {text}")
        else:
            print(f"\n  No results above thresholds.")
    
    print("\nDone.")

if __name__ == '__main__':
    main()
