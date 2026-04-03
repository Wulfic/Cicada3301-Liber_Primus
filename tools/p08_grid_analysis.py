#!/usr/bin/env python3
"""
P08 Bigram Grid Analysis — Priority #1 Unsolved Lead
======================================================
Cicada hint "For those who have fallen behind:" with grid:

  Row 1: TL BE IE OV UT HT RE ID TS EO ST PO SO YR  (14 pairs, all alpha)
  Row 2: SL BT II IY T4 DG UQ IM NU 44 2I 15 33 9M  (14 pairs, alphanumeric)

Interpretations tested:
 A) Row1=plaintext, Row2=ciphertext → key = (R2-R1)%29 (28-value key stream)
 B) Row1=ciphertext, Row2=plaintext → key = (R1-R2)%29 (reverse direction)
 C) Column-pair sums: combine each pair's 2 deltas → 14-value key
 D) Direct GP reading: pairs form a substitution table
 E) Read all 28 pairs as one 56-char key (direct GP mapping)
 F) Grid rows as independent Beaufort keys
 G) 28 values as CYCLIC key at all offsets on all unsolved pages

Also tests P08's own rune text with these methods.
"""

from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE / "pages"

# === Gematria Primus ===
RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]

# Latin letter → GP index
def latin_to_gp(ch):
    """Map a Latin letter (or digit) to its GP index."""
    mapping = {
        'A': 24, 'B': 17, 'C': 5,  'D': 23, 'E': 18, 'F': 0,
        'G': 6,  'H': 8,  'I': 10, 'J': 11, 'K': 5,  'L': 20,
        'M': 19, 'N': 9,  'O': 3,  'P': 13, 'Q': 5,  'R': 4,
        'S': 15, 'T': 16, 'U': 1,  'V': 1,  'W': 7,  'X': 14,
        'Y': 26, 'Z': 15,
        '0': 0,  '1': 1,  '2': 2,  '3': 3,  '4': 4,  '5': 5,
        '6': 6,  '7': 7,  '8': 8,  '9': 9,
    }
    return mapping.get(ch.upper(), None)

# --- The P08 bigram grid ---
ROW1_PAIRS = ['TL','BE','IE','OV','UT','HT','RE','ID','TS','EO','ST','PO','SO','YR']
ROW2_PAIRS = ['SL','BT','II','IY','T4','DG','UQ','IM','NU','44','2I','15','33','9M']

def pairs_to_gp(pairs):
    """Convert list of 2-char pairs to flat GP index list."""
    result = []
    for pair in pairs:
        for ch in pair:
            v = latin_to_gp(ch)
            if v is None:
                print(f"WARNING: Cannot map '{ch}' to GP")
                v = 0
            result.append(v)
    return result

# Compute key streams
R1_GP = pairs_to_gp(ROW1_PAIRS)   # 28 values
R2_GP = pairs_to_gp(ROW2_PAIRS)   # 28 values

# Direction A: cipher=R2, plain=R1 → key = (R2 - R1) % 29
KEY_A = [(r2 - r1) % 29 for r1, r2 in zip(R1_GP, R2_GP)]   # add mode: plain = cipher + key
# Direction B: cipher=R1, plain=R2 → key = (R1 - R2) % 29
KEY_B = [(r1 - r2) % 29 for r1, r2 in zip(R1_GP, R2_GP)]

# Column-pair keys: sum and avg
KEY_C_SUM = [sum(KEY_A[2*i:2*i+2]) % 29 for i in range(14)]   # 14 values (sum of each pair)
KEY_C_DIFF1 = [KEY_A[2*i] for i in range(14)]   # first of each pair (14 values)
KEY_C_DIFF2 = [KEY_A[2*i+1] for i in range(14)] # second of each pair (14 values)

# Extra keys: direct GPR1 and GPR2 as keys
KEY_R1 = R1_GP  # 28-value key directly being row 1 GP values
KEY_R2 = R2_GP  # 28-value key directly being row 2 GP values

