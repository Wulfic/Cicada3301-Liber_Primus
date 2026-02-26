"""
P54 F-skip solver - test DIVINITY key (like P61/P62)
P61: Vigenère SUB, key DIVINITY, F-skip, multi-segment offsets [0,7,5,4,2,1]
P62: Vigenère SUB, key DIVINITY, F-skip, offset 3
P54: Try all offsets and F-skip interpretations
"""
import sys, io, os
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import functools
print = functools.partial(print, flush=True)
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29

# Read cipher
with open('LiberPrimus/pages/page_54/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"P54: {N} runes")
print(f"Cipher: {cipher}")

# Find F(0) positions
f_positions = [i for i, v in enumerate(cipher) if v == 0]
print(f"F(0) rune positions: {f_positions} ({len(f_positions)} total)")

# Parse words
words = []
current = []
idx = 0
for ch in raw:
    if ch in GP:
        current.append(idx)
        idx += 1
    elif ch in '-.\n&$':
        if current:
            words.append(list(current))
            current = []
if current:
    words.append(list(current))

# DIVINITY key: D=23, I=10, V→U=1, I=10, N=9, I=10, T=16, Y=26
# Also try: IA instead of I, and other GP encodings
divinity_key = [23, 10, 1, 10, 9, 10, 16, 26]  # DIVINITY
div_klen = len(divinity_key)
print(f"\nDIVINITY key: {divinity_key} (len={div_klen})")
print(f"Key as runes: {''.join(LAT[v] for v in divinity_key)}")

def decrypt_fskip_sub(cipher, key, klen, offset=0, f_skip_set=None):
    """
    Decrypt Vigenère SUB with F-skip.
    f_skip_set: set of ciphertext positions where F(0) is a plaintext F (not encrypted)
    """
    if f_skip_set is None:
        f_skip_set = set()
    
    plain = []
    key_pos = offset % klen
    
    for i in range(len(cipher)):
        if i in f_skip_set:
            # This is a plaintext F passed through
            plain.append(0)  # F
            # Key does NOT advance
        else:
            # Normal decryption
            plain.append((cipher[i] - key[key_pos % klen]) % MOD)
            key_pos += 1
    
    return plain

def compute_ioc(vals):
    n = len(vals)
    if n < 2: return 0
    counts = Counter(vals)
    ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
    return ic * 29

def text_display(plain, words_list):
    display = []
    for wpos in words_list:
        w = ''.join(LAT[plain[i]] for i in wpos)
        display.append(w)
    return ' '.join(display)

# ============================================================
# Test all combinations: 8 offsets × 2^3 F-interpretations = 64 cases
# ============================================================
print("\n" + "=" * 70)
print("TESTING DIVINITY KEY + F-SKIP (SUB mode)")
print("=" * 70)

results = []

for offset in range(div_klen):
    for f_mask in range(2**len(f_positions)):
        # Build f_skip set
        f_skip = set()
        for bit_idx in range(len(f_positions)):
            if f_mask & (1 << bit_idx):
                f_skip.add(f_positions[bit_idx])
        
        plain = decrypt_fskip_sub(cipher, divinity_key, div_klen, offset, f_skip)
        ioc = compute_ioc(plain)
        text = text_display(plain, words)
        
        # Quick quality check: look for common English fragments
        text_flat = ''.join(LAT[v] for v in plain)
        score = 0
        for word in ['THE', 'AND', 'FOR', 'ALL', 'YOU', 'NOT', 'ARE', 'THIS',
                      'THAT', 'WITH', 'SOME', 'WHAT', 'WILL', 'WOULD', 'WISDOM',
                      'SACRED', 'TRUTH', 'KNOW', 'HOLY', 'INSTRUCTION']:
            if word in text_flat:
                score += len(word)
        
        if score > 10 or ioc > 1.5:
            results.append((score, ioc, offset, f_mask, f_skip, text))
            print(f"  offset={offset}, f_mask={f_mask:03b}, skip={f_skip}")
            print(f"    IoC={ioc:.3f}, score={score}")
            print(f"    {text[:100]}")

# Sort by score
results.sort(reverse=True)
if results:
    print(f"\nTop 5 results:")
    for score, ioc, offset, f_mask, f_skip, text in results[:5]:
        print(f"\n  Score={score}, IoC={ioc:.3f}, offset={offset}, f_skip={f_skip}")
        print(f"  {text}")
else:
    print("\nNo good results with DIVINITY key")

# ============================================================
# Also try ADD mode
# ============================================================
print("\n" + "=" * 70)
print("TESTING DIVINITY KEY + F-SKIP (ADD mode)")  
print("=" * 70)

def decrypt_fskip_add(cipher, key, klen, offset=0, f_skip_set=None):
    if f_skip_set is None:
        f_skip_set = set()
    plain = []
    key_pos = offset % klen
    for i in range(len(cipher)):
        if i in f_skip_set:
            plain.append(0)
            # Key does NOT advance
        else:
            plain.append((cipher[i] + key[key_pos % klen]) % MOD)
            key_pos += 1
    return plain

results_add = []
for offset in range(div_klen):
    for f_mask in range(2**len(f_positions)):
        f_skip = set()
        for bit_idx in range(len(f_positions)):
            if f_mask & (1 << bit_idx):
                f_skip.add(f_positions[bit_idx])
        
        plain = decrypt_fskip_add(cipher, divinity_key, div_klen, offset, f_skip)
        text_flat = ''.join(LAT[v] for v in plain)
        score = 0
        for word in ['THE', 'AND', 'FOR', 'ALL', 'YOU', 'NOT', 'ARE', 'THIS',
                      'THAT', 'WITH', 'SOME', 'WHAT', 'WILL', 'WOULD', 'WISDOM',
                      'SACRED', 'TRUTH', 'KNOW', 'HOLY', 'INSTRUCTION']:
            if word in text_flat:
                score += len(word)
        
        if score > 10:
            ioc = compute_ioc(plain)
            results_add.append((score, ioc, offset, f_mask, f_skip, text_display(plain, words)))
            print(f"  offset={offset}, f_mask={f_mask:03b}, IoC={ioc:.3f}, score={score}")
            print(f"    {text_display(plain, words)[:100]}")

results_add.sort(reverse=True)
if results_add:
    print(f"\nTop 5 ADD results:")
    for score, ioc, offset, f_mask, f_skip, text in results_add[:5]:
        print(f"\n  Score={score}, IoC={ioc:.3f}, offset={offset}")
        print(f"  {text}")

# ============================================================
# Try Beaufort mode too
# ============================================================
print("\n" + "=" * 70)
print("TESTING DIVINITY KEY + F-SKIP (Beaufort mode)")
print("=" * 70)

def decrypt_fskip_beau(cipher, key, klen, offset=0, f_skip_set=None):
    if f_skip_set is None:
        f_skip_set = set()
    plain = []
    key_pos = offset % klen
    for i in range(len(cipher)):
        if i in f_skip_set:
            plain.append(0)
        else:
            plain.append((key[key_pos % klen] - cipher[i]) % MOD)
            key_pos += 1
    return plain

for offset in range(div_klen):
    for f_mask in range(2**len(f_positions)):
        f_skip = set()
        for bit_idx in range(len(f_positions)):
            if f_mask & (1 << bit_idx):
                f_skip.add(f_positions[bit_idx])
        
        plain = decrypt_fskip_beau(cipher, divinity_key, div_klen, offset, f_skip)
        text_flat = ''.join(LAT[v] for v in plain)
        score = 0
        for word in ['THE', 'AND', 'FOR', 'ALL', 'YOU', 'NOT', 'ARE', 'THIS',
                      'THAT', 'WITH', 'SOME', 'WHAT', 'WILL', 'WOULD', 'WISDOM',
                      'SACRED', 'TRUTH', 'KNOW', 'HOLY', 'INSTRUCTION']:
            if word in text_flat:
                score += len(word)
        
        if score > 10:
            ioc = compute_ioc(plain)
            print(f"  offset={offset}, f_mask={f_mask:03b}, IoC={ioc:.3f}, score={score}")
            print(f"    {text_display(plain, words)[:100]}")

# ============================================================
# Try WITHOUT F-skip, just Vigenère SUB/ADD/Beaufort with DIVINITY key
# ============================================================
print("\n" + "=" * 70)
print("TESTING DIVINITY KEY WITHOUT F-SKIP")
print("=" * 70)

for offset in range(div_klen):
    for mode_name, dec_fn in [('SUB', lambda c,k,kl,o: [(c[i]-k[(i+o)%kl])%MOD for i in range(len(c))]),
                               ('ADD', lambda c,k,kl,o: [(c[i]+k[(i+o)%kl])%MOD for i in range(len(c))]),
                               ('BEAU', lambda c,k,kl,o: [(k[(i+o)%kl]-c[i])%MOD for i in range(len(c))])]:
        plain = dec_fn(cipher, divinity_key, div_klen, offset)
        text = text_display(plain, words)
        text_flat = ''.join(LAT[v] for v in plain)
        score = 0
        for word in ['THE', 'AND', 'FOR', 'ALL', 'YOU', 'NOT', 'ARE', 'THIS',
                      'THAT', 'WITH', 'SOME', 'WHAT', 'WILL', 'WOULD', 'WISDOM',
                      'SACRED', 'TRUTH', 'KNOW', 'HOLY', 'INSTRUCTION']:
            if word in text_flat:
                score += len(word)
        ioc = compute_ioc(plain)
        if score > 8 or ioc > 1.5:
            print(f"  {mode_name} offset={offset}: IoC={ioc:.3f}, score={score}")
            print(f"    {text[:100]}")

# ============================================================
# Try other known LP keys
# ============================================================
print("\n" + "=" * 70)
print("TESTING OTHER LP KEYS")
print("=" * 70)

# Known LP keywords from solved pages
test_keys = {
    'DIVINITY': [23, 10, 1, 10, 9, 10, 16, 26],
    'FIRENZE': [0, 10, 4, 18, 9, 15, 18],  # F=0, I=10, R=4, E=18, N=9, Z→S=15, E=18... wait
    'PRIMUS': [13, 4, 10, 19, 1, 15],
    'LIBER': [20, 10, 17, 18, 4],
    'INSTAR': [10, 9, 15, 16, 24, 4],
    'SACRED': [15, 24, 5, 4, 18, 23],
    'WISDOM': [7, 10, 15, 23, 3, 19],
    'TRUTH': [16, 4, 1, 2],  # T=16, R=4, U=1, TH=2
    'CABAL': [5, 24, 17, 24, 20],
    'SHADOW': [15, 8, 24, 23, 3, 7],
    'SHADOWS': [15, 8, 24, 23, 3, 7, 15],
    'MOBIUS': [19, 3, 17, 10, 1, 15],
    'CIRCUMFERENCE': None,  # compute
    'CONSUMPTION': None,
    'PRESERVATION': None,
    'ADHERENCE': None,
    'PRIMALITY': None,
    'EMERGENCE': None,
    'PILGRIM': None,
    'INTUS': None,
    'KOAN': None,
    'PARABLE': None,
}

# Fill in computed keys
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []; i = 0; text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            result.append(DIGRAPHS[text[i:i+2]])
            i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
            i += 1
        else: i += 1
    return result

for kw in test_keys:
    if test_keys[kw] is None:
        test_keys[kw] = eng_to_gp(kw)

for kw, key in test_keys.items():
    kl = len(key)
    best_score = 0
    best_text = ""
    best_info = ""
    
    for offset in range(kl):
        for mode_name, dec_fn in [('SUB', lambda c,k,kl,o: [(c[i]-k[(i+o)%kl])%MOD for i in range(len(c))]),
                                   ('ADD', lambda c,k,kl,o: [(c[i]+k[(i+o)%kl])%MOD for i in range(len(c))]),
                                   ('BEAU', lambda c,k,kl,o: [(k[(i+o)%kl]-c[i])%MOD for i in range(len(c))])]:
            plain = dec_fn(cipher, key, kl, offset)
            text_flat = ''.join(LAT[v] for v in plain)
            score = 0
            for word in ['THE', 'AND', 'FOR', 'ALL', 'YOU', 'NOT', 'ARE', 'THIS',
                          'THAT', 'WITH', 'SOME', 'WHAT', 'WILL', 'WOULD', 'WISDOM',
                          'SACRED', 'TRUTH', 'KNOW', 'HOLY', 'INSTRUCTION']:
                if word in text_flat:
                    score += len(word)
            
            if score > best_score:
                best_score = score
                best_text = text_display(plain, words)
                best_info = f"{mode_name} offset={offset}"
    
    if best_score > 8:
        print(f"\n  Key '{kw}' (len={kl}): {best_info}, score={best_score}")
        print(f"    {best_text[:100]}")

    # Also try with F-skip
    for offset in range(kl):
        for f_mask in range(2**len(f_positions)):
            f_skip = set()
            for bit_idx in range(len(f_positions)):
                if f_mask & (1 << bit_idx):
                    f_skip.add(f_positions[bit_idx])
            
            plain = decrypt_fskip_sub(cipher, key, kl, offset, f_skip)
            text_flat = ''.join(LAT[v] for v in plain)
            score = 0
            for word in ['THE', 'AND', 'FOR', 'ALL', 'YOU', 'NOT', 'ARE', 'THIS',
                          'THAT', 'WITH', 'SOME', 'WHAT', 'WILL', 'WOULD', 'WISDOM',
                          'SACRED', 'TRUTH', 'KNOW', 'HOLY', 'INSTRUCTION']:
                if word in text_flat:
                    score += len(word)
            
            if score > 15:
                ioc = compute_ioc(plain)
                text = text_display(plain, words)
                print(f"\n  Key '{kw}' F-SKIP offset={offset} fmask={f_mask:03b}: score={score}, IoC={ioc:.3f}")
                print(f"    {text[:120]}")

print("\nDONE")
