"""
CREATIVE KEY DERIVATION ATTACK
1. Magic square numbers (mod 29) as keys
2. Prime sequence directly (not totient) as keys
3. Fibonacci, Lucas, Catalan sequences
4. Greek/Hebrew gematria-derived keys
5. Multiplicative cipher (c * k_inv % 29)  
6. Self-referential: use the ciphertext itself as key material
7. Page-number based keys

FOCUS: P20 (812 runes = matches P16 magic square!)
       P22 (131 runes = matches P63 magic square!)
       P42 (272 runes = matches P63 magic square!)
"""
import os
from collections import Counter
from math import gcd

RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def load_page(pn):
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rune_text = ''.join(line for line in lines if not (line.strip() and line.strip()[0].isascii() and line.strip()[0].isalpha()))
    return [RUNE_TO_INDEX[c] for c in rune_text if c in RUNE_TO_INDEX]

def ioc29(vals):
    if len(vals) < 2: return 0
    ct = Counter(vals); n = len(vals)
    return 29 * sum(c*(c-1) for c in ct.values()) / (n*(n-1))

def text(vals): return ''.join(GP[v] for v in vals)

def score_english(vals):
    t = text(vals).upper()
    score = 0
    for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS',
              'ONE','OUR','OUT','HIS','HAS','ITS','WHO','OWN','SAY','SHE','LET']:
        score += t.count(w) * 3
    for w in ['OF','TO','IN','IS','IT','AN','OR','IF','NO','SO','BY','AS','AT','WE','BE']:
        score += t.count(w) * 2
    for w in ['THAT','THIS','WITH','FROM','THEY','HAVE','BEEN','EACH','WILL',
              'YOUR','WHAT','WHEN','THEM','SOME','INTO','THAN','ONLY','SELF',
              'FIND','MAKE','JUST','KNOW','TRUTH','SACRED','WISDOM','WITHIN',
              'PRIME','BEING','WORLD','NEVER','EVERY','THERE','ABOUT','WHICH']:
        score += t.count(w) * 5
    return score

def primes_up_to(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i): sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

PRIMES = primes_up_to(100000)

# ===== MAGIC SQUARE KEYS =====
# P63 magic square:
P63_GRID = [
    [272, 138, 341, 131, 151],
    [366, 199, 130, 320,  18],
    [226, 245,  91, 245, 226],
    [ 18, 320, 130, 199, 366],
    [151, 131, 341, 138, 272]
]
# P16 magic square (constant = 3301!):
P16_GRID = [
    [434, 1311, 312, 278, 966],
    [204,  812, 934, 280, 1071],
    [626,  620, 809, 620, 626],
    [1071, 280, 934, 812, 204],
    [966,  278, 312, 1311, 434]
]

# Extract various key sequences from magic squares
def flatten_grid(grid):
    return [v for row in grid for v in row]

def grid_to_key_mod29(grid):
    return [v % 29 for v in flatten_grid(grid)]

def grid_rows_mod29(grid):
    return [[v % 29 for v in row] for row in grid]

def grid_cols_mod29(grid):
    rows = len(grid)
    cols = len(grid[0])
    return [[grid[r][c] % 29 for r in range(rows)] for c in range(cols)]

# ===== KEY GENERATION FUNCTIONS =====
def key_prime_direct(n):
    """Primes mod 29"""
    return [p % 29 for p in PRIMES[:n]]

def key_prime_euler(n, offset=0):
    """Euler totient of primes mod 29 = (p-1) % 29"""
    return [(PRIMES[i+offset] - 1) % 29 for i in range(n)]

def key_fibonacci(n):
    """Fibonacci sequence mod 29"""
    fib = [1, 1]
    while len(fib) < n:
        fib.append((fib[-1] + fib[-2]) % 29)
    return fib[:n]

def key_lucas(n):
    """Lucas sequence mod 29"""
    luc = [2, 1]
    while len(luc) < n:
        luc.append((luc[-1] + luc[-2]) % 29)
    return luc[:n]

def key_prime_gaps(n, offset=0):
    """Gaps between consecutive primes mod 29"""
    return [(PRIMES[i+1+offset] - PRIMES[i+offset]) % 29 for i in range(n)]

def key_prime_squared(n, offset=0):
    """Prime squared mod 29"""
    return [(PRIMES[i+offset]**2) % 29 for i in range(n)]

def key_prime_factorial_residue(n):
    """n! mod 29 (Wilson's theorem variant)"""
    vals = []; f = 1
    for i in range(1, n+1):
        f = (f * i) % 29
        vals.append(f)
    return vals

# ===== DECRYPT FUNCTIONS =====
def vigenere_sub(cipher, key):
    kl = len(key)
    return [(cipher[i] - key[i % kl]) % 29 for i in range(len(cipher))]

def vigenere_add(cipher, key):
    kl = len(key)
    return [(cipher[i] + key[i % kl]) % 29 for i in range(len(cipher))]

def vigenere_beau(cipher, key):
    kl = len(key)
    return [(key[i % kl] - cipher[i]) % 29 for i in range(len(cipher))]

