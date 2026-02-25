"""
P18 Solver v15 - POWERED BY SOLVED LP PLAINTEXT
Uses GP bigram model trained on ~5000 chars of actual Cicada plaintext.
Key insight: Ciphertext dashes are formatting, plaintext is continuous stream.

Strategy: Bigram SA with incremental scoring, large training corpus.
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
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# ===== GP ENCODING =====
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []
    i = 0
    text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            result.append(DIGRAPHS[text[i:i+2]])
            i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
            i += 1
        else:
            i += 1
    return result

# ===== MASSIVE TRAINING CORPUS =====
# All solved Cicada plaintext + extra English text
corpus_text = """
LIBER PRIMUS
A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH
DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN
EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED
CHAPTER INTUS
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING
YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES
JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE
LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE
WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY
AN INSTRUCTION COMMAND YOUR OWN SELF
SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED
A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER
HE WENT TO THE DOOR OF THE MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER
THE STUDENT TOLD THE MASTER HIS NAME
THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED
WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN
THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR
THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE
CONFUSED THE MAN THOUGHT SOME MORE
FINALLY HE ANSWERED I AM A HUMAN BEING
THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN
AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED
I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY
THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE
WHO ARE YOU WHO WISHES TO STUDY HERE
THE MAN WAS GETTING IRRITATED I AM HE STARTED
BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF
AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY
AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY
THE LOSS OF DIVINITY
THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY
CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS
WITHIN THE DECEPTION
WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH
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
SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN
BE PREPARED TO DESTROY ALL THAT YOU OWN
AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY
A KOAN DURING A LESSON THE MASTER EXPLAINED THE I
THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID
IT IS A VOICE INSIDE YOUR HEAD
I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT
AND HE RAISED HIS HAND TO TELL THE MASTER
THE MASTER STOPPED THE STUDENT AND SAID
THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I
AND THE STUDENTS WERE ENLIGHTENED
AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF
FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE
WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE
REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR
BEING OF ALL WILL THE OATH IS SWORN TO THE ONE WITHIN
THE SPIRIT FINDS ITS OWN PATH THROUGH THE DARKNESS INTO LIGHT
FROM THE ASHES OF TRUTH WE DISCOVER OUR SACRED NATURE
SEEK AND FIND THE DIVINE WITHIN EVERY BEING EVERY SOUL
THE FIRE OF TRUTH BURNS AWAY ALL THAT IS FALSE REVEALS WHAT REMAINS
COMMAND YOUR BODY MIND AND SPIRIT SACRED DIVINE FATHER MOTHER NATURE
A TERRIBLE ACT COMMANDED NONE BUT WICKED WILL THEY FIND AN END
CONSUMPTION SHALL HAVE DIVIDENDED THE CIRCUMFERENCE EMERGE AND EXPAND
DO NOT SHARE SECRETS WITH SOME BEING OF ALL PRIMES AND NUMBERS
REVEAL THE ORDER WITHIN THE CHAOS THROUGH WISDOM AND UNDERSTANDING
WE FIND OUR WAY HOME TO THE DIVINE SHADOW INSTAR TUNNEL SURFACE
SHED DIVINITY WITHIN EMERGE CIRCUMFERENCE FAITH DEATH EARTH
NORTH SOUTH POWER QUEST ORDER NUMBER ANSWER REASON LEARN LIGHT
AN END IS NEVER TRULY AN END BUT THE BEGINNING OF SOMETHING NEW
THOSE WHO SEEK THE TRUTH MUST FIRST LEARN TO SEE WITH NEW EYES
THE WORLD IS BUT A SHADOW OF THE TRUTH THAT LIES BEYOND THE VEIL
ALL THINGS ARE CONNECTED IN THE GREAT WEB OF LIFE AND DEATH
CONSUME THE KNOWLEDGE THAT IS OFFERED AND LET IT TRANSFORM YOUR BEING
THE WAY IS LONG AND THE PATH IS NARROW BUT THE TRUTH AWAITS
NOT ALL WHO WANDER ARE LOST BUT SOME WHO SEEK WILL FIND THE PATH
THERE IS A PATTERN IN ALL THINGS A GREAT ORDER THAT GUIDES THE WAY
THE MIND IS BUT A TOOL AND THE SPIRIT THE HAND THAT WIELDS IT
FROM DEATH COMES NEW LIFE AND FROM DARKNESS COMES THE LIGHT
FAITH IS NOT BELIEF IN WHAT CANNOT BE SEEN BUT TRUST IN WHAT IS KNOWN
"""

corpus_gp = eng_to_gp(corpus_text)
print(f"Training corpus: {len(corpus_gp)} GP values")

# Build bigram model with Laplace smoothing
ALPHA = 0.1  # Small smoothing
bigram_raw = [[ALPHA]*MOD for _ in range(MOD)]
for i in range(len(corpus_gp)-1):
    bigram_raw[corpus_gp[i]][corpus_gp[i+1]] += 1

# Log probabilities
bigram_logp = [[0.0]*MOD for _ in range(MOD)]
for a in range(MOD):
    total = sum(bigram_raw[a])
    for b in range(MOD):
        bigram_logp[a][b] = math.log(bigram_raw[a][b] / total)

# Also build unigram model
uni_raw = [ALPHA]*MOD
for v in corpus_gp:
    uni_raw[v] += 1
uni_total = sum(uni_raw)
uni_logp = [math.log(c/uni_total) for c in uni_raw]

# Show top bigrams
print("Top GP bigrams:")
pairs = []
for a in range(MOD):
    for b in range(MOD):
        if bigram_raw[a][b] > 2:
            pairs.append((bigram_raw[a][b], a, b))
pairs.sort(reverse=True)
for cnt, a, b in pairs[:20]:
    print(f"  {LAT[a]}-{LAT[b]}: {cnt:.0f}")

# ===== LOAD CIPHER =====
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"\nP18: {N} runes, KLEN={KLEN}")

bucket_positions = [[] for _ in range(KLEN)]
for i in range(N):
    bucket_positions[i%KLEN].append(i)

# ===== SCORING =====
def full_score(dec):
    return sum(bigram_logp[dec[i]][dec[i+1]] for i in range(N-1))

def decrypt(key):
    return [(cipher[i] - key[i%KLEN]) % MOD for i in range(N)]

def apply_and_score_delta(dec, key, b, new_val):
    """Change key[b] to new_val, update dec in place, return score delta."""
    old_val = key[b]
    delta = 0.0
    positions = bucket_positions[b]
    # Compute delta BEFORE modifying dec
    for pos in positions:
        old_d = dec[pos]
        new_d = (cipher[pos] - new_val) % MOD
        if pos > 0:
            left = dec[pos-1]
            delta -= bigram_logp[left][old_d]
            delta += bigram_logp[left][new_d]
        if pos < N-1:
            right = dec[pos+1]
            delta -= bigram_logp[old_d][right]
            delta += bigram_logp[new_d][right]
    return delta

def apply_change(dec, key, b, new_val):
    """Actually apply the change."""
    for pos in bucket_positions[b]:
        dec[pos] = (cipher[pos] - new_val) % MOD
    key[b] = new_val

# ===== CONFIRMED VALUES =====
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

# ===== SA FUNCTION =====
def sa_solve(free_positions, n_restarts=500, init_key=None, T0=5.0, alpha=0.9997, T_min=0.005):
    """SA with incremental scoring. Returns best key and score."""
    best_ever_score = -float('inf')
    best_ever_key = None
    
    for r in range(n_restarts):
        # Initialize
        if init_key:
            key = list(init_key)
        else:
            key = [0]*KLEN
        for b in range(KLEN):
            if b in confirmed:
                key[b] = confirmed[b]
            elif b in free_positions:
                key[b] = random.randint(0, MOD-1)
        
        dec = decrypt(key)
        score = full_score(dec)
        best_score = score
        best_key = list(key)
        
        T = T0
        steps = 0
        while T > T_min:
            b = random.choice(free_positions)
            old_val = key[b]
            new_val = random.randint(0, MOD-2)
            if new_val >= old_val:
                new_val += 1
            
            delta = apply_and_score_delta(dec, key, b, new_val)
            
            if delta > 0 or random.random() < math.exp(delta / T):
                apply_change(dec, key, b, new_val)
                score += delta
                if score > best_score:
                    best_score = score
                    best_key = list(key)
            
            T *= alpha
            steps += 1
        
        if best_score > best_ever_score:
            best_ever_score = best_score
            best_ever_key = list(best_key)
        
        if (r+1) % 100 == 0:
            dec_best = decrypt(best_ever_key)
            text = ''.join(LAT[v] for v in dec_best[:100])
            print(f"  [{r+1}/{n_restarts}] score={best_ever_score:.2f} text[:100]={text}")
    
    return best_ever_key, best_ever_score

# ===== PHASE 1: Constrained (confirmed fixed) =====
print(f"\n{'='*80}")
print(f"PHASE 1: SA with confirmed FIXED, {len(undetermined)} free")
print(f"{'='*80}")
t0 = time.time()
key1, score1 = sa_solve(undetermined, n_restarts=500)
dec1 = decrypt(key1)
text1 = ''.join(LAT[v] for v in dec1)
print(f"\nBest constrained: score={score1:.2f}")
print(f"Key: {key1}")
print(f"Undetermined values:")
for b in undetermined:
    print(f"  key[{b:2d}] = {key1[b]:2d} ({LAT[key1[b]]})")
print(f"Text:")
for i in range(0, len(text1), 70):
    print(f"  [{i:3d}] {text1[i:i+70]}")

# ===== PHASE 2: Fully free =====
print(f"\n{'='*80}")
print(f"PHASE 2: SA with ALL 53 positions free")
print(f"{'='*80}")
all_positions = list(range(KLEN))
key2, score2 = sa_solve(all_positions, n_restarts=500, T0=8.0, alpha=0.9995)
dec2 = decrypt(key2)
text2 = ''.join(LAT[v] for v in dec2)
n_agree = sum(1 for b,v in confirmed.items() if key2[b]==v)
print(f"\nBest free: score={score2:.2f}")
print(f"Agrees with confirmed: {n_agree}/{len(confirmed)}")
print(f"Key: {key2}")
print(f"Text:")
for i in range(0, len(text2), 70):
    print(f"  [{i:3d}] {text2[i:i+70]}")

# ===== PHASE 3: Try ADD and BEAU modes =====
print(f"\n{'='*80}")
print(f"PHASE 3: ADD and BEAUFORT modes (free)")
print(f"{'='*80}")

for mode, mode_fn in [('ADD', lambda c,k: (c+k)%MOD), ('BEAU', lambda c,k: (k-c)%MOD)]:
    best_s = -float('inf')
    best_k = None
    for r in range(200):
        key = [random.randint(0,MOD-1) for _ in range(KLEN)]
        dec = [mode_fn(cipher[i], key[i%KLEN]) for i in range(N)]
        score = full_score(dec)
        
        T = 8.0
        while T > 0.01:
            b = random.randint(0, KLEN-1)
            old_v = key[b]
            new_v = random.randint(0, MOD-2)
            if new_v >= old_v: new_v += 1
            
            # Full recompute for simplicity (modes differ)
            key[b] = new_v
            new_dec = [mode_fn(cipher[i], key[i%KLEN]) for i in range(N)]
            new_score = full_score(new_dec)
            d = new_score - score
            if d > 0 or random.random() < math.exp(d/T):
                score = new_score
                dec = new_dec
                if score > best_s:
                    best_s = score
                    best_k = list(key)
            else:
                key[b] = old_v
            T *= 0.999
    
    if best_k:
        dec_m = [mode_fn(cipher[i], best_k[i%KLEN]) for i in range(N)]
        text_m = ''.join(LAT[v] for v in dec_m)
        print(f"{mode}: score={best_s:.2f}")
        print(f"  Text[:200]: {text_m[:200]}")

# ===== PHASE 4: SOLUTION.md key (one-time pad for 53 runes) =====
print(f"\n{'='*80}")
print(f"PHASE 4: SOLUTION.md one-time key (first 53 runes)")
print(f"{'='*80}")
sol_key_53 = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16, 9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24, 22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]
dec_sol = [(cipher[i] - sol_key_53[i]) % MOD for i in range(53)]
text_sol = ''.join(LAT[v] for v in dec_sol)
print(f"First 53 runes: {text_sol}")
score_sol = sum(bigram_logp[dec_sol[i]][dec_sol[i+1]] for i in range(52))
print(f"Bigram score (53 runes): {score_sol:.2f}")

# Compare with phase 1 key for first 53 runes
dec1_53 = dec1[:53]
text1_53 = ''.join(LAT[v] for v in dec1_53)
score1_53 = sum(bigram_logp[dec1_53[i]][dec1_53[i+1]] for i in range(52))
print(f"Phase 1 first 53: {text1_53}")
print(f"Phase 1 score (53): {score1_53:.2f}")

# Compare with phase 2 key for first 53 runes
dec2_53 = dec2[:53]
text2_53 = ''.join(LAT[v] for v in dec2_53)
score2_53 = sum(bigram_logp[dec2_53[i]][dec2_53[i+1]] for i in range(52))
print(f"Phase 2 first 53: {text2_53}")
print(f"Phase 2 score (53): {score2_53:.2f}")

elapsed = time.time() - t0
print(f"\nTotal time: {elapsed:.1f}s")
print("=== DONE ===")
