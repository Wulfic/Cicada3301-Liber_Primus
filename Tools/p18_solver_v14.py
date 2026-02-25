"""
P18 Continuous Text Solver - v14
BREAKTHROUGH INSIGHT: Ciphertext dashes are visual formatting, NOT word boundaries.
Plaintext is continuous English. Optimize key for continuous text quality.

Uses bigram log-probability scoring with incremental updates for fast SA.
Builds scoring model from GP-level English statistics.
"""
import os, sys, random, math, time
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

# ===== BUILD GP BIGRAM MODEL FROM ENGLISH =====
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    """Convert English text to GP values, handling digraphs."""
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
        i += 1
    return result

# Large English corpus for GP bigram statistics
# Using solved Cicada pages + general English text
english_corpus = """
AN END A DEATH I AM REBORN HAVE YOU FOUND WHAT YOU WERE LOOKING FOR
A TERRIBLE ACT COMMANDED TO NONE BUT THE WICKED WILL THEY FIND AN END
LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE THAT WAS YOUR GOAL AND YOUR PATH
CONSUMPTION SHALL HAVE DIVIDENDED THE CIRCUMFERENCE EMERGE AND EXPAND
THE LOSS OF DIVINITY THE GREAT JUBILEE
COMMAND YOUR BODY MIND AND SPIRIT SEEK THE TRUTH WITHIN
DO NOT SHARE SECRETS WITH SOME BEING OF ALL
AN INSTRUCTION WITHIN THE DEEP WEB THAT HASHES TO
REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR
THE SHARING OF OUR EXPERIENCES AND KNOWLEDGE IS THE GREATEST FORM
BUT NOT ALL THAT IS HIDDEN IS MEANT TO BE FOUND BY EVERYONE
A COMMANDMENT AN INSTRUCTION A WARNING SOME WISDOM IS NOT FOR EVERYONE
THE INSTAR EMERGES A TERRIBLE BEAUTY A SACRED THING OR SOME MIGHT SAY
YES AND I THINK THAT THEY ARE NOT SO DIFFERENT FROM US
FROM THE ASHES OF THE TRUTH THAT SOME MAY DISCOVER FOR THEMSELVES
THAT WHICH WAS LOST TO THE AGES WILL EMERGE ONCE MORE FROM SHADOWS
IT IS THROUGH CONSUMPTION THAT WE BECOME ALL THINGS DIVINE
THE OATH IS SWORN TO THE ONE WITHIN AND WITHOUT SHADOW AND LIGHT
BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
WITHIN YOU IS THE SEED OF A GREAT BECOMING SEEK AND FIND
LEARN THE TRUTH THAT LIES WITHIN EVERY BEING EVERY SOUL
THE SPIRIT FINDS ITS OWN PATH THROUGH THE DARKNESS INTO LIGHT
CIPHER SACRED DIVINE FATHER MOTHER NATURE REASON ANSWER NUMBER ORDER
QUEST WISDOM DEATH EARTH SOUTH NORTH POWER BEING FAITH SHADOW
FOLLOW THE PATH AND SEEK THE TRUTH IN THE SHADOWS OF LIGHT
AN END IS NEVER TRULY AN END BUT THE BEGINNING OF SOMETHING NEW
PRIMES AND NUMBERS REVEAL THE ORDER WITHIN THE CHAOS OF ALL THINGS
THROUGH WISDOM AND UNDERSTANDING WE FIND OUR WAY HOME TO THE DIVINE
THE FIRE OF TRUTH BURNS AWAY ALL THAT IS FALSE AND REVEALS WHAT REMAINS
THIS IS THE TRUTH THAT LIES AT THE HEART OF ALL THINGS SACRED
NOT ALL WHO WANDER ARE LOST BUT SOME WHO SEEK WILL FIND THE PATH
THERE IS A PATTERN IN ALL THINGS A GREAT ORDER THAT GUIDES THE WAY
THE MIND IS BUT A TOOL AND THE SPIRIT THE HAND THAT WIELDS IT
FROM DEATH COMES NEW LIFE AND FROM DARKNESS COMES THE LIGHT
THOSE WHO SEEK THE TRUTH MUST FIRST LEARN TO SEE WITH NEW EYES
FAITH IS NOT BELIEF IN WHAT CANNOT BE SEEN BUT TRUST IN WHAT IS KNOWN
THE WORLD IS BUT A SHADOW OF THE TRUTH THAT LIES BEYOND THE VEIL
ALL THINGS ARE CONNECTED IN THE GREAT WEB OF LIFE AND DEATH
CONSUME THE KNOWLEDGE THAT IS OFFERED AND LET IT TRANSFORM YOUR BEING
THE WAY IS LONG AND THE PATH IS NARROW BUT THE TRUTH AWAITS
"""

corpus_gp = eng_to_gp(english_corpus)
print(f"Corpus size: {len(corpus_gp)} GP values")

