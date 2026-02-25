"""
Comprehensive Totient Cipher Attack with FIXED GP mapping (U+16C4 J variant)
Tests totient stream at various key offsets on ALL pages.
Uses English word detection for scoring.
"""
import os, sys, math, time
from collections import Counter

# FIXED GP mapping
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,
    '\u16B7':6,'\u16B9':7,'\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,
    '\u16C4':11,  # <<<< THE FIX: J variant
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,
    '\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,
    '\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
IDX2LAT = {0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',
           10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',
           19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',27:'IA',28:'EA'}

# Common English words that would appear in runeglish
ENGLISH_WORDS_2 = {'AN','AT','BE','BY','DO','GO','HE','IF','IN','IS','IT','ME','MY','NO','OF','ON','OR','SO','TO','UP','US','WE'}
ENGLISH_WORDS_3 = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR','OUT','DAY','HAD','HAS','HIM','HIS','HOW','ITS','MAY','NEW','NOW','OLD','SEE','WAY','WHO','DID','LET','SAY','SHE','TOO','USE'}
ENGLISH_WORDS_4 = {'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','CALL','COME','EACH','FIND','MADE','MANY','MOST','MUST','NAME','OVER','PART','SUCH','TAKE','THAN','THEM','THEN','TIME','VERY','WHEN','WHAT','SOME','INTO','ONLY','KNOW','SELF'}
ENGLISH_WORDS_5P = {'WHICH','THEIR','THERE','WOULD','ABOUT','THESE','OTHER','AFTER','COULD','BEING','WORLD','WITHIN','SHOULD','THROUGH','BETWEEN','BEFORE','UNDER','THREE','RIGHT','THINK','WHERE','THOSE','STILL'}

# Build combined set
ALL_WORDS = set()
for ws in [ENGLISH_WORDS_2, ENGLISH_WORDS_3, ENGLISH_WORDS_4, ENGLISH_WORDS_5P]:
    ALL_WORDS.update(ws)

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

print("Building totient stream...")
PRIMES = sieve(800000)
MAX_OFFSET = 10000
TOT = [totient(PRIMES[i])%29 for i in range(min(MAX_OFFSET + 5000, len(PRIMES)))]
print(f"  {len(TOT)} totient values ready")

def load_runes(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    runes = [GP[c] for c in raw if c in GP]
    return runes

def decrypt_totient(cipher_runes, key_offset, direction=-1):
    """Decrypt with totient stream, F-skip, starting at key_offset.
    direction=-1: plain=(cipher-tot)%29  (SUB)
    direction=+1: plain=(cipher+tot)%29  (ADD)
    """
    key_idx = key_offset
    plain = []
    for c in cipher_runes:
        if c == 0:  # F - skip
            plain.append(0)
            continue
        if key_idx >= len(TOT):
            return None  # out of range
        k = TOT[key_idx]
        p = (c + direction * k) % 29
        plain.append(p)
        key_idx += 1
    return plain

def to_runeglish(indices):
    return ''.join(IDX2LAT[i] for i in indices)

def score_english(text):
    """Score how English-like a runeglish text is.
    Returns (word_count, total_word_chars, text_snippet)
    """
    # Try to find English words in the text
    words_found = []
    text_upper = text.upper()
    
    # Sliding window approach - find words
    n = len(text_upper)
    used = [False] * n
    
    # First find longer words (more significant)
    for word_set in [ENGLISH_WORDS_5P, ENGLISH_WORDS_4, ENGLISH_WORDS_3, ENGLISH_WORDS_2]:
        for word in word_set:
            wlen = len(word)
            start = 0
            while start <= n - wlen:
                idx = text_upper.find(word, start)
                if idx == -1:
                    break
                # Check not already used
                if not any(used[idx:idx+wlen]):
                    for j in range(idx, idx+wlen):
                        used[j] = True
                    words_found.append(word)
                start = idx + 1
    
    total_word_chars = sum(len(w) for w in words_found)
    coverage = total_word_chars / max(1, len(text))
    
    return len(words_found), coverage, words_found[:15]

def score_ioc(plain_indices):
    """Compute IoC for the decrypted rune indices (29-alphabet)"""
    n = len(plain_indices)
    if n < 10:
        return 0.0
    freq = Counter(plain_indices)
    ioc = sum(f*(f-1) for f in freq.values()) / (n*(n-1))
    return ioc * 29  # Normalized to ~1.0 for random, ~1.73 for English GP

# Load all pages
print("\nLoading pages...")
pages = {}
for pn in range(0, 75):
    path = f'LiberPrimus/pages/page_{pn:02d}/runes.txt'
    if not os.path.exists(path):
        continue
    runes = load_runes(path)
    if len(runes) >= 20:
        pages[pn] = runes

print(f"Loaded {len(pages)} pages")

# ===== PHASE 1: Quick scan with key offset 0 =====
print("\n" + "="*80)
print("PHASE 1: TOTIENT SUB (key offset 0) ON ALL PAGES")
print("="*80)

results = []
for pn in sorted(pages):
    runes = pages[pn]
    plain = decrypt_totient(runes, 0, -1)
    if plain is None: continue
    text = to_runeglish(plain)
    ioc = score_ioc(plain)
    nw, cov, words = score_english(text)
    results.append((cov, nw, ioc, pn, text[:100], words))

results.sort(reverse=True)
print(f"\nTop 15 pages by English coverage at offset 0:")
for cov, nw, ioc, pn, snippet, words in results[:15]:
    print(f"  P{pn:02d}: coverage={cov:.2%}, words={nw}, IoC={ioc:.3f}")
    print(f"    Text: {snippet[:80]}")
    if words:
        print(f"    Words: {', '.join(words[:10])}")

# ===== PHASE 2: Try ADD direction too =====
print("\n" + "="*80)
print("PHASE 2: TOTIENT ADD (key offset 0) ON ALL PAGES")
print("="*80)

results2 = []
for pn in sorted(pages):
    runes = pages[pn]
    plain = decrypt_totient(runes, 0, +1)
    if plain is None: continue
    text = to_runeglish(plain)
    ioc = score_ioc(plain)
    nw, cov, words = score_english(text)
    results2.append((cov, nw, ioc, pn, text[:100], words))

results2.sort(reverse=True)
print(f"\nTop 10 pages by English coverage (ADD, offset 0):")
for cov, nw, ioc, pn, snippet, words in results2[:10]:
    print(f"  P{pn:02d}: coverage={cov:.2%}, words={nw}, IoC={ioc:.3f}")
    print(f"    Text: {snippet[:80]}")

# ===== PHASE 3: Scan key offsets 0-5000 for unsolved pages =====
print("\n" + "="*80)
print("PHASE 3: KEY OFFSET SCAN (0-5000) FOR PAGES 18-54")
print("="*80)

OFFSET_RANGE = 5000
best_per_page = {}
t0 = time.time()

for pn in sorted(pages):
    if pn < 18 or pn > 54:
        continue
    runes = pages[pn]
    n = len(runes)
    best = (0, 0, 0, 0, '', [])  # (cov, nw, ioc, offset, text, words)
    
    for offset in range(OFFSET_RANGE):
        # Try SUB
        plain = decrypt_totient(runes, offset, -1)
        if plain is None: break
        text = to_runeglish(plain)
        nw, cov, words = score_english(text)
        if cov > best[0] or (cov == best[0] and nw > best[1]):
            ioc = score_ioc(plain)
            best = (cov, nw, ioc, offset, text[:150], words, 'SUB')
        
        # Try ADD
        plain = decrypt_totient(runes, offset, +1)
        if plain is None: break
        text = to_runeglish(plain)
        nw, cov, words = score_english(text)
        if cov > best[0] or (cov == best[0] and nw > best[1]):
            ioc = score_ioc(plain)
            best = (cov, nw, ioc, offset, text[:150], words, 'ADD')
    
    best_per_page[pn] = best
    elapsed = time.time() - t0
    if len(best_per_page) % 5 == 0:
        print(f"  Progress: {len(best_per_page)} pages done ({elapsed:.1f}s)")

print(f"\nDone! ({time.time()-t0:.1f}s)")
print(f"\nBest results per page (sorted by coverage):")
sorted_results = sorted(best_per_page.items(), key=lambda x: x[1][0], reverse=True)
for pn, (cov, nw, ioc, offset, text, words, direction) in sorted_results:
    if cov > 0.15:  # Only show pages with >15% English word coverage
        print(f"\n  P{pn:02d}: coverage={cov:.2%}, words={nw}, IoC={ioc:.3f}, offset={offset}, dir={direction}")
        print(f"    Text: {text[:120]}")
        if words:
            print(f"    Words: {', '.join(words[:12])}")

# Also show all pages with their best score
print(f"\n--- All pages summary (sorted by coverage) ---")
for pn, (cov, nw, ioc, offset, text, words, direction) in sorted_results:
    marker = "***" if cov > 0.30 else "  *" if cov > 0.20 else "   "
    print(f"  {marker} P{pn:02d}: cov={cov:.2%} nw={nw:3d} IoC={ioc:.3f} off={offset:5d} {direction}")

# ===== PHASE 4: Beaufort variant =====
print("\n" + "="*80)
print("PHASE 4: BEAUFORT VARIANT (key-cipher % 29)")  
print("="*80)

# Beaufort: plain = (tot - cipher) % 29
def decrypt_beaufort(cipher_runes, key_offset):
    key_idx = key_offset
    plain = []
    for c in cipher_runes:
        if c == 0:  # F-skip
            plain.append(0)
            continue
        if key_idx >= len(TOT):
            return None
        k = TOT[key_idx]
        p = (k - c) % 29
        plain.append(p)
        key_idx += 1
    return plain

# Quick scan for unsolved pages
best_beaufort = {}
for pn in sorted(pages):
    if pn < 18 or pn > 54: continue
    runes = pages[pn]
    best = (0, 0, 0, 0, '', [])
    for offset in range(OFFSET_RANGE):
        plain = decrypt_beaufort(runes, offset)
        if plain is None: break
        text = to_runeglish(plain)
        nw, cov, words = score_english(text)
        if cov > best[0] or (cov == best[0] and nw > best[1]):
            ioc = score_ioc(plain)
            best = (cov, nw, ioc, offset, text[:150], words)
    best_beaufort[pn] = best

sorted_beau = sorted(best_beaufort.items(), key=lambda x: x[1][0], reverse=True)
print(f"\nBeau top results:")
for pn, (cov, nw, ioc, offset, text, words) in sorted_beau[:10]:
    marker = "***" if cov > 0.30 else "  *" if cov > 0.20 else "   "
    print(f"  {marker} P{pn:02d}: cov={cov:.2%} nw={nw:3d} IoC={ioc:.3f} off={offset:5d}")
    if cov > 0.20:
        print(f"      Text: {text[:120]}")
        if words: print(f"      Words: {', '.join(words[:10])}")

print("\nDONE")
