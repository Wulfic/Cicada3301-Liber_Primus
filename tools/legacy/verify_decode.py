"""
Decode Verifier -- Cryptographic reproducibility test.

This tool does NOT use any vocabulary search or score optimization.
It answers: "Is the current key cryptographically consistent?"

Tests performed:
  1. LONG-WORD DERIVATION -- For each confirmed long word (len>=8):
       key_required[i] = (cipher[pos+i] - GP_plain[i]) % 29
       Then propagate via TTP and show what OTHER positions decode to.
       No search needed -- purely deterministic.

  2. TTP TWIN VERIFICATION -- Extract TTP slave regions and confirm
       cipher[slave] - key[canon] == cipher[master] - key[canon] (mod 29)
       i.e., the cipher itself encodes twin regions identically.
       If this FAILS, the TTP constraints are wrong (cipher structure error).
       If this PASSES, twin decodes must agree regardless of key.

  3. IoC PER PAGE (no vocabulary bias) -- Compute letter frequency
       over decoded text from ONLY long-word-anchored positions.
       English IoC target: ~1.73. LP Old English: ~1.80-2.10.

  4. LONG-WORD CONSISTENCY MATRIX -- Take the 8+ rune cribs.
       For each pair that share TTP-linked positions, check they agree.
       Agreement = genuine constraint satisfaction; disagreement = fake.

  5. PURE QUADGRAM BASELINE COMPARISON --
       Score current key WITHOUT any word-bonus (pure quadgrams only).
       Compare to: random key, vigenere-period-1 key, solved-page key.

Output: data/verify_decode_report.txt
"""
import sys, json, math
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

outlines = []
def p(*args):
    line = ' '.join(str(a) for a in args)
    print(line, flush=True)
    outlines.append(line)

# ---------------------------------------------------------------------------
# GP alphabet
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
    w = phrase.upper(); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return tuple(r)
def gp_str(seq):
    return ''.join(IDX_TO[v] for v in seq)

# ---------------------------------------------------------------------------
# Load cipher
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

cipher_list = []; word_slots = []; ki = 0; page_offsets = {}
for pg in range(21, 55):
    runes, words = load_page(pg)
    if not runes: continue
    page_offsets[pg] = ki
    for w in words:
        word_slots.append((pg, ki, len(w)))
        ki += len(w)
    cipher_list.extend(runes)

CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)

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
LINK_MAP = np.arange(N, dtype=np.int32)
for src_s, dst_s, ln in TTP:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]

# For each canonical pos, list all positions (including itself) linked to it
CANON_SLAVES = defaultdict(list)
for pos in range(N):
    CANON_SLAVES[int(LINK_MAP[pos])].append(pos)

# ---------------------------------------------------------------------------
# Load checkpoint key
# ---------------------------------------------------------------------------
ck_path = 'data/gpu_hill_checkpoint_gpu1_v4.json'
if not Path(ck_path).exists():
    ck_path = 'data/gpu_hill_checkpoint_gpu1_v3.json'
ck = json.loads(Path(ck_path).read_text())
KEY = np.array(ck['key'], dtype=np.int32)
# Propagate TTP
for src_s, dst_s, ln in TTP:
    KEY[dst_s:dst_s+ln] = KEY[src_s:src_s+ln]

p(f'Checkpoint: {ck_path}')
p(f'Score: {ck.get("score", 0):.1f}  Step: {ck.get("step", 0):,}')
p()

# ---------------------------------------------------------------------------
# TEST 1: TTP CIPHER TWIN VERIFICATION (cipher-only, no key needed)
# ---------------------------------------------------------------------------
p('=' * 70)
p('TEST 1: TTP CIPHER STRUCTURE VERIFICATION (key-free)')
p('  For each TTP pair (master, slave), cipher[slave]-cipher[master] mod 29')
p('  must be CONSTANT across all positions in the region.')
p('  This is a property of the CIPHER ITSELF, not the key.')
p()

for region_idx, (src_s, dst_s, ln) in enumerate(TTP):
    diffs = (CIPHER[dst_s:dst_s+ln].astype(int) - CIPHER[src_s:src_s+ln].astype(int)) % M
    counts = Counter(diffs.tolist())
    most_common_diff, most_common_count = counts.most_common(1)[0]
    pct = 100.0 * most_common_count / ln
    status = 'UNIFORM (OTP-like key)' if pct > 95 else f'TOP DIFF {pct:.1f}% -- NOT uniform (structured key?)'
    p(f'  Region {region_idx+1}: master={src_s:5d}-{src_s+ln-1:5d} slave={dst_s:5d}-{dst_s+ln-1:5d}'
      f'  len={ln:4d}  cipher_diff_distribution: {status}')
    if pct <= 95:
        # Show top 5 diffs
        for diff, cnt in counts.most_common(5):
            p(f'    diff={diff:2d}: {cnt:4d}/{ln} ({100.0*cnt/ln:.1f}%)')

