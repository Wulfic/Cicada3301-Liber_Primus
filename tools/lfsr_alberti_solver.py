#!/usr/bin/env python3
"""
LFSR and Alberti Cipher Solver for Liber Primus
Tests:
  1. Alberti progressive cipher (direction x letter_shift x space_shift) 
  2. LFSR over GF(29) for lengths 2-4
  3. Prime/Fibonacci stream (from RuneSolver)
  4. Berlekamp-Massey with crib-dragging
"""

import sys, os, json, itertools, math
from collections import Counter
from pathlib import Path

# ── Gematria Primus alphabet ─────────────────────────────────────────────────
RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP_VALUES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,
             89,97,101,103,107,109]
SEPARATORS = set("•.-:' \n")
N = 29  # alphabet size

RUNE_TO_IDX = {r: i for i, r in enumerate(RUNES)}

# ── English bigram log-probability table (approximation) ─────────────────────
# We use IoC and trigram hits as our scoring functions
COMMON_BIGRAMS = {
    (16,8): 5,   # TH
    (8,18): 4,   # HE
    (10,9): 4,   # IN
    (18,4): 3,   # ER
    (24,9): 3,   # AN
    (4,18): 3,   # RE
    (22,9): 3,   # ON (OE->N, but let's use standard)
    (24,16): 3,  # AT
    (18,9): 3,   # EN
    (9,23): 3,   # ND
    (16,10): 3,  # TI
    (18,15): 3,  # ES
    (22,4): 2,   # OR (using OE=22)
    (16,18): 3,  # TE
    (24,20): 2,  # AL
    (15,16): 2,  # ST
    (10,16): 2,  # IT
    (10,15): 2,  # IS
    (22,0): 2,   # OF (using OE=22, F=0)
    (8,24): 2,   # HA
}

COMMON_TRIGRAMS_SET = set()
# Build from runeglish: THE, AND, THA, ENT, ION, etc.
for trig_str in ["THE","AND","THA","ENT","ION","TIO","FOR","NDE","HAS","NCE",
                  "EDT","TIS","OFT","MEN","ALL","ARE","HER","WAS","ONE","OUR",
                  "OUT","NOT","ING","HAT","HIS","HIN","ITH","FTH","STH","WIT"]:
    # Convert to rune indices
    idxs = []
    pos = 0
    while pos < len(trig_str):
        found = False
        # Try 2-char runeglish first
        if pos + 1 < len(trig_str):
            di = trig_str[pos:pos+2]
            if di in RUNEGLISH:
                idxs.append(RUNEGLISH.index(di))
                pos += 2
                found = True
        if not found:
            ch = trig_str[pos]
            if ch in RUNEGLISH:
                idxs.append(RUNEGLISH.index(ch))
            pos += 1
    if len(idxs) == 3:
        COMMON_TRIGRAMS_SET.add(tuple(idxs))

def extract_runes(text):
    """Extract rune indices from text, skipping separators."""
    indices = []
    sep_positions = []  # track which positions in original are separators
    for i, ch in enumerate(text):
        if ch in RUNE_TO_IDX:
            indices.append(RUNE_TO_IDX[ch])
        elif ch in SEPARATORS:
            sep_positions.append(len(indices))  # separator after this many runes
    return indices, sep_positions

def ioc(indices):
    """Calculate Index of Coincidence, normalized by alphabet size (x29)."""
    n = len(indices)
    if n < 2:
        return 0.0
    freq = Counter(indices)
    total = sum(f * (f - 1) for f in freq.values())
    return (total * N) / (n * (n - 1))

def bigram_score(indices):
    """Score based on common bigram matches."""
    score = 0
    for i in range(len(indices) - 1):
        pair = (indices[i], indices[i+1])
        if pair in COMMON_BIGRAMS:
            score += COMMON_BIGRAMS[pair]
    return score

def trigram_hits(indices):
    """Count common trigram matches."""
    hits = 0
    for i in range(len(indices) - 2):
        trip = (indices[i], indices[i+1], indices[i+2])
        if trip in COMMON_TRIGRAMS_SET:
            hits += 1
    return hits

def decrypt_sub(cipher, key_stream):
    """SUB mode: plain = (cipher - key) % 29"""
    return [(c - k) % N for c, k in zip(cipher, key_stream)]

def decrypt_add(cipher, key_stream):
    """ADD mode: plain = (cipher + key) % 29"""
    return [(c + k) % N for c, k in zip(cipher, key_stream)]

