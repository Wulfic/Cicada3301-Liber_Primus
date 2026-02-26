#!/usr/bin/env python3
"""
Structural & Steganographic Analysis
=====================================
Investigate elements BEYOND the rune values:
1. Page numbering: check if page_00 == page_17 content
2. Special characters (& $ etc.) on each page
3. F-rune positions and their patterns
4. Word lengths (dot/dash separated)
5. Digit-rearranged primes as substitution/key
6. First/last rune patterns across pages
7. Rune text vs word boundary analysis
"""
import os, sys, io, math, re
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GP_RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C2\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11
MOD = 29
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

def load_raw(page_num):
    """Load raw text including separators and special chars."""
    f = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num:02d}\\runes.txt"
    if not os.path.exists(f): return None
    with open(f, 'r', encoding='utf-8') as fh:
        return fh.read()

def load_runes(page_num):
    f = f"c:\\Users\\tyler\\Repos\\Cicada3301\\LiberPrimus\\pages\\page_{page_num:02d}\\runes.txt"
    if not os.path.exists(f): return None
    with open(f, 'r', encoding='utf-8') as fh:
        return [GP_RUNE_TO_IDX[c] for c in fh.read() if c in GP_RUNE_TO_IDX]

def ioc(v):
    if len(v)<2: return 0
    c=Counter(v); n=len(v)
    return sum(x*(x-1) for x in c.values())/(n*(n-1))*MOD

def to_text(idx):
    return ''.join(GP_LETTERS[i] for i in idx)

COMMON_WORDS = {"THE","AND","FOR","ARE","NOT","YOU","ALL","HER","WAS","ONE",
    "OUR","OUT","HAS","HIS","HOW","MAN","NEW","NOW","OLD","SEE","WAY","WHO",
    "DID","GET","HIM","LET","SAY","SHE","TOO","BUT","CAN","HAD","ITS","MAY",
    "WILL","EACH","MAKE","LIKE","SOME","THEM","THAN","BEEN","HAVE","FROM",
    "INTO","WITH","THAT","THIS","WHAT","WHEN","THEY","COME","MADE","FIND",
    "MORE","ONLY","JUST","OVER","SUCH","ALSO","VERY","AFTER","BEING","THEIR",
    "THESE","THOSE","UNDER","ABOUT","COULD","EVERY","FIRST","SHALL","THERE",
    "THINK","WHERE","WHICH","WHILE","WORLD","WOULD","MIGHT","NEVER","STILL",
    "TRUTH","KNOW","MUST","SELF","SOUL","MIND","LIFE","DEAD","FEAR","FIRE",
    "FORM","GOOD","LORD","KING","WISE","WORD","WORK","PATH","RUNE",
    "WITHIN","FOLLOW","PILGRIM","WISDOM","CONSUMPTION","CIRCUMFERENCE",
    "PRIMES","NUMBERS","REARRANGING","SHOW","DEOR","DIVINITY","INSTAR",
    "SACRED","TOTIENT","FUNCTION","EMERGE","PARABLE","TUNNELING","SURFACE",
    "SHED","KOAN","MASTER","STUDY","INSTRUCTION","COMMAND","LOSS","PRESERVE"}

def word_score(text):
    sc=0; tu=text.upper()
    for w in COMMON_WORDS:
        st=0
        while True:
            p=tu.find(w,st)
            if p<0: break
            sc+=len(w); st=p+1
    return sc

# =========================================================================
# SECTION 1: Page numbering check — is page_00 the same as page_17?
# =========================================================================
print("="*80)
print("SECTION 1: Page content comparison")
print("="*80)

for pair in [(0, 17), (1, 59), (5, 63), (6, 64), (10, 68)]:
    p1, p2 = pair
    r1 = load_runes(p1)
    r2 = load_runes(p2)
    if r1 and r2:
        match = r1 == r2
        alike = sum(1 for a, b in zip(r1, r2) if a == b) if min(len(r1), len(r2)) > 0 else 0
        print(f"  page_{p1:02d} ({len(r1)} runes) vs page_{p2:02d} ({len(r2)} runes): "
              f"identical={match}, matching={alike}/{min(len(r1),len(r2))}")

# =========================================================================
# SECTION 2: Special characters in rune text
# =========================================================================
print("\n" + "="*80)
print("SECTION 2: Special characters analysis")
print("="*80)

