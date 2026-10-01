"""
P02 Known-Plaintext Attack
===========================
Strategy: P02 contains the koan from LP1 pages 06-08 ("A KOAN / A MAN DECIDED
TO GO AND STUDY WITH A MASTER..."). Four known fragments confirm this:
  - "SAME AS THAT"  → "I AM THE SAME AS THAT WHICH I AM STUDYING"
  - "THE OTHER"     → "HE ARRIVED... AND FOUND ANOTHER STUDENT"
  - "WITH A"        → "STUDY WITH A MASTER"
  - "THE SONG"      → "WHAT I AM IS THE SONG" (from the full koan)

Steps:
  1. Decode P06 (Shift 3 + Reversed Gematria: plain = (31 - cipher) % 29) to get koan
  2. Convert koan to GP index sequence
  3. Apply F-skip: positions where cipher=0 → plaintext F, key NOT advanced
  4. Derive key[i%43] = (cipher - plain) % 29 at each non-F position
  5. Check consistency, find conflicts, fill gaps by crib dragging
  6. Show final decoded P02 text
"""

import os, re
from collections import defaultdict, Counter

# ─── Gematria Primus ─────────────────────────────────────────────────────────
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
LATIN_TO_GP = {   # single-char Latin → GP index (multi-char handled separately)
    'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
    'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,
    'D':23,'A':24,'Y':26,
}
DIGRAPH_TO_GP = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
N = 29
KEY_LEN = 43

# Known partial P02 key (from prior crib dragging, session 17 test4 result)
KNOWN_KEY_PARTIAL = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20,
                     1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9,
                     22, 26, 22, 15]

# ─── Helpers ─────────────────────────────────────────────────────────────────
def latin_to_gp(text):
    """Convert English text to list of GP indices. Handles digraphs TH,EO,NG,OE,AE,IA,EA."""
    result = []
    t = text.upper()
    i = 0
    while i < len(t):
        if i + 1 < len(t):
            dg = t[i:i+2]
            if dg in DIGRAPH_TO_GP:
                result.append(DIGRAPH_TO_GP[dg])
                i += 2
                continue
        c = t[i]
        if c in LATIN_TO_GP:
            result.append(LATIN_TO_GP[c])
        i += 1
    return result

def decode_p06(path):
    """Decode P06 runes using Shift 3 + Reversed Gematria: plain = (31 - cipher) % 29.
    P06 uses '•' as word separator. Returns list of (word_latin, gp_indices) pairs."""
    words = []
    current_word = []
    for line in open(path, encoding='utf-8'):
        for ch in line:
            if ch in RUNE_TO_IDX:
                idx = RUNE_TO_IDX[ch]
                plain_idx = (31 - idx) % N
                current_word.append(plain_idx)
            elif ch in '•\n/':
                if current_word:
                    words.append(current_word[:])
                    current_word = []
            elif ch in '"':  # skip quote marks
                pass
    if current_word:
        words.append(current_word)
    return words

def parse_p02_raw(path):
    """Parse P02 cipher: returns list of (is_rune, value) pairs.
    is_rune=True: value=GP index
    is_rune=False: value=separator character
    """
    tokens = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        ascii_alpha = sum(1 for c in line if c.isascii() and c.isalpha())
        rune_count  = sum(1 for c in line if c in RUNE_TO_IDX)
        if ascii_alpha > 0 and rune_count == 0: continue
        if ascii_alpha > 2 and rune_count < ascii_alpha: continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                tokens.append((True, RUNE_TO_IDX[ch]))
            elif ch in '-./&$':
                tokens.append((False, ch))
    return tokens

def get_cipher_sequence(tokens):
    """Extract just the cipher GP indices from token list."""
    return [v for is_rune, v in tokens if is_rune]

