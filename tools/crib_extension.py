"""
Crib Extension Tool — extend key from confirmed anchor positions
using LP vocabulary beam search.

Strategy:
  1. Start from each confirmed anchor run (62 positions total)
  2. Decode adjacent positions using LP bigram/unigram scores
  3. Use beam search to find most LP-like extension
  4. Show top candidates + update anchors if high-confidence

Usage: python crib_extension.py [--extend N] [--min-score S]
"""

import json, sys, argparse
from pathlib import Path
from collections import Counter
from itertools import product

RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
M = 29

LP_MAP = {
    'F':0,'U':1,'TH':2,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,
    'N':9,'I':10,'J':11,'Y':26,'EO':12,'P':13,'X':14,'Z':14,'S':15,
    'T':16,'B':17,'E':18,'M':19,'L':20,'NG':21,'ING':21,'OE':22,
    'D':23,'A':24,'AE':25,'IO':27,'IA':27,'EA':28,
    'V':1,'Q':5,
}

# ─── LP vocabulary for scoring ──────────────────────────────────────────────
LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS',
    'GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY',
    'DEEP','ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS',
    'OF','IN','NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER',
    'INSIDE','YOURSELF','IMPOSE','NOTHING','OTHERS','CHAPTER','INTUS',
    'PARABLE','INSTAR','BUTTERFLY','SHADOW','FORM','AND','FOR','BUT','BY',
    'AS','AT','THAT','WHICH','CAUSE','BEGINNING','JOURNEY','LIGHT','DARK',
    'WORLD','SOUL','LIKE','THROUGH','ONLY','GOING','SHED','OWN','INNER',
    'OUTER','EMERGE','SHELL','FIND','SEE','HEAR','FEEL','KNOW',
}

# ─── TTP constraints ────────────────────────────────────────────────────────
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]

def build_link_map(n):
    lm = list(range(n))
    for src, dst, ln in TTP_CONSTRAINTS:
        for i in range(ln):
            lm[dst + i] = lm[src + i]
    return lm

# ─── Load cipher ────────────────────────────────────────────────────────────
def load_runes_and_words(pages):
    runes = []; words = []; curr = []; pos = 0; word_start_pos = []
    for pg in pages:
        p = Path(f'pages/page_{pg:02d}/runes.txt')
        if not p.exists(): continue
        for ch in p.read_text(encoding='utf-8'):
            if ch in RUNE_TO_IDX:
                runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
            elif ch in '-. \n\r\t\u2022/' and curr:
                words.append((pos - len(curr), tuple(curr)))
                curr = []
        if curr:
            words.append((pos - len(curr), tuple(curr)))
            curr = []
        pos = len(runes)
    return runes, words

print('Loading cipher...')
CIPHER, CIPHER_WORDS = load_runes_and_words(range(21, 55))
N = len(CIPHER)
LINK_MAP = build_link_map(N)
print(f'  {N} runes, {len(CIPHER_WORDS)} words')

# Build word-boundary map: mark which positions start/end words
WORD_AT = {}   # pos -> word tuple
IS_WORD_START = set()
IS_WORD_END = set()
for wstart, w in CIPHER_WORDS:
    WORD_AT[wstart] = w
    IS_WORD_START.add(wstart)
    IS_WORD_END.add(wstart + len(w) - 1)

# ─── Build LP bigram/unigram table from known text ───────────────────────────
def text_to_gp(txt):
    txt = txt.upper(); result = []; i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in LP_MAP:
            result.append(LP_MAP[txt[i:i+2]]); i += 2
        elif txt[i] in LP_MAP:
            result.append(LP_MAP[txt[i]]); i += 1
        else:
            i += 1
    return result

