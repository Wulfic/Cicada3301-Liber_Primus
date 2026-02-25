"""
CRITICAL FIX: Add missing J rune variant U+16C4 (ᛄ) to GP mapping.
All rune files use ᛄ (U+16C4) instead of ᛂ (U+16C2) for J.
847 instances across 59 pages were being silently dropped!

Re-verify P19 (known Vigenère key) and P55/P73 (known totient) decryptions.
"""
import os, math

# FIXED GP mapping - includes BOTH J variants
GP = {
    '\u16A0':0,  # ᚠ F
    '\u16A2':1,  # ᚢ U
    '\u16A6':2,  # ᚦ TH
    '\u16A9':3,  # ᚩ O
    '\u16B1':4,  # ᚱ R
    '\u16B3':5,  # ᚳ CK/C
    '\u16B7':6,  # ᚷ G
    '\u16B9':7,  # ᚹ W
    '\u16BB':8,  # ᚻ H
    '\u16BE':9,  # ᚾ N
    '\u16C1':10, # ᛁ I
    '\u16C2':11, # ᛂ J (standard)
    '\u16C4':11, # ᛄ J (variant used in rune files!) <<< THE FIX
    '\u16C7':12, # ᛇ EO
    '\u16C8':13, # ᛈ P
    '\u16C9':14, # ᛉ X
    '\u16CB':15, # ᛋ S
    '\u16CF':16, # ᛏ T
    '\u16D2':17, # ᛒ B
    '\u16D6':18, # ᛖ E
    '\u16D7':19, # ᛗ M
    '\u16DA':20, # ᛚ L
    '\u16DD':21, # ᛝ NG
    '\u16DF':22, # ᛟ OE
    '\u16DE':23, # ᛞ D
    '\u16AA':24, # ᚪ A
    '\u16AB':25, # ᚫ AE
    '\u16A3':26, # ᚣ Y
    '\u16E1':27, # ᛡ IA
    '\u16E0':28, # ᛠ EA
}

IDX2LAT = {0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',
           10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',
           19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',27:'IA',28:'EA'}

P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]

def sieve(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(len(s)) if s[i]]

def totient(n):
    r=n;p=2;t=n
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            r-=r//p
        p+=1
    if t>1: r-=r//t
    return r

PRIMES = sieve(600000)
print(f"Primes: {len(PRIMES)} available")

def load_runes(path):
    """Load rune file and return list of integer values (with FIXED GP mapping)"""
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    runes = []
    for c in raw:
        if c in GP:
            runes.append(GP[c])
    return runes, raw

# ====== P19 VERIFICATION ======
print("\n" + "="*80)
print("P19 VERIFICATION (Vigenère ADD, key length 47)")
print("="*80)

p19_runes, p19_raw = load_runes('LiberPrimus/pages/page_19/runes.txt')
j_count = p19_raw.count('\u16C4')
print(f"P19 runes: {len(p19_runes)} (with fix), J variant count: {j_count}")
print(f"Key length: {len(P19_KEY)}")

# Decrypt: plain = (cipher - key) % 29
p19_plain = []
for i, c in enumerate(p19_runes):
    k = P19_KEY[i % len(P19_KEY)]
    p = (c - k) % 29
    p19_plain.append(p)

p19_text = ''.join(IDX2LAT[p] for p in p19_plain)
print(f"\nDecrypted runeglish (first 300 chars):")
print(p19_text[:300])

# Check if it contains expected text
known_fragments = ["REARRANGING", "PRIMES", "NUMBERS", "PATH", "DEOR"]
for frag in known_fragments:
    if frag in p19_text:
        idx = p19_text.index(frag)
        print(f"  Found '{frag}' at position {idx} ✓")
    else:
        print(f"  '{frag}' NOT FOUND ✗")

# Now check word boundaries
print(f"\n--- P19 Word Boundary Check ---")
tokens = []
for c in p19_raw:
    if c in GP:
        tokens.append(('R', GP[c]))
    elif c in ('-', '\u2022', '.', ' ', '\n'):
        tokens.append(('S', c))

# Parse words
words = []
cur = []
ri = 0
for t, v in tokens:
    if t == 'R':
        cur.append(ri)
        ri += 1
    elif t == 'S':
        if cur:
            words.append(cur)
            cur = []
if cur:
    words.append(cur)

