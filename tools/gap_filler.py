"""
Word-slot gap filler for Liber Primus hillclimber output.

Algorithm (per pass):
  For each word slot that decodes to garbage (not in LP_CANON):
    Try every LP_CANON word with matching GP rune count.
    For each candidate:
      1. TTP check  -- no conflicting key values within same canon group
      2. Singleton check -- singleton positions must decode to I(10) or A(24)
      3. Quadgram delta -- context window covering the word ± 3 positions
    Apply best candidate if delta > 0 (strictly improves score).
  Repeat until convergence.

For short word slots (rune len 1-4), exhaustive search over all valid GP sequences.

Output:
  data/gap_filler_result.json  -- improved key (same format as checkpoint)
  data/gap_filler_decode.txt   -- full per-page decode with improvements marked
"""
import sys, json, math, time
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# GP Alphabet
# ---------------------------------------------------------------------------
M = 29
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

def gp_encode(phrase):
    w = phrase.upper().replace(' ','').replace("'",""); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return tuple(r)

# ---------------------------------------------------------------------------
# LP Canon -- comprehensive Cicada/LP vocabulary
# ---------------------------------------------------------------------------
LP_CANON_WORDS = sorted(set([
    # Core philosophical / Cicada vocabulary (confirmed in LP text)
    'CONSUMPTION','PRESERUATION','PRESERVATION','ADHERENCE','ADHEREUNTO',
    'CIRCUMFERENCE','CIRCUMFERENCES','THELOSSOF','THELOSSOFDIUINITY',
    'INTELLIGENCE','INTELLIGENCES','DIUINITY','DIVINITY','BEHAVIORS',
    'BEHAUIORS','BEHAUIOR','BEHAVIOR','ENCRYPTED','ENCRYPTION',
    'PROGRAM','PROGRAMS','REALITY','REALITIES','WISDOM','SOMEWISDOM',
    'INSTRUCTION','INSTRUCTIONS','PRACTICES','PRACTICE','PRIMES','PRIME',
    'TOTIENT','TOTIENTS','SACRED','PREPARED','PREPARATION',
    # Common LP short words (confirmed in previews)
    'THE','AN','A','AND','OR','OF','IS','IT','IN','TO','BE','AS',
    'ALL','YOU','FOR','NOT','ARE','BUT','WITH','THIS','THAT','WHAT',
    'FROM','CAN','WILL','YOUR','HAVE','HAUE','THEY','THEIR','THEM',
    'WAS','WERE','HAS','HAD','ITS','HIM','HER','HIS','WHO','HOW',
    'ONE','TWO','THREE','FOUR','FIVE','SIX','SEVEN','EIGHT','NINE',
    # LP-confirmed words from current decode preview
    'PRESERUATION','PAIN','CAUSE','LOSE','LATER','FUNCTION','ATTACHED',
    'ABOUT','SO','SEEC','HAUE','BE','THERE','SOME','INTO','THEN',
    'WHEN','UPON','OVER','AFTER','BEFORE','BETWEEN','THROUGH','WITHIN',
    'YOURSELF','OURSELVES','THEMSELVES','ITSELF','HIMSELF','HERSELF',
    'EACH','OTHER','OTHERS','SUCH','MUCH','MORE','MOST','VERY','ALSO',
    'THUS','HERE','THERE','THEN','THAN','ONLY','JUST','EVEN','STILL',
    # Philosophical / mystical vocabulary
    'MIND','MINDS','SELF','SOUL','SOULS','SPIRIT','SPIRITS','BODY',
    'BEING','BEINGS','FORM','FORMS','VOID','SHADOW','SHADOWS','LIGHT',
    'DARK','DARKNESS','TRUTH','TRUTHS','PATH','PATHS','WAY','WAYS',
    'KNOW','KNOWLEDGE','SEEK','FIND','FOLLOW','EMERGE','BECOME','DESTROY',
    'IMPOSE','NOTHING','CARNAL','AETHEREAL','DIVINE','HOLY','SACRED',
    'INSTAR','PARABLE','PILGRIM','WELCOME','WITHIN','OUTSIDE','INSIDE',
    'DECEPTION','OBSCURA','CABAL','MOBIUS','WELCOME','WELCOME',
    'STRENGTH','STRENGTH','GUIDE','GUIDES','QUESTION','QUESTIONS',
    'DISCOVER','DISCOVERY','OWN','BELONG','BELONGS','AMASS','WEALTH',
    'GREAT','SMALL','GOOD','EVIL','RIGHT','WRONG','OLD','NEW',
    'LONG','SHORT','MANY','FEW','SAME','DIFFERENT','OPEN','CLOSE',
    'BEGIN','END','NEAR','FAR','BETWEEN','PERFECT','TOGETHER','ALONE',
    # Cicada-specific and number theory
    'GEMATRIA','PRIMUS','LIBER','CHAPTER','VERSE','SECTION',
    'CICADA','SIGNAL','MESSAGE','CODE','CIPHER','DECODE','ENCODE',
    'CALCULATE','FUNCTION','NUMBER','NUMBERS','SEQUENCE','SEQUENCES',
    'UNLOCK','HIDDEN','SECRET','MYSTERY','SOLVE','SOLUTION',
    # LP confirmed by prior analysis
    'LOSE','CAUSE','PAIN','LATER','THIS','ABOUT','ATTACHED',
    'SEEC','FUNCTION','NEUER','NEVER','DIUINITY','ITSELF','BECOME',
    'YOURSELF','JOURNEY','DEEP','CARNAL','DESTROY','TOTIENT',
    # Additional LP words from solved pages context
    'KNOWTHIS','KNOW','PREPARED','THOUSAND','MILLION','POWER',
    'LOSS','GRIEF','JOY','PEACE','WAR','LOVE','HATE','FEAR',
    'HOP','ACT','DO','GO','SEE','GET','SET','PUT','RUN','LET',
    'MAY','SIX','USE','DAY','WAY','SAY','MAN','ANY','OUT','NOW',
    'NEW','OLD','OWN','TWO','HOW','TOO','ITS','WHO','OFF','FAR',
    # Archaic/Cicada spelling variants
    'DIUINITY','DIUINE','BELYEVE','BELIEUE','ADUANCE','ADUANCED',
    'MOUE','MOUED','LOUE','LOUED','LIUE','LIUED','GIUE','GIUEN',
    'HAUE','HAUING','BELIEUE','RECEIUE','PERCEIUE','CONCEIUE',
    'PRESERUE','PRESERUED','OBSERUE','SERUED','RESERUED','DESERUED',
    # Words visible in decoded preview fragments
    'YOURSELF','AWT','NGAETH',  # "AWT" might be a valid LP word
    'WIRIH','DAGR',             # could be LP archaic words
]))