print("=== P08 BIGRAM GRID KEY STREAMS ===")
print(f"Row 1 GP: {R1_GP}")
print(f"Row 2 GP: {R2_GP}")
print(f"Key A (R2-R1): {KEY_A}")
print(f"Key B (R1-R2): {KEY_B}")
print(f"Key C-sum (14 values): {KEY_C_SUM}")

# Show key A as runeglish
print(f"Key A as GP letters: {' '.join(IDX_TO_LETTER[k] for k in KEY_A)}")
print(f"Key B as GP letters: {' '.join(IDX_TO_LETTER[k] for k in KEY_B)}")
print()


def load_runes(page_num):
    """Load rune file and return (indices, raw_content)."""
    rune_file = PAGES_DIR / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        return None, None
    with open(rune_file, 'r', encoding='utf-8') as f:
        content = f.read()
    indices = [RUNE_TO_IDX[ch] for ch in content if ch in RUNE_TO_IDX]
    return indices, content


def compute_ioc(indices):
    n = len(indices)
    if n < 2:
        return 0
    counts = Counter(indices)
    num = sum(c * (c-1) for c in counts.values())
    return 29 * num / (n * (n-1))


def decrypt(cipher, key, mode='sub'):
    kl = len(key)
    result = []
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'add':
            result.append((c + k) % 29)
        elif mode == 'beau':
            result.append((k - c) % 29)
    return result


def to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)


# Singleton constraint: single-rune words MUST be I(10) or A(24)
def check_singletons(plain_indices, raw_content):
    """Return False if any single-rune word decrypts to something other than I or A."""
    rune_pos = 0
    in_word = True
    word_len = 0
    word_start = 0

    for ch in raw_content:
        if ch in RUNE_TO_IDX:
            if not in_word:
                in_word = True
                word_len = 1
                word_start = rune_pos
            else:
                word_len += 1
            rune_pos += 1
        elif ch in '-. ':
            if in_word and word_len == 1:
                v = plain_indices[word_start]
                if v not in (10, 24):
                    return False
            in_word = False
            word_len = 0

    if in_word and word_len == 1:
        v = plain_indices[word_start]
        if v not in (10, 24):
            return False
    return True


COMMON = {
    'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','WAS','ONE','OUR',
    'OUT','HAD','HAS','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY',
    'WHO','THIS','THAT','WITH','HAVE','FROM','THEY','BEEN','SAID','WILL',
    'INTO','THAN','THEM','THEN','WHAT','WHEN','MAKE','LIKE','LONG','LOOK',
    'MANY','SOME','TIME','YOUR','KNOW','JUST','COME','BACK','ONLY','SELF',
    'BEING','TRUTH','WITHIN','SACRED','WISDOM','FOLLOW','INSTRUCTION',
    'DIVINITY','BELIEVE','NOTHING','EXCEPT','TRUE','TEST','KNOWLEDGE',
    'EXPERIENCE','DEATH','CHANGE','MESSAGE','CONTAINED','WORDS','NUMBERS',
    'THINGS','SHOULD','PRIMES','TOTIENT','PILGRIM','JOURNEY','TOWARD',
    'THESE','THOSE','NECESSARY','ALONG','STRUGGLE','SUFFERING','INNOCENCE',
    'ILLUSIONS','CERTAINTY','REALITY','DISCOVER','THROUGH','PILGRIMAGE',
    'SHAPE','OURSELVES','REALITIES','DEEP','ARRIVE','OUTSIDE','INSTAR',
    'EMERGE','HOLY','INTELLIGENCE','COMMAND','VOID','FORM','CABAL',
    'A','I','OF','TO','IN','IS','IT','AN','AS','AT','BE','BY','DO','GO',
    'IF','ME','MY','NO','ON','OR','SO','UP','WE',
    'REARRANGING','PRIMES','SHOW','PATH','DEOR',
}

