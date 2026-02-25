"""
P54 — Test autokey and totient cipher hypotheses.
76 runes, IoC*29=2.008 at kl=13 but NOT simple repeating Vigenère.

Autokey: key = keyword_primer + plaintext feedback
Totient: (cipher - totient(prime[idx])) % 29 with F-skip (proven for P55/P73)
"""
import os, sys, math, random
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

def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

primes = primes_up_to(20000)

with open('LiberPrimus/pages/page_54/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"P54: {N} runes")

# Score function
def score_text(dec):
    text = gp_to_lat(dec)
    s = 0
    for w in ['THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS','WHICH','ARE',
              'WITHIN','HOLY','LIVES','EACH','BEING','UNTO','YOURSELF','WEB','PAGE',
              'DEEP','HASHES','EXISTS','END','WISDOM','DIVINITY','INSTRUCTION',
              'TRUTH','SACRED','LOSS','BELIEVE','NOTHING','FIND','SELF','OWN',
              'DEATH','INTELLIGENCE','LAW','COMMAND','MASTER','PILGRIM','DUTY',
              'EVERY','SEEK','CONSUME','ENOUGH','FOLLOW','DOGMA','BELONG',
              'PRESERVE','WEAK','KNOWLEDGE','EXPERIENCE','CIRCUMFERENCE','INSTAR']:
        s += text.count(w) * len(w)
    return s, text

# ===== TOTIENT CIPHER (P55/P73 style) =====
print("="*80)
print("TOTIENT CIPHER TEST")
print("="*80)

# Standard totient: dec[i] = (cipher[i] - (prime[offset+idx]-1)) % 29
# With F-skip: F runes pass through, key doesn't advance

for start_idx in range(0, 5000, 1):
    # Without F-skip
    dec = []
    for i in range(N):
        p = primes[start_idx + i]
        t = (p - 1) % MOD
        dec.append((cipher[i] - t) % MOD)
    sc, text = score_text(dec)
    if sc >= 15:
        print(f"  No F-skip offset={start_idx}: score={sc} text={text[:80]}")
    
    # With F-skip
    dec_fs = []
    pi = start_idx
    for i in range(N):
        if cipher[i] == 0:  # F rune
            dec_fs.append(0)
        else:
            p = primes[pi]
            t = (p - 1) % MOD
            dec_fs.append((cipher[i] - t) % MOD)
            pi += 1
    sc_fs, text_fs = score_text(dec_fs)
    if sc_fs >= 15:
        print(f"  F-skip offset={start_idx}: score={sc_fs} text={text_fs[:80]}")

    # Also try ADD mode
    dec_add = []
    for i in range(N):
        p = primes[start_idx + i]
        t = (p - 1) % MOD
        dec_add.append((cipher[i] + t) % MOD)
    sc_add, text_add = score_text(dec_add)
    if sc_add >= 15:
        print(f"  No F-skip ADD offset={start_idx}: score={sc_add} text={text_add[:80]}")

print("Totient scan done (0-4999)")

# ===== AUTOKEY CIPHER =====
print("\n" + "="*80)
print("AUTOKEY CIPHER TEST")
print("="*80)

# Autokey with plaintext feedback:
# For i < kl: p[i] = (c[i] - primer[i]) % 29
# For i >= kl: p[i] = (c[i] - p[i-kl]) % 29

# Try various primers (Cicada keywords) with various key lengths
primers = {
    "DIVINITY": eng_to_gp("DIVINITY"),  # len 8
    "SACRED": eng_to_gp("SACRED"),  # len 6
    "PILGRIM": eng_to_gp("PILGRIM"),  # len 7
    "PRIMUS": eng_to_gp("PRIMUS"),  # len 6
    "WISDOM": eng_to_gp("WISDOM"),  # len 6
    "TRUTH": eng_to_gp("TRUTH"),  # len 4 (with TH)
    "INSTAR": eng_to_gp("INSTAR"),  # len 6
    "CIRCUMFERENCE": eng_to_gp("CIRCUMFERENCE"),  # len 13
    "INTUS": eng_to_gp("INTUS"),  # len 5
    "LIBER": eng_to_gp("LIBER"),  # len 5
    "CABAL": eng_to_gp("CABAL"),  # len 5
    "CONSUMPTION": eng_to_gp("CONSUMPTION"),  # len 11
    "PRESERVATION": eng_to_gp("PRESERVATION"),  # len 12
    "ADHERENCE": eng_to_gp("ADHERENCE"),  # len 9
    "DECEPTION": eng_to_gp("DECEPTION"),  # len 9
    "EMERGENCE": eng_to_gp("EMERGENCE"),  # len 9
}

for name, primer in primers.items():
    kl = len(primer)
    
    # Autokey SUB (plaintext feedback)
    dec = [0] * N
    for i in range(N):
        if i < kl:
            k = primer[i]
        else:
            k = dec[i - kl]
        dec[i] = (cipher[i] - k) % MOD
    sc, text = score_text(dec)
    if sc >= 10:
        print(f"  Autokey-SUB {name:15s} (kl={kl:2d}): score={sc:3d} text={text[:80]}")
    
    # Autokey ADD (plaintext feedback)
    dec = [0] * N
    for i in range(N):
        if i < kl:
            k = primer[i]
        else:
            k = dec[i - kl]
        dec[i] = (cipher[i] + k) % MOD
    sc, text = score_text(dec)
    if sc >= 10:
        print(f"  Autokey-ADD {name:15s} (kl={kl:2d}): score={sc:3d} text={text[:80]}")
    
    # Autokey BEAU (plaintext feedback)
    dec = [0] * N
    for i in range(N):
        if i < kl:
            k = primer[i]
        else:
            k = dec[i - kl]
        dec[i] = (k - cipher[i]) % MOD
    sc, text = score_text(dec)
    if sc >= 10:
        print(f"  Autokey-BEAU {name:15s} (kl={kl:2d}): score={sc:3d} text={text[:80]}")
    
    # Ciphertext-feedback autokey
    for mode_name, mode_fn in [('CipherFB-SUB', lambda c,k: (c-k)%MOD), ('CipherFB-ADD', lambda c,k: (c+k)%MOD)]:
        dec = [0] * N
        for i in range(N):
            if i < kl:
                k = primer[i]
            else:
                k = cipher[i - kl]
            dec[i] = mode_fn(cipher[i], k)
        sc, text = score_text(dec)
        if sc >= 10:
            print(f"  {mode_name} {name:15s} (kl={kl:2d}): score={sc:3d} text={text[:80]}")

# ===== BRUTE FORCE AUTOKEY =====
print("\n" + "="*80)
print("BRUTE FORCE AUTOKEY (kl=1 to 5)")
print("="*80)

# For short key lengths, brute force all possible primers
for kl in range(1, 6):
    best_sc = 0
    best_text = ""
    best_key = None
    best_mode = ""
    
    # For kl=1: 29 options, kl=2: 29^2=841, kl=3: 29^3=24389, kl=4: too many
    if 29**kl > 50000:
        print(f"  kl={kl}: too many ({29**kl}), skipping brute force")
        continue
    
    for key_val in range(29**kl):
        primer = []
        v = key_val
        for _ in range(kl):
            primer.append(v % MOD)
            v //= MOD
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = [0] * N
            for i in range(N):
                if i < kl:
                    k = primer[i]
                else:
                    k = dec[i - kl]
                if mode == 'SUB': dec[i] = (cipher[i] - k) % MOD
                elif mode == 'ADD': dec[i] = (cipher[i] + k) % MOD
                elif mode == 'BEAU': dec[i] = (k - cipher[i]) % MOD
            
            sc, text = score_text(dec)
            if sc > best_sc:
                best_sc = sc
                best_text = text
                best_key = list(primer)
                best_mode = mode
    
    if best_sc > 0:
        print(f"  kl={kl}: best score={best_sc} {best_mode} key={best_key} ({gp_to_lat(best_key)}) text={best_text[:80]}")

# ===== Try with separator-aware key advancement =====
print("\n" + "="*80)
print("SEPARATOR-AWARE VIGENERE (key advances on separators too)")
print("="*80)

# If dashes in the ORIGINAL text advance the key, the effective key period on runes only
# would be different from 13
chars = []
for c in raw:
    if c in GP: chars.append(('R', GP[c]))
    elif c == '-': chars.append(('D', -1))
    elif c == '\n': chars.append(('N', -2))
    elif c == '.': chars.append(('P', -3))

# Try key on ALL characters (dashes advance key)
for kl in [13]:
    for mode in ['SUB', 'ADD', 'BEAU']:
        for skip_types in [('D',), ('N',), ('D','N'), ('D','N','P')]:
            for init_off in range(kl):
                key_idx = init_off
                dec = []
                for t, v in chars:
                    if t == 'R':
                        # Frequency analysis: try all keys for this column
                        k_col = key_idx % kl
                        if mode == 'SUB': dec.append((v - 0) % MOD)  # Will fill later
                        elif mode == 'ADD': dec.append((v + 0) % MOD)
                        elif mode == 'BEAU': dec.append((0 - v) % MOD)
                        key_idx += 1
                    elif t[0] in skip_types:
                        key_idx += 1
                
                # Actually easier: just try it with frequency-based key finding
                # For this, I need to build columns with skip-aware indexing
                columns = [[] for _ in range(kl)]
                key_idx = init_off
                for t, v in chars:
                    if t == 'R':
                        columns[key_idx % kl].append(v)
                        key_idx += 1
                    elif t[0] in skip_types:
                        key_idx += 1
                
                # Check IoC of columns
                avg_ioc = 0
                for col in columns:
                    if len(col) < 2: continue
                    counts = Counter(col)
                    ioc = sum(c*(c-1) for c in counts.values()) / (len(col) * (len(col)-1)) * MOD
                    avg_ioc += ioc
                avg_ioc /= kl
                
                if avg_ioc > 1.5:
                    print(f"  kl={kl} skip={''.join(skip_types)} off={init_off}: avg IoC*29={avg_ioc:.3f}")

print("\n=== DONE ===")
