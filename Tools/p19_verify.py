"""
P19 Full Solution Verification
Check if the repeating key fully decrypts the page.
"""
import os
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

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    words, current, start, pos = [], [], 0, 0
    for c in raw:
        if c in GP:
            if not current: start = pos
            current.append(GP[c]); pos += 1
        elif current:
            words.append((start, list(current))); current = []
    if current: words.append((start, list(current)))
    return runes, words, raw

cipher, words, raw = load_page(19)
N = len(cipher)
print(f"P19: {N} runes, {len(words)} words")
print(f"Word lengths: {[len(w) for _,w in words]}")

# IoC analysis for various key lengths
print(f"\nIoC analysis:")
for kl in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,86]:
    if kl > N: break
    cols = [[] for _ in range(kl)]
    for i in range(N): cols[i%kl].append(cipher[i])
    iocs = []
    for col in cols:
        if len(col) < 2: continue
        freq = Counter(col)
        ioc = sum(c*(c-1) for c in freq.values()) / (len(col)*(len(col)-1)) * MOD
        iocs.append(ioc)
    avg_ioc = sum(iocs)/len(iocs) if iocs else 0
    min_vals = min(len(col) for col in cols) if cols else 0
    max_vals = max(len(col) for col in cols) if cols else 0
    print(f"  kl={kl:3d}: IoC*29={avg_ioc:.3f} (vals/col: {min_vals}-{max_vals})")

# Key from SOLUTION.md (47 values)
key47 = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23, 28, 28, 28, 28]

# Key from conversation summary (43 values)
key43 = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

# Test both key lengths with ADD mode: plain = (cipher + key) % 29
for desc, key in [("Key len 43 (ADD)", key43), ("Key len 47 (ADD)", key47)]:
    klen = len(key)
    print(f"\n{'='*80}")
    print(f"{desc}")
    print(f"{'='*80}")
    
    dec = [(cipher[i] + key[i % klen]) % MOD for i in range(N)]
    full_text = ''.join(LAT[v] for v in dec)
    
    # Show word by word
    print(f"Text: {full_text[:200]}")
    print(f"\nWords:")
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals)
        print(f"  w{wi:2d} (pos {start:3d}-{start+len(wrunes)-1:3d}): '{txt}'")
    
    # IoC of decoded text
    counts = Counter(dec)
    ioc = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
    print(f"\nFull IoC*29: {ioc:.3f}")
    
    # Check second half separately
    if N > klen:
        second_half = dec[klen:]
        counts2 = Counter(second_half)
        if len(second_half) > 1:
            ioc2 = sum(c*(c-1) for c in counts2.values()) / (len(second_half)*(len(second_half)-1)) * MOD
            print(f"Second half IoC*29 (pos {klen}+): {ioc2:.3f}")
            text2 = ''.join(LAT[v] for v in second_half)
            print(f"Second half text: {text2}")

# Also try SUB mode
for desc, key in [("Key len 43 (SUB)", key43)]:
    klen = len(key)
    print(f"\n{'='*80}")  
    print(f"{desc}")
    print(f"{'='*80}")
    
    dec = [(cipher[i] - key[i % klen]) % MOD for i in range(N)]
    full_text = ''.join(LAT[v] for v in dec)
    
    print(f"Text: {full_text[:200]}")
    print(f"\nWords:")
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals)
        print(f"  w{wi:2d} (pos {start:3d}-{start+len(wrunes)-1:3d}): '{txt}'")

# Try autokey with key43 as primer
print(f"\n{'='*80}")
print(f"Autokey ADD with 43-rune primer")
print(f"{'='*80}")

dec_ak = [0] * N
for i in range(N):
    if i < 43:
        dec_ak[i] = (cipher[i] + key43[i]) % MOD
    else:
        dec_ak[i] = (cipher[i] + dec_ak[i - 43]) % MOD

text_ak = ''.join(LAT[v] for v in dec_ak)
print(f"Text: {text_ak}")
print(f"\nWords:")
for wi, (start, wrunes) in enumerate(words):
    vals = dec_ak[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    print(f"  w{wi:2d} (pos {start:3d}-{start+len(wrunes)-1:3d}): '{txt}'")

# IoC of second half
counts_ak2 = Counter(dec_ak[43:])
if len(dec_ak[43:]) > 1:
    ioc_ak2 = sum(c*(c-1) for c in counts_ak2.values()) / (len(dec_ak[43:])*(len(dec_ak[43:])-1)) * MOD
    print(f"Second half IoC*29: {ioc_ak2:.3f}")

print(f"\n=== DONE ===")
