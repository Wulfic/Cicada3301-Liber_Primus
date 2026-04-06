#!/usr/bin/env python3
"""
Session 16 — Deep solve for partially solved + unsolved pages.

Tests:
1. P.S. number (131 digits) as key material for P02 (key len 43)
2. P63 magic square numbers as key for various pages
3. P20 non-prime stream — systematic Caesar + keyword attacks
4. P18/P19 gap completion via crib dragging
5. Novel key derivations for P21-54 (p.s. number as seed, etc.)
"""

import os, sys, json, math
from collections import Counter

# --- Gematria Primus ---
RUNE_TO_IDX = {
    'ᚠ':0,'ᚢ':1,'ᚦ':2,'ᚩ':3,'ᚱ':4,'ᚳ':5,'ᚷ':6,'ᚹ':7,
    'ᚻ':8,'ᚾ':9,'ᛁ':10,'ᛄ':11,'ᛇ':12,'ᛈ':13,'ᛉ':14,'ᛋ':15,
    'ᛏ':16,'ᛒ':17,'ᛖ':18,'ᛗ':19,'ᛚ':20,'ᛝ':21,'ᛟ':22,'ᛞ':23,
    'ᚪ':24,'ᚫ':25,'ᚣ':26,'ᛡ':27,'ᛠ':28
}
# Also handle alternate J rune
RUNE_TO_IDX['ᛂ'] = 11

IDX_TO_LATIN = {
    0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',
    8:'H',9:'N',10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',
    16:'T',17:'B',18:'E',19:'M',20:'L',21:'NG',22:'OE',23:'D',
    24:'A',25:'AE',26:'Y',27:'IA',28:'EA'
}

M = 29  # modulus

def load_runes(page_num):
    """Load rune indices from a page file."""
    path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    indices = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            indices.append(RUNE_TO_IDX[ch])
    return indices

def decrypt(cipher, key, mode='sub'):
    """Decrypt cipher with key. mode: sub, add, beaufort."""
    out = []
    kl = len(key)
    ki = 0
    for i, c in enumerate(cipher):
        k = key[ki % kl]
        if mode == 'sub':
            p = (c - k) % M
        elif mode == 'add':
            p = (c + k) % M
        elif mode == 'beaufort':
            p = (k - c) % M
        else:
            p = (c - k) % M
        out.append(p)
        ki += 1
    return out

def decrypt_fskip(cipher, key, mode='sub'):
    """Decrypt with F-skip rule."""
    out = []
    kl = len(key)
    ki = 0
    for c in cipher:
        if c == 0:  # F rune
            # Try literal F first
            out.append(0)
            # Don't advance key
            continue
        k = key[ki % kl]
        if mode == 'sub':
            p = (c - k) % M
        elif mode == 'add':
            p = (c + k) % M
        elif mode == 'beaufort':
            p = (k - c) % M
        else:
            p = (c - k) % M
        out.append(p)
        ki += 1
    return out

def to_runeglish(indices):
    """Convert index list to runeglish string."""
    return ''.join(IDX_TO_LATIN.get(i, '?') for i in indices)

def ioc(indices):
    """Index of coincidence."""
    n = len(indices)
    if n < 2:
        return 0
    counts = Counter(indices)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * M

def english_score(text):
    """Simple English scoring based on common words."""
    words = ['THE','AND','OF','TO','IN','IS','IT','THAT','FOR','WAS','ON',
             'ARE','WITH','AS','HIS','THEY','BE','AT','ONE','HAVE','THIS',
             'FROM','OR','HAD','BY','NOT','BUT','WHAT','ALL','WERE','WHEN',
             'YOUR','CAN','SAID','THERE','EACH','WHICH','THEIR','AN','WILL',
             'YOU','DO','IF','HER','HE','SHE','WE','MY','NO','UP','SO',
             # LP-specific words
             'WISDOM','SACRED','PRIMES','TOTIENT','DIUINITY','CIRCUMFERENCE',
             'CONSUMPTION','PRESERUATION','ADHERENCE','BEHAUIORS','INSTRUCTION',
             'INTELLIGENCE','PARABLE','INSTAR','PILGRIM','DECEPTION','TRUTH',
             'FOLLOW','PROGRAM','MIND','REALITY','SELF','SUFFERING','STRUGGLE',
             'INNOCENCE','ILLUSIONS','CERTAINTY','EMERGE','WITHIN','DIVINITY',
             'WELCOME','JOURNEY','ENCRYPTED','FUNCTION','NOTHING','BELIEVE',
             'DESTROY','FORM','MOBIUS','CARNAL','OBSCURA','AETHEREAL','CABAL',
             'SHADOWS','MOURNFUL','BUFFERS','VOID','ANALOG',
             'CHAPTER','INTUS','WARNING','KOAN','MASTER','LESSON',
             'SOME','KNOW','THIS','QUESTION','DISCOVER','EXPERIENCE',
             'DEATH','BEING','HOLY','IMPOSE','COMMAND']
    score = 0
    for w in words:
        if w in text:
            score += len(w) * len(w)  # weight longer matches more
    return score

