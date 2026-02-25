"""Apply known Vigenère keys from Page 63 grid to pages 21-30.
Then attempt transposition reversal using prime-based methods.
J-FIXED GP mapping used throughout."""

import os
from collections import Counter
from itertools import permutations
import math

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

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

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c * (c-1) for c in counts.values()) / (n * (n-1))

# Known keys from Page 63 grid
P63_KEYS = {
    21: ("CABAL", "BEAUFORT"),
    22: ("DIVINITY", "BEAUFORT"),
    23: ("ENCRYPTION", "ADD"),
    24: ("OBSCURA", "BEAUFORT"),
    25: ("CABAL", "BEAUFORT"),
    26: ("ENCRYPT", "ADD"),
    27: ("SHADOWS", "ADD"),
    28: ("DEOR", "SUB"),
    29: ("TOTIENT", "BEAUFORT"),
    30: ("MOURNFUL", "ADD"),
}

# Also try these keys directly as GP rune values (from community docs)
GP_KEYS_DIRECT = {
    "CABAL": [5,24,17,24,20],
    "OBSCURA": [3,17,15,5,1,4,24],
    "SHADOWS": [15,8,24,23,3,7,15],
    "MOURNFUL": [19,3,1,4,9,0,1,20],
}

print("="*90)
print("STEP 1: Apply known Vigenère keys to pages 21-30")
print("="*90)

decrypted_pages = {}
for pg in range(21, 31):
    runes, words = load_page(pg)
    if runes is None:
        continue
    
    keyword_text, mode = P63_KEYS[pg]
    
    # Try both english_to_gp conversion AND direct GP values if available
    key_candidates = [("eng2gp", english_to_gp(keyword_text))]
    if keyword_text in GP_KEYS_DIRECT:
        key_candidates.append(("direct", GP_KEYS_DIRECT[keyword_text]))
    
    best_ioc = 0
    best_dec = None
    best_mode = None
    best_key_type = None
    
    for key_type, key_gp in key_candidates:
        kl = len(key_gp)
        
        for try_mode in [mode, 'ADD', 'SUB', 'BEAUFORT']:
            if try_mode == 'ADD':
                dec = [(runes[i] + key_gp[i % kl]) % 29 for i in range(len(runes))]
            elif try_mode == 'SUB':
                dec = [(runes[i] - key_gp[i % kl]) % 29 for i in range(len(runes))]
            else:  # BEAUFORT
                dec = [(key_gp[i % kl] - runes[i]) % 29 for i in range(len(runes))]
            
            ic = ioc(dec) * 29
            if ic > best_ioc:
                best_ioc = ic
                best_dec = dec
                best_mode = try_mode
                best_key_type = key_type
                best_key_gp = key_gp
    
    decrypted_pages[pg] = {
        'runes': best_dec,
        'cipher': runes,
        'words': words,
        'ioc': best_ioc,
        'mode': best_mode,
        'key_type': best_key_type,
        'key_gp': best_key_gp,
        'keyword': keyword_text,
        'n': len(runes)
    }
    
    # Show first 15 words of best decryption
    pos = 0
    word_texts = []
    for word in words[:15]:
        n = len(word)
        word_dec = best_dec[pos:pos+n]
        word_lat = ''.join(LATIN[v] for v in word_dec)
        word_texts.append(word_lat)
        pos += n
    
    print(f"\n  Page {pg}: {len(runes)} runes, key='{keyword_text}'({best_key_type}), mode={best_mode}, IoC*29={best_ioc:.3f}")
    print(f"    Key GP: {best_key_gp}")
    print(f"    First words: {' '.join(word_texts)}")
    
    # Factor analysis 
    n = len(runes)
    factors = [f for f in range(2, n+1) if n % f == 0]
    print(f"    Rune count {n} factors: {factors[:15]}...")

# === STEP 2: Try transposition methods on each decrypted page ===
print()
print("="*90)
print("STEP 2: Transposition attacks on Vigenère-decrypted pages")
print("="*90)

