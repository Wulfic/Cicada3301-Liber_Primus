#!/usr/bin/env python3
"""
Single-Rune Word Keystream Recovery Attack

Community research established:
- Spaces ('-') and periods ('.') are NOT encrypted
- Single-rune words MUST decrypt to 'I' (index 10) or 'A' (index 24)
- This gives us known plaintext at specific positions
- We can recover keystream values at those positions
- Then test if the keystream matches any known sequence (primes, totient, LFSR)

Also tests:
- Cross-page keystream continuity (does the prime sequence continue across pages?)
- LFSR polynomial fitting from recovered keystream bits
"""

import os, sys, io, re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# CORRECT GP mapping
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11  # ᛄ alias for J
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def sieve_primes(n):
    """Generate primes up to n"""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

PRIMES = sieve_primes(100000)

def load_runes(page_num):
    """Load runes for a page, return (full_text, rune_only_indices, rune_values)"""
    rpath = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(rpath):
        return None, None, None
    with open(rpath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    rune_positions = []  # (position_in_text, rune_char, gp_index)
    for i, ch in enumerate(text):
        if ch in GP_RUNE_TO_IDX:
            rune_positions.append((i, ch, GP_RUNE_TO_IDX[ch]))
    
    return text, rune_positions

def find_single_rune_words(text, rune_positions):
    """Find single-rune words and their rune-stream position"""
    # Parse word boundaries
    results = []
    # Split text into tokens by '-' (space) and '.' (period)
    i = 0
    rune_counter = 0
    current_word_runes = []
    current_word_start_rune_pos = 0
    
    for pos, ch in enumerate(text):
        if ch in GP_RUNE_TO_IDX:
            if not current_word_runes:
                current_word_start_rune_pos = rune_counter
            current_word_runes.append((rune_counter, ch, GP_RUNE_TO_IDX[ch]))
            rune_counter += 1
        elif ch in '-.\n\r ':
            if len(current_word_runes) == 1:
                rc, rch, ridx = current_word_runes[0]
                results.append({
                    'rune_stream_pos': rc,
                    'char': rch,
                    'gp_index': ridx,
                    'gp_letter': GP_LETTERS[ridx]
                })
            current_word_runes = []
        # Numbers, &, etc. - treat as non-rune characters in words
        elif ch.isdigit() or ch == '&':
            current_word_runes = []  # reset, these aren't pure rune words
            rune_counter_skip = True  # don't count
    
    # Check last word
    if len(current_word_runes) == 1:
        rc, rch, ridx = current_word_runes[0]
        results.append({
            'rune_stream_pos': rc,
            'char': rch,
            'gp_index': ridx,
            'gp_letter': GP_LETTERS[ridx]
        })
    
    return results

def recover_keystream_at_position(cipher_idx, plaintext_idx, mode):
    """Given cipher index and plaintext index, recover keystream value"""
    if mode == 'sub':
        # plain = (cipher - key) % 29 => key = (cipher - plain) % 29
        return (cipher_idx - plaintext_idx) % 29
    elif mode == 'add':
        # plain = (cipher + key) % 29 => key = (plain - cipher) % 29
        return (plaintext_idx - cipher_idx) % 29
    elif mode == 'beaufort':
        # plain = (key - cipher) % 29 => key = (plain + cipher) % 29
        return (plaintext_idx + cipher_idx) % 29

print("=" * 80)
print("SINGLE-RUNE WORD KEYSTREAM RECOVERY")
print("=" * 80)

# Phase 1: Collect all single-rune word positions across all pages
all_page_data = {}
total_rune_offset = 0  # Cumulative rune count (for cross-page continuity test)

for page in range(18, 55):
    text, rune_positions = load_runes(page)
    if text is None:
        continue
    
    singles = find_single_rune_words(text, rune_positions)
    if singles:
        all_page_data[page] = {
            'singles': singles,
            'n_runes': len(rune_positions),
            'cumulative_start': total_rune_offset,
            'text': text
        }
    total_rune_offset += len(rune_positions) if rune_positions else 0

print(f"\nPages with single-rune words: {len(all_page_data)}")
print(f"Total rune stream length (pages 18-54): {total_rune_offset}")

# Phase 2: For each page, show possible keystream values
print("\n" + "=" * 80)
print("PHASE 2: Keystream values at single-rune word positions")
print("=" * 80)

for page in sorted(all_page_data.keys()):
    data = all_page_data[page]
    print(f"\n--- Page {page} ({data['n_runes']} runes, cumulative offset {data['cumulative_start']}) ---")
    for s in data['singles']:
        pos = s['rune_stream_pos']
        ci = s['gp_index']
        global_pos = data['cumulative_start'] + pos
        
        # Calculate keystream for both I(10) and A(24) in all modes
        print(f"  Pos {pos} (global {global_pos}): cipher={s['gp_letter']}({ci})")
        for mode in ['sub', 'add', 'beaufort']:
            ki = recover_keystream_at_position(ci, 10, mode)  # plaintext = I
            ka = recover_keystream_at_position(ci, 24, mode)  # plaintext = A
            
            # Check if either matches totient of consecutive primes
            for start_offset in range(500):
                prime_idx = start_offset + pos
                if prime_idx < len(PRIMES):
                    tot_val = (PRIMES[prime_idx] - 1) % 29
                    if tot_val == ki:
                        print(f"    {mode}/I: key={ki} MATCHES totient(prime[{prime_idx}]={PRIMES[prime_idx]}) start={start_offset}")
                    if tot_val == ka:
                        print(f"    {mode}/A: key={ka} MATCHES totient(prime[{prime_idx}]={PRIMES[prime_idx]}) start={start_offset}")

# Phase 3: Cross-page totient consistency check
print("\n" + "=" * 80)
print("PHASE 3: Cross-page totient consistency check")
print("=" * 80)
print("Testing if primes continue sequentially across pages...")

for mode in ['sub', 'add', 'beaufort']:
    for pt_val, pt_name in [(10, 'I'), (24, 'A')]:
        # For each possible global starting offset
        for start_offset in range(2000):
            all_match = True
            matches = 0
            total_checks = 0
            
            for page in sorted(all_page_data.keys()):
                data = all_page_data[page]
                for s in data['singles']:
                    pos = s['rune_stream_pos']
                    ci = s['gp_index']
                    global_pos = data['cumulative_start'] + pos
                    
                    key_needed = recover_keystream_at_position(ci, pt_val, mode)
                    prime_idx = start_offset + global_pos
                    
                    if prime_idx >= len(PRIMES):
                        all_match = False
                        break
                    
                    tot_val = (PRIMES[prime_idx] - 1) % 29
                    total_checks += 1
                    if tot_val == key_needed:
                        matches += 1
                    else:
                        all_match = False
                
                if not all_match:
                    break
            
            if total_checks > 5 and matches == total_checks:
                print(f"  PERFECT MATCH: {mode}/plain={pt_name}, global_start={start_offset}, {matches}/{total_checks} positions match!")
            elif total_checks > 5 and matches > total_checks * 0.7:
                print(f"  Partial match: {mode}/plain={pt_name}, global_start={start_offset}, {matches}/{total_checks} positions")

# Phase 4: Test if keystream is per-PAGE prime sequence (not global)
print("\n" + "=" * 80)
print("PHASE 4: Per-page totient test (prime sequence restarts each page)")
print("=" * 80)

for mode in ['sub', 'add', 'beaufort']:
    for pt_val, pt_name in [(10, 'I'), (24, 'A')]:
        for page in sorted(all_page_data.keys()):
            data = all_page_data[page]
            if len(data['singles']) < 2:
                continue
            
            for start_offset in range(500):
                all_match = True
                for s in data['singles']:
                    pos = s['rune_stream_pos']
                    ci = s['gp_index']
                    key_needed = recover_keystream_at_position(ci, pt_val, mode)
                    prime_idx = start_offset + pos
                    if prime_idx >= len(PRIMES):
                        all_match = False
                        break
                    tot_val = (PRIMES[prime_idx] - 1) % 29
                    if tot_val != key_needed:
                        all_match = False
                        break
                
                if all_match:
                    print(f"  P{page} {mode}/plain={pt_name}: start={start_offset} — all {len(data['singles'])} positions match!")

# Phase 5: Test mixed I/A assignments
print("\n" + "=" * 80)
print("PHASE 5: Mixed I/A assignments with per-page totient")
print("=" * 80)
print("Each single-rune word could be I or A — test all combinations")

from itertools import product

for mode in ['sub', 'add', 'beaufort']:
    for page in sorted(all_page_data.keys()):
        data = all_page_data[page]
        n_singles = len(data['singles'])
        if n_singles < 2 or n_singles > 8:
            continue
        
        best_start = None
        best_combo = None
        
        for combo in product([10, 24], repeat=n_singles):
            for start_offset in range(500):
                all_match = True
                for idx, s in enumerate(data['singles']):
                    pos = s['rune_stream_pos']
                    ci = s['gp_index']
                    pt_val = combo[idx]
                    key_needed = recover_keystream_at_position(ci, pt_val, mode)
                    prime_idx = start_offset + pos
                    if prime_idx >= len(PRIMES):
                        all_match = False
                        break
                    tot_val = (PRIMES[prime_idx] - 1) % 29
                    if tot_val != key_needed:
                        all_match = False
                        break
                
                if all_match:
                    ia_str = ''.join(['I' if v==10 else 'A' for v in combo])
                    if best_start is None:
                        print(f"  P{page} {mode}: combo={ia_str}, start={start_offset}")

# Phase 6: LFSR keystream test
print("\n" + "=" * 80)
print("PHASE 6: LFSR polynomial fitting")
print("=" * 80)
print("Testing if recovered keystream values fit an LFSR pattern...")

# For pages with 4+ single-rune words, try to find LFSR parameters
for mode in ['sub']:
    for page in sorted(all_page_data.keys()):
        data = all_page_data[page]
        if len(data['singles']) < 3:
            continue
        
        # Try both I and A for each position
        for combo in product([10, 24], repeat=len(data['singles'])):
            keyvals = []
            positions = []
            for idx, s in enumerate(data['singles']):
                pos = s['rune_stream_pos']
                ci = s['gp_index']
                key = recover_keystream_at_position(ci, combo[idx], mode)
                keyvals.append(key)
                positions.append(pos)
            
            # Check for linear recurrence mod 29
            # key[i] = a*key[i-1] + b mod 29
            if len(keyvals) >= 3:
                k0, k1, k2 = keyvals[0], keyvals[1], keyvals[2]
                p0, p1, p2 = positions[0], positions[1], positions[2]
                # But positions aren't consecutive, so simple LFSR won't work directly
                # We need the full keystream, not just sampled values
                pass  # Skip for now - need different approach

# Phase 7: Test Fibonacci-indexed primes
print("\n" + "=" * 80)
print("PHASE 7: Fibonacci-indexed primes as keystream")
print("=" * 80)

def fibonacci_sequence(n):
    fibs = [1, 1]
    while len(fibs) < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

FIBS = fibonacci_sequence(200)

for mode in ['sub', 'add', 'beaufort']:
    for pt_val, pt_name in [(10, 'I'), (24, 'A')]:
        for page in sorted(all_page_data.keys()):
            data = all_page_data[page]
            if len(data['singles']) < 2:
                continue
            
            for start_offset in range(100):
                all_match = True
                for s in data['singles']:
                    pos = s['rune_stream_pos']
                    fib_idx = start_offset + pos
                    if fib_idx >= len(FIBS) or FIBS[fib_idx] >= len(PRIMES):
                        all_match = False
                        break
                    prime_val = PRIMES[FIBS[fib_idx]]
                    key_val = (prime_val - 1) % 29
                    key_needed = recover_keystream_at_position(s['gp_index'], pt_val, mode)
                    if key_val != key_needed:
                        all_match = False
                        break
                
                if all_match:
                    print(f"  P{page} {mode}/plain={pt_name}: fib_start={start_offset} — all {len(data['singles'])} match!")

# Phase 8: P19 known plaintext verification
print("\n" + "=" * 80)
print("PHASE 8: P19 known plaintext — deeper key analysis")
print("=" * 80)

p19_text, p19_runes = load_runes(19)
if p19_text:
    # Known plaintext for P19 first words
    known_plain = "REARRANGING THE PRIME NUMBERS WILL SHOW A PATH TO THE DEOR"
    # Convert to GP - but need to handle multi-char runes (TH, NG, etc.)
    # Map from text to GP indices
    plain_indices = []
    i = 0
    while i < len(known_plain):
        ch = known_plain[i]
        if ch == ' ':
            i += 1
            continue
        # Try two-char match first
        if i + 1 < len(known_plain):
            digraph = known_plain[i:i+2]
            if digraph in ['TH', 'NG', 'EO', 'OE', 'AE', 'IA', 'EA']:
                idx = GP_LETTERS.index(digraph)
                plain_indices.append(idx)
                i += 2
                continue
        # Single char
        ch_upper = ch.upper()
        letter_map = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,
                      'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'D':23,'A':24,'Y':26}
        if ch_upper in letter_map:
            plain_indices.append(letter_map[ch_upper])
            i += 1
        else:
            print(f"  Unknown char: {ch}")
            i += 1
    
    # Get cipher indices
    cipher_indices = [r[2] for r in p19_runes[:len(plain_indices)]]
    
    print(f"  Known plaintext length: {len(plain_indices)} runes")
    print(f"  Cipher length: {len(cipher_indices)} runes")
    
    # Recover key for all three modes
    for mode in ['sub', 'add', 'beaufort']:
        key = []
        for ci, pi in zip(cipher_indices, plain_indices):
            k = recover_keystream_at_position(ci, pi, mode)
            key.append(k)
        
        print(f"\n  Key ({mode}): {key}")
        
        # Test against various sequences
        # 1. Sequential primes mod 29
        for start in range(2000):
            matches = sum(1 for i, k in enumerate(key) if (PRIMES[start+i]-1)%29 == k)
            if matches > len(key) * 0.5:
                print(f"    Totient match: start={start}, {matches}/{len(key)}")
        
        # 2. Primes mod 29 directly
        for start in range(2000):
            matches = sum(1 for i, k in enumerate(key) if PRIMES[start+i]%29 == k)
            if matches > len(key) * 0.5:
                print(f"    Prime mod 29 match: start={start}, {matches}/{len(key)}")
        
        # 3. Is the key itself a known sequence?
        # Check if differences are constant (linear)
        diffs = [(key[i+1] - key[i]) % 29 for i in range(len(key)-1)]
        if len(set(diffs)) == 1:
            print(f"    KEY IS ARITHMETIC PROGRESSION! diff={diffs[0]}")
        
        # Check if key values mod small numbers show pattern
        for mod in [2, 3, 5, 7, 11, 13]:
            residues = [k % mod for k in key]
            if len(set(residues)) <= 2:
                print(f"    Key mod {mod}: only {len(set(residues))} distinct values: {set(residues)}")
        
        # 4. GP primes of key values
        key_as_primes = [GP_PRIMES[k] for k in key]
        print(f"    Key as GP primes: {key_as_primes[:20]}...")
        
        # Check if key_as_primes matches a sequence
        prime_diffs = [key_as_primes[i+1] - key_as_primes[i] for i in range(len(key_as_primes)-1)]
        print(f"    Prime diffs: {prime_diffs[:20]}...")
        
        # 5. Check if key[i] = some_function(i)
        # Try key[i] = (a*i + b) % 29
        for a in range(29):
            for b in range(29):
                matches = sum(1 for i, k in enumerate(key) if (a*i + b) % 29 == k)
                if matches > len(key) * 0.6:
                    print(f"    Linear: key[i] = ({a}*i + {b}) % 29: {matches}/{len(key)} match")
        
        # Try key[i] = (a*i^2 + b*i + c) % 29
        for a in range(29):
            for b in range(29):
                for c in [key[0]]:  # Fix c = key[0]
                    matches = sum(1 for i, k in enumerate(key) if (a*i*i + b*i + c) % 29 == k)
                    if matches > len(key) * 0.6:
                        print(f"    Quadratic: ({a}*i^2 + {b}*i + {c}) % 29: {matches}/{len(key)} match")

# Phase 9: Test Emerson's Self-Reliance as running key
print("\n" + "=" * 80)
print("PHASE 9: Self-Reliance running key test")
print("=" * 80)

# Key passage from Self-Reliance
self_reliance = """A man should learn to detect and watch that gleam of light which flashes across 
his mind from within more than the lustre of the firmament of bards and sages 
yet he dismisses without notice his thought because it is his in every work of 
genius we recognize our own rejected thoughts they come back to us with a certain 
alienated majesty great works of art have no more affecting lesson for us than this 
they teach us to abide by our spontaneous impression with good humored inflexibility 
then most when the whole cry of voices is on the other side else to morrow a stranger 
will say with masterly good sense precisely what we have thought and felt all the 
time and we shall be forced to take with shame our own opinion from another"""

# Convert to GP indices
def text_to_gp_indices(text):
    indices = []
    text = text.upper()
    i = 0
    letter_map = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,
                  'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'D':23,'A':24,'Y':26,'V':1,'K':5,'Q':5,'Z':15}
    while i < len(text):
        ch = text[i]
        if ch == ' ' or ch == '\n' or ch == '\r':
            i += 1
            continue
        # Try digraphs
        if i+1 < len(text):
            di = text[i:i+2]
            if di == 'TH':
                indices.append(2)
                i += 2
                continue
            elif di == 'NG':
                indices.append(21)
                i += 2
                continue
        if ch in letter_map:
            indices.append(letter_map[ch])
        i += 1
    return indices

sr_key = text_to_gp_indices(self_reliance)
print(f"Self-Reliance key length: {len(sr_key)}")

# Test on pages with enough runes
from math import log

def calc_ioc(indices):
    if len(indices) < 20:
        return 0
    freq = defaultdict(int)
    for v in indices:
        freq[v] += 1
    n = len(indices)
    ioc = sum(f*(f-1) for f in freq.values()) / (n*(n-1)) if n > 1 else 0
    return ioc * 29  # Normalize to 29-letter alphabet

for page in range(18, 55):
    text, rune_positions = load_runes(page)
    if text is None:
        continue
    
    cipher = [r[2] for r in rune_positions]
    n = len(cipher)
    
    if n > len(sr_key):
        continue
    
    for mode in ['sub', 'add', 'beaufort']:
        for offset in range(min(50, len(sr_key) - n)):
            if mode == 'sub':
                plain = [(c - sr_key[offset + i]) % 29 for i, c in enumerate(cipher)]
            elif mode == 'add':
                plain = [(c + sr_key[offset + i]) % 29 for i, c in enumerate(cipher)]
            else:
                plain = [(sr_key[offset + i] - c) % 29 for i, c in enumerate(cipher)]
            
            ioc = calc_ioc(plain)
            if ioc > 1.4:
                # Decode
                decoded = ''.join(GP_LETTERS[v] for v in plain)
                # Count common words
                words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','YOUR','WHAT',
                         'THERE','THEIR','BEEN','SOME','WERE','WHICH','WHEN','THEM']
                wscore = sum(decoded.count(w) * len(w)**2 for w in words)
                if wscore > 20:
                    print(f"  P{page} {mode} offset={offset}: IoC={ioc:.2f}, wscore={wscore}")
                    print(f"    Text: {decoded[:100]}")