def multiplicative_decrypt(cipher, k):
    """c = p * k mod 29 → p = c * k_inv mod 29"""
    k_inv = pow(k, -1, 29)  # modular inverse
    return [(c * k_inv) % 29 for c in cipher]

def affine_decrypt(cipher, a, b):
    """c = a*p + b mod 29 → p = a_inv * (c - b) mod 29"""
    a_inv = pow(a, -1, 29)
    return [(a_inv * (c - b)) % 29 for c in cipher]

# ===== MAIN ATTACK =====
print("=" * 80)
print("CREATIVE KEY DERIVATION ATTACK")
print("=" * 80)

# Focus pages
focus_pages = [20, 22, 42, 17, 19, 21, 23, 25, 32, 40, 44, 50]
pages = {pn: load_page(pn) for pn in focus_pages}

# Test all key types on all focus pages
key_generators = {
    'P63_flat': grid_to_key_mod29(P63_GRID),
    'P16_flat': grid_to_key_mod29(P16_GRID),
    'P63_row1': grid_rows_mod29(P63_GRID)[0],
    'P63_row2': grid_rows_mod29(P63_GRID)[1],
    'P63_row3': grid_rows_mod29(P63_GRID)[2],
    'P63_col1': grid_cols_mod29(P63_GRID)[0],
    'P63_col2': grid_cols_mod29(P63_GRID)[1],
    'P63_diag': [P63_GRID[i][i] % 29 for i in range(5)],
    'P16_row1': grid_rows_mod29(P16_GRID)[0],
    'P16_row2': grid_rows_mod29(P16_GRID)[1],  # Contains 812!
    'P16_row3': grid_rows_mod29(P16_GRID)[2],
    'P16_col1': grid_cols_mod29(P16_GRID)[0],
    'P16_diag': [P16_GRID[i][i] % 29 for i in range(5)],
    'fibonacci': key_fibonacci(50),
    'lucas': key_lucas(50),
    'prime_direct': key_prime_direct(100),
    'prime_gaps': key_prime_gaps(100),
    'prime_squared': key_prime_squared(100),
}

print("\n--- Key sequences ---")
for name, key in key_generators.items():
    print(f"  {name}: {key[:15]}...")

print(f"\n{'='*80}")
print(f"SECTION 1: Vigenère with creative keys")
print(f"{'='*80}")

for pn in focus_pages:
    d = pages[pn]
    if not d: continue
    
    best_ic = 0
    best_info = None
    
    for kname, key in key_generators.items():
        if not key: continue
        for mode_name, decrypt_fn in [('SUB', vigenere_sub), ('ADD', vigenere_add), ('BEAU', vigenere_beau)]:
            dec = decrypt_fn(d, key)
            ic = ioc29(dec)
            sc = score_english(dec)
            if ic > best_ic:
                best_ic = ic
                best_info = (kname, mode_name, ic, sc, text(dec)[:100])
    
    if best_info:
        kname, mode, ic, sc, t = best_info
        print(f"  P{pn:02d}: IoC={ic:.4f} score={sc} key={kname} mode={mode}")
        print(f"    {t[:100]}")

# ===== SECTION 2: TOTIENT WITH VERY WIDE OFFSET RANGE =====
print(f"\n{'='*80}")
print(f"SECTION 2: Totient φ(prime) with WIDE offsets (0-2000) on P20")
print(f"{'='*80}")

d20 = pages[20]
best_results = []
for offset in range(0, 2000):
    if offset + len(d20) >= len(PRIMES): break
    for mode in ['SUB', 'ADD', 'BEAU']:
        key = [(PRIMES[i+offset] - 1) % 29 for i in range(len(d20))]
        if mode == 'SUB': dec = [(d20[i] - key[i]) % 29 for i in range(len(d20))]
        elif mode == 'ADD': dec = [(d20[i] + key[i]) % 29 for i in range(len(d20))]
        else: dec = [(key[i] - d20[i]) % 29 for i in range(len(d20))]
        ic = ioc29(dec)
        if ic > 1.15:
            best_results.append((ic, offset, mode, text(dec)[:80]))

best_results.sort(reverse=True)
for ic, off, mode, t in best_results[:10]:
    print(f"  offset={off} {mode}: IoC={ic:.4f} -- {t}")

# ===== SECTION 3: PRIME DIRECT (p mod 29, not p-1 mod 29) =====
print(f"\n{'='*80}")
print(f"SECTION 3: Prime direct (p mod 29) with wide offsets on P20")
print(f"{'='*80}")

best_results = []
for offset in range(0, 2000):
    if offset + len(d20) >= len(PRIMES): break
    for mode in ['SUB', 'ADD', 'BEAU']:
        key = [PRIMES[i+offset] % 29 for i in range(len(d20))]
        if mode == 'SUB': dec = [(d20[i] - key[i]) % 29 for i in range(len(d20))]
        elif mode == 'ADD': dec = [(d20[i] + key[i]) % 29 for i in range(len(d20))]
        else: dec = [(key[i] - d20[i]) % 29 for i in range(len(d20))]
        ic = ioc29(dec)
        if ic > 1.15:
            best_results.append((ic, offset, mode, text(dec)[:80]))