solved_pages = list(range(0, 21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
known_gp = []
for pg in solved_pages:
    r, _ = load_runes_and_words([pg])
    known_gp.extend(r)

lp_phrases = [
    "SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
    "AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS",
    "CONSUMPTION PRESERVATION ADHERENCE",
    "AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN",
    "QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF",
    "FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
    "WITHIN THE DEEP WEB THERE EXISTS A PAGE",
    "LIKE THE INSTAR TUNNELING TO THE SURFACE",
    "WE MUST SHED OUR OWN CIRCUMFERENCES",
    "FIND THE DIVINITY WITHIN AND EMERGE",
    "JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE",
    "YOU ARE A BEING UNTO YOURSELF",
    "EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY",
]
for phrase in lp_phrases:
    known_gp.extend(text_to_gp(phrase))

import math
unigram = Counter(known_gp)
bigram  = Counter()
trigram = Counter()
for i in range(len(known_gp)-1):
    bigram[(known_gp[i], known_gp[i+1])] += 1
for i in range(len(known_gp)-2):
    trigram[(known_gp[i], known_gp[i+1], known_gp[i+2])] += 1

total_uni = sum(unigram.values()) + M
total_bi  = sum(bigram.values()) + M*M
total_tri = sum(trigram.values()) + M*M*M

log_uni = {v: math.log((unigram.get(v,0)+1)/total_uni) for v in range(M)}
log_bi  = {k: math.log((bigram.get(k,0)+1)/total_bi) for k in [(a,b) for a in range(M) for b in range(M)]}
log_tri = {k: math.log((trigram.get(k,0)+1)/total_tri) for k in [(a,b,c) for a in range(M) for b in range(M) for c in range(M)] if k in trigram}

def lp_log_score(seq):
    """Log probability of a sequence under LP trigram model."""
    if len(seq) == 0: return 0.0
    if len(seq) == 1: return log_uni[seq[0]]
    if len(seq) == 2: return log_uni[seq[0]] + log_bi[(seq[0],seq[1])]
    s = log_uni[seq[0]] + log_bi[(seq[0],seq[1])]
    for i in range(2, len(seq)):
        k = (seq[i-2],seq[i-1],seq[i])
        s += log_tri.get(k, math.log(1/total_tri))
    return s

def lp_word_score(plain_seq, context_words):
    """Score by LP vocabulary + length (per-word bigram scoring)."""
    score = 0
    for wstart, w in context_words:
        # decode this word using plain_seq offset
        wp = [plain_seq.get(wstart + j) for j in range(len(w))]
        if None in wp: continue
        txt = ''.join(IDX_TO[v] for v in wp)
        if txt in LP_VOCAB:
            score += len(txt) * 15 + 30
        elif len(txt) >= 4 and any(lw in txt for lw in LP_VOCAB if len(lw) >= 4):
            score += 10
    return score

# ─── Load checkpoint & anchors ───────────────────────────────────────────────
ckpt = json.loads(Path('data/gpu_hill_checkpoint_gpu1.json').read_text())
KEY  = ckpt['key']   # best-guess key, list of 14529 ints

anchor_data = json.loads(Path('data/key_anchors.json').read_text())
CONFIRMED = {int(k): v for k, v in anchor_data['anchors'].items()}
print(f'Confirmed positions: {len(CONFIRMED)}')

# ─── Decode with confirmed + checkpoint key ───────────────────────────────────
def decode_pos(pos, key_val):
    """plain = (cipher - key) % 29"""
    return (CIPHER[pos] - key_val) % M

def decode_range(start, end, override=None):
    """Decode positions start..end-1. override = {pos: key_val} for forcing."""
    override = override or {}
    plain = {}
    for i in range(start, end):
        if i < 0 or i >= N: continue
        kv = override.get(i, CONFIRMED.get(i, KEY[i]))
        plain[i] = decode_pos(i, kv)
    return plain

def plain_to_str(plain, start, end):
    parts = []
    for i in range(start, end):
        v = plain.get(i)
        parts.append(IDX_TO[v] if v is not None else '?')
    return ''.join(parts)

# ─── Find anchor runs ─────────────────────────────────────────────────────────
items = sorted(CONFIRMED.items())
runs = []
cr = []
for pos, val in items:
    if not cr or pos == cr[-1][0]+1: cr.append((pos,val))
    else:
        runs.append(cr); cr = [(pos,val)]
if cr: runs.append(cr)

print(f'\nFound {len(runs)} anchor runs:\n')

# ─── For each anchor run, show context + try extension ───────────────────────
CONTEXT = 40   # chars before/after anchor to show
EXTEND  = 20   # max positions to extend per direction
BEAM    = 5    # beam width

results = []

for run_idx, run in enumerate(runs):
    run_start = run[0][0]
    run_end   = run[-1][0]
    run_vals  = {pos: val for pos,val in run}
    
    # Show context
    ctx_start = max(0, run_start - CONTEXT)
    ctx_end   = min(N, run_end + CONTEXT + 1)
    plain_ctx = decode_range(ctx_start, ctx_end, run_vals)
    decoded   = plain_to_str(plain_ctx, ctx_start, ctx_end)
    
    # word score for confirmed section
    ctx_words = [(ws, w) for ws, w in CIPHER_WORDS if ctx_start <= ws < ctx_end]
    ws = lp_word_score(plain_ctx, ctx_words)
    
    anchor_text = plain_to_str({p: v for p,v in plain_ctx.items() if run_start <= p <= run_end}, run_start, run_end+1)
    
    print(f'=== Run {run_idx+1}: positions [{run_start}-{run_end}] len={len(run)} ===')
    print(f'  Anchor text: "{anchor_text}"')
    print(f'  Context: "...{decoded}..."')
    print(f'  Context WordScore: {ws}')
    
    # ─── Beam search: extend FORWARD from run_end ────────────────────────────
    # Beam state: (score, extension_dict, plain_seq_so_far)
    # Initialize beam with just the confirmed run
    base_plain = {p: decode_pos(p, v) for p, v in run_vals.items()}
    
    # Forward extension
    fwd_beam = [(0.0, {}, list(base_plain[p] for p in sorted(base_plain.keys())))]
    fwd_extended = {}
    
    for step in range(EXTEND):
        pos = run_end + step + 1
        if pos >= N: break
        new_beam = []
        for score, ext, history in fwd_beam:
            for kv in range(M):
                p = decode_pos(pos, kv)
                new_hist = history + [p]
                # Score: trigram log-prob of last 3 chars
                if len(new_hist) >= 3:
                    tri_score = log_tri.get(tuple(new_hist[-3:]), math.log(1/total_tri))
                elif len(new_hist) == 2:
                    tri_score = log_bi.get((new_hist[-2], new_hist[-1]), math.log(1/total_bi))
                else:
                    tri_score = log_uni[p]
                new_ext = dict(ext); new_ext[pos] = kv
                new_beam.append((score + tri_score, new_ext, new_hist))
        # Keep top BEAM
        new_beam.sort(key=lambda x: -x[0])
        fwd_beam = new_beam[:BEAM]
    
    if fwd_beam:
        best_fwd_score, best_fwd_ext, best_fwd_hist = fwd_beam[0]
        fwd_plain = ''.join(IDX_TO[v] for v in best_fwd_hist[len(run):])
        print(f'  Fwd extension ({EXTEND} steps, top beam): "{fwd_plain}" (score delta={best_fwd_score:.2f})')
        
        # Check for LP vocab matches
        all_override = dict(run_vals); all_override.update(best_fwd_ext)
        all_plain = decode_range(run_start, run_end + EXTEND + 1, all_override)
        fwd_words = [(ws, w) for ws, w in CIPHER_WORDS if run_start <= ws < run_end + EXTEND + 1]
        fwd_ws = lp_word_score(all_plain, fwd_words)
        print(f'  Fwd extension WordScore: {fwd_ws} (vs context base {ws})')
    
    # Backward extension
    bwd_beam = [(0.0, {}, list(reversed([base_plain[p] for p in sorted(base_plain.keys())])) )]
    
    for step in range(EXTEND):
        pos = run_start - step - 1
        if pos < 0: break
        new_beam = []
        for score, ext, history in bwd_beam:
            for kv in range(M):
                p = decode_pos(pos, kv)
                new_hist = [p] + history  # prepend
                if len(new_hist) >= 3:
                    tri_score = log_tri.get(tuple(new_hist[:3]), math.log(1/total_tri))
                elif len(new_hist) == 2:
                    tri_score = log_bi.get((new_hist[0], new_hist[1]), math.log(1/total_bi))
                else:
                    tri_score = log_uni[p]
                new_ext = dict(ext); new_ext[pos] = kv
                new_beam.append((score + tri_score, new_ext, new_hist))
        new_beam.sort(key=lambda x: -x[0])
        bwd_beam = new_beam[:BEAM]
    
    if bwd_beam:
        best_bwd_score, best_bwd_ext, best_bwd_hist = bwd_beam[0]
        bwd_plain = ''.join(IDX_TO[v] for v in best_bwd_hist[:EXTEND])
        print(f'  Bwd extension ({EXTEND} steps, top beam): "{bwd_plain}" (score delta={best_bwd_score:.2f})')
    
    # ─── Also show what the checkpoint key produces (for comparison) ─────────
    ckpt_plain = decode_range(run_start - 20, run_end + 21)
    ckpt_text  = plain_to_str(ckpt_plain, run_start - 20, run_end + 21)
    print(f'  Checkpoint context: "...{ckpt_text}..."')
    
    print()
    results.append({
        'run': run_idx+1,
        'start': run_start,
        'end': run_end,
        'anchor_text': anchor_text,
        'context': decoded,
        'word_score': ws,
    })

# ─── Summary ────────────────────────────────────────────────────────────────
print('\n=== Summary ===')
print(f'Total confirmed key positions: {len(CONFIRMED)}')
print(f'Anchor runs: {len(runs)}')
print()
print('Next steps:')
print(' 1. High-confidence forward extensions can be promoted to anchors')
print(' 2. Run GPU hillclimber with these additional anchor constraints')
print(' 3. After each GPU improvement, re-run this tool to find more extensions')