# Phase 10: Test P63 grid numbers as keystream
print("\n" + "=" * 80)
print("PHASE 10: P63 grid numbers as keystream")
print("=" * 80)

# Numbers from P63 grid
grid_numbers = [272, 138, 131, 151, 226, 245, 18, 151, 131, 138, 272]
# Various ways to use these
keystreams_to_test = {
    'grid_mod29': [n % 29 for n in grid_numbers],
    'grid_digits': [int(d) for n in grid_numbers for d in str(n)],
    'grid_primes': [PRIMES[n % len(PRIMES)] % 29 for n in grid_numbers],
    'grid_totient': [(PRIMES[n % len(PRIMES)] - 1) % 29 for n in grid_numbers],
}

# Add sequences of just the row/column patterns
keystreams_to_test['row1'] = [272 % 29, 138 % 29, 131 % 29, 151 % 29]
keystreams_to_test['row1_totient'] = [(PRIMES[272 % len(PRIMES)]-1) % 29, (PRIMES[138 % len(PRIMES)]-1) % 29, 
                                       (PRIMES[131 % len(PRIMES)]-1) % 29, (PRIMES[151 % len(PRIMES)]-1) % 29]

for name, keystream in keystreams_to_test.items():
    if len(keystream) < 2:
        continue
    
    for page in range(18, 55):
        text, rune_positions = load_runes(page)
        if text is None:
            continue
        
        cipher = [r[2] for r in rune_positions]
        n = len(cipher)
        
        # Repeat key to match cipher length
        key = (keystream * ((n // len(keystream)) + 1))[:n]
        
        for mode in ['sub', 'add', 'beaufort']:
            if mode == 'sub':
                plain = [(c - key[i]) % 29 for i, c in enumerate(cipher)]
            elif mode == 'add':
                plain = [(c + key[i]) % 29 for i, c in enumerate(cipher)]
            else:
                plain = [(key[i] - c) % 29 for i, c in enumerate(cipher)]
            
            ioc = calc_ioc(plain)
            if ioc > 1.4:
                decoded = ''.join(GP_LETTERS[v] for v in plain)
                words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','YOUR','WHAT']
                wscore = sum(decoded.count(w) * len(w)**2 for w in words)
                if wscore > 10:
                    print(f"  {name} P{page} {mode}: IoC={ioc:.2f}, wscore={wscore}")
                    print(f"    Text: {decoded[:80]}")

print("\n" + "=" * 80)
print("PHASE 11: Missing primes (73-1223) as LFSR taps")
print("=" * 80)

# The telnet had a gap from prime 71 to prime 1229
# Missing primes: 73, 79, 83, ..., 1223
missing_primes = [p for p in PRIMES if 71 < p < 1229]
print(f"Missing primes: {len(missing_primes)} primes from {missing_primes[0]} to {missing_primes[-1]}")

# Test if these missing primes mod 29 form the keystream
mp_key = [(p - 1) % 29 for p in missing_primes]

for page in range(18, 55):
    text, rune_positions = load_runes(page)
    if text is None:
        continue
    
    cipher = [r[2] for r in rune_positions]
    n = len(cipher)
    
    if n > len(mp_key):
        continue
    
    for start in range(0, min(50, len(mp_key) - n)):
        key = mp_key[start:start+n]
        
        for mode in ['sub', 'add', 'beaufort']:
            if mode == 'sub':
                plain = [(c - key[i]) % 29 for i, c in enumerate(cipher)]
            elif mode == 'add':
                plain = [(c + key[i]) % 29 for i, c in enumerate(cipher)]
            else:
                plain = [(key[i] - c) % 29 for i, c in enumerate(cipher)]
            
            ioc = calc_ioc(plain)
            if ioc > 1.3:
                decoded = ''.join(GP_LETTERS[v] for v in plain)
                words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL']
                wscore = sum(decoded.count(w) * len(w)**2 for w in words)
                print(f"  Missing primes P{page} {mode} start={start}: IoC={ioc:.2f}, wscore={wscore}")
                if wscore > 10:
                    print(f"    Text: {decoded[:100]}")

print("\n\nDONE.")
