#!/usr/bin/env python3
"""
Targeted totient attack on ALL unsolved pages with CORRECT GP mapping.
Also: extended running key tests, and small page brute force.
"""

import os, sys, io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ====================== CORRECT GP MAPPING ======================
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
            'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11

LETTER_TO_IDX = {}
for i, lt in enumerate(GP_LATIN):
    LETTER_TO_IDX[lt] = i
for i, lt in enumerate(GP_LATIN):
    if len(lt) == 1: LETTER_TO_IDX[lt] = i
LETTER_TO_IDX['V'] = 1; LETTER_TO_IDX['K'] = 5; LETTER_TO_IDX['Z'] = 15; LETTER_TO_IDX['Q'] = 5

def runes_to_indices(text):
    return [GP_RUNE_TO_IDX[ch] for ch in text if ch in GP_RUNE_TO_IDX]

def indices_to_latin(indices):
    return ''.join(GP_LATIN[i] for i in indices)

def ioc29(indices):
    if len(indices) < 2: return 0
    c = Counter(indices)
    n = len(indices)
    return 29 * sum(v*(v-1) for v in c.values()) / (n*(n-1))

def load_page(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f: return runes_to_indices(f.read())

def load_page_raw(pn):
    path = os.path.join('LiberPrimus', 'pages', f'page_{pn:02d}', 'runes.txt')
    if not os.path.exists(path): return None
    with open(path, 'r', encoding='utf-8') as f: return f.read()

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

# ====================== GENERATE PRIMES ======================
def gen_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        ok = True
        for p in primes:
            if p*p > c: break
            if c % p == 0: ok = False; break
        if ok: primes.append(c)
        c += 1
    return primes

primes = gen_primes(10000)

# English word list
COMMON_3PLUS = set(['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR',
    'OUT','HAS','HIS','WHO','MAY','NOW','WAY','BOY','DID','GET','HIM','LET','SAY','SHE',
    'TOO','USE','MAN','DAY','HAD','THAT','THIS','WITH','HAVE','FROM','THEY','BEEN','SAID',
    'EACH','WHICH','THEIR','WILL','OTHER','ABOUT','INTO','THAN','THEM','THEN','WHEN','SOME',
    'WHAT','WERE','THERE','THOSE','BEING','WOULD','COULD','SHOULD','THESE','AFTER','BEFORE',
    'WITHIN','THROUGH','BETWEEN','WITHOUT','DURING','UPON','UNTO','YOUR','SELF','TRUTH',
    'KNOW','FIND','WISDOM','SACRED','PRIME','DEATH','LIFE','PATH','LOSS','JUST','LIKE',
    'MAKE','OVER','SUCH','TAKE','VERY','COME','MADE','MANY','ONLY','ALSO','BACK','EVEN',
    'GIVE','MORE','MOST','MUST','NAME','NEED','NEXT'])

def word_score(text):
    score = 0
    for w in COMMON_3PLUS:
        idx = 0
        while True:
            pos = text.find(w, idx)
            if pos == -1: break
            score += len(w) ** 2
            idx = pos + 1
    return score

# ====================== ATTACK 1: DEEP TOTIENT SEARCH ======================
print("=" * 80)
print("ATTACK 1: TOTIENT CIPHER - DEEP SEARCH (starts 0-500)")
print("=" * 80)

totient_hits = []

for pn in range(18, 58):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20: continue
    n = len(cipher)
    
    best_for_page = (0, 0, '', '', 0)
    
    for start in range(500):
        if start + n >= len(primes): break
        
        # SUB: p = (c - (prime-1)) % 29
        dec = [(cipher[i] - (primes[start+i] - 1)) % 29 for i in range(n)]
        ic = ioc29(dec)
        if ic > best_for_page[0]:
            text = indices_to_latin(dec)
            best_for_page = (ic, start, 'sub', text[:60], word_score(text))
        
        # ADD
        dec = [(cipher[i] + (primes[start+i] - 1)) % 29 for i in range(n)]
        ic = ioc29(dec)
        if ic > best_for_page[0]:
            text = indices_to_latin(dec)
            best_for_page = (ic, start, 'add', text[:60], word_score(text))
        
        # F-skip SUB
        dec_fs = []
        k = start
        for c in cipher:
            if c == 0:
                dec_fs.append(0)
            else:
                dec_fs.append((c - (primes[k] - 1)) % 29 if k < len(primes) else c)
                k += 1
        ic_fs = ioc29(dec_fs)
        if ic_fs > best_for_page[0]:
            text = indices_to_latin(dec_fs)
            best_for_page = (ic_fs, start, 'sub_fskip', text[:60], word_score(text))
    
    ic, start, mode, text, wscore = best_for_page
    if ic > 1.1 or wscore > 50:
        totient_hits.append((ic, wscore, pn, start, mode, text))
        print(f"  P{pn:02d}: IoC={ic:.4f} wscore={wscore:3d} start={start:3d} mode={mode:10s}  {text}")

totient_hits.sort(key=lambda x: (-x[0], -x[1]))
print(f"\nTop 10 totient results:")
for ic, ws, pn, start, mode, text in totient_hits[:10]:
    print(f"  P{pn:02d}: IoC={ic:.4f} wscore={ws:3d} start={start:3d} {mode:10s}  {text}")

# ====================== ATTACK 2: TOTIENT WITH PAGE-NUM OFFSETS ======================
print("\n" + "=" * 80)
print("ATTACK 2: TOTIENT WITH PAGE-RELATED OFFSETS")
print("=" * 80)

for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20: continue
    n = len(cipher)
    
    # What if the prime index starts at the page number?
    for start_fn in [pn, pn*2, pn*3, pn-18, (pn-18)*10, pn*pn % 500]:
        start = max(0, start_fn)
        if start + n >= len(primes): continue
        
        dec = [(cipher[i] - (primes[start+i] - 1)) % 29 for i in range(n)]
        ic = ioc29(dec)
        text = indices_to_latin(dec)
        ws = word_score(text)
        
        if ic > 1.2 or ws > 80:
            print(f"  P{pn:02d} start=f({pn})={start}: IoC={ic:.4f} wscore={ws}  {text[:60]}")

# ====================== ATTACK 3: CUMULATIVE PRIME GAPS AS KEY ======================
print("\n" + "=" * 80)
print("ATTACK 3: PRIME GAP KEYSTREAMS")
print("=" * 80)

# Key = prime[i+1] - prime[i] (gaps between consecutive primes)
gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]

