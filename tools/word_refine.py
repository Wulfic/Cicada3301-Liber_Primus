"""
word_refine.py — Word-boundary-aware key refinement for the LP hillclimber.

Takes the current best key from the GPU checkpoint and applies deterministic
LP-vocabulary-guided corrections. Works on _word_ boundaries (preserved in the
cipher): for each word slot, computes edit-distance to known LP words of the
same length, and if an LP word is ≤2 edits away AND the key change is TTP-
consistent, locks that word.

This is a complementary approach: the GPU hillclimber optimizes character-level
quadgram statistics, but this tool optimizes word-level coherence.

Usage:
  python Tools/word_refine.py [--apply]
    --apply  : write the refined key back to the checkpoint
    (default): dry-run — show what would change, don't modify checkpoint
"""

import json, sys, os, math
from pathlib import Path
from collections import Counter
import numpy as np

M = 29

# ── GP Alphabet (same as gpu_hillclimber.py) ──────────────────────────────────
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}

def encode(text):
    text = text.upper()
    enc = []
    i = 0
    while i < len(text):
        d = text[i:i+2]
        if d in LETTER_TO_GP:
            enc.append(LETTER_TO_GP[d]); i += 2
        elif text[i] in LETTER_TO_GP:
            enc.append(LETTER_TO_GP[text[i]]); i += 1
        else:
            i += 1
    return tuple(enc)

def gp_to_text(indices):
    return ''.join(IDX_TO[i] if 0 <= i < len(IDX_TO) else '?' for i in indices)

# ── Load cipher ───────────────────────────────────────────────────────────────
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return [], []
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []; ws = 0
    for ch in text:
        if ch in RUNE_TO_IDX:
            if not curr: ws = len(runes)
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append((ws, tuple(curr))); curr = []
    if curr: words.append((ws, tuple(curr)))
    return runes, words

print('Loading cipher...')
cipher_list = []; word_slots = []; page_offsets = {}; cum = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes:
        page_offsets[pg] = cum
        for ws, wv in words:
            word_slots.append((cum + ws, wv))  # (global_start, cipher_rune_tuple)
        cum += len(runes)

CIPHER = np.array(cipher_list if cipher_list else [r for pg in range(21,55) for r in load_page(pg)[0]], dtype=np.int32)
# Rebuild properly
cipher_list = []
word_slots = []; page_offsets = {}; cum = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes:
        page_offsets[pg] = cum
        for ws, wv in words:
            word_slots.append((cum + ws, wv))
        cum += len(runes)
        cipher_list.extend(runes)
CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)
print(f'  {N} runes, {len(word_slots)} words')

# ── TTP link map ──────────────────────────────────────────────────────────────
TTP_PAIRS = [
    (0, 1312, 6727, 1312), (1312, 1423, 8139, 1423),
    (2735, 265, 6727, 265), (3001, 178, 9727, 178),
    (3179, 237, 9905, 237), (3417, 301, 10143, 301),
]
LINK_MAP = np.arange(N, dtype=np.int32)
ttp_twins = {}  # canonical → list of all positions sharing that key
for a_start, a_len, b_start, b_len in TTP_PAIRS:
    span = min(a_len, b_len, max(0, N-a_start), max(0, N-b_start))
    for k in range(span):
        pa, pb = a_start+k, b_start+k
        if pa < N and pb < N:
            canon = min(pa, pb)
            LINK_MAP[pa] = canon
            LINK_MAP[pb] = canon
            ttp_twins.setdefault(canon, set()).add(pa)
            ttp_twins.setdefault(canon, set()).add(pb)

# Singleton positions
SING_SET = set()
for pg in range(21, 55):
    _, words = load_page(pg)
    for ws, wv in words:
        if len(wv) == 1:
            gpos = page_offsets.get(pg, 0) + ws
            SING_SET.add(gpos)

# ── Confirmed cribs (locked — never change these) ────────────────────────────
CONFIRMED_CRIBS = [
    ('CONSUMPTION',31), ('KNOWTHIS',476), ('PROGRAM',599),
    ('DIUINITY',1356), ('PRESERUATION',2093), ('CIRCUMFERENCE',3080),
    ('SOMEWISDOM',4131), ('THELOSSOFDIUINITY',4325), ('ADHERENCE',8532),
]
LOCKED = set()
for phrase, start in CONFIRMED_CRIBS:
    enc = encode(phrase)
    for i in range(len(enc)):
        LOCKED.add(int(LINK_MAP[start+i]))

