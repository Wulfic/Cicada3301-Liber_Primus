"""Comprehensive cipher testing on P71 (308 runes, IoC~1.0, encrypted)"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

ENG = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
       'M':19,'N':9,'O':3,'P':13,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26}

KEYWORDS = {
    'DIVINITY': [23,10,1,10,9,10,16,26],
    'CABAL': [5,24,17,24,20],
    'ENCRYPTION': [18,9,5,4,26,13,16,10,3,9],
    'OBSCURA': [3,17,15,5,1,4,24],
    'ENCRYPT': [18,9,5,4,26,13,16],
    'SHADOWS': [15,8,24,23,3,7,15],
    'DEOR': [23,18,3,4],
    'TOTIENT': [16,3,16,10,18,9,16],
    'MOURNFUL': [19,3,1,4,9,0,1,20],
    'CIRCUMFERENCE': [5,10,4,5,1,19,0,18,4,18,9,5,18],
    'FIRFUMFERENFE': [0,10,4,0,1,19,0,18,4,18,9,0,18],
    'PRIMUS': [13,4,10,19,1,15],
    'MOBIUS': [19,3,17,10,1,15],
    'WELCOME': [7,18,20,5,3,19,18],
}

def load(p):
    rf = 'LiberPrimus/pages/page_%02d/runes.txt' % p
    with open(rf,'r',encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def ioc(data):
    if len(data) < 2: return 0
    c = Counter(data)
    n = len(data)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)) * 29

def score_english(text):
    bigrams = ['TH','HE','IN','AN','ER','ON','RE','AT','EN','ND','ST','OR','TE','ES','IS','IT','NT','TO','AR','SE','OU','ED','HA','OF']
    sc = 0
    for i in range(len(text)-1):
        if text[i:i+2] in bigrams:
            sc += 1
    return sc

def get_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        ok = True
        for p in primes:
            if p*p > c: break
            if c % p == 0: ok = False; break
        if ok: primes.append(c)
        c += 1
    return primes

p71 = load(71)
print("P71: %d runes, IoC: %.3f" % (len(p71), ioc(p71)))

results = []

# === 1. Totient cipher (all offsets, with/without F-skip) ===
print("\n=== TOTIENT CIPHER ===")
primes = get_primes(500)
for offset in range(50):
    # With F-skip
    dec = []
    ki = 0
    for r in p71:
        if r == 0:
            dec.append(0)
        else:
            dec.append((r - (primes[ki+offset]-1)) % 29)
            ki += 1
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    ic = ioc(dec)
    if sc > 15 or ic > 1.3:
        results.append(('TOTIENT fskip off=%d' % offset, sc, ic, text[:60]))
    
    # Without F-skip
    dec2 = [(r - (primes[i+offset]-1)) % 29 for i, r in enumerate(p71)]
    text2 = ''.join(IDX[i] for i in dec2)
    sc2 = score_english(text2)
    ic2 = ioc(dec2)
    if sc2 > 15 or ic2 > 1.3:
        results.append(('TOTIENT noskip off=%d' % offset, sc2, ic2, text2[:60]))
    
    # ADD mode: (r + (p-1)) % 29
    dec3 = []
    ki = 0
    for r in p71:
        if r == 0:
            dec3.append(0)
        else:
            dec3.append((r + (primes[ki+offset]-1)) % 29)
            ki += 1
    text3 = ''.join(IDX[i] for i in dec3)
    sc3 = score_english(text3)
    ic3 = ioc(dec3)
    if sc3 > 15 or ic3 > 1.3:
        results.append(('TOTIENT-ADD fskip off=%d' % offset, sc3, ic3, text3[:60]))

# === 2. Vigenere with all keywords ===
print("\n=== VIGENERE ===")
for kname, key in KEYWORDS.items():
    klen = len(key)
    for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29), ("BEAU", lambda c,k: (k-c)%29)]:
        for off in range(klen):
            # Standard
            dec = [mode_fn(p71[i], key[(i+off) % klen]) for i in range(len(p71))]
            text = ''.join(IDX[i] for i in dec)
            sc = score_english(text)
            ic = ioc(dec)
            if sc > 20 or ic > 1.3:
                results.append(('VIG %s %s off=%d' % (kname, mode_name, off), sc, ic, text[:60]))
            
            # F-skip
            dec2 = []
            ki = off
            for r in p71:
                if r == 0:
                    dec2.append(0)
                else:
                    dec2.append(mode_fn(r, key[ki % klen]))
                    ki += 1
            text2 = ''.join(IDX[i] for i in dec2)
            sc2 = score_english(text2)
            ic2 = ioc(dec2)
            if sc2 > 20 or ic2 > 1.3:
                results.append(('VIG-FSKIP %s %s off=%d' % (kname, mode_name, off), sc2, ic2, text2[:60]))

# === 3. Autokey (plaintext and ciphertext feedback) ===
print("\n=== AUTOKEY ===")
for kname, key in KEYWORDS.items():
    klen = len(key)
    for mode_name in ["SUB", "ADD", "BEAU"]:
        # Plaintext autokey
        dec_pt = []
        for i, r in enumerate(p71):
            if i < klen:
                k = key[i]
            else:
                k = dec_pt[i - klen]
            if mode_name == "SUB":
                dec_pt.append((r - k) % 29)
            elif mode_name == "ADD":
                dec_pt.append((r + k) % 29)
            else:
                dec_pt.append((k - r) % 29)
        text = ''.join(IDX[i] for i in dec_pt)
        sc = score_english(text)
        ic = ioc(dec_pt)
        if sc > 20 or ic > 1.3:
            results.append(('AUTOKEY-PT %s %s' % (kname, mode_name), sc, ic, text[:60]))
        
        # Ciphertext autokey
        dec_ct = []
        for i, r in enumerate(p71):
            if i < klen:
                k = key[i]
            else:
                k = p71[i - klen]
            if mode_name == "SUB":
                dec_ct.append((r - k) % 29)
            elif mode_name == "ADD":
                dec_ct.append((r + k) % 29)
            else:
                dec_ct.append((k - r) % 29)
        text = ''.join(IDX[i] for i in dec_ct)
        sc = score_english(text)
        ic = ioc(dec_ct)
        if sc > 20 or ic > 1.3:
            results.append(('AUTOKEY-CT %s %s' % (kname, mode_name), sc, ic, text[:60]))

# === 4. Running key from known plaintexts ===
print("\n=== RUNNING KEY ===")
known_texts = {
    'P05': 'SOMEWISDOMTHEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLDIVISIONSARENOTEQUALSOMEARETRUERANDTHESEARETHEDIVISIONSBETWEENZEROANDONE',
    'P16': 'ANINSTRUCTIONCWESTIONALLTHNGSDISCOUERTRUTHINSIDEYOURSELFFOLLOWYO URTRUTHIMPOSENOTHNGONCLUDEONOTHNGONLYWONDERTHEWORKTHATISCICADA',
    'P13': 'SOMEWISDOMAMASSGREATWEALTHNEUERBECOMEATTACHEDTOWHATYOUOWNBEPREPAREDTODESTROYALLTHATYOUOWNANINSTRUCTIANPROGRAMYOURMINDPROGRAMREALITY',
}
for tname, txt in known_texts.items():
    txt = txt.replace(' ','').upper()
    kvals = []
    for c in txt:
        if c in ENG:
            kvals.append(ENG[c])
    if len(kvals) < len(p71):
        continue
    for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29), ("BEAU", lambda c,k: (k-c)%29)]:
        dec = [mode_fn(p71[i], kvals[i]) for i in range(len(p71))]
        text = ''.join(IDX[i] for i in dec)
        sc = score_english(text)
        ic = ioc(dec)
        if sc > 15 or ic > 1.3:
            results.append(('RUNKEY %s %s' % (tname, mode_name), sc, ic, text[:60]))

# === 5. Atbash variants ===
print("\n=== ATBASH + SHIFT ===")
for sh in range(29):
    dec = [(28 - (r - sh)) % 29 for r in p71]
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    ic = ioc(dec)
    if sc > 15:
        results.append(('ATBASH+SHIFT %d' % sh, sc, ic, text[:60]))

# === 6. All Caesar shifts (for completeness) ===
for sh in range(29):
    dec = [(r - sh) % 29 for r in p71]
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    if sc > 18:
        results.append(('CAESAR %d' % sh, sc, ioc(dec), text[:60]))

# Print results sorted by score
print("\n===== RESULTS (sorted by score) =====")
results.sort(key=lambda x: -x[1])
for name, sc, ic, txt in results[:30]:
    print("%-40s score=%3d IoC=%.3f %s" % (name, sc, ic, txt))

if not results:
    print("NO results above threshold!")
    # Print best candidates for each method
    print("\nBest Caesar:")
    best = max(range(29), key=lambda sh: score_english(''.join(IDX[i] for i in [(r-sh)%29 for r in p71])))
    dec = [(r-best)%29 for r in p71]
    print("  shift %d: score=%d %s" % (best, score_english(''.join(IDX[i] for i in dec)), ''.join(IDX[i] for i in dec)[:60]))

print("\nDone.")
