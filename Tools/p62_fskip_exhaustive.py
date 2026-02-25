"""
P62 — Exhaustive F-skip combination search.
9 F runes → 2^9 = 512 combinations of literal vs encrypted F.
For each, test all 8 offsets × 3 modes.
"""
import os
from itertools import product

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

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS_ORDERED = [('TH',2),('NG',21),('EA',28),('OE',22),('EO',12),('AE',25),('IA',27)]

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

with open('LiberPrimus/pages/page_62/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)

f_positions = [i for i in range(N) if cipher[i] == 0]
print(f"P62: {N} runes, {len(f_positions)} F runes at {f_positions}")

DIVINITY = eng_to_gp("DIVINITY")
KL = len(DIVINITY)

# English frequency scoring based on common bigrams and words
COMMON_BIGRAMS = {'TH':15,'HE':12,'IN':10,'AN':10,'ER':10,'ON':9,'RE':9,'ND':8,
                  'EN':8,'AT':8,'OU':8,'ED':7,'HA':7,'TO':7,'OR':7,'IT':7,
                  'IS':7,'HI':6,'ES':6,'NG':6,'ST':6,'AL':6,'TE':6,'AR':6,
                  'NT':6,'SE':6,'OF':6,'LE':6,'EA':6,'IO':6}

def score_text(text):
    s = 0
    for w in ['WISDOM','THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS',
              'WHICH','ARE','WITHIN','HOLY','LIVES','EACH','BEING','UNTO',
              'YOURSELF','INTELLIGENCE','INSTRUCTION','COMMAND','YOUR','OWN',
              'SELF','LAW','SACRED']:
        c = text.count(w)
        s += c * len(w) * 2  # Double weight for known words
    # Also score common bigrams
    for bg, wt in COMMON_BIGRAMS.items():
        s += text.count(bg) * wt // 5
    return s

# ===== EXHAUSTIVE F-SKIP COMBINATION SEARCH =====
print(f"\nTesting all 2^{len(f_positions)} = {2**len(f_positions)} F-literal combinations × {KL} offsets × 3 modes...")
print(f"Total: {2**len(f_positions) * KL * 3} combinations")

best_overall = []

for f_mask in range(2**len(f_positions)):
    # Which F positions are literal (1) vs encrypted (0)
    literal_set = set()
    for bit in range(len(f_positions)):
        if f_mask & (1 << bit):
            literal_set.add(f_positions[bit])
    
    # Count how many non-literal positions (need to check if MOD 8 works)
    non_literal = N - len(literal_set)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        for off in range(KL):
            dec = []
            k = off
            for i in range(N):
                if i in literal_set:
                    dec.append(0)  # Literal F
                else:
                    kv = DIVINITY[k % KL]
                    if mode == 'SUB':
                        dec.append((cipher[i] - kv) % MOD)
                    elif mode == 'ADD':
                        dec.append((cipher[i] + kv) % MOD)
                    else:
                        dec.append((kv - cipher[i]) % MOD)
                    k += 1
            
            text = gp_to_lat(dec)
            sc = score_text(text)
            
            if sc >= 80:  # High threshold
                mask_str = ''.join('1' if f_positions[b] in literal_set else '0' for b in range(len(f_positions)))
                best_overall.append((sc, mode, off, mask_str, text, len(literal_set)))

best_overall.sort(reverse=True)
print(f"\nTop 30 results (score >= 80):")
for sc, mode, off, mask, text, n_lit in best_overall[:30]:
    print(f"  score={sc:4d} {mode:5s} off={off} F-mask={mask} (lit={n_lit}): {text[:120]}")

# ===== DEEP ANALYSIS OF TOP RESULTS =====
if best_overall:
    print("\n" + "="*80)
    print("DETAILED TOP 5 RESULTS")
    print("="*80)
    
    for idx, (sc, mode, off, mask, text, n_lit) in enumerate(best_overall[:5]):
        print(f"\n--- Result #{idx+1}: {mode} off={off} mask={mask} score={sc} ---")
        print(f"Full text: {text}")
        
        # Try to segment into known words
        pos = 0; words = []; unk_count = 0
        WORD_LIST = ['WISDOM','YOU','ARE','A','BEING','UNTO','YOURSELF','LAW','EACH',
                     'INTELLIGENCE','IS','HOLY','FOR','ALL','THAT','LIVES','AN',
                     'INSTRUCTION','COMMAND','YOUR','OWN','SELF','THE','AND','WITHIN',
                     'CIRCUMFERENCE','DIVINITY','PILGRIM','SACRED','TRUTH','BELIEVE',
                     'NOTHING','FIND','SEEK','DEEP','WEB','NOT','THIS','WHICH','WITH',
                     'BUT','DUTY','EVERY','CONSUME','LOSS','TEST','KNOW','TRUE','MASTER',
                     'PRESERVE','WEAK','FOLLOW','DOGMA','BELONG','OF','FROM','WHAT','WE',
                     'HAVE','NOW','BY','ENOUGH','EMERGE','LIKE','INSTAR','IF','OR','IT',
                     'TO','DO','BE','HAS','IN','NO','AS','ON','AT','SO','HE','SHE']
        while pos < len(text):
            found = False
            for wlen in range(min(20, len(text)-pos), 0, -1):
                chunk = text[pos:pos+wlen]
                if chunk in WORD_LIST:
                    words.append(chunk)
                    pos += wlen
                    found = True
                    break
            if not found:
                words.append('['+text[pos]+']')
                pos += 1
                unk_count += 1
        
        print(f"Segmented ({unk_count} unknown chars): {' '.join(words)}")

# ===== ALSO CHECK: Skip ALL F's vs only select ones =====
print("\n" + "="*80)
print("F-SKIP ALL vs NONE baseline")
print("="*80)

# All F's literal
all_lit = set(f_positions)
for mode in ['SUB']:
    for off in range(KL):
        dec = []
        k = off
        for i in range(N):
            if i in all_lit:
                dec.append(0)
            else:
                kv = DIVINITY[k % KL]
                dec.append((cipher[i] - kv) % MOD)
                k += 1
        text = gp_to_lat(dec)
        sc = score_text(text)
        print(f"  ALL-literal {mode} off={off}: score={sc:3d} | {text[:100]}")

# No F's literal (standard Vigenère)
print()
for mode in ['SUB']:
    for off in range(KL):
        dec = [(cipher[i] - DIVINITY[(i+off)%KL]) % MOD for i in range(N)]
        text = gp_to_lat(dec)
        sc = score_text(text)
        print(f"  NO-literal  {mode} off={off}: score={sc:3d} | {text[:100]}")

print("\n=== DONE ===")
