#!/usr/bin/env python3
"""
P18 Autokey Extension: Use first 53 known plaintext chars as key seed,
then extend using autokey to decode the rest of the 260 runes.
Also: test P18 key on P02 and vice versa.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_runes(page):
    with open(f'LiberPrimus/pages/page_{page:02d}/runes.txt','r',encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def to_runeglish(indices):
    return ''.join(IDX2LAT[i] for i in indices)

# P18 known solution
p18_key = [11, 6, 1, 20, 25, 20, 9, 15, 24, 26, 25, 7, 19, 8, 10, 24, 18, 9, 0, 16, 9, 4, 14, 22, 13, 13, 3, 28, 5, 21, 24, 19, 5, 1, 27, 14, 6, 17, 24, 24, 22, 8, 23, 6, 22, 19, 2, 11, 3, 19, 25, 15, 24]
p18_cipher = load_runes(18)
print(f"P18: {len(p18_cipher)} runes, key len: {len(p18_key)}")

# Verify first 53 runes
p18_first53 = [(p18_cipher[i] - p18_key[i]) % 29 for i in range(53)]
print(f"First 53 plaintext: {to_runeglish(p18_first53)}")
print()

# ===== Method 1: Autokey using plaintext as key extension =====
print("=" * 60)
print("METHOD 1: AUTOKEY (plaintext feeds back as key)")
print("=" * 60)

for mode in ['sub', 'add', 'beau']:
    plain = list(p18_first53)  # Known first 53
    for i in range(53, len(p18_cipher)):
        # Key at position i = plaintext at position i-53
        k = plain[i - 53]
        if mode == 'sub':
            p = (p18_cipher[i] - k) % 29
        elif mode == 'add':
            p = (p18_cipher[i] + k) % 29
        else:
            p = (k - p18_cipher[i]) % 29
        plain.append(p)
    
    text = to_runeglish(plain)
    print(f"\n{mode.upper()}: {text}")

# ===== Method 2: Autokey using CIPHERTEXT as key extension =====
print("\n" + "=" * 60)
print("METHOD 2: AUTOKEY (ciphertext feeds back as key)")
print("=" * 60)

for mode in ['sub', 'add', 'beau']:
    plain = list(p18_first53)  # Known first 53
    for i in range(53, len(p18_cipher)):
        k = p18_cipher[i - 53]
        if mode == 'sub':
            p = (p18_cipher[i] - k) % 29
        elif mode == 'add':
            p = (p18_cipher[i] + k) % 29
        else:
            p = (k - p18_cipher[i]) % 29
        plain.append(p)
    
    text = to_runeglish(plain)
    print(f"\n{mode.upper()}: {text}")

# ===== Method 3: Autokey using KEY STREAM as extension =====
print("\n" + "=" * 60)
print("METHOD 3: AUTOKEY (key itself feeds back)")
print("=" * 60)

for mode in ['sub', 'add', 'beau']:
    key_stream = list(p18_key)
    plain = list(p18_first53)
    for i in range(53, len(p18_cipher)):
        # Extend key using previously computed key values
        k = key_stream[i - 53]  # Hmm, that's the same as repeating
        # Actually try: key extends by past plaintext values
        pass
    
    # Try: key = original_key || plaintext[0:] || plaintext[53:] etc.
    key_extended = list(p18_key) + list(p18_first53)  # 53+53=106
    while len(key_extended) < len(p18_cipher):
        # Use what we've decoded so far
        next_batch = []
        start = len(key_extended) - 53
        for i in range(53):
            if start + i < len(key_extended):
                next_batch.append(key_extended[start + i])
        key_extended.extend(next_batch)
    
    if mode == 'sub':
        plain_ext = [(p18_cipher[i] - key_extended[i]) % 29 for i in range(len(p18_cipher))]
    elif mode == 'add':
        plain_ext = [(p18_cipher[i] + key_extended[i]) % 29 for i in range(len(p18_cipher))]
    else:
        plain_ext = [(key_extended[i] - p18_cipher[i]) % 29 for i in range(len(p18_cipher))]
    
    text = to_runeglish(plain_ext)
    print(f"\n{mode.upper()} (key+plain extend): {text}")

# ===== Method 4: Progressive key (shift key by constants) =====
print("\n" + "=" * 60)
print("METHOD 4: PROGRESSIVE KEY (key shifts each cycle)")
print("=" * 60)

for step in range(1, 29):
    key_prog = list(p18_key)
    for cycle in range(1, 10):
        shifted = [(k + cycle * step) % 29 for k in p18_key]
        key_prog.extend(shifted)
    
    plain = [(p18_cipher[i] - key_prog[i]) % 29 for i in range(len(p18_cipher))]
    text = to_runeglish(plain)
    
    # Score the post-53 portion
    text_after53 = text[len(to_runeglish(p18_first53)):]
    score = 0
    for w in ['THE','AND','FOR','THIS','THAT','SOME','SACRED','ALL','NOT','YOU',
              'BEING','WITHIN','TRUTH','SELF','THINGS','WILL','MUST','SHALL',
              'ONE','ARE','WAS','WITH','ABOVE','WAY','OATH','SWORN']:
        if w in text_after53:
            score += len(w) * 3
    
    if score > 20:
        print(f"Step {step:2d}: score={score:3d}")
        print(f"  Post-53: {text_after53[:100]}")

# ===== P02 analysis =====
print("\n" + "=" * 60)
print("P02 FRESH ANALYSIS")
print("=" * 60)

p02 = load_runes(2)
print(f"P02: {len(p02)} runes")

# IoC analysis
def ioc(data):
    N = len(data)
    if N < 2: return 0
    freq = [0]*29
    for d in data: freq[d] += 1
    return 29 * sum(f*(f-1) for f in freq) / (N*(N-1))

print(f"Raw IoC*29: {ioc(p02):.4f}")

# Periodic IoC
for period in range(1, 60):
    total = count = 0
    for col in range(period):
        column = [p02[i] for i in range(col, len(p02), period)]
        if len(column) > 1:
            total += ioc(column)
            count += 1
    avg = total/count if count else 0
    if avg > 1.3:
        print(f"  Period {period:3d}: avg IoC = {avg:.4f} ***")
    elif avg > 1.15:
        print(f"  Period {period:3d}: avg IoC = {avg:.4f} **")
    elif period <= 10 or avg > 1.05:
        print(f"  Period {period:3d}: avg IoC = {avg:.4f}")

# Try P18 plaintext as running key for P02
print("\nP18 plaintext as running key for P02:")
p18_plain_repeated = (p18_first53 * 5)[:len(p02)]
for mode in ['sub', 'add', 'beau']:
    if mode == 'sub':
        p02_dec = [(p02[i] - p18_plain_repeated[i]) % 29 for i in range(len(p02))]
    elif mode == 'add':
        p02_dec = [(p02[i] + p18_plain_repeated[i]) % 29 for i in range(len(p02))]
    else:
        p02_dec = [(p18_plain_repeated[i] - p02[i]) % 29 for i in range(len(p02))]
    text = to_runeglish(p02_dec)
    score = 0
    for w in ['THE','AND','FOR','THIS','THAT','SOME','SACRED','ALL']:
        if w in text: score += len(w) * 3
    print(f"  {mode.upper()}: score={score}, {text[:80]}")

# Try P18 KEY as key for P02
print("\nP18 key applied to P02:")
p18_key_repeated = (p18_key * 5)[:len(p02)]
for mode in ['sub', 'add', 'beau']:
    if mode == 'sub':
        p02_dec = [(p02[i] - p18_key_repeated[i]) % 29 for i in range(len(p02))]
    elif mode == 'add':
        p02_dec = [(p02[i] + p18_key_repeated[i]) % 29 for i in range(len(p02))]
    else:
        p02_dec = [(p18_key_repeated[i] - p02[i]) % 29 for i in range(len(p02))]
    text = to_runeglish(p02_dec)
    score = 0
    for w in ['THE','AND','FOR','THIS','THAT','SOME','SACRED','ALL','CHAPTER','INTUS']:
        if w in text: score += len(w) * 3
    if score > 0:
        print(f"  {mode.upper()}: score={score}, {text[:80]}")

print("\nDone.")
