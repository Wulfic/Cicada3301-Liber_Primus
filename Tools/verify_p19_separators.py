"""
Verify P19 word separators: Do ciphertext separator positions match plaintext word boundaries?
This is critical to determine if the known-plaintext (single-rune word) approach is valid.
"""
import os

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,
      '\u16B7':6,'\u16B9':7,'\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,
      '\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,
      '\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = {0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',
           10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',
           19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',27:'IA',28:'EA'}

P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]

# Load P19 rune file preserving ALL characters
with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read().strip()

print("=== P19 RAW TEXT (first 200 chars) ===")
print(repr(raw[:200]))
print()

# Parse into tokens: each token is either a rune value or a separator marker
tokens = []
for c in raw:
    if c in GP:
        tokens.append(('R', GP[c]))  # Rune
    elif c in ('-', '\u2022', '.', ' ', '\n'):
        tokens.append(('S', c))  # Separator
    else:
        tokens.append(('O', c))  # Other

# Extract just the runes (for decryption)
cipher_runes = [v for t, v in tokens if t == 'R']
print(f"Total cipher runes: {len(cipher_runes)}")
print(f"Key length: {len(P19_KEY)}")

# Decrypt with Vigenere ADD: plain = (cipher - key) % 29
plain_runes = []
for i, c in enumerate(cipher_runes):
    k = P19_KEY[i % len(P19_KEY)]
    p = (c - k) % 29
    plain_runes.append(p)

# Convert to Latin (runeglish)
plain_text = ''.join(IDX2LAT[p] for p in plain_runes)
print(f"\n=== DECRYPTED PLAINTEXT (full) ===")
print(plain_text)

# Now reconstruct with separators
print(f"\n=== CIPHERTEXT WORD STRUCTURE ===")
cipher_words = []
cur_word = []
rune_idx = 0
for t, v in tokens:
    if t == 'R':
        cur_word.append(rune_idx)
        rune_idx += 1
    elif t == 'S':
        if cur_word:
            cipher_words.append(cur_word)
            cur_word = []
if cur_word:
    cipher_words.append(cur_word)

print(f"Number of ciphertext 'words': {len(cipher_words)}")
print(f"Word lengths: {[len(w) for w in cipher_words]}")

# Show each ciphertext "word" and what it decrypts to
print(f"\n=== CIPHERTEXT WORDS → PLAINTEXT ===")
for i, w in enumerate(cipher_words):
    cipher_str = ''.join(IDX2LAT[cipher_runes[j]] for j in w)
    plain_str = ''.join(IDX2LAT[plain_runes[j]] for j in w)
    marker = " <<<" if len(w) == 1 else ""
    print(f"  Word {i:3d} ({len(w):2d} runes): cipher={cipher_str:20s} → plain={plain_str}{marker}")

# Count single-rune words and what they decrypt to
print(f"\n=== SINGLE-RUNE WORDS ANALYSIS ===")
singles = [(i, w[0]) for i, w in enumerate(cipher_words) if len(w) == 1]
print(f"Found {len(singles)} single-rune words in ciphertext")
for word_idx, rune_pos in singles:
    c = cipher_runes[rune_pos]
    p = plain_runes[rune_pos]
    print(f"  Word #{word_idx}, rune pos {rune_pos}: cipher={IDX2LAT[c]} → plain={IDX2LAT[p]}")

# Now look at actual English plaintext word boundaries
print(f"\n=== EXPECTED PLAINTEXT WORDS (from known solution) ===")
known = "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
# This is partial - let me derive it from the full decrypted text
eng_words = plain_text  # This is the full runeglish output
# Let's see what the natural English words would be
print(f"Full runeglish: {plain_text[:200]}")

# Check if P55/P73 separators match
print("\n" + "="*80)
print("=== P55 SEPARATOR VERIFICATION ===")

# P55 uses totient cipher
import math

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

PRIMES = sieve(10000)

if os.path.exists('LiberPrimus/pages/page_55/runes.txt'):
    with open('LiberPrimus/pages/page_55/runes.txt', 'r', encoding='utf-8') as f:
        p55_raw = f.read().strip()
    
    p55_runes = [GP[c] for c in p55_raw if c in GP]
    print(f"P55 total runes: {len(p55_runes)}")
    
    # Decrypt with totient, F-skip
    key_idx = 0
    p55_plain = []
    for c in p55_runes:
        if c == 0:  # F - skip
            p55_plain.append(0)
            continue
        k = totient(PRIMES[key_idx]) % 29
        p = (c - k) % 29
        p55_plain.append(p)
        key_idx += 1
    
    p55_text = ''.join(IDX2LAT[p] for p in p55_plain)
    print(f"P55 decrypted (first 200): {p55_text[:200]}")
    
    # Parse P55 words
    p55_tokens = []
    for c in p55_raw:
        if c in GP:
            p55_tokens.append(('R', GP[c]))
        elif c in ('-', '\u2022', '.', ' ', '\n'):
            p55_tokens.append(('S', c))
    
    p55_words = []
    cur = []
    ri = 0
    for t, v in p55_tokens:
        if t == 'R':
            cur.append(ri)
            ri += 1
        elif t == 'S':
            if cur:
                p55_words.append(cur)
                cur = []
    if cur:
        p55_words.append(cur)
    
    print(f"\nP55 word structure (first 20 words):")
    for i, w in enumerate(p55_words[:20]):
        plain_str = ''.join(IDX2LAT[p55_plain[j]] for j in w)
        print(f"  Word {i:3d} ({len(w):2d} runes): {plain_str}")

# Also check P73
print("\n" + "="*80)
print("=== P73 SEPARATOR VERIFICATION ===")

if os.path.exists('LiberPrimus/pages/page_73/runes.txt'):
    with open('LiberPrimus/pages/page_73/runes.txt', 'r', encoding='utf-8') as f:
        p73_raw = f.read().strip()
    
    # Skip the note line
    lines = p73_raw.split('\n')
    if lines[0].startswith('Note'):
        p73_raw = '\n'.join(lines[1:])
    
    p73_runes = [GP[c] for c in p73_raw if c in GP]
    print(f"P73 total runes: {len(p73_runes)}")
    
    # Decrypt with totient, F-skip
    key_idx = 0
    p73_plain = []
    for c in p73_runes:
        if c == 0:  # F - skip
            p73_plain.append(0)
            continue
        k = totient(PRIMES[key_idx]) % 29
        p = (c - k) % 29
        p73_plain.append(p)
        key_idx += 1
    
    p73_text = ''.join(IDX2LAT[p] for p in p73_plain)
    print(f"P73 decrypted (first 200): {p73_text[:200]}")
    
    # Parse P73 words
    p73_tokens = []
    for c in p73_raw:
        if c in GP:
            p73_tokens.append(('R', GP[c]))
        elif c in ('-', '\u2022', '.', ' ', '\n'):
            p73_tokens.append(('S', c))
    
    p73_words = []
    cur = []
    ri = 0
    for t, v in p73_tokens:
        if t == 'R':
            cur.append(ri)
            ri += 1
        elif t == 'S':
            if cur:
                p73_words.append(cur)
                cur = []
    if cur:
        p73_words.append(cur)
    
    print(f"\nP73 word structure (first 20 words):")
    for i, w in enumerate(p73_words[:20]):
        plain_str = ''.join(IDX2LAT[p73_plain[j]] for j in w)
        print(f"  Word {i:3d} ({len(w):2d} runes): {plain_str}")
