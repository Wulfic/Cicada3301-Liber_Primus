#!/usr/bin/env python3
"""
Novel Cipher Classes Attack
============================
All standard additive ciphers (Vigenere, Beaufort, running key, autokey, LFSR)
have failed. Try:
1. Multiplicative cipher (mod 29)
2. Affine cipher
3. Outguess hex blob analysis
4. Bifid/trifid cipher
5. Gromark cipher (running key from cipher differences)
6. Transposition then substitution
7. Page-number-specific derivation
8. Double-layer prime operations
"""
import os, sys, io, math, struct
from collections import Counter
from itertools import product

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GP_RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C2\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11
MOD = 29
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def sieve_primes(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(2,n+1) if s[i]]
PRIMES = sieve_primes(50000)

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

# Multiplicative inverse mod 29
def mod_inv(a, m=29):
    if a % m == 0: return None
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

# Precompute inverses
INV = {i: mod_inv(i) for i in range(1, MOD)}

# Load pages
pages = {}
for pn in range(18, 55):
    r = load_runes(pn)
    if r and len(r) > 50:
        pages[pn] = r

P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,21,1,10,24]

print(f"Loaded {len(pages)} pages")

# =========================================================================
# ATTACK 1: Multiplicative cipher mod 29
# cipher[i] = (plain[i] * key[i]) mod 29
# plain[i] = (cipher[i] * inv(key[i])) mod 29
# =========================================================================
print("\n" + "="*80)
print("ATTACK 1: Multiplicative cipher mod 29")
print("="*80)

best1 = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    # Multiplicative with sequential primes
    for key_type in ["prime_mod29", "gp_prime_cycle", "fixed_mult"]:
        for key_param in range(1, 29):
            if key_type == "fixed_mult":
                if key_param > 1:
                    break  # Only try fixed multipliers 1-28
                key = [key_param] * n
            elif key_type == "prime_mod29":
                key = [(PRIMES[i] % MOD) for i in range(n)]
                if key_param > 1:
                    break
            elif key_type == "gp_prime_cycle":
                key = [GP_PRIMES[i % 29] % MOD for i in range(n)]
                if key_param > 1:
                    break
            
            plain = []
            valid = True
            for i in range(n):
                c = cipher[i]
                k = key[i] if key_type != "fixed_mult" else key_param
                if k == 0:
                    plain.append(c)
                    continue
                inv_k = INV.get(k % MOD)
                if inv_k is None:
                    plain.append(c)
                    continue
                plain.append((c * inv_k) % MOD)
            
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 30:
                tag = f"P{page_num}/{key_type}/{key_param}"
                best1.append((ic, ws, tag, txt[:80]))

# Also try multiplicative Vigenere: fixed multiplier per column
for page_num in [18, 20, 25, 32, 40, 44, 50]:
    cipher = pages[page_num]
    n = len(cipher)
    for k in [2, 3, 5, 7]:
        for mult_key in product(range(1, MOD), repeat=k):
            if k >= 5:
                break  # Too many combos for k>=5
            plain = []
            for i in range(n):
                m = mult_key[i % k]
                inv_m = INV.get(m)
                if inv_m is None:
                    plain.append(cipher[i])
                else:
                    plain.append((cipher[i] * inv_m) % MOD)
            ic = ioc(plain)
            if ic > 1.4:
                txt = to_text(plain)
                ws = word_score(txt)
                if ws > 20:
                    best1.append((ic, ws, f"P{page_num}/mult_vig/k{k}/{mult_key}", txt[:80]))
        if k >= 4:
            break  # Skip k=5,7 for larger keys

