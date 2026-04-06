"""
P02 Simulated Annealing Solver
===============================
Optimizes the 43-position Vigenère key for P02 using:
  - LP/English quadgram scoring
  - F-skip aware decoding
  - Locked anchor: kp[12]=26, kp[13]=9, kp[14]=1 (from "THAT")

P02: 201 runes, key length 43, SUB mode: plain = (cipher - key) % 29
F-skip rule: cipher ᚠ(0) → output F literally, do NOT advance key counter
"""

import os, sys, math, random, time
from collections import defaultdict

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
CONFIRMED = {12: 26, 13: 9, 14: 1}

# Rune alphabet digraph set (for multi-char rune detection)
DIGRAPH_TO_GP = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
MONO_TO_GP = {
    'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
    'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,
    'D':23,'A':24,'Y':26,
}

def parse_cipher(path):
    """Returns list of (is_fskip, cipher_idx) pairs in order."""
    seq = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        # Skip comment/header lines
        if line and not any(c in RUNE_TO_IDX for c in line):
            continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                seq.append(RUNE_TO_IDX[ch])
    return seq

def build_key_mapping(cipher_seq):
    """Build list of (cipher_val, key_pos) for each rune; key_pos=None for F-skip."""
    result = []
    ki = 0
    for c in cipher_seq:
        if c == 0:  # F-skip
            result.append((0, None))
        else:
            result.append((c, ki % KEY_LEN))
            ki += 1
    return result

def decode(kv_pairs, key):
    """Fully decode to list of GP indices."""
    out = []
    for c, kp in kv_pairs:
        if kp is None:
            out.append(0)  # literal F
        else:
            out.append((c - key[kp]) % N)
    return out

def decode_to_latin(kv_pairs, key):
    return ''.join(IDX_TO_LATIN[v] for v in decode(kv_pairs, key))

# ─── Build LP bigram/trigram scorer from LP vocabulary ────────────────────
# Convert LP word list to GP sequence and count bigrams
KOAN_LP_TEXT = """
AKOAN AMAN DECIDED TO GO AND STUDY WITH AMASTER HE WENT TO THE DOOR OF THE MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER
HIS NAME THAT IS NOT WHAT YOU ARE THAT IS JUST THE NAME YOUR PARENTS CALLED YOU
THE STUDENT THOUGHT FOR AMOMENT THEN SAID I AM AHUMAN BEING THAT IS NOT WHAT YOU ARE
EITHER THAT IS JUST THE SPECIES OF THE BODY YOU ARE INHABITING I AM A CONSCIOUSNESS
INHABITING AN ARBITRARY BODY OF THE SPECIES HOMO SAPIENS THE PROFESSOR STARTED
I AM A REPLIED THE STUDENT BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE
TRAILED OFF AFTER A PAUSE THE MASTER TOLD THE STUDENT THAT IS THE CLOSEST ANYONE
HAS COME TO ANSWERING THAT QUESTION CORRECTLY YOU ARE WELCOME TO COME STUDY HERE
AKOAN DURING A LESSON THE MASTER EXPLAINED THE VOICE INSIDE YOUR HEAD IS NOT YOU
IT IS A PROGRAM THAT YOU HAVE INHERITED FROM YOUR ANCESTORS ITS JOB IS TO KEEP YOU
SAFE IT DOES THIS BY COMMENTING ON EVERYTHING THAT HAPPENS AND IMAGINING BAD OUTCOMES
FOR ALL POSSIBLE FUTURES THE VOICE IS NOT YOU YOU ARE THE AWARENESS THAT CAN HEAR
THE VOICE THE STUDENT SAT IN SILENCE FOR A LONG TIME BEFORE ASKING SO WHAT AM I
THE MASTER REPLIED WITH A SMILE THAT IS THE QUESTION FOLLOW THE WHITE RABBIT
THESONG THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH
CAUSE THE LOSS OF DIVINITY CONSUMPTION PRESERVATION ADHERENCE TO CONCEPT
INTELLIGENCE INSTRUCTION COMMAND CNOW YOURSELF DO NOT FOLLOW OTHERS BELIEVE
NOTHING IMPOSE NOTHING QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF
CONSUME THIS AND FIND WHAT IS WITHIN QUESTION ALL THINGS DISCOVER TRUTH
PRIMES TOTIENT SACRED PROGRAM LOOK WITHIN LOOK WITHOUT INTELLIGENCE WISDOM
YOU ARE MADE OF STARDUST AND YOUR HISTORY IS THE UNIVERSE ITSELF
SHADOWS AND BUFFERS AETHEREAL VOID CARNAL FORM MOBIUS ANALOG MOURNFUL CABAL
""".strip()