# ── Load checkpoint ───────────────────────────────────────────────────────────
print('Loading checkpoint...')
ck = json.load(open('data/gpu_hill_checkpoint_gpu1.json'))
KEY = np.array(ck['key'], dtype=np.int32)
step = ck['step']
score = ck['score']
print(f'  Step {step}, score {score:.1f}')

# ── LP vocabulary — comprehensive word list ───────────────────────────────────
# Build from solved LP pages
lp_words_by_len = {}  # length → set of GP tuples

# Load all solved-page words
solved_pages = list(range(0,21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
for pg in solved_pages:
    _, words = load_page(pg)
    for _, wv in words:
        ln = len(wv)
        if ln >= 2:  # skip single-rune words for now
            lp_words_by_len.setdefault(ln, set()).add(wv)

# Also add known LP phrases broken into words
phrases = """
AN INSTRUCTION SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED
KNOW THIS WARNING WELCOME PILGRIM LOSS DIVINITY DIUINITY CIRCUMFERENCE PRACTICES
THREE BEHAVIORS CAUSE CONSUMPTION PRESERVATION PRESERUATION ADHERENCE AMASS GREAT
WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN PREPARED DESTROY PROGRAM YOUR MIND
REALITY SEEK TRUTH WITHIN FOLLOW QUESTION DISCOVER INSIDE YOURSELF IMPOSE NOTHING
OTHERS CHAPTER PARABLE SACRED FORM MOBIUS AETHEREAL ETHEREAL CARNAL OBSCURA BUFFER
DECEPTION VOID PATTERN SHADOW LIGHT DARKNESS ONENESS DEATH LIFE SPIRITUAL MORTAL
DIVINE BEING PATH WALK CEASING CEASE KNOWLEDGE BUILD BEGIN DETAIL PROFUNDITY
WHOLE SIMPLY STRONG STRONGENCE EMERGE WILL EVERY DEEP ABOVE SAME OTHER ONE FROM
AND FOR BUT NOT WITH HAVE THAT WHICH OF THINGS WORTH PRESERVING
""".split()
for w in phrases:
    enc = encode(w)
    if len(enc) >= 2:
        lp_words_by_len.setdefault(len(enc), set()).add(enc)

total_vocab = sum(len(v) for v in lp_words_by_len.values())
print(f'  LP vocabulary: {total_vocab} words across lengths {sorted(lp_words_by_len.keys())}')

# ── Decode current key ────────────────────────────────────────────────────────
def decode_word(start, length):
    """Decode cipher word at position start with current KEY."""
    return tuple((int(CIPHER[start+i]) - int(KEY[start+i])) % M for i in range(length))

def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))

# ── Find near-matches ────────────────────────────────────────────────────────
print('\n=== Scanning word slots for LP near-matches ===\n')

corrections = []  # (word_start, current_decode, best_match_word, best_match_text, ham_dist, edits)

