"""
P18 SA Solver - Quadgram scoring with chi-squared initialization
CORRECT GP mapping verified by P55/P73 85/85 solution
"""
import sys, io, os, random, math, time
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []; i = 0; text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            result.append(DIGRAPHS[text[i:i+2]]); i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]]); i += 1
        else: i += 1
    return result

# Build corpus from ALL solved LP text
corpus_text = """
A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
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
COMMAND YOUR OWN SELF
THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED
A MAN DECIDED TO GO AND STUDY WITH A MASTER
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
DO FOUR UNREASONABLE THINGS EACH DAY
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
AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN
BE PREPARED TO DESTROY ALL THAT YOU OWN
PROGRAM YOUR MIND PROGRAM REALITY
DURING A LESSON THE MASTER EXPLAINED THE I
THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID
IT IS A VOICE INSIDE YOUR HEAD
I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT
AND HE RAISED HIS HAND TO TELL THE MASTER
THE MASTER STOPPED THE STUDENT AND SAID
THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I
AND THE STUDENTS WERE ENLIGHTENED
QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF
FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
LIKE THE INSTAR TUNNELING TO THE SURFACE
WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE
REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR
"""

corpus_gp = eng_to_gp(corpus_text)
print(f"Corpus: {len(corpus_gp)} GP values")

# Build quadgram model
qg_counts = defaultdict(int)
for i in range(len(corpus_gp)-3):
    key = (corpus_gp[i], corpus_gp[i+1], corpus_gp[i+2], corpus_gp[i+3])
    qg_counts[key] += 1

total_qg = len(corpus_gp) - 3
FLOOR = math.log10(0.01 / total_qg)
qg_logp = {}
for qg, cnt in qg_counts.items():
    qg_logp[qg] = math.log10(cnt / total_qg)

print(f"Quadgram model: {len(qg_logp)} distinct (of {total_qg} total)")

# Also build bigram model for faster scoring
bg_counts = defaultdict(int)
for i in range(len(corpus_gp)-1):
    bg_counts[(corpus_gp[i], corpus_gp[i+1])] += 1
total_bg = len(corpus_gp) - 1
BG_FLOOR = math.log10(0.01 / total_bg)
bg_logp = {}
for bg, cnt in bg_counts.items():
    bg_logp[bg] = math.log10(cnt / total_bg)

# Target frequency for chi-squared
target_freq = [0.0] * MOD
c_corp = Counter(corpus_gp)
total_corp = len(corpus_gp)
for idx in range(MOD):
    target_freq[idx] = c_corp.get(idx, 0) / total_corp

# Load cipher
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"P18: {N} runes")

bucket_positions = [[] for _ in range(KLEN)]
for i in range(N):
    bucket_positions[i%KLEN].append(i)

def decrypt_sub(cip, key):
    return [(cip[i] - key[i % len(key)]) % MOD for i in range(len(cip))]

def qg_score(dec):
    s = 0.0
    for i in range(len(dec)-3):
        s += qg_logp.get((dec[i], dec[i+1], dec[i+2], dec[i+3]), FLOOR)
    return s

def bg_score(dec):
    s = 0.0
    for i in range(len(dec)-1):
        s += bg_logp.get((dec[i], dec[i+1]), BG_FLOOR)
    return s

# Chi-squared initial key
def chi_key():
    key = []
    for b in range(KLEN):
        col = [cipher[i] for i in range(b, N, KLEN)]
        n_col = len(col)
        best_chi = float('inf'); best_s = 0
        for s in range(MOD):
            shifted = [(c - s) % MOD for c in col]
            obs = [0.0] * MOD
            cc = Counter(shifted)
            for idx in range(MOD): obs[idx] = cc.get(idx, 0) / n_col
            chi = sum((obs[j] - target_freq[j])**2 / max(target_freq[j], 0.001) for j in range(MOD))
            if chi < best_chi:
                best_chi = chi; best_s = s
        key.append(best_s)
    return key

# SA with quadgram scoring - efficient incremental updates
def sa_solve(init_key, n_iters=200000, T0=2.0, alpha=0.99997, use_qg=True):
    key = list(init_key)
    dec = decrypt_sub(cipher, key)
    score = qg_score(dec) if use_qg else bg_score(dec)
    best_score = score
    best_key = list(key)
    T = T0
    accepts = 0
    
    for it in range(n_iters):
        b = random.randint(0, KLEN-1)
        old_val = key[b]
        new_val = random.randint(0, MOD-2)
        if new_val >= old_val: new_val += 1
        
        # Compute delta efficiently
        bpos = bucket_positions[b]
        affected = set()
        for pos in bpos:
            for start in range(max(0, pos-3), min(N-3, pos+1)):
                affected.add(start)
        
        delta = 0.0
        if use_qg:
            for start in affected:
                old_qg = (dec[start], dec[start+1], dec[start+2], dec[start+3])
                new_qg = list(old_qg)
                for pos in bpos:
                    offset = pos - start
                    if 0 <= offset < 4:
                        new_qg[offset] = (cipher[pos] - new_val) % MOD
                delta -= qg_logp.get(old_qg, FLOOR)
                delta += qg_logp.get(tuple(new_qg), FLOOR)
        else:
            for start in affected:
                if start+1 < N:
                    old_bg = (dec[start], dec[start+1])
                    new_bg_l = list(old_bg)
                    for pos in bpos:
                        if pos == start: new_bg_l[0] = (cipher[pos] - new_val) % MOD
                        elif pos == start+1: new_bg_l[1] = (cipher[pos] - new_val) % MOD
                    delta -= bg_logp.get(old_bg, BG_FLOOR)
                    delta += bg_logp.get(tuple(new_bg_l), BG_FLOOR)
        
        if delta > 0 or random.random() < math.exp(delta * 10 / max(T, 0.0001)):
            for pos in bpos:
                dec[pos] = (cipher[pos] - new_val) % MOD
            key[b] = new_val
            score += delta
            accepts += 1
            if score > best_score:
                best_score = score
                best_key = list(key)
        
        T *= alpha
    
    return best_key, best_score, accepts