def build_gp_score_table(text):
    """Build GP bigram frequency table from LP text."""
    bigrams = defaultdict(int)
    trigrams = defaultdict(int)
    
    # Convert text to GP indices
    gp_seq = []
    text = text.upper()
    i = 0
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPH_TO_GP:
            gp_seq.append(DIGRAPH_TO_GP[text[i:i+2]])
            i += 2
        elif text[i] in MONO_TO_GP:
            gp_seq.append(MONO_TO_GP[text[i]])
            i += 1
        else:
            i += 1
    
    for i in range(len(gp_seq)-1):
        bigrams[(gp_seq[i], gp_seq[i+1])] += 1
    for i in range(len(gp_seq)-2):
        trigrams[(gp_seq[i], gp_seq[i+1], gp_seq[i+2])] += 1
    
    # Add English letter frequencies in GP space
    # Common GP bigrams from LP analysis
    common = ['TH','HE','IN','ER','AN','RE','ES','ON','AT','EN','NT','TI','OR',
              'AS','TE','TO','HA','OF','THE','AND','FOR','WITH','THAT']
    for w in common:
        gps = []
        j = 0
        while j < len(w):
            if j+1 < len(w) and w[j:j+2] in DIGRAPH_TO_GP:
                gps.append(DIGRAPH_TO_GP[w[j:j+2]])
                j += 2
            elif w[j] in MONO_TO_GP:
                gps.append(MONO_TO_GP[w[j]])
                j += 1
            else:
                j += 1
        for k in range(len(gps)-1):
            bigrams[(gps[k], gps[k+1])] += 10
        for k in range(len(gps)-2):
            trigrams[(gps[k], gps[k+1], gps[k+2])] += 5
    
    return bigrams, trigrams

# Build the LP word set for word-score
def latin_to_gp(text):
    result = []
    t = text.upper()
    i = 0
    while i < len(t):
        if i+1 < len(t) and t[i:i+2] in DIGRAPH_TO_GP:
            result.append(DIGRAPH_TO_GP[t[i:i+2]])
            i += 2
        elif t[i] in MONO_TO_GP:
            result.append(MONO_TO_GP[t[i]])
            i += 1
        else:
            i += 1
    return result

def parse_word_structure(path):
    """Parse cipher into word-separated list of (encoded_pairs) list."""
    words = []
    cur = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not any(c in RUNE_TO_IDX for c in line):
            continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                cur.append(RUNE_TO_IDX[ch])
            elif ch in '-./':
                if cur:
                    words.append(cur[:])
                    cur = []
    if cur:
        words.append(cur)
    return words

LP_WORDS_SET = set()
LP_WORDS_BY_LEN = defaultdict(list)
for w in KOAN_LP_TEXT.split():
    gp = tuple(latin_to_gp(w))
    if gp:
        LP_WORDS_SET.add(gp)
        LP_WORDS_BY_LEN[len(gp)].append((w, list(gp)))

