"""
P54 CSP Word-Based Solver
========================
Strategy: P54 has k=13 Vigenere. Word 8 spans 12 runes and covers 12 of 13 key positions.
Single-rune words W0 and W7 fix key[0] and key[10] (2 options each: A or I).
For each (W0, W7, mode) combo, try every 12-GP-rune dictionary word as W8 crib.
This determines all 13 key values. Then check all 19 words against dictionary.
"""
import sys, functools, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print = functools.partial(print, flush=True)

# ===== CORRECT GP MAPPING =====
GP_RUNES = '\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0'
GP = {}
for i, r in enumerate(GP_RUNES):
    GP[r] = i
GP['\u16C2'] = 11  # alternate J

MOD = 29

# GP index to Latin name
IDX_TO_LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def gp_to_text(vals):
    return ''.join(IDX_TO_LAT[v] for v in vals)

def eng_to_gp(word):
    """Convert English word to GP rune indices, handling digraphs."""
    result = []
    i = 0
    w = word.upper()
    while i < len(w):
        # Check digraphs first (longest match)
        matched = False
        for dg in ['TH', 'EA', 'OE', 'AE', 'NG', 'IA', 'EO']:
            if w[i:i+len(dg)] == dg:
                result.append(IDX_TO_LAT.index(dg))
                i += len(dg)
                matched = True
                break
        if not matched:
            ch = w[i]
            # Map single letters
            mapping = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,
                       'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,
                       'M':19,'L':20,'D':23,'A':24,'Y':26}
            if ch in mapping:
                result.append(mapping[ch])
                i += 1
            elif ch == 'V':  # V -> U in runes
                result.append(1)
                i += 1
            elif ch == 'K':  # K -> C
                result.append(5)
                i += 1
            elif ch == 'Q':  # Q -> C
                result.append(5)
                i += 1
            elif ch == 'Z':  # Z -> S
                result.append(15)
                i += 1
            else:
                return None  # Can't convert
    return result

# ===== LOAD CIPHER =====
# Read P54 rune file
p54_path = None
for candidate in ['pages/p54.txt', 'Pages/p54.txt', 'p54.txt']:
    if os.path.exists(candidate):
        p54_path = candidate
        break

if p54_path is None:
    # Search for it
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.lower() == 'p54.txt':
                p54_path = os.path.join(root, f)
                break
        if p54_path:
            break

if p54_path is None:
    # Use hardcoded values
    cipher = [21, 25, 19, 10, 7, 15, 17, 14, 19, 15, 12, 6, 23, 2, 25, 0, 27, 24, 17, 5, 1, 7, 4, 17, 28, 0, 14, 10, 19, 1, 5, 13, 8, 21, 20, 12, 19, 15, 23, 27, 13, 0, 17, 8, 12, 5, 12, 18, 28, 18, 10, 6, 14, 6, 15, 18, 15, 12, 2, 2, 18, 15, 2, 22, 5, 28, 10, 19, 5, 14, 23, 11, 1, 17, 18, 10]
    word_lens = [1, 4, 2, 2, 6, 6, 2, 1, 12, 6, 4, 2, 7, 7, 2, 4, 2, 3, 3]
    print("Using hardcoded P54 cipher values")
else:
    with open(p54_path, encoding='utf-8') as f:
        raw = f.read().strip()
    # Remove trailing $ or . if present
    raw = raw.rstrip('$.\n ')
    
    # Parse into words (separated by - or newline)
    tokens = []
    for line in raw.split('\n'):
        for part in line.split('-'):
            part = part.strip()
            if part:
                tokens.append(part)
    
    word_lens = []
    cipher = []
    for tok in tokens:
        word_runes = []
        for ch in tok:
            if ch in GP:
                word_runes.append(GP[ch])
        if word_runes:
            word_lens.append(len(word_runes))
            cipher.extend(word_runes)
    
    print(f"Loaded P54 from {p54_path}: {len(cipher)} runes, {len(word_lens)} words")
    print(f"Word lengths: {word_lens}")

N = len(cipher)
NW = len(word_lens)
K = 13

# ===== COMPUTE WORD POSITIONS AND KEY MAPPINGS =====
word_starts = []
pos = 0
for wl in word_lens:
    word_starts.append(pos)
    pos += wl

# For each word, which key positions does it use?
word_key_positions = []
word_cipher_vals = []
for wi in range(NW):
    start = word_starts[wi]
    length = word_lens[wi]
    keys = [(start + j) % K for j in range(length)]
    cvals = cipher[start:start + length]
    word_key_positions.append(keys)
    word_cipher_vals.append(cvals)