def decrypt_beaufort(cipher, key_stream):
    """Beaufort mode: plain = (key - cipher) % 29"""
    return [(k - c) % N for c, k in zip(cipher, key_stream)]

def to_runeglish(indices):
    """Convert rune indices to runeglish string."""
    return "".join(RUNEGLISH[i] for i in indices)

# ── LFSR over GF(29) ────────────────────────────────────────────────────────

def lfsr_keystream(init_state, taps, length):
    """Generate LFSR keystream over GF(29).
    
    init_state: list of n initial values in [0,28]
    taps: list of n coefficients in [0,28]
    length: number of keystream elements to generate
    """
    n = len(init_state)
    state = list(init_state)
    keystream = []
    
    for _ in range(length):
        keystream.append(state[0])
        # Compute feedback
        new_val = sum(t * s for t, s in zip(taps, state)) % N
        state = state[1:] + [new_val]
    
    return keystream

def brute_force_lfsr_n2(cipher, modes=None):
    """Brute-force all LFSR(2) over GF(29). 29^4 = 707,281 combos."""
    if modes is None:
        modes = [("SUB", decrypt_sub), ("ADD", decrypt_add), ("BEAU", decrypt_beaufort)]
    
    best = []
    length = len(cipher)
    total = N ** 4
    count = 0
    
    for s0 in range(N):
        for s1 in range(N):
            for c0 in range(N):
                for c1 in range(N):
                    ks = lfsr_keystream([s0, s1], [c0, c1], length)
                    for mode_name, decrypt_fn in modes:
                        plain = decrypt_fn(cipher, ks)
                        ic = ioc(plain)
                        if ic > 1.5:
                            bg = bigram_score(plain)
                            tg = trigram_hits(plain)
                            best.append({
                                'ioc': ic,
                                'bigrams': bg,
                                'trigrams': tg,
                                'mode': mode_name,
                                'state': (s0, s1),
                                'taps': (c0, c1),
                                'sample': to_runeglish(plain[:60]),
                                'score': ic + bg * 0.01 + tg * 0.05,
                            })
        count += N ** 3
        if count % (N ** 3 * 5) == 0:
            pct = count / total * 100
            print(f"  LFSR(2) progress: {pct:.1f}% ({len(best)} hits so far)")
    
    best.sort(key=lambda x: -x['score'])
    return best[:50]

def smart_lfsr_n3(cipher, modes=None, sample_size=100):
    """Smart LFSR(3) search: fix first 3 keystream elements from top IoC bands."""
    if modes is None:
        modes = [("SUB", decrypt_sub)]
    
    best = []
    length = len(cipher)
    
    # For LFSR(3), we need state (s0,s1,s2) and taps (c0,c1,c2)
    # Key insight: given s0,s1,s2 and the first 6 outputs, we can compute taps
    # Output: k0=s0, k1=s1, k2=s2, k3=(c0*s0+c1*s1+c2*s2)%29, etc.
    # So if we hypothesize k0,k1,k2,k3,k4,k5, we can solve for c0,c1,c2
    # using k3 = c0*k0 + c1*k1 + c2*k2 (mod 29)
    #       k4 = c0*k1 + c1*k2 + c2*k3 (mod 29)
    #       k5 = c0*k2 + c1*k3 + c2*k4 (mod 29)
    # This is a 3x3 linear system over GF(29)
    
    # Strategy: try all 29^3 = 24,389 possible (s0,s1,s2), then all 29^3 taps
    # Total: 29^6 ≈ 595M — too many. Let's prune.
    
    # Better: for each mode, try all (s0,s1,s2), compute first 3 keystream elements,
    # check if partial decryption is promising, then try all (c0,c1,c2) only for promising ones.
    
    # Even better: random sampling approach
    import random
    random.seed(42)
    
    tested = 0
    for _ in range(500000):  # 500K random samples
        s = [random.randint(0, N-1) for _ in range(3)]
        c = [random.randint(0, N-1) for _ in range(3)]
        ks = lfsr_keystream(s, c, length)
        
        for mode_name, decrypt_fn in modes:
            plain = decrypt_fn(cipher, ks)
            ic = ioc(plain)
            if ic > 1.5:
                bg = bigram_score(plain)
                tg = trigram_hits(plain)
                best.append({
                    'ioc': ic,
                    'bigrams': bg,
                    'trigrams': tg,
                    'mode': mode_name,
                    'state': tuple(s),
                    'taps': tuple(c),
                    'sample': to_runeglish(plain[:60]),
                    'score': ic + bg * 0.01 + tg * 0.05,
                })
        
        tested += 1
        if tested % 100000 == 0:
            print(f"  LFSR(3) random search: {tested}/500000 ({len(best)} hits)")
    
    best.sort(key=lambda x: -x['score'])
    return best[:50]