# ─── F-skip Aware Decoder ────────────────────────────────────────────────────
def decode_fskip(cipher, key, mode='SUB'):
    """Decode with F-skip rule: cipher[i]==0 → output F(0) without advancing key counter."""
    plain = []
    ki = 0
    for c in cipher:
        if c == 0:  # Literal F — F-skip
            plain.append(0)
        else:
            kv = key[ki % len(key)]
            if mode == 'SUB':
                p = (c - kv) % N
            elif mode == 'ADD':
                p = (c + kv) % N
            else:  # BEAUFORT
                p = (kv - c) % N
            plain.append(p)
            ki += 1
    return plain

def derive_key_fskip(cipher, plain, key_len, mode='SUB'):
    """Given cipher and plaintext, derive the key values (F-skip aware).
    Returns dict: key_pos → key_value (only for non-F positions).
    Also returns conflicts: key_pos → set of conflicting values.
    """
    key_map = {}   # key_pos → key_value (most voted)
    votes = defaultdict(Counter)   # key_pos → {key_val: count}
    ki = 0
    for pos, (c, p) in enumerate(zip(cipher, plain)):
        if c == 0:  # F-skip: cipher is F, plain is F, no key used
            continue
        kp = ki % key_len
        if mode == 'SUB':
            kv = (c - p) % N
        elif mode == 'ADD':
            kv = (p - c) % N
        else:  # BEAUFORT
            kv = (p + c) % N
        votes[kp][kv] += 1
        ki += 1
    # Determine best vote per key position
    for kp, cnts in votes.items():
        best = cnts.most_common(1)[0]
        key_map[kp] = best[0]
    return key_map, votes

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p02_path = os.path.join(base, 'pages', 'page_02', 'runes.txt')
    p06_path = os.path.join(base, 'pages', 'page_06', 'runes.txt')

    if not os.path.exists(p02_path):
        print("ERROR: pages/page_02/runes.txt not found"); return
    if not os.path.exists(p06_path):
        print("ERROR: pages/page_06/runes.txt not found"); return

    # ─── Step 1: Decode P06 to recover koan text ───────────────────────────
    print("=" * 70)
    print("STEP 1: DECODE P06 (Shift 3 + Reversed Gematria)")
    print("=" * 70)
    p06_words = decode_p06(p06_path)
    koan_text = ' '.join(''.join(IDX_TO_LATIN[i] for i in w) for w in p06_words)
    print(f"P06 decoded ({len(p06_words)} words):")
    print(koan_text)
    print()
    # Build flat GP sequence from koan (the expected plaintext)
    koan_gp = [idx for w in p06_words for idx in w]
    print(f"P06 total runes (GP): {len(koan_gp)}")
    print()

    # ─── Step 2: Parse P02 cipher ──────────────────────────────────────────
    print("=" * 70)
    print("STEP 2: PARSE P02 CIPHER")
    print("=" * 70)
    tokens = parse_p02_raw(p02_path)
    cipher = get_cipher_sequence(tokens)
    print(f"P02 cipher: {len(cipher)} runes")
    F_positions = [i for i, c in enumerate(cipher) if c == 0]
    print(f"F-skip rune positions in cipher: {F_positions} ({len(F_positions)} total)")
    # Count how many non-F runes there are
    non_f_count = len(cipher) - len(F_positions)
    print(f"Non-F rune positions (use key): {non_f_count}")
    print()

    # ─── Step 3: Match P02 cipher to P06 koan plaintext ───────────────────
    print("=" * 70)
    print("STEP 3: KNOWN-PLAINTEXT ATTACK — P02 cipher × P06 koan")
    print("=" * 70)

    # We need to align P06 koan with P02 cipher.
    # P02 might not start at the beginning of the koan, or they may match perfectly.
    # Strategy: try all sub-sequence offsets of koan_gp vs cipher, find best alignment
    best_score = -1
    best_offset = 0
    for offset in range(max(0, len(koan_gp) - len(cipher) + 1)):
        # Extract koan slice matching cipher length
        koan_slice = koan_gp[offset:offset + len(cipher)]
        if len(koan_slice) < len(cipher): break
        # Derive key under SUB mode (best for P02)
        key_map, votes = derive_key_fskip(cipher, koan_slice, KEY_LEN, 'SUB')
        # Consistency score: sum of vote fractions (1.0 = unanimously consistent)
        consistency = sum(cnts.most_common(1)[0][1] for kp, cnts in votes.items())
        total_votes = sum(sum(cnts.values()) for cnts in votes.values())
        score = consistency / total_votes if total_votes else 0
        if score > best_score:
            best_score = score
            best_offset = offset
            best_koan_slice = koan_slice[:]
            best_key_map = key_map
            best_votes = votes

    print(f"Best koan offset: {best_offset} (consistency {best_score:.4f})")
    koan_text_slice = ' '.join(''.join(IDX_TO_LATIN[i] for i in koan_gp[best_offset:best_offset+len(cipher)]).split())
    print(f"Koan slice used: {koan_text_slice[:200]}")
    print()

    # ─── Step 4: Show derived key ──────────────────────────────────────────
    print("=" * 70)
    print("STEP 4: DERIVED KEY ANALYSIS")
    print("=" * 70)
    derived_key = [best_key_map.get(kp, -1) for kp in range(KEY_LEN)]
    print(f"Derived key: {derived_key}")
    print()

    # Show conflicts (positions where more than one value was voted)
    print("Key position consistency:")
    conflicts = 0
    for kp in range(KEY_LEN):
        cnts = best_votes.get(kp, Counter())
        total = sum(cnts.values())
        if total == 0:
            print(f"  pos {kp:2d}: NO DATA")
            continue
        dominant = cnts.most_common(1)[0]
        frac = dominant[1] / total
        all_vals = sorted(cnts.items(), key=lambda x: -x[1])
        if frac < 1.0:
            print(f"  pos {kp:2d}: {dominant[0]:2d} ({frac:.0%}) CONFLICT — also: {[(v,c) for v,c in all_vals[1:]]} total_votes={total}")
            conflicts += 1
        else:
            pass  # Clean position, skip verbose output
    print(f"Total key positions with conflicts: {conflicts}/{KEY_LEN}")
    print()

    # Compare with known partial key
    print("Comparison with known partial key:")
    for kp in range(KEY_LEN):
        known = KNOWN_KEY_PARTIAL[kp]
        derived = best_key_map.get(kp, -1)
        match = "✅" if known == derived else f"⚠️  known={known}, derived={derived}"
        print(f"  pos {kp:2d}: derived={derived:3d}  {match}")
    print()

    # ─── Step 5: Build best complete key ──────────────────────────────────
    print("=" * 70)
    print("STEP 5: BUILD COMPLETE KEY + DECODE P02")
    print("=" * 70)

    # For each key position, prefer derived key (has the koan evidence) over
    # the old partial key where they differ, UNLESS we have very low vote counts
    complete_key = list(derived_key)
    for kp in range(KEY_LEN):
        if complete_key[kp] == -1:
            # No data from koan — fall back to old partial key
            complete_key[kp] = KNOWN_KEY_PARTIAL[kp]
            print(f"  pos {kp:2d}: using fallback KNOWN_KEY_PARTIAL[{kp}] = {KNOWN_KEY_PARTIAL[kp]}")
        elif KNOWN_KEY_PARTIAL[kp] != complete_key[kp]:
            # Conflict between derived and old — report
            cn = best_votes.get(kp, Counter())
            total = sum(cn.values())
            dom = cn.most_common(1)[0]
            kept = complete_key[kp]
            print(f"  pos {kp:2d}: koan→{complete_key[kp]} vs old_key→{KNOWN_KEY_PARTIAL[kp]} (votes={dom[1]}/{total}) → keeping koan-derived={kept}")

    print()
    print(f"Complete key: {complete_key}")
    print()

    # Now decode P02 with this complete key, F-skip
    plain = decode_fskip(cipher, complete_key, 'SUB')
    plain_text = ''.join(IDX_TO_LATIN[i] for i in plain)
    print("Flat decoded text:")
    print(plain_text[:400])
    print()

    # Formatted with word boundaries
    print("Word-boundary formatted decode (F-skip aware):")
    plain_ki = 0
    formatted = []
    for is_rune, val in tokens:
        if is_rune:
            c = val
            if c == 0:  # F-skip literal
                formatted.append('F')
            else:
                p = (c - complete_key[plain_ki % KEY_LEN]) % N
                formatted.append(IDX_TO_LATIN[p])
                plain_ki += 1
        elif val == '-':
            formatted.append(' ')
        elif val == '.':
            formatted.append('. ')
        elif val in '&$':
            formatted.append(f'\n[{val}]\n')
        elif val == '\n':
            pass
    full_text = ''.join(formatted)
    print(full_text)
    print()

    # ─── Step 6: Singleton constraint check (F-skip aware) ─────────────────
    print("=" * 70)
    print("STEP 6: SINGLETONS — F-SKIP AWARE")
    print("=" * 70)
    # Find single-rune words, track their TRUE key position (skip ᚠ runes)
    words_with_pos = []  # (word_cipher_list, true_key_start)
    curr_word = []
    curr_ki = 0  # tracks key counter (doesn't advance for F runes)
    word_ki_start = 0

    # Pass 1: build word list with true key positions
    for is_rune, val in tokens:
        if is_rune:
            curr_word.append((val, curr_ki))
            if val != 0:
                curr_ki += 1
        else:
            if curr_word:
                words_with_pos.append(list(curr_word))
                curr_word = []

    if curr_word:
        words_with_pos.append(curr_word)

    singletons_ok = 0
    singletons_conflict = 0
    for wdata in words_with_pos:
        if len(wdata) == 1:
            c, ki = wdata[0]
            kp = ki % KEY_LEN
            if c == 0:
                # Literal F (F-skip): always plain=F, no key used, no constraint
                print(f"  single F at kp=n/a (F-skip literal, no constraint)")
                continue
            # plain must be I(10) or A(24)
            kv = complete_key[kp]
            plain_val = (c - kv) % N
            needed = {(c - 10) % N, (c - 24) % N}
            status = "✅" if kv in needed else "⚠️ CONFLICT"
            print(f"  cipher={c:2d} true_ki={ki:3d} key_pos={kp:2d} key={kv:2d} → plain={plain_val:2d}={IDX_TO_LATIN[plain_val]:3s}  {status}")
            if kv in needed:
                singletons_ok += 1
            else:
                singletons_conflict += 1

    print(f"\n  Singleton result: {singletons_ok} OK, {singletons_conflict} conflicts")

    # ─── Step 7: Word score / phrase check ─────────────────────────────────
    print()
    print("=" * 70)
    print("STEP 7: FINAL DECODE QUALITY")
    print("=" * 70)
    LP_PHRASES = [
        'AKOAN', 'AMAN', 'STUDYWITHAMASTER', 'AMASTER', 'ARRIVEDATTHESCHOOL',
        'THESCHOOL', 'SAMEASTHAT', 'WHICHIAMSTUDY', 'THESONGOFSELF',
        'THEOTHERSTUDENT', 'HEWASGETTINGIRRI', 'WHATIAMSTUDY', 'WHATIAM',
        'THESONG', 'WITHAMINSTR', 'THESAMEASSOMETH', 'SAMEASWHAT',
        'WHATWAS', 'STUDYHERE', 'WHATYOUARE', 'AREYOUTHESAME',
        'YOUWISHESTOSTUDY', 'DECIDEDTOGO', 'TOTHEGRANDMASTER',
        'WHOWISHES', 'FOUNDANOTHER', 'WISHES', 'DECIDED',
        'INSTRUCTOR', 'PROFESSOR', 'SAMEAS', 'THEOTHER', 'WITHAM',
        'MASTER', 'STUDENT', 'KOAN', 'SONG', 'STUDYING',
        'ARRIVED', 'SCHOOL', 'FOUND', 'SIMILAR', 'IDENTITY',
    ]
    clean_text = full_text.replace(' ', '').replace('.', '').replace('\n', '')
    found_phrases = [p for p in LP_PHRASES if p in clean_text]
    print(f"Found LP phrases: {found_phrases}")
    print(f"Clean text: {clean_text[:300]}")


if __name__ == '__main__':
    main()
