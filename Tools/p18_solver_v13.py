"""
P18/P19 - Continuous text analysis
KEY INSIGHT: Dashes may be LINE BREAKS not word separators for some pages.
P19 proves this: "REARRANGING" is split across dash-separated chunks.

Strategy: 
1. Decrypt as continuous stream (ignoring dashes)
2. Score using n-gram analysis and word detection
3. Hill-climb on undetermined key positions

For P18: 34 confirmed values, 19 unknown. Optimize the 19 for best continuous English.
For P19: kl=43 first period works. Check continuous text quality.
"""
import os, sys, random, math
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53
random.seed(42)

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    return [GP[c] for c in raw if c in GP]

cipher = load_page(18)
N = len(cipher)
print(f"P18: {N} runes")

# Build n-gram scoring tables
# Common English bigrams in GP encoding
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def text_to_gp(text):
    result = []
    i = 0
    text = text.upper()
    while i < len(text):
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in DIGRAPHS:
                result.append(DIGRAPHS[di])
                i += 2
                continue
        if text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
        elif text[i] == ' ':
            result.append(-1)  # Space marker
            i += 1
            continue
        else:
            i += 1
            continue
        i += 1
    return result

# Build rune bigram frequencies from English text
# Use a sample of Cicada-like text
sample_text = """
THE LOSS OF DIVINITY A COMMANDMENT AN INSTRUCTION A WARNING 
WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO 
AN END BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
SOME WISDOM IS NOT MEANT FOR EVERYONE THE INSTAR EMERGES 
REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR
CONSUMPTION SHALL HAVE DIVIDENDED THE CIRCUMFERENCE EMERGE AND EXPAND
DO NOT SHARE WISDOM WITH THOSE WHO HAVE NOT PROVEN THEIR WORTH
FIND THE TRUTH IN THE SHADOWS AND THE LIGHT SHALL FOLLOW
THE BEING OF ALL I WILL ASK THE OATH IS SWORN TO THE ONE
COMMAND YOUR BODY AND YOUR MIND SACRED DIVINE SPIRIT PRIMES CIPHER
FATHER MOTHER NATURE REASON ANSWER BECOME NUMBER QUEST ORDER
WISDOM LEARN TRUTH LIGHT FAITH DEATH EARTH SOUTH NORTH
"""

# Build bigram counts from sample
bigram_counts = Counter()
sample_gp = [v for v in text_to_gp(sample_text) if v >= 0]
for i in range(len(sample_gp) - 1):
    bigram_counts[(sample_gp[i], sample_gp[i+1])] += 1

# Also build from English letter frequencies
ENG_FREQ = [0.022, 0.038, 0.035, 0.075, 0.060, 0.036, 0.020, 0.024,
            0.061, 0.067, 0.070, 0.002, 0.005, 0.019, 0.002, 0.063,
            0.056, 0.015, 0.127, 0.024, 0.040, 0.015, 0.003, 0.043,
            0.082, 0.003, 0.020, 0.003, 0.003]

# Common English words to detect in continuous text
COMMON_WORDS = []
for w in "THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT HAD HAS HIS HOW ITS LET MAY NEW NOW OLD SEE WAY WHO THAT WITH HAVE THIS WILL YOUR FROM THEY BEEN EACH FIND SOME THEM THEN WHAT WHEN WILL WITH WORD ABOUT AFTER BEING COULD EVERY FIRST GREAT HOUSE LIGHT MIGHT NEVER OTHER RIGHT SHALL SMALL STILL THEIR THERE THESE THINK THREE WHERE WHICH WORLD WOULD YOUNG BEFORE SHOULD THROUGH WITHIN SPIRIT TRUTH EARTH DEATH FAITH LEARN LIAR WISDOM SACRED DIVINE PRIMES CIPHER NORTH SOUTH FATHER MOTHER NATURE REASON".split():
    gp = text_to_gp(w)
    if gp:
        COMMON_WORDS.append((w, tuple(gp)))

# Score: count English words found in continuous decoded stream
def find_words_in_stream(dec_values):
    """Find English words in continuous decoded values. Returns count."""
    n_found = 0
    found_words = []
    for word, gp_vals in COMMON_WORDS:
        wlen = len(gp_vals)
        for i in range(len(dec_values) - wlen + 1):
            if tuple(dec_values[i:i+wlen]) == gp_vals:
                n_found += 1
                found_words.append((i, word))
                break  # Count each word only once
    return n_found, found_words

def continuous_score(key):
    """Score key based on continuous text quality."""
    dec = [(cipher[i] - key[i % KLEN]) % MOD for i in range(N)]
    
    # 1. Letter frequency correlation
    counts = Counter(dec)
    freq_score = sum(ENG_FREQ[v] * counts.get(v, 0) / N for v in range(MOD))
    
    # 2. Bigram score
    bi_score = 0
    for i in range(N - 1):
        bi = (dec[i], dec[i+1])
        if bi in bigram_counts:
            bi_score += 1
    bi_score /= (N - 1)
    
    # 3. Word detection
    n_words, found = find_words_in_stream(dec)
    
    # Combined score (heavily weight word detection)
    total = n_words * 100 + freq_score * 200 + bi_score * 50
    return total, n_words, found, dec