# ── Alberti Progressive Cipher ──────────────────────────────────────────────

def alberti_decrypt(text, direction, letter_shift, space_shift, mode="sub"):
    """
    Alberti cipher: maintains a shifting alphabet.
    After each letter, shift the cipher alphabet by letter_shift.
    After each space/separator, shift by space_shift.
    direction=True: shift right (clockwise), False: shift left.
    """
    cipher_indices, sep_positions = extract_runes(text)
    plain = []
    offset = 0
    sep_set = set(sep_positions)
    rune_count = 0
    
    for i, c in enumerate(cipher_indices):
        if mode == "sub":
            p = (c - offset) % N
        elif mode == "add":
            p = (c + offset) % N
        else:  # beaufort
            p = (offset - c) % N
        
        plain.append(p)
        
        if direction:
            offset = (offset + letter_shift) % N
        else:
            offset = (offset - letter_shift) % N
        
        rune_count += 1
        # Check if a separator follows this position
        if rune_count in sep_set:
            if direction:
                offset = (offset + space_shift) % N
            else:
                offset = (offset - space_shift) % N
    
    return plain

def brute_force_alberti(text, top_n=30):
    """Test all direction x letter_shift x space_shift x mode combinations."""
    print("\n=== ALBERTI PROGRESSIVE CIPHER ===")
    
    cipher, seps = extract_runes(text)
    print(f"  Cipher length: {len(cipher)} runes, {len(seps)} separators")
    
    best = []
    
    for direction in [True, False]:
        dir_name = "CW" if direction else "CCW"
        for letter_shift in range(N):
            for space_shift in range(N):
                for mode in ["sub", "add", "beaufort"]:
                    plain = alberti_decrypt(text, direction, letter_shift, space_shift, mode)
                    ic = ioc(plain)
                    if ic > 1.4:
                        bg = bigram_score(plain)
                        tg = trigram_hits(plain)
                        best.append({
                            'ioc': ic,
                            'bigrams': bg,
                            'trigrams': tg,
                            'dir': dir_name,
                            'letter_shift': letter_shift,
                            'space_shift': space_shift,
                            'mode': mode,
                            'sample': to_runeglish(plain[:80]),
                            'score': ic + bg * 0.01 + tg * 0.05,
                        })
        print(f"  Direction {dir_name} done ({len(best)} hits with IoC > 1.4)")
    
    best.sort(key=lambda x: -x['score'])
    return best[:top_n]

# ── RuneSolver-style Streams ────────────────────────────────────────────────

PRIME_STREAM = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,
                83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,
                173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,
                263,1,269,271,277,281,283,293,307,311,313,317,331,337,347,349,353,
                359,367,373,379,383,389,397,401,409,419,421,431,433]

FIBONACCI_STREAM = [0,1,1,2,3,5,8,13,21,5,26,2,28]

def stream_decrypt(cipher, stream, mode="sub", skip_first=False):
    """Apply a repeating stream as key, like RuneSolver vigstream."""
    offset = 1 if skip_first else 0
    ks = []
    for i in range(len(cipher)):
        ks.append(stream[(i + offset) % len(stream)] % N)
    
    if mode == "sub":
        return [(c - k) % N for c, k in zip(cipher, ks)]
    elif mode == "add":
        return [(c + k) % N for c, k in zip(cipher, ks)]
    else:
        return [(k - c) % N for c, k in zip(cipher, ks)]

