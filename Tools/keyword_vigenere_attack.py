"""Comprehensive Vigenère attack on unsolved pages using known keywords.
Keywords from solved pages: DIVINITY, CIRCUMFERENCE/FIRFUMFERENFE, etc.
Also try: autokey, running key, prime-derived keys."""

import os
from collections import Counter
from itertools import product

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English letter to GP
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

# Digraph-aware English to GP
def english_to_gp(text):
    text = text.upper()
    gp = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph in ('TH','NG','EO','OE','EA','AE','IA'):
                dgmap = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
                gp.append(dgmap[digraph])
                i += 2
                continue
        c = text[i]
        if c in ENG2GP:
            gp.append(ENG2GP[c])
        i += 1
    return gp

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                runes = [GP[c] for c in raw if c in GP]
                words = []
                current = []
                for c in raw:
                    if c in GP:
                        current.append(GP[c])
                    elif current:
                        words.append(current)
                        current = []
                if current:
                    words.append(current)
                return runes, words
    return None, None

# English word list for scoring
ENGLISH_WORDS = set()
# Common words likely in Liber Primus context
for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
          'OUR','OUT','HAS','HIS','HOW','WHO','ITS','MAY','NEW','NOW','OLD','SEE',
          'WAY','DID','GET','HIM','LET','SAY','SHE','TOO','USE','THIS','THAT',
          'WITH','HAVE','FROM','THEY','BEEN','MANY','SOME','THEM','THAN','EACH',
          'MAKE','LIKE','LONG','LOOK','MOST','OVER','SUCH','TAKE','WHAT','WHEN',
          'WILL','INTO','PATH','SHOW','RUNE','SELF','MIND','SOUL','SEEK','FIND',
          'KNOW','WITHIN','WITHOUT','SACRED','WISDOM','TRUTH','LIGHT','PRIME',
          'NUMBER','PRIMES','NUMBERS','DIVINITY','CIRCUMFERENCE','CONSUMPTION',
          'PROGRAM','COMMAND','INSTALL','GENTOO','DEEP','WEB','PAGE','THERE',
          'EXISTS','GOOD','LUCK','AN','END','ON','IN','OF','IS','IT','TO','AS',
          'AT','WE','DO','BE','HE','IF','OR','NO','UP','SO','BY','GO','MY',
          'WE','US','AM','WORD','WORDS','LOSS','DATA','INFORMATION',
          'A','I','BEING','THING','THINGS','THROUGH','BETWEEN','EVERY','WORLD',
          'THESE','THOSE','FIRST','AFTER','BEFORE','OTHER','WHICH','THEIR',
          'ABOUT','WOULD','THERE','COULD','PEOPLE','THINK','WHERE','UNDER',
          'STILL','ALSO','BACK','ONLY','COME','MADE','AFTER','YEAR','YEARS',
          'THEM','JUST','LIKE','OVER','SUCH','VERY','SOME','WHEN',
          'ADHERE','REMEMBER','NOTHING','EVERYTHING','CONSCIOUSNESS',
          'SECURITY','PRIVACY','FREEDOM','ENCRYPTION','CIPHER','KEY',
          'PARABLE','LOSS','LOSERS','CONSUME','CONSUMPTION','LOST',
          'INSTRUCTION','WELCOME','WARN','WARNING']:
    ENGLISH_WORDS.add(w)

def score_decryption(runes, words_structure):
    """Score a decryption by counting matching English words."""
    pos = 0
    matched = 0
    total_words = len(words_structure)
    matched_chars = 0
    
    for word in words_structure:
        n = len(word)
        word_dec = runes[pos:pos+n]
        word_lat = ''.join(LATIN[v] for v in word_dec)
        if word_lat.upper() in ENGLISH_WORDS:
            matched += 1
            matched_chars += len(word_lat)
        pos += n
    
    return matched, matched_chars, total_words

def ioc(values):
    n = len(values)
    if n < 2:
        return 0
    counts = Counter(values)
    return sum(c * (c-1) for c in counts.values()) / (n * (n-1))

# === Keywords to try ===
keywords_text = [
    "DIVINITY",
    "CIRCUMFERENCE",
    "FIRFUMFERENFE",
    "CONSUMPTION",
    "WISDOM",
    "PRIMES",
    "SACRED",
    "LIBERTY",
    "TRUTH",
    "ENLIGHTENMENT",
    "KOAN",
    "PARABLE",
    "INSTAR",
    "EMERGENCE",
    "ADHERENCE",
    "WELCOME",
    "PILGRIM",
    "CICADA",
    "LIBER",
    "PRIMUS",
    "DEOR",
    "REARRANGING",
    "PATH",
    "TOTIENT",
    "EULER",
    "PHI",
    "GEMATRIA",
    "LOSS",
]

# Convert keywords to GP sequences
keywords_gp = {}
for kw in keywords_text:
    gp = english_to_gp(kw)
    keywords_gp[kw] = gp

# Also try direct LATIN values (in case keyword is already in GP-Latin form)
keywords_gp["YAHEOOPYJ"] = [26,24,8,18,3,3,13,26,11]  # Known P17 key
keywords_gp["P19_KEY_43"] = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23]

# Generate prime-based keys
def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

primes = primes_up_to(10000)

# Prime sequences as keys
keywords_gp["PRIMES_MOD29"] = [p % 29 for p in primes[:50]]
keywords_gp["PRIMES_MOD29_REVERSED"] = [p % 29 for p in primes[:50]][::-1]

# Totient of primes mod 29 (totient(p) = p-1 for primes)
keywords_gp["TOTIENT_PRIMES_MOD29"] = [(p - 1) % 29 for p in primes[:50]]