for word_start, cipher_word in word_slots:
    wlen = len(cipher_word)
    if wlen < 2 or wlen > 20:
        continue

    current_plain = decode_word(word_start, wlen)
    current_text = gp_to_text(current_plain)

    # Check if any position in this word is locked
    word_positions = list(range(word_start, word_start + wlen))
    any_locked = any(int(LINK_MAP[p]) in LOCKED for p in word_positions)

    # Get LP words of same length
    candidates = lp_words_by_len.get(wlen, set())
    if not candidates:
        continue

    # Find best match by Hamming distance
    best_match = None
    best_ham = wlen + 1  # impossibly high

    for cand in candidates:
        h = hamming(current_plain, cand)
        if h < best_ham:
            best_ham = h
            best_match = cand

    if best_match is None:
        continue

    # Only care about close matches (≤30% positions differ, at least 1 change)
    if best_ham == 0:
        continue  # already matches
    if best_ham > max(2, wlen // 3):
        continue  # too far

    # Check TTP consistency of proposed change
    proposed_key_changes = {}  # canonical_pos → new_key_value
    ttp_ok = True
    for i in range(wlen):
        pos = word_start + i
        if current_plain[i] == best_match[i]:
            continue  # no change needed at this position
        canon = int(LINK_MAP[pos])
        if canon in LOCKED:
            ttp_ok = False  # would modify a locked crib position
            break
        new_key = (int(CIPHER[pos]) - best_match[i]) % M
        if canon in proposed_key_changes:
            if proposed_key_changes[canon] != new_key:
                ttp_ok = False
                break
        else:
            proposed_key_changes[canon] = new_key

    if not ttp_ok:
        continue

    # Check that key changes don't conflict with existing key at TTP twin positions
    # For each changed canonical position, check if any twin positions (outside this word)
    # would produce worse decodes
    twin_ok = True
    twin_effects = []
    for canon, new_kv in proposed_key_changes.items():
        twins = ttp_twins.get(canon, set())
        for tp in twins:
            if word_start <= tp < word_start + wlen:
                continue  # within the same word
            old_plain_at_twin = (int(CIPHER[tp]) - int(KEY[tp])) % M
            new_plain_at_twin = (int(CIPHER[tp]) - new_kv) % M
            twin_effects.append((tp, old_plain_at_twin, new_plain_at_twin))

    cand_text = gp_to_text(best_match)
    corrections.append((word_start, wlen, current_text, cand_text, best_ham,
                         proposed_key_changes, twin_effects, any_locked))

# Sort by hamming distance (closest matches first), then by word length (longer = more confident)
corrections.sort(key=lambda x: (x[4], -x[1]))

# ── Display results ───────────────────────────────────────────────────────────
print(f'Found {len(corrections)} word correction candidates\n')
print(f'{"g.pos":>6s}  {"len":>3s}  {"ham":>3s}  {"Current":>15s} → {"LP Match":>15s}  {"Twin effects":>20s}')
print('-' * 85)

apply_mode = '--apply' in sys.argv
applied = 0
skipped = 0

for word_start, wlen, cur_text, cand_text, ham, key_changes, twin_fx, any_locked in corrections[:80]:
    # Evaluate twin effects: count how many twin positions improve vs degrade
    twin_improve = sum(1 for _, old_p, new_p in twin_fx if new_p in (10, 24) and old_p not in (10, 24))
    twin_degrade = sum(1 for _, old_p, new_p in twin_fx if old_p in (10, 24) and new_p not in (10, 24))

    flag = ''
    if any_locked:
        flag = ' [LOCKED]'
    elif twin_degrade > 0:
        flag = f' [TWIN-DEG:{twin_degrade}]'
    elif ham == 1 and wlen >= 5:
        flag = ' *** HIGH-CONF ***'
    elif ham == 1:
        flag = ' ** likely **'
    elif ham == 2 and wlen >= 8:
        flag = ' * possible *'

    print(f'{word_start:6d}  {wlen:3d}  {ham:3d}  {cur_text:>15s} → {cand_text:>15s}  '
          f'twins:{len(twin_fx):2d} +{twin_improve}/-{twin_degrade}{flag}')

    # Apply if --apply and safe
    if apply_mode and not any_locked and twin_degrade == 0 and ham <= 2 and wlen >= 5:
        for canon, new_kv in key_changes.items():
            # Apply to ALL positions linked to this canonical position
            for pos in range(N):
                if int(LINK_MAP[pos]) == canon:
                    KEY[pos] = new_kv
        applied += 1

# ── Summary statistics ────────────────────────────────────────────────────────
ham1_count = sum(1 for *_, ham, _, _, _ in corrections if ham == 1)
ham2_count = sum(1 for *_, ham, _, _, _ in corrections if ham == 2)
safe_count = sum(1 for _, wl, _, _, ham, _, tf, lk in corrections
                 if not lk and ham <= 2 and wl >= 5
                 and not any(1 for _, o, n in tf if o in (10,24) and n not in (10,24)))

print(f'\n=== Summary ===')
print(f'  Hamming-1 matches: {ham1_count}')
print(f'  Hamming-2 matches: {ham2_count}')
print(f'  Safe to apply (ham≤2, len≥5, no twin degradation): {safe_count}')

if apply_mode:
    print(f'\n  Applied {applied} corrections to key.')
    if applied > 0:
        # Save updated checkpoint
        ck['key'] = KEY.tolist()
        ck['step'] = step  # keep same step
        ck['score'] = score  # will be recalculated by hillclimber
        backup = f'data/gpu_hill_checkpoint_gpu1_pre_refine.json'
        import shutil
        if not os.path.exists(backup):
            shutil.copy('data/gpu_hill_checkpoint_gpu1.json', backup)
            print(f'  Backup saved to {backup}')
        with open('data/gpu_hill_checkpoint_gpu1.json', 'w') as f:
            json.dump(ck, f)
        print(f'  Updated checkpoint saved.')
else:
    print(f'\n  Dry run — run with --apply to modify checkpoint')
    print(f'  NOTE: The hillclimber is still running and will overwrite the checkpoint!')
    print(f'  Stop the hillclimber first if you want to apply refinements.')

print('\nDone.')