def test_streams(cipher, page_name):
    """Test prime and fibonacci streams from RuneSolver."""
    print(f"\n=== STREAM CIPHER TESTS ({page_name}) ===")
    
    results = []
    for stream_name, stream in [("PRIME", PRIME_STREAM), ("FIBONACCI", FIBONACCI_STREAM)]:
        for mode in ["sub", "add", "beaufort"]:
            for skip in [False, True]:
                plain = stream_decrypt(cipher, stream, mode, skip)
                ic = ioc(plain)
                bg = bigram_score(plain)
                tg = trigram_hits(plain)
                skip_str = "+skip" if skip else ""
                results.append({
                    'stream': stream_name,
                    'mode': mode,
                    'skip': skip,
                    'ioc': ic,
                    'bigrams': bg,
                    'trigrams': tg,
                    'sample': to_runeglish(plain[:60]),
                    'score': ic + bg * 0.01 + tg * 0.05,
                })
    
    # Also test totient variant (stream - 1)
    for stream_name, stream in [("PRIME-1", [max(0,s-1) for s in PRIME_STREAM])]:
        for mode in ["sub", "add", "beaufort"]:
            plain = stream_decrypt(cipher, stream, mode, False)
            ic = ioc(plain)
            bg = bigram_score(plain)
            tg = trigram_hits(plain)
            results.append({
                'stream': stream_name,
                'mode': mode,
                'skip': False,
                'ioc': ic,
                'bigrams': bg,
                'trigrams': tg,
                'sample': to_runeglish(plain[:60]),
                'score': ic + bg * 0.01 + tg * 0.05,
            })
    
    results.sort(key=lambda x: -x['score'])
    for r in results[:10]:
        skip_str = "+skip" if r['skip'] else ""
        print(f"  {r['stream']}{skip_str} {r['mode']:8s} IoC={r['ioc']:.4f} bg={r['bigrams']:3d} tg={r['trigrams']:2d} | {r['sample'][:50]}")
    
    return results

# ── Berlekamp-Massey over GF(29) ───────────────────────────────────────────

def mod_inverse(a, m=N):
    """Modular inverse using extended Euclidean algorithm."""
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

def berlekamp_massey_gf29(sequence):
    """
    Berlekamp-Massey algorithm over GF(29).
    Returns LFSR taps (connection polynomial coefficients).
    """
    n = len(sequence)
    c = [0] * (n + 1)
    b = [0] * (n + 1)
    c[0] = 1
    b[0] = 1
    L = 0
    m = 1
    bb = 1
    
    for i in range(n):
        # Compute discrepancy
        d = sequence[i]
        for j in range(1, L + 1):
            d = (d + c[j] * sequence[i - j]) % N
        d = d % N
        
        if d == 0:
            m += 1
        elif 2 * L <= i:
            t = list(c)
            inv_bb = mod_inverse(bb)
            if inv_bb is None:
                return None
            coeff = (d * inv_bb) % N
            for j in range(m, n + 1):
                if j - m < len(b):
                    c[j] = (c[j] - coeff * b[j - m]) % N
            L = i + 1 - L
            b = list(t)
            bb = d
            m = 1
        else:
            inv_bb = mod_inverse(bb)
            if inv_bb is None:
                return None
            coeff = (d * inv_bb) % N
            for j in range(m, n + 1):
                if j - m < len(b):
                    c[j] = (c[j] - coeff * b[j - m]) % N
            m += 1
    
    return c[:L+1], L

def crib_drag_lfsr(cipher, cribs, mode="sub"):
    """
    Try cribs at various positions, extract keystream, run Berlekamp-Massey.
    """
    print(f"\n=== CRIB-DRAG LFSR ATTACK (mode={mode}) ===")
    results = []
    
    for crib_name, crib_indices in cribs.items():
        crib_len = len(crib_indices)
        if crib_len < 4:
            continue
        
        for start_pos in range(len(cipher) - crib_len):
            # Extract keystream from crib
            if mode == "sub":
                ks = [(cipher[start_pos + i] - crib_indices[i]) % N for i in range(crib_len)]
            elif mode == "add":
                ks = [(crib_indices[i] - cipher[start_pos + i]) % N for i in range(crib_len)]
            else:  # beaufort
                ks = [(cipher[start_pos + i] + crib_indices[i]) % N for i in range(crib_len)]
            
            # Run Berlekamp-Massey on extracted keystream
            result = berlekamp_massey_gf29(ks)
            if result is None:
                continue
            
            poly, lfsr_len = result
            
            if lfsr_len < 2 or lfsr_len > crib_len // 2:
                continue
            
            # Reconstruct full keystream from LFSR
            # The connection polynomial c means: s[i] = -sum(c[j]*s[i-j] for j=1..L) mod 29
            full_state = list(ks[:lfsr_len])
            full_ks = list(full_state)
            
            for i in range(lfsr_len, len(cipher)):
                new_val = 0
                for j in range(1, lfsr_len + 1):
                    new_val = (new_val - poly[j] * full_ks[i - j]) % N
                full_ks.append(new_val)
            
            # Decrypt entire page
            if mode == "sub":
                plain = [(c - k) % N for c, k in zip(cipher, full_ks)]
            elif mode == "add":
                plain = [(c + k) % N for c, k in zip(cipher, full_ks)]
            else:
                plain = [(k - c) % N for c, k in zip(cipher, full_ks)]
            
            ic = ioc(plain)
            if ic > 1.4:
                bg = bigram_score(plain)
                tg = trigram_hits(plain)
                results.append({
                    'crib': crib_name,
                    'pos': start_pos,
                    'lfsr_len': lfsr_len,
                    'poly': poly[:lfsr_len+1],
                    'init_state': full_state,
                    'ioc': ic,
                    'bigrams': bg,
                    'trigrams': tg,
                    'mode': mode,
                    'sample': to_runeglish(plain[:80]),
                    'score': ic + bg * 0.01 + tg * 0.05,
                })
    
    results.sort(key=lambda x: -x['score'])
    
    if results:
        print(f"  Found {len(results)} candidates with IoC > 1.4")
        for r in results[:10]:
            print(f"    crib={r['crib']} pos={r['pos']} LFSR({r['lfsr_len']}) IoC={r['ioc']:.4f} bg={r['bigrams']} tg={r['trigrams']}")
            print(f"      poly={r['poly']} init={r['init_state']}")
            print(f"      -> {r['sample'][:60]}")
    else:
        print("  No candidates found")
    
    return results