BIGRAMS = {
    'TH': 8, 'HE': 7, 'IN': 6, 'AN': 6, 'ER': 5, 'ND': 5, 'ON': 5,
    'EN': 5, 'AT': 5, 'RE': 5, 'ED': 4, 'ES': 4, 'OU': 4, 'TO': 4,
    'HA': 4, 'IS': 4, 'IT': 4, 'AL': 4, 'ST': 4, 'NG': 4, 'OR': 3,
    'AR': 3, 'TE': 3, 'SE': 3, 'OF': 3, 'LE': 3, 'SA': 3, 'EA': 3,
    'TR': 3, 'WH': 3, 'OW': 3, 'BE': 3, 'WI': 3, 'HI': 3, 'LL': 3,
    'LY': 2, 'EL': 2, 'ME': 2, 'NO': 2, 'LI': 2, 'GE': 2, 'ET': 2,
    'TI': 2, 'NE': 2, 'DE': 2, 'AC': 2, 'NT': 2, 'MA': 2, 'US': 2,
}


def score_words(text):
    words = text.replace('.',' ').replace('-',' ').split()
    score = 0
    for w in words:
        wu = w.upper()
        if wu in COMMON:
            score += len(wu) * 10
        elif wu.replace('C','K') in COMMON or wu.replace('U','V') in COMMON:
            score += len(wu) * 8
        elif len(wu) >= 4:
            # count bigram hits instead
            pass
    flat = text.replace(' ','').replace('.','').replace('-','')
    for i in range(len(flat)-1):
        b = flat[i:i+2].upper()
        if b in BIGRAMS:
            score += BIGRAMS[b]
    return score


def test_key_on_page(page_num, key, mode, key_name):
    """Test a key against a page. Returns best result dict or None."""
    indices, raw = load_runes(page_num)
    if indices is None or len(indices) < 20:
        return None

    plain = decrypt(indices, key, mode)
    ioc = compute_ioc(plain)
    singletons_ok = check_singletons(plain, raw)
    text = to_runeglish(plain)
    score = score_words(text)

    return {
        'page': page_num,
        'key_name': key_name,
        'mode': mode,
        'ioc': ioc,
        'singletons': singletons_ok,
        'score': score,
        'text': text[:200],
    }


def run_fixed_keys():
    """Test all derived bigram keys on all unsolved pages."""
    print("=" * 80)
    print("FIXED KEY TESTS (P08 grid-derived keys, no offset)")
    print("=" * 80)

    keys = {
        'KEY_A_28': KEY_A,
        'KEY_B_28': KEY_B,
        'KEY_C_sum14': KEY_C_SUM,
        'KEY_C_d1_14': KEY_C_DIFF1,
        'KEY_C_d2_14': KEY_C_DIFF2,
        'KEY_R1_raw': KEY_R1,
        'KEY_R2_raw': KEY_R2,
    }

    pages = list(range(8, 55))  # Include P08 itself
    results = []

    for page in pages:
        for kname, key in keys.items():
            for mode in ['sub', 'add', 'beau']:
                r = test_key_on_page(page, key, mode, kname)
                if r and (r['ioc'] > 1.3 or (r['ioc'] > 1.15 and r['singletons'])):
                    results.append(r)

    results.sort(key=lambda x: (-x['ioc'], -x['score']))

    if not results:
        print("  No results above IoC 1.15 with singletons passing.")
        print("  Showing top 10 by IoC regardless:")
        all_r = []
        for page in pages:
            for kname, key in keys.items():
                for mode in ['sub', 'add', 'beau']:
                    r = test_key_on_page(page, key, mode, kname)
                    if r:
                        all_r.append(r)
        all_r.sort(key=lambda x: -x['ioc'])
        for r in all_r[:15]:
            s = '✓' if r['singletons'] else '✗'
            print(f"  P{r['page']:02d} {r['key_name']:<15} {r['mode']:<4} IoC={r['ioc']:.4f} [{s}] Score={r['score']:>5} | {r['text'][:60]}")
    else:
        print(f"\n{'Page':>4} {'Key':<15} {'Mode':<4} {'IoC':>7} {'Sing'} {'Score':>6} | Text")
        print("-" * 90)
        for r in results[:30]:
            s = '✓' if r['singletons'] else '✗'
            print(f"P{r['page']:02d}  {r['key_name']:<15} {r['mode']:<4} {r['ioc']:.4f} [{s}] {r['score']:>6} | {r['text'][:55]}")