# === MAIN ===
t0 = time.time()

# Phase 1: Chi-squared initialization + SA refinement
chi_init = chi_key()
dec_chi = decrypt_sub(cipher, chi_init)
print(f"\nChi-squared init: qg_score={qg_score(dec_chi):.2f}")
print(f"Text: {''.join(LAT[v] for v in dec_chi[:100])}")

# Phase 2: Multiple SA restarts from chi-squared + random perturbation
print(f"\n{'='*70}")
print("SA SEARCH (quadgram scoring)")
print(f"{'='*70}")

best_overall_score = -float('inf')
best_overall_key = None
n_restarts = 200

for r in range(n_restarts):
    # Start from chi-squared key with random perturbations
    if r == 0:
        init = list(chi_init)
    elif r < 50:
        # Perturb 5-15 positions from chi key
        init = list(chi_init)
        for _ in range(random.randint(5, 15)):
            pos = random.randint(0, KLEN-1)
            init[pos] = random.randint(0, MOD-1)
    else:
        # Fully random start
        init = [random.randint(0, MOD-1) for _ in range(KLEN)]
    
    key, score, accepts = sa_solve(init, n_iters=150000, T0=2.0 + random.random(), alpha=0.99997)
    
    if score > best_overall_score:
        best_overall_score = score
        best_overall_key = list(key)
        dec_best = decrypt_sub(cipher, key)
        txt = ''.join(LAT[v] for v in dec_best[:120])
        print(f"  [{r+1:3d}] NEW BEST score={score:.2f} accepts={accepts}")
        print(f"    {txt}")
    
    if (r+1) % 50 == 0:
        dt = time.time() - t0
        print(f"  --- {r+1}/{n_restarts} done ({dt:.0f}s) best={best_overall_score:.2f} ---")

# Final output
print(f"\n{'='*70}")
print("FINAL RESULT")
print(f"{'='*70}")
dec_final = decrypt_sub(cipher, best_overall_key)
txt_final = ''.join(LAT[v] for v in dec_final)
print(f"Score: {best_overall_score:.2f}")
print(f"Key: {best_overall_key}")
print(f"Text:")
for i in range(0, len(txt_final), 70):
    print(f"  [{i:3d}] {txt_final[i:i+70]}")

# Also try ADD and Beaufort with best SA approach
print(f"\n{'='*70}")
print("TESTING ADD AND BEAUFORT MODES")
print(f"{'='*70}")

for mode_name, mode_fn in [('ADD', lambda c,k: (c+k)%MOD), ('BEAUFORT', lambda c,k: (k-c)%MOD)]:
    best_ms = -float('inf')
    best_mk = None
    for r in range(50):
        init = [random.randint(0, MOD-1) for _ in range(KLEN)]
        key = list(init)
        dec = [mode_fn(cipher[i], key[i%KLEN]) for i in range(N)]
        score = qg_score(dec)
        best_ls = score; best_lk = list(key)
        T = 2.5
        for it in range(100000):
            b = random.randint(0, KLEN-1)
            old_v = key[b]
            new_v = random.randint(0, MOD-2)
            if new_v >= old_v: new_v += 1
            key[b] = new_v
            dec2 = [mode_fn(cipher[i], key[i%KLEN]) for i in range(N)]
            ns = qg_score(dec2)
            d = ns - score
            if d > 0 or random.random() < math.exp(d*10/max(T,0.001)):
                score = ns; dec = dec2
                if score > best_ls: best_ls = score; best_lk = list(key)
            else:
                key[b] = old_v
            T *= 0.99995
        if best_ls > best_ms:
            best_ms = best_ls; best_mk = list(best_lk)
    
    dec_m = [mode_fn(cipher[i], best_mk[i%KLEN]) for i in range(N)]
    txt_m = ''.join(LAT[v] for v in dec_m[:150])
    print(f"{mode_name}: score={best_ms:.2f}")
    print(f"  Text: {txt_m}")

total_time = time.time() - t0
print(f"\nTotal time: {total_time:.0f}s")
