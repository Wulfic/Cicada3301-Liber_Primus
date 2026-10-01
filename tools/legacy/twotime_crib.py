"""
Two-Time-Pad Crib Dragging Attack on Liber Primus P21-P54
==========================================================
Key Discovery: P27-P31 ciphertexts are IDENTICAL to P44[0:1312].
This means:
  - key[3001..4312] == key[9727..11038]  (same key segment used twice)
  - plain[3001..4312] == plain[9727..11038]  (same LP content appears twice)

Attack:
  For all positions 0..6725 where period-1 and period-2 differ:
    diff[i] = (cipher[i] - cipher[i+6726]) mod 29 = (plain1[i] - plain2[i]) mod 29
  
  Crib drag: guess plain1[i..i+n] = crib => compute plain2[i..i+n] and score both.
"""

import sys; sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter

# ── Gematria Primus ──────────────────────────────────────────────────────────
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
          'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
GP_VALS = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
M = 29

# English letter freq for scoring
ENG_FREQ = {
    'E':12.7,'T':9.1,'A':8.2,'O':7.5,'I':7.0,'N':6.7,'S':6.3,'H':6.1,
    'R':6.0,'D':4.3,'L':4.0,'C':2.8,'U':2.8,'M':2.4,'W':2.4,'F':2.2,
    'G':2.0,'Y':2.0,'P':1.9,'B':1.5,'V':0.98,'K':0.77,'J':0.15,'X':0.15,
    'Q':0.10,'Z':0.07
}

# GP phoneme → rough English letters for scoring
GP_TO_LETTERS = {
    0:'F', 1:'U', 2:'TH', 3:'O', 4:'R', 5:'C', 6:'G', 7:'W', 8:'H', 9:'N',
    10:'I', 11:'J', 12:'EO', 13:'P', 14:'X', 15:'S', 16:'T', 17:'B', 18:'E',
    19:'M', 20:'L', 21:'NG', 22:'OE', 23:'D', 24:'A', 25:'AE', 26:'Y',
    27:'IO', 28:'EA'
}

LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE','BEHAVIORS',
    'WHICH','CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS','GREAT',
    'WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN','PREPARED',
    'DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH','WITHIN',
    'HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY','DEEP',
    'ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS','OF','IN',
    'NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER','INSIDE','YOURSELF',
    'IMPOSE','NOTHING','OTHERS','CHAPTER','INTUS','PARABLE','INSTAR','BUTTERFLY',
    'SHADOW','FORM','AND','FOR','BUT','BY','AS','AT','HE','IT','ON',
    'LIBER','PRIMUS','BOOK','FIRST','SACRED','UNSEEN','GUIDE'
}

