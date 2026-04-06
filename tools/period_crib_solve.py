"""
Period-Constrained Crib Dragging Solver
========================================
For pages with detected prime-period Vigenère (session17 Test 9 findings).
Exploit word-boundary structure for systematic key recovery.

Usage:
    python Tools/period_crib_solve.py PAGE PERIOD [MODE]
    e.g.  python Tools/period_crib_solve.py 30 17
          python Tools/period_crib_solve.py 27 43

Method:
  1. Parse cipher word-by-word (word boundaries from `-` separators)
  2. For each word slot, try all LP words of matching length as plaintext crib
  3. Derive key values K[pos%P .. (pos+len-1)%P] under each mode
  4. Check derived key is consistent with all other word slots
  5. Score by: (a) full key coverage, (b) LP word/phrase density
  6. Apply complete key and show decoded text

Key insight: if period P is correct and a crib is correct,
  ALL positions with key index j = pos%P must produce valid LP text.
  This serves as a powerful consistency check.
"""

import os, sys, json, re
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
N = 29

def idx_to_lat(i): return IDX_TO_LATIN[i % N]

def parse_words(path):
    """Parse rune file → list of (word_start_pos, word_rune_list) tuples.
    Skips metadata lines. Returns rune position offsets for each word.
    """
    all_runes = []
    word_boundary_pos = []  # position of each '-' or '.' or '&'/'$' separator
    word_starts = []        # start position of each word
    current_word = []
    current_word_start = 0

    for raw_line in open(path, encoding='utf-8'):
        line = raw_line.rstrip()
        ascii_alpha = sum(1 for c in line if c.isascii() and c.isalpha())
        rune_count = sum(1 for c in line if c in RUNE_TO_IDX)
        if ascii_alpha > 0 and rune_count == 0: continue
        if ascii_alpha > 2 and rune_count < ascii_alpha: continue

        for ch in line:
            if ch in RUNE_TO_IDX:
                current_word.append(RUNE_TO_IDX[ch])
            elif ch in '-./&$\n':
                if current_word:
                    word_starts.append((current_word_start, list(current_word)))
                    current_word_start = len(all_runes) + len(current_word)
                    all_runes.extend(current_word)
                    current_word = []
                    current_word_start = len(all_runes)

    if current_word:
        word_starts.append((current_word_start, list(current_word)))
        all_runes.extend(current_word)

    return all_runes, word_starts

def decrypt_sub(cipher, key):
    k = len(key)
    return [(c - key[i % k]) % N for i, c in enumerate(cipher)]

def decrypt_add(cipher, key):
    k = len(key)
    return [(c + key[i % k]) % N for i, c in enumerate(cipher)]

def decrypt_beaufort(cipher, key):
    k = len(key)
    return [(key[i % k] - c) % N for i, c in enumerate(cipher)]

def indices_to_text(idxs):
    return ''.join(IDX_TO_LATIN[i] for i in idxs)

MODES = {
    'SUB': decrypt_sub,
    'ADD': decrypt_add,
    'BEAUFORT': decrypt_beaufort,
}

# ─── LP Vocabulary ───────────────────────────────────────────────────────────
LP_WORDS_BY_LEN = defaultdict(list)
LP_WORDS_SET = set()

