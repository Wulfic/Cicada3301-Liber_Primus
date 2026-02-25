"""
P54 — Focused investigation of totient cipher and autokey.
Totient hit at offset 889 (F-skip) showing WITH...DEATH.
"""
import os, math
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

primes = primes_up_to(100000)

with open('LiberPrimus/pages/page_54/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"P54: {N} runes, cipher[:10]={cipher[:10]}")

# Count F runes
f_count = sum(1 for c in cipher if c == 0)
print(f"F runes (val 0): {f_count} at positions {[i for i in range(N) if cipher[i]==0]}")

def score_text(dec):
    text = gp_to_lat(dec)
    s = 0
    for w in ['THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS','WHICH','ARE',
              'WITHIN','HOLY','LIVES','EACH','BEING','UNTO','YOURSELF','WEB','PAGE',
              'DEEP','HASHES','EXISTS','END','WISDOM','DIVINITY','INSTRUCTION',
              'TRUTH','SACRED','LOSS','BELIEVE','NOTHING','FIND','SELF','OWN',
              'DEATH','INTELLIGENCE','LAW','COMMAND','MASTER','PILGRIM','DUTY',
              'EVERY','SEEK','CONSUME','ENOUGH','FOLLOW','DOGMA','BELONG',
              'PRESERVE','WEAK','KNOWLEDGE','EXPERIENCE','CIRCUMFERENCE','INSTAR',
              'TEST','YOUR','BOOK','EXCEPT','WHAT','KNOW','TRUE']:
        s += text.count(w) * len(w)
    return s, text

# ===== DETAILED TOTIENT SCAN =====
print("\n" + "="*80)
print("TOTIENT SCAN (offsets 0 - 10000)")
print("="*80)

best_results = []

for start_idx in range(min(10000, len(primes) - N - 1)):
    # F-skip SUB
    dec_fs = []
    pi = start_idx
    for i in range(N):
        if cipher[i] == 0:
            dec_fs.append(0)
        else:
            if pi >= len(primes):
                break
            p = primes[pi]
            t = (p - 1) % MOD
            dec_fs.append((cipher[i] - t) % MOD)
            pi += 1
    else:
        sc, text = score_text(dec_fs)
        if sc >= 10:
            best_results.append((sc, start_idx, 'F-skip-SUB', text))
    
    # No F-skip SUB
    if start_idx + N <= len(primes):
        dec = []
        for i in range(N):
            p = primes[start_idx + i]
            t = (p - 1) % MOD
            dec.append((cipher[i] - t) % MOD)
        sc, text = score_text(dec)
        if sc >= 10:
            best_results.append((sc, start_idx, 'no-skip-SUB', text))
    
    # F-skip ADD
    dec_fa = []
    pi = start_idx
    for i in range(N):
        if cipher[i] == 0:
            dec_fa.append(0)
        else:
            if pi >= len(primes):
                break
            p = primes[pi]
            t = (p - 1) % MOD
            dec_fa.append((cipher[i] + t) % MOD)
            pi += 1
    else:
        sc, text = score_text(dec_fa)
        if sc >= 10:
            best_results.append((sc, start_idx, 'F-skip-ADD', text))

best_results.sort(reverse=True)
print(f"\nTop 20 totient results:")
for sc, idx, mode, text in best_results[:20]:
    print(f"  score={sc:3d} offset={idx:5d} {mode:15s}: {text[:100]}")

# ===== AUTOKEY CIPHER TESTING =====
print("\n" + "="*80)
print("AUTOKEY CIPHER (keyword primers)")
print("="*80)

primers = {
    "DIVINITY": eng_to_gp("DIVINITY"),
    "SACRED": eng_to_gp("SACRED"),
    "PILGRIM": eng_to_gp("PILGRIM"),
    "PRIMUS": eng_to_gp("PRIMUS"),
    "WISDOM": eng_to_gp("WISDOM"),
    "TRUTH": eng_to_gp("TRUTH"),
    "INSTAR": eng_to_gp("INSTAR"),
    "CIRCUMFERENCE": eng_to_gp("CIRCUMFERENCE"),
    "INTUS": eng_to_gp("INTUS"),
    "LIBER": eng_to_gp("LIBER"),
    "CABAL": eng_to_gp("CABAL"),
    "MOBIUS": eng_to_gp("MOBIUS"),
    "FIRFUMFERENFE": eng_to_gp("FIRFUMFERENFE"),
    "END": eng_to_gp("END"),
    "DEEP": eng_to_gp("DEEP"),
    "DEOR": eng_to_gp("DEOR"),
    "CONSUMPTION": eng_to_gp("CONSUMPTION"),
    "PRESERVATION": eng_to_gp("PRESERVATION"),
    "ADHERENCE": eng_to_gp("ADHERENCE"),
    "DECEPTION": eng_to_gp("DECEPTION"),
    "EMERGENCE": eng_to_gp("EMERGENCE"),
    "SHADOW": eng_to_gp("SHADOW"),
    "TOTIENT": eng_to_gp("TOTIENT"),
    "PRIMALITY": eng_to_gp("PRIMALITY"),
}

best_autokey = []

for name, primer in primers.items():
    kl = len(primer)
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        # Autokey (plaintext feedback)
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
        if sc >= 10:
            best_autokey.append((sc, name, f'Autokey-{mode}', kl, text))
        
        # Ciphertext-feedback autokey
        dec = [0] * N
        for i in range(N):
            if i < kl:
                k = primer[i]
            else:
                k = cipher[i - kl]
            if mode == 'SUB': dec[i] = (cipher[i] - k) % MOD
            elif mode == 'ADD': dec[i] = (cipher[i] + k) % MOD
            elif mode == 'BEAU': dec[i] = (k - cipher[i]) % MOD
        
        sc, text = score_text(dec)
        if sc >= 10:
            best_autokey.append((sc, name, f'CipherFB-{mode}', kl, text))

best_autokey.sort(reverse=True)
print(f"\nTop 20 autokey results:")
for sc, name, mode, kl, text in best_autokey[:20]:
    print(f"  score={sc:3d} {name:15s} {mode:15s} (kl={kl:2d}): {text[:100]}")

# ===== BRUTE FORCE AUTOKEY kl=1,2,3 =====
print("\n" + "="*80)
print("BRUTE FORCE AUTOKEY kl=1,2,3")
print("="*80)

for kl in range(1, 4):
    best_sc = 0
    best_text = ""
    best_key = None
    best_mode = ""
    
    total = MOD**kl
    for key_val in range(total):
        primer = []
        v = key_val
        for _ in range(kl):
            primer.append(v % MOD)
            v //= MOD
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            # Plaintext feedback
            dec = [0] * N
            for i in range(N):
                if i < kl: k = primer[i]
                else: k = dec[i - kl]
                if mode == 'SUB': dec[i] = (cipher[i] - k) % MOD
                elif mode == 'ADD': dec[i] = (cipher[i] + k) % MOD
                elif mode == 'BEAU': dec[i] = (k - cipher[i]) % MOD
            
            sc, text = score_text(dec)
            if sc > best_sc:
                best_sc = sc
                best_text = text
                best_key = list(primer)
                best_mode = f'PtFB-{mode}'
            
            # Ciphertext feedback
            dec = [0] * N
            for i in range(N):
                if i < kl: k = primer[i]
                else: k = cipher[i - kl]
                if mode == 'SUB': dec[i] = (cipher[i] - k) % MOD
                elif mode == 'ADD': dec[i] = (cipher[i] + k) % MOD
                elif mode == 'BEAU': dec[i] = (k - cipher[i]) % MOD
            
            sc, text = score_text(dec)
            if sc > best_sc:
                best_sc = sc
                best_text = text
                best_key = list(primer)
                best_mode = f'CtFB-{mode}'
    
    if best_sc > 0:
        print(f"  kl={kl}: best={best_sc} {best_mode} key={best_key} ({gp_to_lat(best_key)}) text={best_text[:80]}")

# ===== ALSO CHECK SIMPLE SHIFTS (Caesar) MORE CAREFULLY =====
print("\n" + "="*80)
print("CAESAR SHIFTS")
print("="*80)

for shift in range(MOD):
    dec = [(cipher[i] - shift) % MOD for i in range(N)]
    sc, text = score_text(dec)
    if sc >= 10:
        print(f"  shift={shift} ({LAT[shift]}): score={sc} text={text[:80]}")
    
    dec = [(cipher[i] + shift) % MOD for i in range(N)]
    sc, text = score_text(dec)
    if sc >= 10:
        print(f"  shift={shift} ADD ({LAT[shift]}): score={sc} text={text[:80]}")

# ===== ATBASH =====
print("\n=== ATBASH ===")
dec = [(MOD - 1 - cipher[i]) % MOD for i in range(N)]
sc, text = score_text(dec)
print(f"  score={sc} text={text[:80]}")

print("\n=== DONE ===")