def score_decode(plaintext_indices):
    """Score a decryption attempt."""
    text = to_runeglish(plaintext_indices)
    ic = ioc(plaintext_indices)
    es = english_score(text)
    return ic, es, text

# ====================================================================
# TEST 1: P.S. NUMBER AS KEY FOR P02
# ====================================================================
def test_ps_number_p02():
    print("=" * 70)
    print("TEST 1: P.S. Number (131 digits) as key for P02 (key len 43)")
    print("=" * 70)
    
    PS_NUM = "10412790658919985359827898739594318956404425106955675643739226952372682423852959081739834390370374475764863415203423499357108713631"
    
    cipher = load_runes(2)
    if cipher is None:
        print("ERROR: Cannot load P02 runes")
        return
    print(f"P02 cipher: {len(cipher)} runes")
    
    results = []
    
    # Method A: Split into 43 triples, each mod 29
    triples = []
    for i in range(0, 129, 3):  # 43 triples × 3 = 129 digits
        triples.append(int(PS_NUM[i:i+3]))
    remainder = PS_NUM[129:]  # "31"
    key_a = [t % M for t in triples]
    print(f"\nMethod A: 43 triples mod 29 = {key_a}")
    print(f"  Remainder: {remainder} (= I rune prime value)")
    
    for mode in ['sub', 'add', 'beaufort']:
        plain = decrypt(cipher, key_a, mode)
        ic, es, text = score_decode(plain)
        results.append(('PS_triples', mode, False, ic, es, text))
        plain_fs = decrypt_fskip(cipher, key_a, mode)
        ic2, es2, text2 = score_decode(plain_fs)
        results.append(('PS_triples', mode, True, ic2, es2, text2))
    
    # Method B: Individual digits mod 29 (131 values, cycled over cipher)
    key_b = [int(d) for d in PS_NUM]
    for mode in ['sub', 'add', 'beaufort']:
        plain = decrypt(cipher, key_b, mode)
        ic, es, text = score_decode(plain)
        results.append(('PS_digits', mode, False, ic, es, text))
    
    # Method C: Digit pairs (65 values + 1 leftover)
    pairs = []
    for i in range(0, 130, 2):
        pairs.append(int(PS_NUM[i:i+2]))
    key_c = [p % M for p in pairs]
    for mode in ['sub', 'add', 'beaufort']:
        plain = decrypt(cipher, key_c, mode)
        ic, es, text = score_decode(plain)
        results.append(('PS_pairs', mode, False, ic, es, text))
    
    # Method D: Triples as GP prime values → index lookup
    PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    PRIME_TO_IDX = {p:i for i,p in enumerate(PRIMES)}
    key_d = [t % 109 for t in triples]  # mod largest GP prime
    key_d2 = []
    for v in key_d:
        # Find closest GP prime
        best = min(PRIMES, key=lambda p: abs(p - v))
        key_d2.append(PRIME_TO_IDX[best])
    for mode in ['sub', 'add', 'beaufort']:
        plain = decrypt(cipher, key_d2, mode)
        ic, es, text = score_decode(plain)
        results.append(('PS_prime_map', mode, False, ic, es, text))
    
    # Method E: Direct GP index from each triple mod 29
    # This is same as Method A but let's also try with known partial key overlay
    known_key = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]
    
    # Check how many positions match between PS-derived key and known partial key
    matches_a = sum(1 for i in range(43) if key_a[i] == known_key[i])
    print(f"\n  PS triples mod 29 vs known P02 key: {matches_a}/43 matches")
    
    # Method F: PS number as seed for mathematical generation
    # Sum consecutive digits in groups of various sizes
    for group_size in [2, 3, 4, 5, 6, 7]:
        key_f = []
        for i in range(0, len(PS_NUM) - group_size + 1, group_size):
            val = sum(int(d) for d in PS_NUM[i:i+group_size])
            key_f.append(val % M)
        if len(key_f) < 5: continue
        for mode in ['sub', 'add', 'beaufort']:
            plain = decrypt(cipher, key_f, mode)
            ic, es, text = score_decode(plain)
            results.append((f'PS_digitsum{group_size}', mode, False, ic, es, text))
    
    # Method G: PS number digits as ordinal GP prime indices
    # digit 1 → prime[1]=3, digit 0 → prime[0]=2, etc.
    key_g = [int(d) % M for d in PS_NUM]
    for mode in ['sub', 'add', 'beaufort']:
        plain = decrypt(cipher, key_g, mode)
        ic, es, text = score_decode(plain)
        results.append(('PS_ordinal', mode, False, ic, es, text))
    
    # Sort by IoC
    results.sort(key=lambda x: x[3], reverse=True)
    
    print("\n--- TOP 15 RESULTS (sorted by IoC) ---")
    for name, mode, fskip, ic, es, text in results[:15]:
        fs_str = "+Fskip" if fskip else ""
        print(f"  {name:20s} {mode:8s}{fs_str:8s}  IoC={ic:.4f}  EScore={es:4d}  {text[:80]}")
    
    print("\n--- TOP 15 RESULTS (sorted by English Score) ---")
    results.sort(key=lambda x: x[4], reverse=True)
    for name, mode, fskip, ic, es, text in results[:15]:
        fs_str = "+Fskip" if fskip else ""
        print(f"  {name:20s} {mode:8s}{fs_str:8s}  IoC={ic:.4f}  EScore={es:4d}  {text[:80]}")