def run_offset_sweep():
    """Test KEY_A and KEY_B at all offsets on all unsolved pages."""
    print("\n" + "=" * 80)
    print("OFFSET SWEEP (keys at all rotations on all unsolved pages)")
    print("=" * 80)

    pages = list(range(8, 55))
    keys_to_sweep = [
        ('KEY_A_28', KEY_A),
        ('KEY_B_28', KEY_B),
        ('KEY_C_s14', KEY_C_SUM),
        ('KEY_R1_28', KEY_R1),
        ('KEY_R2_28', KEY_R2),
    ]
    MODES = ['sub', 'add', 'beau']

    top_results = []

    for page in pages:
        indices, raw = load_runes(page)
        if indices is None or len(indices) < 20:
            continue

        for kname, base_key in keys_to_sweep:
            kl = len(base_key)
            for offset in range(kl):
                rotated_key = base_key[offset:] + base_key[:offset]
                for mode in MODES:
                    plain = decrypt(indices, rotated_key, mode)
                    ioc = compute_ioc(plain)
                    if ioc > 1.25:
                        singletons_ok = check_singletons(plain, raw)
                        text = to_runeglish(plain)
                        score = score_words(text)
                        top_results.append({
                            'page': page, 'kname': kname, 'offset': offset,
                            'mode': mode, 'ioc': ioc, 'singletons': singletons_ok,
                            'score': score, 'text': text[:150],
                        })

    top_results.sort(key=lambda x: (-x['ioc'], -x['score']))

    if not top_results:
        print("  No results above IoC 1.25 at any offset.")
        # Show best IoC for each page
        print("  Showing best IoC per page (KEY_A, all modes, all offsets):")
        page_best = {}
        for page in pages:
            indices, raw = load_runes(page)
            if indices is None:
                continue
            best = 0
            for offset in range(len(KEY_A)):
                rk = KEY_A[offset:] + KEY_A[:offset]
                for mode in MODES:
                    pl = decrypt(indices, rk, mode)
                    ioc = compute_ioc(pl)
                    if ioc > best:
                        best = ioc
                        best_mode = mode
                        best_off = offset
            page_best[page] = (best, best_mode, best_off)

        sorted_pages = sorted(page_best.items(), key=lambda x: -x[1][0])
        for pg, (ioc, mode, off) in sorted_pages[:20]:
            indices, raw = load_runes(pg)
            rk = KEY_A[off:] + KEY_A[:off]
            pl = decrypt(indices, rk, mode)
            text = to_runeglish(pl)
            sc = check_singletons(pl, raw)
            print(f"  P{pg:02d} off={off:>2} {mode:<4} IoC={ioc:.4f} {'✓' if sc else '✗'} | {text[:60]}")
    else:
        print(f"\n{'Page':>4} {'Key':<10} {'Off':>3} {'Mode':<4} {'IoC':>7} {'S'} {'Score':>6} | Text")
        print("-" * 100)
        for r in top_results[:30]:
            s = '✓' if r['singletons'] else '✗'
            print(f"P{r['page']:02d}  {r['kname']:<10} {r['offset']:>3} {r['mode']:<4} {r['ioc']:.4f} [{s}] {r['score']:>6} | {r['text'][:55]}")


