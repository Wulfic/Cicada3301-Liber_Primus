"""
P54 DEEP SOLVER — 76 runes, period 13, IoC*29=2.008
SA found "WITHIN THE DEEP" with kl=13 ADD mode!
Known Cicada text: "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO..."

Also: kl=26 has IoC*29=2.603 (= 2×13)

Strategy:
1. Confirm kl=13 with crib "WITHIN THE DEEP"
2. Use known plaintext to recover key
3. Try kl=13 with all cribs from known Cicada texts
"""
import os, sys, random, math
from collections import Counter, defaultdict

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

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

# Load P54
with open('LiberPrimus/pages/page_54/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

# Parse structure
chars = []
for c in raw:
    if c in GP:
        chars.append(('R', GP[c]))
    elif c == '\u2022' or c == '•':
        chars.append(('S', -1))
    elif c == '-':
        chars.append(('D', -2))
    elif c == '\n':
        chars.append(('N', -3))
    elif c == '.':
        chars.append(('P', -4))

cipher = [v for t,v in chars if t == 'R']
N = len(cipher)
print(f"P54: {N} runes")

# Show raw structure
sep_count = sum(1 for t,v in chars if t in ('S','D','P'))
nl_count = sum(1 for t,v in chars if t == 'N')
print(f"Separators: {sep_count}, Newlines: {nl_count}")
print(f"Character stream: ", end="")
for t, v in chars[:60]:
    if t == 'R': print(f'{v}', end=' ')
    elif t == 'S': print('BULL', end=' ')
    elif t == 'D': print('DASH', end=' ')
    elif t == 'N': print('NL', end=' ')
    elif t == 'P': print('DOT', end=' ')
print("...")

# ===== KNOWN PLAINTEXT CRIBS =====
print("\n" + "="*80)
print("CRIB TESTING — known Cicada texts")
print("="*80)

# Known texts that might appear on P54
cribs = {
    "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO": None,
    "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO": None,
    "WITHIN THE DEEP WEB THERE EXISTS A PAGE": None,
    "AN END WITHIN THE DEEP WEB THERE EXISTS": None,
    "AN END WITHIN THE DEEP WEB": None,
    "WITHIN THE DEEP WEB": None,
    "WITHIN THE DEEP": None,
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS": None,
    "THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY": None,
    "THE LOSS OF DIVINITY": None,
    "CONSUMPTION WE CONSUME TOO MUCH": None,
    "ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT": None,
    "WELCOME PILGRIM TO THE GREAT JOURNEY": None,
    "A WARNING BELIEVE NOTHING FROM THIS BOOK": None,
}

for crib_text in cribs:
    crib_gp = eng_to_gp(crib_text)
    cribs[crib_text] = crib_gp
    if len(crib_gp) > N:
        continue
    
    print(f"\nCrib: '{crib_text}' ({len(crib_gp)} GP values)")
    
    # Try at every position with every mode
    for mode in ['SUB', 'ADD', 'BEAU']:
        for start_pos in range(N - len(crib_gp) + 1):
            # Recover key
            key_recovered = []
            for j in range(len(crib_gp)):
                ci = cipher[start_pos + j]
                pi = crib_gp[j]
                if mode == 'SUB':
                    k = (ci - pi) % MOD
                elif mode == 'ADD':
                    k = (pi - ci) % MOD
                elif mode == 'BEAU':
                    k = (pi + ci) % MOD
                key_recovered.append(k)
            
            # Check if key is periodic with period 13
            for period in [13, 26]:
                if len(crib_gp) < period: continue
                is_periodic = True
                for j in range(len(crib_gp)):
                    expected_idx = (start_pos + j) % period
                    # Build expected key for this period
                    ref_idx = -1
                    for k in range(j):
                        if (start_pos + k) % period == expected_idx:
                            ref_idx = k
                            break
                    if ref_idx >= 0 and key_recovered[j] != key_recovered[ref_idx]:
                        is_periodic = False
                        break
                
                if is_periodic:
                    # Extract the period-length key
                    full_key = [None] * period
                    for j in range(len(crib_gp)):
                        idx = (start_pos + j) % period
                        full_key[idx] = key_recovered[j]
                    
                    # Decrypt full cipher with this key
                    dec = []
                    for i in range(N):
                        ki = i % period
                        if full_key[ki] is not None:
                            if mode == 'SUB': dec.append((cipher[i] - full_key[ki]) % MOD)
                            elif mode == 'ADD': dec.append((cipher[i] + full_key[ki]) % MOD)
                            elif mode == 'BEAU': dec.append((full_key[ki] - cipher[i]) % MOD)
                        else:
                            dec.append(-1)
                    
                    # Count known positions
                    known = sum(1 for k in full_key if k is not None)
                    text = ''.join(LAT[v] if v >= 0 else '?' for v in dec)
                    
                    # Score
                    score = 0
                    for w in ['THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS','WHICH',
                              'ARE','WITHIN','HOLY','LIVES','EACH','BEING','UNTO','YOURSELF',
                              'WEB','PAGE','DEEP','HASHES','EXISTS','END','WISDOM','DIVINITY',
                              'INSTRUCTION','COMMAND','SELF','OWN','TRUTH','SACRED']:
                        score += text.count(w) * len(w)
                    
                    if score >= 15 or known >= 10:
                        key_str = ''.join(LAT[k] if k is not None else '?' for k in full_key)
                        print(f"  {mode} pos={start_pos:2d} per={period:2d}: {known}/{period} key positions, score={score}")
                        print(f"    Key: {key_str}")
                        print(f"    Text: {text[:100]}")

# ===== SA WITH KL=13 ADD (best from initial scan) =====
print("\n" + "="*80)
print("REFINED SA — kl=13 all modes")
print("="*80)

# English frequency for scoring
ENG_FREQ = [0.0]*MOD
corpus = eng_to_gp("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH WISDOM YOU ARE A BEING UNTO YOURSELF EACH INTELLIGENCE IS HOLY A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE LOSS OF DIVINITY WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK BEING OF ALL WILL THE OATH IS SWORN TO THE ONE WITHIN")
for v in corpus:
    ENG_FREQ[v] += 1
total = sum(ENG_FREQ)
ENG_FREQ = [c/total for c in ENG_FREQ]

# Bigram model
bg_counts = defaultdict(int)
bg_total = 0
for i in range(len(corpus)-1):
    bg_counts[(corpus[i], corpus[i+1])] += 1
    bg_total += 1
FLOOR_BG = math.log10(0.01/max(1,bg_total))
bg_logp = {k: math.log10(v/bg_total) for k,v in bg_counts.items()}

def bigram_score(dec):
    return sum(bg_logp.get((dec[i],dec[i+1]), FLOOR_BG) for i in range(len(dec)-1))

def sa_solve(cipher, kl, mode, n_restarts=500, n_anneal=3000):
    N = len(cipher)
    best_score = -float('inf')
    best_key = None
    
    for r in range(n_restarts):
        key = [random.randint(0, MOD-1) for _ in range(kl)]
        # Decrypt
        dec = []
        for i in range(N):
            k = key[i % kl]
            if mode == 'SUB': dec.append((cipher[i]-k)%MOD)
            elif mode == 'ADD': dec.append((cipher[i]+k)%MOD)
            elif mode == 'BEAU': dec.append((k-cipher[i])%MOD)
        score = bigram_score(dec)
        local_best = (score, list(key))
        
        T = 5.0
        for step in range(n_anneal):
            b = random.randint(0, kl-1)
            old_v = key[b]
            new_v = random.randint(0, MOD-2)
            if new_v >= old_v: new_v += 1
            key[b] = new_v
            new_dec = list(dec)
            for i in range(b, N, kl):
                if mode=='SUB': new_dec[i]=(cipher[i]-new_v)%MOD
                elif mode=='ADD': new_dec[i]=(cipher[i]+new_v)%MOD
                elif mode=='BEAU': new_dec[i]=(new_v-cipher[i])%MOD
            ns = bigram_score(new_dec)
            d = ns - score
            if d > 0 or random.random() < math.exp(d*10/T):
                score = ns
                dec = new_dec
                if score > local_best[0]:
                    local_best = (score, list(key))
            else:
                key[b] = old_v
            T *= 0.998
        
        s, k = local_best
        if s > best_score:
            best_score = s
            best_key = list(k)
    
    # Final decrypt
    dec = []
    for i in range(N):
        k = best_key[i%kl]
        if mode=='SUB': dec.append((cipher[i]-k)%MOD)
        elif mode=='ADD': dec.append((cipher[i]+k)%MOD)
        elif mode=='BEAU': dec.append((k-cipher[i])%MOD)
    text = gp_to_lat(dec)
    return best_key, best_score, dec, text

for mode in ['SUB', 'ADD', 'BEAU']:
    print(f"\n--- {mode} kl=13 ---")
    key, score, dec, text = sa_solve(cipher, 13, mode, n_restarts=500)
    key_lat = gp_to_lat(key)
    print(f"  Score: {score:.2f}")
    print(f"  Key: {key}")
    print(f"  Key LAT: {key_lat}")
    print(f"  Text: {text}")
    
    # Count English words
    words = ['THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS','WHICH','ARE',
             'WITHIN','HOLY','LIVES','EACH','BEING','UNTO','YOUR','YOURSELF','WEB','PAGE',
             'DEEP','HASHES','EXISTS','END','WISDOM','DIVINITY','INSTRUCTION','TRUTH',
             'SACRED','LOSS','CIRCUMFERENCE','BELIEVE','NOTHING','FIND','SELF','OWN',
             'DEATH','INTELLIGENCE','LAW','COMMAND','MASTER','STUDY','PILGRIM']
    hits = []
    for w in words:
        if w in text:
            hits.append(w)
    if hits:
        print(f"  English words found: {hits}")

# ===== Also try kl=26 (2×13) =====
print("\n" + "="*80)
print("SA — kl=26 (IoC=2.603)")
print("="*80)

for mode in ['SUB', 'ADD', 'BEAU']:
    print(f"\n--- {mode} kl=26 ---")
    key, score, dec, text = sa_solve(cipher, 26, mode, n_restarts=200)
    key_lat = gp_to_lat(key)
    print(f"  Score: {score:.2f}")
    print(f"  Key LAT: {key_lat}")
    print(f"  Text: {text}")
    hits = [w for w in ['THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS','DEEP',
                         'WITHIN','WEB','PAGE','EXISTS','HASHES','END','BELIEVE'] if w in text]
    if hits:
        print(f"  English words: {hits}")

print("\n=== DONE ===")