COMMON_WORDS = set()
for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
          'OUR','OUT','HAS','HIS','HOW','WHO','ITS','MAY','NEW','NOW','OLD','SEE',
          'THIS','THAT','WITH','HAVE','FROM','THEY','BEEN','MANY','SOME','THEM',
          'THAN','EACH','MAKE','LIKE','WILL','INTO','SELF','MIND','SOUL','SEEK',
          'FIND','KNOW','WITHIN','WITHOUT','SACRED','WISDOM','TRUTH','LIGHT',
          'PRIME','PRIMES','NUMBER','A','I','AN','IN','OF','IS','IT','TO','AS',
          'AT','WE','DO','BE','HE','IF','OR','NO','UP','SO','BY','GO','MY',
          'WORD','WORDS','LOSS','BEING','THROUGH','EVERY','WORLD','THESE',
          'THOSE','FIRST','AFTER','OTHER','WHICH','THEIR','ABOUT','THERE',
          'WOULD','COULD','THINK','WHERE','UNDER','STILL','ALSO','BACK',
          'ONLY','COME','MADE','DAY','WAY','DID','GET','HIM','LET','SAY',
          'SHE','TOO','USE','WHAT','WHEN','RUNE','PATH','SHOW',
          'CONSUME','LOST','WELCOME','WARN','WARNING','ADHERE','REMEMBER',
          'NOTHING','EVERYTHING','CONSCIOUSNESS','ENCRYPTION','CIPHER','KEY',
          'PARABLE','DIVINITY','CIRCUMFERENCE']:

    COMMON_WORDS.add(w)

def score_words(dec_runes, word_structure):
    """Score based on English word matches."""
    pos = 0
    matched = 0
    for word in word_structure:
        n = len(word)
        word_dec = dec_runes[pos:pos+n]
        word_lat = ''.join(LATIN[v] for v in word_dec)
        if word_lat.upper() in COMMON_WORDS:
            matched += 1
        pos += n
    return matched

def primes_up_to(n):
    sieve = [True] * (n+1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5)+1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

primes = primes_up_to(5000)