def test_grid_as_substitution():
    """Interpret the bigram grid as a bigram substitution cipher on solved pages."""
    print("\n" + "=" * 80)
    print("BIGRAM SUBSTITUTION TABLE TEST")
    print("=" * 80)

    # Build substitution: Row1_pair[i] → Row2_pair[i] (and reverse)
    # Each pair is treated as 2 consecutive GP letters
    sub_fwd = {}  # R1 pair → R2 pair encoding
    sub_rev = {}  # R2 pair → R1 pair

    for r1, r2 in zip(ROW1_PAIRS, ROW2_PAIRS):
        r1_gp = (latin_to_gp(r1[0]), latin_to_gp(r1[1]))
        r2_gp = (latin_to_gp(r2[0]), latin_to_gp(r2[1]))
        sub_fwd[r1_gp] = r2_gp
        sub_rev[r2_gp] = r1_gp

    print(f"Forward substitution table ({len(sub_fwd)} bigram pairs):")
    for (p1, p2), (c1, c2) in sub_fwd.items():
        print(f"  {IDX_TO_LETTER[p1]}{IDX_TO_LETTER[p2]} → {IDX_TO_LETTER[c1]}{IDX_TO_LETTER[c2]}")

    # Test this substitution on all pages
    pages_to_test = list(range(8, 55))
    results = []

    for page in pages_to_test:
        indices, raw = load_runes(page)
        if indices is None or len(indices) < 4:
            continue

        # Apply forward substitution (pairs)
        plain_fwd = []
        i = 0
        while i < len(indices) - 1:
            pair = (indices[i], indices[i+1])
            if pair in sub_rev:
                plain_fwd.extend(sub_rev[pair])
                i += 2
            else:
                plain_fwd.append(indices[i])
                i += 1
        if i < len(indices):
            plain_fwd.append(indices[i])

        ioc = compute_ioc(plain_fwd)
        if ioc > 1.1:
            text = to_runeglish(plain_fwd)
            score = score_words(text)
            results.append({
                'page': page, 'direction': 'fwd_sub',
                'ioc': ioc, 'score': score, 'text': text[:100],
            })

    results.sort(key=lambda x: -x['ioc'])
    if results:
        for r in results[:10]:
            print(f"P{r['page']:02d} {r['direction']} IoC={r['ioc']:.4f} | {r['text'][:60]}")
    else:
        print("  No pages with IoC > 1.1 after bigram substitution")


def test_grid_as_polybius():
    """Treat the 14-column bigram pairs as Polybius coordinates."""
    print("\n" + "=" * 80)
    print("POLYBIUS COORDINATE TEST")
    print("=" * 80)

    # Each column gives (row_char, col_char) → a cell value
    # Build a 29×29 lookup using position as value
    # col_pair[i] = (Row1_pair[i], Row2_pair[i]) = ((r1a,r1b),(r2a,r2b))
    # Interpretation: (r1a, r2a) gives first coordinate pair, (r1b, r2b) gives second
    # So for each "column" i, the cipher bigram (r1a,r1b) decodes to plain bigram (r2a,r2b)

    # Already tested above as bigram substitution
    # Try alternative: each PAIR encodes a single GP value
    # Polybius: cell(r, c) in a √29 × √29 grid

    # 14 values from column-pair interpretation
    # row key = R1 gives row hint, R2 gives column hint
    row_key = [latin_to_gp(p[0]) for p in ROW1_PAIRS]  # first letter of each R1 pair
    col_key = [latin_to_gp(p[1]) for p in ROW1_PAIRS]  # second letter of each R1 pair
    print(f"Row indicators: {[IDX_TO_LETTER[v] for v in row_key]}")
    print(f"Col indicators: {[IDX_TO_LETTER[v] for v in col_key]}")
    row_key2 = [latin_to_gp(p[0]) for p in ROW2_PAIRS]
    col_key2 = [latin_to_gp(p[1]) for p in ROW2_PAIRS]
    print(f"Row2 indicators: {[IDX_TO_LETTER[v] for v in row_key2]}")
    print(f"Col2 indicators: {[IDX_TO_LETTER[v] for v in col_key2]}")

    # Map each pair of (row_indicator, col_indicator) to a GP value
    # Standard Polybius: cell = row*sqrt(N) + col (for NxN grid)
    print("\nAttempting Polybius mapping:")
    for i, (r1, r2) in enumerate(zip(ROW1_PAIRS, ROW2_PAIRS)):
        r1a, r1b = latin_to_gp(r1[0]), latin_to_gp(r1[1])
        r2a, r2b = latin_to_gp(r2[0]), latin_to_gp(r2[1])
        # r1 pair could be coordinates, r2 pair is the result
        # or: r1 is plaintext, r2 is cipher
        cell_val = (r1a + r1b) % 29
        print(f"  Pair {i+1:2d}: {r1}({r1a},{r1b})→sum={cell_val}({IDX_TO_LETTER[cell_val]}) | "
              f"{r2}({r2a},{r2b})→sum={( r2a+r2b)%29}({IDX_TO_LETTER[(r2a+r2b)%29]})")