# Build bigram log-probabilities
bigram_counts = [[1] * MOD for _ in range(MOD)]  # Laplace smoothing
for i in range(len(corpus_gp) - 1):
    bigram_counts[corpus_gp[i]][corpus_gp[i+1]] += 10  # Weight real data
    
# Also add unigram frequency prior
unigram = Counter(corpus_gp)
total = sum(unigram.values())

# Normalize to log probabilities
bigram_logp = [[0.0]*MOD for _ in range(MOD)]
for a in range(MOD):
    row_total = sum(bigram_counts[a])
    for b in range(MOD):
        bigram_logp[a][b] = math.log(bigram_counts[a][b] / row_total)

# Unigram log-prob
unigram_logp = [0.0]*MOD
for v in range(MOD):
    unigram_logp[v] = math.log((unigram.get(v, 0) + 1) / (total + MOD))

# ===== LOAD CIPHER TEXT =====
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"P18: {N} runes, key length {KLEN}")
print(f"Positions per bucket: ~{N/KLEN:.1f}")

# ===== SCORING FUNCTION =====
def full_score(key):
    """Compute full bigram log-likelihood of decrypted text."""
    dec = [(cipher[i] - key[i % KLEN]) % MOD for i in range(N)]
    s = 0.0
    for i in range(N-1):
        s += bigram_logp[dec[i]][dec[i+1]]
    return s, dec

def delta_score(key, dec, bucket, old_val, new_val):
    """Compute score change when changing key[bucket] from old_val to new_val.
    Only positions where i%KLEN == bucket are affected."""
    delta = 0.0
    positions = [i for i in range(bucket, N, KLEN)]
    for pos in positions:
        old_dec = (cipher[pos] - old_val) % MOD
        new_dec = (cipher[pos] - new_val) % MOD
        # Remove old bigrams, add new ones
        if pos > 0:
            left = dec[pos-1]
            delta -= bigram_logp[left][old_dec]
            delta += bigram_logp[left][new_dec]
        if pos < N-1:
            right = dec[pos+1]
            delta -= bigram_logp[old_dec][right]
            delta += bigram_logp[new_dec][right]
    return delta

# Build position lookup
bucket_positions = [[] for _ in range(KLEN)]
for i in range(N):
    bucket_positions[i % KLEN].append(i)

# ===== CONFIRMED KEY VALUES =====
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

# ===== PHASE 1: Column-by-column with bigram scoring =====
print(f"\n{'='*80}")
print(f"PHASE 1: Column-by-column optimization (all 53 positions)")
print(f"{'='*80}")

# For each column, try all 29 values and pick the best
key_colwise = [0] * KLEN
for b in range(KLEN):
    best_val = 0
    best_s = -float('inf')
    for v in range(MOD):
        # Temporarily set this column to v  
        key_colwise[b] = v
        # Score just the unigram frequencies of this column
        s = sum(unigram_logp[(cipher[i] - v) % MOD] for i in bucket_positions[b])
        if s > best_s:
            best_s = s
            best_val = v
    key_colwise[b] = best_val

score_cw, dec_cw = full_score(key_colwise)
text_cw = ''.join(LAT[v] for v in dec_cw)
n_agree = sum(1 for b, v in confirmed.items() if key_colwise[b] == v)
print(f"Column-wise unigram key:")
print(f"  Score: {score_cw:.2f}")
print(f"  Agrees with confirmed: {n_agree}/{len(confirmed)}")
print(f"  Text[:200]: {text_cw[:200]}")

# ===== PHASE 2: SA with confirmed values fixed =====
print(f"\n{'='*80}")
print(f"PHASE 2: SA with confirmed values FIXED ({len(undetermined)} free positions)")
print(f"{'='*80}")

best_constrained_score = -float('inf')
best_constrained_key = None
best_constrained_text = None

N_RESTARTS = 200
t0 = time.time()
for restart in range(N_RESTARTS):
    # Init: confirmed + random for undetermined
    key = [confirmed.get(b, random.randint(0, MOD-1)) for b in range(KLEN)]
    score, dec = full_score(key)
    best_s = score
    best_k = list(key)
    
    T = 5.0
    alpha = 0.9995
    steps = 0
    
    while T > 0.01:
        b = random.choice(undetermined)
        old_val = key[b]
        new_val = random.randint(0, MOD-2)
        if new_val >= old_val:
            new_val += 1
        
        d = delta_score(key, dec, b, old_val, new_val)
        
        if d > 0 or random.random() < math.exp(d / T):
            # Apply
            key[b] = new_val
            score += d
            for pos in bucket_positions[b]:
                dec[pos] = (cipher[pos] - new_val) % MOD
            if score > best_s:
                best_s = score
                best_k = list(key)
        else:
            pass  # Reject
        
        T *= alpha
        steps += 1
    
    if best_s > best_constrained_score:
        best_constrained_score = best_s
        best_constrained_key = list(best_k)
        s2, d2 = full_score(best_k)
        best_constrained_text = ''.join(LAT[v] for v in d2)
    
    if (restart+1) % 50 == 0:
        elapsed = time.time() - t0
        print(f"  Restart {restart+1}/{N_RESTARTS}: best score={best_constrained_score:.2f} ({elapsed:.1f}s)")

