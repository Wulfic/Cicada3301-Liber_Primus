"""
P18 SOLVER v3 - Constrained search
Fix single-rune word positions (must be I=10 or A=24), then optimize rest.
2^7 = 128 constraint combinations × bigram hill-climbing.
Also tries F-skip variants.
"""
import os, itertools
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
KLEN = 53

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    path = f'LiberPrimus/pages/page_{pg:02d}/runes.txt'
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    words = []
    current = []
    start = 0
    pos = 0
    for c in raw:
        if c in GP:
            if not current:
                start = pos
            current.append(GP[c])
            pos += 1
        elif current:
            words.append((start, current))
            current = []
    if current:
        words.append((start, current))
    return runes, words

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1))

eng_gp_freq = [0.022, 0.038, 0.035, 0.075, 0.060, 0.036, 0.020, 0.024,
               0.061, 0.067, 0.070, 0.002, 0.005, 0.019, 0.002, 0.063,
               0.056, 0.015, 0.127, 0.024, 0.040, 0.015, 0.003, 0.043,
               0.082, 0.003, 0.020, 0.003, 0.003]
tot = sum(eng_gp_freq)
eng_gp_freq = [f/tot for f in eng_gp_freq]

# Bigram bonus scores
bigram_bonus = {}
bg_pairs = [
    (2,18,3),(8,18,2.5),(10,9,2),(18,4,2),(24,9,2),(4,18,2),(3,9,1.5),(24,16,1.5),
    (18,9,1.5),(9,23,1.5),(16,10,1.5),(18,15,1.5),(3,4,1.5),(16,18,1.5),(3,0,1.5),
    (18,23,1.5),(10,15,1.5),(10,16,1.5),(24,20,1.5),(24,4,1.5),(15,16,1.5),(9,18,1.5),
    (2,24,1.5),(2,10,1.5),(2,3,1),(15,18,1),(20,18,1),(20,10,1),(9,3,1),(23,18,1),
    (24,15,1),(0,3,1),(7,10,1),(7,24,1),(17,18,1),(5,3,1),(3,19,1),(19,18,1),
    (2,4,1),(10,20,1),(24,21,1.5),(21,23,1),  # NG-D
]
for a, b, s in bg_pairs:
    bigram_bonus[(a,b)] = bigram_bonus.get((a,b), 0) + s

# Word lists
common_words = {'THE','AND','OF','TO','IN','IS','IT','THAT','WAS','FOR','ON','ARE','WITH',
                'AS','AT','BE','THIS','FROM','OR','AN','BY','NOT','BUT','WHAT','ALL','A','I',
                'HE','SHE','THEY','WE','YOU','HIS','HER','ITS','OUR','THEIR','WHO','WHICH',
                'HAS','HAD','HAVE','BEEN','ONE','EACH','LIKE','DO','SO','IF','NO','MY','UP',
                'ABOUT','OUT','THEM','THEN','INTO','SOME','THAN','OVER','SUCH','ALSO',
                'TIME','VERY','YOUR','MAKE','HOW','THERE','WHEN','COULD','THESE','THOSE',
                'WOULD','OTHER','MORE','AFTER','MANY','WILL','SHALL','WITHIN','DEEP','WEB',
                'KNOW','WISDOM','YET','NOW','HERE','ONLY','SEEK','FIND','SEE','TRUTH',
                'SELF','REALITY','BEING','MIND','LIFE','DEATH','THROUGH','BETWEEN',
                'PATH','WAY','MUST','CAN','MAY','PART','WHOLE','BEFORE','INTO',
                'EVERY','NEVER','ALWAYS','ONCE','MOST','FIRST','LAST','NEXT','OWN',
                'SAME','MUCH','BOTH','STILL','EVEN','TOO','JUST','UNDER','OVER','UPON',
                'SAID','CAME','TOOK','GAVE','MADE','KNEW','WENT','TOLD','DID'}

cipher, words = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

# Single-rune words and their key bucket constraints
singles = [(start, word[0]) for start, word in words if len(word) == 1]
print(f"Single-rune words: {len(singles)}")
for pos, val in singles:
    print(f"  pos={pos} bucket={pos%KLEN} cipher={val}({LAT[val]})")

# For each mode, derive the constraint key values
# Beaufort: plain = (key - cipher) % 29, so key = (plain + cipher) % 29
# SUB: plain = (cipher - key) % 29, so key = (cipher - plain) % 29
# ADD: plain = (cipher + key) % 29, so key = (plain - cipher) % 29

def compute_single_constraints(singles, mode):
    """For each single-rune word, compute {bucket: (key_if_I, key_if_A)}"""
    constraints = {}
    for pos, val in singles:
        bucket = pos % KLEN
        if mode == 'SUB':
            kI = (val - 10) % 29
            kA = (val - 24) % 29
        elif mode == 'ADD':
            kI = (10 - val) % 29
            kA = (24 - val) % 29
        elif mode == 'BEAUFORT':
            kI = (10 + val) % 29
            kA = (24 + val) % 29
        constraints[bucket] = (kI, kA)
    return constraints

def decrypt(cipher, key, mode):
    if mode == 'SUB':
        return [(cipher[i] - key[i%KLEN]) % 29 for i in range(len(cipher))]
    elif mode == 'ADD':
        return [(cipher[i] + key[i%KLEN]) % 29 for i in range(len(cipher))]
    elif mode == 'BEAUFORT':
        return [(key[i%KLEN] - cipher[i]) % 29 for i in range(len(cipher))]