def test_p08_runes():
    """Test P08's own rune text with all bigram-derived keys."""
    print("\n" + "=" * 80)
    print("P08 RUNE TEXT DECRYPTION")
    print("=" * 80)

    indices, raw = load_runes(8)
    if indices is None:
        print("  P08 rune file not found")
        return

    print(f"P08: {len(indices)} runes")
    print(f"Raw GP: {indices[:28]}")

    # Test with Shift-3-Reversed-Gematria = (2-i)%29
    plain_koan = [(2 - c) % 29 for c in indices]
    text_koan = to_runeglish(plain_koan)
    ioc_koan = compute_ioc(plain_koan)
    print(f"\nShift-3-RevGem (2-i)%29: IoC={ioc_koan:.4f} | {text_koan[:100]}")

    # Test with P08 grid keys
    print("\nP08 grid keys on P08 rune text:")
    all_keys = [
        ('KEY_A', KEY_A), ('KEY_B', KEY_B),
        ('KEY_R1', KEY_R1), ('KEY_R2', KEY_R2),
        ('KEY_C_sum', KEY_C_SUM),
    ]
    for kname, key in all_keys:
        for mode in ['sub', 'add', 'beau']:
            plain = decrypt(indices, key, mode)
            ioc = compute_ioc(plain)
            text = to_runeglish(plain)
            if ioc > 1.2:
                sc = check_singletons(plain, raw)
                print(f"  {kname:<10} {mode:<4} IoC={ioc:.4f} {'✓' if sc else '✗'} | {text[:80]}")

    # Also test at Koan formula shifted
    print("\nKoan formula variants on P08:")
    for shift in range(29):
        plain = [(shift - c) % 29 for c in indices]
        ioc = compute_ioc(plain)
        if ioc > 1.5:
            text = to_runeglish(plain)
            print(f"  (shift={shift}-c)%29: IoC={ioc:.4f} | {text[:80]}")


