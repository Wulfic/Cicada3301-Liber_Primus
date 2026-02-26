#!/usr/bin/env python3
"""
P19 Key Verification and Cross-Page Application

P19 SOLUTION.md claims:
- Mode: ADD (P = (C + K) % 29)
- Key length: 47 (prime!)  
- No digraphs in plaintext conversion
- First 43 key values confirmed

This script:
1. Verifies the P19 key by fully decrypting P19
2. Determines the remaining 4 key values (indices 43-46)
3. Tests this key on ALL other unsolved pages
4. Tests the LFSR hypothesis on the key
"""

import os, sys, io, re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# CORRECT GP mapping
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11  # ᛄ alias for J

# Single-letter mapping (no digraphs) - each English letter to GP index
SINGLE_LETTER = {'F':0,'U':1,'V':1,'TH':2,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,
                 'N':9,'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,
                 'L':20,'D':23,'A':24,'Y':26,'Q':5,'Z':15}

GP_LETTERS_SINGLE = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_runes(page_num):
    """Load cipher rune indices for a page"""
    rpath = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(rpath):
        return None, None
    with open(rpath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    rune_indices = []
    for ch in text:
        if ch in GP_RUNE_TO_IDX:
            rune_indices.append(GP_RUNE_TO_IDX[ch])
    
    return text, rune_indices

def calc_ioc(indices):
    if len(indices) < 20:
        return 0
    freq = defaultdict(int)
    for v in indices:
        freq[v] += 1
    n = len(indices)
    ioc = sum(f*(f-1) for f in freq.values()) / (n*(n-1)) if n > 1 else 0
    return ioc * 29

def decrypt_add(cipher, key):
    """Decrypt using ADD: P = (C + K) % 29"""
    n = len(cipher)
    klen = len(key)
    return [(cipher[i] + key[i % klen]) % 29 for i in range(n)]

def decrypt_sub(cipher, key):
    """Decrypt using SUB: P = (C - K) % 29"""
    n = len(cipher)
    klen = len(key)
    return [(cipher[i] - key[i % klen]) % 29 for i in range(n)]

def decrypt_beaufort(cipher, key):
    """Decrypt using BEAUFORT: P = (K - C) % 29"""
    n = len(cipher)
    klen = len(key)
    return [(key[i % klen] - cipher[i]) % 29 for i in range(n)]

def indices_to_text(indices):
    """Convert GP indices to text using single-letter mapping"""
    return ''.join(GP_LETTERS_SINGLE[v] for v in indices)

# P19 confirmed key (first 43 values from SOLUTION.md)
P19_KEY_PARTIAL = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

print("=" * 80)
print("PHASE 1: P19 Full Decryption & Key Recovery")
print("=" * 80)

p19_text, p19_cipher = load_runes(19)
if p19_cipher:
    n = len(p19_cipher)
    print(f"P19 cipher length: {n} runes")
    
    # Decrypt first 43 positions with known key
    plain_first43 = [(p19_cipher[i] + P19_KEY_PARTIAL[i]) % 29 for i in range(43)]
    text_first43 = indices_to_text(plain_first43)
    print(f"First 43 runes decrypted: {text_first43}")
    
    # If key length is 47, positions 47..89 should also decrypt correctly with key[0..42]
    if n >= 90:
        plain_47_89 = [(p19_cipher[47+i] + P19_KEY_PARTIAL[i]) % 29 for i in range(43)]
        text_47_89 = indices_to_text(plain_47_89)
        print(f"Positions 47-89 with same key: {text_47_89}")
        
        # Check if this is English
        words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','YOUR','WHAT',
                 'THERE','THEIR','BEEN','SOME','WERE','WHICH','WHEN','THEM','NOT','FOR',
                 'BUT','ARE','ALL','CAN','YOU','ONE','HIS','HER','WAS','OUR']
        wscore = sum(text_47_89.count(w) * len(w)**2 for w in words)
        print(f"  Word score: {wscore}")
    
    # Try to find key[43..46] by brute force
    print("\nBrute forcing key positions 43-46...")
    best_score = 0
    best_remaining = None
    
    for k43 in range(29):
        for k44 in range(29):
            for k45 in range(29):
                for k46 in range(29):
                    full_key = P19_KEY_PARTIAL + [k43, k44, k45, k46]
                    plain = decrypt_add(p19_cipher, full_key)
                    text = indices_to_text(plain)
                    
                    # Score based on English word frequency
                    words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL',
                             'NOT','FOR','BUT','ARE','ALL','CAN','YOU','ONE','WAS','OUR',
                             'HIS','HER','WHO','ITS','HAD','HAS','BEEN','EACH','MAKE',
                             'LIKE','INTO','TIME','VERY','WHEN','COME','COULD','MORE',
                             'THAN','WOULD','OTHER','ABOUT','THEIR','WHICH']
                    wscore = sum(text.count(w) * len(w)**2 for w in words)
                    ioc = calc_ioc(plain)
                    score = wscore + ioc * 10
                    
                    if score > best_score:
                        best_score = score
                        best_remaining = [k43, k44, k45, k46]
                        best_text = text
                        best_ioc = ioc
    
    full_key = P19_KEY_PARTIAL + best_remaining
    print(f"\nBest key[43-46]: {best_remaining}")
    print(f"Full key (47): {full_key}")
    print(f"Full key as letters: {''.join(GP_LETTERS_SINGLE[v] for v in full_key)}")
    print(f"IoC: {best_ioc:.4f}")
    print(f"Best score: {best_score:.1f}")
    print(f"Full plaintext: {best_text}")
    
    # Insert word boundaries
    p19_markup = p19_text
    rune_pos = 0
    plain_with_spaces = []
    for ch in p19_text:
        if ch in GP_RUNE_TO_IDX:
            plain_with_spaces.append(GP_LETTERS_SINGLE[decrypt_add([GP_RUNE_TO_IDX[ch]], [full_key[rune_pos % 47]])[0]])
            rune_pos += 1
        elif ch == '-':
            plain_with_spaces.append(' ')
        elif ch == '.':
            plain_with_spaces.append('.')
        elif ch == '\n':
            plain_with_spaces.append('\n')
    
    readable = ''.join(plain_with_spaces)
    print(f"\nWith word boundaries:")
    print(readable)

