"""
P18 SOLVER v5 - Context-aware bucket determination
For each undetermined bucket, show ALL affected cipher positions and their
word context, then optimize globally.
Uses the 31 confirmed key values as hard constraints.
"""
import os, random
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
            words.append((start, list(current)))
            current = []
    if current:
        words.append((start, list(current)))
    return runes, words

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1))

cipher, words = load_page(18)
N = len(cipher)

# Build position→word index mapping
pos_to_word = {}
for wi, (start, wrunes) in enumerate(words):
    for j in range(len(wrunes)):
        pos_to_word[start + j] = (wi, j)  # (word_index, position_within_word)

# 31 CONFIRMED key values (zero conflicts) from matched words
confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}

# Undetermined buckets
undetermined = sorted(set(range(KLEN)) - set(confirmed.keys()))
print(f"Confirmed: {len(confirmed)}/53, Undetermined: {len(undetermined)}")
print(f"Undetermined buckets: {undetermined}")

# Build initial key
key = [0] * KLEN
for b, v in confirmed.items():
    key[b] = v

# For undetermined positions, start with frequency-analysis best guess
eng_gp_freq = [0.022, 0.038, 0.035, 0.075, 0.060, 0.036, 0.020, 0.024,
               0.061, 0.067, 0.070, 0.002, 0.005, 0.019, 0.002, 0.063,
               0.056, 0.015, 0.127, 0.024, 0.040, 0.015, 0.003, 0.043,
               0.082, 0.003, 0.020, 0.003, 0.003]
tot = sum(eng_gp_freq)
eng_gp_freq = [f/tot for f in eng_gp_freq]

columns = [[] for _ in range(KLEN)]
for i in range(N): columns[i%KLEN].append(cipher[i])

for b in undetermined:
    col = columns[b]
    best_shift = 0
    best_score = -999
    for shift in range(29):
        dec = [(v - shift) % 29 for v in col]
        counts = Counter(dec)
        score = sum(counts.get(i,0)/len(col) * eng_gp_freq[i] for i in range(29))
        if score > best_score:
            best_score = score
            best_shift = shift
    key[b] = best_shift

# Extended word list
common_words = {'THE','AND','OF','TO','IN','IS','IT','THAT','WAS','FOR','ON','ARE','WITH',
                'AS','AT','BE','THIS','FROM','OR','AN','BY','NOT','BUT','WHAT','ALL','A','I',
                'HE','SHE','THEY','WE','YOU','HIS','HER','ITS','OUR','THEIR','WHO','WHICH',
                'HAS','HAD','HAVE','BEEN','ONE','EACH','LIKE','DO','SO','IF','NO','MY','UP',
                'ABOUT','OUT','THEM','THEN','INTO','SOME','THAN','OVER','SUCH','ALSO',
                'TIME','VERY','YOUR','MAKE','HOW','THERE','WHEN','COULD','THESE','THOSE',
                'WOULD','OTHER','MORE','AFTER','MANY','WILL','SHALL','WITHIN','DEEP','WEB',
                'KNOW','TRUTH','SELF','REALITY','BEING','MIND','LIFE','DEATH','THROUGH',
                'PATH','WAY','MUST','CAN','MAY','PART','WHOLE','BEFORE','EVERY','NEVER',
                'ALWAYS','ONCE','MOST','FIRST','LAST','NEXT','OWN','SAME','MUCH','BOTH',
                'STILL','EVEN','TOO','JUST','UNDER','UPON','SAID','SEEK','FIND','SEE',
                'WISDOM','LOOK','WORLD','ANOTHER','WHERE','BETWEEN','NEW','OLD','GREAT',
                'SMALL','LONG'}

def decrypt_word(wi, k):
    """Decrypt word wi using key k, return (latin_str, gp_values)."""
    start, wrunes = words[wi]
    dec = [(cipher[start+j] - k[(start+j)%KLEN]) % 29 for j in range(len(wrunes))]
    return ''.join(LAT[v] for v in dec), dec

def count_matched_words(k):
    """Count how many words match the common word list."""
    count = 0
    for wi, (start, wrunes) in enumerate(words):
        dec = [(cipher[start+j] - k[(start+j)%KLEN]) % 29 for j in range(len(wrunes))]
        word_str = ''.join(LAT[v] for v in dec).upper()
        if word_str in common_words:
            count += 1
    return count

def full_score(k):
    """Combined scoring: word matches + monogram frequency correlation + bigram bonus."""
    dec = [(cipher[i] - k[i%KLEN]) % 29 for i in range(N)]
    
    # Word score (weighted heavily)
    wscore = 0
    for wi, (start, wrunes) in enumerate(words):
        word_dec = dec[start:start+len(wrunes)]
        word_str = ''.join(LAT[v] for v in word_dec).upper()
        if word_str in common_words:
            wscore += 10
    
    # Monogram frequency correlation
    counts = Counter(dec)
    mono = sum(counts.get(i,0)/N * eng_gp_freq[i] for i in range(29)) * 500
    
    # Bigram bonus
    bg = 0
    common_bg = {(2,18):3,(8,18):2.5,(10,9):2,(18,4):2,(24,9):2,(4,18):2,(3,9):1.5,
                 (24,16):1.5,(18,9):1.5,(9,23):1.5,(16,10):1.5,(18,15):1.5,(3,4):1.5,
                 (16,18):1.5,(3,0):1.5,(18,23):1.5,(10,15):1.5,(10,16):1.5,(24,20):1.5,
                 (24,4):1.5,(15,16):1.5,(9,18):1.5,(2,24):1.5,(2,10):1.5}
    for i in range(N-1):
        bg += common_bg.get((dec[i], dec[i+1]), 0)
    
    # Penalty for rare digraph runes
    for v in dec:
        if v in {11, 14, 22, 25, 27, 28}: bg -= 0.2
    
    return wscore + mono + bg