def load_lp_words():
    """Load and organize LP vocabulary by word length in GP units."""
    # Core LP vocabulary (GP indices)
    lp_vocab_latin = [
        'THE', 'AND', 'OF', 'A', 'TO', 'IS', 'IT', 'YOU', 'THAT', 'FOR',
        'ARE', 'THIS', 'WITH', 'ALL', 'THINGS', 'BE', 'NOT', 'HAVE', 'FROM',
        'DO', 'AN', 'THERE', 'EACH', 'YOUR', 'SELF', 'INTO', 'WITHIN', 'NOTHING',
        'SOME', 'FOLLOW', 'TRUTH', 'WISDOM', 'SACRED', 'PRIMES', 'TOTIENT',
        'FUNCTION', 'ENCRYPTED', 'DIVINITY', 'DIVINE', 'KNOW', 'KNOWTHIS',
        'INSTRUCTION', 'FIND', 'EXPERIENCE', 'DEATH', 'BELIEVE', 'TEST',
        'KNOWLEDGE', 'IMPOSE', 'OTHERS', 'INSTAR', 'EMERGE', 'JOURNEY', 'END',
        'GREAT', 'ALONG', 'WAY', 'WILL', 'THROUGH', 'GOING', 'WITHIN', 'BEING',
        'UNTO', 'ITSELF', 'COMMAND', 'OWN', 'INTELLIGENCE', 'HOLY', 'LIVES',
        'LAW', 'CIRCUMFERENCE', 'PRACTICES', 'THREE', 'BEHAVIORS', 'CAUSE',
        'LOSS', 'CONSUMPTION', 'PRESERVATION', 'PRESERUATION', 'ADHERENCE',
        'AMASS', 'WEALTH', 'BECOME', 'ATTACHED', 'PREPARED', 'DESTROY',
        'PROGRAM', 'MIND', 'REALITY', 'QUESTION', 'DISCOVER', 'DISCOUER', 'DEEP',
        'WEB', 'EXISTS', 'PAGE', 'HASHES', 'DUTY', 'PILGRIM', 'SEEK', 'OUT',
        'SAME', 'AS', 'WHAT', 'TRUE', 'EITHER', 'WORDS', 'NUMBERS', 'CHANGE',
        'BOOK', 'EXCEPT', 'EDIT', 'MESSAGE', 'CONTAINED', 'BUT', 'WHO', 'HERE',
        'NECESSARY', 'ONE', 'EASY', 'TRIP', 'STRUGGLE', 'SUFFERING', 'INNOCENCE',
        'ILLUSIONS', 'CERTAINTY', 'ULTIMATELY', 'SHAPE', 'OURSELVES', 'REALITIES',
        'OUTSIDE', 'LIKE', 'ONLY', 'MAY', 'PARABLE', 'TUNNELING', 'SURFACE',
        'MUST', 'SHED', 'LIBER', 'PRIMUS', 'EPILOGUE', 'CHAPTER', 'INTUS',
        'REARRANGING', 'SHOW', 'PATH', 'DEOR', 'SWORN', 'OATH', 'ABOVE',
        'ASTARTING', 'COERCED', 'CAN', 'SEE', 'HER', 'HIS', 'THEIR', 'THEM',
        'PERSON', 'MAN', 'WOMAN', 'MASTER', 'STUDENT', 'VOICE', 'HEAD', 'ASKED',
        'SAID', 'EXPLAINED', 'LESSON', 'DURING', 'FOUR', 'UNREASONABLE', 'DAY',
        'SHADOWS', 'AETHEREAL', 'BUFFERS', 'VOID', 'CARNAL', 'OBSCURA', 'FORM',
        'MOBIUS', 'ANALOG', 'MOURNFUL', 'CABAL', 'SUOID', 'DECEPTION', 'STRENGTH',
        'SACRED', 'DIUINITY', 'HAUE', 'NEUER', 'BELIEUE', 'DISCOUER', 'CNOW',
        'GONG', 'LICE', 'BENG', 'SEEC', 'THENGS', 'NOTHENG', 'KNOWENGE', 'FOLLOWENG',
        'WEFOLLOWDECEPTION', 'PRESERUE', 'OBSERUE', 'CONCEIUE', 'BELEIUE',
        'BEHAUIOR', 'RECEIUE', 'PERCEIUE', 'SEUEN', 'BECAUSE', 'ERRORS',
        'AT', 'BY', 'IN', 'ON', 'NO', 'OR', 'IF', 'SO', 'UP', 'US',
        'HAS', 'ITS', 'HIM', 'HER', 'WAS', 'HAD', 'HIS', 'OUR', 'WE', 'MY',
        'NEW', 'TOO', 'TWO', 'OLD', 'NOW', 'HOW', 'GET', 'GOT', 'LET',
        'SET', 'PUT', 'TRY', 'ASK', 'USE', 'RUN', 'SEE', 'BUY', 'PAY',
        'THEY', 'THEM', 'THEN', 'WHEN', 'THAN', 'THAT', 'ALSO', 'WELL',
        'EVEN', 'SUCH', 'MOST', 'JUST', 'OVER', 'VERY', 'ONLY', 'MUCH',
        'BOTH', 'LESS', 'BEST', 'LONG', 'GOOD', 'MANY', 'BEEN', 'HAVE',
        'DOES', 'DONE', 'MADE', 'MAKE', 'TAKE', 'COME', 'GIVE', 'KNOW',
        'LIVE', 'LOVE', 'MOVE', 'OPEN', 'SHOW', 'KEEP', 'NEED', 'FEEL',
        'WORD', 'LIFE', 'WORK', 'HAND', 'HOLD', 'HOME', 'TIME', 'YEAR',
        'PART', 'PLACE', 'WORLD', 'EVERY', 'AFTER', 'WHILE', 'WHERE',
        'BEFORE', 'UNDER', 'AGAIN', 'NEVER', 'THOSE', 'THEIR', 'THESE',
        'WHICH', 'WOULD', 'COULD', 'MIGHT', 'STILL', 'ABOUT', 'FIRST',
        'OTHER', 'THINK', 'SMALL', 'GREAT', 'LIGHT', 'NIGHT', 'RIGHT',
        'WHILE', 'TRULY', 'OUGHT', 'AMONG', 'BEING', 'ALONG', 'READY',
    ]

    # Convert Latin → GP indices (simple monograph, handle digraphs)
    def latin_to_gp(text):
        result = []
        i = 0
        t = text.upper()
        while i < len(t):
            if i+1 < len(t):
                dg = t[i:i+2]
                dg_map = {'TH': 2, 'EO': 12, 'NG': 21, 'OE': 22, 'AE': 25, 'IA': 27, 'EA': 28}
                if dg in dg_map:
                    result.append(dg_map[dg])
                    i += 2
                    continue
            c = t[i]
            mono = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                    'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,
                    'D':23,'A':24,'Y':26}
            if c in mono:
                result.append(mono[c])
            i += 1
        return result

    for word in lp_vocab_latin:
        gp_idxs = latin_to_gp(word)
        if gp_idxs:
            key = tuple(gp_idxs)
            LP_WORDS_BY_LEN[len(gp_idxs)].append((word, gp_idxs))
            LP_WORDS_SET.add(key)