# Phase 2: Test P19 key (length 47) on other pages
print("\n" + "=" * 80)
print("PHASE 2: P19 key applied to other unsolved pages")
print("=" * 80)

for page in range(18, 55):
    if page == 19:
        continue
    text, cipher = load_runes(page)
    if cipher is None:
        continue
    
    n = len(cipher)
    
    for mode_name, decrypt_fn in [('add', decrypt_add), ('sub', decrypt_sub), ('beaufort', decrypt_beaufort)]:
        plain = decrypt_fn(cipher, full_key)
        ioc = calc_ioc(plain)
        decoded = indices_to_text(plain)
        
        words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','NOT','FOR',
                 'BUT','ARE','ALL','CAN','YOU','ONE','WAS','OUR','HIS','HER']
        wscore = sum(decoded.count(w) * len(w)**2 for w in words)
        
        if ioc > 1.3 or wscore > 30:
            # Also show with word boundaries
            rune_pos = 0
            plain_ws = []
            for ch in text:
                if ch in GP_RUNE_TO_IDX:
                    plain_ws.append(GP_LETTERS_SINGLE[plain[rune_pos]])
                    rune_pos += 1
                elif ch == '-':
                    plain_ws.append(' ')
                elif ch == '.':
                    plain_ws.append('.')
            readable = ''.join(plain_ws)
            
            print(f"\n  P{page:02d} {mode_name}: IoC={ioc:.2f}, wscore={wscore}")
            print(f"    Text: {readable[:120]}")

# Phase 3: LFSR analysis of the P19 key
print("\n" + "=" * 80)
print("PHASE 3: LFSR analysis of P19 key")
print("=" * 80)

key = full_key

# Try to find LFSR of degree d that generates this key
# For LFSR of degree d: k[i] = sum(a[j] * k[i-j], j=1..d) mod 29
# We need to solve a linear system over GF(29)

def mod_inverse(a, m):
    """Extended GCD to find modular inverse"""
    if a == 0:
        return None
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def solve_linear_system_mod(A, b, mod):
    """Solve Ax = b mod m using Gaussian elimination"""
    n = len(A)
    m = len(A[0])
    # Augmented matrix
    aug = [row[:] + [b[i]] for i, row in enumerate(A)]
    
    pivot_cols = []
    row = 0
    for col in range(m):
        # Find pivot
        found = False
        for r in range(row, n):
            if aug[r][col] % mod != 0:
                aug[row], aug[r] = aug[r], aug[row]
                found = True
                break
        if not found:
            continue
        
        pivot_cols.append(col)
        inv = mod_inverse(aug[row][col], mod)
        if inv is None:
            continue
        
        # Scale row
        for j in range(len(aug[row])):
            aug[row][j] = (aug[row][j] * inv) % mod
        
        # Eliminate
        for r in range(n):
            if r != row and aug[r][col] % mod != 0:
                factor = aug[r][col]
                for j in range(len(aug[r])):
                    aug[r][j] = (aug[r][j] - factor * aug[row][j]) % mod
        
        row += 1
    
    # Extract solution
    if row < m:
        return None  # Underdetermined
    
    solution = [0] * m
    for i, col in enumerate(pivot_cols):
        if i < len(aug):
            solution[col] = aug[i][-1] % mod
    
    return solution