# ====================================================================
# TEST 2: P63 MAGIC SQUARE NUMBERS AS KEY
# ====================================================================
def test_p63_numbers():
    print("\n" + "=" * 70)
    print("TEST 2: P63 Magic Square numbers as key material")
    print("=" * 70)
    
    # P63 grid numbers (row-major order, skipping keywords)
    grid_nums = [272, 138, 131, 151, 18, 226, 245, 18, 151, 131, 138, 272]
    # Grid with keywords (using GP index sums for keywords)
    # SHADOWS = [15,8,24,23,3,7,15] → sum=95
    # AETHEREAL = [24,18,2,8,18,4,18,24,20] → sum=136
    # etc.
    
    # Numbers mod 29
    key_grid = [n % M for n in grid_nums]
    print(f"Grid numbers mod 29: {key_grid}")
    
    # Full 5x5 grid as key (reading numbers only, 12 values)
    # Also full 5x5 grid reading order
    full_row = [272, 138, 341, 131, 151,  366, 199, 130, 320, 18,  226, 245, 91, 245, 226,  18, 320, 130, 199, 366,  151, 131, 341, 138, 272]
    key_full = [n % M for n in full_row]
    print(f"Full grid mod 29 (25 values): {key_full}")
    
    # Test on P02 and P20
    for page in [2, 20]:
        cipher = load_runes(page)
        if cipher is None:
            print(f"  P{page:02d}: Cannot load runes")
            continue
        print(f"\n  P{page:02d} ({len(cipher)} runes):")
        for key, kname in [(key_grid, 'nums12'), (key_full, 'full25')]:
            for mode in ['sub', 'add', 'beaufort']:
                plain = decrypt(cipher, key, mode)
                ic, es, text = score_decode(plain)
                if ic > 1.2 or es > 50:
                    print(f"    {kname:8s} {mode:8s}  IoC={ic:.4f}  EScore={es:4d}  {text[:70]}")