def score_text(dec, word_list):
    """Combined score: bigram + word match."""
    # Bigram component
    bg = 0
    for i in range(len(dec)-1):
        bg += bigram_bonus.get((dec[i], dec[i+1]), 0)
        if dec[i] in {11, 12, 14, 22, 25, 27, 28}: bg -= 0.3  # rare rune penalty
    
    # Word component
    dw = []
    for start, word in word_list:
        wd = [dec[start+j] for j in range(len(word))]
        dw.append(''.join(LAT[v] for v in wd).upper())
    wc = sum(3 for w in dw if w in common_words)
    
    # IoC component
    ic = ioc(dec) * 29
    ic_bonus = max(0, (ic - 1.0) * 50)
    
    return bg + wc + ic_bonus

# Pre-compute column frequency best shifts as initial values
columns = [[] for _ in range(KLEN)]
for i in range(N): columns[i%KLEN].append(cipher[i])

for mode in ['SUB', 'ADD', 'BEAUFORT']:
    print(f"\n{'='*80}")
    print(f"MODE: {mode}")
    print(f"{'='*80}")
    
    constraints = compute_single_constraints(singles, mode)
    constrained_buckets = sorted(constraints.keys())
    print(f"Constrained buckets: {constrained_buckets}")
    for b in constrained_buckets:
        kI, kA = constraints[b]
        print(f"  bucket {b}: key_if_I={kI}({LAT[kI]}) key_if_A={kA}({LAT[kA]})")
    
    # Compute freq-based initial key for unconstrained positions
    init_key = [0] * KLEN
    for col_idx in range(KLEN):
        col = columns[col_idx]
        n = len(col)
        best_shift = 0
        best_score = -999
        for shift in range(29):
            if mode == 'SUB':
                dec = [(v - shift) % 29 for v in col]
            elif mode == 'ADD':
                dec = [(v + shift) % 29 for v in col]
            elif mode == 'BEAUFORT':
                dec = [(shift - v) % 29 for v in col]
            counts = Counter(dec)
            score = sum(counts.get(i,0)/n * eng_gp_freq[i] for i in range(29))
            if score > best_score:
                best_score = score
                best_shift = shift
        init_key[col_idx] = best_shift
    
    # Try all 2^7 = 128 I/A combinations for constrained buckets
    best_combo_score = -999
    best_combo_key = None
    best_combo_text = None
    best_combo_words = None
    best_combo_idx = -1
    
    n_combos = 2 ** len(constrained_buckets)
    for combo_idx in range(n_combos):
        key = list(init_key)
        
        # Set constrained positions based on combo bits
        for bit, bucket in enumerate(constrained_buckets):
            kI, kA = constraints[bucket]
            if combo_idx & (1 << bit):
                key[bucket] = kA  # A
            else:
                key[bucket] = kI  # I
        
        # Hill-climb UNconstrained positions
        for iteration in range(3):
            improved = True
            while improved:
                improved = False
                for pos in range(KLEN):
                    if pos in constraints: continue  # Don't change constrained positions
                    
                    old_val = key[pos]
                    best_val = old_val
                    dec = decrypt(cipher, key, mode)
                    best_s = score_text(dec, words)
                    
                    for val in range(29):
                        if val == old_val: continue
                        key[pos] = val
                        dec = decrypt(cipher, key, mode)
                        s = score_text(dec, words)
                        if s > best_s:
                            best_s = s
                            best_val = val
                    
                    key[pos] = best_val
                    if best_val != old_val:
                        improved = True
        
        dec = decrypt(cipher, key, mode)
        sc = score_text(dec, words)
        
        if sc > best_combo_score:
            best_combo_score = sc
            best_combo_key = list(key)
            
            dw = []
            for start, word in words:
                wd = [dec[start+j] for j in range(len(word))]
                dw.append(''.join(LAT[v] for v in wd))
            best_combo_text = ''.join(LAT[v] for v in dec)
            best_combo_words = dw
            best_combo_idx = combo_idx
    
    # Print results
    dec = decrypt(cipher, best_combo_key, mode)
    ic = ioc(dec) * 29
    wc = sum(1 for w in best_combo_words if w.upper() in common_words)
    
    # Decode the combo to show I/A assignments
    ia_assign = []
    for bit, bucket in enumerate(constrained_buckets):
        if best_combo_idx & (1 << bit):
            ia_assign.append(f"bucket{bucket}=A")
        else:
            ia_assign.append(f"bucket{bucket}=I")
    
    print(f"\nBest combo #{best_combo_idx}: score={best_combo_score:.1f} IoC={ic:.3f} words={wc}/{len(best_combo_words)}")
    print(f"I/A: {', '.join(ia_assign)}")
    print(f"Key: {best_combo_key}")
    key_lat = ''.join(LAT[v] for v in best_combo_key)
    print(f"Key (Latin): {key_lat}")
    print(f"Words: {' '.join(best_combo_words[:35])}")
    print(f"Text: {best_combo_text[:300]}")
    
    # Show top word matches
    matched = [(w, i) for i, w in enumerate(best_combo_words) if w.upper() in common_words]
    print(f"Matched words: {matched}")

print("\n=== DONE ===")
