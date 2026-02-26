"""
Small page analysis - P49, P52, P53, P54, P71
Key finding: P71 = P53+P54 concatenation with decoded.txt available
"""
import sys, io, os
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
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

def read_runes(path):
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    return raw, runes

def compute_ioc(vals, alphabet_size=29):
    n = len(vals)
    if n < 2: return 0
    counts = Counter(vals)
    ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
    return ic * alphabet_size

def kasiski_ioc(runes, max_k=60):
    """Compute average column IoC for each period k"""
    results = []
    n = len(runes)
    for k in range(2, min(max_k+1, n//2+1)):
        cols_ioc = []
        for col in range(k):
            column = [runes[i] for i in range(col, n, k)]
            if len(column) >= 2:
                cols_ioc.append(compute_ioc(column))
        avg_ioc = sum(cols_ioc)/len(cols_ioc) if cols_ioc else 0
        results.append((k, avg_ioc))
    return results

def parse_words(raw):
    """Parse words from raw rune text, returning list of (word_rune_indices)"""
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
    return words

# ============================================================
# Read all pages
# ============================================================
pages = {}
for pn in [49, 52, 53, 54, 71, 33]:
    path = f'LiberPrimus/pages/page_{pn}/runes.txt'
    if os.path.exists(path):
        raw, runes = read_runes(path)
        words = parse_words(raw)
        pages[pn] = {'raw': raw, 'runes': runes, 'words': words}
        print(f"Page {pn}: {len(runes)} runes, {len(words)} words")

# ============================================================
# VERIFY: P71 = P53 + P54 ?
# ============================================================
print("\n" + "=" * 70)
print("VERIFY: P71 = P53 + P54 concatenation?")
print("=" * 70)

p53_runes = pages[53]['runes']
p54_runes = pages[54]['runes']
p71_runes = pages[71]['runes']
concat = p53_runes + p54_runes

print(f"P53: {len(p53_runes)} runes")
print(f"P54: {len(p54_runes)} runes")
print(f"P53+P54: {len(concat)} runes")
print(f"P71: {len(p71_runes)} runes")

if concat == p71_runes:
    print("✓ EXACT MATCH: P71 runes = P53 + P54 runes")
else:
    # Find mismatches
    min_len = min(len(concat), len(p71_runes))
    mismatches = [(i, concat[i] if i < len(concat) else None, p71_runes[i] if i < len(p71_runes) else None) 
                  for i in range(max(len(concat), len(p71_runes))) 
                  if i >= min_len or concat[i] != p71_runes[i]]
    print(f"✗ MISMATCH: {len(mismatches)} differences")
    for pos, cv, pv in mismatches[:10]:
        print(f"  pos {pos}: concat={cv}({LAT[cv] if cv is not None else '?'}) vs p71={pv}({LAT[pv] if pv is not None else '?'})")

# ============================================================
# P71 decoded text analysis
# ============================================================
print("\n" + "=" * 70)
print("P71 DECODED TEXT ANALYSIS")
print("=" * 70)

decoded_text = "SOMEWISDOMAMASSGREATWEALTHNEUERBECOMEATTACHEDTOWHATYOUOWNBEPREPAREDTODESTROYALLTHATYOUOWN"
decoded_gp = eng_to_gp(decoded_text)
print(f"Decoded text: {decoded_text}")
print(f"Decoded GP length: {len(decoded_gp)} runes")
print(f"P71 cipher length: {len(p71_runes)} runes")
print(f"Ratio: {len(p71_runes)/len(decoded_gp):.2f}x")

# Try known-plaintext attack: Vigenère SUB
# If plaintext matches start of ciphertext...
print(f"\nKnown-plaintext key recovery (Vigenère SUB, first {len(decoded_gp)} positions):")
kp_key = [(p71_runes[i] - decoded_gp[i]) % MOD for i in range(len(decoded_gp))]
print(f"Key values: {kp_key}")
key_text = ''.join(LAT[v] for v in kp_key)
print(f"Key as rune text: {key_text}")

# Check if key has periodic structure
print("\n  Key periodicity check:")
for period in range(2, 30):
    if len(kp_key) < period * 2:
        continue
    match = all(kp_key[i] == kp_key[i % period] for i in range(period, len(kp_key)))
    if match:
        print(f"  PERIODIC with period {period}: {kp_key[:period]}")
        # Decrypt full text with this key
        full_dec = [(p71_runes[i] - kp_key[i % period]) % MOD for i in range(len(p71_runes))]
        full_text = ''.join(LAT[v] for v in full_dec)
        ioc = compute_ioc(full_dec)
        print(f"  Full decryption IoC*29: {ioc:.3f}")
        print(f"  Full decryption: {full_text[:150]}...")

# Try ADD mode
print(f"\nKnown-plaintext key recovery (Vigenère ADD, first {len(decoded_gp)} positions):")
kp_key_add = [(decoded_gp[i] - p71_runes[i]) % MOD for i in range(len(decoded_gp))]
print(f"Key values: {kp_key_add}")

for period in range(2, 30):
    if len(kp_key_add) < period * 2:
        continue
    match = all(kp_key_add[i] == kp_key_add[i % period] for i in range(period, len(kp_key_add)))
    if match:
        print(f"  PERIODIC ADD with period {period}: {kp_key_add[:period]}")
        full_dec = [(p71_runes[i] + kp_key_add[i % period]) % MOD for i in range(len(p71_runes))]
        full_text = ''.join(LAT[v] for v in full_dec)
        ioc = compute_ioc(full_dec)
        print(f"  Full decryption IoC*29: {ioc:.3f}")
        print(f"  Full decryption: {full_text[:150]}...")

# Try Beaufort mode
print(f"\nKnown-plaintext key recovery (Beaufort: key = cipher + plain):")
kp_key_beau = [(p71_runes[i] + decoded_gp[i]) % MOD for i in range(len(decoded_gp))]
for period in range(2, 30):
    if len(kp_key_beau) < period * 2:
        continue
    match = all(kp_key_beau[i] == kp_key_beau[i % period] for i in range(period, len(kp_key_beau)))
    if match:
        print(f"  PERIODIC BEAU with period {period}: {kp_key_beau[:period]}")

# Try: maybe the decoded text is wrong and the ACTUAL plaintext starts elsewhere?
# Or maybe it's a running-key / autokey

# Try autokey: key = initial_key || plaintext
# For autokey SUB: plain[i] = (cipher[i] - key_stream[i]) % 29
# where key_stream[i] = key[i] for i < k, key_stream[i] = plain[i-k] for i >= k
# If we know plaintext, key_stream[i] = plain[i-k] for i >= k
# So for i >= k: key_stream[i] = plaintext[i-k]
# And for i < k: key_stream[i] = (cipher[i] - plaintext[i]) % 29

# With decoded_gp as plaintext for first 85 positions:
# For an autokey, we'd need a short initial key, then the rest follows from plaintext
# Let's check if the KP key has autokey structure

print(f"\nAutokey structure check:")
# For autokey with period k: key_stream[i] = decoded_gp[i-k] for i >= k
# So (cipher[i] - decoded_gp[i]) % 29 = decoded_gp[i-k] for i >= k
for k_try in range(2, 50):
    matches = 0
    total = 0
    for i in range(k_try, len(decoded_gp)):
        expected_key = decoded_gp[i - k_try]
        actual_key = (p71_runes[i] - decoded_gp[i]) % MOD
        if expected_key == actual_key:
            matches += 1
        total += 1
    if total > 0 and matches == total:
        print(f"  PERFECT AUTOKEY with initial key length {k_try}!")
        initial_key = [(p71_runes[i] - decoded_gp[i]) % MOD for i in range(k_try)]
        print(f"  Initial key: {initial_key}")
        print(f"  Key text: {''.join(LAT[v] for v in initial_key)}")
        
        # Now decrypt FULL P71 with this autokey
        full_plain = []
        for i in range(len(p71_runes)):
            if i < k_try:
                key_val = initial_key[i]
            else:
                key_val = full_plain[i - k_try]
            full_plain.append((p71_runes[i] - key_val) % MOD)
        
        full_text = ''.join(LAT[v] for v in full_plain)
        ioc = compute_ioc(full_plain)
        print(f"  Full decryption IoC*29: {ioc:.3f}")
        print(f"  Full text: {full_text[:300]}")
        print(f"  Full text cont: {full_text[300:]}")
        break
    elif total > 0 and matches / total > 0.8:
        print(f"  Near-autokey k={k_try}: {matches}/{total} ({100*matches/total:.1f}%)")

# ============================================================
# IoC analysis for each page
# ============================================================
print("\n" + "=" * 70)
print("IoC ANALYSIS FOR SMALL PAGES")
print("=" * 70)

for pn in [33, 49, 52, 53, 54]:
    runes = pages[pn]['runes']
    n = len(runes)
    raw_ioc = compute_ioc(runes)
    print(f"\nPage {pn}: {n} runes, raw IoC*29 = {raw_ioc:.3f}")
    
    # Find best periods
    results = kasiski_ioc(runes, max_k=min(n//2, 80))
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"  Top 10 periods by avg column IoC:")
    for k, ioc in results[:10]:
        col_sizes = [len([1 for i in range(col, n, k)]) for col in range(k)]
        min_cs = min(col_sizes)
        print(f"    k={k:3d}: IoC={ioc:.3f} (columns have {min_cs}-{max(col_sizes)} entries)")

# ============================================================
# P53+P54 = P71: try decrypting with various approaches
# ============================================================
print("\n" + "=" * 70)
print("P53+P54 CIPHER ANALYSIS")
print("=" * 70)

# Try Caesar (shift=0 = cleartext)
for shift in range(MOD):
    dec = [(v - shift) % MOD for v in p71_runes]
    text = ''.join(LAT[v] for v in dec)
    # Check for common English patterns
    has_the = 'THE' in text[:100]
    has_and = 'AND' in text[:100]
    ioc = compute_ioc(dec)
    if has_the or has_and or ioc > 1.5:
        print(f"  Caesar shift {shift}: IoC={ioc:.3f}, text={text[:80]}...")

# Cleartext test (shift=0)
dec0 = p71_runes
text0 = ''.join(LAT[v] for v in dec0)
print(f"\n  Caesar-0 (cleartext): {text0[:100]}...")

# Atbash 
dec_atbash = [(28 - v) % MOD for v in p71_runes]
text_atbash = ''.join(LAT[v] for v in dec_atbash)
ioc_atbash = compute_ioc(dec_atbash)
print(f"  Atbash: IoC={ioc_atbash:.3f}, {text_atbash[:100]}...")

# Atbash + each Caesar
for shift in range(MOD):
    dec = [(28 - v + shift) % MOD for v in p71_runes]
    text = ''.join(LAT[v] for v in dec)
    ioc = compute_ioc(dec)
    if 'THE' in text[:80] or ioc > 1.5:
        print(f"  Atbash+Caesar{shift}: IoC={ioc:.3f}, {text[:80]}...")

# ============================================================
# P49 analysis
# ============================================================
print("\n" + "=" * 70)
print("P49 DETAILED ANALYSIS")
print("=" * 70)

p49_runes = pages[49]['runes']
p49_words = pages[49]['words']
n49 = len(p49_runes)

# Word structure
print(f"P49: {n49} runes, {len(p49_words)} words")
word_lens = [len(w) for w in p49_words]
print(f"Word lengths: {word_lens}")

# Caesar scan
print("\nCaesar scan:")
for shift in range(MOD):
    dec = [(v - shift) % MOD for v in p49_runes]
    text = ''.join(LAT[v] for v in dec)
    ioc = compute_ioc(dec)
    # Parse into words
    words_text = []
    for wpos in p49_words:
        w = ''.join(LAT[dec[i]] for i in wpos)
        words_text.append(w)
    if ioc > 1.2 or shift == 0:
        print(f"  shift={shift:2d}: IoC={ioc:.3f} words: {' '.join(words_text[:10])}...")

# Frequency analysis
freq = Counter(p49_runes)
print(f"\nFrequency distribution:")
for v, c in freq.most_common():
    print(f"  {LAT[v]:3s}({v:2d}): {c:2d} ({100*c/n49:.1f}%)")

# ============================================================
# Check P49 for Vigenère
# ============================================================
print("\nP49 Kasiski/IoC top periods:")
res = kasiski_ioc(p49_runes, 33)
res.sort(key=lambda x: x[1], reverse=True)
for k, ioc in res[:5]:
    print(f"  k={k}: avgIoC={ioc:.3f}")

# ============================================================
# P33 analysis  
# ============================================================
print("\n" + "=" * 70)
print("P33 DETAILED ANALYSIS")
print("=" * 70)

p33_runes = pages[33]['runes']
p33_raw = pages[33]['raw']
n33 = len(p33_runes)

# Check for & separator (multiple sections)
sections = p33_raw.split('&')
print(f"P33: {n33} runes, {len(sections)} sections")
for si, sec in enumerate(sections):
    sec_runes = [GP[c] for c in sec if c in GP]
    print(f"  Section {si}: {len(sec_runes)} runes")
    ioc = compute_ioc(sec_runes)
    print(f"    IoC*29 = {ioc:.3f}")

# Caesar scan
print("\nCaesar scan:")
for shift in range(MOD):
    dec = [(v - shift) % MOD for v in p33_runes]
    ioc = compute_ioc(dec)
    if ioc > 1.2:
        text = ''.join(LAT[v] for v in dec)
        print(f"  shift={shift:2d}: IoC={ioc:.3f} {text[:80]}...")

# Period analysis
print("\nP33 Kasiski top periods:")
res = kasiski_ioc(p33_runes, 60)
res.sort(key=lambda x: x[1], reverse=True)
for k, ioc in res[:8]:
    print(f"  k={k}: avgIoC={ioc:.3f}")

# Check each section independently
for si, sec in enumerate(sections):
    sec_runes = [GP[c] for c in sec if c in GP]
    if len(sec_runes) < 10:
        continue
    print(f"\n  Section {si} ({len(sec_runes)} runes) top periods:")
    res = kasiski_ioc(sec_runes, min(40, len(sec_runes)//2))
    res.sort(key=lambda x: x[1], reverse=True)
    for k, ioc in res[:5]:
        print(f"    k={k}: avgIoC={ioc:.3f}")

print("\nDONE")