gap_hits = []
for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20: continue
    n = len(cipher)
    
    for start in range(0, 200, 1):
        if start + n >= len(gaps): break
        
        for mode in ['sub', 'add']:
            key = [gaps[start+i] % 29 for i in range(n)]
            if mode == 'sub':
                dec = [(cipher[i] - key[i]) % 29 for i in range(n)]
            else:
                dec = [(cipher[i] + key[i]) % 29 for i in range(n)]
            ic = ioc29(dec)
            if ic > 1.25:
                text = indices_to_latin(dec)
                gap_hits.append((ic, pn, start, mode, text[:60]))

if gap_hits:
    gap_hits.sort(reverse=True)
    print(f"Found {len(gap_hits)} prime gap results with IoC > 1.25:")
    for ic, pn, start, mode, text in gap_hits[:20]:
        print(f"  P{pn:02d} start={start:3d}/{mode}: IoC={ic:.4f}  {text}")
else:
    print("  *** No prime gap results ***")

# ====================== ATTACK 4: INTERLEAVED TOTIENT (even/odd positions) ======================
print("\n" + "=" * 80)
print("ATTACK 4: SPLIT CIPHER (even vs odd indices, different keys)")
print("=" * 80)

for pn in [18, 19, 20, 21, 22, 49, 54]:
    cipher = load_page(pn)
    if not cipher: continue
    n = len(cipher)
    
    even = [cipher[i] for i in range(0, n, 2)]
    odd = [cipher[i] for i in range(1, n, 2)]
    
    ic_even = ioc29(even)
    ic_odd = ioc29(odd)
    
    if ic_even > 1.2 or ic_odd > 1.2:
        print(f"  P{pn:02d}: even IoC={ic_even:.4f}, odd IoC={ic_odd:.4f}")
    
    # Every 3rd, 4th...
    for period in range(2, 10):
        for phase in range(period):
            subset = [cipher[i] for i in range(phase, n, period)]
            ic = ioc29(subset)
            if ic > 1.3 and len(subset) > 15:
                print(f"  P{pn:02d}: period={period} phase={phase}: IoC={ic:.4f} ({len(subset)} runes)")

# ====================== ATTACK 5: ALL-PAGES MOD-29 VIGENERE BRUTE FORCE ======================
print("\n" + "=" * 80)
print("ATTACK 5: SHORT KEY BRUTE FORCE (key lengths 1-4)")
print("=" * 80)