def test_p19_plaintext_as_key():
    """P19's solved plaintext says 'REARRANGING THE PRIME NUMBERS WILL SHOW A PATH TO THE DEOR K'.
    The bigram grid might tell us HOW to rearrange. Test various rearrangements."""
    print("\n" + "=" * 80)
    print("P19 KEY → PRIME REARRANGEMENT → TEST ON P08/P21-54")
    print("=" * 80)

    # The 14 pairs may define a permutation of the first 28 primes
    # or a permutation of the 29-rune alphabet
    # R1 GP indices (28 values) might specify POSITIONS in a prime table
    # R2 GP indices might give the OUTPUT at those positions

    # Build a permutation table from R1→R2 mapping
    perm = {}
    for r1, r2 in zip(R1_GP, R2_GP):
        if r1 not in perm:
            perm[r1] = r2

    print(f"Permutation (R1→R2): { {IDX_TO_LETTER[k]: IDX_TO_LETTER[v] for k,v in perm.items()} }")

    # Apply this permutation as a substitution cipher (monoalphabetic)
    pages = list(range(8, 55))
    results = []
    for page in pages:
        indices, raw = load_runes(page)
        if indices is None:
            continue
        # Forward permutation
        plain_fwd = [perm.get(c, c) for c in indices]
        # Reverse permutation
        rev_perm = {v: k for k, v in perm.items()}
        plain_rev = [rev_perm.get(c, c) for c in indices]

        for plain, direction in [(plain_fwd, 'fwd'), (plain_rev, 'rev')]:
            ioc = compute_ioc(plain)
            if ioc > 1.15:
                sc = check_singletons(plain, raw)
                text = to_runeglish(plain)
                score = score_words(text)
                results.append({'page': page, 'dir': direction, 'ioc': ioc, 'sc': sc,
                                 'score': score, 'text': text[:80]})

    results.sort(key=lambda x: -x['ioc'])
    if results:
        for r in results[:10]:
            print(f"P{r['page']:02d} {r['dir']} IoC={r['ioc']:.4f} {'✓' if r['sc'] else '✗'} | {r['text'][:60]}")
    else:
        print("  No pages with IoC > 1.15 under permutation")
        # Show top 5 anyway
        all_r = []
        for page in pages:
            indices, raw = load_runes(page)
            if indices is None:
                continue
            plain = [perm.get(c, c) for c in indices]
            ioc = compute_ioc(plain)
            all_r.append((page, ioc, to_runeglish(plain)[:60]))
        all_r.sort(key=lambda x: -x[1])
        for pg, ioc, text in all_r[:5]:
            print(f"  P{pg:02d}: IoC={ioc:.4f} | {text}")


def test_koan_as_key():
    """The solved koan text (P06-09) as a running key for unsolved pages."""
    print("\n" + "=" * 80)
    print("KOAN TEXT AS RUNNING KEY FOR UNSOLVED PAGES")
    print("=" * 80)

    koan_text = (
        "AKOANAMANDEICEDEDTOGOANDSTUDYWITHMASTERHE"
        "WENTTOTHEDOOROFTHEMASTERWHOAREYOUWHOWISHES"
        "TOSTUDYHEREASKDTHEMASTERTHESTUDENTOLDTHEMA"
        "STERHISNAMETHATISNNOTWHATYOUARETHATISONLYW"
        "HATYOUARECALLEDWHOAREYOUWHOWISHESTOSTUDYHE"
        "REHEARESKEDAGAINTHEMANTHOUGHTFORAMOMENTAND"
        "REPLIEDIIAMAPROFESSORTHATISWATYOUDO"
        "NOTWHATYOUAREREPLIEDTHEMASTERWHOAREYOUWHOW"
        "ISHESTOSTUDYHERETHEMANWASGETTINGIRRITATEDIAM"
        "HESTARTEDBUTHHECOULDNOTTHINKOFANYTHINGELSE"
        "TOSAYSOHETRAILEDOFFAFTERALONPAUSETHEMASTERR"
        "EPLIEDTHENYOUAREWELCOMETOCOMESTUDYANINSTRUCT"
        "IONDOFOURUNREASONABLETHINGSEACHDAY"
    )

    # Convert koan text to GP indices (bigrams like TH, NG, EO, AE, OE, IO, EA handled)
    koan_gp = []
    i = 0
    while i < len(koan_text):
        if i+1 < len(koan_text):
            bigram = koan_text[i:i+2]
            if bigram == 'TH':
                koan_gp.append(2); i += 2; continue
            elif bigram == 'NG' or bigram == 'ING':
                koan_gp.append(21); i += 2; continue
            elif bigram == 'AE':
                koan_gp.append(25); i += 2; continue
            elif bigram == 'OE':
                koan_gp.append(22); i += 2; continue
            elif bigram == 'IO':
                koan_gp.append(27); i += 2; continue
            elif bigram == 'EA':
                koan_gp.append(28); i += 2; continue
            elif bigram == 'EO':
                koan_gp.append(12); i += 2; continue
        v = latin_to_gp(koan_text[i])
        if v is not None:
            koan_gp.append(v)
        i += 1

    print(f"Koan as GP key: {len(koan_gp)} values")

    pages = list(range(8, 55))
    results = []
    for page in pages:
        indices, raw = load_runes(page)
        if indices is None:
            continue
        best_ioc = 0
        best_r = None
        for offset in range(min(len(koan_gp), 500)):
            key_segment = koan_gp[offset:]
            for mode in ['sub', 'add', 'beau']:
                plain = decrypt(indices, key_segment, mode)
                ioc = compute_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    sc = check_singletons(plain, raw)
                    text = to_runeglish(plain)
                    score = score_words(text)
                    best_r = {'page': page, 'offset': offset, 'mode': mode,
                               'ioc': ioc, 'sc': sc, 'score': score, 'text': text[:80]}
        if best_r and best_r['ioc'] > 1.1:
            results.append(best_r)

    results.sort(key=lambda x: -x['ioc'])
    if results:
        for r in results[:10]:
            print(f"P{r['page']:02d} off={r['offset']:>3} {r['mode']} IoC={r['ioc']:.4f} {'✓' if r['sc'] else '✗'} | {r['text'][:60]}")
    else:
        print("  No results above IoC 1.1 using koan as running key")


