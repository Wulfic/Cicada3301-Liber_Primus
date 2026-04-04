"""
TTP Crib Driver — exploit two-time-pad constraints to confirm crib positions.

For each candidate LP phrase:
- Slide it over all valid positions in Region A (TTP source region)
- Compute key[i] = (cipher_A[i] - phrase[i]) % 29
- Apply that key to Region B cipher (TTP mirror): plaintext_B = (cipher_B - key) % 29
- Score plaintext_B for LP vocabulary / readability
- Also check singleton constraints

If a crib placement in Region A automatically produces LP text in Region B (with
ZERO free parameters), it is a confirmed crib.

TTP regions (from hillclimber):
  TTP-1: A=[3001,4312], B=[9727,11038], len=1312
  TTP-2: A=[6298,7765], B=[12311,13778], len=1468
  TTP-3: A=[0,403],     B=[5803,6206],   len=404
  TTP-4: A=[2736,3000], B=[8643,8907],   len=265
  TTP-5: A=[737,908],   B=[8100,8271],   len=172
  TTP-6: A=[910,1006],  B=[8273,8369],   len=97
"""

import json, math
from pathlib import Path
from collections import Counter

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
    'D':23,'A':24,'AE':25,'IO':27,'IA':27,'EA':28,'V':1,'Q':5,
}

def encode(word):
    runes = []; i = 0; w = word.upper()
    while i < len(w):
        if w[i]==' ': i+=1; continue
        if i+2<len(w) and w[i:i+3] in LP_MAP: runes.append(LP_MAP[w[i:i+3]]); i+=3
        elif i+1<len(w) and w[i:i+2] in LP_MAP: runes.append(LP_MAP[w[i:i+2]]); i+=2
        elif w[i] in LP_MAP: runes.append(LP_MAP[w[i]]); i+=1
        else: i+=1
    return runes

TTP_CONSTRAINTS = [
    (3001,  9727, 1312),  # TTP-1
    (6298, 12311, 1468),  # TTP-2
    (   0,  5803,  404),  # TTP-3
    (2736,  8643,  265),  # TTP-4
    ( 737,  8100,  172),  # TTP-5
    ( 910,  8273,   97),  # TTP-6
]

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
    'INSIDE','YOURSELF','IMPOSE','NOTHING','OTHERS','AND','FOR','BUT',
    'CAUSE','THAT','WHICH','THREE','BEHAVIORS','PRACTICES','CIRCUMFERENCE',
    'LOSS','ABOVE','FORM','SHADOW','JOURNEYS','JOURNEY','LIGHT','DARK',
    'WORLD','SOUL','SHELL','SHED','LIKE','THROUGH','ONLY','GOING',
    'INNER','OUTER','FIND','ENOUGH','THOSE','STRONG','PRIME',
}

# ─── Load cipher ─────────────────────────────────────────────────────────────
def load_page_runes(pg):
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if not p.exists(): return []
    return [RUNE_TO_IDX[ch] for ch in p.read_text(encoding='utf-8') if ch in RUNE_TO_IDX]

def load_page_words(pg):
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if not p.exists(): return []
    words = []; curr = []
    for ch in p.read_text(encoding='utf-8'):
        if ch in RUNE_TO_IDX: curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr: words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return words

cipher_list = []
words_all = []
page_offsets = {}
cum = 0
for pg in range(21, 55):
    runes = load_page_runes(pg)
    page_offsets[pg] = cum
    cum += len(runes)
    cipher_list.extend(runes)
    words_all.extend([(cum - len(runes) + i, w) for i, w in
                       enumerate([(ws, ww) for ws, ww in
                                  [(sum(len(x) for x in [load_page_words(pg)[:j]]) if False else 0, x)
                                   for j, x in enumerate(load_page_words(pg))]])])

# Reload properly
cipher_list = []; words_all_proper = []; page_offsets = {}; cum = 0
for pg in range(21, 55):
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if not p.exists(): continue
    page_offsets[pg] = cum
    text = p.read_text(encoding='utf-8')
    curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            cipher_list.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words_all_proper.append((cum - len(curr), tuple(curr))); curr = []
    if curr:
        words_all_proper.append((cum - len(curr), tuple(curr)))
    cum += sum(1 for ch in text if ch in RUNE_TO_IDX)

CIPHER = cipher_list
N = len(CIPHER)

# Singleton positions (single-rune words must be I=10 or A=24)
SINGLETONS = {wstart: cipher_list[wstart] for wstart, w in words_all_proper if len(w) == 1}
print(f'Cipher: {N} runes, {len(words_all_proper)} words, {len(SINGLETONS)} singletons')

# ─── Build LP bigram scoring ──────────────────────────────────────────────────
def text_to_gp(txt):
    txt=txt.upper(); r=[]; i=0
    while i<len(txt):
        if i+1<len(txt) and txt[i:i+2] in LP_MAP: r.append(LP_MAP[txt[i:i+2]]); i+=2
        elif txt[i] in LP_MAP: r.append(LP_MAP[txt[i]]); i+=1
        else: i+=1
    return r

