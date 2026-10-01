"""
LP Word-Boundary Crib Drag
==========================
Uses a completely different approach from the hillclimber:

1. Cipher preserves word boundaries (spaces/dashes not encrypted)
2. We know EVERY word's rune count from the raw ciphertext
3. We have a large corpus of expected LP vocabulary from solved pages
4. STRATEGY: build a word-length sequence for P21-54, then systematically
   try every phrase from known LP text (matched by word lengths), derive
   the implied key, score using TTP consistency and singleton constraints.

This is O(P * Q) where P = candidate phrases, Q = matching positions.
NO random search. Finds deterministically what's consistent.

Key insight: if a 4-word phrase fits at position W, and TTP says key[W]
must equal key[W+6726], then the SAME key-slot is constrained twice.
We count how many cross-constraints are CONSISTENT for each candidate.
"""

import json, math
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

M = 29
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}
def enc(phrase):
    w = phrase.upper().replace(' ', ''); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP: r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP: r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return r
def dec(seq): return ''.join(IDX_TO[v] for v in seq if 0 <= v < M)

# ─── Load cipher (P21-54) ─────────────────────────────────────────────────────
print('Loading cipher stream...')
cipher_list = []; page_offsets = {}; cum = 0; words_p21_54 = []; word_starts = []
for pg in range(21, 55):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): continue
    text = path.read_text(encoding='utf-8')
    runes_ = []; curr = []
    page_offsets[pg] = cum
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes_.append(RUNE_TO_IDX[ch])
            cipher_list.append(RUNE_TO_IDX[ch])
            curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            word_starts.append(cum + len(cipher_list) - len(runes_) - len(curr)
                                if False else cum)
            # Rebuild correctly below
            curr = []
    cum += len(runes_)

# Redo word extraction properly
cipher_list = []; cum = 0; page_offsets = {}
words_p21_54 = []         # list of (start_pos, rune_list)
for pg in range(21, 55):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): continue
    text = path.read_text(encoding='utf-8')
    page_offsets[pg] = cum
    curr = []; curr_start = cum
    for ch in text:
        if ch in RUNE_TO_IDX:
            cipher_list.append(RUNE_TO_IDX[ch])
            curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words_p21_54.append((curr_start, curr.copy()))
            curr_start = cum + len(cipher_list)  # next position after this word
            curr = []
    if curr:
        words_p21_54.append((curr_start, curr.copy()))
    cum += sum(1 for ch in text if ch in RUNE_TO_IDX)

CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)
print(f'  Cipher: {N} runes, {len(words_p21_54)} words')

# ─── TTP constraints ─────────────────────────────────────────────────────────
TTP = [(3001,9727,1312),(6298,12311,1468),(0,5803,404),(2736,8643,265),(737,8100,172),(910,8273,97)]
LINK_MAP = np.arange(N, dtype=np.int32)
for s, d, l in TTP:
    for i in range(l): LINK_MAP[d+i] = LINK_MAP[s+i]

# Build TTP neighbor map: canonical pos → all positions that share that key slot
from collections import defaultdict
ttp_twins = defaultdict(list)
for i in range(N):
    ttp_twins[int(LINK_MAP[i])].append(i)

# ─── Singleton constraints ────────────────────────────────────────────────────
SING_POS = set(); SING_CIP = {}
for start, word in words_p21_54:
    if len(word) == 1:
        SING_POS.add(start)
        SING_CIP[start] = word[0]