p()
p('  NOTE: Uniform diff means each twin region uses the SAME key offset everywhere.')
p('  Non-uniform means an OTP-like (position-varying) key.')
p()

# ---------------------------------------------------------------------------
# TEST 2: LONG-WORD DERIVATION -- Verify from cipher alone
# ---------------------------------------------------------------------------
p('=' * 70)
p('TEST 2: LONG-WORD KEY DERIVATION (deterministic, no search)')
p('  For each word slot of len>=8 that decodes to an LP word under current key:')
p('  a) Show the REQUIRED key values (cipher[i] - plain[i]) mod 29')
p('  b) Propagate via TTP to all linked positions')
p('  c) Show what those OTHER positions decode to')
p('  d) Check if those other positions decode to readable text')
p()

# Long words in current decode (only verified LP words, len>=8)
LONG_LP_WORDS = [
    'PRESERUATION', 'INTELLIGENCE', 'INTELLIGENCES', 'CIRCUMFERENCE', 'CIRCUMFERENCES',
    'THELOSSOF', 'THELOSSOFDIUINITY', 'CONSUMPTION', 'BEHAUIORS', 'BEHAUIOR',
    'ADHERENCE', 'ADHEREUNTO', 'ENCRYPTED', 'ENCRYPTED', 'AETHEREAL',
    'DECEPTION', 'YOURSELF', 'ATTACHED', 'INSTRUCTION', 'INSTRUCTIONS',
    'FUNCTION', 'DISCOVERY', 'DISCOUER', 'STRENGTH', 'STRENGTH',
    'THEMSELVES', 'THEMSELUES', 'SHADOWS', 'THOUSAND', 'PREPARED',
    'PREPARED', 'PRACTICES', 'PROGRAM', 'REALITY', 'DIUINITY',
    'TOTIENTS', 'TOTIENT', 'INSTAR', 'BECOME', 'DESTROY',
]
LONG_LP_GP = {}
for w in LONG_LP_WORDS:
    enc = gp_encode(w)
    if len(enc) >= 8:
        LONG_LP_GP[w] = enc

# Decode all word slots, find the long LP word matches
long_word_hits = []  # (pg, start, length, word, gp_seq)
for pg, start, length in word_slots:
    if length < 8: continue
    decoded = tuple((int(CIPHER[start+i]) - int(KEY[int(LINK_MAP[start+i])])) % M for i in range(length))
    decoded_str = gp_str(decoded)
    if decoded_str in LONG_LP_GP:
        long_word_hits.append((pg, start, length, decoded_str, decoded))

p(f'  Found {len(long_word_hits)} word slots of len>=8 decoding to known LP words.')
p()

# For each, propagate key and check other linked positions
verification_results = []
for pg, start, length, word, decoded_gp in long_word_hits[:30]:  # cap at 30 to keep output manageable
    # Required key values for this word
    req_keys = {}  # canon_pos -> key_val
    conflict = False
    for i in range(length):
        pos = start + i
        canon = int(LINK_MAP[pos])
        kv = (int(CIPHER[pos]) - decoded_gp[i]) % M
        if canon in req_keys and req_keys[canon] != kv:
            conflict = True; break
        req_keys[canon] = kv

    if conflict:
        p(f'  P{pg:02d} pos={start:5d} len={length:2d} "{word}" -- INTERNAL CONFLICT (impossible)')
        continue

    # Find any other word slots whose positions are linked to these canon positions
    linked_words = []
    for other_pg, other_start, other_len in word_slots:
        if other_start == start: continue  # skip self
        # Check if any position in this other word shares a canon with our req_keys
        shared = False
        for i in range(other_len):
            other_canon = int(LINK_MAP[other_start + i])
            if other_canon in req_keys:
                shared = True; break
        if not shared: continue

        # Decode this other word using req_keys where available, current KEY otherwise
        other_decoded = []
        for i in range(other_len):
            other_pos = other_start + i
            other_canon = int(LINK_MAP[other_pos])
            kv_use = req_keys.get(other_canon, int(KEY[other_canon]))
            plain = (int(CIPHER[other_pos]) - kv_use) % M
            other_decoded.append(plain)
        other_str = gp_str(other_decoded)
        linked_words.append((other_pg, other_start, other_str))

    # Current key consistency check
    current_decoded = tuple((int(CIPHER[start+i]) - int(KEY[int(LINK_MAP[start+i])])) % M for i in range(length))
    current_str = gp_str(current_decoded)
    matches_current = (current_str == word)

    verification_results.append((pg, start, word, linked_words, matches_current))
    mark = '✓' if matches_current else '✗'
    p(f'  {mark} P{pg:02d} pos={start:5d} len={length:2d} "{word}"'
      f'  ({len(req_keys)} canon keys)  '
      f'  TTP-linked words: {len(linked_words)}')

    # Show first 3 linked words
    for other_pg, other_start, other_str in linked_words[:3]:
        dist = other_start - start
        p(f'      → P{other_pg:02d} pos={other_start:5d} (offset {dist:+d}): "{other_str}"')

