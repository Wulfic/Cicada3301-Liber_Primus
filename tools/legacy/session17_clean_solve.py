"""
Session 17 — Clean Brute-Force Solver (NO hillclimbing)
========================================================
Approaches:
  1. VALIDATE — Decode P03 with DIVINITY key (confirm our decoder is correct)
  2. FULL DECODE P18/P19 — Apply recovered periodic keys to complete ciphertext
  3. P02 CONSTRAINED SEARCH — Word-boundary + known-crib constraint propagation
  4. P21-54 PHRASE ATTACK — Find LP phrases directly, avoid word-salad trap
  5. P20 NON-PRIME KEY DERIVATION — Test LP solved text as running key for non-prime stream

Run:  python Tools/session17_clean_solve.py
"""

import os, sys, json, re, itertools
from collections import defaultdict, Counter

# ─── Gematria Primus ────────────────────────────────────────────────────────
RUNE_TO_IDX = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,  'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,
    'ᚻ': 8,  'ᚾ': 9,  'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LATIN = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA',
]
N = 29

def rune_to_idx(r): return RUNE_TO_IDX.get(r, -1)
def idx_to_lat(i): return IDX_TO_LATIN[i % N]

def parse_runes(path):
    """Return list of (rune_index, is_separator, char) tuples.
    Separators: - . / & $ (not encrypted). Skips non-rune chars.
    Ignores lines that are metadata (contain Latin alpha chars before runes == Note lines).
    Also handles • (bullet, U+2022) as word separator for old-format files.
    """
    tokens = []
    for raw_line in open(path, encoding='utf-8'):
        line = raw_line.rstrip('\n')
        # Skip metadata lines: lines that contain ASCII letters a-z/A-Z mixed with runes
        # A cipher line should be only runes + separators + punctuation
        ascii_alpha = sum(1 for c in line if c.isascii() and c.isalpha())
        rune_count  = sum(1 for c in line if c in RUNE_TO_IDX)
        if ascii_alpha > 0 and rune_count == 0:
            continue  # Pure metadata line, skip
        if ascii_alpha > 2 and rune_count < ascii_alpha:
            continue  # Mostly English text (e.g. "Note: Every clear..."), skip
        for ch in line:
            if ch in RUNE_TO_IDX:
                tokens.append(('rune', rune_to_idx(ch)))
            elif ch in '-./&$\n\u2022':  # include bullet • as word separator
                tokens.append(('sep', '-' if ch == '\u2022' else ch))
            # else: ignore spaces, etc.
    return tokens

def tokens_to_rune_list(tokens):
    """Extract just the rune indices from tokens."""
    return [v for t, v in tokens if t == 'rune']

def decrypt_sub(cipher, key):
    """Vigenère SUB: plain = (cipher - key) % 29"""
    k = len(key)
    return [(c - key[i % k]) % N for i, c in enumerate(cipher)]

def decrypt_add(cipher, key):
    """Vigenère ADD: plain = (cipher + key) % 29"""
    k = len(key)
    return [(c + key[i % k]) % N for i, c in enumerate(cipher)]

def decrypt_beaufort(cipher, key):
    """Beaufort: plain = (key - cipher) % 29"""
    k = len(key)
    return [(key[i % k] - c) % N for i, c in enumerate(cipher)]

def indices_to_text(idxs):
    """Convert GP indices to Latin string."""
    return ''.join(IDX_TO_LATIN[i] for i in idxs)

def decrypt_sub_fskip(cipher_tokens, key):
    """Vigenère SUB with F-skip rule.
    F-skip: if plaintext would be F(0), consume cipher F literally, DO NOT advance key pos.
    Returns list of plain indices (no separators).
    """
    k = len(key)
    plain = []
    key_pos = 0
    for t, v in cipher_tokens:
        if t != 'rune':
            continue
        if v == 0:  # Cipher rune is ᚠ — literal F, skip key
            plain.append(0)
            # key_pos does NOT advance
        else:
            p = (v - key[key_pos % k]) % N
            plain.append(p)
            key_pos += 1
    return plain

# ─── LP vocabulary / scoring ────────────────────────────────────────────────
LP_WORDLIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'wordlist.txt')

def load_lp_wordlist():
    words = set()
    if os.path.exists(LP_WORDLIST_PATH):
        for line in open(LP_WORDLIST_PATH, encoding='utf-8'):
            w = line.strip().upper()
            if w:
                words.add(w)
    # Also add known LP words directly
    for w in [
        'THE','AND','OF','A','TO','IN','IS','IT','YOU','THAT','FOR','ARE','THIS',
        'WITH','ALL','THINGS','BE','NOT','HAVE','FROM','DO','AN','THERE','EACH',
        'YOUR','SELF','INTO','WITHIN','NOTHING','SOME','FOLLOW','TRUTH','WISDOM',
        'SACRED','PRIMES','TOTIENT','FUNCTION','ENCRYPTED','DIVINITY','DIVINE',
        'KNOW','KNOWTHIS','INSTRUCTION','FIND','EXPERIENCE','DEATH','BELIEVE',
        'TEST','KNOWLEDGE','IMPOSE','OTHERS','INSTAR','EMERGE','JOURNEY','END',
        'GREAT','ALONG','WAY','WILL','THROUGH','GOING','WITHIN','BEING','UNTO',
        'ITSELF','COMMAND','OWN','INTELLIGENCE','HOLY','LIVES','LAW','BEING',
        'CIRCUMFERENCE','PRACTICES','THREE','BEHAVIORS','CAUSE','LOSS','CONSUMPTION',
        'PRESERVATION','ADHERENCE','AMASS','WEALTH','BECOME','ATTACHED','OWN','PREPARED',
        'DESTROY','PROGRAM','MIND','REALITY','QUESTION','DISCOVER','DEEP','WEB',
        'EXISTS','PAGE','HASHES','DUTY','PILGRIM','SEEK','OUT','SAME','AS','WHAT',
        'TRUE','EITHER','WORDS','NUMBERS','CHANGE','BOOK','EXCEPT','EDIT','MESSAGE',
        'CONTAINED','BUT','WHO','HERE','NECESSARY','ONE','EASY','TRIP','STRUGGLE',
        'SUFFERING','INNOCENCE','ILLUSIONS','CERTAINTY','ULTIMATELY','DISCOVER',
        'SHAPE','OURSELVES','REALITIES','DEEP','OUTSIDE','LIKE','ONLY','MAY',
        'PARABLE','INSTAR','TUNNELING','SURFACE','MUST','SHED','FIND','LIBER','PRIMUS',
        'EPILOGUE','WITHIN','CHAPTER','INTUS','REARRANGING','NUMBERS','SHOW','PATH',
        'DEOR','BEING','SWORN','OATH','ABOVE','ASTARTING','JILT','MY','WISHING',
        'COERCED','NOT','CAN','SEE','HER','HIS','THEIR','THEM','THEMSELVES',
        'PERSON','MAN','WOMAN','MASTER','STUDENT','VOICE','HEAD','ASKED','SAID',
        'EXPLAINED','LESSON','DURING','FOUR','UNREASONABLE','THINGS','EACH','DAY',
        'SHADOWS','AETHEREAL','BUFFERS','VOID','CARNAL','OBSCURA','FORM','MOBIUS',
        'ANALOG','MOURNFUL','CABAL','SUOID',
    ]:
        words.add(w)
    return words

