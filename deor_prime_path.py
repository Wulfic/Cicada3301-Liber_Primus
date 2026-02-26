#!/usr/bin/env python3
"""
Deor + Rearranged Primes Attack
================================
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
P55 method: plaintext[i] = (value[i] - (prime[i] - 1)) mod 29

This script explores: prime-indexed positions in the Deor poem as keystream,
totient-transformed Deor keys, Fibonacci-spiral ordering, and running key.
"""
import os, sys, io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# --- CORRECT GP MAPPING ---
GP_RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C2\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11
MOD = 29
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_runes(page_num):
    f = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num}\\runes.txt"
    if not os.path.exists(f): return None
    with open(f, 'r', encoding='utf-8') as fh:
        return [GP_RUNE_TO_IDX[c] for c in fh.read() if c in GP_RUNE_TO_IDX]

def ioc(v):
    if len(v)<2: return 0
    c=Counter(v); n=len(v)
    return sum(x*(x-1) for x in c.values())/(n*(n-1))*MOD

def to_text(idx):
    return ''.join(GP_LETTERS[i] for i in idx)

COMMON_WORDS = {"THE","AND","FOR","ARE","NOT","YOU","ALL","HER","WAS","ONE",
    "OUR","OUT","HAS","HIS","HOW","MAN","NEW","NOW","OLD","SEE","WAY","WHO",
    "DID","GET","HIM","LET","SAY","SHE","TOO","BUT","CAN","HAD","ITS","MAY",
    "WILL","EACH","MAKE","LIKE","SOME","THEM","THAN","BEEN","HAVE","FROM",
    "INTO","WITH","THAT","THIS","WHAT","WHEN","THEY","COME","MADE","FIND",
    "MORE","ONLY","JUST","OVER","SUCH","ALSO","VERY","AFTER","BEING","THEIR",
    "THESE","THOSE","UNDER","ABOUT","COULD","EVERY","FIRST","SHALL","THERE",
    "THINK","WHERE","WHICH","WHILE","WORLD","WOULD","MIGHT","NEVER","STILL",
    "TRUTH","KNOW","MUST","SELF","SOUL","MIND","LIFE","DEAD","FEAR","FIRE",
    "FORM","GOOD","LORD","KING","WISE","WORD","WORK","PATH","RUNE",
    "WITHIN","FOLLOW","PILGRIM","WISDOM","CONSUMPTION","CIRCUMFERENCE",
    "PRIMES","NUMBERS","REARRANGING","SHOW","DEOR","DIVINITY"}

def word_score(text):
    sc=0; tu=text.upper()
    for w in COMMON_WORDS:
        st=0
        while True:
            p=tu.find(w,st)
            if p<0: break
            sc+=len(w); st=p+1
    return sc

def sieve_primes(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(2,n+1) if s[i]]

PRIMES = sieve_primes(50000)
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]

# Load Deor poem
deor_path = "c:\\Users\\tyler\\Repos\\Cicada3301\\Analysis\\Reference_Docs\\deor_poem.txt"
with open(deor_path, 'r', encoding='utf-8') as f:
    deor_text = f.read()

# Convert Deor to GP indices (map Latin letters to GP)
LATIN_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15
}

# Method 1: Deor as Latin text -> GP indices
deor_latin = [c.upper() for c in deor_text if c.upper() in LATIN_TO_GP]
deor_gp = [LATIN_TO_GP[c] for c in deor_latin]
print(f"Deor poem: {len(deor_text)} chars, {len(deor_latin)} Latin chars, {len(deor_gp)} GP values")
print(f"First 30 Deor GP: {deor_gp[:30]}")
print(f"First 30 Deor text: {''.join(deor_latin[:30])}")

# Method 2: Deor has rune characters too? Check for runes in the text
deor_runes_raw = [GP_RUNE_TO_IDX[c] for c in deor_text if c in GP_RUNE_TO_IDX]
print(f"Deor rune characters found: {len(deor_runes_raw)}")

# Load target pages
pages = {}
for pn in range(18, 55):
    r = load_runes(pn)
    if r and len(r) > 50:
        pages[pn] = r