def load_flat(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return []
    return [RUNE_TO_IDX[ch] for ch in path.read_text(encoding='utf-8') if ch in RUNE_TO_IDX]

def load_words(pg):
    """Load page as list of words (each word = list of rune indices)."""
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return []
    text = path.read_text(encoding='utf-8')
    words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return words

def ioc(vals):
    if len(vals) < 2: return 0.0
    c = Counter(vals)
    n = len(vals)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def score_gp_seq(seq):
    """Score a sequence of GP indices for English plausibility."""
    if not seq: return 0.0
    # Convert GP to approximate letters
    letters = []
    for v in seq:
        s = GP_TO_LETTERS.get(v, 'X')
        letters.extend(list(s))
    freq = Counter(letters)
    n = len(letters)
    if n == 0: return 0.0
    
    # Chi-squared style score vs English
    score = 0.0
    for l, expected_pct in ENG_FREQ.items():
        obs = freq.get(l, 0) / n * 100
        score -= (obs - expected_pct) ** 2 / (expected_pct + 0.1)
    return score

def score_words(seq):
    """Score by matching LP vocabulary words."""
    # Try to parse the sequence as words using word boundary logic
    full_text = ''.join(IDX_TO[v] for v in seq)
    score = 0
    # Check for LP word matches
    for word in LP_VOCAB:
        count = full_text.count(word)
        if count > 0:
            score += len(word) * 10 * count
    return score

def phrase_to_gp(phrase):
    """Convert English phrase string to GP indices. Returns list of ints."""
    LP_LETTER_MAP = {
        'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
        'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
        'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
        'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
    }
    # Handle digraphs first, then single letters
    result = []
    i = 0
    phrase = phrase.upper().replace(' ', '').replace('-','')
    while i < len(phrase):
        # Try digraph first
        if i+1 < len(phrase):
            dg = phrase[i:i+2]
            if dg in LP_LETTER_MAP:
                result.append(LP_LETTER_MAP[dg])
                i += 2
                continue
        ch = phrase[i]
        if ch in LP_LETTER_MAP:
            result.append(LP_LETTER_MAP[ch])
        i += 1
    return result

# ─── Main ────────────────────────────────────────────────────────────────────
# Build global cipher stream
cumoffs = {}; cum = 0
flats = {pg: load_flat(pg) for pg in range(21, 55)}
for pg in range(21, 55):
    cumoffs[pg] = cum
    cum += len(flats[pg])

global_cipher = []
for pg in range(21, 55):
    global_cipher.extend(flats[pg])
total = len(global_cipher)

PERIOD = 6726

# Build diff streams
diff12 = [(global_cipher[i] - global_cipher[i+PERIOD]) % M
          for i in range(PERIOD)]  # for period 1 vs 2

diff13 = [(global_cipher[i] - global_cipher[i+2*PERIOD]) % M
          for i in range(min(PERIOD, total - 2*PERIOD))]  # period 1 vs 3

print(f"Total runes: {total}, Period: {PERIOD}")
print(f"Diff12 length: {len(diff12)} (positions 0..{PERIOD-1} vs {PERIOD}..{2*PERIOD-1})")
print(f"Diff13 length: {len(diff13)} (positions 0..{len(diff13)-1} vs {2*PERIOD}..)")
print()

# Cribs to try — LP-style phrases
CRIBS = [
    "AN INSTRUCTION",
    "SOME WISDOM",
    "A WARNING",
    "THE LOSS OF DIVINITY",
    "WELCOME PILGRIM",
    "KNOW THIS",
    "THE PRIMES ARE SACRED",
    "ALL THINGS SHOULD BE ENCRYPTED",
    "PROGRAM YOUR MIND",
    "SEEK TRUTH WITHIN YOURSELF",
    "CHAPTER",
    "THE CIRCUMFERENCE",
    "SOME WISDOM AMASS",
    "DIVINE",
    "FOLLOW YOUR TRUTH",
    "DISCOVER TRUTH INSIDE YOURSELF",
    "IMPOSE NOTHING ON OTHERS",
    "QUESTION ALL THINGS",
    "BEING",
    "AND",
    "THE",
    "INSTRUCTION",
    "LIBER PRIMUS",
    "AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    "WELCOME PILGRIM TO THE SACRED",
]

print("=== CRIB DRAGGING ATTACK (Period 1 vs Period 2) ===")
print("Note: diff12 = plain1 - plain2 (mod 29)")
print("      If crib = plain1 => plain2 = crib - diff12")
print()

best_results = []

for crib_str in CRIBS:
    crib = phrase_to_gp(crib_str)
    crib_len = len(crib)
    if crib_len < 4: continue
    
    for mode in ['sub', 'add']:
        # mode=sub: cipher = key + plain (ADD mode), diff12 = plain1 - plain2
        # mode=add: cipher = key - plain (SUB mode), diff12 = plain2 - plain1 (sign flipped)
        for start in range(0, PERIOD - crib_len):
            # Hypothesis: plain1[start..start+n] = crib
            d = diff12[start:start+crib_len]
            
            if mode == 'sub':
                # plain2 = plain1 - diff12
                plain2 = [(crib[j] - d[j]) % M for j in range(crib_len)]
            else:
                # plain2 = plain1 + diff12
                plain2 = [(crib[j] + d[j]) % M for j in range(crib_len)]
            
            s2 = score_words(plain2)
            s1 = score_words(crib)  # crib itself
            
            if s2 >= 50:  # paired plaintext is also LP-like
                p2_start = start + PERIOD
                # Find which page
                pg1 = next((p for p in range(21,55) if cumoffs[p]<=start<cumoffs[p]+len(flats[p])), None)
                pg2 = next((p for p in range(21,55) if cumoffs[p]<=p2_start<cumoffs[p]+len(flats[p])), None)
                
                p1_txt = ''.join(IDX_TO[v] for v in crib)
                p2_txt = ''.join(IDX_TO[v] for v in plain2)
                
                best_results.append((s2, start, p2_start, pg1, pg2, mode, crib_str, p1_txt, p2_txt))

best_results.sort(key=lambda x: -x[0])

print(f"Top crib matches (pairs with score >= 50):")
seen = set()
for score, s1, s2, pg1, pg2, mode, crib_str, p1txt, p2txt in best_results[:40]:
    key = (s1, crib_str[:15], mode)
    if key in seen: continue
    seen.add(key)
    print(f"  [{mode}] score={score:4d} start={s1:4d}(P{pg1}) => +6726={s2:5d}(P{pg2})")
    print(f"    P1: '{p1txt[:60]}' (={crib_str})")
    print(f"    P2: '{p2txt[:60]}'")
    print()

print()
print("=== EXHAUSTIVE DIFF STREAM ANALYSIS ===")
print("Computing entropy and pattern analysis of diff12 stream")

# IoC of diff12 — if cipher is ADD: diff12[i] = plain1[i] - plain2[i]
# IoC of NATURAL LP text pairs should be high (~1.5-2.0) if texts are English
# IoC near 1.0 means the differences look random

diff_ioc = ioc(diff12)
print(f"  IoC(diff12) = {diff_ioc:.4f}  (LP text IoC ~2.0, random ~1.0)")
print(f"  Expected for English pair: ~1.2-1.5")
print()

# Distribution of diff values
diff_cnt = Counter(diff12)
print("  Diff12 distribution:")
for v in range(M):
    n = diff_cnt.get(v, 0)
    bar = '#' * (n // 10)
    print(f"    diff={v:2d}: {n:4d} {bar}")

print()
# Check the KNOWN REGION (3001-4312 = P27-P31): diff12 should be 0
matched = [(i, diff12[i]) for i in range(3001, min(4313, PERIOD)) if diff12[i] == 0]
non_matched = [(i, diff12[i]) for i in range(3001, min(4313, PERIOD)) if diff12[i] != 0]
print(f"  In P27-P31 match region (3001-4312): {len(matched)} zeros, {len(non_matched)} non-zeros")
print(f"  (Expected: 1312 zeros, 0 non-zeros if plain1=plain2)")
