"""
SINGLE-RUNE WORD CRIB ATTACK
Single-rune words in the ciphertext MUST decrypt to I (index 10) or A (index 24).
This gives us known key values at specific stream positions.
We can then check if these key values match any known sequence.

Also: extract full word structure for all unsolved pages.
"""
import os, re
from collections import Counter, defaultdict

RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def primes_up_to(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i): sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

PRIMES = primes_up_to(200000)

def load_raw_text(pn):
    """Load raw rune text preserving word structure."""
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return ""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Filter out note lines (P03 has an ASCII note)
    filtered = ''.join(line for line in lines if not (line.strip() and line.strip()[0].isascii() and line.strip()[0].isalpha()))
    return filtered

def parse_words(raw_text):
    """Parse rune text into words, tracking rune positions in stream.
    Returns: list of (word_rune_indices, word_stream_positions)
    """
    words = []
    current_word_indices = []
    current_word_positions = []
    stream_pos = 0
    
    for ch in raw_text:
        if ch in RUNE_TO_INDEX:
            current_word_indices.append(RUNE_TO_INDEX[ch])
            current_word_positions.append(stream_pos)
            stream_pos += 1
        elif ch in ['•', ' ', '\n', '\r', '.', ',', ':', ';', '-', '\'', '"']:
            if current_word_indices:
                words.append((list(current_word_indices), list(current_word_positions)))
                current_word_indices = []
                current_word_positions = []
    
    if current_word_indices:
        words.append((list(current_word_indices), list(current_word_positions)))
    
    return words

def get_word_lengths(words):
    """Get distribution of word lengths."""
    return Counter(len(w[0]) for w in words)

print("=" * 80)
print("SINGLE-RUNE WORD CRIB ATTACK")
print("=" * 80)

# ===== SECTION 1: WORD STRUCTURE ANALYSIS =====
print(f"\n--- SECTION 1: Word structure analysis for unsolved pages ---\n")

all_single_cribs = {}  # page -> list of (stream_pos, cipher_value)

for pn in range(17, 55):
    raw = load_raw_text(pn)
    if not raw.strip(): continue
    
    words = parse_words(raw)
    wlens = get_word_lengths(words)
    total_runes = sum(len(w[0]) for w in words)
    total_words = len(words)
    single_words = [(w, p) for w, p in words if len(w) == 1]
    
    print(f"P{pn:02d}: {total_runes} runes, {total_words} words, {len(single_words)} single-rune words")
    print(f"  Word lengths: {dict(sorted(wlens.items()))}")
    
    if single_words:
        cribs = []
        for w, positions in single_words:
            cipher_val = w[0]
            stream_pos = positions[0]
            # If plaintext = I (10): key = (cipher - 10) % 29
            key_if_I = (cipher_val - 10) % 29
            # If plaintext = A (24): key = (cipher - 24) % 29
            key_if_A = (cipher_val - 24) % 29
            cribs.append((stream_pos, cipher_val))
            print(f"  Single-rune at pos {stream_pos}: cipher={GP[cipher_val]}({cipher_val}) → key_if_I={key_if_I}, key_if_A={key_if_A}")
        
        all_single_cribs[pn] = cribs

# ===== SECTION 2: CHECK CRIBS AGAINST PRIME SEQUENCES =====
print(f"\n{'='*80}")
print("SECTION 2: Check single-rune cribs against prime-based key sequences")
print("=" * 80)