# ── Common cribs for Liber Primus ──────────────────────────────────────────

def word_to_indices(word):
    """Convert a runeglish word to rune indices."""
    indices = []
    pos = 0
    word = word.upper()
    while pos < len(word):
        found = False
        # Try 2-char match first
        if pos + 1 < len(word):
            di = word[pos:pos+2]
            for idx, rg in enumerate(RUNEGLISH):
                if rg == di:
                    indices.append(idx)
                    pos += 2
                    found = True
                    break
        if not found:
            ch = word[pos]
            for idx, rg in enumerate(RUNEGLISH):
                if rg == ch:
                    indices.append(idx)
                    pos += 1
                    found = True
                    break
            if not found:
                pos += 1  # skip unknown
    return indices

# Common cribs from Cicada philosophy
CRIBS = {
    "THE": word_to_indices("THE"),
    "AND": word_to_indices("AND"),
    "WISDOM": word_to_indices("WISDOM"),
    "TRUTH": word_to_indices("TRUTH"),
    "DIVINITY": word_to_indices("DIVINITY"),
    "WITHIN": word_to_indices("WITHIN"),
    "COMMAND": word_to_indices("COMMAND"),
    "CONSCIOUSNESS": word_to_indices("CONSCIOUSNESS"),
    "CIRCUMFERENCE": word_to_indices("CIRCUMFERENCE"),
    "CONSUMPTION": word_to_indices("CONSUMPTION"),
    "PARABLE": word_to_indices("PARABLE"),
    "PILGRIM": word_to_indices("PILGRIM"),
    "FOLLY": word_to_indices("FOLLY"),
    "SHADOWS": word_to_indices("SHADOWS"),
    "CABAL": word_to_indices("CABAL"),
    "DEOR": word_to_indices("DEOR"),
    "SOME": word_to_indices("SOME"),
    "FROM": word_to_indices("FROM"),
    "THIS": word_to_indices("THIS"),
    "THAT": word_to_indices("THAT"),
    "WITH": word_to_indices("WITH"),
    "LIKE": word_to_indices("LIKE"),
    "INSTAR": word_to_indices("INSTAR"),
    "EMERGE": word_to_indices("EMERGE"),
    "SURFACE": word_to_indices("SURFACE"),
    "TUNNEL": word_to_indices("TUNNEL"),
    "FIND": word_to_indices("FIND"),
    "SHED": word_to_indices("SHED"),
}

# ── Main ─────────────────────────────────────────────────────────────────────

def load_page_runes(page_num):
    """Load rune text for a page."""
    rune_path = Path(f"pages/page_{page_num:02d}/runes.txt")
    if rune_path.exists():
        return rune_path.read_text(encoding='utf-8')
    return None