for pn in range(0, 75):
    raw = load_raw(pn)
    if not raw:
        continue
    # Find non-rune, non-separator characters
    special = []
    rune_chars = set(GP_RUNES) | {'\u16C4'}
    separators = {'-', '.', '\u2022', '\n', '\r', ' ', '\t'}  # bullet point
    for i, c in enumerate(raw):
        if c not in rune_chars and c not in separators:
            special.append((i, c, repr(c)))
    
    if special:
        # Count separator types
        has_dots = raw.count('\u2022') + raw.count('.')
        has_dashes = raw.count('-')
        sep_type = []
        if has_dots > 0: sep_type.append(f"dots({has_dots})")
        if has_dashes > 0: sep_type.append(f"dashes({has_dashes})")
        
        runes = load_runes(pn)
        nrunes = len(runes) if runes else 0
        
        print(f"\n  Page {pn:2d} ({nrunes} runes, seps: {','.join(sep_type) if sep_type else 'none'}):")
        for pos, ch, repr_ch in special:
            print(f"    pos={pos}: '{ch}' ({repr_ch}, ord={ord(ch)})")

# =========================================================================
# SECTION 3: F-rune positions on unsolved pages
# =========================================================================
print("\n" + "="*80)
print("SECTION 3: F-rune analysis on unsolved pages")
print("="*80)

for pn in range(17, 55):
    runes = load_runes(pn)
    if not runes:
        continue
    f_positions = [i for i, v in enumerate(runes) if v == 0]
    n = len(runes)
    f_count = len(f_positions)
    f_pct = 100 * f_count / n if n > 0 else 0
    expected = n / 29  # Expected under uniform distribution
    
    # Check if F positions form a pattern
    f_gaps = [f_positions[i+1] - f_positions[i] for i in range(len(f_positions)-1)]
    
    line = f"  P{pn:2d}: {n:4d} runes, {f_count:3d} F ({f_pct:.1f}%, expected={expected:.1f})"
    if f_count > 0:
        line += f", avg_gap={sum(f_gaps)/len(f_gaps):.1f}" if f_gaps else ""
        # Check for periodic F positions
        if f_gaps:
            gap_mode = Counter(f_gaps).most_common(1)[0]
            line += f", mode_gap={gap_mode[0]}(x{gap_mode[1]})"
    print(line)

# =========================================================================
# SECTION 4: Word length analysis
# =========================================================================
print("\n" + "="*80)
print("SECTION 4: Word length patterns")
print("="*80)

for pn in range(17, 55):
    raw = load_raw(pn)
    if not raw:
        continue
    
    # Split by separators (dots, dashes, spaces, newlines)
    words = re.split(r'[-.\u2022\s]+', raw)
    # Convert each word to rune indices
    word_lens = []
    for w in words:
        rune_count = sum(1 for c in w if c in GP_RUNE_TO_IDX)
        if rune_count > 0:
            word_lens.append(rune_count)
    
    if word_lens:
        total = sum(word_lens)
        avg = sum(word_lens) / len(word_lens)
        print(f"  P{pn:2d}: {total:4d} runes in {len(word_lens):3d} words, "
              f"avg={avg:.1f}, lens={word_lens[:20]}{'...' if len(word_lens)>20 else ''}")

# =========================================================================
# SECTION 5: Digit-rearranged primes cipher
# =========================================================================
print("\n" + "="*80)
print("SECTION 5: Digit-rearranged primes cipher")
print("="*80)

def reverse_digits(n):
    return int(str(n)[::-1])

# Build rearranged prime substitution table
rearranged = [reverse_digits(GP_PRIMES[i]) % MOD for i in range(29)]
print(f"GP_PRIMES:   {GP_PRIMES}")
print(f"Reversed:    {[reverse_digits(p) for p in GP_PRIMES]}")
print(f"Rev mod 29:  {rearranged}")

# Check if this creates a valid permutation
rev_perm = rearranged
print(f"Unique values: {len(set(rev_perm))} (need 29 for bijection)")
dupes = {v: [i for i in range(29) if rev_perm[i] == v] for v in set(rev_perm) if rev_perm.count(v) > 1}
print(f"Duplicate mappings: {dupes}")

# Try as substitution on each unsolved page
for pn in range(17, 55):
    runes = load_runes(pn)
    if not runes or len(runes) < 30:
        continue
    
    # Forward substitution: replace each rune value with rearranged value
    subst = [rearranged[v] for v in runes]
    ic_s = ioc(subst)
    txt_s = to_text(subst)
    ws_s = word_score(txt_s)
    
    if ic_s > 1.2 or ws_s > 30:
        print(f"  P{pn} fwd_subst: IoC={ic_s:.3f} ws={ws_s}")
        print(f"    {txt_s[:80]}")
    
    # Try as Vigenere key (cycling rearranged primes as key)
    key = rearranged  # Length 29, cycle over message
    for mode in ["SUB", "ADD"]:
        if mode == "SUB":
            plain = [(runes[i] - key[i % 29]) % MOD for i in range(len(runes))]
        else:
            plain = [(runes[i] + key[i % 29]) % MOD for i in range(len(runes))]
        ic = ioc(plain)
        txt = to_text(plain)
        ws = word_score(txt)
        if ic > 1.2 or ws > 30:
            print(f"  P{pn} rev_prime_vig/{mode}: IoC={ic:.3f} ws={ws}")
            print(f"    {txt[:80]}")