def check_cribs_vs_sequence(cribs, seq_fn, name, max_offset=2000):
    """Check if cribs match a key sequence at some offset."""
    best = (0, 0, -1, 'I')
    
    for offset in range(max_offset):
        for pt_name, pt_val in [('I', 10), ('A', 24)]:
            matches = 0
            for stream_pos, cipher_val in cribs:
                idx = offset + stream_pos
                if idx >= len(PRIMES) - 1: 
                    break
                try:
                    key_val = seq_fn(idx)
                except:
                    break
                expected_cipher = (pt_val + key_val) % 29  # c = p + k
                if expected_cipher == cipher_val:
                    matches += 1
                # Also try SUB: c = p - k → k = p - c → c = (p - k) % 29? 
                # Actually c - k = p → k = c - p → for checking: expected_c = (p + k) or (k - p) or...
                # Let's be explicit:
                # SUB: p = (c - k) % 29 → c = (p + k) % 29
                # ADD: p = (c + k) % 29 → c = (p - k) % 29
                # BEAU: p = (k - c) % 29 → c = (k - p) % 29
            
            if matches > best[0]:
                best = (matches, offset, len(cribs), pt_name)
    
    return best

# Also check ADD and BEAU modes
def check_cribs_all_modes(cribs, seq_fn, name, max_offset=2000):
    """Check cribs in all three modes."""
    results = []
    for offset in range(max_offset):
        for pt_name, pt_val in [('I', 10), ('A', 24)]:
            for mode in ['SUB', 'ADD', 'BEAU']:
                matches = 0
                for stream_pos, cipher_val in cribs:
                    idx = offset + stream_pos
                    try:
                        key_val = seq_fn(idx)
                    except:
                        break
                    
                    # cipher → plaintext relationship
                    if mode == 'SUB':  # p = (c - k) %29 → c = (p + k) %29
                        expected_c = (pt_val + key_val) % 29
                    elif mode == 'ADD':  # p = (c + k) %29 → c = (p - k) %29
                        expected_c = (pt_val - key_val) % 29
                    else:  # p = (k - c) %29 → c = (k - p) %29
                        expected_c = (key_val - pt_val) % 29
                    
                    if expected_c == cipher_val:
                        matches += 1
                
                if matches >= 2:
                    results.append((matches, offset, mode, pt_name, len(cribs)))
    
    results.sort(reverse=True)
    return results[:5]

# Key sequence generators
def seq_totient(i): return (PRIMES[i] - 1) % 29
def seq_prime_direct(i): return PRIMES[i] % 29
def seq_prime_squared(i): return (PRIMES[i]**2) % 29
def seq_prime_gap(i): return (PRIMES[i+1] - PRIMES[i]) % 29
def seq_fibonacci_mod29(i):
    a, b = 1, 1
    for _ in range(i):
        a, b = b, (a + b) % 29
    return a
# Precompute fibonacci
FIB29 = [0] * 5000
FIB29[0] = FIB29[1] = 1
for i in range(2, 5000):
    FIB29[i] = (FIB29[i-1] + FIB29[i-2]) % 29
def seq_fib(i): return FIB29[i]
def seq_prime_digit_sum(i): return sum(int(d) for d in str(PRIMES[i])) % 29

sequences = {
    'totient': seq_totient,
    'prime_direct': seq_prime_direct,
    'prime_squared': seq_prime_squared,
    'prime_gap': seq_prime_gap,
    'fibonacci': seq_fib,
    'prime_digit_sum': seq_prime_digit_sum,
}

for pn, cribs in all_single_cribs.items():
    if len(cribs) < 2: continue
    print(f"\nP{pn:02d} ({len(cribs)} cribs):")
    for sname, sfn in sequences.items():
        results = check_cribs_all_modes(cribs, sfn, sname, max_offset=500)
        if results:
            best = results[0]
            matches, offset, mode, pt, total = best
            pct = 100 * matches / total if total else 0
            print(f"  {sname}: best {matches}/{total} ({pct:.0f}%) at offset={offset} mode={mode} pt={pt}")
            if matches >= max(3, total - 1):
                print(f"    *** POTENTIAL MATCH! ***")

# ===== SECTION 3: EXHAUSTIVE 2-WAY CRIB (I vs A) =====
print(f"\n{'='*80}")
print("SECTION 3: Exhaustive crib attack — try ALL combos of I/A for single words")
print("=" * 80)

