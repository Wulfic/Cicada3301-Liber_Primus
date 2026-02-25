"""
P62 Deep Investigation — DIVINITY keyword shows "ALL THAT LIUES IS" at end!
This is from known Cicada text: "EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY"

Strategy:
1. Verify DIVINITY + SUB exact output
2. Try shifting the key alignment 
3. Try partial key variants
4. Try autokey, running key, progressive modes
5. Compare with known plaintext to find exact key
"""
import os, sys
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

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    runes = [c for c in raw if c in GP]
    vals = [GP[c] for c in runes]
    return vals, runes, raw

# Load P62
cipher, runes, raw = load_page(62)
N = len(cipher)
print(f"P62: {N} runes")
print(f"Raw text preview: {raw[:200]}")
print(f"Cipher values: {cipher[:30]}...")

# DIVINITY keyword
div_gp = eng_to_gp("DIVINITY")
print(f"\nDIVINITY GP: {div_gp} = {gp_to_lat(div_gp)}")
print(f"DIVINITY key length: {len(div_gp)}")

# ===== BASIC DECRYPTION =====
print("\n" + "="*80)
print("BASIC DECRYPTION WITH DIVINITY")
print("="*80)

for mode in ['SUB', 'ADD', 'BEAU']:
    dec = []
    for i in range(N):
        k = div_gp[i % len(div_gp)]
        if mode == 'SUB': dec.append((cipher[i]-k)%MOD)
        elif mode == 'ADD': dec.append((cipher[i]+k)%MOD)
        elif mode == 'BEAU': dec.append((k-cipher[i])%MOD)
    text = gp_to_lat(dec)
    print(f"\n{mode}: {text}")
    # Show word-by-word
    words = []
    for j in range(0, N, 8):
        chunk = dec[j:min(j+8, N)]
        words.append(gp_to_lat(chunk))
    print(f"  Chunked (8): {' | '.join(words)}")

# ===== KEY OFFSET TESTING =====
print("\n" + "="*80)
print("KEY OFFSET TESTING (shift start position)")
print("="*80)

for offset in range(8):
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = []
        for i in range(N):
            k = div_gp[(i + offset) % len(div_gp)]
            if mode == 'SUB': dec.append((cipher[i]-k)%MOD)
            elif mode == 'ADD': dec.append((cipher[i]+k)%MOD)
            elif mode == 'BEAU': dec.append((k-cipher[i])%MOD)
        text = gp_to_lat(dec)
        # Check for English fragments
        english_count = 0
        for word in ['THE','AND','THAT','WITH','FOR','ALL','ARE','YOU','NOT','BUT','FROM','THIS','WHICH','HAVE','BEING','WITHIN','HOLY','LIVES','EACH','INTELLIGENCE','DIVINITY','SACRED','WISDOM','TRUTH']:
            if word in text:
                english_count += 1
        if english_count >= 3:
            print(f"  offset={offset} {mode}: [{english_count} hits] {text[:120]}")

# ===== AUTOKEY VARIANTS =====
print("\n" + "="*80) 
print("AUTOKEY VARIANTS WITH DIVINITY PRIMER")
print("="*80)

# Autokey (plaintext feedback)
for mode in ['SUB', 'ADD']:
    kl = len(div_gp)
    dec = []
    key_stream = list(div_gp)  # Start with DIVINITY
    for i in range(N):
        k = key_stream[i]
        if mode == 'SUB': 
            p = (cipher[i]-k)%MOD
        else:
            p = (cipher[i]+k)%MOD
        dec.append(p)
        key_stream.append(p)  # Autokey: feed back plaintext
    text = gp_to_lat(dec)
    print(f"Autokey-{mode}: {text[:120]}")
    
# Autokey (ciphertext feedback)
for mode in ['SUB', 'ADD']:
    kl = len(div_gp)
    dec = []
    key_stream = list(div_gp)
    for i in range(N):
        k = key_stream[i]
        if mode == 'SUB':
            p = (cipher[i]-k)%MOD
        else:
            p = (cipher[i]+k)%MOD
        dec.append(p)
        key_stream.append(cipher[i])  # Feed back ciphertext
    text = gp_to_lat(dec)
    print(f"CipherFB-{mode}: {text[:120]}")

