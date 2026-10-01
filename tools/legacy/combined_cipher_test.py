#!/usr/bin/env python3
"""
Test COMBINED cipher: keyword Vigenere + prime totient stream.
Hypothesis: plaintext[i] = (cipher[i] OP1 keyword[i%kl] OP2 totient(prime[s+i])) % 29
where OP1 and OP2 can be +/- independently.

This would explain why keyword alone gives IoC ~1.0 (only removes one layer).
"""

import sys, os, math
from collections import Counter
from pathlib import Path
from itertools import product

N = 29

RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP = {r: i for i, r in enumerate(RUNES)}
SEPS = set(".-\u2022 \n")

DIGRAPHS = {"TH":2, "EO":12, "NG":21, "OE":22, "AE":25, "IA":27, "EA":28}
SINGLES_MAP = {"F":0, "U":1, "V":1, "O":3, "R":4, "C":5, "K":5, "G":6, "W":7,
               "H":8, "N":9, "I":10, "J":11, "P":13, "X":14, "S":15, "T":16,
               "B":17, "E":18, "M":19, "L":20, "D":23, "A":24, "Y":26}

# All P63 keywords
KEYWORDS = {
    "CABAL": [5, 24, 17, 24, 20],
    "DIVINITY": [23, 10, 1, 10, 9, 10, 16, 26],
    "ENCRYPTION": [18, 9, 5, 4, 26, 13, 16, 10, 3, 9],
    "OBSCURA": [3, 17, 15, 5, 1, 4, 24],
    "ENCRYPT": [18, 9, 5, 4, 26, 13, 16],
    "SHADOWS": [15, 8, 24, 23, 3, 7, 15],
    "DEOR": [23, 12, 4],
    "TOTIENT": [16, 3, 16, 10, 18, 9, 16],
    "MOURNFUL": [19, 3, 1, 4, 9, 0, 1, 20],
    "VOID": [1, 3, 10, 23],
    "AETHEREAL": [24, 18, 2, 8, 18, 4, 18, 24, 20],
    "BUFFERS": [17, 1, 0, 0, 18, 4, 15],
    "CARNAL": [5, 24, 4, 9, 24, 20],
    "ANALOG": [24, 9, 24, 20, 3, 6],
    "MOBIUS": [19, 3, 17, 10, 1, 15],
    "FORM": [0, 3, 4, 19],
}

def sieve_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

PRIMES = sieve_primes(100000)

def load_page(pn):
    path = Path(f"pages/page_{pn:02d}/runes.txt")
    if not path.exists(): return None, None
    text = path.read_text(encoding='utf-8')
    flat = []; words = []; current = []
    for ch in text:
        if ch in GP:
            current.append(GP[ch])
            flat.append(GP[ch])
        elif ch in SEPS:
            if current: words.append(current); current = []
    if current: words.append(current)
    return flat, words

def ioc(vals):
    n = len(vals)
    if n < 2: return 0.0
    freq = Counter(vals)
    return sum(f*(f-1) for f in freq.values()) * N / (n*(n-1))

def check_singletons(vals, words):
    pos = 0; total = 0; passing = 0
    for w in words:
        if len(w) == 1:
            total += 1
            if vals[pos] in (10, 24): passing += 1
        pos += len(w)
    return total, passing

def vals_to_words(vals, words):
    pos = 0; result = []
    for w in words:
        rg = ''.join(RUNEGLISH[vals[pos+i]] for i in range(len(w)))
        result.append(rg)
        pos += len(w)
    return result

def combined_decrypt(flat, keyword, kw_op, stream, st_op):
    """
    Decrypt: plaintext[i] = (cipher[i] KW_OP kw[i%kl] ST_OP stream[i]) % 29
    kw_op/st_op: 'sub' means subtract that component, 'add' means add
    """
    kl = len(keyword)
    result = []
    for i in range(len(flat)):
        v = flat[i]
        k = keyword[i % kl]
        s = stream[i] if i < len(stream) else 0
        
        if kw_op == "sub": v = (v - k) % N
        else: v = (v + k) % N
        
        if st_op == "sub": v = (v - s) % N
        else: v = (v + s) % N
        
        result.append(v)
    return result

def main():
    os.chdir(Path(__file__).parent.parent)
    
    print("=" * 80)
    print("COMBINED CIPHER TEST: Keyword Vigenere + Prime Totient Stream")
    print("=" * 80)
    
    ops = ["sub", "add"]
    
    # Pre-generate stream types
    max_len = 2000
    streams = {}
    
    for start_idx in range(0, 50):
        # Totient stream: (prime[i] - 1) % 29
        tot = [(PRIMES[start_idx + i] - 1) % N for i in range(max_len)]
        streams[f"totient_s{start_idx}"] = tot
        
        # Prime mod 29
        pmod = [PRIMES[start_idx + i] % N for i in range(max_len)]
        streams[f"primemod_s{start_idx}"] = pmod
    
    # Also: cumulative totient
    cum = [0] * max_len
    running = 0
    for i in range(max_len):
        running = (running + PRIMES[i] - 1) % N
        cum[i] = running
    streams["cumul_totient"] = cum
    
    # Simple index: stream[i] = i % 29
    streams["linear"] = [i % N for i in range(max_len)]
    
    # Fibonacci: f(0)=0, f(1)=1, f(n)=f(n-1)+f(n-2) mod 29
    fib = [0, 1]
    for i in range(2, max_len):
        fib.append((fib[-1] + fib[-2]) % N)
    streams["fibonacci"] = fib
    
    best_per_page = {}
    
    for pn in range(21, 55):
        flat, words = load_page(pn)
        if flat is None: continue
        
        nr = len(flat)
        n_singles = sum(1 for w in words if len(w) == 1)
        
        page_best = []
        
        for kw_name, kw_vals in KEYWORDS.items():
            for stream_name, stream_vals in streams.items():
                if len(stream_vals) < nr: continue
                
                for kw_op in ops:
                    for st_op in ops:
                        plain = combined_decrypt(flat, kw_vals, kw_op, stream_vals[:nr], st_op)
                        ic = ioc(plain)
                        
                        if ic > 1.4:
                            t, p = check_singletons(plain, words)
                            page_best.append({
                                'kw': kw_name, 'stream': stream_name,
                                'kw_op': kw_op, 'st_op': st_op,
                                'ioc': ic, 'singles': f"{p}/{t}",
                                'plain': plain,
                            })
        
        page_best.sort(key=lambda x: -x['ioc'])
        
        if page_best:
            print(f"\nP{pn} ({nr} runes, {n_singles} singles) — {len(page_best)} hits with IoC > 1.4:")
            for r in page_best[:5]:
                rg = vals_to_words(r['plain'], words)
                text = ' '.join(rg[:12])
                print(f"  IoC={r['ioc']:.4f} sing={r['singles']} [{r['kw']:15s}] kw_{r['kw_op']} + [{r['stream']:20s}] st_{r['st_op']}")
                print(f"    -> {text}...")
            
            best_per_page[pn] = page_best[0]
        else:
            print(f"\nP{pn} ({nr} runes) — NO hits with IoC > 1.4")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY — Best per page:")
    print("=" * 80)
    for pn in sorted(best_per_page):
        r = best_per_page[pn]
        rg = vals_to_words(r['plain'], load_page(pn)[1])
        text = ' '.join(rg[:10])
        print(f"  P{pn:02d}: IoC={r['ioc']:.4f} [{r['kw']}] kw_{r['kw_op']} + [{r['stream']}] st_{r['st_op']} | {text}...")
    
    print("\nDone.")

if __name__ == "__main__":
    main()