# Also try: sum of digits of each prime as key
digit_sums = [sum(int(d) for d in str(GP_PRIMES[i])) % MOD for i in range(29)]
print(f"\nDigit sums mod 29: {digit_sums}")

for pn in range(17, 55):
    runes = load_runes(pn)
    if not runes or len(runes) < 30:
        continue
    for mode in ["SUB", "ADD"]:
        if mode == "SUB":
            plain = [(runes[i] - digit_sums[i % 29]) % MOD for i in range(len(runes))]
        else:
            plain = [(runes[i] + digit_sums[i % 29]) % MOD for i in range(len(runes))]
        ic = ioc(plain)
        if ic > 1.2:
            txt = to_text(plain)
            ws = word_score(txt)
            print(f"  P{pn} digit_sum/{mode}: IoC={ic:.3f} ws={ws}")

# =========================================================================
# SECTION 6: First/last rune patterns across pages
# =========================================================================
print("\n" + "="*80)
print("SECTION 6: First/last rune patterns")
print("="*80)

print("  First rune of each unsolved page:")
firsts = []
lasts = []
for pn in range(17, 55):
    runes = load_runes(pn)
    if not runes:
        continue
    first = runes[0]
    last = runes[-1]
    firsts.append(first)
    lasts.append(last)
    print(f"    P{pn}: first={GP_LETTERS[first]}({first}), last={GP_LETTERS[last]}({last})")

print(f"\n  First rune values: {firsts}")
print(f"  First rune text: {to_text(firsts)}")
print(f"  Last rune values: {lasts}")
print(f"  Last rune text: {to_text(lasts)}")

# =========================================================================
# SECTION 7: Separator-aware analysis 
# =========================================================================
print("\n" + "="*80)
print("SECTION 7: P18 word-level analysis")
print("="*80)

raw_18 = load_raw(18)
if raw_18:
    # Split into words
    words_18 = re.split(r'[-.\u2022\s]+', raw_18)
    rune_words = []
    for w in words_18:
        word_runes = [GP_RUNE_TO_IDX[c] for c in w if c in GP_RUNE_TO_IDX]
        if word_runes:
            rune_words.append(word_runes)
    
    print(f"P18: {len(rune_words)} words")
    print(f"Word lengths: {[len(w) for w in rune_words]}")
    
    # Check if word lengths encode information
    wl = [len(w) for w in rune_words]
    # Could word lengths be a key?
    print(f"Sum of lengths: {sum(wl)}")
    print(f"Word length sequence mod 29: {[l % 29 for l in wl]}")
    
    # Check: are word lengths prime?
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0: return False
        return True
    
    prime_word_lens = [(i, l) for i, l in enumerate(wl) if is_prime(l)]
    print(f"Prime-length words: {len(prime_word_lens)}/{len(wl)} ({[l for _, l in prime_word_lens]})")
    
    # First rune of each word
    word_firsts = [w[0] for w in rune_words]
    print(f"First rune of each word: {to_text(word_firsts)}")
    print(f"First rune values: {word_firsts}")
    ws_wf = word_score(to_text(word_firsts))
    ic_wf = ioc(word_firsts)
    print(f"IoC of word firsts: {ic_wf:.3f}, ws={ws_wf}")
    
    # Last rune of each word
    word_lasts = [w[-1] for w in rune_words]
    print(f"Last rune of each word: {to_text(word_lasts)}")
    ic_wl = ioc(word_lasts)
    print(f"IoC of word lasts: {ic_wl:.3f}")

# =========================================================================
# SECTION 8: Cross-page acrostic check
# =========================================================================
print("\n" + "="*80)
print("SECTION 8: Cross-page patterns (first words)")
print("="*80)

for pn in range(17, 55):
    raw = load_raw(pn)
    if not raw:
        continue
    words = re.split(r'[-.\u2022\s]+', raw)
    rune_words = []
    for w in words:
        wr = [GP_RUNE_TO_IDX[c] for c in w if c in GP_RUNE_TO_IDX]
        if wr:
            rune_words.append(wr)
    
    if rune_words:
        first_word = to_text(rune_words[0])
        first_rune = GP_LETTERS[rune_words[0][0]]
        print(f"  P{pn:2d}: first_word='{first_word}' (len={len(rune_words[0])}), "
              f"#words={len(rune_words)}")

# =========================================================================
# SECTION 9: Rearranged primes as a path index
# =========================================================================
print("\n" + "="*80)
print("SECTION 9: Primes rearranged as path through text")
print("="*80)

# What if we take the N-th prime, reverse its digits, and use that as
# a position index into the cipher text?
def sieve_primes(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(2,n+1) if s[i]]
PRIMES = sieve_primes(50000)