score_c, dec_c = full_score(best_constrained_key)
text_c = ''.join(LAT[v] for v in dec_c)
print(f"\nBest constrained key (confirmed fixed):")
print(f"  Score: {score_c:.2f}")
print(f"  Key: {best_constrained_key}")
print(f"  Key (LAT): {''.join(LAT[v] for v in best_constrained_key)}")
print(f"  Text[:300]:")
for i in range(0, min(300, len(text_c)), 60):
    print(f"    [{i:3d}] {text_c[i:i+60]}")
print(f"  Full text:")
for i in range(0, len(text_c), 60):
    print(f"    [{i:3d}] {text_c[i:i+60]}")

# ===== PHASE 3: SA with ALL positions free =====
print(f"\n{'='*80}")
print(f"PHASE 3: SA with ALL 53 positions FREE")
print(f"{'='*80}")

best_free_score = -float('inf')
best_free_key = None

for restart in range(N_RESTARTS):
    key = [random.randint(0, MOD-1) for _ in range(KLEN)]
    score, dec = full_score(key)
    best_s = score
    best_k = list(key)
    
    T = 8.0
    alpha = 0.9993
    
    while T > 0.01:
        b = random.randint(0, KLEN-1)
        old_val = key[b]
        new_val = random.randint(0, MOD-2)
        if new_val >= old_val:
            new_val += 1
        
        d = delta_score(key, dec, b, old_val, new_val)
        
        if d > 0 or random.random() < math.exp(d / T):
            key[b] = new_val
            score += d
            for pos in bucket_positions[b]:
                dec[pos] = (cipher[pos] - new_val) % MOD
            if score > best_s:
                best_s = score
                best_k = list(key)
        else:
            pass
        
        T *= alpha
    
    if best_s > best_free_score:
        best_free_score = best_s
        best_free_key = list(best_k)
    
    if (restart+1) % 50 == 0:
        elapsed = time.time() - t0
        print(f"  Restart {restart+1}/{N_RESTARTS}: best score={best_free_score:.2f} ({elapsed:.1f}s)")

score_f, dec_f = full_score(best_free_key)
text_f = ''.join(LAT[v] for v in dec_f)
n_agree = sum(1 for b, v in confirmed.items() if best_free_key[b] == v)
print(f"\nBest free key (all positions free):")
print(f"  Score: {score_f:.2f}")
print(f"  Agrees with confirmed: {n_agree}/{len(confirmed)}")
print(f"  Key: {best_free_key}")
print(f"  Key (LAT): {''.join(LAT[v] for v in best_free_key)}")
print(f"  Text[:300]:")
for i in range(0, min(300, len(text_f)), 60):
    print(f"    [{i:3d}] {text_f[i:i+60]}")
print(f"  Full text:")
for i in range(0, len(text_f), 60):
    print(f"    [{i:3d}] {text_f[i:i+60]}")

# ===== PHASE 4: Compare modes =====
print(f"\n{'='*80}")
print(f"PHASE 4: Compare ADD and BEAUFORT modes")
print(f"{'='*80}")

for mode_name, mode_fn in [('ADD', lambda c,k: (c+k)%MOD), ('BEAUFORT', lambda c,k: (k-c)%MOD)]:
    # Rebuild bigram scoring for this mode
    def make_score_fn(fn):
        def full_score_mode(key):
            dec = [fn(cipher[i], key[i%KLEN]) for i in range(N)]
            s = sum(bigram_logp[dec[i]][dec[i+1]] for i in range(N-1))
            return s, dec
        return full_score_mode
    
    fsm = make_score_fn(mode_fn)
    
    best_mode_score = -float('inf')
    best_mode_key = None
    
    for restart in range(100):
        key = [random.randint(0, MOD-1) for _ in range(KLEN)]
        score, dec = fsm(key)
        best_s = score
        best_k = list(key)
        
        T = 8.0
        alpha = 0.999
        while T > 0.05:
            b = random.randint(0, KLEN-1)
            old_val = key[b]
            new_val = random.randint(0, MOD-2)
            if new_val >= old_val:
                new_val += 1
            key[b] = new_val
            new_score, new_dec = fsm(key)
            d = new_score - score
            if d > 0 or random.random() < math.exp(d/T):
                score = new_score
                dec = new_dec
                if score > best_s:
                    best_s = score
                    best_k = list(key)
            else:
                key[b] = old_val
            T *= alpha
        
        if best_s > best_mode_score:
            best_mode_score = best_s
            best_mode_key = list(best_k)
    
    _, dec_m = fsm(best_mode_key)
    text_m = ''.join(LAT[v] for v in dec_m)
    print(f"\n{mode_name}: score={best_mode_score:.2f}")
    print(f"  Text[:200]: {text_m[:200]}")

print(f"\n{'='*80}")
print("=== DONE ===")
print(f"Total time: {time.time()-t0:.1f}s")