print(f"\nWord -> Key position mapping:")
for wi in range(NW):
    print(f"  W{wi:2d} (len={word_lens[wi]:2d}): positions {word_starts[wi]:2d}-{word_starts[wi]+word_lens[wi]-1:2d}, keys={word_key_positions[wi]}, cipher={word_cipher_vals[wi]}")

# ===== LOAD DICTIONARY AND CONVERT TO GP =====
print(f"\nLoading dictionary...")
with open('wordlist.txt') as f:
    raw_words = f.read().strip().split('\n')
print(f"Raw dictionary: {len(raw_words)} words")

# Convert to GP and group by GP-rune length
gp_dict = {}  # length -> set of tuples
gp_dict_words = {}  # length -> list of (tuple, english_word)

for word in raw_words:
    word = word.strip().lower()
    if len(word) < 1 or len(word) > 25:
        continue
    gp = eng_to_gp(word)
    if gp is None:
        continue
    gplen = len(gp)
    if gplen < 1 or gplen > 15:
        continue
    gpt = tuple(gp)
    if gplen not in gp_dict:
        gp_dict[gplen] = set()
        gp_dict_words[gplen] = []
    if gpt not in gp_dict[gplen]:
        gp_dict[gplen].add(gpt)
        gp_dict_words[gplen].append((gpt, word))

print(f"GP dictionary by length:")
for l in sorted(gp_dict.keys()):
    print(f"  Length {l:2d}: {len(gp_dict[l]):6d} unique GP words")

# ===== DEFINE CIPHER MODES =====
def decrypt_sub(c, k):
    return (c - k) % MOD

def decrypt_add(c, k):
    return (c + k) % MOD

def decrypt_beau(c, k):
    return (k - c) % MOD

