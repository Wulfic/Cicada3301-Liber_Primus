"""
P02 Focused Crib-Drag Solver
============================
Uses:
  1. CONFIRMED anchors: key[12]=26, key[13]=9, key[14]=1 → word "THAT"
  2. Koan-specific vocabulary (both LP1 koans)
  3. F-skip aware key position tracking
  4. Exhaustive position-by-position refinement

Key insight: P02 contains the P06-08 koan about identity ("Who are you?").
Known fragments: SAME AS THAT, THE OTHER, WITH A, THE SONG
"""

import os, sys, itertools
from collections import defaultdict, Counter

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
KEY_LEN = 43

# Build reverse Latin→GP map
DIGRAPH_TO_GP = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
MONO_TO_GP = {
    'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
    'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,
    'D':23,'A':24,'Y':26,
}

def latin_to_gp(text):
    result = []
    t = text.upper()
    i = 0
    while i < len(t):
        if i + 1 < len(t) and t[i:i+2] in DIGRAPH_TO_GP:
            result.append(DIGRAPH_TO_GP[t[i:i+2]])
            i += 2
        elif t[i] in MONO_TO_GP:
            result.append(MONO_TO_GP[t[i]])
            i += 1
        else:
            i += 1  # skip unmappable chars
    return result

def parse_p02(path):
    """Parse P02 runes file. Returns list of word-lists (each word = list of (is_fskip, cipher_value, orig_char))."""
    words = []
    cur = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        ascii_a = sum(1 for c in line if c.isascii() and c.isalpha())
        rune_c = sum(1 for c in line if c in RUNE_TO_IDX)
        if ascii_a > 0 and rune_c == 0: continue
        if ascii_a > 2 and rune_c < ascii_a: continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                v = RUNE_TO_IDX[ch]
                cur.append(v)
            elif ch in '-./&$':
                if cur:
                    words.append(cur[:])
                    cur = []
    if cur:
        words.append(cur)
    return words

def build_word_key_positions(words):
    """For each word, record (word_cipher_list, [key_positions]) using F-skip aware counting."""
    result = []
    ki = 0  # key counter (doesn't advance for F-skip runes)
    for word in words:
        word_kps = []
        word_enc = []  # (cipher_val, key_pos_or_None)
        for c in word:
            if c == 0:  # F-skip
                word_enc.append((0, None))
            else:
                word_enc.append((c, ki % KEY_LEN))
                ki += 1
        result.append(word_enc)  # list of (cipher, key_pos or None)
    return result

def decode_word(word_enc, key):
    """Decode a word's encoded pairs using given key array."""
    out = []
    for c, kp in word_enc:
        if kp is None:  # F-skip
            out.append(0)
        else:
            out.append((c - key[kp]) % N)
    return out

def gp_to_text(gp_list):
    return ''.join(IDX_TO_LATIN[i] for i in gp_list)