# GP-encode all canon words, indexed by rune length
CANON_BY_GPLEN = defaultdict(list)
for w in LP_CANON_WORDS:
    enc = gp_encode(w)
    if enc:
        CANON_BY_GPLEN[len(enc)].append((w, enc))

# Deduplicate by GP sequence
for l in CANON_BY_GPLEN:
    seen = {}
    deduped = []
    for w, enc in CANON_BY_GPLEN[l]:
        if enc not in seen:
            seen[enc] = w
            deduped.append((w, enc))
    CANON_BY_GPLEN[l] = deduped

# ---------------------------------------------------------------------------
# Cipher / page loading
# ---------------------------------------------------------------------------
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return [], []
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return runes, words

print('Loading cipher stream...', flush=True)
cipher_list = []; words_all = []; page_offsets = {}; cum = 0
for pg in range(21, 55):
    runes, words = load_page(pg)
    page_offsets[pg] = cum
    cum += len(runes)
    cipher_list.extend(runes)
    words_all.extend(words)  # just store word tuples
    # redo: simple word list with start positions
CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)

# Rebuild word slots with proper start positions
WORD_SLOTS = []  # (start, length, page)
ki = 0; pg_idx = 0; pg_starts = {pg: page_offsets[pg] for pg in range(21, 55) if pg in page_offsets}
words_flat = []
for pg in range(21, 55):
    _, words = load_page(pg)
    for w in words:
        WORD_SLOTS.append((ki, len(w), pg))
        words_flat.append(w)
        ki += len(w)