for pg in range(21, 31):
    if pg not in decrypted_pages:
        continue
    
    data = decrypted_pages[pg]
    dec = data['runes']
    words = data['words']
    n = data['n']
    
    print(f"\n--- Page {pg} ({n} runes, IoC*29={data['ioc']:.3f}) ---")
    
    results = []
    
    # Method 1: Columnar transposition with various widths
    for width in range(2, min(60, n)):
        if n % width != 0:
            continue  # Only try exact-fit widths first
        height = n // width
        
        # Read by columns (standard columnar)
        reordered = []
        for col in range(width):
            for row in range(height):
                reordered.append(dec[row * width + col])
        
        score = score_words(reordered, words)
        ic = ioc(reordered) * 29
        if score >= 3:
            results.append(('columnar_read_cols', width, score, ic, reordered))
        
        # Write by columns, read by rows
        reordered2 = [0] * n
        idx = 0
        for col in range(width):
            for row in range(height):
                reordered2[row * width + col] = dec[idx]
                idx += 1
        
        score2 = score_words(reordered2, words)
        if score2 >= 3:
            results.append(('columnar_write_cols', width, score2, ic, reordered2))
    
    # Method 2: Rail fence
    for rails in range(2, 15):
        # Build rail fence pattern
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for i in range(n):
            fence[rail].append(dec[i])
            if rail == 0:
                direction = 1
            elif rail == rails - 1:
                direction = -1
            rail += direction
        
        # Read off rails
        reordered = []
        for r in fence:
            reordered.extend(r)
        
        # Now reverse: the ciphertext IS the rails read off, put back
        # Decrypt: figure out positions
        indices = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for i in range(n):
            indices[rail].append(i)
            if rail == 0: direction = 1
            elif rail == rails - 1: direction = -1
            rail += direction
        
        # Distribute cipher text to rails
        reordered3 = [0] * n
        idx = 0
        for r in range(rails):
            for pos in indices[r]:
                if idx < n:
                    reordered3[pos] = dec[idx]
                    idx += 1
        
        score3 = score_words(reordered3, words)
        if score3 >= 3:
            results.append(('rail_fence_decrypt', rails, score3, ioc(reordered3)*29, reordered3))
    
    # Method 3: Prime-position reading
    # Read positions at prime indices
    prime_set = set(primes_up_to(n))
    prime_positions = [i for i in range(n) if i in prime_set]
    non_prime_positions = [i for i in range(n) if i not in prime_set]
    
    # Interleave: first prime positions, then non-prime
    for order_name, order in [("prime_first", prime_positions + non_prime_positions),
                               ("non_prime_first", non_prime_positions + prime_positions)]:
        reordered = [dec[i] for i in order]
        score = score_words(reordered, words)
        if score >= 3:
            results.append((f'prime_read_{order_name}', 0, score, ioc(reordered)*29, reordered))
        
        # Also: write at prime positions, read sequentially
        reordered2 = [0] * n
        for new_idx, old_idx in enumerate(order):
            if new_idx < n:
                reordered2[old_idx] = dec[new_idx]
        score2 = score_words(reordered2, words)
        if score2 >= 3:
            results.append((f'prime_write_{order_name}', 0, score2, ioc(reordered2)*29, reordered2))
    
    # Method 4: Reverse
    rev = dec[::-1]
    score = score_words(rev, words)
    if score >= 3:
        results.append(('reverse', 0, score, ioc(rev)*29, rev))
    
    # Method 5: Skip cipher (every k-th position)
    for k in range(2, min(30, n//2)):
        reordered = []
        visited = set()
        for start in range(k):
            for i in range(start, n, k):
                if i not in visited:
                    reordered.append(dec[i])
                    visited.add(i)
        if len(reordered) == n:
            score = score_words(reordered, words)
            if score >= 3:
                results.append(('skip', k, score, ioc(reordered)*29, reordered))
    
    # Method 6: Columnar transposition with prime widths
    for width in primes[:20]:  # First 20 primes as widths
        if width >= n:
            break
        height = math.ceil(n / width)
        
        # Pad if needed
        padded = dec + [0] * (width * height - n)
        
        # Read by columns
        reordered = []
        for col in range(width):
            for row in range(height):
                idx = row * width + col
                if idx < n:
                    reordered.append(padded[idx])
        
        if len(reordered) >= n:
            reordered = reordered[:n]
        score = score_words(reordered, words)
        ic = ioc(reordered) * 29
        if score >= 3:
            results.append(('col_prime_width', width, score, ic, reordered))
    
    # Method 7: Diagonal reading
    for width in [7, 11, 13, 17, 19, 23, 29]:
        if width >= n:
            continue
        height = math.ceil(n / width)
        # Read diagonally
        reordered = []
        for d in range(width + height - 1):
            for row in range(max(0, d - width + 1), min(d + 1, height)):
                col = d - row
                if col < width:
                    idx = row * width + col
                    if idx < n:
                        reordered.append(dec[idx])
        if len(reordered) >= n:
            reordered = reordered[:n]
        score = score_words(reordered, words)
        if score >= 3:
            results.append(('diagonal', width, score, ioc(reordered)*29, reordered))
    
    # Show results
    if results:
        results.sort(key=lambda x: -x[2])
        print(f"  HITS (≥3 word matches):")
        for method, param, score, ic, reordered in results[:5]:
            pos = 0
            word_texts = []
            for word in words[:15]:
                wn = len(word)
                word_dec = reordered[pos:pos+wn]
                word_lat = ''.join(LATIN[v] for v in word_dec)
                word_texts.append(word_lat)
                pos += wn
            print(f"    {method}(param={param}): score={score}, text={' '.join(word_texts)}")
    else:
        print(f"  No transposition produced ≥3 word matches")

# === STEP 3: Single-rune word analysis ===
print()
print("="*90)
print("STEP 3: Single-rune word analysis (must be A=24 or I=10)")
print("="*90)

for pg in range(21, 31):
    if pg not in decrypted_pages:
        continue
    
    data = decrypted_pages[pg]
    dec = data['runes']
    words = data['words']
    
    single_rune_words = []
    pos = 0
    for wi, word in enumerate(words):
        if len(word) == 1:
            v = dec[pos]
            expected = "A" if v == 24 else ("I" if v == 10 else f"UNEXPECTED({LATIN[v]})")
            single_rune_words.append((wi, pos, v, LATIN[v], expected))
        pos += len(word)
    
    if single_rune_words:
        print(f"\n  Page {pg}:")
        for wi, pos, v, lat, exp in single_rune_words:
            marker = " ✓" if v in [24, 10] else " ✗ WRONG"
            print(f"    Word {wi} (pos {pos}): {lat} ({v}) → {exp}{marker}")