# Progressive key
for mode in ['SUB', 'ADD']:
    dec = []
    for i in range(N):
        k = (div_gp[i % len(div_gp)] + i // len(div_gp)) % MOD
        if mode == 'SUB':
            p = (cipher[i]-k)%MOD
        else:
            p = (cipher[i]+k)%MOD
        dec.append(p)
    text = gp_to_lat(dec)
    print(f"Progressive-{mode}: {text[:120]}")

# ===== REVERSE ENGINEERING FROM KNOWN PLAINTEXT =====
print("\n" + "="*80)
print("REVERSE ENGINEERING - if end is 'ALLTHATLIUESISHOLY'")
print("="*80)

# Known plaintext for the end
known_texts = [
    "ALLTHATLIVESISHOLY",
    "EACHINTELLIGENCEISHOLYFORALLTHATLIVESISHOLY",
    "WISDOMYOUAREABEINGUNTOYOURSELFYOUAREALAWUNTOYOURSELFEACHINTELLIGENCEISHOLYFORALLTHATLIVESISHOLY",
    "FORALLTHATLIVESISHOLY",
]

for known in known_texts:
    kp_gp = eng_to_gp(known)
    kp_len = len(kp_gp)
    if kp_len > N: continue
    
    start = N - kp_len
    print(f"\nKnown text: '{known}' ({kp_len} GP values, starts at pos {start})")
    
    for mode in ['SUB', 'ADD', 'BEAU']:
        key_recovered = []
        for i in range(kp_len):
            ci = cipher[start + i]
            pi = kp_gp[i]
            if mode == 'SUB':
                # p = (c - k) % 29 → k = (c - p) % 29
                k = (ci - pi) % MOD
            elif mode == 'ADD':
                # p = (c + k) % 29 → k = (p - c) % 29
                k = (pi - ci) % MOD
            elif mode == 'BEAU':
                # p = (k - c) % 29 → k = (p + c) % 29
                k = (pi + ci) % MOD
            key_recovered.append(k)
        
        # Check if key is periodic with DIVINITY
        key_lat = gp_to_lat(key_recovered)
        
        # Check periodicity
        is_periodic = True
        period = None
        for p in range(1, kp_len):
            periodic = True
            for j in range(p, kp_len):
                if key_recovered[j] != key_recovered[j % p]:
                    periodic = False
                    break
            if periodic:
                period = p
                break
        
        # Check if it matches DIVINITY with any offset
        div_match = False
        for off in range(8):
            match = True
            for j in range(kp_len):
                if key_recovered[j] != div_gp[(j + off) % 8]:
                    match = False
                    break
            if match:
                div_match = True
                print(f"  {mode}: KEY MATCHES DIVINITY offset={off}!")
                break
        
        # Check if CONSTANT key
        if len(set(key_recovered)) == 1:
            print(f"  {mode}: CONSTANT KEY = {key_recovered[0]} ({LAT[key_recovered[0]]})")
        elif period and period <= 15:
            print(f"  {mode}: PERIODIC key period={period}, key={gp_to_lat(key_recovered[:period])}")
        elif not div_match:
            # Show key pattern
            print(f"  {mode}: key={key_lat[:60]}...")
            # Check mod-8 pattern
            for off in range(8):
                cols = [key_recovered[j] for j in range(off, kp_len, 8)]
                if len(set(cols)) == 1:
                    pass  # Don't spam
            # Check if key is sequential
            diffs = [(key_recovered[i+1] - key_recovered[i]) % MOD for i in range(kp_len-1)]
            if len(set(diffs)) == 1:
                print(f"    Sequential! diff={diffs[0]}")

# ===== SEARCH FOR BEST PARTIAL ALIGNMENT =====
print("\n" + "="*80)
print("SEARCH FOR PARTIAL KEY MATCH WITH DIVINITY")
print("="*80)

# For each position, try the text being from known Cicada pages
# and see if the key aligns with DIVINITY

# Try a broader approach: for each of the 3 modes, and for each possible
# start position of the known text at the end, reverse-engineer the key
# and check how many positions match DIVINITY (with any offset)

best_matches = []
for mode in ['SUB', 'ADD', 'BEAU']:
    for known in ["WISDOMYOUAREABEINGUNTOYOURSELFYOUAREALAWUNTOYOURSELFEACHINTELLIGENCEISHOLYFORALLTHATLIVESISHOLY"]:
        kp_gp = eng_to_gp(known)
        if len(kp_gp) > N: continue
        
        start = N - len(kp_gp)
        key_recovered = []
        for i in range(len(kp_gp)):
            ci = cipher[start + i]
            pi = kp_gp[i]
            if mode == 'SUB': k = (ci - pi) % MOD
            elif mode == 'ADD': k = (pi - ci) % MOD
            elif mode == 'BEAU': k = (pi + ci) % MOD
            key_recovered.append(k)
        
        # Check DIVINITY match rate for each offset
        for off in range(8):
            matches = sum(1 for j in range(len(kp_gp)) if key_recovered[j] == div_gp[(start + j + off) % 8])
            rate = matches / len(kp_gp) * 100
            if rate > 30:
                print(f"  {mode} offset={off}: {matches}/{len(kp_gp)} ({rate:.1f}%) match DIVINITY")
                # Show which positions match
                mismatches = [(j, key_recovered[j], div_gp[(start+j+off)%8]) for j in range(len(kp_gp)) if key_recovered[j] != div_gp[(start+j+off)%8]]
                if len(mismatches) < 20:
                    print(f"    Mismatches: {mismatches[:15]}")

# ===== COLUMN-BY-COLUMN DEEP ANALYSIS =====
print("\n" + "="*80)
print("COLUMN-BY-COLUMN ANALYSIS (period 8 = DIVINITY length)")
print("="*80)

# IoC for period 8
columns = [[] for _ in range(8)]
for i, v in enumerate(cipher):
    columns[i%8].append(v)

for b in range(8):
    col = columns[b]
    n = len(col)
    counts = Counter(col)
    ioc = sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * MOD if n > 1 else 0
    
    # Try each key value and compute decrypted IoC
    best_sub = max(range(MOD), key=lambda k: sum(((v-k)%MOD == e) for v in col for e in [0,2,3,4,8,9,10,15,16,18,20,24]))
    best_add = max(range(MOD), key=lambda k: sum(((v+k)%MOD == e) for v in col for e in [0,2,3,4,8,9,10,15,16,18,20,24]))
    
    print(f"  Col {b} ({LAT[div_gp[b]]}): n={n}, IoC*29={ioc:.2f}, counts={dict(counts)}")
    
    # For SUB mode with DIVINITY key value
    dec_div = [(v - div_gp[b]) % MOD for v in col]
    dec_lat = ''.join(LAT[v] for v in dec_div)
    print(f"    DIVINITY-SUB decrypt: {dec_lat} (vals: {dec_div})")

# ===== TRY TOTIENT CIPHER =====
print("\n" + "="*80)
print("TOTIENT CIPHER TEST")
print("="*80)

def euler_totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

primes = primes_up_to(10000)

# Try various offsets into the prime sequence
for start_idx in range(0, 200, 10):
    dec = []
    for i in range(N):
        p = primes[start_idx + i]
        t = euler_totient(p) % MOD  # totient(prime) = prime-1
        dec.append((cipher[i] - t) % MOD)
    text = gp_to_lat(dec)
    # Check for English words
    hits = sum(1 for w in ['THE','AND','WITH','FOR','ALL','YOU','NOT','THIS','THAT'] if w in text)
    if hits >= 2:
        print(f"  Totient offset={start_idx}: [{hits} hits] {text[:80]}")

# F-skip totient
print("\n  F-skip totient:")
for start_idx in range(0, 200, 10):
    dec = []
    pi = start_idx
    for i in range(N):
        if cipher[i] == 0:  # F rune
            dec.append(0)
        else:
            p = primes[pi]
            t = euler_totient(p) % MOD
            dec.append((cipher[i] - t) % MOD)
            pi += 1
    text = gp_to_lat(dec)
    hits = sum(1 for w in ['THE','AND','WITH','FOR','ALL','YOU','NOT','THIS','THAT'] if w in text)
    if hits >= 2:
        print(f"  F-skip totient offset={start_idx}: [{hits} hits] {text[:80]}")

print("\n=== DONE ===")