print(f"Ciphertext words: {len(words)}")
print(f"\nFirst 20 words (cipher → plain):")
for i, w in enumerate(words[:20]):
    cipher_str = ''.join(IDX2LAT[p19_runes[j]] for j in w)
    plain_str = ''.join(IDX2LAT[p19_plain[j]] for j in w)
    print(f"  Word {i:3d} ({len(w):2d}): cipher={cipher_str:20s} → plain={plain_str}")

# Single-rune words
singles = [(i, w[0]) for i, w in enumerate(words) if len(w) == 1]
print(f"\nSingle-rune words: {len(singles)}")
for word_idx, rune_pos in singles:
    c = p19_runes[rune_pos]
    p = p19_plain[rune_pos]
    print(f"  Word #{word_idx}, pos {rune_pos}: cipher={IDX2LAT[c]} → plain={IDX2LAT[p]}")

# ====== P55 VERIFICATION ======
print("\n" + "="*80)
print("P55 VERIFICATION (Totient cipher, F-skip)")
print("="*80)

if os.path.exists('LiberPrimus/pages/page_55/runes.txt'):
    p55_runes, p55_raw = load_runes('LiberPrimus/pages/page_55/runes.txt')
    j_count55 = p55_raw.count('\u16C4')
    print(f"P55 runes: {len(p55_runes)}, J variant count: {j_count55}")
    
    # Try both decryption directions
    for direction, label in [(-1, "SUB: plain=(c-tot)%29"), (1, "ADD: plain=(c+tot)%29")]:
        key_idx = 0
        plain = []
        for c in p55_runes:
            if c == 0:  # F - skip
                plain.append(0)
                continue
            k = totient(PRIMES[key_idx]) % 29
            p = (c + direction * k) % 29
            plain.append(p)
            key_idx += 1
        
        text = ''.join(IDX2LAT[p] for p in plain)
        print(f"\n  {label}: {text[:200]}")
        
        # Check for English words
        common_words = ["THE", "AND", "OF", "IS", "IN", "TO", "IT", "FOR", "AN"]
        found = [w for w in common_words if w in text]
        print(f"  English words found: {found}")

# ====== P57 VERIFICATION (known plaintext page) ======
print("\n" + "="*80)
print("P57 VERIFICATION (plaintext page)")
print("="*80)

if os.path.exists('LiberPrimus/pages/page_57/runes.txt'):
    p57_runes, p57_raw = load_runes('LiberPrimus/pages/page_57/runes.txt')
    j_count57 = p57_raw.count('\u16C4')
    print(f"P57 runes: {len(p57_runes)}, J variant count: {j_count57}")
    
    p57_text = ''.join(IDX2LAT[p] for p in p57_runes)
    print(f"Direct runeglish: {p57_text[:300]}")
    
    # P57 is a plaintext page (parable) - should be directly readable
    if "PARABLE" in p57_text or "LIKE" in p57_text or "SURFACE" in p57_text:
        print("  ✓ P57 plaintext page reads correctly!")
    else:
        print("  ✗ P57 not readable - check mapping")

# ====== P56 VERIFICATION (known solved) ======
print("\n" + "="*80)
print("P56 VERIFICATION (Totient cipher)")
print("="*80)

if os.path.exists('LiberPrimus/pages/page_56/runes.txt'):
    p56_runes, p56_raw = load_runes('LiberPrimus/pages/page_56/runes.txt')
    print(f"P56 runes: {len(p56_runes)}")
    
    for direction, label in [(-1, "SUB"), (1, "ADD")]:
        key_idx = 0
        plain = []
        for c in p56_runes:
            if c == 0:  # F-skip
                plain.append(0)
                continue
            k = totient(PRIMES[key_idx]) % 29
            p = (c + direction * k) % 29
            plain.append(p)
            key_idx += 1
        text = ''.join(IDX2LAT[p] for p in plain)
        print(f"  {label}: {text[:200]}")

# ====== RUNE COUNT COMPARISON ======
print("\n" + "="*80)
print("RUNE COUNT CHANGES (OLD vs FIXED)")
print("="*80)

# Count how many runes each page has with the fix
GP_OLD = {k:v for k,v in GP.items() if k != '\u16C4'}  # old mapping without fix

for pn in range(18, 55):
    path = f'LiberPrimus/pages/page_{pn:02d}/runes.txt'
    if not os.path.exists(path): continue
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    old_count = sum(1 for c in raw if c in GP_OLD)
    new_count = sum(1 for c in raw if c in GP)
    diff = new_count - old_count
    if diff > 0:
        print(f"  P{pn:02d}: {old_count} → {new_count} runes (+{diff} J's recovered)")
