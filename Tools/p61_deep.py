"""
P61 deep attack with DIVINITY key + all F-skip combinations.
P61: 394 runes, 16 F runes, non-F = 378.
DIVINITY used on P03, P04, P61 per key hints.
Also test P61 with exhaustive F-skip (2^16 = 65536 combos - feasible with pruning).
"""
import os
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

DIGRAPHS_ORDERED = [('TH',2),('NG',21),('EA',28),('OE',22),('EO',12),('AE',25),('IA',27)]
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
    while i < len(text):
        found = False
        for dg, val in DIGRAPHS_ORDERED:
            if text[i:i+len(dg)] == dg:
                result.append(val)
                i += len(dg)
                found = True
                break
        if not found:
            if text[i] in ENG2GP:
                result.append(ENG2GP[text[i]])
            i += 1
    return result

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

def score_text(text):
    s = 0
    for w in ['WISDOM','THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS',
              'WHICH','ARE','WITHIN','HOLY','LIVES','EACH','BEING','UNTO',
              'YOURSELF','INTELLIGENCE','INSTRUCTION','COMMAND','YOUR','OWN',
              'SELF','LAW','SACRED','DIVINITY','PILGRIM','TRUTH','BELIEVE',
              'NOTHING','FIND','SEEK','WEB','DEEP','HASHES','EXISTS','END',
              'PAGE','DUTY','EVERY','PRESERVE','WEAK','CONSUME','ENOUGH',
              'FOLLOW','DOGMA','BELONG','CIRCUMFERENCE','LOSS','KOAN','MASTER',
              'WHAT','HAVE','KNOW','TRUE','FROM','THEY','WILL','THEIR','HAS',
              'WELCOME','STUDY','HERE','ASKED','STUDENT','NAME','CALLED',
              'DOOR','WENT','DECIDED','MAN','CAME','SAID','TOLD','GIVE',
              'VOICE','LESSON','DURING','JUST','WARNING','EXCEPT','BOOK',
              'PRACTICE','THREE','BEHAVIORS','CAUSE','CONSUMPTION','WE',
              'BECAUSE','TOO','MUCH','MOST','THINGS','WORTH','PRESERVING',
              'STRONG','LATER','OBTAIN','NEED','LUCK','NOW','PRIMES',
              'TOTIENT','ENCRYPTED','SHOULD','PARABLE','LIKE','INSTAR',
              'TUNNELING','SURFACE','MUST','SHED','EMERGE','OUR','SOME',
              'TEST','YOUR','QUESTION','DO','FOUR','UNREASONABLE','DAY',
              'WAS','WHOSE','TEACHER','HIS','HER','WHO','HOW','WHEN',
              'THERE','THEM','BEEN','HIM','THEN','ONLY','ALSO','WOULD',
              'AFTER','BEFORE','INTO','OVER','COULD','MAY','VERY','THESE',
              'OTHER','ABOUT','MORE','MAKE','FIRST','THOSE','SUCH','UP',
              'LONG','MANY','WAY','COULD','PEOPLE','WORK','PART','TAKE',
              'COME','BECOME','ACT','TWO','SAME','STILL','BACK','GOOD',
              'GREAT','LITTLE','UNDER','WORLD','POWER','THING','PLACE',
              'HAND','HIGH','KEEP','LAST','LET','THOUGHT','POINT','WORD',
              'GOING','WHERE','COME','LEAVE','LOSS','TELL','CALL','STATE']:
        c = text.count(w)
        s += c * len(w)
    return s

with open('LiberPrimus/pages/page_61/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
f_pos = [i for i in range(N) if cipher[i] == 0]
n_f = len(f_pos)
print(f"P61: {N} runes, {n_f} F runes at {f_pos}")
print(f"Non-F: {N - n_f}")

# Check divisibility for DIVINITY
DIVINITY = eng_to_gp("DIVINITY")
KL = len(DIVINITY)
non_f = N - n_f
print(f"Non-F % {KL} = {non_f % KL}")

# First: standard Vigenère (no F-skip) with all offsets
print("\n===== STANDARD VIGENÈRE (no F-skip) =====")
for mode in ['SUB', 'ADD', 'BEAU']:
    for off in range(KL):
        dec = []
        for i in range(N):
            kv = DIVINITY[(i + off) % KL]
            if mode == 'SUB': dec.append((cipher[i] - kv) % MOD)
            elif mode == 'ADD': dec.append((cipher[i] + kv) % MOD)
            else: dec.append((kv - cipher[i]) % MOD)
        text = gp_to_lat(dec)
        sc = score_text(text)
        if sc >= 50:
            print(f"  {mode} off={off}: score={sc:3d} | {text[:120]}")

# All-F-literal
print("\n===== ALL-F LITERAL =====")
for mode in ['SUB', 'ADD', 'BEAU']:
    for off in range(KL):
        dec = []
        k = off
        for i in range(N):
            if cipher[i] == 0:
                dec.append(0)
            else:
                kv = DIVINITY[k % KL]
                if mode == 'SUB': dec.append((cipher[i] - kv) % MOD)
                elif mode == 'ADD': dec.append((cipher[i] + kv) % MOD)
                else: dec.append((kv - cipher[i]) % MOD)
                k += 1
        text = gp_to_lat(dec)
        sc = score_text(text)
        if sc >= 50:
            print(f"  {mode} off={off}: score={sc:3d} | {text[:120]}")

# Exhaustive F-skip: 2^16 = 65536 combinations
# But with 16 F's this is expensive (65536 * 8 * 3 = ~1.5M). 
# Let's do SUB only with top offsets first
print("\n===== EXHAUSTIVE F-SKIP (SUB mode) =====")
print(f"Testing 2^{n_f} = {2**n_f} F-combos × {KL} offsets...")

best_results = []
for f_mask in range(2**n_f):
    lit_set = set()
    for bit in range(n_f):
        if f_mask & (1 << bit):
            lit_set.add(f_pos[bit])
    
    for off in range(KL):
        dec = []
        k = off
        for i in range(N):
            if i in lit_set:
                dec.append(0)
            else:
                kv = DIVINITY[k % KL]
                dec.append((cipher[i] - kv) % MOD)
                k += 1
        text = gp_to_lat(dec)
        sc = score_text(text)
        if sc >= 120:  # High threshold for 394 runes
            mask_str = format(f_mask, f'0{n_f}b')
            best_results.append((sc, off, mask_str, sum(1 for b in range(n_f) if f_mask & (1<<b)), text))

best_results.sort(reverse=True)
print(f"\nTop 20 exhaustive results (score >= 120):")
for sc, off, mask, n_lit, text in best_results[:20]:
    print(f"  score={sc:4d} off={off} lit={n_lit:2d} mask={mask}: {text[:120]}")

# Also check if P61 is already solved (might be in decoded.txt)
import glob
for f in glob.glob('LiberPrimus/pages/page_61/*'):
    print(f"  Found: {f}")

# Check README
readme_path = 'LiberPrimus/pages/page_61/README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\nP61 README (first 500 chars):\n{content[:500]}")

print("\n=== DONE ===")
