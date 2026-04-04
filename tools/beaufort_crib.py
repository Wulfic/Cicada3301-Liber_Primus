"""
Beaufort Crib Dragger - Targeted LP Phrase Search
==================================================
NOW CONFIRMED: Beaufort is the cipher mode (GPU1 producing LP-like text
with 217/217 singletons at all times in beaufort mode).

Beaufort: plain = (key - cipher) % 29
         => key  = (plain + cipher) % 29

Strategy:
  For every known LP phrase, at every cipher position:
    1. Derive what key[pos:pos+n] would need to be
    2. Score ALL possible key continuations via quadgram IoC
    3. Compute a "consistency score" across the extended region
  
  Additionally, uses the P27-P31 = P44[0:1312] two-time-pad to cross-check:
  If the same key segment applies to BOTH P27-P31 AND P44[0:1312], then
  a crib match at one location proves what the key is at BOTH locations.

Usage:
  python beaufort_crib.py

Output: data/beaufort_crib_results.txt
"""

import sys, math
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

M = 29
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

LETTER_MAP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14
}
DIGRAPH_MAP = {'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28}

def text_to_gp(txt):
    txt = txt.upper(); res = []; i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in DIGRAPH_MAP:
            res.append(DIGRAPH_MAP[txt[i:i+2]]); i += 2
        elif txt[i] in LETTER_MAP:
            res.append(LETTER_MAP[txt[i]]); i += 1
        else:
            i += 1
    return res

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

# ─── Load cipher ────────────────────────────────────────────────────────────
print('Loading cipher stream...')
cipher_runes = []
all_words = []
page_starts = {}
for pg in range(21, 55):
    runes, words = load_page(pg)
    page_starts[pg] = len(cipher_runes)
    cipher_runes.extend(runes)
    all_words.extend(words)

CIPHER = cipher_runes
N = len(CIPHER)
print(f'  Cipher: {N} runes')

# Singleton positions
sing_pos = []; sing_cip = []
pos = 0
for w in all_words:
    if len(w) == 1: sing_pos.append(pos); sing_cip.append(w[0])
    pos += len(w)
N_SING = len(sing_pos)
SING_SET = set(zip(sing_pos, sing_cip))
print(f'  Singletons: {N_SING}')

# ─── Page info and word boundaries ──────────────────────────────────────────
rune_to_page = {}
for pg in range(21, 55):
    end = page_starts.get(pg+1, N) if pg < 54 else N
    for r in range(page_starts[pg], end):
        rune_to_page[r] = pg

# ─── Build bigram / unigram freq table from LP known text ──────────────────
print('Building GP frequency tables...')
known_runes = []
for pg in list(range(0, 21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]:
    r, _ = load_page(pg)
    known_runes.extend(r)

unigram = Counter(known_runes)
bigram  = Counter(zip(known_runes[:-1], known_runes[1:]))
total_u = sum(unigram.values()) + M
total_b = sum(bigram.values()) + M*M

def bigram_score(seq):
    """Log-prob of sequence under LP bigram model."""
    s = 0.0
    for i in range(len(seq)-1):
        s += math.log((bigram.get((seq[i],seq[i+1]), 0) + 1) / total_b)
    return s

def ioc(seq):
    if len(seq) < 2: return 0.0
    c = Counter(seq)
    n = len(seq)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

# ─── All known LP phrases for crib dragging ─────────────────────────────────
# Each phrase → raw GP sequence
RAW_PHRASES = [
    "AN INSTRUCTION",
    "PROGRAM YOUR MIND",
    "PROGRAM REALITY",
    "SOME WISDOM",
    "THE PRIMES ARE SACRED",
    "ALL THINGS SHOULD BE ENCRYPTED",
    "KNOW THIS",
    "THE LOSS OF DIVINITY",
    "THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS",
    "CAUSE THE LOSS OF DIVINITY",
    "CONSUMPTION",
    "PRESERVATION",
    "ADHERENCE",
    "AMASS GREAT WEALTH",
    "NEVER BECOME ATTACHED TO WHAT YOU OWN",
    "BE PREPARED TO DESTROY ALL THAT YOU OWN",
    "QUESTION ALL THINGS",
    "DISCOVER TRUTH INSIDE YOURSELF",
    "FOLLOW YOUR TRUTH",
    "IMPOSE NOTHING ON OTHERS",
    "WELCOME PILGRIM",
    "ARE SACRED",
    "THINGS SHOULD BE ENCRYPTED",
    "SEEK TRUTH WITHIN",
    "DIVINITY",
    "WISDOM",
    "PROGRAM",
    "CIRCUMFERENCE",
    "REALITY",
    "TRUTH",
    "SELF",
    "PRIMES",
    "SACRED",
    "CONSUMPTION PRESERVATION ADHERENCE",
    "THE LOSS",
    "AN END",
    "ALL THINGS",
    "SHOULD BE ENCRYPTED",
]

LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS',
    'GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','SELF','PATH','QUESTION','DISCOVER','INSIDE','YOURSELF',
    'IMPOSE','NOTHING','OTHERS','AND','FOR','BUT','A','I','IS','OF','IN',
    'NOT','WITH','NO','WE','DO','SO','ALSO','FOLLOW','END'
}

def word_score_seq(gp_seq):
    """Score a GP sequence by how many contiguous words match LP vocab."""
    # Greedy match longest LP words
    score = 0; sep = ' '
    text = ' '.join(IDX_TO[v] for v in gp_seq)
    for word in text.split():
        if word in LP_VOCAB:
            score += len(word) * 20 + 30
    return score

# ─── Core crib drag function ─────────────────────────────────────────────────
WINDOW = 80  # context window for IoC check

def crib_drag(phrase_gp, phrase_str):
    """
    For beaufort mode:  key[pos] = (plain[pos] + cipher[pos]) % 29
    
    For each offset pos, compute the derived key segment for the crib,
    then use that to decode cipher[pos-WINDOW:pos+len+WINDOW] and score it.
    Returns list of (score, pos, decoded_context).
    """
    n = len(phrase_gp)
    results = []
    
    for pos in range(0, N - n + 1):
        # Derived key segment from crib: k[i] = (plain[i] + cipher[pos+i]) % 29
        crib_key = [(phrase_gp[i] + CIPHER[pos+i]) % M for i in range(n)]
        
        # Check singleton compatibility within crib window
        sing_ok = True
        for sp, sc in zip(sing_pos, sing_cip):
            if pos <= sp < pos + n:
                local = sp - pos
                derived_plain = (crib_key[local] - CIPHER[sp]) % M
                if derived_plain not in (10, 24):
                    sing_ok = False; break
        
        # Decode extended context with crib key (repeating crib key outside window)
        start = max(0, pos - WINDOW)
        end   = min(N, pos + n + WINDOW)
        context = []
        for r in range(start, end):
            if r < pos or r >= pos+n:
                # Outside crib: use FIRST crib_key value (periodic) for context
                k = crib_key[(r - pos) % n]
            else:
                k = crib_key[r - pos]
            context.append((CIPHER[r] + k) % M)  # wait: beaufort plain = (k - c) % 29. Let me recalculate.
            # Actually: beaufort: plain = (key - cipher) % 29
            #           With crib_key[i] = (crib[i] + cipher[pos+i]) % 29:
            #           plain[pos+i] = (crib_key[i] - cipher[pos+i]) % 29 = crib[i] ✓
        # Redo properly:
        context = []
        for r in range(start, end):
            if r < pos or r >= pos+n:
                k = crib_key[(r - pos) % n]
            else:
                k = crib_key[r - pos]
            p = (k - CIPHER[r]) % M  # beaufort decrypt
            context.append(p)

        s_ioc = ioc(context)
        s_bg  = bigram_score(context)
        s_ws  = word_score_seq(context)
        sing_bonus = 200 if sing_ok else 0
        
        # Combined score
        combo = s_bg + s_ioc * 500 + s_ws * 0.5 + sing_bonus
        
        page = rune_to_page.get(pos, '?')
        results.append((combo, s_ioc, s_bg, s_ws, pos, page, context, crib_key, sing_ok))
    
    return results

# ─── Run all cribs ────────────────────────────────────────────────────────────
print(f'\nRunning crib drag for {len(RAW_PHRASES)} phrases against {N} rune cipher...')
print(f'Mode: BEAUFORT')
print()

all_hits = []
for phrase_str in RAW_PHRASES:
    phrase_gp = text_to_gp(phrase_str)
    if not phrase_gp: continue
    n = len(phrase_gp)
    
    results = crib_drag(phrase_gp, phrase_str)
    results.sort(reverse=True)
    
    best = results[:5]  # top 5 offsets
    
    # Report if best is noteworthy
    top = best[0]
    combo, s_ioc, s_bg, s_ws, pos, page, context, crib_key, sing_ok = top
    
    context_str = ' '.join(IDX_TO[v] for v in context[:60])
    flag = ''
    if s_ioc >= 0.05:   flag += ' <<HIGH IOC>>'
    if s_ws >= 200:     flag += ' <<LP VOCAB>>'
    if sing_ok:         flag += ' <<SING OK>>'
    
    line = (f'{phrase_str!r:50s} n={n:3d} | best: pos={pos:5d}(P{page}) '
            f'IoC={s_ioc:.4f} BGscore={s_bg:.1f} WS={s_ws:4d}{flag}')
    print(line)
    all_hits.append((top, phrase_str, phrase_gp))

# Report top 20 overall hits
print(f'\n{"="*80}')
print('TOP 20 POSITIONS OVERALL (any phrase, ranked by score)')
print(f'{"="*80}')

flat = [(h[0][0], h[0][1], h[0][4], h[0][5], h[0][8], h[1], h[0][6]) 
        for h in all_hits]
flat.sort(reverse=True)
for combo, sioc, pos, page, sing_ok, phrase, context in flat[:20]:
    context_str = ' '.join(IDX_TO[v] for v in context[:40])
    print(f'  score={combo:.1f} IoC={sioc:.4f} pos={pos:5d}(P{page}) sing={sing_ok} | {phrase!r}')
    print(f'    context: {context_str}')

# ─── Extended: two-time-pad cross check ─────────────────────────────────────
# P27-P31 (global 3001-4312) == P44[0:1312] (global 9727-11038)
# In beaufort: key[3001+i] = key[9727+i] for i in 0..1311
# So ANY crib hit in P27-P31 range also constrains P44 range
print(f'\n{"="*80}')
print('TWO-TIME-PAD: checking if any top cribs fall in P27-P31 (3001-4312)')
print(f'{"="*80}')
for top, phrase_str, phrase_gp in all_hits:
    combo, s_ioc, s_bg, s_ws, pos, page, context, crib_key, sing_ok = top
    n = len(phrase_gp)
    # Check if this overlap with P27-P31 region
    if 2800 <= pos <= 4400 or 9500 <= pos <= 11200:
        print(f'  HIT in match region: {phrase_str!r} at pos={pos} (P{page})')
        # P44 counterpart
        if 2800 <= pos <= 4400:
            mirror = pos - 3001 + 9727
        else:
            mirror = pos - 9727 + 3001
        mirror_cip = [CIPHER[mirror + i] for i in range(n) if mirror+i < N]
        # Decode P44 counterpart using same key
        mirror_plain = [(crib_key[i] - mirror_cip[i]) % M for i in range(len(mirror_cip))]
        mirror_text = ' '.join(IDX_TO[v] for v in mirror_plain)
        print(f'    Mirror at pos={mirror}: {mirror_text}')

# ─── Save results ────────────────────────────────────────────────────────────
outfile = 'data/beaufort_crib_results.txt'
with open(outfile, 'w', encoding='utf-8') as f:
    f.write('BEAUFORT CRIB DRAG RESULTS\n')
    f.write(f'Cipher: {N} runes, Mode: beaufort\n')
    f.write('='*80 + '\n\n')
    
    flat2 = [(top, phrase_str) for top, phrase_str, _ in all_hits]
    flat2.sort(key=lambda x: -x[0][0])
    
    for top, phrase_str in flat2[:50]:
        combo, s_ioc, s_bg, s_ws, pos, page, context, crib_key, sing_ok = top
        n = len(text_to_gp(phrase_str))
        context_str = ' '.join(IDX_TO[v] for v in context)
        f.write(f'PHRASE: {phrase_str}\n')
        f.write(f'  Best pos={pos} (P{page}), IoC={s_ioc:.4f}, BGscore={s_bg:.1f}, WS={s_ws}, sing_ok={sing_ok}\n')
        f.write(f'  Key at crib: {crib_key[:min(n,20)]}\n')
        f.write(f'  Context (key repeated outside crib): {context_str[:300]}\n\n')

print(f'\nResults saved to {outfile}')

# ─── Also try: FULL LP opening text as running crib ─────────────────────────
# "AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY"
# "SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS"
# These are ALL known LP encrypted-section openers
# Try them in sequence at pos=0, 1, 2... (actual LP structured content)
print(f'\n{"="*80}')
print('STRUCTURED CRIB: Testing LP intro sequence at various alignments')
print(f'{"="*80}')

lp_intro_seqs = [
    "AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    "SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
    "WELCOME PILGRIM TO THE SACRED TEXT OF THE LIBER PRIMUS",
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION PRESERVATION ADHERENCE",
    "AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN",
    "QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
]

for seq_str in lp_intro_seqs:
    gp = text_to_gp(seq_str)
    n = len(gp)
    best_score = float('-inf')
    best_pos = 0
    
    for pos in range(0, min(N - n + 1, 3000)):  # First 3000 positions
        # Beaufort key that would make this the plaintext
        crib_key = [(gp[i] + CIPHER[pos+i]) % M for i in range(n)]
        # Decode next WINDOW runes with repeated key
        extended_plain = []
        for r in range(pos, min(pos + n + 50, N)):
            k = crib_key[(r - pos) % n]
            extended_plain.append((k - CIPHER[r]) % M)
        sc = bigram_score(extended_plain) + word_score_seq(extended_plain) * 0.3
        if sc > best_score:
            best_score = sc; best_pos = pos
    
    gp_best_key = [(gp[i] + CIPHER[best_pos+i]) % M for i in range(n)]
    decoded_context = [(gp_best_key[(r-best_pos) % n] - CIPHER[r]) % M for r in range(best_pos, min(best_pos+n+50, N))]
    dc_str = ' '.join(IDX_TO[v] for v in decoded_context)
    pg_est = rune_to_page.get(best_pos, '?')
    print(f'\nCrib: {seq_str[:60]}...')
    print(f'  Best pos={best_pos} (P{pg_est}), score={best_score:.1f}')
    print(f'  Decoded: {dc_str[:200]}')

print('\nDone.')