known_gp = []
for pg in list(range(0,21))+[55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]:
    known_gp.extend(load_page_runes(pg))
for phrase in [
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY",
    "CONSUMPTION PRESERVATION ADHERENCE",
    "AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN",
    "AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    "SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
    "QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
    "YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY",
    "LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
    "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE",
    "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE",
]:
    known_gp.extend(text_to_gp(phrase))

bigram = Counter()
for i in range(len(known_gp)-1):
    bigram[(known_gp[i], known_gp[i+1])] += 1
total_bi = sum(bigram.values()) + M*M
LOG_BI = {k: math.log((bigram.get(k,0)+1)/total_bi)
          for a in range(M) for b in range(M)
          for k in [(a,b)]}
LOG_UNI = {v: math.log((sum(1 for x in known_gp if x==v)+1)/(len(known_gp)+M)) for v in range(M)}

def bi_score(seq):
    if len(seq) < 2: return 0.0
    return sum(LOG_BI.get((seq[i],seq[i+1]), math.log(1/total_bi)) for i in range(len(seq)-1))

def word_score(plain_dict, words_in_window):
    score = 0
    for wstart, w in words_in_window:
        wp = [plain_dict.get(wstart+j) for j in range(len(w))]
        if None in wp: continue
        txt = ''.join(IDX_TO[v] for v in wp)
        if txt in LP_VOCAB: score += len(txt)*10+30
    return score

# ─── Check singleton consistency ─────────────────────────────────────────────
def singleton_ok(key_dict):
    for pos, c in SINGLETONS.items():
        kv = key_dict.get(pos)
        if kv is None: continue
        dec = (c - kv) % M
        if dec != 10 and dec != 24:
            return False
    return True

# ─── Test a crib in a TTP region ─────────────────────────────────────────────
def test_crib_in_ttp(crib_enc, src_start, dst_start, ttp_len, min_pos, max_pos, top_n=5):
    """
    Slide crib over positions [min_pos, max_pos] in TTP source region.
    For each placement:
    - Derive key at crib positions
    - Apply SAME key to TTP destination region
    - Score destination plaintext for LP vocabulary
    Returns sorted list of (score, pos, src_plain, dst_plain) tuples.
    """
    clen = len(crib_enc)
    results = []
    
    # Build destination cipher window (same offsets relative to dst_start)
    for pos in range(min_pos, max_pos - clen + 1):
        # pos = start of crib in source region (global cipher pos)
        # Offset from src_start
        offset = pos - src_start
        if offset < 0 or offset + clen > ttp_len:
            continue
        
        # Derived key for this placement
        derived_key = {pos + j: (CIPHER[pos + j] - crib_enc[j]) % M for j in range(clen)}
        
        # Check singleton consistency
        if not singleton_ok(derived_key):
            continue
        
        # Apply same key to destination region
        dst_plain = {}
        for j in range(clen):
            dst_pos = dst_start + offset + j
            if dst_pos < N:
                dst_plain[dst_pos] = (CIPHER[dst_pos] - derived_key[pos + j]) % M
        
        # Score destination plain
        dst_seq = [dst_plain[dst_start + offset + j] for j in range(clen) if dst_start+offset+j in dst_plain]
        dst_bi  = bi_score(dst_seq)
        
        # Word score at destination
        dst_words = [(ws, w) for ws, w in words_all_proper
                     if dst_start + offset <= ws < dst_start + offset + clen]
        dst_ws = word_score(dst_plain, dst_words)
        
        # Also score source context (bigram)
        src_plain_seq = [crib_enc[j] for j in range(clen)]
        src_bi = bi_score(src_plain_seq)  # This is exactly the crib's own bigram score
        
        total_score = dst_bi + dst_ws * 0.5
        dst_text = ''.join(IDX_TO[v] for v in dst_seq)
        results.append((total_score, pos, dst_bi, dst_ws, dst_text))
    
    results.sort(key=lambda x: -x[0])
    return results[:top_n]