for pn, cribs in all_single_cribs.items():
    if len(cribs) < 3: continue
    n = len(cribs)
    if n > 20: 
        print(f"P{pn:02d}: {n} cribs (too many for exhaustive, sampling)")
        # Sample approach
        continue
    
    print(f"\nP{pn:02d} ({n} cribs, {2**n} combinations):")
    
    best_match = (0, '', '', 0, '')
    
    for combo in range(2**n):
        pt_vals = []
        for j in range(n):
            if combo & (1 << j):
                pt_vals.append(24)  # A
            else:
                pt_vals.append(10)  # I
        
        # For each sequence and mode, compute key values at crib positions
        for sname, sfn in sequences.items():
            for mode in ['SUB', 'ADD', 'BEAU']:
                # What key values do we need?
                needed_keys = []
                for idx, (stream_pos, cipher_val) in enumerate(cribs):
                    pv = pt_vals[idx]
                    if mode == 'SUB':  # p = (c - k) → k = (c - p)
                        k = (cipher_val - pv) % 29
                    elif mode == 'ADD':  # p = (c + k) → k = (p - c)
                        k = (pv - cipher_val) % 29
                    else:  # p = (k - c) → k = (p + c)
                        k = (pv + cipher_val) % 29
                    needed_keys.append((stream_pos, k))
                
                # Check if these key values match the sequence at some offset
                for offset in range(0, 500):
                    matches = 0
                    for pos, needed_k in needed_keys:
                        try:
                            actual_k = sfn(offset + pos)
                        except:
                            break
                        if actual_k == needed_k:
                            matches += 1
                    
                    if matches >= max(3, n - 1):
                        combo_str = ''.join('A' if (combo & (1<<j)) else 'I' for j in range(n))
                        if matches > best_match[0]:
                            best_match = (matches, sname, mode, offset, combo_str)
    
    if best_match[0] >= 3:
        matches, sname, mode, off, combo_str = best_match
        print(f"  BEST: {matches}/{n} match with {sname} mode={mode} off={off} combo={combo_str}")

# ===== SECTION 4: WORD LENGTH STATISTICS =====
print(f"\n{'='*80}")
print("SECTION 4: Word length statistics comparison (English vs ciphertext)")
print("=" * 80)

# English word length distribution (approximate)
eng_wl = {1: 3.4, 2: 17.2, 3: 20.6, 4: 19.0, 5: 14.0, 6: 10.5, 7: 7.0, 8: 4.5, 9: 2.5, 10: 1.3}
print(f"  English word lengths: {eng_wl}")

for pn in range(17, 55):
    raw = load_raw_text(pn)
    if not raw.strip(): continue
    words = parse_words(raw)
    total = len(words)
    if total < 10: continue
    wl = get_word_lengths(words)
    wl_pct = {k: round(100*v/total, 1) for k, v in sorted(wl.items())}

# ===== SECTION 5: KEY RECOVERY FROM DENSE CRIBS (P20) =====
print(f"\n{'='*80}")
print("SECTION 5: Key pattern recovery from cribs")
print("=" * 80)

# Focus on pages with most cribs
for pn, cribs in sorted(all_single_cribs.items(), key=lambda x: -len(x[1])):
    if len(cribs) < 3: continue
    print(f"\nP{pn:02d} single-rune words at positions:")
    for pos, val in cribs:
        print(f"  pos={pos}: cipher={GP[val]}({val}) → if_I: k={(val-10)%29}, if_A: k={(val-24)%29}")
    
    # Check spacing between single-rune word positions
    positions = [pos for pos, _ in cribs]
    if len(positions) >= 2:
        gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        print(f"  Gaps between single words: {gaps}")
        # Check if gaps are prime-related
        gap_primes = [g for g in gaps if g in set(PRIMES[:100])]
        print(f"  Prime gaps: {gap_primes} out of {len(gaps)} total")

print(f"\n{'='*80}")
print("CRIB ATTACK COMPLETE")
print("=" * 80)