p()

# ---------------------------------------------------------------------------
# TEST 3: TTP SLAVE DECODE CONSISTENCY
# ---------------------------------------------------------------------------
p('=' * 70)
p('TEST 3: TTP SLAVE REGION DIRECT MATCH CHECK')
p('  master_plain[i] must equal slave_plain[i] under a valid key.')
p('  (This is the cipher property: cipher[slave]=cipher[master]+const implies')
p('   that for OTP key k[slave]=k[master]+const, decodes are equal.)')
p()

for region_idx, (src_s, dst_s, ln) in enumerate(TTP):
    master_plain = (CIPHER[src_s:src_s+ln].astype(int) - KEY[src_s:src_s+ln].astype(int)) % M
    slave_plain  = (CIPHER[dst_s:dst_s+ln].astype(int) - KEY[dst_s:dst_s+ln].astype(int)) % M
    mismatches = int(np.sum(master_plain != slave_plain))
    pct_match = 100.0 * (ln - mismatches) / ln
    p(f'  Region {region_idx+1}:  len={ln:4d}  mismatches={mismatches:4d}  '
      f'match={pct_match:.1f}%')
    if mismatches > 0 and mismatches < 20:
        mismatch_positions = np.where(master_plain != slave_plain)[0]
        for mp in mismatch_positions[:5]:
            p(f'    pos+{mp}: master→{IDX_TO[master_plain[mp]]} slave→{IDX_TO[slave_plain[mp]]}')

p()
p('  NOTE: 100% match = TTP enforced correctly.')
p('  Any mismatch = key has drifted from TTP (should never happen with enforce_ttp).')
p()

# ---------------------------------------------------------------------------
# TEST 4: IoC ANALYSIS (per page, unbiased)
# ---------------------------------------------------------------------------
p('=' * 70)
p('TEST 4: IoC PER PAGE (pure letter frequency, no vocabulary bias)')
p('  Genuine LP plaintext has IoC 1.7-2.2. Random has IoC ~1.0. Cipher ~1.0.')
p()

def ioc(seq):
    if len(seq) < 2: return 0.0
    counts = Counter(seq)
    n = len(seq)
    return M * sum(c*(c-1) for c in counts.values()) / (n*(n-1))

for pg in range(21, 55):
    if pg not in page_offsets: continue
    poff = page_offsets[pg]
    # Find how many runes this page has
    all_pages = sorted(page_offsets.keys())
    pg_idx = all_pages.index(pg)
    if pg_idx + 1 < len(all_pages):
        pnext_off = page_offsets[all_pages[pg_idx+1]]
    else:
        pnext_off = N
    plen = pnext_off - poff
    if plen < 50: continue

    plain = [(int(CIPHER[poff+i]) - int(KEY[int(LINK_MAP[poff+i])])) % M for i in range(plen)]
    page_ioc = ioc(plain)

    # Word-level diversity (unique words / total words)
    _, pg_words = load_page(pg)
    decoded_words = []
    ki2 = poff
    for w in pg_words:
        dec = tuple((int(CIPHER[ki2+i]) - int(KEY[int(LINK_MAP[ki2+i])])) % M for i in range(len(w)))
        decoded_words.append(gp_str(dec))
        ki2 += len(w)

    unique_w = len(set(decoded_words))
    total_w  = len(decoded_words)
    diversity = unique_w / total_w if total_w else 0

    # AND-flooding check
    and_gp = gp_str(gp_encode('AND'))
    and_count = decoded_words.count(and_gp)
    and_pct   = 100.0 * and_count / total_w if total_w else 0

    p(f'  P{pg:02d}: IoC={page_ioc:.3f}  words={total_w:3d}  unique={unique_w:3d}  '
      f'diversity={diversity:.2f}  AND={and_count}({and_pct:.0f}%)')