def lp_score(plain_idxs):
    """Score a sequence of plain indices for LP vocabulary."""
    text = indices_to_text(plain_idxs)
    score = 0
    for word_set in LP_WORDS_BY_LEN.values():
        for w, gp in word_set:
            if w in text: score += 1
    return score


def solve_with_period(page_num, period, max_iters=5000, verbose=True):
    """Try to crack a page using period-constrained word-boundary crib dragging."""
    path = os.path.join(os.path.dirname(__file__), '..', 'pages', f'page_{page_num:02d}', 'runes.txt')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found"); return

    load_lp_words()
    cipher, words = parse_words(path)
    n = len(cipher)
    print(f"\n=== Period-{period} Crib-Drag Solver: Page {page_num:02d} ===")
    print(f"  Cipher: {n} runes | Words: {len(words)} | Period: {period}")
    print(f"  Streams per key pos: ~{n//period}")

    # Compute split-stream IoC to confirm period signal
    from collections import Counter
    streams = [cipher[i::period] for i in range(period)]
    iocts = []
    for s in streams:
        if len(s) < 2: continue
        nn = len(s); cnt = Counter(s)
        iocts.append(N * sum(v*(v-1) for v in cnt.values()) / (nn*(nn-1)))
    avg_ioc = sum(iocts)/len(iocts) if iocts else 0.0
    print(f"  Split-stream IoC at period {period}: {avg_ioc:.4f}")
    print()

    best_overall = []  # (score, key, mode, text)

    for mode_name, mode_fn in MODES.items():
        print(f"  --- Mode: {mode_name} ---")

        # Approach 1: For each word, try all LP words of same length as crib
        # Build a candidate key score map: key_pos → (cipher_val → plain_score)
        key_partial = [-1] * period  # -1 = unknown

        # Count LP word matches per key-position assignment
        key_scores = defaultdict(lambda: defaultdict(int))

        crib_count = 0
        for word_start, word_runes in words:
            L = len(word_runes)
            if L < 2 or L > 15: continue

            for latin_word, gp_plain in LP_WORDS_BY_LEN[L]:
                # Derive key values this crib would require
                derived_k = {}
                consistent = True
                for i in range(L):
                    kp = (word_start + i) % period
                    c = word_runes[i]
                    p = gp_plain[i]
                    # Mode: SUB: plain = (cipher - key) % N → key = (cipher - plain) % N
                    # Mode: ADD: plain = (cipher + key) % N → key = (plain - cipher) % N
                    # Mode: BEAUFORT: plain = (key - cipher) % N → key = (plain + cipher) % N
                    if mode_name == 'SUB':
                        k_val = (c - p) % N
                    elif mode_name == 'ADD':
                        k_val = (p - c) % N
                    else:  # BEAUFORT
                        k_val = (p + c) % N

                    if kp in derived_k and derived_k[kp] != k_val:
                        consistent = False; break
                    derived_k[kp] = k_val

                if consistent:
                    # Score: check if these key values make OTHER words also LP words
                    for kp, kv in derived_k.items():
                        key_scores[kp][kv] += 1
                    crib_count += 1

        if verbose:
            print(f"    LP crib attempts: {crib_count}")

        # Find the most-voted key value for each position
        partial_key = [0] * period
        key_confidence = []
        for kp in range(period):
            if key_scores[kp]:
                best_kv = max(key_scores[kp], key=lambda kv: key_scores[kp][kv])
                partial_key[kp] = best_kv
                best_score = key_scores[kp][best_kv]
                total_votes = sum(key_scores[kp].values())
                key_confidence.append(best_score / total_votes)
            else:
                key_confidence.append(0.0)

        avg_conf = sum(key_confidence) / len(key_confidence) if key_confidence else 0.0
        print(f"    Average key-pos confidence: {avg_conf:.3f}")
        print(f"    Key position confidence: {[f'{c:.2f}' for c in key_confidence]}")
        print(f"    Derived key: {partial_key}")

        # Decode with partial key
        plain = mode_fn(cipher, partial_key)
        text = indices_to_text(plain)
        ws = lp_score(plain)

        # Check per-word results
        print(f"    Word score: {ws}")
        print(f"    Decoded first 120 chars: {text[:120]}")

        # Show per-word decoded
        words_decoded = []
        for word_start, word_runes in words:
            p = mode_fn(word_runes, [partial_key[(word_start+i)%period] for i in range(len(word_runes))])
            wtext = indices_to_text(p)
            words_decoded.append(wtext)
        print(f"    First 20 words: {' | '.join(words_decoded[:20])}")
        print()

        # Check phrases
        LP_PHRASES = [
            'BELIEVENOTHING', 'TESTTHEKNOWLEDGE', 'FINDYOURTRUTH',
            'EXPERIENCEYOURDEATH', 'ALLTHINGSSHOULDBEENCRYPTED',
            'THEPRIMESARESACRED', 'THETOTIENTFUNCTION',
            'QUESTIONALLTHINGS', 'COMMANDYOUROWNSELF',
            'EACHINTELLIGENCEISHOLY', 'FORALLTHATLIVEISHOLY',
            'YOUAREABEINGUNTOYOURSELF', 'YOUAREALAWUNTOYOURSELF',
            'JOURNEYDEEPWITHIN', 'LIKETHEINSTSAR',
            'WELCOMEPILGRIM', 'GREATJOURNEY', 'ENDOFALLTHINGS',
            'PROGRAMYOURMIND', 'PROGRAMREALITY',
            'THELOSSOFDIUINITY', 'THELOSSOFDIUINITY',
            'REARRANGINGTHEPRIMES', 'PATHTOTHDEOR',
            'BEINGOFALLI', 'SWORNTOTHEONE', 'SOMEWISDOM',
        ]
        found = [p for p in LP_PHRASES if p in text.replace(' ', '')]
        if found:
            print(f"    !!!! LP PHRASES FOUND: {found}")

        best_overall.append((ws, partial_key, mode_name, text, key_confidence))

    # Sort by word score
    best_overall.sort(reverse=True)
    print("\n  === TOP RESULTS ===")
    for ws, key, mode, text, conf in best_overall[:3]:
        print(f"  Mode={mode} score={ws}")
        print(f"  Key: {key}")
        print(f"  Text: {text[:200]}")
        print()

    # Try exhaustive key refinement on best result
    print("  === BRUTE-FORCE REFINEMENT (cycle through uncertain positions) ===")
    best_ws, best_key, best_mode, best_text, best_conf = best_overall[0]
    mode_fn = MODES[best_mode]

    # Find key positions with low confidence → try all 29 values
    uncertain = [i for i, c in enumerate(best_conf) if c < 0.3]
    print(f"  Positions to refine (confidence < 0.3): {uncertain}")

    if len(uncertain) <= 10:  # Tractable
        print(f"  Trying all 29 values for each of {len(uncertain)} uncertain positions...")
        for kp in uncertain:
            best_pos_score = best_ws
            best_pos_val = best_key[kp]
            for v in range(N):
                trial_key = list(best_key)
                trial_key[kp] = v
                plain = mode_fn(cipher, trial_key)
                ws = lp_score(plain)
                if ws > best_pos_score:
                    best_pos_score = ws
                    best_pos_val = v
            if best_pos_val != best_key[kp]:
                print(f"    Key pos {kp}: {best_key[kp]} → {best_pos_val} (score {best_ws} → {best_pos_score})")
                best_key[kp] = best_pos_val
                best_ws = best_pos_score

        final_plain = mode_fn(cipher, best_key)
        final_text = indices_to_text(final_plain)
        print(f"\n  Final refined decode (mode={best_mode}):")
        print(f"  Key: {best_key}")
        print(f"  Text: {final_text[:200]}")
        print()

        # Show word-by-word
        words_Final = []
        for word_start, word_runes in words:
            p = mode_fn(word_runes, [best_key[(word_start+i)%period] for i in range(len(word_runes))])
            words_Final.append(indices_to_text(p))
        print(f"  Words: {' | '.join(words_Final)}")


if __name__ == '__main__':
    page = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    period = int(sys.argv[2]) if len(sys.argv) > 2 else 17
    solve_with_period(page, period)