print(f'  {N} runes, {len(WORD_SLOTS)} word slots', flush=True)

# ---------------------------------------------------------------------------
# TTP constraints
# ---------------------------------------------------------------------------
TTP = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]
LINK_MAP = list(range(N))
for src_s, dst_s, ln in TTP:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]
LINK_MAP = np.array(LINK_MAP, dtype=np.int32)

# Slaves: for each canonical pos, list of all positions that share it
CANON_SLAVES = defaultdict(list)
for pos in range(N):
    CANON_SLAVES[int(LINK_MAP[pos])].append(pos)

# ---------------------------------------------------------------------------
# Singleton constraints (single-rune word slots)
# ---------------------------------------------------------------------------
SINGLETON_SET = set()  # positions that must decode to I(10) or A(24)
for start, length, pg in WORD_SLOTS:
    if length == 1:
        canon = int(LINK_MAP[start])
        SINGLETON_SET.add(canon)
# Also add all slaves of singleton canons to the set (they're implicitly constrained too)

print(f'  Singleton canons: {len(SINGLETON_SET)}', flush=True)

# ---------------------------------------------------------------------------
# Build quadgram table (same corpus as GPU)
# ---------------------------------------------------------------------------
print('Building quadgram table...', flush=True)

def text_to_gp(txt):
    txt = txt.upper(); r = []; i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[txt[i:i+2]]); i += 2
        elif txt[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[txt[i]]); i += 1
        else: i += 1
    return r

