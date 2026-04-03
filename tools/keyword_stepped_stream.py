#!/usr/bin/env python3
"""
Keyword-Stepped Prime Stream Cipher Test
==========================================
Hypothesis: "Rearranging the prime numbers" means the keyword determines
HOW to step through the prime table, creating a non-repeating stream.

Variants tested:
1. Cumulative keyword step: index[i] = sum(kw[j % kl] for j in 0..i) + offset
2. Multiplicative step: index[i] = kw[i % kl] * i + offset  
3. Prime-indexed keyword: index[i] = prime[kw[i % kl]] + i
4. Keyword as prime selector: key[i] = prime[kw[i%kl] + i] % 29
5. Fibonacci-recurrence with keyword seed
6. Keyword XOR position: key[i] = totient(prime[kw[i%kl] XOR i]) % 29
"""

import sys
from pathlib import Path
from collections import Counter
from sympy import nextprime

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

ALL_KEYWORDS = {
    'DIVINITY':     [23, 10, 1, 10, 9, 10, 16, 26],
    'CABAL':        [5, 24, 17, 24, 20],
    'SHADOWS':      [15, 8, 24, 23, 3, 7, 15],
    'OBSCURA':      [3, 17, 15, 5, 1, 4, 24],
    'VOID':         [1, 3, 10, 23],
    'FORM':         [0, 3, 4, 19],
    'MOBIUS':       [19, 3, 17, 10, 1, 15],
    'ANALOG':       [24, 9, 24, 20, 3, 6],
    'MOURNFUL':     [19, 3, 1, 4, 9, 0, 1, 20],
    'AETHEREAL':    [24, 18, 2, 8, 18, 4, 18, 24, 20],
    'BUFFERS':      [17, 1, 0, 0, 18, 4, 15],
    'CARNAL':       [5, 24, 4, 9, 24, 20],
    'TOTIENT':      [16, 3, 16, 10, 18, 9, 16],
    'ENCRYPT':      [18, 9, 5, 4, 26, 13, 16],
    'ENCRYPTION':   [18, 9, 5, 4, 26, 13, 16, 10, 3, 9],
    'DEOR':         [23, 12, 4],
    'CICADA':       [5, 10, 5, 24, 23, 24],
    'FIRFUMFERENFE': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
    'PRIMES':       [13, 4, 10, 19, 18, 15],
    'SACRED':       [15, 24, 5, 4, 18, 23],
}


def load_page(page_num):
    rune_path = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_path.exists():
        return None, None, None
    content = rune_path.read_text(encoding='utf-8').strip()
    indices = []
    words = []
    wstart = 0
    wlen = 0
    for ch in content:
        if ch in RUNE_TO_IDX:
            if wlen == 0: wstart = len(indices)
            indices.append(RUNE_TO_IDX[ch])
            wlen += 1
        elif ch in '-\n /%.&$':
            if wlen > 0:
                words.append((wstart, wlen))
                wlen = 0
    if wlen > 0:
        words.append((wstart, wlen))
    singletons = [(s, indices[s]) for s, l in words if l == 1]
    return indices, singletons, content


def compute_ioc(plain):
    n = len(plain)
    if n < 2: return 0
    freq = Counter(plain)
    total = sum(f*(f-1) for f in freq.values())
    return (total / (n*(n-1))) / (1.0/29)


def to_runeglish(plain):
    return ''.join(IDX_TO_LETTER[i] for i in plain)


def check_singletons(plain, singletons):
    for pos, _ in singletons:
        if pos < len(plain) and plain[pos] not in (10, 24):
            return False
    return True


# Generate primes
print("Generating primes...", flush=True)
PRIMES = []
p = 2
while len(PRIMES) < 500000:
    PRIMES.append(p)
    p = nextprime(p)
print(f"  Generated {len(PRIMES)} primes (max={PRIMES[-1]})", flush=True)

# Pre-compute totient values for primes
TOTIENT_MOD29 = [(p - 1) % 29 for p in PRIMES]