# Confirmed key values from word matching
confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}
undetermined = [b for b in range(KLEN) if b not in confirmed]
print(f"Confirmed: {len(confirmed)}, Undetermined: {len(undetermined)}")
print(f"Undetermined positions: {undetermined}")

# Check baseline score with confirmed values + zeros for undetermined
key_base = [0] * KLEN
for b, v in confirmed.items():
    key_base[b] = v
score0, nw0, found0, dec0 = continuous_score(key_base)
text0 = ''.join(LAT[v] for v in dec0)
print(f"\nBaseline (undetermined=0): {nw0} words found, score={score0:.2f}")
print(f"Text: {text0[:300]}")
print(f"Found words: {found0}")

# Hill-climbing on undetermined positions, optimizing continuous text quality
print(f"\n{'='*80}")
print(f"Hill-climbing on {len(undetermined)} undetermined positions")
print(f"{'='*80}")

best_overall_key = None
best_overall_score = -1
best_overall_words = 0

N_RESTARTS = 500
for restart in range(N_RESTARTS):
    key = list(key_base)
    # Random init for undetermined
    for b in undetermined:
        key[b] = random.randint(0, MOD-1)
    
    score, nw, found, _ = continuous_score(key)
    best_key = list(key)
    best_score = score
    best_nw = nw
    
    # Simulated annealing
    T = 10.0
    T_min = 0.1
    alpha = 0.997
    
    while T > T_min:
        # Mutate one undetermined position
        b = random.choice(undetermined)
        old_val = key[b]
        key[b] = random.randint(0, MOD-1)
        
        new_score, new_nw, new_found, _ = continuous_score(key)
        
        delta = new_score - score
        if delta > 0 or random.random() < math.exp(delta / T):
            score = new_score
            nw = new_nw
            if score > best_score:
                best_score = score
                best_key = list(key)
                best_nw = nw
        else:
            key[b] = old_val
        
        T *= alpha
    
    if best_nw > best_overall_words or (best_nw == best_overall_words and best_score > best_overall_score):
        best_overall_words = best_nw
        best_overall_score = best_score
        best_overall_key = list(best_key)
    
    if (restart + 1) % 100 == 0:
        print(f"  Restart {restart+1}/{N_RESTARTS}: best = {best_overall_words} words (score={best_overall_score:.2f})")

# Show best result
print(f"\n{'='*80}")
print(f"BEST RESULT: {best_overall_words} continuous English words")
print(f"{'='*80}")

score_final, nw_final, found_final, dec_final = continuous_score(best_overall_key)
text_final = ''.join(LAT[v] for v in dec_final)

print(f"Key: {best_overall_key}")
print(f"Key (LAT): {''.join(LAT[v] for v in best_overall_key)}")
print(f"\nFound words: {sorted(found_final, key=lambda x: x[0])}")
print(f"\nFull text:")

# Print with word highlighting
for i in range(0, len(text_final), 60):
    chunk = text_final[i:i+60]
    print(f"  [{i:3d}] {chunk}")

# Show undetermined values 
print(f"\nUndetermined values:")
for b in undetermined:
    print(f"  key[{b}] = {best_overall_key[b]} ({LAT[best_overall_key[b]]})")

# Compare with confirmed values
print(f"\nConfirmed values unchanged: {all(best_overall_key[b] == v for b, v in confirmed.items())}")

# Also try: score where we allow CHANGING confirmed values
print(f"\n{'='*80}")
print(f"FULL hill-climbing (ALL 53 positions free)")  
print(f"{'='*80}")

best_full_key = None
best_full_score = -1
best_full_words = 0

for restart in range(300):
    key = [random.randint(0, MOD-1) for _ in range(KLEN)]
    
    score, nw, found, _ = continuous_score(key)
    best_key = list(key)
    best_score = score
    best_nw = nw
    
    T = 15.0
    alpha = 0.996
    
    while T > 0.1:
        b = random.randint(0, KLEN-1)
        old_val = key[b]
        key[b] = random.randint(0, MOD-1)
        
        new_score, new_nw, new_found, _ = continuous_score(key)
        
        delta = new_score - score
        if delta > 0 or random.random() < math.exp(delta / T):
            score = new_score
            nw = new_nw
            if score > best_score:
                best_score = score
                best_key = list(key)
                best_nw = nw
        else:
            key[b] = old_val
        
        T *= alpha
    
    if best_nw > best_full_words or (best_nw == best_full_words and best_score > best_full_score):
        best_full_words = best_nw
        best_full_score = best_score
        best_full_key = list(best_key)
    
    if (restart + 1) % 100 == 0:
        print(f"  Restart {restart+1}/300: best = {best_full_words} words (score={best_full_score:.2f})")

score_full, nw_full, found_full, dec_full = continuous_score(best_full_key)
text_full = ''.join(LAT[v] for v in dec_full)
print(f"\nBEST FULL: {nw_full} words")
print(f"Key (LAT): {''.join(LAT[v] for v in best_full_key)}")
print(f"Found words: {sorted(found_full, key=lambda x: x[0])}")
print(f"\nText:")
for i in range(0, len(text_full), 60):
    print(f"  [{i:3d}] {text_full[i:i+60]}")

# Compare with confirmed
n_agree = sum(1 for b, v in confirmed.items() if best_full_key[b] == v)
print(f"Agrees with confirmed: {n_agree}/{len(confirmed)}")

print(f"\n=== DONE ===")