def score_key(kv_pairs, word_kv_list, key, bigrams, trigrams):
    """Score a key by LP word matches + bigram frequency."""
    # Word score (LP word count * word length)
    word_score = 0
    for word_enc in word_kv_list:
        dec = tuple((c - key[kp]) % N if kp is not None else 0 for c, kp in word_enc)
        if dec in LP_WORDS_SET:
            word_score += len(dec) * 3

    # Bigram/trigram score on full decode
    full = decode(kv_pairs, key)
    bg_score = sum(bigrams.get((full[i], full[i+1]), 0) for i in range(len(full)-1))
    tg_score = sum(trigrams.get((full[i], full[i+1], full[i+2]), 0) for i in range(len(full)-2))
    
    return word_score + bg_score * 0.5 + tg_score * 1.5


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, 'pages', 'page_02', 'runes.txt')

    cipher_seq = parse_cipher(path)
    kv_pairs = build_key_mapping(cipher_seq)
    word_src = parse_word_structure(path)
    
    # Build word_kv_list
    word_kv_list = []
    ki = 0
    for word in word_src:
        word_enc = []
        for c in word:
            if c == 0:
                word_enc.append((0, None))
            else:
                word_enc.append((c, ki % KEY_LEN))
                ki += 1
        word_kv_list.append(word_enc)

    total = len(cipher_seq)
    fskip = sum(1 for c in cipher_seq if c == 0)
    print(f"P02: {total} runes, {fskip} F-skip, {len(word_src)} words")

    bigrams, trigrams = build_gp_score_table(KOAN_LP_TEXT)
    print(f"Scoring table: {len(bigrams)} bigrams, {len(trigrams)} trigrams, {len(LP_WORDS_SET)} LP words")

    # Initial key from previous best + confirmed anchors
    # From p02_crib_drag.py refined run:
    current_key = [7, 2, 6, 27, 7, 12, 23, 25, 13, 19, 28, 4, 26, 9, 1, 19, 19, 2, 16, 17, 17, 8, 4, 1, 2, 9, 24, 0, 0, 23, 5, 2, 7, 27, 0, 16, 23, 28, 19, 8, 20, 26, 22]
    # Apply confirmed
    for kp, kv in CONFIRMED.items():
        current_key[kp] = kv

    current_score = score_key(kv_pairs, word_kv_list, current_key, bigrams, trigrams)
    best_key = list(current_key)
    best_score = current_score

    print(f"Initial score: {current_score:.1f}")
    print(f"Initial decode: {decode_to_latin(kv_pairs, current_key)[:100]}")
    print()

    # ─── Simulated Annealing ──────────────────────────────────────────────
    T = 5.0
    T_min = 0.01
    cooling = 0.999995
    n_iter = 2_000_000
    
    free_positions = [kp for kp in range(KEY_LEN) if kp not in CONFIRMED]

    print(f"Running SA: {n_iter} iterations, {len(free_positions)} free positions...")
    t0 = time.time()

    for it in range(n_iter):
        T *= cooling
        if T < T_min:
            break

        # Random key change: swap one position
        kp = random.choice(free_positions)
        old_v = current_key[kp]
        new_v = random.randint(0, N-1)
        if new_v == old_v:
            continue

        current_key[kp] = new_v
        new_score = score_key(kv_pairs, word_kv_list, current_key, bigrams, trigrams)
        delta = new_score - current_score

        if delta > 0 or random.random() < math.exp(delta / max(T, 1e-9)):
            current_score = new_score
            if new_score > best_score:
                best_score = new_score
                best_key = list(current_key)
        else:
            current_key[kp] = old_v

        if it % 200000 == 0:
            elapsed = time.time() - t0
            print(f"  iter={it:7d} T={T:.3f} cur={current_score:.1f} best={best_score:.1f} [{elapsed:.1f}s]")

    print(f"\nDone in {time.time()-t0:.1f}s, best score: {best_score:.1f}")
    print()

    # Show results
    print("Best key:", best_key)
    print("Key as GP letters:", [IDX_TO_LATIN[v] for v in best_key])
    print()

    full_decode = decode(kv_pairs, best_key)
    full_text = decode_to_latin(kv_pairs, best_key)
    print("Full decode:", full_text)
    print()
    
    # Word-by-word decode
    print("Word-by-word:")
    ki_reset = 0
    for wi, word in enumerate(word_src):
        word_enc = []
        for c in word:
            if c == 0:
                word_enc.append((0, None))
            else:
                word_enc.append((c, ki_reset % KEY_LEN))
                ki_reset += 1
        dec = tuple((c - best_key[kp]) % N if kp is not None else 0 for c, kp in word_enc)
        word_text = ''.join(IDX_TO_LATIN[v] for v in dec)
        is_lp = " ✓" if dec in LP_WORDS_SET else ""
        print(f"  w{wi+1:2d} [{len(word):2d}]: {word_text:20s}{is_lp}")
    
    # Score LP words found
    lp_words_found = sum(1 for wi, word in enumerate(word_src) if True)
    print()
    
    # Compute final word-match count
    ki_r = 0
    matched_words = 0
    matched_chars = 0
    for word in word_src:
        word_enc = []
        for c in word:
            if c == 0:
                word_enc.append((0, None))
            else:
                word_enc.append((c, ki_r % KEY_LEN))
                ki_r += 1
        dec = tuple((c - best_key[kp]) % N if kp is not None else 0 for c, kp in word_enc)
        if dec in LP_WORDS_SET:
            matched_words += 1
            matched_chars += len(dec)
    
    print(f"LP words matched: {matched_words}/{len(word_src)} ({100*matched_words/len(word_src):.1f}%)")
    print(f"LP chars matched: {matched_chars}/{total-fskip} ({100*matched_chars/(total-fskip):.1f}%)")

if __name__ == '__main__':
    main()
