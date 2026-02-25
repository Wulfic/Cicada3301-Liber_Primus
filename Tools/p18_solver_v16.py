"""
P18 Solver v16 - QUADGRAM SCORING
Quadgrams are far more discriminative than bigrams for small alphabets.
The English quadgram space is sparse — random text will have many unseen quadgrams
while real English will use common ones.

Training: All solved LP plaintext (~4000+ GP values).
Method: SA with incremental quadgram scoring.
"""
import os, sys, random, math, time
from collections import Counter, defaultdict

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

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
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

# ===== BUILD QUADGRAM MODEL =====
# All solved LP plaintext  
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
BEING OF ALL WILL THE OATH IS SWORN TO THE ONE WITHIN THE ABOVE THE WAY
COMMAND YOUR BODY MIND AND SPIRIT SEEK THE TRUTH WITHIN
FROM THE ASHES OF TRUTH WE DISCOVER OUR SACRED NATURE
SEEK AND FIND THE DIVINE WITHIN EVERY BEING EVERY SOUL
THE SPIRIT FINDS ITS OWN PATH THROUGH THE DARKNESS INTO LIGHT
LEARN THE TRUTH THAT LIES WITHIN EVERY BEING
AN END IS NEVER TRULY AN END BUT THE BEGINNING OF SOMETHING NEW
PRIMES AND NUMBERS REVEAL THE ORDER WITHIN THE CHAOS OF ALL THINGS
THROUGH WISDOM AND UNDERSTANDING WE FIND OUR WAY HOME
THE FIRE OF TRUTH BURNS AWAY ALL THAT IS FALSE AND REVEALS WHAT REMAINS
THIS IS THE TRUTH THAT LIES AT THE HEART OF ALL THINGS SACRED
NOT ALL WHO WANDER ARE LOST BUT SOME WHO SEEK WILL FIND THE PATH
THERE IS A PATTERN IN ALL THINGS A GREAT ORDER THAT GUIDES THE WAY
THE MIND IS BUT A TOOL AND THE SPIRIT THE HAND THAT WIELDS IT
FROM DEATH COMES NEW LIFE AND FROM DARKNESS COMES THE LIGHT
FAITH IS NOT BELIEF IN WHAT CANNOT BE SEEN BUT TRUST IN WHAT IS KNOWN
THE WORLD IS BUT A SHADOW OF THE TRUTH THAT LIES BEYOND THE VEIL
"""

corpus_gp = eng_to_gp(corpus_text)
print(f"Corpus: {len(corpus_gp)} GP values")

# Build quadgram frequency table
qg_counts = defaultdict(int)
for i in range(len(corpus_gp)-3):
    key = (corpus_gp[i], corpus_gp[i+1], corpus_gp[i+2], corpus_gp[i+3])
    qg_counts[key] += 1

total_qg = len(corpus_gp) - 3
n_distinct = len(qg_counts)
print(f"Distinct quadgrams: {n_distinct} (of {MOD**4} = {MOD**4} possible)")
print(f"Total quadgram instances: {total_qg}")

# Log10 probability with floor for unseen
FLOOR = math.log10(0.01 / total_qg)  # Very low prob for unseen quadgrams
qg_logp = {}
for qg, cnt in qg_counts.items():
    qg_logp[qg] = math.log10(cnt / total_qg)

def qg_score_full(dec):
    """Full quadgram score of decoded text."""
    s = 0.0
    for i in range(len(dec)-3):
        qg = (dec[i], dec[i+1], dec[i+2], dec[i+3])
        s += qg_logp.get(qg, FLOOR)
    return s

# Incremental update: changing key[b] affects positions in bucket b.
# Each position p participates in quadgrams starting at p-3, p-2, p-1, p.
# So changing position p affects quadgrams [p-3..p, p-2..p+1, p-1..p+2, p..p+3].
# For each changed position, we need to update up to 4 quadgrams.

def qg_delta(dec, bucket_pos, old_vals, new_vals, N):
    """Compute score change when changing decoded values at bucket positions."""
    delta = 0.0
    # Collect all affected quadgram start positions
    affected = set()
    for pos in bucket_pos:
        for start in range(max(0, pos-3), min(N-3, pos+1)):
            affected.add(start)
    
    for start in affected:
        old_qg = (dec[start], dec[start+1], dec[start+2], dec[start+3])
        # Figure out new quadgram
        new_qg = list(old_qg)
        for idx, pos in enumerate(bucket_pos):
            offset = pos - start
            if 0 <= offset < 4:
                new_qg[offset] = new_vals[idx]
        new_qg = tuple(new_qg)
        
        delta -= qg_logp.get(old_qg, FLOOR)
        delta += qg_logp.get(new_qg, FLOOR)
    
    return delta

# ===== LOAD CIPHER =====
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"P18: {N} runes")

bucket_positions = [[] for _ in range(KLEN)]
for i in range(N):
    bucket_positions[i%KLEN].append(i)

def decrypt(key):
    return [(cipher[i]-key[i%KLEN])%MOD for i in range(N)]

# ===== CONFIRMED KEY =====
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

# ===== SA WITH INCREMENTAL QUADGRAM SCORING =====
def sa_quadgram(free_pos, n_restarts=500, T0=2.0, alpha=0.99985, T_min=0.001):
    best_score = -float('inf')
    best_key = None
    t0 = time.time()
    
    for r in range(n_restarts):
        key = [confirmed.get(b, random.randint(0,MOD-1)) for b in range(KLEN)]
        for b in free_pos:
            if b not in confirmed:
                key[b] = random.randint(0, MOD-1)
        dec = decrypt(key)
        score = qg_score_full(dec)
        local_best_s = score
        local_best_k = list(key)
        
        T = T0
        while T > T_min:
            b = random.choice(free_pos)
            old_val = key[b]
            new_val = random.randint(0, MOD-2)
            if new_val >= old_val: new_val += 1
            
            bpos = bucket_positions[b]
            old_vals = [dec[p] for p in bpos]
            new_vals = [(cipher[p]-new_val)%MOD for p in bpos]
            
            delta = qg_delta(dec, bpos, old_vals, new_vals, N)
            
            if delta > 0 or random.random() < math.exp(delta*10 / T):  # Scale delta for SA sensitivity
                for idx, p in enumerate(bpos):
                    dec[p] = new_vals[idx]
                key[b] = new_val
                score += delta
                if score > local_best_s:
                    local_best_s = score
                    local_best_k = list(key)
            
            T *= alpha
        
        if local_best_s > best_score:
            best_score = local_best_s
            best_key = list(local_best_k)
        
        if (r+1) % 100 == 0:
            dt = time.time() - t0
            dec_b = decrypt(best_key)
            txt = ''.join(LAT[v] for v in dec_b[:120])
            print(f"  [{r+1}/{n_restarts}] score={best_score:.2f} ({dt:.1f}s)")
            print(f"    text: {txt}")
    
    return best_key, best_score

# ===== PHASE 1: Confirmed fixed =====
print(f"\n{'='*80}")
print(f"PHASE 1: SA with {len(confirmed)} confirmed fixed, {len(undetermined)} free")
print(f"{'='*80}")
key1, score1 = sa_quadgram(undetermined, n_restarts=500)
dec1 = decrypt(key1)
text1 = ''.join(LAT[v] for v in dec1)
print(f"\nBest: score={score1:.2f}")
print(f"Key: {key1}")
for b in undetermined:
    print(f"  key[{b:2d}] = {key1[b]:2d} ({LAT[key1[b]]})")
print(f"Text:")
for i in range(0, len(text1), 70):
    print(f"  [{i:3d}] {text1[i:i+70]}")

# ===== PHASE 2: All free =====
print(f"\n{'='*80}")
print(f"PHASE 2: SA with ALL 53 free")
print(f"{'='*80}")
all_pos = list(range(KLEN))
key2, score2 = sa_quadgram(all_pos, n_restarts=500, T0=3.0, alpha=0.99975)
dec2 = decrypt(key2)
text2 = ''.join(LAT[v] for v in dec2)
n_agree = sum(1 for b,v in confirmed.items() if key2[b]==v)
print(f"\nBest: score={score2:.2f}, agrees={n_agree}/{len(confirmed)}")
print(f"Key: {key2}")
print(f"Text:")
for i in range(0, len(text2), 70):
    print(f"  [{i:3d}] {text2[i:i+70]}")

# ===== PHASE 3: Test SOLUTION.md key =====
print(f"\n{'='*80}")
print(f"PHASE 3: Score comparison")
print(f"{'='*80}")
sol_key = [11,6,1,20,25,20,9,15,24,26,25,7,19,8,10,24,18,9,0,16,9,4,14,22,13,13,3,28,5,21,24,19,5,1,27,14,6,17,24,24,22,8,23,6,22,19,2,11,3,19,25,15,24]
dec_sol = decrypt(sol_key)
score_sol = qg_score_full(dec_sol)
text_sol = ''.join(LAT[v] for v in dec_sol)
print(f"SOLUTION.md key (as repeating): score={score_sol:.2f}")
print(f"  Text[:200]: {text_sol[:200]}")

print(f"\nPhase 1 score: {score1:.2f}")
print(f"Phase 2 score: {score2:.2f}")
print(f"SOLUTION key score: {score_sol:.2f}")

# ===== PHASE 4: Try Beaufort =====
print(f"\n{'='*80}")
print(f"PHASE 4: Beaufort and ADD modes")
print(f"{'='*80}")

for mode, mfn in [('ADD', lambda c,k: (c+k)%MOD), ('BEAU', lambda c,k: (k-c)%MOD)]:
    best_s = -float('inf')
    best_k = None
    for r in range(200):
        key = [random.randint(0,MOD-1) for _ in range(KLEN)]
        dec = [mfn(cipher[i], key[i%KLEN]) for i in range(N)]
        score = qg_score_full(dec)
        best_ls = score
        best_lk = list(key)
        T = 3.0
        while T > 0.005:
            b = random.randint(0,KLEN-1)
            old_v = key[b]
            new_v = random.randint(0,MOD-2)
            if new_v >= old_v: new_v += 1
            key[b] = new_v
            dec2 = [mfn(cipher[i], key[i%KLEN]) for i in range(N)]
            ns = qg_score_full(dec2)
            d = ns - score
            if d > 0 or random.random() < math.exp(d*10/T):
                score = ns
                dec = dec2
                if score > best_ls:
                    best_ls = score
                    best_lk = list(key)
            else:
                key[b] = old_v
            T *= 0.999
        if best_ls > best_s:
            best_s = best_ls
            best_k = list(best_lk)
    dec_m = [mfn(cipher[i], best_k[i%KLEN]) for i in range(N)]
    txt_m = ''.join(LAT[v] for v in dec_m)
    print(f"{mode}: score={best_s:.2f}")
    print(f"  Text[:200]: {txt_m[:200]}")

print(f"\nTotal: {time.time()-time.time():.0f}s")
print("=== DONE ===")