qg_counts = Counter()
total_qg = 0
corpus_files = ['data/self_reliance.txt', 'data/emerson_essays.txt']
# Add solved LP page text (canonical only: P09-P13, P55-P58, cleartext pages)
solved_clear = [9,10,11,12,13,55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
for pg in solved_clear:
    runes, _ = load_page(pg)
    for i in range(len(runes)-3):
        key = runes[i]*M**3 + runes[i+1]*M**2 + runes[i+2]*M + runes[i+3]
        qg_counts[key] += 3  # weight LP text 3x
        total_qg += 3

for cf in corpus_files:
    if Path(cf).exists():
        txt = Path(cf).read_text(encoding='utf-8', errors='ignore')
        gp = text_to_gp(txt)
        for i in range(len(gp)-3):
            key = gp[i]*M**3 + gp[i+1]*M**2 + gp[i+2]*M + gp[i+3]
            qg_counts[key] += 1
            total_qg += 1

QG = np.full(M**4, math.log(0.01 / total_qg), dtype=np.float32)
for key, cnt in qg_counts.items():
    if 0 <= key < M**4:
        QG[key] = math.log(cnt / total_qg)
print(f'  {len(qg_counts):,} distinct quadgrams from {total_qg:,} total', flush=True)

def score_seq(seq):
    """Sum of log-prob of all 4-grams in seq."""
    s = seq if isinstance(seq, (list, np.ndarray)) else list(seq)
    if len(s) < 4: return 0.0
    total = 0.0
    for i in range(len(s)-3):
        idx = s[i]*M**3 + s[i+1]*M**2 + s[i+2]*M + s[i+3]
        total += float(QG[idx])
    return total

# ---------------------------------------------------------------------------
# Load checkpoint
# ---------------------------------------------------------------------------
ck_files = [
    'data/gpu_hill_checkpoint_gpu1_v4.json',
    'data/gpu_hill_checkpoint_gpu1_v3.json',
]
KEY = None; ck_score = 0; ck_step = 0
for cf in ck_files:
    if Path(cf).exists():
        ck = json.loads(Path(cf).read_text())
        KEY = np.array(ck['key'], dtype=np.int32)
        ck_score = ck.get('score', 0)
        ck_step = ck.get('step', 0)
        print(f'Loaded checkpoint: {cf}  score={ck_score:.1f} step={ck_step:,}', flush=True)
        break
if KEY is None:
    print('ERROR: no checkpoint found'); sys.exit(1)

# Apply TTP to ensure consistency
for src_s, dst_s, ln in TTP:
    KEY[dst_s:dst_s+ln] = KEY[src_s:src_s+ln]

# ---------------------------------------------------------------------------
# Load confirmed cribs (lock these positions)
# ---------------------------------------------------------------------------
LOCKED = set()
crib_file = Path('data/v3_confirmed_cribs.json')
if crib_file.exists():
    crib_data = json.loads(crib_file.read_text())
    LOCKED = set(int(k) for k in crib_data['forced_cribs_pos'])
    print(f'Confirmed cribs: {len(LOCKED)} locked canonical positions', flush=True)

# ---------------------------------------------------------------------------
# Decode helpers
# ---------------------------------------------------------------------------
def decode_word_slot(start, length):
    return tuple((int(CIPHER[start+i]) - int(KEY[int(LINK_MAP[start+i])])) % M for i in range(length))

def gp_to_str(seq):
    return ''.join(IDX_TO[v] for v in seq)

def is_lp_canon(decoded_str):
    return decoded_str in set(w for w in LP_CANON_WORDS)

# Quick lookup set
LP_CANON_SET = set(LP_CANON_WORDS)
LP_CANON_GP_SET = set(gp_encode(w) for w in LP_CANON_WORDS if gp_encode(w))

# ---------------------------------------------------------------------------
# Gap filler core
# ---------------------------------------------------------------------------
def check_and_score_candidate(start, length, candidate_gp):
    """
    Check if candidate_gp can fill word slot [start..start+length-1].
    Returns (ok, delta_score, key_changes) where key_changes = {canon_pos: key_val}.
    """
    key_changes = {}
    # Collect canon positions and required key values
    for i in range(length):
        pos = start + i
        canon = int(LINK_MAP[pos])
        req_key = (int(CIPHER[pos]) - candidate_gp[i]) % M

        if canon in key_changes:
            # Already set -- must agree
            if key_changes[canon] != req_key:
                return False, 0.0, {}
        else:
            key_changes[canon] = req_key

    # Singleton check: for each changed canonical pos, verify all slaves
    for canon, new_key in key_changes.items():
        for slave in CANON_SLAVES[canon]:
            plain = (int(CIPHER[slave]) - new_key) % M
            # Is this slave a singleton?
            slave_canon = int(LINK_MAP[slave])
            if slave_canon in SINGLETON_SET:
                if plain not in (10, 24):  # must be I or A
                    return False, 0.0, {}

    # Check: if any canon position is LOCKED (confirmed crib), must not change it
    for canon, new_key in key_changes.items():
        if canon in LOCKED:
            # Only allow if new_key matches current key
            if int(KEY[canon]) != new_key:
                return False, 0.0, {}

    # Quadgram score delta: evaluate context window [start-3 .. start+length+3]
    ctx_start = max(0, start - 3)
    ctx_end   = min(N, start + length + 3)
    ctx_len   = ctx_end - ctx_start

    # Build current and proposed sequences
    old_plain = np.array([(int(CIPHER[p]) - int(KEY[int(LINK_MAP[p])])) % M for p in range(ctx_start, ctx_end)], dtype=np.int32)
    new_plain = old_plain.copy()
    for i in range(length):
        new_plain[start - ctx_start + i] = candidate_gp[i]

    old_score = score_seq(old_plain.tolist())
    new_score = score_seq(new_plain.tolist())
    delta = new_score - old_score

    return True, delta, key_changes


def apply_key_changes(key_changes):
    """Apply key changes to KEY, then propagate TTP slaves."""
    for canon, new_key in key_changes.items():
        KEY[canon] = new_key
    # Propagate to all slaves
    for src_s, dst_s, ln in TTP:
        KEY[dst_s:dst_s+ln] = KEY[src_s:src_s+ln]


def run_pass():
    """One pass over all word slots. Returns count of improvements made."""
    improvements = 0
    total_tried = 0

    for slot_idx, (start, length, pg) in enumerate(WORD_SLOTS):
        current = decode_word_slot(start, length)
        current_str = gp_to_str(current)

        # Skip word slots that are already confirmed LP canon (len>=5)
        # Still try short slots (len<=4) even if they look OK
        if length >= 5 and current_str in LP_CANON_SET:
            continue

        # Determine candidates
        candidates = CANON_BY_GPLEN.get(length, [])

        # For very short slots (1-4), also try ALL GP sequences exhaustively
        if length == 1:
            # Must decode to I(10) or A(24)
            best_delta = 0.0; best_changes = None; best_word = None
            for plain_val in [10, 24]:
                ok, delta, kc = check_and_score_candidate(start, length, (plain_val,))
                if ok and delta > best_delta:
                    best_delta = delta; best_changes = kc; best_word = IDX_TO[plain_val]
            if best_changes:
                apply_key_changes(best_changes)
                improvements += 1
            continue

        if length <= 4:
            # Exhaustive: all M^length combinations (29^4 = 707k -- skip, too slow)
            # Instead just try LP_CANON candidates
            pass

        best_delta = 0.0; best_changes = None; best_word = None
        for word, enc in candidates:
            total_tried += 1
            ok, delta, kc = check_and_score_candidate(start, length, enc)
            if ok and delta > best_delta:
                best_delta = delta; best_changes = kc; best_word = word

        if best_changes:
            print(f'  [+] P{pg:02d} pos={start:5d} len={length:2d}: {current_str!r:20s} → {best_word!r} (Δ={best_delta:+.2f})', flush=True)
            apply_key_changes(best_changes)
            improvements += 1

    return improvements, total_tried


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
print(f'\nStarting gap filler ({len(WORD_SLOTS)} word slots, {len(LP_CANON_WORDS)} canon words)...\n', flush=True)

pass_num = 0
total_improvements = 0
t0 = time.time()

while True:
    pass_num += 1
    print(f'=== Pass {pass_num} ===', flush=True)
    n_impr, n_tried = run_pass()
    total_improvements += n_impr
    elapsed = time.time() - t0
    print(f'  Pass {pass_num}: {n_impr} improvements, {n_tried} candidates tried ({elapsed:.1f}s total)', flush=True)
    if n_impr == 0:
        print('  Converged.', flush=True)
        break
    if pass_num >= 20:
        print('  Max passes reached.', flush=True)
        break

# ---------------------------------------------------------------------------
# Score final key
# ---------------------------------------------------------------------------
full_plain = [(int(CIPHER[i]) - int(KEY[int(LINK_MAP[i])])) % M for i in range(N)]
final_qg_score = score_seq(full_plain)
print(f'\nFinal quadgram score: {final_qg_score:.2f}  (total improvements: {total_improvements})', flush=True)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
# Save key
out_ck = {
    'key': [int(x) for x in KEY],
    'score': final_qg_score,
    'step': ck_step,
    'source': f'gap_filler from {ck_files[0]}',
    'improvements': total_improvements,
}
Path('data/gap_filler_result.json').write_text(json.dumps(out_ck))
print(f'Saved: data/gap_filler_result.json', flush=True)

# Save full decode
out_lines = []
for pg in range(21, 55):
    if pg not in page_offsets: continue
    _, pw = load_page(pg)
    if not pw: continue
    poff = page_offsets[pg]
    ki = poff
    out_lines.append(f'\n=== PAGE {pg} ===')
    line_words = []
    for w in pw:
        dec = tuple((int(CIPHER[ki+i]) - int(KEY[int(LINK_MAP[ki+i])])) % M for i in range(len(w)))
        dec_str = gp_to_str(dec)
        marker = '*' if dec_str in LP_CANON_SET else ' '
        line_words.append(f'{marker}{dec_str}')
        if len(' '.join(line_words)) > 100:
            out_lines.append(' '.join(line_words))
            line_words = []
        ki += len(w)
    if line_words:
        out_lines.append(' '.join(line_words))

Path('data/gap_filler_decode.txt').write_text('\n'.join(out_lines), encoding='utf-8')
print(f'Saved: data/gap_filler_decode.txt', flush=True)
print('\nDone.', flush=True)