def generate_keyword_stepped_stream(keyword, length, offset, variant):
    """Generate non-repeating key stream by stepping through primes via keyword."""
    kl = len(keyword)
    stream = []
    
    if variant == 'cumulative':
        # index[i] = offset + sum(kw[j%kl] for j in 0..i-1)
        idx = offset
        for i in range(length):
            if idx >= len(PRIMES):
                return None
            stream.append(TOTIENT_MOD29[idx])
            idx += keyword[i % kl]
            if idx < 0: idx = 0
    
    elif variant == 'cumulative_prime':
        # Same but use prime mod 29 instead of totient
        idx = offset
        for i in range(length):
            if idx >= len(PRIMES):
                return None
            stream.append(PRIMES[idx] % 29)
            idx += keyword[i % kl]
            if idx < 0: idx = 0
    
    elif variant == 'multiplicative':
        # index[i] = offset + kw[i%kl] * i
        for i in range(length):
            idx = offset + keyword[i % kl] * i
            if idx >= len(PRIMES) or idx < 0:
                return None
            stream.append(TOTIENT_MOD29[idx])
    
    elif variant == 'prime_selector':
        # key[i] = (prime[kw[i%kl] + i + offset] - 1) % 29
        for i in range(length):
            idx = keyword[i % kl] + i + offset
            if idx >= len(PRIMES) or idx < 0:
                return None
            stream.append(TOTIENT_MOD29[idx])
    
    elif variant == 'prime_selector_mod':
        # key[i] = prime[kw[i%kl] * (i+1) + offset] % 29
        for i in range(length):
            idx = keyword[i % kl] * (i + 1) + offset
            if idx >= len(PRIMES) or idx < 0:
                return None
            stream.append(PRIMES[idx] % 29)
    
    elif variant == 'keyword_add_sequential':
        # key[i] = (kw[i%kl] + prime[i + offset] - 1) % 29
        # This is keyword Vigenère + totient stream combined (different from earlier test
        # because we use (kw + totient) not kw OP1 cipher OP2 totient)
        for i in range(length):
            idx = i + offset
            if idx >= len(PRIMES):
                return None
            stream.append((keyword[i % kl] + TOTIENT_MOD29[idx]) % 29)
    
    elif variant == 'fib_recurrence':
        # Fibonacci-like recurrence seeded by keyword:
        # state[i] = (state[i-1] + state[i-kl]) % 29
        # First kl values are the keyword
        state = list(keyword)
        while len(state) < length + offset:
            state.append((state[-1] + state[-kl]) % 29)
        stream = state[offset:offset+length]
    
    elif variant == 'xor_position':
        # key[i] = (prime[(kw[i%kl] XOR i) % MAX] - 1) % 29
        MAX_IDX = len(PRIMES)
        for i in range(length):
            idx = (keyword[i % kl] ^ (i + offset)) % MAX_IDX
            stream.append(TOTIENT_MOD29[idx])
    
    return stream


def main():
    print("=" * 80)
    print("KEYWORD-STEPPED PRIME STREAM CIPHER TEST")
    print("=" * 80)
    sys.stdout.flush()
    
    # Load test pages (high singleton count)
    test_pages = [28, 53, 24, 39, 29, 30, 34, 51, 21, 33, 45]
    pages = {}
    for pg in test_pages:
        data = load_page(pg)
        if data[0] is not None:
            pages[pg] = data
    
    print(f"Testing {len(pages)} pages × {len(ALL_KEYWORDS)} keywords × 8 variants × 3 modes × offsets")
    sys.stdout.flush()
    
    variants = ['cumulative', 'cumulative_prime', 'multiplicative', 'prime_selector',
                'prime_selector_mod', 'keyword_add_sequential', 'fib_recurrence', 'xor_position']
    
    modes = ['sub', 'add', 'beaufort']
    
    all_hits = []
    
    for kw_name, kw_indices in ALL_KEYWORDS.items():
        for variant in variants:
            for pg in sorted(pages.keys()):
                cipher, singletons, content = pages[pg]
                page_len = len(cipher)
                n_sing = len(singletons)
                
                # Test offsets 0 to 1000
                for offset in range(0, 1001):
                    stream = generate_keyword_stepped_stream(kw_indices, page_len, offset, variant)
                    if stream is None or len(stream) < page_len:
                        continue
                    
                    for mode in modes:
                        if mode == 'sub':
                            plain = [(cipher[i] - stream[i]) % 29 for i in range(page_len)]
                        elif mode == 'add':
                            plain = [(cipher[i] + stream[i]) % 29 for i in range(page_len)]
                        elif mode == 'beaufort':
                            plain = [(stream[i] - cipher[i]) % 29 for i in range(page_len)]
                        
                        # Hard singleton check
                        if not check_singletons(plain, singletons):
                            continue
                        
                        ioc = compute_ioc(plain)
                        if ioc > 1.3:
                            text = to_runeglish(plain)
                            all_hits.append((ioc, pg, kw_name, variant, mode, offset, text[:100]))
                            print(f"  *** HIT: P{pg:02d} IoC={ioc:.4f} [{kw_name}] {variant} {mode} off={offset}")
                            print(f"      {text[:100]}")
                            sys.stdout.flush()
        
        print(f"  Keyword '{kw_name}' complete.", flush=True)
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if all_hits:
        all_hits.sort(key=lambda x: -x[0])
        print(f"\n{len(all_hits)} hits with IoC > 1.3:")
        for ioc, pg, kw, var, mode, off, txt in all_hits[:20]:
            print(f"  P{pg:02d} IoC={ioc:.4f} [{kw}] {var} {mode} off={off} | {txt[:70]}")
    else:
        print("\nNO keyword-stepped stream passed all singleton constraints with IoC > 1.3")
        print("Keyword-stepped prime hypothesis: RULED OUT")
    
    print("\nDone.")


if __name__ == '__main__':
    main()