# ─── Koan + LP vocabulary ─────────────────────────────────────────────────────
KOAN_VOCAB_LATIN = [
    # LP standard
    'A', 'AN', 'THE', 'OF', 'AND', 'TO', 'IS', 'IT', 'OR', 'IN', 'ON', 'AT',
    'HE', 'HIS', 'HIM', 'WAS', 'HAD', 'FOR', 'BUT', 'ARE', 'NOT', 'YOU', 'WHO',
    'BE', 'THIS', 'THAT', 'WHAT', 'YOUR', 'WITH', 'WILL', 'HAVE', 'FROM', 'ALL',
    'THEY', 'THEM', 'THEN', 'WHEN', 'THAN', 'ALSO', 'ONLY', 'WELL', 'SOME',
    # Koan P06-P08 specific
    'AKOAN', 'KOAN',
    'MAN', 'AMAN',
    'DECIDED', 'DECIDE',
    'GO', 'WENT',
    'STUDY', 'STUDYING',
    'MASTER', 'AMASTER',
    'DOOR',
    'WISHES', 'WISH',
    'STUDENT', 'ASTUDENT',
    'TOLD', 'SAID', 'ASKED', 'REPLIED', 'ANSWERED',
    'NAME', 'ANAME',
    'CALLED',
    'THOUGHT', 'THINK',
    'MOMENT', 'AMOMENT',
    'PROFESSOR', 'APROFESSOR',
    'HUMAN', 'AHUMAN',
    'BEING', 'ABEING',
    'SPECIES', 'MYSPECIES',
    'CONFUSED',
    'CONSCIOUSNESS', 'ACONSCIOUSNESS',
    'INHABITING', 'ARBITRARY', 'BODY', 'ABODY',
    'MERELY', 'MERELY',
    'GETTING', 'IRRITATED',
    'STARTED', 'START',
    'THINK', 'THINKING',
    'ANYTHING', 'ELSE',
    'TRAILED', 'OFF',
    'AFTER', 'ALONG',
    'PAUSE',
    'WELCOME', 'COME',
    'HERE',
    'SAME', 'SAMEAS', 'SAME AS',
    'OTHER', 'ANOTHER', 'THEOTHER', 'THEOTHERSTUDENT',
    'SONG', 'THESONG', 'ASONG',
    'IDENTITY', 'SELF',
    'INNER', 'VOICE', 'INNERVOICE',
    # Koan P14-15 specific (voice in head)
    'LESSON', 'ALESSON',
    'EXPLAINED', 'EXPLAIN',
    'DURING', 'DURNG',
    'SOUND', 'ASOUND',
    'INSIDE', 'OUTSIDE',
    'HEAR', 'HEARD',
    'SPEAKING', 'SPEAKS',
    'LISTEN',
    # LP core content
    'WISDOM', 'TRUTH', 'KNOWLEDGE', 'FOLLOW', 'BELIEVE', 'BELIEUE', 'NEUER',
    'SACRED', 'HOLY', 'DIVINE', 'DIUINE', 'DIVINITY', 'DIUINITY',
    'MIND', 'REALITY', 'WORLD', 'PROGRAM', 'PRIMES', 'TOTIENT',
    'INTELLIGENCE', 'INSTRUCTION', 'COMMAND', 'DISCOVER', 'DISCOUER',
    'QUESTION', 'CUESTION', 'CNOW', 'KNOW', 'IMPOSE', 'NOTHING',
    'WITHIN', 'PILGRIM', 'JOURNEY', 'END', 'EMERGE', 'INSTAR', 'LIKE',
    'SHED', 'CIRCUMFERENCE', 'CIRCUMFERENCES',
    'CONSUMPTION', 'PRESERVATION', 'PRESERUATION', 'ADHERENCE',
    'LOSS', 'BEHAVIORS', 'BEHAUIORS', 'CAUSE',
    'THELOSSOF', 'THELOSS',
    'CHAPTER', 'INTUS', 'WARNING', 'BELIEVE', 'EXPERIENCE',
    'DEATH', 'PATH', 'DEEP', 'WEB', 'PAGE', 'SEEK', 'OUT',
    'GREAT', 'NECESSARY', 'STRUGGLE', 'SUFFERING',
    'INNOCENCE', 'ILLUSIONS', 'CERTAINTY',
    'SHAPE', 'OURSELVES', 'REALITIES',
    'LIBER', 'PRIMUS', 'CABAL', 'SHADOWS', 'AETHEREAL',
    'VOID', 'CARNAL', 'OBSCURA', 'FORM', 'MOBIUS', 'ANALOG', 'MOURNFUL',
    'DECEPTION', 'PROGRAM', 'INTELLIGENCE', 'AMASS', 'WEALTH', 'DESTROY',
    'ATTACHEDTO', 'ATTACHED', 'PREPARED',
    'PRESERUATION', 'SOMEWISDOM', 'KNOWTHIS', 'CNOWTHIS',
    'THISMESSAGE', 'ENCRYPT', 'ENCRYPTED', 'ALLTHINGS',
    'FOLLOWYOUR', 'FOLLOWTHIS',
    'DEOR', 'REARRANGING', 'PRIMES', 'NUMBERS', 'SHOW',
    'WORDS', 'NUMBERS',
]