LP_WORDS = load_lp_wordlist()

def lp_score_words(text):
    """Score by LP word matches (space or concatenation aware)."""
    # First try splitting by spaces/word boundaries
    parts = re.findall(r'[A-Z]+', text.upper())
    score = sum(1 for p in parts if p in LP_WORDS)
    # Also scan for LP words as substrings (handles concatenated text)
    t = text.upper()
    for w in LP_WORDS:
        if len(w) >= 4:
            score += t.count(w)
    return score

def lp_score_phrases(text, min_len=3):
    """Count occurrences of known LP phrases (n-grams) in text."""
    LP_PHRASES = [
        'BELIEVE NOTHING', 'TEST THE KNOWLEDGE', 'FIND YOUR TRUTH',
        'EXPERIENCE YOUR DEATH', 'ALL THINGS SHOULD BE ENCRYPTED',
        'THE PRIMES ARE SACRED', 'THE TOTIENT FUNCTION',
        'QUESTION ALL THINGS', 'COMMAND YOUR OWN SELF',
        'EACH INTELLIGENCE IS HOLY', 'FOR ALL THAT LIVES IS HOLY',
        'YOU ARE A BEING', 'YOU ARE A LAW UNTO YOURSELF',
        'JOURNEY DEEP WITHIN', 'LIKE THE INSTAR',
        'WELCOME PILGRIM', 'GREAT JOURNEY', 'END OF ALL THINGS',
        'ALONG THE WAY', 'PROGRAM YOUR MIND', 'PROGRAM REALITY',
        'THE DEEP WEB', 'SAME AS THAT WHICH', 'SAME AS THAT',
        'THE OTHER SIDE', 'WITH A GREAT', 'THE SONG',
        'REARRANGING THE PRIMES', 'PATH TO THE DEOR',
        'BEING OF ALL', 'SWORN TO THE ONE',
        'LOSS OF DIVINITY', 'SOME WISDOM', 'AN INSTRUCTION',
        'A WARNING', 'A KOAN', 'SOME WISDOM',
        'KNOW THIS', 'DO NOT', 'NOT AN EASY',
        'WITHIN AND', 'DEEP WITHIN', 'THE INSTAR',
        'SHED OUR OWN CIRCUMFERENCES', 'DIVINITY WITHIN',
        'YOU WILL FIND', 'AN END TO ALL',
    ]
    score = 0
    t = text.upper()
    for phrase in LP_PHRASES:
        if phrase in t:
            score += len(phrase.split())
    return score

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: VALIDATE — Decode P03 with key DIVINITY (known correct)
# ─────────────────────────────────────────────────────────────────────────────
def test1_validate_p03():
    print("=" * 70)
    print("TEST 1: VALIDATE — P03 with DIVINITY key (must match known plaintext)")
    print("=" * 70)

    p03_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'page_03', 'runes.txt')
    if not os.path.exists(p03_path):
        print("ERROR: pages/page_03/runes.txt not found")
        return

    DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]  # DIVINITY in GP indices
    tokens = parse_runes(p03_path)
    cipher_runes = tokens_to_rune_list(tokens)

    # Decode SUB with F-skip
    plain = decrypt_sub_fskip(tokens, DIVINITY)
    text = indices_to_text(plain)

    # Known first ~50 chars: WELCOMEP ILGRIMTOTHEGREATEOURNEY...
    # (word separators stripped, so no spaces)
    expected_fragment = "WELCOMEPILGRIMTOTHEGREATJOURNEY"
    if expected_fragment in text:
        print(f"  [PASS] '{expected_fragment}' found in decoded P03")
    else:
        # Try without F-skip
        plain2 = decrypt_sub(cipher_runes, DIVINITY)
        text2 = indices_to_text(plain2)
        if expected_fragment in text2:
            print(f"  [PASS no-fskip] '{expected_fragment}' found in decoded P03")
            text = text2
        else:
            print(f"  [FAIL] Expected '{expected_fragment}' not found")
            print(f"  Got (first 80): {text[:80]}")
            print(f"  No-fskip (first 80): {text2[:80]}")

    # Show word-boundary decode
    print(f"\n  Full P03 decode (first 120 chars):")
    print(f"  {text[:120]}")
    ws = lp_score_words(text)
    ps = lp_score_phrases(text)
    print(f"  Word score={ws}, Phrase score={ps}\n")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: FULL DECODE P18 with recovered 53-element key