# For VERY short keys (length 1-4), brute force all possibilities
for pn in [49, 54, 52, 22, 9]:  # smallest pages
    cipher = load_page(pn)
    if not cipher or len(cipher) < 20: continue
    n = len(cipher)
    
    best = (0, [], '', '')
    
    # Length 1 (Caesar)
    for k0 in range(29):
        dec = [(c - k0) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best[0]:
            best = (ic, [k0], 'sub', indices_to_latin(dec)[:60])
    
    # Length 2
    for k0 in range(29):
        for k1 in range(29):
            dec = [(cipher[i] - [k0,k1][i%2]) % 29 for i in range(n)]
            ic = ioc29(dec)
            if ic > best[0]:
                best = (ic, [k0,k1], 'sub', indices_to_latin(dec)[:60])
    
    # Length 3
    for k0 in range(29):
        for k1 in range(29):
            for k2 in range(29):
                dec = [(cipher[i] - [k0,k1,k2][i%3]) % 29 for i in range(n)]
                ic = ioc29(dec)
                if ic > best[0]:
                    best = (ic, [k0,k1,k2], 'sub', indices_to_latin(dec)[:60])
    
    ic, key, mode, text = best
    ws = word_score(text)
    print(f"  P{pn:02d}: best IoC={ic:.4f} key={key} wscore={ws}  {text}")

# ====================== ATTACK 6: P19 KNOWN PLAINTEXT EXTENSION ======================
print("\n" + "=" * 80)
print("ATTACK 6: P19 KNOWN PLAINTEXT ATTACK")
print("=" * 80)

p19 = load_page(19)
if p19:
    # Known: first 43 GP positions decode to:
    # "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
    # Using ADD mode
    known_plain_text = "REARRANGINGTHEPRIMESNUMBERSWILLSHOWAPATHTOTHEDEOR"
    
    # Convert to GP indices
    kp_indices = []
    i = 0
    t = known_plain_text.upper()
    while i < len(t):
        if i + 2 <= len(t):
            d = t[i:i+2]
            if d in LETTER_TO_IDX:
                kp_indices.append(LETTER_TO_IDX[d])
                i += 2
                continue
        ch = t[i]
        if ch in LETTER_TO_IDX:
            kp_indices.append(LETTER_TO_IDX[ch])
        i += 1
    
    print(f"P19: {len(p19)} runes")
    print(f"Known plaintext: {len(kp_indices)} GP indices")
    print(f"  Text: {indices_to_latin(kp_indices)}")
    
    # Recover key for first 43 positions: key[i] = (cipher[i] + plain[i]) % 29 (ADD mode)
    kp_len = min(len(kp_indices), len(p19))
    key_recovered = [(p19[i] + kp_indices[i]) % 29 for i in range(kp_len)]
    print(f"\n  Recovered key (ADD mode, first {kp_len} positions):")
    print(f"  {key_recovered}")
    print(f"  As letters: {indices_to_latin(key_recovered)}")
    
    # Also try SUB mode: key[i] = (cipher[i] - plain[i]) % 29
    key_sub = [(p19[i] - kp_indices[i]) % 29 for i in range(kp_len)]
    print(f"\n  Recovered key (SUB mode, first {kp_len} positions):")
    print(f"  {key_sub}")
    print(f"  As letters: {indices_to_latin(key_sub)}")
    
    # Check if the key has any pattern
    print(f"\n  Key periodicity check:")
    for period in range(1, 20):
        consistent = True
        for i in range(period, kp_len):
            if key_recovered[i] != key_recovered[i % period]:
                consistent = False
                break
        if consistent:
            print(f"    Period {period} MATCHES! Key = {key_recovered[:period]}")
            print(f"    Key text: {indices_to_latin(key_recovered[:period])}")
            break
    else:
        print(f"    No exact periodicity found in first {kp_len} positions")
    
    # Check if key matches any known sequence
    print(f"\n  Key comparison with prime sequence:")
    prime_key = [(primes[i] - 1) % 29 for i in range(kp_len)]
    match_count = sum(1 for i in range(kp_len) if key_recovered[i] == prime_key[i])
    print(f"    ADD key matches φ(prime): {match_count}/{kp_len}")
    
    prime_key_direct = [primes[i] % 29 for i in range(kp_len)]
    match_count2 = sum(1 for i in range(kp_len) if key_recovered[i] == prime_key_direct[i])
    print(f"    ADD key matches prime mod 29: {match_count2}/{kp_len}")
    
    # Try extending: use the recovered key pattern to decode rest of P19
    print(f"\n  Extended decryption of P19 using recovered key:")
    # If key is a sequence, try to find which sequence
    for offset in range(0, 100):
        key_test = [(primes[offset+i] - 1) % 29 for i in range(kp_len)]
        match = sum(1 for i in range(kp_len) if key_recovered[i] == key_test[i])
        if match > kp_len * 0.8:
            print(f"    offset={offset}: {match}/{kp_len} matches with φ(prime) stream")
            # Try full decryption
            full_dec = [(p19[i] + (primes[offset+i]-1) % 29) % 29 for i in range(len(p19))]
            print(f"    Full text: {indices_to_latin(full_dec)[:120]}")
    
    for offset in range(0, 100):
        key_test = [primes[offset+i] % 29 for i in range(kp_len)]
        match = sum(1 for i in range(kp_len) if key_recovered[i] == key_test[i])
        if match > kp_len * 0.8:
            print(f"    offset={offset}: {match}/{kp_len} matches with prime mod 29")

print("\n=== TARGETED TOTIENT ATTACKS COMPLETE ===")