for d in range(1, 24):
    # Build system: for i = d, d+1, ..., 46
    # k[i] = a[1]*k[i-1] + a[2]*k[i-2] + ... + a[d]*k[i-d] (mod 29)
    n_eqs = 47 - d
    if n_eqs < d:
        break
    
    A = []
    b = []
    for i in range(d, 47):
        row = [key[i-j-1] for j in range(d)]
        A.append(row)
        b.append(key[i])
    
    # Use first d equations to solve, then verify with remaining
    A_solve = A[:d]
    b_solve = b[:d]
    
    coeffs = solve_linear_system_mod(A_solve, b_solve, 29)
    
    if coeffs is not None:
        # Verify with ALL equations
        all_match = True
        for i in range(len(A)):
            predicted = sum(coeffs[j] * A[i][j] for j in range(d)) % 29
            if predicted != b[i]:
                all_match = False
                break
        
        if all_match:
            print(f"  LFSR degree {d} FITS! Coefficients: {coeffs}")
            # Generate more keystream to verify
            extended = key[:]
            for _ in range(100):
                next_val = sum(coeffs[j] * extended[-(j+1)] for j in range(d)) % 29
                extended.append(next_val)
            print(f"    Extended key (first 60): {extended[:60]}")
            print(f"    Extended as text: {''.join(GP_LETTERS_SINGLE[v] for v in extended[:60])}")
            break

# Phase 4: Mathematical sequences in the key
print("\n" + "=" * 80)
print("PHASE 4: Mathematical sequences in P19 key")
print("=" * 80)

# Check if key[i] follows any pattern involving primes
primes_list = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

print(f"Key: {key}")
print(f"Key as text: {''.join(GP_LETTERS_SINGLE[v] for v in key)}")

# Check each position against GP primes
for i, k in enumerate(key):
    gp_prime = primes_list[k] if k < len(primes_list) else '?'
    print(f"  [{i:2d}] key={k:2d} ({GP_LETTERS_SINGLE[k]:>2s}) prime={gp_prime}")

# Check differences
diffs = [(key[i+1] - key[i]) % 29 for i in range(len(key)-1)]
print(f"\nKey differences mod 29: {diffs}")

# Check second differences
diffs2 = [(diffs[i+1] - diffs[i]) % 29 for i in range(len(diffs)-1)]
print(f"Second differences: {diffs2}")

# Check if key is a permutation cycle
# What values repeat?
from collections import Counter
counts = Counter(key)
print(f"\nKey value frequencies: {sorted(counts.items())}")
print(f"Distinct values: {len(counts)} out of 29")

# Phase 5: If LFSR works, apply to ALL pages
print("\n" + "=" * 80)
print("PHASE 5: Extended LFSR keystream on all pages")
print("=" * 80)

# Check if an LFSR was found
if 'extended' in dir():
    # The LFSR extends the key beyond 47. Test on other pages with offset alignment
    for page in range(18, 55):
        if page == 19:
            continue
        text, cipher = load_runes(page)
        if cipher is None:
            continue
        n = len(cipher)
        
        for mode_name, decrypt_fn in [('add', decrypt_add), ('sub', decrypt_sub), ('beaufort', decrypt_beaufort)]:
            # Try different starting offsets in the extended keystream
            for offset in range(min(50, len(extended) - n)):
                key_slice = extended[offset:offset+n]
                if len(key_slice) < n:
                    break
                plain = decrypt_fn(cipher, key_slice)
                ioc = calc_ioc(plain)
                
                if ioc > 1.4:
                    decoded = indices_to_text(plain)
                    words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','NOT','FOR']
                    wscore = sum(decoded.count(w) * len(w)**2 for w in words)
                    if wscore > 20:
                        print(f"  P{page:02d} {mode_name} offset={offset}: IoC={ioc:.2f}, wscore={wscore}")
                        print(f"    Text: {decoded[:100]}")
else:
    # If no LFSR found, note that
    print("  No LFSR was found. Key appears truly aperiodic within 47 positions.")
    print("  Testing the 47-length key as Vigenere on other pages (Phase 2 covered this).")

print("\n\nDONE.")