# === Phase 1: Show context for each undetermined bucket ===
print("\n=== Undetermined bucket context ===")
for b in undetermined:
    positions = [b + KLEN * k for k in range(20) if b + KLEN * k < N]
    print(f"\nBucket {b}: affects positions {positions}")
    
    # For each affected position, show its word context
    for pos in positions:
        if pos in pos_to_word:
            wi, j = pos_to_word[pos]
            start, wrunes = words[wi]
            wlen = len(wrunes)
            
            # Show context: previous word, this word, next word
            word_str, word_dec = decrypt_word(wi, key)
            prev_str = decrypt_word(wi-1, key)[0] if wi > 0 else ""
            next_str = decrypt_word(wi+1, key)[0] if wi < len(words)-1 else ""
            
            # Show what this position would decrypt to for all 29 values
            best_vals = []
            for v in range(29):
                test_key = list(key)
                test_key[b] = v
                w_str, w_dec = decrypt_word(wi, test_key)
                if w_str.upper() in common_words:
                    best_vals.append((v, LAT[v], w_str))
            
            marker = f"[pos{j}]" 
            print(f"  pos {pos} in w{wi} ({wlen}r): ...{prev_str}| {word_str} |{next_str}... {marker}")
            if best_vals:
                print(f"    --> WORD MATCHES: {best_vals}")

# === Phase 2: Greedy hill-climbing on undetermined positions ===
print("\n" + "="*80)
print("Phase 2: Hill-climbing on undetermined buckets (100 random restarts)")
print("="*80)

best_global_key = list(key)
best_global_score = full_score(key)
best_global_wcount = count_matched_words(key)

for restart in range(100):
    k = list(key)  # Start from confirmed + freq-analysis
    
    # Random perturbation for restarts > 0
    if restart > 0:
        for b in undetermined:
            k[b] = random.randint(0, 28)
    
    # Hill climb
    improved = True
    while improved:
        improved = False
        for b in undetermined:
            old_val = k[b]
            best_val = old_val
            best_s = full_score(k)
            
            for v in range(29):
                if v == old_val: continue
                k[b] = v
                s = full_score(k)
                if s > best_s:
                    best_s = s
                    best_val = v
            
            k[b] = best_val
            if best_val != old_val:
                improved = True
    
    wc = count_matched_words(k)
    sc = full_score(k)
    
    if wc > best_global_wcount or (wc == best_global_wcount and sc > best_global_score):
        best_global_key = list(k)
        best_global_score = sc
        best_global_wcount = wc
        
        # Decode
        dec = [(cipher[i] - k[i%KLEN]) % 29 for i in range(N)]
        dec_words = []
        for start, wrunes in words:
            wd = [dec[start+j] for j in range(len(wrunes))]
            dec_words.append(''.join(LAT[v] for v in wd))
        
        print(f"\nRestart {restart}: words={wc}/{len(words)} score={sc:.1f}")
        print(f"  Words: {' '.join(dec_words[:35])}")
        matched = [(dec_words[i], i) for i in range(len(dec_words)) if dec_words[i].upper() in common_words]
        print(f"  Matched: {matched}")

# Final result
print("\n" + "="*80)
print("FINAL RESULT")
print("="*80)
k = best_global_key
dec = [(cipher[i] - k[i%KLEN]) % 29 for i in range(N)]
ic = ioc(dec) * 29

dec_words = []
for start, wrunes in words:
    wd = [dec[start+j] for j in range(len(wrunes))]
    dec_words.append(''.join(LAT[v] for v in wd))

wc = count_matched_words(k)
text = ''.join(LAT[v] for v in dec)

print(f"IoC*29: {ic:.3f}")
print(f"Words matched: {wc}/{len(words)}")
print(f"Key: {k}")
print(f"Key (LAT): {''.join(LAT[v] for v in k)}")
print(f"\nWords: {' '.join(dec_words)}")
print(f"\nFull text: {text}")

# Show matched and unmatched
print(f"\nMatched words:")
for i, w in enumerate(dec_words):
    if w.upper() in common_words:
        print(f"  w{i}: '{w}'")

print(f"\nUnmatched words:")
for i, w in enumerate(dec_words):
    if w.upper() not in common_words:
        start, wrunes = words[i]
        buckets = [(start+j)%KLEN for j in range(len(wrunes))]
        undet_in_word = [b for b in buckets if b in set(undetermined)]
        print(f"  w{i}: '{w}' (len={len(wrunes)}) buckets={buckets} undet={undet_in_word}")

print("\n=== DONE ===")