# ─────────────────────────────────────────────────────────────────────────────
def test2_decode_p18():
    print("=" * 70)
    print("TEST 2: FULL DECODE P18 with known 53-element key")
    print("=" * 70)

    p18_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'page_18', 'runes.txt')
    if not os.path.exists(p18_path):
        print("ERROR: pages/page_18/runes.txt not found"); return

    # P18 key (53 indices from MASTER_TRACKER, recovered by crib dragging)
    KEY18 = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16,
             9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24,
             22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]

    tokens = parse_runes(p18_path)
    cipher_runes = tokens_to_rune_list(tokens)
    print(f"  P18 total runes: {len(cipher_runes)}, key length: {len(KEY18)}")

    for mode_name, mode_fn in [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAUFORT', decrypt_beaufort)]:
        plain = mode_fn(cipher_runes, KEY18)
        text = indices_to_text(plain)
        ws = lp_score_words(text)
        ps = lp_score_phrases(text)
        print(f"\n  [{mode_name}] word={ws} phrase={ps}")
        print(f"  {text[:100]}")
        # Check for known fragment
        frags = ['BEING OF ALL', 'THE OATH IS SWORN', 'WITHIN THE ABOVE']
        for f in frags:
            if f in text:
                print(f"  [FOUND] Known fragment: '{f}'")

    # Try with word-boundary reconstruction
    print("\n  Reconstructing with word boundaries (SUB mode):")
    plain_sub = decrypt_sub(cipher_runes, KEY18)
    text_sub = indices_to_text(plain_sub)

    # Rebuild with separators from token list
    result_parts = []
    rune_idx = 0
    for t, v in tokens:
        if t == 'rune':
            result_parts.append(IDX_TO_LATIN[plain_sub[rune_idx]])
            rune_idx += 1
        else:
            result_parts.append(' ' if v == '-' else v)
    full_text = ''.join(result_parts)
    print(f"  {full_text[:200]}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: FULL DECODE P19 with recovered 47-element key
# ─────────────────────────────────────────────────────────────────────────────
def test3_decode_p19():
    print("=" * 70)
    print("TEST 3: FULL DECODE P19 with known 47-element key")
    print("=" * 70)

    p19_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'page_19', 'runes.txt')
    if not os.path.exists(p19_path):
        print("ERROR: pages/page_19/runes.txt not found"); return

    # P19 key (47 indices from MASTER_TRACKER, ADD mode)
    KEY19 = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8,
             22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4,
             5, 18, 23, 28, 28, 28, 28]

    tokens = parse_runes(p19_path)
    cipher_runes = tokens_to_rune_list(tokens)
    print(f"  P19 total runes: {len(cipher_runes)}, key length: {len(KEY19)}")

    for mode_name, mode_fn in [('ADD', decrypt_add), ('SUB', decrypt_sub), ('BEAUFORT', decrypt_beaufort)]:
        plain = mode_fn(cipher_runes, KEY19)
        text = indices_to_text(plain)
        ws = lp_score_words(text)
        ps = lp_score_phrases(text)
        print(f"\n  [{mode_name}] word={ws} phrase={ps}")
        print(f"  {text[:120]}")
        frags = ['REARRANGING THE PRIMES', 'PATH TO THE DEOR', 'WISHING NOT COERCED', 'STARING JILT']
        for f in frags:
            if f in text:
                print(f"  [FOUND] Known fragment: '{f}'")

    # Try with word boundaries
    print("\n  P19 reconstruction with word separators (ADD mode):")
    plain_add = decrypt_add(cipher_runes, KEY19)
    result_parts = []
    rune_idx = 0
    for t, v in tokens:
        if t == 'rune':
            result_parts.append(IDX_TO_LATIN[plain_add[rune_idx]])
            rune_idx += 1
        else:
            result_parts.append(' ' if v == '-' else v)
    full = ''.join(result_parts)
    print(f"  {full[:400]}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: P02 WORD-BOUNDARY CONSTRAINED SEARCH
# ─────────────────────────────────────────────────────────────────────────────
def test4_p02_constrained():
    print("=" * 70)
    print("TEST 4: P02 WORD-BOUNDARY CONSTRAINED KEY SEARCH")
    print("=" * 70)

    p02_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'page_02', 'runes.txt')
    if not os.path.exists(p02_path):
        print("ERROR: pages/page_02/runes.txt not found"); return

    KEY_LEN = 43
    # Known partial P02 key (positions 0-42)
    KNOWN_KEY = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20,
                 1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9,
                 22, 26, 22, 15]

    tokens = parse_runes(p02_path)
    cipher_runes = tokens_to_rune_list(tokens)
    print(f"  P02 rune count: {len(cipher_runes)}, key length: {KEY_LEN}")

    # Step 1: Show current decode with known key
    for mode_name, mode_fn in [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAUFORT', decrypt_beaufort)]:
        plain = mode_fn(cipher_runes, KNOWN_KEY)
        text = indices_to_text(plain)
        ws = lp_score_words(text)
        ps = lp_score_phrases(text)
        print(f"\n  [{mode_name}] word={ws} phrase={ps}")
        print(f"  {text[:80]}")
        frags = ['SAME AS THAT', 'THE OTHER', 'WITH A', 'THE SONG', 'CHAPTER', 'INTUS']
        for f in frags:
            if f in text:
                print(f"  ✅ Found known fragment: '{f}'")

    # Step 2: Reconstruct with word boundaries (SUB mode, best mode so far)
    print("\n  P02 word-boundary reconstruction (SUB mode):")
    plain_sub = decrypt_sub(cipher_runes, KNOWN_KEY)
    result_parts = []
    rune_idx = 0
    for t, v in tokens:
        if t == 'rune':
            result_parts.append(IDX_TO_LATIN[plain_sub[rune_idx]])
            rune_idx += 1
        elif v == '-':
            result_parts.append(' ')
        elif v == '.':
            result_parts.append('. ')
        elif v in '&$':
            result_parts.append(f'\n[{v}]\n')
        elif v == '\n':
            result_parts.append('\n')
    full = ''.join(result_parts)
    print(f"  {full}")

    # Step 3: Singleton constraint analysis
    print("\n  Singleton constraint analysis (single-rune words must be I or A):")
    words = []
    current_word = []
    for t, v in tokens:
        if t == 'rune':
            current_word.append(v)
        else:
            if current_word:
                words.append(current_word[:])
                current_word = []
    if current_word:
        words.append(current_word)

    # Track rune positions per word
    rpos = 0
    constrained_positions = {}  # key_pos -> set of allowed values
    for w in words:
        if len(w) == 1:
            c = w[0]
            kp = rpos % KEY_LEN
            # plain = (c - key[kp]) % 29 must be 10 (I) or 24 (A)
            candidates = set()
            for target in [10, 24]:
                candidates.add((c - target) % N)
            if kp not in constrained_positions:
                constrained_positions[kp] = candidates
            else:
                constrained_positions[kp] &= candidates  # intersection
            print(f"    Rune pos {rpos:3d} key pos {kp:2d} cipher={c:2d} → key must be one of {sorted(constrained_positions[kp])} (word=I or A)")
        rpos += len(w)

    print(f"\n  Total constrained key positions from singletons: {len(constrained_positions)}")

    # Step 4: Show which key positions are CONFIRMED vs UNCERTAIN
    print("\n  Key position analysis:")
    # Check known key consistency with singletons
    conflicts = 0
    for kp, allowed in constrained_positions.items():
        actual = KNOWN_KEY[kp]
        match = actual in allowed
        if not match:
            print(f"    ⚠️  Key pos {kp:2d}: known={actual}, allowed={sorted(allowed)} — CONFLICT")
            conflicts += 1
        else:
            # Find what the plaintext is
            plain_val = None
            rpos2 = 0
            for w in words:
                if len(w) == 1 and rpos2 % KEY_LEN == kp:
                    plain_val = (w[0] - actual) % N
                    break
                rpos2 += len(w)
            ltr = idx_to_lat(actual) if actual < N else '?'
    if conflicts == 0:
        print("    [OK] No conflicts -- singleton constraints consistent with known key")

    # Step 5: Crib-based key position locking and extension
    print("\n  Crib-based key extension for P02:")
    CRIBS = [
        (list(map(lambda c: 'F U U N C T I O N'.split().index(c) if c in 'FUUNCTION' else
                  [0,1,1,9,5,16,10,3,9],
                  'FUNCTION')), 'FUNCTION'),  # placeholder
    ]
    # Build proper crib list using GP indices
    CRIB_WORDS = {
        'SAME': [15, 24, 19, 18],
        'AS': [24, 15],
        'THAT': [16, 8, 24, 16],
        'WHICH': [7, 8, 10, 5, 8],
        'THE': [2, 8, 18],
        'OTHER': [3, 2, 8, 4],
        'WITH': [7, 10, 2, 8],
        'SONG': [15, 3, 21, 6],
        'CHAPTER': [5, 8, 24, 13, 16, 18, 4],
        'INTUS': [10, 9, 16, 1, 15],
        'FUNCTION': [0, 1, 9, 5, 16, 10, 3, 9],
        'PRIMES': [13, 4, 10, 19, 18, 15],
        'SACRED': [15, 24, 5, 4, 18, 23],
        'TOTIENT': [16, 3, 16, 10, 18, 9, 16],
        'WISDOM': [7, 10, 15, 23, 3, 19],
        'INSTRUCTION': [10, 9, 15, 16, 4, 1, 5, 16, 10, 3, 9],
        'WELCOME': [7, 18, 20, 5, 3, 19, 18],
        'PILGRIM': [13, 10, 20, 6, 4, 10, 19],
        'JOURNEY': [11, 3, 1, 4, 9, 18, 26],
        'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
        'WITHIN': [7, 10, 2, 10, 9],
        'TRUTH': [16, 4, 1, 2, 8],
    }

    # Count how many key positions each crib would lock
    print("\n  Testing LP cribs against cipher word lengths for P02:")
    rpos = 0
    word_starts = []
    for w in words:
        word_starts.append((rpos, len(w)))
        rpos += len(w)

    locked_key = list(KNOWN_KEY)  # Start from known key
    new_locks = {}

    for ws_pos, wlen in word_starts:
        for crib_word, crib_idxs in CRIB_WORDS.items():
            if len(crib_idxs) == wlen:
                # This crib fits this word slot
                # Derive key values this crib would require
                candidate_key_vals = {}
                consistent = True
                for i, ci in enumerate(crib_idxs):
                    global_pos = ws_pos + i
                    kp = global_pos % KEY_LEN
                    # SUB mode: plain = (cipher - key) % 29 → key = (cipher - plain) % 29
                    cipher_val = cipher_runes[global_pos] if global_pos < len(cipher_runes) else None
                    if cipher_val is None:
                        consistent = False; break
                    derived_key = (cipher_val - ci) % N
                    if kp in candidate_key_vals and candidate_key_vals[kp] != derived_key:
                        consistent = False; break  # Contradicts itself
                    # Check against locked key
                    if locked_key[kp] != derived_key and any(locked_key[p] != 0 for p in range(KEY_LEN)):
                        pass  # Don't break yet, just note
                    candidate_key_vals[kp] = derived_key

                if consistent and len(candidate_key_vals) >= 1:
                    # Check against known key
                    matches = sum(1 for kp, kv in candidate_key_vals.items() if locked_key[kp] == kv)
                    if matches == len(candidate_key_vals):
                        print(f"    [ALL MATCH] '{crib_word}' @ word pos {ws_pos:3d} (len={wlen}) -- {matches} key positions match known key")
                    elif matches >= len(candidate_key_vals) // 2:
                        print(f"    [PARTIAL]   '{crib_word}' @ word pos {ws_pos:3d} (len={wlen}) -- {matches}/{len(candidate_key_vals)} key positions match")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: P21-54 PHRASE DETECTION ATTACK
# Direct search for complete LP PHRASES in decoded text using known best key
# ─────────────────────────────────────────────────────────────────────────────
def test5_p2154_phrase_attack():
    print("=" * 70)
    print("TEST 5: P21-54 PHRASE DETECTION ATTACK")
    print("   (Using best checkpoint key — looking for complete LP phrases)")
    print("=" * 70)

    checkpoint_path = os.path.join(os.path.dirname(__file__), '..', 'data',
                                    'gpu_hill_checkpoint_gpu1_v4.json')
    if not os.path.exists(checkpoint_path):
        print("  Checkpoint not found, skipping"); return

    with open(checkpoint_path, encoding='utf-8') as f:
        ckpt = json.load(f)

    score = ckpt.get('score', 0)
    canonical_key = ckpt.get('canonical_key', ckpt.get('best_key', ckpt.get('key', [])))
    print(f"  Checkpoint score: {score}, canonical key length: {len(canonical_key)}")

    LP_SENTENCES = [
        'BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE',
        'TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH',
        'ALL THINGS SHOULD BE ENCRYPTED KNOW THIS',
        'THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED',
        'QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF',
        'COMMAND YOUR OWN SELF EACH INTELLIGENCE IS HOLY',
        'FOR ALL THAT LIVES IS HOLY',
        'WELCOME PILGRIM TO THE GREAT JOURNEY',
        'LIKE THE INSTAR TUNNELING TO THE SURFACE',
        'PROGRAM YOUR MIND PROGRAM REALITY',
        'YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF',
        'JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE',
        'IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE',
        'AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY',
        'SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED',
        'THE LOSS OF DIVINITY',
        'REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR',
    ]

    # Load a few pages and test
    for pg in [21, 22, 23, 24, 25, 26, 27, 28, 30, 32]:
        pg_path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{pg:02d}', 'runes.txt')
        if not os.path.exists(pg_path):
            continue
        tokens = parse_runes(pg_path)
        cipher_runes = tokens_to_rune_list(tokens)
        if not cipher_runes or not canonical_key:
            continue

        # Try SUB and ADD with the canonical key
        best_ps = 0
        best_text = ''
        best_mode = ''
        for mode_name, mode_fn in [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAUFORT', decrypt_beaufort)]:
            plain = mode_fn(cipher_runes, canonical_key)
            text = indices_to_text(plain)
            ps = lp_score_phrases(text)
            ws = lp_score_words(text)
            if ps > best_ps or (ps == best_ps and ws > lp_score_words(best_text)):
                best_ps = ps
                best_text = text
                best_mode = mode_name

        found_sents = [s for s in LP_SENTENCES if s in best_text]
        print(f"\n  Page {pg:02d} [{best_mode}] phrase_score={best_ps}")
        if found_sents:
            for s in found_sents:
                print(f"    [!!!] FULL SENTENCE: '{s}'")
        else:
            # Show partial matches
            best_partial = ''
            best_partial_len = 0
            for sent in LP_SENTENCES:
                words = sent.split()
                for i in range(len(words)):
                    for j in range(i+3, len(words)+1):
                        chunk = ' '.join(words[i:j])
                        if chunk in best_text and len(chunk) > best_partial_len:
                            best_partial = chunk
                            best_partial_len = len(chunk)
            if best_partial:
                print(f"    Best partial match: '{best_partial}'")
            else:
                print(f"    No LP phrase matches (first 60: {best_text[:60]})")


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: P20 Non-Prime Stream — LP1 Solved Text as Running Key
# ─────────────────────────────────────────────────────────────────────────────
def test6_p20_running_key():
    print("=" * 70)
    print("TEST 6: P20 NON-PRIME STREAM — LP Solved Text as Running Key")
    print("=" * 70)

    p20_path = os.path.join(os.path.dirname(__file__), '..', 'pages', 'page_20', 'runes.txt')
    if not os.path.exists(p20_path):
        print("  pages/page_20/runes.txt not found"); return

    tokens = parse_runes(p20_path)
    all_runes = tokens_to_rune_list(tokens)
    print(f"  P20 total runes: {len(all_runes)}")

    # Separate prime-position and non-prime-position runes
    def is_prime(n):
        if n < 2: return False
        if n == 2: return True
        if n % 2 == 0: return False
        for i in range(3, int(n**0.5)+1, 2):
            if n % i == 0: return False
        return True

    # 1-indexed positions (as used in LP prime stream analysis)
    prime_runes = [all_runes[i] for i in range(len(all_runes)) if is_prime(i+1)]
    nonprime_runes = [all_runes[i] for i in range(len(all_runes)) if not is_prime(i+1)]
    print(f"  Prime-pos stream: {len(prime_runes)} runes")
    print(f"  Non-prime stream: {len(nonprime_runes)} runes")

    # LP1 solved plaintext as running key sources
    LP1_TEXTS = {
        'P01': 'AWARNINGBELIEVENOTHINGFROMTHISBOOKEXCEPTWHATYOUKNOWTOBETRUETEST'
               'THEKNOWLEDGEFINDYOURTRUTHEXPERIENCEYOURDEATHDONOTEDITORCHANETHIS'
               'BOOKORTHEMESSAGECONTAINEDWITHINEITHERTHEWORDERSORTHEERNUMBERSFOR'
               'ALLISSACRED',
        'P03': 'WELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOTAN'
               'EASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISNECESSARYONEALONGTHEWAY'
               'YOUWILLFINDANENDTOALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURILLUSIONS'
               'YOURCERTAINTYANDYOURREALITYULTIMATELYYOUWILLDISCOVERANENDTOSELF',
        'P04': 'ITISTHROUGHTHISPILGRIMAGETHATWESHAPEOURSELVESANDOURREALITIESJOURNEY'
               'DEEPWITHINANDYOUVILLARIVEOUTSIDELIKETHEINSTARITISONLY'
               'THROUGHGOINGWITHINTHATWEMAYEMERDEWISDOMYOUAREABEINGUNTOYOURSELF'
               'YOUAREALAWUNTOYOURSELFEACHINTELLIGENCEISHOLYFORALLTHATLIVES'
               'ISHOLYANINSTRUCTIONCOMMANDYOUROWNOSELF',
        'P56_57': 'PARABLELIKETHEINSTARRUNNELLINGTOTHESURFACEWEMUSTOUROWNCIREM'
                  'FERENCESEFINDINGTHEDIVINYWITHINANDEMERGE',
        'DEOR': open(os.path.join(os.path.dirname(__file__), '..', 'data', 'deor_poem.txt'),
                     encoding='utf-8').read().upper().replace('\n', '').replace(' ', '')
                if os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'data', 'deor_poem.txt'))
                else '',
    }

    # Convert LP text to GP indices for running key
    def text_to_gp(text):
        """Convert Latin text to GP indices (best-effort, one char at a time)."""
        result = []
        i = 0
        t = text.upper()
        while i < len(t):
            # Try digraphs first
            if i+1 < len(t):
                dg = t[i:i+2]
                dg_map = {'TH': 2, 'EO': 12, 'NG': 21, 'OE': 22, 'AE': 25, 'IA': 27, 'EA': 28}
                if dg in dg_map:
                    result.append(dg_map[dg])
                    i += 2
                    continue
            c = t[i]
            mono_map = {
                'F': 0, 'U': 1, 'V': 1, 'O': 3, 'R': 4, 'C': 5, 'K': 5,
                'G': 6, 'W': 7, 'H': 8, 'N': 9, 'I': 10, 'J': 11, 'P': 13,
                'X': 14, 'S': 15, 'T': 16, 'B': 17, 'E': 18, 'M': 19, 'L': 20,
                'D': 23, 'A': 24, 'Y': 26,
            }
            if c in mono_map:
                result.append(mono_map[c])
            i += 1
        return result

    target = nonprime_runes  # 646-671 rune non-prime stream

    print(f"\n  Testing LP1 solved text as running key for non-prime stream:")
    print(f"  {'Key Source':<20} {'Mode':<10} {'IoC':>6} {'WScore':>7} {'PScore':>7}  Text (first 60)")
    print(f"  {'-'*20} {'-'*10} {'-'*6} {'-'*7} {'-'*7}  {'-'*60}")

    from math import gcd

    def ioc(idxs):
        if len(idxs) < 2: return 0.0
        cnt = Counter(idxs)
        n = len(idxs)
        return N * sum(v*(v-1) for v in cnt.values()) / (n*(n-1))

    best_results = []

    for src_name, src_text in LP1_TEXTS.items():
        if not src_text: continue
        key_gp = text_to_gp(src_text)
        if len(key_gp) < 50: continue

        for offset in range(0, min(len(key_gp) - len(target), 500), 37):
            k = key_gp[offset:offset+len(target)]
            if len(k) < len(target):
                # Wrap
                while len(k) < len(target):
                    k = k + key_gp
                k = k[:len(target)]

            for mode_name, mode_fn in [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAUFORT', decrypt_beaufort)]:
                plain = mode_fn(target, k)
                text = indices_to_text(plain)
                ic = ioc(plain)
                ws = lp_score_words(text)
                ps = lp_score_phrases(text)
                total = ic * 10 + ws * 0.1 + ps * 0.5
                best_results.append((total, ic, ws, ps, src_name, offset, mode_name, text[:60]))

    best_results.sort(reverse=True)
    for total, ic, ws, ps, src, off, mode, snippet in best_results[:20]:
        print(f"  {src+str(off):<20} {mode:<10} {ic:6.4f} {ws:7d} {ps:7d}  {snippet}")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: P23/P26/P27/P30 ADD mode test with verified_keys.json
# These pages reportedly use ADD mode — test if the verified keys decode them
# ─────────────────────────────────────────────────────────────────────────────
def test7_verified_keys_decode():
    print("=" * 70)
    print("TEST 7: FULL DECODE using verified_keys.json on claimed ADD-mode pages")
    print("=" * 70)

    vk_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'verified_keys.json')
    if not os.path.exists(vk_path):
        print("  verified_keys.json not found"); return

    with open(vk_path, encoding='utf-8') as f:
        vkeys = json.load(f)

    # Pages that reportedly use ADD mode: P23, P26, P27, P30
    # Pages that reportedly use Beaufort: P21, P22, P24, P25, P29
    page_modes = {
        '21': 'BEAUFORT', '22': 'BEAUFORT', '23': 'ADD', '24': 'BEAUFORT',
        '25': 'BEAUFORT', '26': 'ADD', '27': 'ADD', '28': 'SUB',
        '29': 'BEAUFORT', '30': 'ADD',
    }

    print(f"\n  Page  Mode      Key_match  WScore  PScore  First 80 chars")
    print(f"  {'-'*4}  {'-'*8}  {'-'*9}  {'-'*6}  {'-'*6}  {'-'*80}")

    for pg_str, expected_mode in page_modes.items():
        pg_int = int(pg_str)
        pg_path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{pg_int:02d}', 'runes.txt')
        if not os.path.exists(pg_path):
            continue
        if pg_str not in vkeys:
            print(f"  P{pg_int:02d}   no key in verified_keys.json")
            continue

        key = vkeys[pg_str]
        tokens = parse_runes(pg_path)
        cipher_runes = tokens_to_rune_list(tokens)

        # Try all 3 modes
        best_ws = -1; best_mode = ''; best_text = ''
        for mode_name, mode_fn in [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAUFORT', decrypt_beaufort)]:
            plain = mode_fn(cipher_runes, key)
            text = indices_to_text(plain)
            ws = lp_score_words(text)
            ps = lp_score_phrases(text)
            if ws > best_ws:
                best_ws = ws; best_mode = mode_name; best_text = text
                best_ps = ps

        mode_match = 'OK ' if best_mode == expected_mode else '???'
        print(f"  P{pg_int:02d}   {best_mode:<8}  {mode_match}   {best_ws:6d}  {best_ps:6d}  {best_text[:80]}")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: KNOWN PLAINTEXT ATTACK — Derive key if P21-54 plaintext is known LP text
# For each P21-54 cipher page, if the plaintext = known LP text (aligned at some offset),
# the derived key k = (cipher - plain) % 29 would show periodicity (prime period).
# Test: Autocorrelation analysis of derived key stream.
# ─────────────────────────────────────────────────────────────────────────────
def test8_known_plaintext_attack():
    print("=" * 70)
    print("TEST 8: KNOWN PLAINTEXT ATTACK on P21-54")
    print("   (If plain = LP text, derive key and check periodicity)")
    print("=" * 70)

    # Build full LP solved text corpus (GP indices)
    def text_to_gp_strict(text):
        """Convert Latin text to GP indices (monograph only, no digraph folding)."""
        result = []
        mono_map = {
            'F': 0, 'U': 1, 'V': 1, 'T': 16, 'H': 8, 'O': 3, 'R': 4, 'C': 5, 'K': 5,
            'G': 6, 'W': 7, 'N': 9, 'I': 10, 'J': 11, 'P': 13,
            'X': 14, 'S': 15, 'B': 17, 'E': 18, 'M': 19, 'L': 20, 'D': 23, 'A': 24,
            'Y': 26,
        }
        for c in text.upper():
            if c.isalpha() and c in mono_map:
                result.append(mono_map[c])
        return result

    def text_to_gp_digraph(text):
        """Convert Latin text to GP indices preferring digraph encoding."""
        result = []
        i = 0
        t = text.upper()
        while i < len(t):
            if i+1 < len(t):
                dg = t[i:i+2]
                dg_map = {'TH': 2, 'EO': 12, 'NG': 21, 'IN': None, 'EA': 28, 'AE': 25, 'IA': 27, 'OE': 22}
                if dg in dg_map and dg_map[dg] is not None:
                    result.append(dg_map[dg])
                    i += 2
                    continue
            c = t[i]
            mono_map = {
                'F': 0, 'U': 1, 'V': 1, 'O': 3, 'R': 4, 'C': 5, 'K': 5,
                'G': 6, 'W': 7, 'H': 8, 'N': 9, 'I': 10, 'J': 11, 'P': 13,
                'X': 14, 'S': 15, 'T': 16, 'B': 17, 'E': 18, 'M': 19, 'L': 20,
                'D': 23, 'A': 24, 'Y': 26,
            }
            if c in mono_map:
                result.append(mono_map[c])
            i += 1
        return result

    # Full LP1 known plaintext (all solved pages concatenated, no punctuation)
    LP_KNOWN_TEXTS = {
        'LP1_WARNING': 'AWARNINGBELIEVENOTHINGFROMTHISBOOKEXCEPTWHATYOUKNOWTOBETRUETEST'
                       'THEKNOWLEDGEFINDYOURTRUTHEXPERIENCEYOURDEATHDONOTEDITCHANGETHIS'
                       'BOOKORTHEMESSAGECONTAINEDWITHINEITHERTHEWORKSOFORTHENUMBERSFOR'
                       'ALLISSACRED',
        'LP1_CH1_P03': 'WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITIS'
                       'NOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONEALONG'
                       'THEWAYYOUWILLFINDANENDTOALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURIL'
                       'LUSIONSYOURCERTAINTYANDYOURREALITYULTIMATELYYOUWILLDISCOVERANENDTOSELF',
        'LP1_CH1_P04': 'ITISTHROUGHTHISPILGRIMAGETHATWESHAPEOURSELVESANDOURREALITIESJOURNEY'
                       'DEEPWITHINANDYOUWILLARRIVEOUTSIDELIKETHEINSTARITISON'
                       'LYTHROUGHGOINGWITHINTHATWEMAYEMERGEWISDOMYOUAREABEINGUNTOYOURSELFYOU'
                       'AREALAWUNTOYOURSELFEACHINTELLIGENCEISHOLYFORALLTHATLIVES'
                       'ISHOLYANINSTRUCTIONCOMMANDYOUROWNOSELF',
        'LP1_WISDOM':  'SOMEWISDOMTHEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLTHINGS'
                       'SHOULDBEENCRYPTEDKNOWTHIS',
        'LP1_KOAN':    'AKOANAMANDECIDEDTOGOANDSTUDY',
        'LP1_LOSS':    'THELOSSOFDIVINITY THECIRCUMFERENCEPRACTICESTHREEBEHAVIORSWHICHCAUSE'
                       'THELOSSOFDIVINITY CONSUMPTIONPRESERVATIONADHERENCE SOMEWISDOM'
                       'AMASSGREATWEALTHNEVERBECOMEATACHEDTOTHATYOUOWNBEPREPAREDTODESTROY'
                       'ALLTHATYOUOWN ANINSTRUCTIONPROGRAMYOURMINDPROGRAMREALITY',
        'LP1_INSTRUCT': 'ANINSTRUCTIONQUESTIONALLTHINGSDISCOVERYOURTRUTHINSIDEYOURSELF'
                        'FOLLOWYOURTRUTHIMPOSEONOTHERSKNOWTHIS',
        'LP2_CONCAT':   'LIBERPRIMUS AWARNING CHAPTERIINTUS '
                        'WELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOTAN'
                        'EASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISNECESSARYONEALONGTHEWAY'
                        'SOMEWISDOMTHEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLTHINGS'
                        'SHOULDBEENCRYPTEDKNOWTHISQUESTIONALLTHINGSDISCOVERYOURTRUTH'
                        'PARABLELIKETHEINSTAR',
    }

    # Check periodicity of a sequence: Kasiski-style autocorrelation
    def autocorr_ioc(seq, period):
        """IC at a given lag: compare seq[i] vs seq[i+period]."""
        if len(seq) < period + 10:
            return 0.0
        cnt = Counter()
        n = 0
        for i in range(len(seq) - period):
            if seq[i] == seq[i+period]:
                cnt[seq[i]] += 1
                n += 1
        # Fraction matching at this lag (ideal periodic = high)
        return n / (len(seq) - period) if (len(seq) - period) > 0 else 0.0

    def key_period_score(key_stream):
        """Test all prime periods up to 200 for periodicity."""
        best = (0, 0)
        primes_to_test = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113]
        for p in primes_to_test:
            if p >= len(key_stream) // 2:
                break
            score = autocorr_ioc(key_stream, p)
            if score > best[0]:
                best = (score, p)
        return best  # (autocorr_score, period)

    # Load P21-30 cipher pages
    results = []
    test_pages = list(range(21, 35))

    for pg_num in test_pages:
        pg_path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{pg_num:02d}', 'runes.txt')
        if not os.path.exists(pg_path):
            continue
        tokens = parse_runes(pg_path)
        cipher = tokens_to_rune_list(tokens)
        if not cipher or len(cipher) < 30:
            continue

        for pt_name, pt_text in LP_KNOWN_TEXTS.items():
            gp = text_to_gp_digraph(pt_text)
            if len(gp) < 20:
                continue

            # Try all offsets where the text fits
            max_offset = max(0, len(gp) - len(cipher) + 200)
            step = max(1, len(cipher) // 20)  # ~20 offsets
            for off in range(0, min(len(gp) + len(cipher), 2000), step):
                # Build aligned plaintext (wrap if needed)
                plain_gp = []
                for i in range(len(cipher)):
                    plain_gp.append(gp[(off + i) % len(gp)])

                # Derive key for ADD mode: k = (cipher - plain) % 29
                # (SUB: plain = cipher - key → key = cipher - plain)
                # (ADD: plain = cipher + key → key = plain - cipher)
                key_sub = [(cipher[i] - plain_gp[i]) % N for i in range(len(cipher))]
                key_add = [(plain_gp[i] - cipher[i]) % N for i in range(len(cipher))]

                for key_stream, mode in [(key_sub, 'SUB'), (key_add, 'ADD')]:
                    amax, period = key_period_score(key_stream)
                    if amax > 0.25:  # Much higher than random (~1/29 ≈ 0.034)
                        # Verify: apply derived period key to cipher
                        period_key = key_stream[:period]
                        if mode == 'SUB':
                            plain = decrypt_sub(cipher, period_key)
                        else:
                            plain = decrypt_add(cipher, period_key)
                        text = indices_to_text(plain)
                        ws = lp_score_words(text)
                        ps = lp_score_phrases(text)
                        results.append((amax, period, pg_num, pt_name, off, mode, ws, ps, text[:60]))

    if not results:
        print("  No strong periodicity found in any derived key stream.")
        print("  Random autocorrelation baseline: ~0.034 (1/29)")
        print("  Would need autocorr > 0.25 to indicate periodicity")
        # Show the best results even if weak
        weak = []
        for pg_num in test_pages:
            pg_path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{pg_num:02d}', 'runes.txt')
            if not os.path.exists(pg_path): continue
            tokens = parse_runes(pg_path)
            cipher = tokens_to_rune_list(tokens)
            if not cipher or len(cipher) < 30: continue
            for pt_name, pt_text in LP_KNOWN_TEXTS.items():
                gp = text_to_gp_digraph(pt_text)
                if len(gp) < 20: continue
                for off in [0, len(gp)//4, len(gp)//2]:
                    plain_gp = [gp[(off+i)%len(gp)] for i in range(len(cipher))]
                    key_sub = [(cipher[i]-plain_gp[i])%N for i in range(len(cipher))]
                    amax, period = key_period_score(key_sub)
                    weak.append((amax, period, pg_num, pt_name, off, 'SUB'))
        weak.sort(reverse=True)
        print(f"\n  Top 10 best autocorrelation scores (all weak):")
        for amax, period, pg, pt, off, mode in weak[:10]:
            print(f"    P{pg:02d} vs {pt[:20]:<20} offset={off} mode={mode} period={period} autocorr={amax:.4f}")
    else:
        results.sort(reverse=True)
        print(f"\n  [SIGNIFICANT] Found {len(results)} results with autocorr > 0.25:")
        for amax, period, pg, pt, off, mode, ws, ps, snippet in results[:20]:
            print(f"  P{pg:02d} vs {pt[:15]:<15} off={off} mode={mode} period={period} autocorr={amax:.3f} word={ws} phrase={ps}")
            print(f"      Snippet: {snippet}")

    print()



# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: KASISKI + SPLIT-STREAM IoC PERIOD FINDER (no plaintext needed)
# Classic Vigenère period detection directly on every P21-54 page.
# If any page has a periodic key, the split-stream IoC reveals it.
# ─────────────────────────────────────────────────────────────────────────────
def test9_kasiski_ioc():
    print("=" * 70)
    print("TEST 9: KASISKI + SPLIT-STREAM IoC PERIOD FINDER on P21-54")
    print("   (No plaintext needed — looks for period in raw ciphertext)")
    print("=" * 70)

    def ioc_stream(seq):
        """Standard index of coincidence, scaled to N=29."""
        n = len(seq)
        if n < 2: return 0.0
        cnt = Counter(seq)
        return N * sum(v*(v-1) for v in cnt.values()) / (n*(n-1))

    def split_ioc(ciphertext, period):
        """Average IoC of the P streams for a given period."""
        streams = [ciphertext[i::period] for i in range(period)]
        iocs = [ioc_stream(s) for s in streams if len(s) > 1]
        return sum(iocs) / len(iocs) if iocs else 0.0

    def kasiski(ciphertext, gram_len=3):
        """Find repeated n-grams and return GCDs of their distances."""
        from math import gcd
        from functools import reduce
        seq = ciphertext
        n = len(seq)
        distances = []
        seen = {}
        for i in range(n - gram_len):
            gram = tuple(seq[i:i+gram_len])
            if gram in seen:
                dist = i - seen[gram]
                distances.append(dist)
            else:
                seen[gram] = i
        if not distances:
            return {}
        # Count GCDs
        from collections import Counter as C
        gcds = C()
        for d in distances:
            for fac in range(2, d+1):
                if d % fac == 0:
                    gcds[fac] += 1
        return gcds

    PRIMES_TO_TEST = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131]

    for pg_num in list(range(21, 55)):
        pg_path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{pg_num:02d}', 'runes.txt')
        if not os.path.exists(pg_path): continue
        tokens = parse_runes(pg_path)
        cipher = tokens_to_rune_list(tokens)
        if not cipher or len(cipher) < 50: continue

        # Compute IoC for all prime periods
        base_ioc = ioc_stream(cipher)
        best_period = 0
        best_ioc = base_ioc
        period_iocs = []
        for p in PRIMES_TO_TEST:
            if p > len(cipher) // 3:
                break
            si = split_ioc(cipher, p)
            period_iocs.append((si, p))
            if si > best_ioc:
                best_ioc = si
                best_period = p

        period_iocs.sort(reverse=True)

        # Kasiski trigram GCDs
        gcds = kasiski(cipher)
        prime_gcds = [(v, k) for k, v in gcds.items() if k in set(PRIMES_TO_TEST)]
        prime_gcds.sort(reverse=True)

        print(f"\n  P{pg_num:02d} ({len(cipher)} runes)  base_IoC={base_ioc:.4f}")
        print(f"    Top IoC periods: ", end='')
        for si, p in period_iocs[:5]:
            flag = ' ← STRONG' if si > base_ioc * 1.3 else ''
            print(f"period={p}:{si:.4f}{flag}", end='  ')
        print()
        if prime_gcds:
            print(f"    Kasiski top prime GCDs: ", end='')
            for cnt, p in prime_gcds[:5]:
                print(f"p={p}(x{cnt})", end='  ')
            print()

        if best_period and best_ioc > base_ioc * 1.3:
            print(f"    [!!! POSSIBLE PERIOD {best_period} !!!] Split IoC={best_ioc:.4f} vs base={base_ioc:.4f}")

    print()


if __name__ == '__main__':
    import sys
    tests = sys.argv[1:] if len(sys.argv) > 1 else ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    for t in tests:
        if t == '1': test1_validate_p03()
        elif t == '2': test2_decode_p18()
        elif t == '3': test3_decode_p19()
        elif t == '4': test4_p02_constrained()
        elif t == '5': test5_p2154_phrase_attack()
        elif t == '6': test6_p20_running_key()
        elif t == '7': test7_verified_keys_decode()
        elif t == '8': test8_known_plaintext_attack()
        elif t == '9': test9_kasiski_ioc()