def main():
    base = Path(__file__).parent.parent
    os.chdir(base)
    
    # Target pages (unsolved)
    target_pages = [28, 15, 20, 21, 22, 27, 29, 30, 40, 41, 42, 43]
    
    all_results = {}
    
    for page_num in target_pages:
        print(f"\n{'='*70}")
        print(f"  PAGE {page_num}")
        print(f"{'='*70}")
        
        text = load_page_runes(page_num)
        if not text:
            print(f"  No rune file found for page {page_num}")
            continue
        
        cipher, seps = extract_runes(text)
        print(f"  Cipher: {len(cipher)} runes, {len(seps)} separators")
        print(f"  Raw IoC: {ioc(cipher):.4f}")
        
        page_results = {}
        
        # ── 1. Alberti Progressive Cipher ──
        print("\n--- Alberti Progressive Cipher ---")
        alberti_results = brute_force_alberti(text)
        if alberti_results:
            print(f"\n  Top 5 Alberti results:")
            for r in alberti_results[:5]:
                print(f"    {r['dir']} letter={r['letter_shift']} space={r['space_shift']} {r['mode']} IoC={r['ioc']:.4f} bg={r['bigrams']} tg={r['trigrams']}")
                print(f"      -> {r['sample'][:60]}")
        page_results['alberti'] = alberti_results
        
        # ── 2. Stream Ciphers ──
        print("\n--- Stream Ciphers (Prime/Fibonacci) ---")
        stream_results = test_streams(cipher, f"P{page_num}")
        page_results['streams'] = stream_results
        
        # ── 3. LFSR(2) Brute Force ──
        if page_num in [28, 15]:  # Only for primary targets (expensive)
            print(f"\n--- LFSR(2) Brute Force (P{page_num}) ---")
            lfsr2_results = brute_force_lfsr_n2(cipher, [("SUB", decrypt_sub)])
            if lfsr2_results:
                print(f"\n  Top 5 LFSR(2) SUB results:")
                for r in lfsr2_results[:5]:
                    print(f"    state={r['state']} taps={r['taps']} IoC={r['ioc']:.4f} bg={r['bigrams']} tg={r['trigrams']}")
                    print(f"      -> {r['sample'][:60]}")
            page_results['lfsr2'] = lfsr2_results
            
            # Also test ADD mode
            print(f"\n--- LFSR(2) Brute Force ADD (P{page_num}) ---")
            lfsr2_add = brute_force_lfsr_n2(cipher, [("ADD", decrypt_add)])
            if lfsr2_add:
                print(f"\n  Top 5 LFSR(2) ADD results:")
                for r in lfsr2_add[:5]:
                    print(f"    state={r['state']} taps={r['taps']} IoC={r['ioc']:.4f} bg={r['bigrams']} tg={r['trigrams']}")
                    print(f"      -> {r['sample'][:60]}")
            page_results['lfsr2_add'] = lfsr2_add
        
        # ── 4. Crib Dragging + Berlekamp-Massey ──
        print(f"\n--- Crib-Drag + Berlekamp-Massey (P{page_num}) ---")
        for mode in ["sub", "add", "beaufort"]:
            crib_results = crib_drag_lfsr(cipher, CRIBS, mode)
            page_results[f'crib_{mode}'] = crib_results
        
        # ── 5. LFSR(3) Random Search (only for P28) ──
        if page_num == 28:
            print(f"\n--- LFSR(3) Random Search (P{page_num}) ---")
            lfsr3_results = smart_lfsr_n3(cipher, [("SUB", decrypt_sub)], sample_size=100)
            if lfsr3_results:
                print(f"\n  Top 5 LFSR(3) results:")
                for r in lfsr3_results[:5]:
                    print(f"    state={r['state']} taps={r['taps']} IoC={r['ioc']:.4f} bg={r['bigrams']} tg={r['trigrams']}")
                    print(f"      -> {r['sample'][:60]}")
            page_results['lfsr3'] = lfsr3_results
        
        all_results[page_num] = page_results
        
        # Only do full analysis on first few pages for speed
        if page_num not in [28, 15]:
            continue
    
    # ── Summary ──
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    
    for page_num, pr in all_results.items():
        print(f"\n  Page {page_num}:")
        best_overall = None
        best_score = 0
        for method, results in pr.items():
            if results and isinstance(results, list) and len(results) > 0:
                top = results[0]
                if isinstance(top, dict) and 'score' in top and top['score'] > best_score:
                    best_score = top['score']
                    best_overall = (method, top)
        
        if best_overall:
            method, top = best_overall
            print(f"    Best: {method} score={top['score']:.4f} IoC={top['ioc']:.4f}")
            if 'sample' in top:
                print(f"    Text: {top['sample'][:60]}")
        else:
            print(f"    No promising results")

if __name__ == "__main__":
    main()