# Fibonacci mod 29
fib = [1, 1]
for _ in range(50):
    fib.append(fib[-1] + fib[-2])
keywords_gp["FIBONACCI_MOD29"] = [f % 29 for f in fib[:50]]

# All unsolved pages
unsolved_pages = list(range(18, 55))

print(f"Testing {len(keywords_gp)} keywords on {len(unsolved_pages)} pages")
print(f"Modes: ADD, SUB, BEAUFORT")
print()

# Test all combinations
results = []
for pg in unsolved_pages:
    runes, words = load_page(pg)
    if runes is None or len(runes) < 10:
        continue
    
    for kw_name, kw_gp in keywords_gp.items():
        if not kw_gp:
            continue
        kw_len = len(kw_gp)
        
        for mode in ['ADD', 'SUB', 'BEAUFORT']:
            if mode == 'ADD':
                dec = [(runes[i] + kw_gp[i % kw_len]) % 29 for i in range(len(runes))]
            elif mode == 'SUB':
                dec = [(runes[i] - kw_gp[i % kw_len]) % 29 for i in range(len(runes))]
            else:  # BEAUFORT
                dec = [(kw_gp[i % kw_len] - runes[i]) % 29 for i in range(len(runes))]
            
            matched, matched_chars, total_words = score_decryption(dec, words)
            ioc_val = ioc(dec) * 29
            
            if matched >= 3 or ioc_val > 1.5:
                results.append((pg, kw_name, mode, matched, matched_chars, total_words, ioc_val))

# Sort by matches
results.sort(key=lambda x: (-x[3], -x[6]))

print("="*100)
print("TOP RESULTS (≥3 word matches or IoC*29 > 1.5)")
print("="*100)
for pg, kw, mode, matched, mchars, total, ioc_val in results[:30]:
    runes, words = load_page(pg)
    kw_gp = keywords_gp[kw]
    kw_len = len(kw_gp)
    if mode == 'ADD':
        dec = [(runes[i] + kw_gp[i % kw_len]) % 29 for i in range(len(runes))]
    elif mode == 'SUB':
        dec = [(runes[i] - kw_gp[i % kw_len]) % 29 for i in range(len(runes))]
    else:
        dec = [(kw_gp[i % kw_len] - runes[i]) % 29 for i in range(len(runes))]
    
    # Show first few words
    pos = 0
    first_words = []
    for word in words[:15]:
        n = len(word)
        word_dec = dec[pos:pos+n]
        word_lat = ''.join(LATIN[v] for v in word_dec)
        first_words.append(word_lat)
        pos += n
    
    print(f"\n  P{pg:02d} | {kw:25s} | {mode:8s} | words={matched}/{total} | IoC*29={ioc_val:.3f}")
    print(f"    Text: {' '.join(first_words)}")

# === AUTOKEY CIPHER TEST ===
print()
print("="*100)
print("AUTOKEY CIPHER TEST (key feeds into itself using plaintext)")
print("="*100)

# Autokey: key[0..k-1] is the primer, then key[i] = plaintext[i-k] for i >= k
# Decryption: plain[i] = (cipher[i] - key[i]) % 29, then key[i+k] = plain[i]
# Try short primers (1-8 values)

best_autokey = []
for pg in unsolved_pages:
    runes, words = load_page(pg)
    if runes is None or len(runes) < 50:
        continue
    
    for primer_len in range(1, 9):
        for primer_val in range(29):  # Single-value primer repeated
            primer = [primer_val] * primer_len
            
            # Autokey SUB
            plain = []
            key_stream = list(primer)
            for i in range(len(runes)):
                if i < len(key_stream):
                    p = (runes[i] - key_stream[i]) % 29
                else:
                    p = (runes[i] - plain[i - primer_len]) % 29
                plain.append(p)
            
            ioc_val = ioc(plain) * 29
            if ioc_val > 1.5:
                matched, mchars, total = score_decryption(plain, words)
                best_autokey.append((pg, primer_val, primer_len, 'SUB', matched, total, ioc_val))
            
            # Autokey ADD
            plain = []
            for i in range(len(runes)):
                if i < primer_len:
                    p = (runes[i] + primer[i]) % 29
                else:
                    p = (runes[i] + plain[i - primer_len]) % 29
                plain.append(p)
            
            ioc_val = ioc(plain) * 29
            if ioc_val > 1.5:
                matched, mchars, total = score_decryption(plain, words)
                best_autokey.append((pg, primer_val, primer_len, 'ADD', matched, total, ioc_val))

best_autokey.sort(key=lambda x: (-x[6], -x[4]))
print(f"\nTop autokey results (IoC*29 > 1.5):")
for pg, pv, pl, mode, matched, total, ioc_val in best_autokey[:20]:
    runes, words = load_page(pg)
    primer = [pv] * pl
    if mode == 'SUB':
        plain = []
        for i in range(len(runes)):
            if i < pl:
                p = (runes[i] - primer[i]) % 29
            else:
                p = (runes[i] - plain[i - pl]) % 29
            plain.append(p)
    else:
        plain = []
        for i in range(len(runes)):
            if i < pl:
                p = (runes[i] + primer[i]) % 29
            else:
                p = (runes[i] + plain[i - pl]) % 29
            plain.append(p)
    
    pos = 0
    first_words = []
    for word in words[:10]:
        n = len(word)
        word_dec = plain[pos:pos+n]
        word_lat = ''.join(LATIN[v] for v in word_dec)
        first_words.append(word_lat)
        pos += n
    
    print(f"  P{pg:02d} primer={pv}({LATIN[pv]})x{pl} {mode}: words={matched}/{total} IoC*29={ioc_val:.3f}")
    print(f"    Text: {' '.join(first_words)}")