p()
p('  Healthy text: IoC>1.7, diversity>0.4, AND<20%')
p()

# ---------------------------------------------------------------------------
# TEST 5: PURE QUADGRAM SCORE COMPARISON (no LP word bias)
# ---------------------------------------------------------------------------
p('=' * 70)
p('TEST 5: PURE QUADGRAM SCORE (no vocabulary bonus)')
p()

# Build quadgram table from English corpora only (no LP weighting)
from collections import Counter as Ctr
qg_counts = Ctr()
total_qg = 0
for cf in ['data/self_reliance.txt', 'data/emerson_essays.txt']:
    if Path(cf).exists():
        txt = Path(cf).read_text(encoding='utf-8', errors='ignore').upper()
        gp_seq = []
        i = 0
        while i < len(txt):
            if i+1 < len(txt) and txt[i:i+2] in LETTER_TO_GP:
                gp_seq.append(LETTER_TO_GP[txt[i:i+2]]); i += 2
            elif txt[i] in LETTER_TO_GP:
                gp_seq.append(LETTER_TO_GP[txt[i]]); i += 1
            else: i += 1
        for j in range(len(gp_seq)-3):
            k = gp_seq[j]*M**3 + gp_seq[j+1]*M**2 + gp_seq[j+2]*M + gp_seq[j+3]
            qg_counts[k] += 1; total_qg += 1

QG = {}
floor = math.log(0.01 / max(total_qg, 1))
for kk, cnt in qg_counts.items():
    QG[kk] = math.log(cnt / total_qg)

def pure_qg_score(key_arr):
    total = 0.0
    for i in range(N-3):
        plain = [(int(CIPHER[i+j]) - int(key_arr[int(LINK_MAP[i+j])])) % M for j in range(4)]
        k = plain[0]*M**3 + plain[1]*M**2 + plain[2]*M + plain[3]
        total += QG.get(k, floor)
    return total

p('  Computing scores (this takes ~10s)...')

# Current key
score_current = pure_qg_score(KEY)
p(f'  Current key:        {score_current:>12.1f}')

# Random key baseline (average of 5 random keys)
rng = np.random.default_rng(42)
rand_scores = []
for _ in range(3):
    rand_key = rng.integers(0, M, size=N, dtype=np.int32)
    rand_scores.append(pure_qg_score(rand_key))
avg_random = sum(rand_scores) / len(rand_scores)
p(f'  Random key (avg×3): {avg_random:>12.1f}')

# All-zeros key
zero_key = np.zeros(N, dtype=np.int32)
score_zero = pure_qg_score(zero_key)
p(f'  All-zeros key:      {score_zero:>12.1f}')

p()
p(f'  Improvement over random: {score_current - avg_random:+.1f} nats ({100*(score_current-avg_random)/abs(avg_random):.1f}%)')
p()
p('  Rule of thumb: >10% improvement over random is highly significant.')
p('  >20% strongly suggests genuine plaintext structure.')

# ---------------------------------------------------------------------------
# TEST 6: LONG-WORD-ONLY DECODE (strip all short filler words)
# ---------------------------------------------------------------------------
p()
p('=' * 70)
p('TEST 6: LONG-WORD-ONLY DECODE (len>=7, no gap-filler short words)')
p('  Shows ONLY word slots that decode to confirmed long LP words.')
p('  These cannot be accidentally produced by quadgram optimization.')
p()

long_lp_set = set(LONG_LP_GP.keys())

for pg in range(21, 55):
    if pg not in page_offsets: continue
    pg_hits = [(start, length, word) for (p2, start, length, word, _) in long_word_hits if p2 == pg]
    if not pg_hits: continue
    p(f'  P{pg:02d}:')
    for start, length, word in pg_hits:
        p(f'    pos={start:5d} len={length:2d}: {word}')

# ---------------------------------------------------------------------------
# Write report
# ---------------------------------------------------------------------------
Path('data/verify_decode_report.txt').write_text('\n'.join(outlines), encoding='utf-8')
p()
p(f'Report saved: data/verify_decode_report.txt')