print(f"\nLoaded {len(pages)} pages")
for pn in sorted(pages.keys()):
    print(f"  P{pn}: {len(pages[pn])} runes")

# =========================================================================
# ATTACK 1: Prime-indexed Deor characters as keystream
# "Rearranging the primes will show a path TO THE DEOR"
# -> Use primes to index into the Deor poem text
# =========================================================================
print("\n" + "="*80)
print("ATTACK 1: Prime-indexed Deor characters as keystream")
print("="*80)

best_results = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for prime_start in [0, 1]:  # 0-indexed or 1-indexed
        for use_mod in [True, False]:  # mod len(deor) or direct
            for prime_type in ["sequential", "gp_primes"]:
                if prime_type == "sequential":
                    prime_seq = PRIMES[:n]
                else:
                    # Cycle GP primes
                    prime_seq = [GP_PRIMES[i % 29] for i in range(n)]
                
                key = []
                for i in range(n):
                    p = prime_seq[i]
                    idx = (p - prime_start)
                    if use_mod:
                        idx = idx % len(deor_gp)
                    if idx < len(deor_gp):
                        key.append(deor_gp[idx])
                    else:
                        key.append(0)
                
                for mode in ["SUB", "ADD", "BEAUFORT"]:
                    if mode == "SUB":
                        plain = [(cipher[i]-key[i])%MOD for i in range(n)]
                    elif mode == "ADD":
                        plain = [(cipher[i]+key[i])%MOD for i in range(n)]
                    else:
                        plain = [(key[i]-cipher[i])%MOD for i in range(n)]
                    
                    ic = ioc(plain)
                    txt = to_text(plain)
                    ws = word_score(txt)
                    
                    if ic > 1.25 or ws > 20:
                        tag = f"P{page_num}/{prime_type}/start{prime_start}/{'mod' if use_mod else 'nomod'}/{mode}"
                        best_results.append((ic, ws, tag, txt[:80]))