# ─── Load all known LP text from solved pages ─────────────────────────────────
print('Loading LP1 vocabulary...')
solved_pages = list(range(0, 21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
lp_words = []       # list of GP-encoded word lists
for pg in solved_pages:
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): continue
    text = path.read_text(encoding='utf-8')
    curr = []
    for ch in text:
        if ch in RUNE_TO_IDX: curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            lp_words.append(tuple(curr)); curr = []
    if curr: lp_words.append(tuple(curr))

# Also add explicit LP vocabulary phrases (multi-word sequences not in rune pages)
extra_text = [
    "THE PRIMES ARE SACRED",
    "ALL THINGS SHOULD BE ENCRYPTED",
    "SOME WISDOM",
    "AN INSTRUCTION",
    "KNOW THIS",
    "A WARNING",
    "DO NOT",
    "FOLLOW YOUR TRUTH",
    "IMPOSE NOTHING ON OTHERS",
    "QUESTION ALL THINGS",
    "DISCOVER TRUTH INSIDE YOURSELF",
    "PROGRAM YOUR MIND PROGRAM REALITY",
    "THE LOSS OF DIVINITY",
    "CONSUMPTION PRESERVATION ADHERENCE",
    "AMASS GREAT WEALTH",
    "NEVER BECOME ATTACHED",
    "BE PREPARED TO DESTROY ALL THAT YOU OWN",
    "THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS",
    "WHICH CAUSE THE LOSS OF DIVINITY",
]
for phrase in extra_text:
    parts = phrase.split()
    for p in parts:
        w = enc(p)
        if w: lp_words.append(tuple(w))

print(f'  LP vocabulary: {len(lp_words)} known words')

# ─── Build phrase index by word-length sequence ───────────────────────────────
# Key: tuple of word lengths → list of consecutive word sequences with those lengths
print('Building length-keyed phrase index...')
# For n-grams of consecutive LP words (n=2..6)
phrase_by_lengths = defaultdict(list)
for n in range(2, 7):
    for i in range(len(lp_words) - n + 1):
        segment = lp_words[i:i+n]
        lengths = tuple(len(w) for w in segment)
        phrase = [rune for w in segment for rune in w]
        phrase_by_lengths[lengths].append(tuple(phrase))

# Deduplicate
for k in phrase_by_lengths:
    phrase_by_lengths[k] = list(set(phrase_by_lengths[k]))
total_candidates = sum(len(v) for v in phrase_by_lengths.values())
print(f'  Phrase candidates: {total_candidates} unique across {len(phrase_by_lengths)} length-patterns')

# ─── Build word lookup for P21-54 by length sequence ─────────────────────────
# For consecutive words in P21-54, record start pos and lengths
print('Building P21-54 word slots...')
# consecutive word n-grams (n=2..6) indexed by length tuple
slots_by_lengths = defaultdict(list)
for n in range(2, 7):
    for i in range(len(words_p21_54) - n + 1):
        segment = words_p21_54[i:i+n]
        lengths = tuple(len(w) for _, w in segment)
        start_pos = segment[0][0]
        total_len  = sum(len(w) for _, w in segment)
        slots_by_lengths[lengths].append(start_pos)

# ─── Score function: given candidate phrase at start_pos, compute TTP consistency
def score_candidate(phrase_runes, start_pos):
    """
    Returns (n_consistent, n_singleton_ok, n_ttp_matches, n_ttp_conflicts)
    
    For each rune position in the phrase:
      - Derive implied key value (sub mode)
      - Check singleton constraints
      - Check TTP: does the implied key agree with any existing TTP twin?
    """
    phrase = list(phrase_runes)
    n = len(phrase)
    end_pos = start_pos + n
    if end_pos > N: return None

    # Compute implied key values
    implied_key = {}  # canonical_pos → key_val
    consistent = True
    singleton_ok = 0; singleton_total = 0
    ttp_agree = 0; ttp_conflict = 0

    for i in range(n):
        pos = start_pos + i
        if pos >= N: break
        c = int(CIPHER[pos])
        p = phrase[i]
        kv = (c - p) % M

        canon = int(LINK_MAP[pos])

        # Check singleton
        if pos in SING_POS:
            sc = SING_CIP[pos]
            singleton_total += 1
            dec_val = (sc - kv) % M
            if dec_val in (10, 24):
                singleton_ok += 1
            else:
                consistent = False  # hard fail — singletons must be I or A

        # Check TTP consistency
        if canon in implied_key:
            if implied_key[canon] == kv:
                ttp_agree += 1
            else:
                ttp_conflict += 1
                consistent = False  # conflicting TTP constraint
        else:
            implied_key[canon] = kv

    if not consistent:
        return None

    # Check against OTHER phrases' implied keys (cross-phrase TTP)
    # This checks if the implied keys conflict with TTP twins outside this phrase
    # We do this by checking if any TWIN position of a phrase position has
    # a different cipher value that would require a different key
    for i in range(n):
        pos = start_pos + i
        if pos >= N: break
        canon = int(LINK_MAP[pos])
        kv = implied_key.get(canon)
        if kv is None: continue
        # Check all TTP twins of this canonical position
        for twin_pos in ttp_twins[canon]:
            if twin_pos == pos: continue
            twin_c = int(CIPHER[twin_pos])
            # For the twin to be consistent with kv, the decrypt must also be valid LP
            # We just count cross-confirmations (not used to reject here)
            twin_plain = (twin_c - kv) % M
            ttp_agree += 1  # cross-twin consistency (same key → decode)

    return (len(phrase), singleton_ok, ttp_agree, ttp_conflict)

# ─── Run exhaustive search ────────────────────────────────────────────────────
print('\n=== Running exhaustive word-length crib drag ===')
print('(Matching LP phrase sequences by word-length fingerprint)\n')

results = []  # (score, phrase_text, start_pos, details)

matched_length_keys = set(phrase_by_lengths.keys()) & set(slots_by_lengths.keys())
print(f'Length-pattern matches: {len(matched_length_keys)} patterns have both LP phrases and P21-54 slots')

for lengths in sorted(matched_length_keys, key=lambda x: -sum(x)):
    lp_phrases_here = phrase_by_lengths[lengths]
    p21_54_slots    = slots_by_lengths[lengths]

    for start_pos in p21_54_slots:
        for phrase_runes in lp_phrases_here:
            result = score_candidate(phrase_runes, start_pos)
            if result is None: continue
            phrase_len, sing_ok, ttp_agree, ttp_conflict = result

            # Scoring: favour longer phrases, TTP agreement, all singletons OK
            # Filter: require zero TTP conflicts
            if ttp_conflict > 0: continue
            score = phrase_len * 10 + ttp_agree * 5 + sing_ok * 3

            phrase_text = dec(phrase_runes)
            pg = next((p for p in sorted(page_offsets, reverse=True) if page_offsets[p] <= start_pos), '?')
            results.append((score, phrase_text, start_pos, pg, sing_ok, ttp_agree))

results.sort(reverse=True)
print(f'Candidates after TTP filter: {len(results)}')
print()

print('=== TOP 50 CONSISTENT PLACEMENTS ===')
print(f"{'Score':>6} {'Phrase':<40s} {'@':>1} {'Page':>4} {'+Offset':>7} {'TTPagree':>8} {'Singletons':>10}")
print('-' * 90)
seen_phrases = set()
shown = 0
for score, phrase_text, start_pos, pg, sing_ok, ttp_agree in results:
    if shown >= 50: break
    key = (phrase_text[:20], start_pos // 100)  # deduplicate near-duplicates
    if key in seen_phrases: continue
    seen_phrases.add(key)
    offset = start_pos - page_offsets.get(pg, 0)
    print(f'{score:6d}  {phrase_text[:40]:<40s}  P{pg}  +{offset:5d}  {ttp_agree:>8d}  {sing_ok:>10d}')
    shown += 1

print()

# ─── Special analysis: check if LP1 section structure matches P21-54 ─────────
print('=== LP SECTION HEADER SEARCH ===')
print('(Looking for canonical LP section openers at word boundaries)')
section_headers = [
    'AN INSTRUCTION',
    'SOME WISDOM',
    'A KOAN',
    'A WARNING',
    'WELCOME PILGRIM',
    'AN END',
    'THE LOSS OF DIVINITY',
    'THE CIRCUMFERENCE',
    'EPILOGUE',
    'CHAPTER',
]
for header in section_headers:
    header_enc = enc(header)
    header_len = len(header_enc)
    # Check only at word-boundary positions (start of a word slot)
    word_start_set = {start for start, _ in words_p21_54}
    for start_pos in sorted(word_start_set):
        if start_pos + header_len > N: continue
        result = score_candidate(tuple(header_enc), start_pos)
        if result is None: continue
        phrase_len, sing_ok, ttp_agree, ttp_conflict = result
        if ttp_conflict > 0: continue
        pg = next((p for p in sorted(page_offsets, reverse=True) if page_offsets[p] <= start_pos), '?')
        offset = start_pos - page_offsets.get(pg, 0)
        print(f'  {header:<30s} @P{pg}+{offset:4d} — TTPagree:{ttp_agree}, singletons:{sing_ok}')

print()

# ─── Also check current hillclimber best key for comparison ──────────────────
ck_path = Path('data/gpu_hill_checkpoint_gpu1.json')
if ck_path.exists():
    ck = json.loads(ck_path.read_text())
    KEY = np.array(ck['key'], dtype=np.int32)[LINK_MAP]
    PLAIN = (CIPHER - KEY) % M
    print(f'=== CURRENT HILLCLIMBER DECODE (step {ck["step"]:,}, score {ck["score"]:.1f}) ===')
    print('First 50 words:')
    ki = 0
    for j, (start, word) in enumerate(words_p21_54[:50]):
        decoded = ''.join(IDX_TO[(c - int(KEY[start + k])) % M] for k, c in enumerate(word))
        print(f'  [{decoded}]', end='')
        if j % 8 == 7: print()
    print()