# Try: for P18 (260 runes), read runes at positions = reversed primes
p18 = load_runes(18)
if p18:
    print(f"\nP18 ({len(p18)} runes):")
    for method in ["rev_prime_pos", "prime_pos", "rev_prime_mod_n"]:
        selected = []
        positions = []
        for i in range(len(p18)):
            if method == "rev_prime_pos":
                pos = reverse_digits(PRIMES[i]) % len(p18)
            elif method == "prime_pos":
                pos = PRIMES[i] % len(p18)
            elif method == "rev_prime_mod_n":
                pos = (reverse_digits(PRIMES[i]) - 1) % len(p18)
            
            if pos not in positions:  # Only take first occurrence
                selected.append(p18[pos])
                positions.append(pos)
        
        txt = to_text(selected[:50])
        ic = ioc(selected) if len(selected) > 2 else 0
        ws = word_score(txt)
        print(f"  {method}: {len(selected)} chars, IoC={ic:.3f} ws={ws}")
        print(f"    {txt}")

# =========================================================================
# SECTION 10: GP value-based operations (prime arithmetic)
# =========================================================================
print("\n" + "="*80)
print("SECTION 10: Prime-value arithmetic")  
print("="*80)

# Instead of index-based operations, try:
# cipher_prime_value / key_prime_value in the prime field
# or: find x such that GP_PRIMES[x] = GP_PRIMES[cipher] + GP_PRIMES[key]

# Approach: convert cipher to prime values, apply arithmetic, convert back
prime_to_idx = {p: i for i, p in enumerate(GP_PRIMES)}

for pn in [18, 19, 20, 21]:
    runes = load_runes(pn)
    if not runes:
        continue
    n = len(runes)
    
    # Method 1: Add adjacent primes
    cipher_primes = [GP_PRIMES[v] for v in runes]
    
    # Method 2: Multiply adjacent cipher values and reduce
    for method in ["prime_add_const", "prime_mult_inv", "prime_log"]:
        for param in range(1, 30):
            plain = []
            valid = True
            for i in range(n):
                cp = cipher_primes[i]
                if method == "prime_add_const":
                    # Find rune whose prime = (cipher_prime + param) mod some_value
                    target = (cp + param)
                    # Find closest GP prime
                    for pr_idx, pr_val in enumerate(GP_PRIMES):
                        if pr_val == target % 113:  # 113 is prime > 109
                            plain.append(pr_idx)
                            break
                    else:
                        # Map to closest
                        diffs = [abs(pr_val - (target % 113)) for pr_val in GP_PRIMES]
                        plain.append(diffs.index(min(diffs)))
                elif method == "prime_mult_inv":
                    if param > 1:
                        valid = False
                        break
                    # XOR prime values of adjacent runes
                    if i + 1 < n:
                        p1 = cipher_primes[i]
                        p2 = cipher_primes[i+1]
                        result = (p1 ^ p2) % MOD
                        plain.append(result)
                    break
                elif method == "prime_log":
                    if param > 1:
                        valid = False
                        break
                    # Discrete log: find x such that 2^x = cipher_prime mod 29
                    # This is related to the primitive root
                    found = False
                    for x in range(MOD):
                        if pow(2, x, MOD * 4) == cp % (MOD * 4):
                            plain.append(x % MOD)
                            found = True
                            break
                    if not found:
                        plain.append(0)
                    break
            
            if not valid or len(plain) < 10:
                continue
            
            if method == "prime_add_const":
                ic = ioc(plain)
                txt = to_text(plain)
                ws = word_score(txt)
                if ic > 1.2 or ws > 25:
                    print(f"  P{pn}/{method}/param={param}: IoC={ic:.3f} ws={ws}")
                    print(f"    {txt[:80]}")
            break  # Only run param=1 for non-const methods

print("\n" + "="*80)
print("SECTION 11: Checking for interleaving / multi-stream")
print("="*80)

# What if the ciphertext is actually TWO messages interleaved?
# Extract even-position and odd-position runes, check IoC separately
for pn in range(17, 55):
    runes = load_runes(pn)
    if not runes or len(runes) < 50:
        continue
    
    for stride in [2, 3, 5, 7]:
        streams = [[] for _ in range(stride)]
        for i, v in enumerate(runes):
            streams[i % stride].append(v)
        
        iocs = [ioc(s) for s in streams]
        avg_ioc = sum(iocs) / stride
        
        if avg_ioc > 1.3:
            print(f"  P{pn} stride={stride}: avg_IoC={avg_ioc:.3f} ({', '.join(f'{x:.2f}' for x in iocs)})")
            for j, s in enumerate(streams):
                txt = to_text(s)
                ws = word_score(txt)
                if ws > 15:
                    print(f"    stream {j}: ws={ws} {txt[:60]}")

print("\nDONE")