best_results.sort(key=lambda x: (-x[0], -x[1]))
print("Top 10:")
for ic, ws, tag, txt in best_results[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 2: Totient-modified Deor key (P55 style)
# P55: plain[i] = (cipher[i] - (prime[i] - 1)) % 29
# General: key[i] = deor[i] modified by totient(prime[i])
# =========================================================================
print("\n" + "="*80)
print("ATTACK 2: Deor + totient(prime) combined keystream")
print("="*80)

best2 = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for combo_mode in ["deor_plus_totient", "deor_minus_totient", "totient_minus_deor",
                        "deor_xor_totient", "deor_at_prime", "totient_only"]:
        for deor_offset in [0, 1, 10, 100]:
            key = []
            for i in range(n):
                p = PRIMES[i] if i < len(PRIMES) else PRIMES[i % len(PRIMES)]
                tot = (p - 1) % MOD
                d_idx = (i + deor_offset) % len(deor_gp)
                d = deor_gp[d_idx]
                
                if combo_mode == "deor_plus_totient":
                    key.append((d + tot) % MOD)
                elif combo_mode == "deor_minus_totient":
                    key.append((d - tot) % MOD)
                elif combo_mode == "totient_minus_deor":
                    key.append((tot - d) % MOD)
                elif combo_mode == "deor_xor_totient":
                    key.append((d ^ tot) % MOD)
                elif combo_mode == "deor_at_prime":
                    # Index into Deor at prime position
                    d_p = deor_gp[p % len(deor_gp)]
                    key.append(d_p)
                elif combo_mode == "totient_only":
                    key.append(tot)
            
            for mode in ["SUB", "ADD"]:
                if mode == "SUB":
                    plain = [(cipher[i]-key[i])%MOD for i in range(n)]
                else:
                    plain = [(cipher[i]+key[i])%MOD for i in range(n)]
                
                ic = ioc(plain)
                txt = to_text(plain)
                ws = word_score(txt)
                
                if ic > 1.25 or ws > 20:
                    tag = f"P{page_num}/{combo_mode}/off{deor_offset}/{mode}"
                    best2.append((ic, ws, tag, txt[:80]))

best2.sort(key=lambda x: (-x[0], -x[1]))
print("Top 10:")
for ic, ws, tag, txt in best2[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================  
# ATTACK 3: Fibonacci-spiral prime ordering
# From page 15 grid: primes ordered by Fibonacci positions
# =========================================================================
print("\n" + "="*80)
print("ATTACK 3: Fibonacci-indexed primes as keystream")  
print("="*80)

# Fibonacci sequence
fib = [0, 1]
while fib[-1] < 50000:
    fib.append(fib[-1] + fib[-2])

# Method 1: Use fib[i]-th prime
fib_primes = []
for f in fib:
    if f < len(PRIMES):
        fib_primes.append(PRIMES[f])
print(f"Fibonacci-indexed primes: {fib_primes[:20]}")

# Method 2: Primes that are Fibonacci numbers
fib_set = set(fib[:50])
fib_as_primes = [p for p in PRIMES[:200] if p in fib_set]
print(f"Primes that are Fibonacci: {fib_as_primes}")

best3 = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    # Key from Fibonacci-indexed primes mod 29
    for key_type in ["fib_prime_mod29", "fib_prime_totient", "fib_idx_deor"]:
        key = []
        for i in range(n):
            if key_type == "fib_prime_mod29":
                if i < len(fib_primes):
                    key.append(fib_primes[i] % MOD)
                else:
                    key.append(fib_primes[i % len(fib_primes)] % MOD)
            elif key_type == "fib_prime_totient":
                if i < len(fib_primes):
                    key.append((fib_primes[i] - 1) % MOD)
                else:
                    key.append((fib_primes[i % len(fib_primes)] - 1) % MOD)
            elif key_type == "fib_idx_deor":
                # Index Deor at Fibonacci positions
                fi = fib[i % len(fib)] % len(deor_gp)
                key.append(deor_gp[fi])
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 20:
                tag = f"P{page_num}/{key_type}/{mode}"
                best3.append((ic, ws, tag, txt[:80]))

best3.sort(key=lambda x: (-x[0], -x[1]))
print("Top 10:")
for ic, ws, tag, txt in best3[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 4: Deor as running key on ALL pages (now with correct path)
# =========================================================================
print("\n" + "="*80)
print("ATTACK 4: Deor running key on all pages")
print("="*80)

best4 = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    if len(deor_gp) < n:
        continue
        
    for offset in range(0, min(100, len(deor_gp) - n + 1), 5):
        dk = deor_gp[offset:offset+n]
        for mode in ["SUB", "ADD", "BEAUFORT"]:
            if mode == "SUB":
                plain = [(cipher[i]-dk[i])%MOD for i in range(n)]
            elif mode == "ADD":
                plain = [(cipher[i]+dk[i])%MOD for i in range(n)]
            else:
                plain = [(dk[i]-cipher[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 25:
                tag = f"P{page_num}/off{offset}/{mode}"
                best4.append((ic, ws, tag, txt[:80]))

best4.sort(key=lambda x: (-x[0], -x[1]))
print("Top 10:")
for ic, ws, tag, txt in best4[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 5: P55-style totient cipher with sequential primes on ALL pages
# (The proven method from P55, applied page by page)
# =========================================================================
print("\n" + "="*80)
print("ATTACK 5: P55 totient method on all pages")
print("="*80)

for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for prime_offset in [0, 1, 5, 10, 20, 50, 100, 200]:
        for mode in ["SUB", "ADD"]:
            key = [(PRIMES[i + prime_offset] - 1) % MOD for i in range(n)]
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.30 or ws > 30:
                print(f"  P{page_num}/prime_off={prime_offset}/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:100]}")

# =========================================================================
# ATTACK 6: Interleaving Deor and primes — "a path TO the Deor"
# What if primes define a PATH (permutation) through the Deor text?
# =========================================================================
print("\n" + "="*80)
print("ATTACK 6: Primes as path permutation through Deor")
print("="*80)

best6 = []
for page_num in sorted(pages.keys())[:5]:  # Top 5 pages only
    cipher = pages[page_num]
    n = len(cipher)
    
    for path_type in ["prime_mod_deor", "prime_inv_mod_deor", "cumsum_prime_mod",
                      "prime_times_i_mod", "gp_prime_repeat_path"]:
        key = []
        cumsum = 0
        for i in range(n):
            p = PRIMES[i]
            if path_type == "prime_mod_deor":
                idx = p % len(deor_gp)
            elif path_type == "prime_inv_mod_deor":
                idx = (len(deor_gp) - p % len(deor_gp)) % len(deor_gp)
            elif path_type == "cumsum_prime_mod":
                cumsum = (cumsum + p) % len(deor_gp)
                idx = cumsum
            elif path_type == "prime_times_i_mod":
                idx = (p * (i+1)) % len(deor_gp)
            elif path_type == "gp_prime_repeat_path":
                gp = GP_PRIMES[i % 29]
                idx = (gp * (i // 29 + 1)) % len(deor_gp)
            key.append(deor_gp[idx])
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 20:
                tag = f"P{page_num}/{path_type}/{mode}"
                best6.append((ic, ws, tag, txt[:80]))

best6.sort(key=lambda x: (-x[0], -x[1]))
print("Top 10:")
for ic, ws, tag, txt in best6[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 7: LFSR-based keystream
# Community suggests LFSR with prime-related polynomial
# =========================================================================
print("\n" + "="*80)
print("ATTACK 7: LFSR-based keystream")
print("="*80)

def lfsr_stream(taps, init_state, length, mod=29):
    """Generate LFSR-based keystream mod 29."""
    state = list(init_state)
    degree = len(state)
    stream = []
    for _ in range(length):
        stream.append(state[0] % mod)
        fb = sum(state[t] for t in taps) % mod
        state = state[1:] + [fb]
    return stream

best7 = []
# Try various LFSR configurations
lfsr_configs = [
    # (taps, init_state, name)
    ([0, 2], [1, 0, 1], "deg3_taps02"),
    ([0, 4], [1, 0, 1, 0, 1], "deg5_taps04"),
    ([0, 1], [2, 3, 5], "deg3_seed235"),
    ([0, 2, 4], [2, 3, 5, 7, 11], "deg5_primes"),
    ([0, 6], [2, 3, 5, 7, 11, 13, 17], "deg7_primes"),
    ([0, 3, 7], [2, 3, 5, 7, 11, 13, 17, 19], "deg8_primes"),
    # Using DIVINITY as init state
    ([0, 7], [23, 10, 1, 10, 9, 10, 16, 26], "deg8_divinity"),
    ([0, 3], [23, 10, 1, 10, 9, 10, 16, 26], "deg8_divinity_t03"),
    # Using GP primes as taps
    ([0, 1, 2, 4], [1, 1, 1, 1, 1], "deg5_taps0124"),
    # P19 key fragment as seed
    ([0, 8], P19_KEY[:9], "deg9_p19key"),
    ([0, 5], P19_KEY[:6], "deg6_p19key"),
    # Missing prime gap (73) related
    ([0, 3, 6], [7, 3, 7, 9, 1, 3, 7], "deg7_73mod29"),
]

for taps, init, name in lfsr_configs:
    for page_num in [18, 19, 20, 21]:
        cipher = pages[page_num]
        n = len(cipher)
        key = lfsr_stream(taps, init, n)
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 20:
                tag = f"P{page_num}/{name}/{mode}"
                best7.append((ic, ws, tag, txt[:80]))

best7.sort(key=lambda x: (-x[0], -x[1]))
print(f"Top 10 (from {len(best7)} candidates):")
for ic, ws, tag, txt in best7[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 8: Cookie primes 167/761 as key parameters
# =========================================================================
print("\n" + "="*80)
print("ATTACK 8: Cookie primes 167/761")
print("="*80)

for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for key_type in ["167mod29", "761mod29", "167_761_alt", "167_761_add",
                     "prime167_idx", "prime761_idx"]:
        key = []
        for i in range(n):
            if key_type == "167mod29":
                key.append((167 * (i+1)) % MOD)
            elif key_type == "761mod29":
                key.append((761 * (i+1)) % MOD)
            elif key_type == "167_761_alt":
                key.append((167 if i%2==0 else 761) % MOD)
            elif key_type == "167_761_add":
                key.append((167 + 761 * i) % MOD)
            elif key_type == "prime167_idx":
                # 167th prime = 991
                key.append(PRIMES[167 + i] % MOD)
            elif key_type == "prime761_idx":
                key.append(PRIMES[761 + i] % MOD)
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.30 or ws > 25:
                print(f"  P{page_num}/{key_type}/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:100]}")

# =========================================================================
# ATTACK 9: Missing primes (73-1223) as key
# =========================================================================
print("\n" + "="*80)
print("ATTACK 9: Missing telnet primes (73-1223) as key")
print("="*80)

missing_primes = [p for p in PRIMES if 73 <= p <= 1223]
print(f"Missing primes count: {len(missing_primes)}")
print(f"First 20: {missing_primes[:20]}")

best9 = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for key_mode in ["mod29", "totient_mod29", "diff_mod29"]:
        key = []
        for i in range(n):
            mp = missing_primes[i % len(missing_primes)]
            if key_mode == "mod29":
                key.append(mp % MOD)
            elif key_mode == "totient_mod29":
                key.append((mp - 1) % MOD)
            elif key_mode == "diff_mod29":
                if i < len(missing_primes) - 1:
                    key.append((missing_primes[i+1] - missing_primes[i]) % MOD)
                else:
                    key.append(0)
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 20:
                tag = f"P{page_num}/{key_mode}/{mode}"
                best9.append((ic, ws, tag, txt[:80]))

best9.sort(key=lambda x: (-x[0], -x[1]))
print("Top 10:")
for ic, ws, tag, txt in best9[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 10: Self-referential / Beaufort-Autokey with Deor seed
# If cipher is Beaufort-autokey: C[i] = (key[i] - P[i]) mod 29
# where key[i] = Deor[i] for first N positions, then key[i] = P[i-N]
# =========================================================================
print("\n" + "="*80)
print("ATTACK 10: Beaufort/Vigenere autokey with Deor seed")
print("="*80)

for page_num in sorted(pages.keys())[:10]:
    cipher = pages[page_num]
    n = len(cipher)
    
    for seed_len in [5, 10, 20, 29, 47, 100]:
        if seed_len > len(deor_gp):
            continue
        seed = deor_gp[:seed_len]
        
        for ak_mode in ["pt_sub", "pt_add", "ct_sub", "ct_add",
                        "pt_beaufort", "ct_beaufort"]:
            plain = []
            for i in range(n):
                if i < seed_len:
                    k = seed[i]
                else:
                    if ak_mode.startswith("pt"):
                        k = plain[i - seed_len]
                    else:
                        k = cipher[i - seed_len]
                
                if ak_mode.endswith("sub"):
                    plain.append((cipher[i] - k) % MOD)
                elif ak_mode.endswith("add"):
                    plain.append((cipher[i] + k) % MOD)
                else:
                    plain.append((k - cipher[i]) % MOD)
            
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 20:
                print(f"  P{page_num}/seed{seed_len}/{ak_mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:100]}")

# =========================================================================
# ATTACK 11: Combine prime positions with GP value modification  
# Key[i] = (GP_prime_value[cipher[i]] - totient(seq_prime[i])) mod 29
# (like P55 but using GP prime VALUES of the cipher runes)
# =========================================================================
print("\n" + "="*80)
print("ATTACK 11: GP prime value transformation")
print("="*80)

for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for transform in ["gp_sub_totient", "gp_sub_prime", "gp_add_totient",
                      "prime_of_gp_mod29"]:
        plain = []
        for i in range(n):
            gp_val = GP_PRIMES[cipher[i]]  # Get the actual prime for this rune
            p_i = PRIMES[i]  # Sequential prime
            
            if transform == "gp_sub_totient":
                plain.append((gp_val - (p_i - 1)) % MOD)
            elif transform == "gp_sub_prime":
                plain.append((gp_val - p_i) % MOD)
            elif transform == "gp_add_totient":
                plain.append((gp_val + (p_i - 1)) % MOD)
            elif transform == "prime_of_gp_mod29":
                plain.append((gp_val * p_i) % MOD)
        
        ic = ioc(plain)
        txt = to_text(plain)
        ws = word_score(txt)
        if ic > 1.25 or ws > 25:
            print(f"  P{page_num}/{transform}: IoC={ic:.3f} ws={ws}")
            print(f"    {txt[:100]}")

print("\nDONE")