best_results.sort(reverse=True)
for ic, off, mode, t in best_results[:10]:
    print(f"  offset={off} {mode}: IoC={ic:.4f} -- {t}")

# ===== SECTION 4: MULTIPLICATIVE CIPHER =====
print(f"\n{'='*80}")
print(f"SECTION 4: Multiplicative/Affine cipher on all focus pages")
print(f"{'='*80}")

for pn in focus_pages:
    d = pages[pn]
    if not d: continue
    
    best_ic = 0
    best = None
    
    for a in range(1, 29):
        if gcd(a, 29) != 1: continue  # a must be coprime with 29
        for b in range(29):
            dec = affine_decrypt(d, a, b)
            ic = ioc29(dec)
            if ic > best_ic:
                best_ic = ic
                best = (a, b, ic, text(dec)[:80])
    
    if best and best_ic > 1.15:
        a, b, ic, t = best
        print(f"  P{pn:02d}: a={a} b={b} IoC={ic:.4f} -- {t}")

# ===== SECTION 5: AUTOKEY WITH PRIME SEED =====
print(f"\n{'='*80}")
print(f"SECTION 5: Autokey with prime-based seeds on P20, P17")
print(f"{'='*80}")

for pn in [20, 17, 22]:
    d = pages[pn]
    if not d: continue
    
    best_ic = 0
    best = None
    
    # Try prime sequences as initial seeds of various lengths
    for seed_len in [5, 8, 10, 13, 15, 20, 29]:
        for seed_offset in range(0, 100, 5):
            seed = [(PRIMES[i+seed_offset] - 1) % 29 for i in range(seed_len)]
            
            for mode in ['SUB', 'ADD']:
                # Autokey: key = seed + plaintext
                key = list(seed)
                result = []
                for i, c in enumerate(d):
                    if i < len(key):
                        k = key[i]
                    else:
                        break
                    if mode == 'SUB': p = (c - k) % 29
                    else: p = (c + k) % 29
                    result.append(p)
                    key.append(p)
                
                ic = ioc29(result)
                sc = score_english(result)
                if ic > best_ic:
                    best_ic = ic
                    best = (seed_len, seed_offset, mode, ic, sc, text(result)[:80])
    
    if best and best_ic > 1.15:
        sl, so, mode, ic, sc, t = best
        print(f"  P{pn:02d}: seed_len={sl} offset={so} {mode}: IoC={ic:.4f} score={sc}")
        print(f"    {t}")

# ===== SECTION 6: COMBINED CROSS-PAGE KEY =====
print(f"\n{'='*80}")
print(f"SECTION 6: Using solved page plaintext as running key (CORRECT GP mapping)")
print(f"{'='*80}")

# Solved plaintext in GP values
SOLVED_TEXT = "WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONEALONGTHEWAYYOUWILLFINDANENDTOALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURILLUSIONSYOURCERTAINTYANDYOURREALITYULTIMATELYYOUWILLDISCOVERANENDTOSELFITISTHROUGHTHISPILGRIMAGETHATWESHAPEOURSELVESANDOURREALITIESJOURNEYDEEPWITHINANDYOUWILLARRIVEOUTSIDELIKETHEINSTARITISONLY"

def keyword_to_gp(word):
    result = []; i = 0; word = word.upper()
    while i < len(word):
        if i+1 < len(word):
            di = word[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap: result.append(dmap[di]); i += 2; continue
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if word[i] in smap: result.append(smap[word[i]])
        i += 1
    return result

solved_key = keyword_to_gp(SOLVED_TEXT)
print(f"Solved plaintext key length: {len(solved_key)}")

for pn in [20, 17, 21, 22, 23, 32, 40]:
    d = pages[pn]
    if not d: continue
    
    best_ic = 0
    best = None
    
    for start_off in range(0, len(solved_key) - 50, 1):
        key_segment = solved_key[start_off:start_off + len(d)]
        if len(key_segment) < len(d): 
            key_segment = key_segment * (len(d) // len(key_segment) + 1)
            key_segment = key_segment[:len(d)]
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            if mode == 'SUB': dec = [(d[i] - key_segment[i]) % 29 for i in range(len(d))]
            elif mode == 'ADD': dec = [(d[i] + key_segment[i]) % 29 for i in range(len(d))]
            else: dec = [(key_segment[i] - d[i]) % 29 for i in range(len(d))]
            
            ic = ioc29(dec)
            sc = score_english(dec)
            if ic > best_ic:
                best_ic = ic
                best = (start_off, mode, ic, sc, text(dec)[:80])
    
    if best and best_ic > 1.15:
        off, mode, ic, sc, t = best
        print(f"  P{pn:02d}: offset={off} {mode}: IoC={ic:.4f} score={sc}")
        print(f"    {t}")
    elif best:
        off, mode, ic, sc, t = best
        print(f"  P{pn:02d}: best IoC={ic:.4f} (below threshold)")

print(f"\n{'='*80}")
print("ATTACK COMPLETE")
print("=" * 80)
