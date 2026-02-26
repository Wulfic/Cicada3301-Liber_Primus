"""
P18 Crib validation - apply promising cribs and show resulting text.
Test if multi-word cribs produce globally consistent improvements.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53

confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}

# HC best key
hc_key = [28, 24, 21, 6, 19, 6, 6, 5, 11, 15, 8, 2, 18, 18, 25, 25, 15, 10, 16, 24, 
13, 11, 20, 2, 5, 5, 27, 3, 12, 19, 14, 17, 5, 18, 4, 25, 27, 26, 24, 16, 5, 8, 
23, 26, 21, 25, 7, 25, 24, 28, 1, 21, 27]

with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)

# Parse structure
tokens = []
for ch in raw:
    if ch in GP:
        tokens.append(('rune', len([t for t in tokens if t[0]=='rune'])))
    elif ch == '-':
        tokens.append(('sep', None))
    elif ch == '.':
        tokens.append(('period', None))
    elif ch == '\n':
        tokens.append(('newline', None))

# Fix: re-count
tokens = []
rune_count = 0
for ch in raw:
    if ch in GP:
        tokens.append(('rune', rune_count))
        rune_count += 1
    elif ch == '-':
        tokens.append(('sep', None))
    elif ch == '.':
        tokens.append(('period', None))
    elif ch == '\n':
        tokens.append(('newline', None))

def show_text(key, mark_unknown_keys=None):
    dec = [(cipher[i] - key[i % KLEN]) % MOD for i in range(N)]
    result = []
    for tok_type, tok_val in tokens:
        if tok_type == 'rune':
            i = tok_val
            kp = i % KLEN
            val = dec[i]
            lat = LAT[val]
            if mark_unknown_keys and kp in mark_unknown_keys:
                lat = f'[{lat}]'
            result.append(lat)
        elif tok_type == 'sep':
            result.append(' ')
        elif tok_type == 'period':
            result.append('. ')
        elif tok_type == 'newline':
            result.append('\n')
    return ''.join(result)

unknown = sorted(set(range(KLEN)) - set(confirmed.keys()))

# ===== Crib 1: "THE TRUTH" for words 14-15 ("THE DISTH") =====
crib1 = {0: 5, 1: 9, 52: 5}  # key positions implied

# ===== Crib 2: "IS SACRED" for words 9-10 ("PR ESOWSU") =====
crib2 = {30: 17, 31: 6, 32: 8, 33: 9, 34: 2, 35: 28, 36: 24, 37: 4}

# ===== Crib 3: "A WARNING" for words 57-58 ("A HOENGXIAE") =====
crib3 = {7: 6, 8: 9, 9: 3, 10: 13, 11: 2, 12: 22}

# Show HC baseline
print("=" * 70)
print("BASELINE (HC best, unknown in [brackets]):")
print("=" * 70)
print(show_text(hc_key, mark_unknown_keys=set(unknown)))
print()

# Apply Crib 1 only
key1 = list(hc_key)
for kp, kv in crib1.items():
    key1[kp] = kv
remaining1 = set(unknown) - set(crib1.keys())
print("=" * 70)
print("CRIB 1: 'THE TRUTH' (key[0]=5,key[1]=9,key[52]=5)")
print("=" * 70)
print(show_text(key1, mark_unknown_keys=remaining1))
print()

# Apply Crib 2 only
key2 = list(hc_key)
for kp, kv in crib2.items():
    key2[kp] = kv
remaining2 = set(unknown) - set(crib2.keys())
print("=" * 70)
print("CRIB 2: 'IS SACRED' (key[30-37] resolved)")
print("=" * 70)
print(show_text(key2, mark_unknown_keys=remaining2))
print()

# Apply Crib 3 only
key3 = list(hc_key)
for kp, kv in crib3.items():
    key3[kp] = kv
remaining3 = set(unknown) - set(crib3.keys())
print("=" * 70)
print("CRIB 3: 'A WARNING' (key[7-12] resolved)")
print("=" * 70)
print(show_text(key3, mark_unknown_keys=remaining3))
print()

# Apply ALL three cribs
key_all = list(hc_key)
all_cribs = {}
all_cribs.update(crib1)
all_cribs.update(crib2)
all_cribs.update(crib3)
for kp, kv in all_cribs.items():
    key_all[kp] = kv
remaining_all = set(unknown) - set(all_cribs.keys())
print("=" * 70)
print(f"ALL 3 CRIBS COMBINED (remaining unknown: {sorted(remaining_all)})")
print("=" * 70)
print(show_text(key_all, mark_unknown_keys=remaining_all))
print()

# IoC computation
from collections import Counter
def ioc(seq):
    if len(seq) < 2: return 0
    c = Counter(seq)
    n = len(seq)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)) * MOD

dec_hc = [(cipher[i] - hc_key[i % KLEN]) % MOD for i in range(N)]
dec_all = [(cipher[i] - key_all[i % KLEN]) % MOD for i in range(N)]
print(f"IoC baseline (HC):  {ioc(dec_hc):.3f}")
print(f"IoC all cribs:      {ioc(dec_all):.3f}")
print()

# Now, with all 3 cribs applied, we only have key[45] and key[49] unknown
# That's just 2 positions! Let's try all 29*29=841 combinations
print("=" * 70)
print("EXHAUSTIVE SEARCH: key[45] x key[49] (remaining unknowns)")
print("=" * 70)

# We need to count single-letter words that are I or A (common English single-letter words)
# and also look at overall readability

from collections import defaultdict
import math

# Build a simple bigram model from LP text
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS_MAP = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []; i = 0; text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS_MAP:
            result.append(DIGRAPHS_MAP[text[i:i+2]])
            i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
            i += 1
        else: i += 1
    return result

corpus = eng_to_gp("""A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH
DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN
EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING
YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES
JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE
LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE
YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY
COMMAND YOUR OWN SELF THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE
REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR
THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY
CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS
WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH
WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER
TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING
PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK
IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN
THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING
ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT
OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT
THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH
IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE
THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY
AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN
BE PREPARED TO DESTROY ALL THAT YOU OWN
PROGRAM YOUR MIND PROGRAM REALITY""")

bg_counts = defaultdict(int)
for i in range(len(corpus)-1):
    bg_counts[(corpus[i], corpus[i+1])] += 1
total_bg = len(corpus) - 1
FLOOR_BG = math.log10(0.01 / total_bg)
bg_logp = {}
for bg, cnt in bg_counts.items():
    bg_logp[bg] = math.log10(cnt / total_bg)

def bg_score(dec):
    s = 0.0
    for i in range(len(dec)-1):
        s += bg_logp.get((dec[i], dec[i+1]), FLOOR_BG)
    return s

best_bg = -float('inf')
best_45 = 0
best_49 = 0
results = []

for v45 in range(MOD):
    for v49 in range(MOD):
        key_test = list(key_all)
        key_test[45] = v45
        key_test[49] = v49
        dec_test = [(cipher[i] - key_test[i % KLEN]) % MOD for i in range(N)]
        score = bg_score(dec_test)
        ic = ioc(dec_test)
        results.append((score, ic, v45, v49))
        if score > best_bg:
            best_bg = score
            best_45 = v45
            best_49 = v49

results.sort(key=lambda x: -x[0])
print("Top 20 (key[45], key[49]) by bigram score:")
for score, ic, v45, v49 in results[:20]:
    key_test = list(key_all)
    key_test[45] = v45
    key_test[49] = v49
    dec_test = [(cipher[i] - key_test[i % KLEN]) % MOD for i in range(N)]
    text_preview = show_text(key_test)[:200]
    print(f"  key[45]={v45:2d}({LAT[v45]:3s}) key[49]={v49:2d}({LAT[v49]:3s})  bg={score:.2f} IoC={ic:.3f}")

# Best result
print()
print("=" * 70)
print(f"BEST: key[45]={best_45}({LAT[best_45]}), key[49]={best_49}({LAT[best_49]})")
print("=" * 70)
key_final = list(key_all)
key_final[45] = best_45
key_final[49] = best_49
print(show_text(key_final))
print()
print(f"IoC: {ioc([(cipher[i] - key_final[i % KLEN]) % MOD for i in range(N)]):.3f}")
print()
print(f"Final key: {key_final}")
print(f"Final key (LAT): {[LAT[k] for k in key_final]}")