# Convert to GP index sequences, deduplicated by length
LP_WORDS_BY_LEN = defaultdict(list)
for w in KOAN_VOCAB_LATIN:
    gp = latin_to_gp(w)
    if gp and len(gp) >= 1:
        LP_WORDS_BY_LEN[len(gp)].append((w, gp))

# Remove duplicates
for L in LP_WORDS_BY_LEN:
    seen = set()
    deduped = []
    for name, gp in LP_WORDS_BY_LEN[L]:
        key = tuple(gp)
        if key not in seen:
            seen.add(key)
            deduped.append((name, gp))
    LP_WORDS_BY_LEN[L] = deduped


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, 'pages', 'page_02', 'runes.txt')

    words_raw = parse_p02(path)
    word_enc_list = build_word_key_positions(words_raw)

    total_runes = sum(len(w) for w in words_raw)
    fskip_count = sum(1 for we in word_enc_list for c, kp in we if kp is None)
    print(f"P02: {total_runes} total runes, {fskip_count} F-skip, {len(words_raw)} words")

    # ─── Key vote table ─────────────────────────────────────────────────────
    # For each (kp, kv), count how many LP word cribs support it
    CONFIRMED = {12: 26, 13: 9, 14: 1}  # from "THAT" decode; verified correct
    
    # Build vote table: kp → Counter(kv → count)
    votes = defaultdict(Counter)  # SUB mode: key = (cipher - plain) % N
    crib_count = 0

    for wi, word_enc in enumerate(word_enc_list):
        # Count non-F runes in this word to get effective word length for key purposes
        eff_len = sum(1 for c, kp in word_enc if kp is not None)
        
        # All cipher values in word (for matching length)
        full_len = len(word_enc)  # total cipher runes including F-skip

        # Try all LP/koan words of the same full length (F-skip positions match F in vocab)
        for vocab_name, vocab_gp in LP_WORDS_BY_LEN.get(full_len, []):
            # Derive key values this crib would require
            derived = {}
            consistent = True
            for j, (c, kp) in enumerate(word_enc):
                if kp is None:  # F-skip
                    # Plain must be F(0), and vocab must be F(0) at this position
                    if vocab_gp[j] != 0:
                        consistent = False; break
                    continue
                p = vocab_gp[j]
                kv = (c - p) % N
                # Check against confirmed anchors
                if kp in CONFIRMED and CONFIRMED[kp] != kv:
                    consistent = False; break
                if kp in derived and derived[kp] != kv:
                    consistent = False; break
                derived[kp] = kv
            
            if consistent:
                for kp, kv in derived.items():
                    votes[kp][kv] += 1
                crib_count += 1

    print(f"LP crib attempts: {crib_count}")
    print()

    # Apply confirmed anchors to votes (override with highest confidence)
    for kp, kv in CONFIRMED.items():
        votes[kp] = Counter({kv: 9999})

    # Best key
    best_key = [0] * KEY_LEN
    confidence = []
    for kp in range(KEY_LEN):
        if kp in CONFIRMED:
            best_key[kp] = CONFIRMED[kp]
            confidence.append(1.0)
        elif votes[kp]:
            mv, mc = votes[kp].most_common(1)[0]
            total = sum(votes[kp].values())
            best_key[kp] = mv
            confidence.append(mc / total)
        else:
            # No data — fall back to KNOWN
            KNOWN_FALLBACK = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20,
                              1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9,
                              22, 26, 22, 15]
            best_key[kp] = KNOWN_FALLBACK[kp]
            confidence.append(0.0)

    print(f"Key confidence (avg={sum(confidence)/len(confidence):.3f}):")
    for kp in range(KEY_LEN):
        top3 = votes[kp].most_common(3) if kp in votes else []
        top3_str = ', '.join(f'{v}:{c}' for v,c in top3)
        print(f"  kp{kp:2d}: key={best_key[kp]:2d} ({IDX_TO_LATIN[best_key[kp]]:3s}) conf={confidence[kp]:.2f}  votes=[{top3_str}]")
    print()

    # ─── Decode with best key ────────────────────────────────────────────────
    print("Word-by-word decode:")
    all_decoded = []
    for wi, word_enc in enumerate(word_enc_list):
        dec = decode_word(word_enc, best_key)
        word_text = gp_to_text(dec)
        full_len = len(word_enc)
        eff_len = sum(1 for _, kp in word_enc if kp is not None)
        
        # Check if this word matches any LP/koan vocab
        matches = [nm for nm, gp in LP_WORDS_BY_LEN.get(full_len, []) if list(gp) == dec]
        match_str = f" ← {matches[0]}" if matches else ""
        
        all_decoded.append(word_text)
        print(f"  w{wi+1:2d} [{full_len}rune]: {word_text:20s}{match_str}")
    print()
    print("Full text:", ' '.join(all_decoded))
    print()

    # ─── Show top alternative words for each slot ─────────────────────────
    print("Top-3 alternative words for each slot:")
    for wi, word_enc in enumerate(word_enc_list):
        full_len = len(word_enc)
        alts = []
        for vocab_name, vocab_gp in LP_WORDS_BY_LEN.get(full_len, []):
            # Check if consistent with confirmed
            ok = True
            for j, (c, kp) in enumerate(word_enc):
                if kp is None:
                    if vocab_gp[j] != 0: ok = False; break
                    continue
                kv = (c - vocab_gp[j]) % N
                if kp in CONFIRMED and CONFIRMED[kp] != kv:
                    ok = False; break
            if ok:
                # Score by how well it matches best_key
                score = sum(1 for j,(c,kp) in enumerate(word_enc) if kp is not None and best_key[kp] == (c - vocab_gp[j]) % N)
                alts.append((score, vocab_name, vocab_gp))
        alts.sort(reverse=True)
        if alts:
            top = alts[:3]
            print(f"  w{wi+1:2d}: {[f'{nm}({sc})' for sc,nm,gp in top]}")
    
    # ─── Exhaustive refinement on low-confidence positions ─────────────────
    print()
    print("Brute-force single-position refinement:")
    
    def score_key(key):
        """Score by counting exact LP word matches across all slots."""
        total = 0
        for we in word_enc_list:
            dec = decode_word(we, key)
            L = len(we)
            for nm, gp in LP_WORDS_BY_LEN.get(L, []):
                if list(gp) == dec:
                    total += len(gp)  # weight by length
                    break
        return total

    current_score = score_key(best_key)
    print(f"  Starting score: {current_score}")

    improved = True
    while improved:
        improved = False
        for kp in range(KEY_LEN):
            if kp in CONFIRMED: continue
            best_v = best_key[kp]
            best_s = current_score
            for v in range(N):
                if v == best_key[kp]: continue
                trial = list(best_key)
                trial[kp] = v
                s = score_key(trial)
                if s > best_s:
                    best_s = s
                    best_v = v
            if best_v != best_key[kp]:
                print(f"    kp{kp:2d}: {best_key[kp]:2d}→{best_v:2d} (score {current_score}→{best_s})")
                best_key[kp] = best_v
                current_score = best_s
                improved = True

    print(f"  Final score: {current_score}")
    print()

    # Final decode
    print("FINAL DECODE:")
    final_words = []
    for we in word_enc_list:
        dec = decode_word(we, best_key)
        final_words.append(gp_to_text(dec))
    print(' '.join(final_words))
    print()
    print(f"Final key: {best_key}")

if __name__ == '__main__':
    main()