# ====================================================================
# TEST 3: P20 NON-PRIME STREAM SYSTEMATIC ATTACK
# ====================================================================
def test_p20_nonprime():
    print("\n" + "=" * 70)
    print("TEST 3: P20 Non-Prime Stream (646 runes) — Systematic Attack")
    print("=" * 70)
    
    cipher_full = load_runes(20)
    if cipher_full is None:
        print("ERROR: Cannot load P20 runes")
        return
    
    # Generate primes for position check
    def is_prime(n):
        if n < 2: return False
        if n < 4: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i*i <= n:
            if n%i==0 or n%(i+2)==0: return False
            i+=6
        return True
    
    # Separate prime and non-prime positions (0-indexed)
    prime_pos = [i for i in range(len(cipher_full)) if is_prime(i)]
    nonprime_pos = [i for i in range(len(cipher_full)) if not is_prime(i)]
    
    nonprime_stream = [cipher_full[i] for i in nonprime_pos]
    print(f"P20 total: {len(cipher_full)} runes")
    print(f"Prime positions: {len(prime_pos)} runes (solved)")
    print(f"Non-prime positions: {len(nonprime_stream)} runes (unsolved)")
    
    results = []
    
    # Test A: All Caesar shifts
    for shift in range(29):
        plain = [(c - shift) % M for c in nonprime_stream]
        ic, es, text = score_decode(plain)
        results.append((f'Caesar_{shift}', ic, es, text))
    
    # Test B: Known keywords as Vigenère keys
    KEYWORDS = {
        'DIVINITY': [23,10,1,10,9,10,16,26],
        'FIRFUMFERENFE': [0,10,4,0,1,19,0,18,4,18,9,0,18],
        'YAHEOOPYJ': [26,24,8,18,3,3,13,26,11],
        'CICADA': [5,10,5,24,23,24],
        'CABAL': [5,24,17,24,20],
        'OBSCURA': [3,17,15,5,1,4,24],
        'SHADOWS': [15,8,24,23,3,7,15],
        'ENCRYPT': [18,9,5,4,26,13,16],
        'ENCRYPTION': [18,9,5,4,26,13,16,10,3,9],
        'TOTIENT': [16,3,16,10,18,9,16],
        'MOURNFUL': [19,3,1,4,9,0,1,20],
        'DEOR': [23,18,3,4],
        'INSTAR': [10,9,15,16,24,4],
        'PRIMAL': [13,4,10,19,24,20],
        'TRUTH': [16,4,1,16,8],
    }
    
    for kname, key in KEYWORDS.items():
        for mode in ['sub', 'add', 'beaufort']:
            plain = decrypt(nonprime_stream, key, mode)
            ic, es, text = score_decode(plain)
            results.append((f'{kname}_{mode}', ic, es, text))
            # Also with F-skip
            plain_fs = decrypt_fskip(nonprime_stream, key, mode)
            ic2, es2, text2 = score_decode(plain_fs)
            results.append((f'{kname}_{mode}_fs', ic2, es2, text2))
    
    # Test C: P20 prime stream plaintext as running key for non-prime stream
    # (Autokey concept — the solved part keys the unsolved part)
    # Load Deor poem for the prime-stream decrypt
    deor_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'deor_poem.txt')
    if os.path.exists(deor_path):
        with open(deor_path, 'r', encoding='utf-8') as f:
            deor_text = f.read().upper()
        LATIN_TO_IDX = {}
        for idx, latin in IDX_TO_LATIN.items():
            LATIN_TO_IDX[latin] = idx
        
        # Simple letter-by-letter conversion of Deor to GP indices
        deor_gp = []
        i = 0
        while i < len(deor_text):
            matched = False
            for dlen in [2, 1]:  # Try digraphs first
                chunk = deor_text[i:i+dlen]
                if chunk in LATIN_TO_IDX:
                    deor_gp.append(LATIN_TO_IDX[chunk])
                    i += dlen
                    matched = True
                    break
            if not matched:
                i += 1  # skip non-GP chars
        
        if len(deor_gp) > 0:
            print(f"\n  Deor poem: {len(deor_gp)} GP values available")
            # Test Deor as running key at various offsets
            for offset in range(0, min(len(deor_gp), 500), 1):
                key_slice = deor_gp[offset:offset+len(nonprime_stream)]
                if len(key_slice) < len(nonprime_stream):
                    key_slice = (deor_gp * ((len(nonprime_stream) // len(deor_gp)) + 2))[offset:offset+len(nonprime_stream)]
                for mode in ['sub', 'add', 'beaufort']:
                    plain = decrypt(nonprime_stream, key_slice, mode)
                    ic, es, text = score_decode(plain)
                    if ic > 1.5 or es > 100:
                        results.append((f'Deor_off{offset}_{mode}', ic, es, text))
    
    # Test D: P.S. number digits as key
    PS_NUM = "10412790658919985359827898739594318956404425106955675643739226952372682423852959081739834390370374475764863415203423499357108713631"
    ps_key = [int(d) % M for d in PS_NUM]
    for mode in ['sub', 'add', 'beaufort']:
        plain = decrypt(nonprime_stream, ps_key, mode)
        ic, es, text = score_decode(plain)
        results.append((f'PS_digits_{mode}', ic, es, text))
    
    # Test E: Interleave cipher — recombine prime+nonprime with transposition
    # Maybe non-prime runes need a different reading order
    # Try reading non-prime backwards
    for shift in range(29):
        plain = [(c - shift) % M for c in reversed(nonprime_stream)]
        ic, es, text = score_decode(plain)
        if ic > 1.5 or es > 50:
            results.append((f'Rev_Caesar_{shift}', ic, es, text))
    
    # Test F: Columnar transposition of non-prime stream
    for width in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 34, 37, 38]:
        n = len(nonprime_stream)
        # Read columns
        reordered = []
        rows = (n + width - 1) // width
        for col in range(width):
            for row in range(rows):
                pos = row * width + col
                if pos < n:
                    reordered.append(nonprime_stream[pos])
        for shift in range(29):
            plain = [(c - shift) % M for c in reordered]
            ic, es, text = score_decode(plain)
            if ic > 1.5 or es > 80:
                results.append((f'ColT_w{width}_s{shift}', ic, es, text))
    
    # Sort and report
    results.sort(key=lambda x: x[1], reverse=True)
    print("\n--- TOP 20 RESULTS (sorted by IoC) ---")
    for name, ic, es, text in results[:20]:
        print(f"  {name:30s}  IoC={ic:.4f}  EScore={es:4d}  {text[:70]}")
    
    results.sort(key=lambda x: x[2], reverse=True)
    print("\n--- TOP 20 RESULTS (sorted by English Score) ---")
    for name, ic, es, text in results[:20]:
        print(f"  {name:30s}  IoC={ic:.4f}  EScore={es:4d}  {text[:70]}")


# ====================================================================
# TEST 4: P02 CRIB EXTENSION WITH KNOWN FRAGMENTS
# ====================================================================
def test_p02_crib_extend():
    print("\n" + "=" * 70)
    print("TEST 4: P02 Crib Extension from Known Fragments")
    print("=" * 70)
    
    cipher = load_runes(2)
    if cipher is None:
        print("ERROR: Cannot load P02 runes")
        return
    
    # Known partial key (43 elements)
    known_key = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]
    
    # Decrypt with known key
    plain = decrypt(cipher, known_key, 'sub')
    ic_known, es_known, text_known = score_decode(plain)
    print(f"Known key decrypt:  IoC={ic_known:.4f}  EScore={es_known}")
    print(f"Text: {text_known[:200]}")
    
    # Known fragments from crib dragging: "SAME AS THAT", "THE OTHER", "WITH A", "THE SONG"
    # Let's try LP-specific cribs to refine key positions
    LP_CRIBS = [
        "CHAPTER", "INTUS", "SOME WISDOM", "AN INSTRUCTION",
        "A KOAN", "A WARNING", "WELCOME", "PILGRIM",
        "THE PRIMES ARE SACRED", "THE TOTIENT FUNCTION",
        "ALL THINGS SHOULD BE ENCRYPTED", "KNOW THIS",
        "QUESTION ALL THINGS", "DISCOVER TRUTH",
        "AN END", "WITHIN THE DEEP WEB",
        "IT IS THE DUTY", "SEEK OUT THIS PAGE",
        "PROGRAM YOUR MIND", "PROGRAM REALITY",
        "COMMAND YOUR OWN SELF", "EACH INTELLIGENCE IS HOLY",
        "BELIEVE NOTHING", "EXPERIENCE YOUR DEATH",
        "SAME AS THAT WHICH", "THE OTHER SIDE",
        "THE SONG OF", "WITH A GREAT",
        # P19 hint text
        "REARRANGING THE PRIMES",
        # Solved P02 area content
        "CHAPTER I INTUS",
    ]
    
    LATIN_TO_IDX = {}
    for idx, latin in IDX_TO_LATIN.items():
        LATIN_TO_IDX[latin] = idx
    
    def text_to_gp(text):
        """Convert Latin text to GP indices."""
        text = text.upper().replace(' ', '')
        result = []
        i = 0
        while i < len(text):
            matched = False
            for dlen in [2, 1]:
                chunk = text[i:i+dlen]
                if chunk in LATIN_TO_IDX:
                    result.append(LATIN_TO_IDX[chunk])
                    i += dlen
                    matched = True
                    break
            if not matched:
                i += 1
        return result
    
    print(f"\nCipher length: {len(cipher)}, Key length: 43")
    print("Testing LP cribs at all positions...")
    
    best_results = []
    for crib_text in LP_CRIBS:
        crib_gp = text_to_gp(crib_text)
        if len(crib_gp) == 0: continue
        
        # Try placing crib at every position in cipher
        for pos in range(len(cipher) - len(crib_gp) + 1):
            # Derive key values from crib placement
            derived_key = {}
            valid = True
            for j, p in enumerate(crib_gp):
                c = cipher[pos + j]
                k_pos = (pos + j) % 43
                k_val = (c - p) % M
                if k_pos in derived_key and derived_key[k_pos] != k_val:
                    valid = False
                    break
                derived_key[k_pos] = k_val
            
            if not valid: continue
            
            # Check if derived key matches known key at overlapping positions
            match_count = 0
            mismatch_count = 0
            for k_pos, k_val in derived_key.items():
                if k_val == known_key[k_pos]:
                    match_count += 1
                else:
                    mismatch_count += 1
            
            # Build merged key
            merged = list(known_key)
            for k_pos, k_val in derived_key.items():
                merged[k_pos] = k_val
            
            full_plain = decrypt(cipher, merged, 'sub')
            ic, es, text = score_decode(full_plain)
            
            if match_count >= 2 or es > es_known + 20:
                best_results.append((crib_text, pos, match_count, mismatch_count, ic, es, text))
    
    best_results.sort(key=lambda x: (x[2], x[5]), reverse=True)
    print(f"\n--- TOP CRIB PLACEMENTS (by key matches + score) ---")
    for crib, pos, mc, mmc, ic, es, text in best_results[:20]:
        print(f"  '{crib}' @ pos {pos}: matches={mc} mismatches={mmc} IoC={ic:.4f} EScore={es} text={text[:60]}")


# ====================================================================
# TEST 5: P.S. NUMBER ADVANCED DERIVATIONS
# ====================================================================
def test_ps_advanced():
    print("\n" + "=" * 70)
    print("TEST 5: P.S. Number — Advanced Key Derivations")
    print("=" * 70)
    
    PS_NUM = "10412790658919985359827898739594318956404425106955675643739226952372682423852959081739834390370374475764863415203423499357108713631"
    PS_INT = int(PS_NUM)
    
    # Method 1: PS mod prime[n] for n = 0..28
    PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    key_primemod = [int(PS_INT % p) % M for p in PRIMES]
    print(f"PS mod prime[n] mod 29: {key_primemod}")
    
    # Method 2: Cumulative digit products mod 29
    key_cumproduct = []
    prod = 1
    for d in PS_NUM:
        v = int(d)
        if v == 0: v = 1
        prod = (prod * v) % M
        key_cumproduct.append(prod)
    
    # Method 3: PS_INT mod (29^k) for k = 1..50
    key_powers = []
    for k in range(1, 51):
        key_powers.append(int(PS_INT % (M**k)) % M)
    
    # Method 4: Fibonacci-like from PS digits
    key_fib = [int(PS_NUM[0]), int(PS_NUM[1])]
    for i in range(2, 200):
        key_fib.append((key_fib[-1] + key_fib[-2]) % M)
    
    # Method 5: PS digits XOR'd with position
    key_xor = [(int(PS_NUM[i % 131]) ^ (i % 29)) % M for i in range(200)]
    
    # Test all on P02 and unsolved pages
    test_keys = {
        'PS_primemod29': key_primemod,
        'PS_cumproduct': key_cumproduct[:43],
        'PS_powers29': key_powers[:43],
        'PS_fibonacci': key_fib[:43],
        'PS_xor_pos': key_xor[:43],
    }
    
    for page in [2, 18, 20]:
        cipher = load_runes(page)
        if cipher is None: continue
        print(f"\nP{page:02d} ({len(cipher)} runes):")
        for kname, key in test_keys.items():
            for mode in ['sub', 'add', 'beaufort']:
                plain = decrypt(cipher, key, mode)
                ic, es, text = score_decode(plain)
                if ic > 1.3 or es > 40:
                    print(f"  {kname:20s} {mode:8s}  IoC={ic:.4f}  EScore={es:4d}  {text[:60]}")


# ====================================================================
# TEST 6: VALUE-BASED SEPARATION ATTACKS ON P20
# ====================================================================
def test_p20_value_based():
    print("\n" + "=" * 70)
    print("TEST 6: P20 Value-Based Separation + Interleave Tests")
    print("=" * 70)
    
    cipher = load_runes(20)
    if cipher is None:
        print("ERROR: Cannot load P20")
        return
    
    PRIMES_SET = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109}
    GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
    
    # Separate by GP prime value (prime-valued vs non-prime-valued runes)
    prime_valued = []   # indices whose GP prime value is in some set
    non_prime_valued = []
    for i, idx in enumerate(cipher):
        if GP_PRIMES[idx] in PRIMES_SET:  # all GP values are prime, so this is trivially true
            pass  # Need a different criterion
    
    # Separate by index being prime vs not
    def is_prime(n):
        if n < 2: return False
        if n < 4: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i*i <= n:
            if n%i==0 or n%(i+2)==0: return False
            i+=6
        return True
    
    # Get non-prime position runes
    nonprime_runes = [cipher[i] for i in range(len(cipher)) if not is_prime(i)]
    
    # Try reading non-prime runes in different orders:
    # Spiral reading (Fibonacci spiral — §8.5)
    n = len(nonprime_runes)
    
    # Try interleaving: even-indexed non-prime runes and odd-indexed
    even_np = [nonprime_runes[i] for i in range(0, n, 2)]
    odd_np = [nonprime_runes[i] for i in range(1, n, 2)]
    
    # Try both orderings
    interleaved_1 = even_np + odd_np
    interleaved_2 = odd_np + even_np
    
    results = []
    for stream, sname in [(nonprime_runes, 'nonprime'), (interleaved_1, 'even+odd'), (interleaved_2, 'odd+even')]:
        for shift in range(29):
            plain = [(c - shift) % M for c in stream]
            ic, es, text = score_decode(plain)
            if ic > 1.5 or shift == 16:  # shift 16 was noted as best
                results.append((f'{sname}_s{shift}', ic, es, text))
    
    # Test: recombine prime-stream plaintext interleaved with non-prime shifted
    # This tests whether the full page text makes sense when both streams are combined
    prime_runes = [cipher[i] for i in range(len(cipher)) if is_prime(i)]
    
    # Deor Beaufort for prime stream (known working method)
    deor_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'deor_poem.txt')
    if os.path.exists(deor_path):
        with open(deor_path, 'r', encoding='utf-8') as f:
            deor_text = f.read().upper()
        
        LATIN_TO_IDX = {}
        for idx, latin in IDX_TO_LATIN.items():
            LATIN_TO_IDX[latin] = idx
        
        deor_gp = []
        i = 0
        while i < len(deor_text):
            matched = False
            for dlen in [2, 1]:
                chunk = deor_text[i:i+dlen]
                if chunk in LATIN_TO_IDX:
                    deor_gp.append(LATIN_TO_IDX[chunk])
                    i += dlen
                    matched = True
                    break
            if not matched:
                i += 1
        
        # Decrypt prime stream with Deor Beaufort
        if len(deor_gp) >= len(prime_runes):
            prime_plain = decrypt(prime_runes, deor_gp[:len(prime_runes)], 'beaufort')
            prime_text = to_runeglish(prime_plain)
            print(f"\nPrime stream (Beaufort+Deor): IoC={ioc(prime_plain):.4f}")
            print(f"  {prime_text[:200]}")
    
    results.sort(key=lambda x: x[1], reverse=True)
    print("\n--- TOP P20 Non-Prime Results ---")
    for name, ic, es, text in results[:15]:
        print(f"  {name:25s}  IoC={ic:.4f}  EScore={es:4d}  {text[:70]}")


# ====================================================================
# MAIN
# ====================================================================
if __name__ == '__main__':
    print("Session 16 — Deep Solve for Liber Primus")
    print("=" * 70)
    
    test_ps_number_p02()
    test_p63_numbers()
    test_p20_nonprime()
    test_p02_crib_extend()
    test_ps_advanced()
    test_p20_value_based()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