# ─── LP cribs to test ─────────────────────────────────────────────────────────
# Each is a multi-word LP phrase likely to appear in LP2
CRIBS_TO_TEST = [
    ("THE LOSS OF DIVINITY",                     encode("THE LOSS OF DIVINITY")),
    ("CONSUMPTION PRESERVATION ADHERENCE",        encode("CONSUMPTION PRESERVATION ADHERENCE")),
    ("PRACTICES THREE BEHAVIORS",                 encode("PRACTICES THREE BEHAVIORS")),
    ("BEHAVIORS WHICH CAUSE",                     encode("BEHAVIORS WHICH CAUSE")),
    ("WHICH CAUSE THE LOSS",                      encode("WHICH CAUSE THE LOSS")),
    ("AMASS GREAT WEALTH",                        encode("AMASS GREAT WEALTH")),
    ("NEVER BECOME ATTACHED",                     encode("NEVER BECOME ATTACHED")),
    ("PREPARED TO DESTROY",                       encode("PREPARED TO DESTROY")),
    ("PROGRAM YOUR MIND",                         encode("PROGRAM YOUR MIND")),
    ("PROGRAM REALITY",                           encode("PROGRAM REALITY")),
    ("KNOW THIS THE PRIMES",                      encode("KNOW THIS THE PRIMES")),
    ("THE PRIMES ARE SACRED",                     encode("THE PRIMES ARE SACRED")),
    ("ALL THINGS SHOULD BE ENCRYPTED",            encode("ALL THINGS SHOULD BE ENCRYPTED")),
    ("QUESTION ALL THINGS",                       encode("QUESTION ALL THINGS")),
    ("DISCOVER TRUTH INSIDE YOURSELF",            encode("DISCOVER TRUTH INSIDE YOURSELF")),
    ("FOLLOW YOUR TRUTH IMPOSE NOTHING",          encode("FOLLOW YOUR TRUTH IMPOSE NOTHING")),
    ("IMPOSE NOTHING ON OTHERS",                  encode("IMPOSE NOTHING ON OTHERS")),
    ("YOU ARE A BEING UNTO YOURSELF",             encode("YOU ARE A BEING UNTO YOURSELF")),
    ("EACH INTELLIGENCE IS HOLY",                 encode("EACH INTELLIGENCE IS HOLY")),
    ("FOR ALL THAT LIVES IS HOLY",                encode("FOR ALL THAT LIVES IS HOLY")),
    ("AN INSTRUCTION PROGRAM",                    encode("AN INSTRUCTION PROGRAM")),
    ("THE CIRCUMFERENCE PRACTICES",               encode("THE CIRCUMFERENCE PRACTICES")),
    ("WITHIN THE DEEP WEB",                       encode("WITHIN THE DEEP WEB")),
    ("AN END WITHIN THE DEEP WEB",                encode("AN END WITHIN THE DEEP WEB")),
    ("LIKE THE INSTAR",                           encode("LIKE THE INSTAR")),
    ("WE MUST SHED OUR OWN CIRCUMFERENCES",       encode("WE MUST SHED OUR OWN CIRCUMFERENCES")),
    ("FIND THE DIVINITY WITHIN AND EMERGE",       encode("FIND THE DIVINITY WITHIN AND EMERGE")),
    ("JOURNEY DEEP WITHIN",                       encode("JOURNEY DEEP WITHIN")),
    ("A WARNING BELIEVE NOTHING FROM THIS BOOK",  encode("A WARNING BELIEVE NOTHING FROM THIS BOOK")),
    ("IT IS A NECESSARY ONE",                     encode("IT IS A NECESSARY ONE")),
    ("WELCOME PILGRIM",                           encode("WELCOME PILGRIM")),
    ("SEEK TRUTH WITHIN",                         encode("SEEK TRUTH WITHIN")),
    ("COMMAND YOUR OWN SELF",                     encode("COMMAND YOUR OWN SELF")),
]

print(f'\nTesting {len(CRIBS_TO_TEST)} cribs against {len(TTP_CONSTRAINTS)} TTP regions...\n')

ALL_RESULTS = []

for crib_name, crib_enc in CRIBS_TO_TEST:
    clen = len(crib_enc)
    crib_results = []
    
    for src_start, dst_start, ttp_len in TTP_CONSTRAINTS:
        src_end = src_start + ttp_len
        hits = test_crib_in_ttp(crib_enc, src_start, dst_start, ttp_len,
                                 src_start, src_end, top_n=3)
        for score, pos, dst_bi, dst_ws, dst_text in hits:
            crib_results.append((score, pos, src_start, dst_start, ttp_len, dst_bi, dst_ws, dst_text))
    
    crib_results.sort(key=lambda x: -x[0])
    
    if crib_results:
        best = crib_results[0]
        score, pos, ss, ds, tl, dst_bi, dst_ws, dst_text = best
        print(f'  {crib_name:<45s} | len={clen:2d} | pos={pos:5d} | score={score:8.2f} | dst_WS={dst_ws:4d} | dst="{dst_text[:30]}"')
        ALL_RESULTS.append((score, crib_name, pos, ss, ds, dst_ws, dst_text))

# ─── Top results sorted by destination word score ────────────────────────────
print('\n=== TOP HITS BY DST WORD SCORE ===')
ALL_RESULTS.sort(key=lambda x: (-x[5], -x[0]))
for score, name, pos, ss, ds, dst_ws, dst_text in ALL_RESULTS[:15]:
    print(f'  WS={dst_ws:4d} | {name:<45s} | pos={pos:5d} (TTP src={ss:5d}->dst={ds:5d}) | dst="{dst_text[:40]}"')

print('\n=== TOP HITS BY COMBINED SCORE ===')
ALL_RESULTS.sort(key=lambda x: -x[0])
for score, name, pos, ss, ds, dst_ws, dst_text in ALL_RESULTS[:15]:
    print(f'  score={score:8.2f} | {name:<45s} | pos={pos:5d} | dst_WS={dst_ws:4d} | dst="{dst_text[:40]}"')