MODES = [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAU', decrypt_beau)]

# ===== WORD 0 AND WORD 7 CONSTRAINTS =====
# W0: cipher[0]=21, key pos [0], 1-rune word -> A(24) or I(10)
# W7: cipher[23]=17, key pos [10], 1-rune word -> A(24) or I(10)
#
# For SUB: plain = (cipher - key) % 29 -> key = (cipher - plain) % 29
# For ADD: plain = (cipher + key) % 29 -> key = (plain - cipher) % 29
# For BEAU: plain = (key - cipher) % 29 -> key = (plain + cipher) % 29

def get_key_from_plain(cipher_val, plain_val, mode_name):
    if mode_name == 'SUB':
        return (cipher_val - plain_val) % MOD
    elif mode_name == 'ADD':
        return (plain_val - cipher_val) % MOD
    elif mode_name == 'BEAU':
        return (plain_val + cipher_val) % MOD

# ===== MAIN SOLVER =====
print(f"\n{'='*80}")
print("CSP SOLVER: Trying each 12-GP-rune word as W8 crib")
print(f"{'='*80}")

# Word 8 info
w8_start = word_starts[8]
w8_len = word_lens[8]
w8_keys = word_key_positions[8]
w8_cipher = word_cipher_vals[8]
print(f"\nW8: start={w8_start}, len={w8_len}, keys={w8_keys}, cipher={w8_cipher}")
print(f"W8 key coverage: {sorted(set(w8_keys))} ({len(set(w8_keys))} of {K} positions)")

# Get missing key position for W8
all_keys_in_w8 = set(w8_keys)
missing_keys = set(range(K)) - all_keys_in_w8
print(f"Missing key positions (not in W8): {missing_keys}")

best_results = []

total_w8_candidates = len(gp_dict.get(w8_len, []))
print(f"\nTotal {w8_len}-GP-rune dictionary words to try: {total_w8_candidates}")

for mode_name, mode_fn in MODES:
    for w0_plain_name, w0_plain in [('A', 24), ('I', 10)]:
        key0 = get_key_from_plain(cipher[0], w0_plain, mode_name)
        
        for w7_plain_name, w7_plain in [('A', 24), ('I', 10)]:
            key10 = get_key_from_plain(cipher[23], w7_plain, mode_name)
            
            combo_label = f"{mode_name} W0={w0_plain_name} W7={w7_plain_name}"
            
            # Pre-check: with key[0] and key[10], some words are partially constrained
            # key[0] sets W0, and constrains one rune in W4, W8, W9, W12, W15
            # key[10] sets W7, and constrains one rune in W4, W9, W12, W14, W18
            
            tested = 0
            for w8_gp, w8_eng in gp_dict_words.get(w8_len, []):
                # Derive key values from W8 crib
                key = [None] * K
                key[0] = key0
                key[10] = key10
                
                # W8 key positions: [11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                valid = True
                for j in range(w8_len):
                    k_pos = w8_keys[j]
                    k_val = get_key_from_plain(w8_cipher[j], w8_gp[j], mode_name)
                    
                    if key[k_pos] is not None:
                        if key[k_pos] != k_val:
                            valid = False
                            break
                    else:
                        key[k_pos] = k_val
                
                if not valid:
                    continue
                
                # Check if all key positions are filled
                if any(k is None for k in key):
                    # This shouldn't happen since W8 covers 12 and we set key[0] and key[10]
                    continue
                
                # Decrypt all runes
                plain = [mode_fn(cipher[i], key[i % K]) for i in range(N)]
                
                # Check each word against dictionary
                matches = 0
                match_details = []
                for wi in range(NW):
                    start = word_starts[wi]
                    length = word_lens[wi]
                    word_plain = tuple(plain[start:start + length])
                    
                    if length in gp_dict and word_plain in gp_dict[length]:
                        matches += 1
                        match_details.append(f"W{wi}={gp_to_text(word_plain)}")
                
                if matches >= 10:
                    full_text = gp_to_text(plain)
                    # Insert spaces
                    spaced = []
                    pos = 0
                    for wl in word_lens:
                        spaced.append(gp_to_text(plain[pos:pos+wl]))
                        pos += wl
                    text = ' '.join(spaced)
                    
                    print(f"\n*** {combo_label} W8={w8_eng}: {matches}/{NW} matches ***")
                    print(f"  Key: {key}")
                    print(f"  Text: {text}")
                    print(f"  Matches: {', '.join(match_details)}")
                    best_results.append((matches, combo_label, w8_eng, key, text, match_details))
                
                tested += 1
            
            if tested % 1000 == 0 or True:
                print(f"  {combo_label}: tested {tested} W8 candidates", end='\r')
    
    print(f"\n{mode_name} mode complete.")

# ===== SUMMARY =====
print(f"\n{'='*80}")
print("RESULTS SUMMARY")
print(f"{'='*80}")

if not best_results:
    print("No results with >= 10 word matches found!")
    print("\nTrying lower threshold (>= 7 matches)...")
    # Re-run with lower threshold
    for mode_name, mode_fn in MODES:
        for w0_plain_name, w0_plain in [('A', 24), ('I', 10)]:
            key0 = get_key_from_plain(cipher[0], w0_plain, mode_name)
            for w7_plain_name, w7_plain in [('A', 24), ('I', 10)]:
                key10 = get_key_from_plain(cipher[23], w7_plain, mode_name)
                combo_label = f"{mode_name} W0={w0_plain_name} W7={w7_plain_name}"
                
                for w8_gp, w8_eng in gp_dict_words.get(w8_len, []):
                    key = [None] * K
                    key[0] = key0
                    key[10] = key10
                    
                    valid = True
                    for j in range(w8_len):
                        k_pos = w8_keys[j]
                        k_val = get_key_from_plain(w8_cipher[j], w8_gp[j], mode_name)
                        if key[k_pos] is not None:
                            if key[k_pos] != k_val:
                                valid = False
                                break
                        else:
                            key[k_pos] = k_val
                    
                    if not valid:
                        continue
                    if any(k is None for k in key):
                        continue
                    
                    plain = [mode_fn(cipher[i], key[i % K]) for i in range(N)]
                    
                    matches = 0
                    match_details = []
                    for wi in range(NW):
                        start = word_starts[wi]
                        length = word_lens[wi]
                        word_plain = tuple(plain[start:start + length])
                        if length in gp_dict and word_plain in gp_dict[length]:
                            matches += 1
                            match_details.append(f"W{wi}={gp_to_text(word_plain)}")
                    
                    if matches >= 7:
                        spaced = []
                        pos = 0
                        for wl in word_lens:
                            spaced.append(gp_to_text(plain[pos:pos+wl]))
                            pos += wl
                        text = ' '.join(spaced)
                        
                        print(f"\n  {combo_label} W8={w8_eng}: {matches}/{NW} matches")
                        print(f"    Key: {key}")
                        print(f"    Text: {text}")
                        print(f"    Matches: {', '.join(match_details)}")
                        best_results.append((matches, combo_label, w8_eng, key, text, match_details))
    
    if not best_results:
        print("\nStill no results with >= 7 matches!")
else:
    best_results.sort(key=lambda x: -x[0])
    for i, (matches, combo, w8, key, text, details) in enumerate(best_results[:20]):
        print(f"\n#{i+1}: {matches}/{NW} matches [{combo}] W8={w8}")
        print(f"  Key: {key}")
        print(f"  Text: {text}")
        print(f"  Matches: {', '.join(details)}")

print("\n=== DONE ===")