best1.sort(key=lambda x: (-x[0], -x[1]))
print(f"Top 10 (from {len(best1)} candidates):")
for ic, ws, tag, txt in best1[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 2: Affine cipher per period
# cipher[i] = (a * plain[i] + b) mod 29
# plain[i] = inv(a) * (cipher[i] - b) mod 29
# =========================================================================
print("\n" + "="*80)
print("ATTACK 2: Periodic affine cipher")
print("="*80)

best2 = []
for page_num in [18, 20, 32, 40, 44, 50]:
    cipher = pages[page_num]
    n = len(cipher)
    
    # Period 1: try all (a, b) pairs
    for a in range(1, MOD):
        inv_a = INV.get(a)
        if inv_a is None:
            continue
        for b in range(MOD):
            plain = [(inv_a * (cipher[i] - b)) % MOD for i in range(n)]
            ic = ioc(plain)
            if ic > 1.4:
                txt = to_text(plain)
                ws = word_score(txt)
                if ws > 15:
                    best2.append((ic, ws, f"P{page_num}/a={a}/b={b}", txt[:80]))

best2.sort(key=lambda x: (-x[0], -x[1]))
print(f"Top 10 (from {len(best2)} candidates):")
for ic, ws, tag, txt in best2[:10]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 3: Analyze outguess_00.txt hex blob
# =========================================================================
print("\n" + "="*80)
print("ATTACK 3: Outguess hex blob analysis")
print("="*80)

outguess_path = "c:\\Users\\tyler\\Repos\\Cicada3301\\outguess_00.txt"
with open(outguess_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract hex data (between PGP headers)
hex_data = ""
in_data = False
for line in lines:
    line = line.strip()
    if line.startswith("-----BEGIN PGP SIGNATURE"):
        break
    if in_data and line and not line.startswith("-----"):
        hex_data += line
    if line == "":
        in_data = True
    if "Hash:" in line:
        in_data = True

# Clean hex
hex_data = ''.join(c for c in hex_data if c in '0123456789abcdef')
print(f"Hex data: {len(hex_data)} hex chars = {len(hex_data)//2} bytes")

# Convert to bytes
try:
    raw_bytes = bytes.fromhex(hex_data)
    print(f"First 50 bytes: {raw_bytes[:50].hex()}")
    print(f"First 50 as decimal: {list(raw_bytes[:50])}")
    
    # Check if bytes mod 29 could be GP indices
    as_gp = [b % MOD for b in raw_bytes]
    print(f"First 30 as GP (mod 29): {as_gp[:30]}")
    print(f"As text: {to_text(as_gp[:80])}")
    ic_gp = ioc(as_gp)
    print(f"IoC of full hex mod 29: {ic_gp:.3f}")
    
    # Check byte frequency
    bc = Counter(raw_bytes)
    print(f"Unique byte values: {len(bc)}")
    print(f"Most common: {bc.most_common(5)}")
    print(f"Least common: {bc.most_common()[-5:]}")
    
    # Try as key for P18
    cipher = pages[18]
    n = min(len(cipher), len(as_gp))
    for mode in ["SUB", "ADD", "BEAUFORT"]:
        if mode == "SUB":
            plain = [(cipher[i]-as_gp[i])%MOD for i in range(n)]
        elif mode == "ADD":
            plain = [(cipher[i]+as_gp[i])%MOD for i in range(n)]
        else:
            plain = [(as_gp[i]-cipher[i])%MOD for i in range(n)]
        ic = ioc(plain)
        txt = to_text(plain)
        ws = word_score(txt)
        print(f"  As P18 key ({mode}): IoC={ic:.3f} ws={ws}")
        print(f"    {txt[:100]}")
    
    # Try as key cycled
    for page_num in [18, 19, 20, 21]:
        cipher = pages[page_num]
        n = len(cipher)
        # Cycle the hex bytes as key
        key = [raw_bytes[i % len(raw_bytes)] % MOD for i in range(n)]
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.15 or ws > 20:
                print(f"  P{page_num} hex-cycled {mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:80]}")

except Exception as e:
    print(f"Hex parsing error: {e}")

# =========================================================================
# ATTACK 4: Gromark cipher (running key from cipher differences)
# Key stream = cumulative differences of cipher values
# =========================================================================
print("\n" + "="*80)
print("ATTACK 4: Gromark / difference-based cipher")
print("="*80)

for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    for method in ["cumsum_diff", "running_diff", "fibonacci_sum"]:
        key = []
        if method == "cumsum_diff":
            # Key[i] = sum of first i cipher values mod 29
            s = 0
            for c in cipher:
                s = (s + c) % MOD
                key.append(s)
        elif method == "running_diff":
            # Key[i] = cipher[i] - cipher[i-1] mod 29
            key.append(cipher[0])
            for i in range(1, n):
                key.append((cipher[i] - cipher[i-1]) % MOD)
        elif method == "fibonacci_sum":
            # Key built from Fibonacci-like recurrence on cipher
            key.append(cipher[0])
            if n > 1:
                key.append(cipher[1])
            for i in range(2, n):
                key.append((key[i-1] + key[i-2]) % MOD)
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.20 or ws > 25:
                print(f"  P{page_num}/{method}/{mode}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:80]}")

# =========================================================================
# ATTACK 5: Columnar transposition BEFORE substitution
# If text was first transposed then encrypted, undo transposition first
# =========================================================================
print("\n" + "="*80)
print("ATTACK 5: Undo columnar transposition then frequency analysis")
print("="*80)

def undo_columnar(cipher, ncols):
    """Undo a simple columnar transposition: text was written by rows into
    ncols columns, then read out column by column."""
    n = len(cipher)
    nrows = math.ceil(n / ncols)
    full_cols = n % ncols or ncols  # number of columns with nrows elements
    
    # Reconstruct grid
    grid = [None] * n
    idx = 0
    for col in range(ncols):
        col_len = nrows if col < full_cols else nrows - 1
        for row in range(col_len):
            pos = row * ncols + col
            if pos < n:
                grid[pos] = cipher[idx]
            idx += 1
    
    return [g for g in grid if g is not None]

for page_num in [18, 20, 21, 26, 29]:
    cipher = pages[page_num]
    n = len(cipher)
    
    for ncols in range(2, min(30, n//3)):
        untrans = undo_columnar(cipher, ncols)
        if len(untrans) != n:
            continue
        
        # Check if untransposed version has better periodic IoC
        for k in [5, 7, 8, 9, 10, 11, 13, 17, 20]:
            cols = [[] for _ in range(k)]
            for i, v in enumerate(untrans):
                cols[i%k].append(v)
            avg_ioc = sum(ioc(c) for c in cols) / k
            if avg_ioc > 1.5:
                print(f"  P{page_num} untrans(ncols={ncols}) k={k}: avg_col_IoC={avg_ioc:.3f}")
                # Try frequency-based decryption
                key = []
                for col_data in cols:
                    best_s, best_chi = 0, float('inf')
                    for s in range(MOD):
                        shifted = [(v-s)%MOD for v in col_data]
                        counts = Counter(shifted)
                        ch = sum((counts.get(i,0))**2 for i in range(MOD))
                        if ch > best_chi:  # maximize coincidence
                            best_chi = ch; best_s = s
                    key.append(best_s)
                plain = [(untrans[i]-key[i%k])%MOD for i in range(n)]
                txt = to_text(plain)
                ws = word_score(txt)
                ic = ioc(plain)
                print(f"    Decrypted: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:100]}")

# =========================================================================
# ATTACK 6: XOR-based cipher (bitwise operations on rune values)
# =========================================================================
print("\n" + "="*80)
print("ATTACK 6: XOR-based operations")
print("="*80)

for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    
    # XOR with sequential primes
    for key_type in ["prime_xor", "const_xor", "gp_prime_xor"]:
        for param in range(1, 30):
            key = []
            for i in range(n):
                if key_type == "prime_xor":
                    key.append(PRIMES[i] % 32)  # Keep within 5 bits
                    if param > 1:
                        break
                elif key_type == "const_xor":
                    key.append(param)
                elif key_type == "gp_prime_xor":
                    key.append(GP_PRIMES[i % 29])
                    if param > 1:
                        break
            
            if len(key) < n:
                if key_type in ["prime_xor", "gp_prime_xor"] and param == 1:
                    key = key  # Already length n
                else:
                    continue
            
            plain = [(cipher[i] ^ key[i]) % MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.25 or ws > 25:
                print(f"  P{page_num}/{key_type}/{param}: IoC={ic:.3f} ws={ws}")
                print(f"    {txt[:80]}")

# =========================================================================
# ATTACK 7: Page-number-specific key derivation
# key[i] = f(page_number, i, prime[i]) mod 29
# =========================================================================
print("\n" + "="*80)
print("ATTACK 7: Page-number-specific key derivation")
print("="*80)

best7 = []
for page_num in sorted(pages.keys()):
    cipher = pages[page_num]
    n = len(cipher)
    pn = page_num
    
    for formula in ["pn_times_prime", "pn_plus_prime", "pn_times_i",
                    "pn_xor_prime", "pn_times_i_plus_prime",
                    "prime_minus_pn", "pn_pow_i"]:
        key = []
        for i in range(n):
            p = PRIMES[i]
            if formula == "pn_times_prime":
                key.append((pn * p) % MOD)
            elif formula == "pn_plus_prime":
                key.append((pn + p) % MOD)
            elif formula == "pn_times_i":
                key.append((pn * (i+1)) % MOD)
            elif formula == "pn_xor_prime":
                key.append((pn ^ p) % MOD)
            elif formula == "pn_times_i_plus_prime":
                key.append((pn * (i+1) + p) % MOD)
            elif formula == "prime_minus_pn":
                key.append((p - pn) % MOD)
            elif formula == "pn_pow_i":
                key.append(pow(pn, i+1, MOD))
        
        for mode in ["SUB", "ADD"]:
            if mode == "SUB":
                plain = [(cipher[i]-key[i])%MOD for i in range(n)]
            else:
                plain = [(cipher[i]+key[i])%MOD for i in range(n)]
            ic = ioc(plain)
            txt = to_text(plain)
            ws = word_score(txt)
            if ic > 1.20 or ws > 25:
                tag = f"P{page_num}/{formula}/{mode}"
                best7.append((ic, ws, tag, txt[:80]))

best7.sort(key=lambda x: (-x[0], -x[1]))
print(f"Top 15 (from {len(best7)} candidates):")
for ic, ws, tag, txt in best7[:15]:
    print(f"  {tag}: IoC={ic:.3f} ws={ws}")
    print(f"    {txt}")

# =========================================================================
# ATTACK 8: P19 key analysis — try to find the GENERATING RULE
# The P19 key is meaningful text. If we can understand its structure,
# we might derive keys for other pages.
# =========================================================================
print("\n" + "="*80)
print("ATTACK 8: Deep P19 key structure analysis")
print("="*80)

print(f"P19 key: {P19_KEY}")
print(f"P19 key text: {to_text(P19_KEY)}")
print(f"P19 key length: {len(P19_KEY)}")

# Check if key values correspond to any known sequence
print("\nKey value analysis:")
print(f"  Sum: {sum(P19_KEY)} (mod 29 = {sum(P19_KEY) % MOD})")
print(f"  Unique values: {len(set(P19_KEY))}")
print(f"  Missing values: {set(range(MOD)) - set(P19_KEY)}")
print(f"  Value counts: {Counter(P19_KEY).most_common()}")

# Check relationship between key and cipher at each position
p19_cipher = pages[19]
print(f"\nP19 cipher indices (first 47): {p19_cipher[:47]}")

# Compute cipher - key, cipher + key, key - cipher for first 47
print("\nP19 cipher - key (mod 29) = KNOWN PLAINTEXT:")
p19_plain = [(p19_cipher[i] - P19_KEY[i]) % MOD for i in range(47)]
print(f"  Plain: {p19_plain}")
print(f"  Text: {to_text(p19_plain)}")

# Does the plain text continue past position 47?
# If the key is 47 long and non-repeating, we need to know the full key
print(f"\nP19 beyond position 47 (271-47=224 remaining runes):")
print(f"  Key is only 47 values, cannot decrypt remainder without key")

# What if the key continues with more English text?
# The key text is: A-S-TH-A-R-NG-J-I-L-T-N-M-Y-J-W-C-J-G-IA-H-OE-AE-NG-T-AE-F-IA-N-NG-W-IA-S-NG-N-O-T-C-OE-E-R-C-E-D-NG-U-I-A
# Reading: "A STAR NG JILT NM YJWCJG IA H OE AE NG T AE F IAN NG W IAS NG NOT COERCED NG U I A"
# With NG as separator: sentences = "A STAR", "JILT NM YJWCJG IA H OE AE", "T AE F IAN", "WIAS", "NOT COERCED", "UIA"

# Check: is the key the Deor poem text at prime positions?
deor_path = "c:\\Users\\tyler\\Repos\\Cicada3301\\Analysis\\Reference_Docs\\deor_poem.txt"
with open(deor_path, 'r', encoding='utf-8') as f:
    deor_text = f.read()
LATIN_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15
}
deor_latin = [c.upper() for c in deor_text if c.upper() in LATIN_TO_GP]
deor_gp = [LATIN_TO_GP[c] for c in deor_latin]

print("\nChecking if P19 key = Deor at prime positions:")
for prime_start in [0, 1]:
    for method in ["sequential", "gp"]:
        matches = 0
        for i in range(47):
            if method == "sequential":
                p = PRIMES[i] - prime_start
            else:
                p = GP_PRIMES[i % 29] - prime_start
            if 0 <= p < len(deor_gp):
                if deor_gp[p] == P19_KEY[i]:
                    matches += 1
        print(f"  {method}/start{prime_start}: {matches}/47 matches")

# Check if P19 key = Deor consecutive characters at some offset
print("\nChecking if P19 key = Deor at any consecutive offset:")
for offset in range(len(deor_gp) - 47):
    matches = sum(1 for i in range(47) if deor_gp[offset + i] == P19_KEY[i])
    if matches > 10:
        print(f"  offset={offset}: {matches}/47 matches")
        print(f"  Deor[{offset}:{offset+47}] text: {''.join(deor_latin[offset:offset+47])}")

# Check: key[i] = (cipher[i] + something[i]) mod 29?
# If key comes from a simple transform of the cipher...
print("\nRelationship: key[i] vs cipher[i]:")
for i in range(47):
    diff_add = (P19_KEY[i] - p19_cipher[i]) % MOD
    diff_sub = (p19_cipher[i] - P19_KEY[i]) % MOD
    diff_xor = P19_KEY[i] ^ p19_cipher[i]
    if i < 20:
        print(f"  i={i:2d}: cipher={p19_cipher[i]:2d} key={P19_KEY[i]:2d}  "
              f"key-cipher={diff_add:2d}  cipher-key={diff_sub:2d}  xor={diff_xor:2d}")

# The key-cipher differences are the NEGATIVE of the plaintext values
# (Because in ADD mode: plain = cipher + key, so key - cipher = -(plain))
# cipher + key = plain, so PLAIN = known "REARRANGING..."
# Let's verify
p19_known_plain_text = "REARRANGINGTHEPRIMESNUMBERSWILLSHOWAPATHTOTHEDEOR"
# Map to GP
known_plain = []
i = 0
while i < len(p19_known_plain_text):
    if i+1 < len(p19_known_plain_text):
        digraph = p19_known_plain_text[i:i+2]
        if digraph in ['TH', 'NG', 'EO', 'OE', 'AE', 'IA', 'EA']:
            idx = GP_LETTERS.index(digraph)
            known_plain.append(idx)
            i += 2
            continue
    c = p19_known_plain_text[i]
    if c in LATIN_TO_GP:
        known_plain.append(LATIN_TO_GP[c])
    i += 1

print(f"\nP19 known plaintext as GP: {known_plain}")
print(f"Plain text: {to_text(known_plain)}")
print(f"Length: {len(known_plain)}")

# Verify: cipher + key = plain? or cipher - key = plain?
print(f"\nP19 mode detection:")
for mode in ["ADD", "SUB", "BEAUFORT"]:
    for i in range(min(47, len(known_plain))):
        if mode == "ADD":
            check = (p19_cipher[i] + P19_KEY[i]) % MOD
        elif mode == "SUB":
            check = (p19_cipher[i] - P19_KEY[i]) % MOD
        else:
            check = (P19_KEY[i] - p19_cipher[i]) % MOD
        if check != known_plain[i]:
            break
    else:
        print(f"  {mode}: MATCHES for all {min(47, len(known_plain))} positions!")
        continue
    # Count matches
    cnt = 0
    for j in range(min(47, len(known_plain))):
        if mode == "ADD":
            c = (p19_cipher[j] + P19_KEY[j]) % MOD
        elif mode == "SUB":
            c = (p19_cipher[j] - P19_KEY[j]) % MOD
        else:
            c = (P19_KEY[j] - p19_cipher[j]) % MOD
        if c == known_plain[j]:
            cnt += 1
    print(f"  {mode}: {cnt}/{min(47, len(known_plain))} matches")

print("\nDONE")