def analyze_grid_arithmetic():
    """Look for mathematical patterns in the bigram grid."""
    print("\n" + "=" * 80)
    print("ARITHMETIC ANALYSIS OF BIGRAM GRID")
    print("=" * 80)

    print("\nColumn-by-column GP values:")
    print(f"{'Pos':>3} | {'R1 pair':>8} | {'R1 GP (a,b)':>12} | {'R2 pair':>8} | {'R2 GP (a,b)':>12} | "
          f"{'Diff A-B':>10} | {'Sum R1':>6} | {'Sum R2':>6} | {'Prod%29':>7}")
    print("-" * 90)
    for i, (r1, r2) in enumerate(zip(ROW1_PAIRS, ROW2_PAIRS)):
        r1a, r1b = latin_to_gp(r1[0]), latin_to_gp(r1[1])
        r2a, r2b = latin_to_gp(r2[0]), latin_to_gp(r2[1])
        da = (r2a - r1a) % 29
        db = (r2b - r1b) % 29
        s1 = (r1a + r1b) % 29
        s2 = (r2a + r2b) % 29
        p1 = (r1a * r1b) % 29
        print(f"{i+1:3d} | {r1:>8} | ({r1a:>2},{r1b:>2})        | {r2:>8} | ({r2a:>2},{r2b:>2})        | "
              f"({da:>2},{db:>2})       | {s1:>6} | {s2:>6} | {p1:>7}")

    # Check if key A (differences) follows any known sequence
    print(f"\nKey A (R2-R1) differences: {KEY_A}")
    print(f"Key A sums by pair: {KEY_C_SUM}")

    # Check for prime-related patterns
    from sympy import primepi, isprime, prime as nth_prime, totient
    print("\nChecking if key values relate to primes:")
    for i, (k, r1, r2) in enumerate(zip(KEY_A[:14], R1_GP[:14], R2_GP[:14])):
        print(f"  pos {i:2d}: R1={r1:2d}({IDX_TO_LETTER[r1]}) R2={r2:2d}({IDX_TO_LETTER[r2]}) "
              f"diff={k:2d}({IDX_TO_LETTER[k]}) "
              f"phi(R1)={totient(r1+1):3d}%29={(totient(r1+1))%29:2d} "
              f"R1*R2%29={(r1*r2)%29:2d}")


def main():
    test_p08_runes()
    run_fixed_keys()
    run_offset_sweep()
    test_grid_as_substitution()
    test_grid_as_polybius()
    test_p19_plaintext_as_key()
    test_koan_as_key()
    analyze_grid_arithmetic()


if __name__ == '__main__':
    main()
