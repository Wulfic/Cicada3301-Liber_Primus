"""
P54 SOLVER — 76 runes, period 13, IoC*29 = 2.01
STRONG Vigenère signal! ~5.8 runes per column.
Also try P49 (66 runes), P62 (121 runes), P22 (131 runes).

Strategy:
1. IoC analysis to confirm key length
2. Column-by-column frequency analysis
3. SA with quadgram/word scoring
4. Try all cipher modes (SUB, ADD, BEAU)
5. Try known keys (DIVINITY, FIRFUMFERENFE, etc.)
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

# English frequency in GP encoding (from solved pages)
ENG_FREQ = [0.0]*MOD
corpus = eng_to_gp("""
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING
YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY
CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS
WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE
A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH
WISDOM YOU ARE A BEING UNTO YOURSELF EACH INTELLIGENCE IS HOLY
A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER
THE LOSS OF DIVINITY WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK
""")
for v in corpus:
    ENG_FREQ[v] += 1
total = sum(ENG_FREQ)
ENG_FREQ = [c/total for c in ENG_FREQ]

# Quadgram model
corpus_all = eng_to_gp("""
A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE
IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES
JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR
WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY
AN INSTRUCTION COMMAND YOUR OWN SELF SOME WISDOM THE PRIMES ARE SACRED
THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED
A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER
HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE
THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE
THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR
CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING
THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS
CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS
WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH
PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK
ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT
THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED
FIND THE DIVINITY WITHIN AND EMERGE REARRANGING THE PRIMES
BEING OF ALL WILL THE OATH IS SWORN TO THE ONE WITHIN
""")
qg_counts = defaultdict(int)
for i in range(len(corpus_all)-3):
    qg_counts[(corpus_all[i],corpus_all[i+1],corpus_all[i+2],corpus_all[i+3])] += 1
total_qg = len(corpus_all)-3
FLOOR = math.log10(0.01/total_qg)
qg_logp = {k: math.log10(v/total_qg) for k,v in qg_counts.items()}

def qg_score(dec):
    return sum(qg_logp.get((dec[i],dec[i+1],dec[i+2],dec[i+3]),FLOOR) for i in range(len(dec)-3))

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    return [GP[c] for c in raw if c in GP]

def ioc_analysis(cipher, max_kl=40):
    """IoC*29 for each key length."""
    N = len(cipher)
    results = []
    for kl in range(1, min(max_kl+1, N//2)):
        columns = [[] for _ in range(kl)]
        for i, v in enumerate(cipher):
            columns[i%kl].append(v)
        total_ioc = 0
        for col in columns:
            n = len(col)
            if n < 2: continue
            counts = Counter(col)
            ioc = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
            total_ioc += ioc
        avg_ioc = total_ioc / kl * MOD
        results.append((kl, avg_ioc))
    return results

def try_vigenere(cipher, klen, mode='SUB'):
    """Try all 29^klen keys via column frequency analysis."""
    N = len(cipher)
    columns = [[] for _ in range(klen)]
    for i, v in enumerate(cipher):
        columns[i%klen].append(v)
    
    key = [0]*klen
    for b in range(klen):
        col = columns[b]
        best_corr = -1
        best_k = 0
        for k in range(MOD):
            if mode == 'SUB':
                dec = [(v-k)%MOD for v in col]
            elif mode == 'ADD':
                dec = [(v+k)%MOD for v in col]
            elif mode == 'BEAU':
                dec = [(k-v)%MOD for v in col]
            
            # Chi-squared vs English
            obs = Counter(dec)
            n = len(col)
            corr = sum(ENG_FREQ[v] * obs.get(v,0) / n for v in range(MOD))
            if corr > best_corr:
                best_corr = corr
                best_k = k
        key[b] = best_k
    
    # Decrypt
    dec = []
    for i in range(N):
        k = key[i%klen]
        if mode == 'SUB': dec.append((cipher[i]-k)%MOD)
        elif mode == 'ADD': dec.append((cipher[i]+k)%MOD)
        elif mode == 'BEAU': dec.append((k-cipher[i])%MOD)
    
    text = ''.join(LAT[v] for v in dec)
    score = qg_score(dec)
    return key, dec, text, score

def try_known_keys(cipher, keywords):
    """Try known Cicada keywords as Vigenère keys."""
    N = len(cipher)
    results = []
    for kw_name, kw_text in keywords:
        kw_gp = eng_to_gp(kw_text)
        if len(kw_gp) == 0: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = []
            for i in range(N):
                k = kw_gp[i % len(kw_gp)]
                if mode == 'SUB': dec.append((cipher[i]-k)%MOD)
                elif mode == 'ADD': dec.append((cipher[i]+k)%MOD)
                elif mode == 'BEAU': dec.append((k-cipher[i])%MOD)
            text = ''.join(LAT[v] for v in dec)
            score = qg_score(dec)
            results.append((score, kw_name, mode, text[:100]))
    results.sort(reverse=True)
    return results

def sa_vigenere(cipher, klen, mode='SUB', n_restarts=200):
    N = len(cipher)
    best_score = -float('inf')
    best_key = None
    best_text = None
    
    for r in range(n_restarts):
        key = [random.randint(0,MOD-1) for _ in range(klen)]
        dec = []
        for i in range(N):
            k = key[i%klen]
            if mode=='SUB': dec.append((cipher[i]-k)%MOD)
            elif mode=='ADD': dec.append((cipher[i]+k)%MOD)
            elif mode=='BEAU': dec.append((k-cipher[i])%MOD)
        score = qg_score(dec)
        local_best = (score, list(key))
        
        T = 3.0
        while T > 0.005:
            b = random.randint(0, klen-1)
            old_v = key[b]
            new_v = random.randint(0, MOD-2)
            if new_v >= old_v: new_v += 1
            key[b] = new_v
            new_dec = list(dec)
            for i in range(b, N, klen):
                if mode=='SUB': new_dec[i]=(cipher[i]-new_v)%MOD
                elif mode=='ADD': new_dec[i]=(cipher[i]+new_v)%MOD
                elif mode=='BEAU': new_dec[i]=(new_v-cipher[i])%MOD
            ns = qg_score(new_dec)
            d = ns - score
            if d > 0 or random.random() < math.exp(d*10/T):
                score = ns
                dec = new_dec
                if score > local_best[0]:
                    local_best = (score, list(key))
            else:
                key[b] = old_v
            T *= 0.999
        
        s, k = local_best
        if s > best_score:
            best_score = s
            best_key = list(k)
            dec_b = []
            for i in range(N):
                kv = best_key[i%klen]
                if mode=='SUB': dec_b.append((cipher[i]-kv)%MOD)
                elif mode=='ADD': dec_b.append((cipher[i]+kv)%MOD)
                elif mode=='BEAU': dec_b.append((kv-cipher[i])%MOD)
            best_text = ''.join(LAT[v] for v in dec_b)
    
    return best_key, best_score, best_text

# Known Cicada keywords
KEYWORDS = [
    ("DIVINITY", "DIVINITY"),
    ("FIRFUMFERENFE", "FIRFUMFERENFE"),
    ("CIRCUMFERENCE", "CIRCUMFERENCE"),
    ("INSTAR", "INSTAR"),
    ("PRIMUS", "PRIMUS"),
    ("SACRED", "SACRED"),
    ("WISDOM", "WISDOM"),
    ("TRUTH", "TRUTH"),
    ("DEOR", "DEOR"),
    ("CONSUMPTION", "CONSUMPTION"),
    ("PRESERVATION", "PRESERVATION"),
    ("ADHERENCE", "ADHERENCE"),
    ("SHADOWS", "SHADOWS"),
    ("CABAL", "CABAL"),
    ("MOBIUS", "MOBIUS"),
    ("LIBER", "LIBER"),
    ("INTUS", "INTUS"),
    ("EMERGE", "EMERGE"),
    ("PILGRIM", "PILGRIM"),
    ("PRIMALITY", "PRIMALITY"),
]

# ===== ANALYZE EACH PAGE =====
for pg in [54, 49, 62, 22]:
    cipher = load_page(pg)
    N = len(cipher)
    print(f"\n{'='*80}")
    print(f"PAGE {pg}: {N} runes")
    print(f"{'='*80}")
    
    # IoC analysis
    ioc_results = ioc_analysis(cipher)
    print(f"\nTop IoC*29 values:")
    sorted_ioc = sorted(ioc_results, key=lambda x: -x[1])[:10]
    for kl, ioc in sorted_ioc:
        print(f"  kl={kl:2d}: IoC*29={ioc:.3f}")
    
    # Best key lengths
    top_klens = [kl for kl, ioc in sorted_ioc[:5]]
    
    # Try known keywords
    print(f"\nKnown keyword results:")
    kw_results = try_known_keys(cipher, KEYWORDS)
    for score, kw, mode, text in kw_results[:5]:
        print(f"  {kw} ({mode}): score={score:.2f} text={text}")
    
    # Try frequency analysis for top key lengths
    print(f"\nFrequency analysis for best key lengths:")
    for kl in top_klens[:3]:
        for mode in ['SUB', 'ADD', 'BEAU']:
            key, dec, text, score = try_vigenere(cipher, kl, mode)
            key_lat = ''.join(LAT[v] for v in key)
            print(f"  kl={kl:2d} {mode:4s}: score={score:.2f} key={key_lat[:30]} text={text[:80]}")
    
    # Try Caesar shifts (kl=1)
    print(f"\nCaesar shifts:")
    for shift in range(MOD):
        for mode in ['SUB', 'ADD']:
            dec = [(cipher[i]-shift)%MOD if mode=='SUB' else (cipher[i]+shift)%MOD for i in range(N)]
            text = ''.join(LAT[v] for v in dec)
            score = qg_score(dec)
            if score > -N*0.5:  # Only show promising ones
                print(f"  shift={shift:2d} ({LAT[shift]}) {mode}: score={score:.2f} text={text[:60]}")
    
    # SA for best key length and mode
    print(f"\nSA optimization:")
    best_overall = None
    for kl in top_klens[:2]:
        for mode in ['SUB', 'ADD', 'BEAU']:
            key, score, text = sa_vigenere(cipher, kl, mode, n_restarts=100)
            key_lat = ''.join(LAT[v] for v in key)
            if best_overall is None or score > best_overall[1]:
                best_overall = (key, score, text, kl, mode, key_lat)
            print(f"  kl={kl:2d} {mode:4s}: score={score:.2f} key={key_lat[:30]}... text={text[:80]}")
    
    if best_overall:
        key, score, text, kl, mode, key_lat = best_overall
        print(f"\n  BEST: kl={kl} {mode} score={score:.2f}")
        print(f"  Key: {key}")
        print(f"  Key (LAT): {key_lat}")
        print(f"  Full text: {text}")

print("\n=== DONE ===")
