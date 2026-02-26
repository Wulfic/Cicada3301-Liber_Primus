"""
P54 Comprehensive Alternative Attack
=====================================
Exhaustive testing of non-standard-Vigenère approaches:
1. Running-key cipher with LP decoded text as key
2. Mathematical key sequences (primes, Fibonacci, totient, powers, etc.)
3. Full IoC re-analysis for all periods 1-38
4. Kasiski examination for repeated n-grams
5. Autokey brute-force with word-match scoring
6. Affine per-column cipher
7. Keyword Vigenère with every LP word
"""
import sys, functools, os, math
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print = functools.partial(print, flush=True)

# ===== CORRECT GP MAPPING =====
GP_RUNES = '\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0'
GP = {}
for i, r in enumerate(GP_RUNES):
    GP[r] = i
GP['\u16C2'] = 11  # alternate J

MOD = 29
IDX_TO_LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def gp_to_text(vals):
    return ''.join(IDX_TO_LAT[v] for v in vals)

def eng_to_gp(word):
    result = []
    i = 0
    w = word.upper()
    while i < len(w):
        matched = False
        for dg in ['TH','EA','OE','AE','NG','IA','EO']:
            if w[i:i+len(dg)] == dg:
                result.append(IDX_TO_LAT.index(dg))
                i += len(dg)
                matched = True
                break
        if not matched:
            ch = w[i]
            mapping = {'F':0,'U':1,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,
                       'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,
                       'M':19,'L':20,'D':23,'A':24,'Y':26,'V':1,'K':5,'Q':5,'Z':15}
            if ch in mapping:
                result.append(mapping[ch])
                i += 1
            else:
                return None
    return result

# ===== CIPHER DATA =====
cipher = [21, 25, 19, 10, 7, 15, 17, 14, 19, 15, 12, 6, 23, 2, 25, 0, 27, 24, 17, 5, 1, 7, 4, 17, 28, 0, 14, 10, 19, 1, 5, 13, 8, 21, 20, 12, 19, 15, 23, 27, 13, 0, 17, 8, 12, 5, 12, 18, 28, 18, 10, 6, 14, 6, 15, 18, 15, 12, 2, 2, 18, 15, 2, 22, 5, 28, 10, 19, 5, 14, 23, 11, 1, 17, 18, 10]
word_lens = [1, 4, 2, 2, 6, 6, 2, 1, 12, 6, 4, 2, 7, 7, 2, 4, 2, 3, 3]
N = len(cipher)
NW = len(word_lens)

# Word start positions
word_starts = []
pos = 0
for wl in word_lens:
    word_starts.append(pos)
    pos += wl

# ===== DICTIONARY =====
print("Loading dictionary...")
with open('wordlist.txt') as f:
    raw_words = f.read().strip().split('\n')
gp_dict = {}
for word in raw_words:
    word = word.strip().lower()
    if len(word) < 1 or len(word) > 25:
        continue
    gp = eng_to_gp(word)
    if gp is None:
        continue
    gplen = len(gp)
    if gplen < 1 or gplen > 15:
        continue
    gpt = tuple(gp)
    if gplen not in gp_dict:
        gp_dict[gplen] = set()
    gp_dict[gplen].add(gpt)
print(f"Dictionary loaded: {sum(len(v) for v in gp_dict.values())} GP words")

def count_word_matches(plain):
    """Count how many words in plain match dictionary entries."""
    matches = 0
    details = []
    for wi in range(NW):
        start = word_starts[wi]
        length = word_lens[wi]
        word_plain = tuple(plain[start:start + length])
        if length in gp_dict and word_plain in gp_dict[length]:
            matches += 1
            details.append(f"W{wi}={gp_to_text(word_plain)}")
    return matches, details

def decrypt_text(cipher, key_stream, mode='SUB'):
    """Decrypt using a key stream (not necessarily periodic)."""
    plain = []
    for i in range(len(cipher)):
        k = key_stream[i] % MOD
        if mode == 'SUB':
            plain.append((cipher[i] - k) % MOD)
        elif mode == 'ADD':
            plain.append((cipher[i] + k) % MOD)
        elif mode == 'BEAU':
            plain.append((k - cipher[i]) % MOD)
    return plain

def spaced_text(plain):
    parts = []
    pos = 0
    for wl in word_lens:
        parts.append(gp_to_text(plain[pos:pos+wl]))
        pos += wl
    return ' '.join(parts)

# ===== LP DECODED CORPUS =====
print("\nCollecting LP decoded texts...")
lp_corpus_text = {
    'p58': "SOME WISDOM IS NOT MEANT FOR EVERYONE",
    'p59': "A WARNING PARABLE CONSUMPTION SHALL BRING ABOUT THE RUIN",
    'p60': "WITHIN THE DEPTHS OF YOUR BEING IS THE TRUTH WITHIN THE SILENCE OF THE SELF THE WHISPER OF THE DIVINE THE ONLY PATH FORWARD IS WITHIN LET THE SEEKER LOOK WITHIN AND THE TRUTH WILL SHINE FORTH",
    'p61': "AN INSTRUCTION MEET WITH LIKE MINDS AND WELCOME ALL TO PARTAKE IN THE QUEST INSTAR FROM THE SOLITARY EMERGE TRANSFORMED IN COMMUNION",
    'p62': "AN INSTRUCTION SHARE FREELY ALL THAT HAS BEEN GIVEN BRING ALL THE PILGRIMS TO GATHER FOR THE FEAST OF THE MIND",
    'p63': "A COMMAND FORM YOURSELVES INTO GROUPS BE ORGANIZED LET EACH GROUP BE A TRIAD UNITED IN PURPOSE",
    'p67': "LIKE THE INSTAR IT IS THROUGH STRUGGLE THAT WE EMERGE SOME WISDOM IS A MASS GREAT WEALTH",
    'p68': "NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN",
    'p72': "IN THE END WISDOM COMES LOSS AND PRESERVATION WORKING TOGETHER",
    'p74': "A FINAL DIVINITY THE PRIMES ARE SACRED LET THE SEEKER CONTEMPLATE THE NATURE OF THE PRIME"
}

# Actual decoded.txt GP values (collected from files)
lp_decoded_gp = {}
for root, dirs, files in os.walk('.'):
    for f in files:
        if f == 'decoded.txt':
            fpath = os.path.join(root, f)
            parent = os.path.basename(root)
            try:
                with open(fpath, encoding='utf-8') as fh:
                    content = fh.read().strip()
                vals = []
                for ch in content:
                    if ch in GP:
                        vals.append(GP[ch])
                if len(vals) > 5:
                    lp_decoded_gp[parent] = vals
            except:
                pass

print(f"Found decoded.txt files: {list(lp_decoded_gp.keys())}")

# Build full LP corpus (all decoded GP values concatenated)
full_corpus = []
for name in sorted(lp_decoded_gp.keys()):
    full_corpus.extend(lp_decoded_gp[name])
print(f"Full LP corpus: {len(full_corpus)} GP values")

# ===== 1. RUNNING-KEY CIPHER WITH LP TEXT =====
print(f"\n{'='*80}")
print("1. RUNNING-KEY CIPHER (LP decoded text as key)")
print(f"{'='*80}")

THRESHOLD = 8

# Try each decoded page individually
for page_name, page_gp in lp_decoded_gp.items():
    if len(page_gp) < N:
        continue
    max_offset = len(page_gp) - N
    for offset in range(max_offset + 1):
        key_stream = page_gp[offset:offset + N]
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt_text(cipher, key_stream, mode)
            matches, details = count_word_matches(plain)
            if matches >= THRESHOLD:
                print(f"  {page_name} offset={offset} {mode}: {matches}/{NW} matches")
                print(f"    Text: {spaced_text(plain)}")
                print(f"    Matches: {', '.join(details)}")

# Try full corpus
if len(full_corpus) >= N:
    max_offset = len(full_corpus) - N
    for offset in range(max_offset + 1):
        key_stream = full_corpus[offset:offset + N]
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt_text(cipher, key_stream, mode)
            matches, details = count_word_matches(plain)
            if matches >= THRESHOLD:
                print(f"  FULL-CORPUS offset={offset} {mode}: {matches}/{NW} matches")
                print(f"    Text: {spaced_text(plain)}")
                print(f"    Matches: {', '.join(details)}")

print("Running-key scan complete.")

# ===== 2. MATHEMATICAL KEY SEQUENCES =====
print(f"\n{'='*80}")
print("2. MATHEMATICAL KEY SEQUENCES")
print(f"{'='*80}")

# Generate primes
def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

primes = sieve_primes(100000)

# GP primes (the primes associated with each GP rune)
gp_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

# Euler's totient
def totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

# Mathematical sequences to try as key streams
def gen_sequence(name, length, offset=0):
    """Generate mathematical sequences as potential key streams."""
    if name == 'primes':
        return [primes[offset + i] % MOD for i in range(length)]
    elif name == 'primes_minus_1':
        return [(primes[offset + i] - 1) % MOD for i in range(length)]
    elif name == 'totient_primes':
        return [totient(primes[offset + i]) % MOD for i in range(length)]
    elif name == 'fibonacci':
        fib = [1, 1]
        while len(fib) < length + offset:
            fib.append(fib[-1] + fib[-2])
        return [fib[offset + i] % MOD for i in range(length)]
    elif name == 'triangular':
        return [(((offset + i) * (offset + i + 1)) // 2) % MOD for i in range(length)]
    elif name == 'squares':
        return [((offset + i) ** 2) % MOD for i in range(length)]
    elif name == 'cubes':
        return [((offset + i) ** 3) % MOD for i in range(length)]
    elif name == 'powers_of_2':
        return [(2 ** (offset + i)) % MOD for i in range(length)]
    elif name == 'powers_of_3':
        return [(3 ** (offset + i)) % MOD for i in range(length)]
    elif name == 'factorial':
        val = 1
        vals = []
        for i in range(offset + length):
            val = val * (i + 1) 
            if i >= offset:
                vals.append(val % MOD)
        return vals
    elif name == 'prime_gaps':
        return [(primes[offset + i + 1] - primes[offset + i]) % MOD for i in range(length)]
    elif name == 'gp_primes_cycle':
        return [gp_primes[(offset + i) % 29] % MOD for i in range(length)]
    elif name == 'natural':
        return [(offset + i) % MOD for i in range(length)]
    elif name == 'catalan':
        # Catalan numbers
        def catalan(n):
            if n <= 1: return 1
            c = 1
            for i in range(n):
                c = c * 2 * (2 * i + 1) // (i + 2)
            return c
        return [catalan(offset + i) % MOD for i in range(length)]
    elif name == 'pi_digits':
        # First 200 digits of pi
        pi_str = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989"
        return [int(pi_str[offset + i]) % MOD for i in range(min(length, len(pi_str) - offset))]
    elif name == 'e_digits':
        e_str = "27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190115738341879307021540891499348841675092447614606680822648001684774118537423454424371075390777449920695517027618386062613313845830007520449338265602976067371132007093287091274437470472306969772093101416928368190255151086574637721112523897844250569536967707854499699679468644549059879316368892300987931277361782154249992295763514822082698951936680331825288693984964651058209392398294887933203625094431173012381970684161403970198376793206832823764648042953118023287825098194558153017567173613320698112509961818815930416903515988885193458072738667385894228792284998920868058257492796104841984443634632449684875602336248270419786232090021609902353043699418491463140934317381436405462531520961836908887070167683964243781405927145635490613031072085103837505101157477041718986106873969655212671546889570350354"
        return [int(e_str[offset + i]) % MOD for i in range(min(length, len(e_str) - offset))]
    return None

seq_names = ['primes', 'primes_minus_1', 'totient_primes', 'fibonacci', 'triangular', 
             'squares', 'cubes', 'powers_of_2', 'powers_of_3', 'prime_gaps',
             'gp_primes_cycle', 'natural', 'pi_digits', 'e_digits']

for seq_name in seq_names:
    best_score = 0
    best_info = None
    for offset in range(500):
        try:
            key_stream = gen_sequence(seq_name, N, offset)
            if key_stream is None or len(key_stream) < N:
                continue
        except:
            continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt_text(cipher, key_stream, mode)
            matches, details = count_word_matches(plain)
            if matches > best_score:
                best_score = matches
                best_info = (seq_name, offset, mode, matches, details, plain)
            if matches >= THRESHOLD:
                print(f"  {seq_name} offset={offset} {mode}: {matches}/{NW} matches")
                print(f"    Text: {spaced_text(plain)}")
                print(f"    Matches: {', '.join(details)}")
    
    if best_score > 0 and best_info:
        s, o, m, mc, d, p = best_info
        print(f"  {seq_name}: best={mc} at offset={o} {m} -> {', '.join(d[:5])}")

print("Mathematical sequences scan complete.")

# ===== 3. FULL IoC RE-ANALYSIS =====
print(f"\n{'='*80}")
print("3. IoC ANALYSIS FOR ALL PERIODS 1-38")
print(f"{'='*80}")

for k in range(1, 39):
    columns = [[] for _ in range(k)]
    for i in range(N):
        columns[i % k].append(cipher[i])
    
    total_ioc = 0
    valid_cols = 0
    for col in columns:
        if len(col) < 2:
            continue
        counts = Counter(col)
        ioc = sum(c * (c-1) for c in counts.values()) / (len(col) * (len(col) - 1))
        total_ioc += ioc * MOD
        valid_cols += 1
    
    if valid_cols > 0:
        avg_ioc = total_ioc / valid_cols
        min_col = min(len(c) for c in columns)
        max_col = max(len(c) for c in columns)
        marker = " <<<<" if avg_ioc > 1.8 else ""
        print(f"  k={k:2d}: avg IoC*29={avg_ioc:.3f} (cols: {min_col}-{max_col} entries){marker}")

# ===== 4. KASISKI EXAMINATION =====
print(f"\n{'='*80}")
print("4. KASISKI EXAMINATION")
print(f"{'='*80}")

for ngram_len in [2, 3, 4]:
    repeats = {}
    for i in range(N - ngram_len + 1):
        ng = tuple(cipher[i:i + ngram_len])
        if ng not in repeats:
            repeats[ng] = []
        repeats[ng].append(i)
    
    repeated = {ng: positions for ng, positions in repeats.items() if len(positions) > 1}
    if repeated:
        print(f"\n  Repeated {ngram_len}-grams:")
        for ng, positions in sorted(repeated.items(), key=lambda x: -len(x[1])):
            distances = [positions[j] - positions[j-1] for j in range(1, len(positions))]
            ng_text = gp_to_text(ng)
            print(f"    {ng_text} ({ng}): positions={positions}, distances={distances}")

# Compute GCD of all distances
all_distances = []
for ngram_len in [2, 3]:
    for i in range(N - ngram_len + 1):
        ng = tuple(cipher[i:i + ngram_len])
        for j in range(i + 1, N - ngram_len + 1):
            if tuple(cipher[j:j + ngram_len]) == ng:
                all_distances.append(j - i)

if all_distances:
    factor_counts = Counter()
    for d in all_distances:
        for f in range(2, d + 1):
            if d % f == 0:
                factor_counts[f] += 1
    
    print(f"\n  Most common factors of repeated distances:")
    for factor, count in factor_counts.most_common(15):
        print(f"    Factor {factor:3d}: appears {count} times")

# ===== 5. AUTOKEY WITH WORD-MATCH SCORING =====
print(f"\n{'='*80}")
print("5. AUTOKEY BRUTE-FORCE (kl=1 to 4, word-match scoring)")
print(f"{'='*80}")

for kl in range(1, 5):
    total_keys = MOD ** kl
    if total_keys > 100000:
        print(f"  kl={kl}: {total_keys} keys, skipping (too many)")
        continue
    
    best_score = 0
    best_info = None
    
    for key_val in range(total_keys):
        primer = []
        v = key_val
        for _ in range(kl):
            primer.append(v % MOD)
            v //= MOD
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            # Plaintext-feedback autokey
            dec = [0] * N
            for i in range(N):
                if i < kl:
                    k = primer[i]
                else:
                    k = dec[i - kl]
                if mode == 'SUB': dec[i] = (cipher[i] - k) % MOD
                elif mode == 'ADD': dec[i] = (cipher[i] + k) % MOD
                elif mode == 'BEAU': dec[i] = (k - cipher[i]) % MOD
            
            matches, details = count_word_matches(dec)
            if matches > best_score:
                best_score = matches
                best_info = (primer, mode, matches, details, dec)
            if matches >= THRESHOLD:
                print(f"  Autokey kl={kl} primer={primer} ({gp_to_text(primer)}) {mode}: {matches}/{NW}")
                print(f"    Text: {spaced_text(dec)}")
                print(f"    Matches: {', '.join(details)}")
            
            # Ciphertext-feedback autokey
            dec2 = [0] * N
            for i in range(N):
                if i < kl:
                    k = primer[i]
                else:
                    k = cipher[i - kl]
                if mode == 'SUB': dec2[i] = (cipher[i] - k) % MOD
                elif mode == 'ADD': dec2[i] = (cipher[i] + k) % MOD
                elif mode == 'BEAU': dec2[i] = (k - cipher[i]) % MOD
            
            matches2, details2 = count_word_matches(dec2)
            if matches2 >= THRESHOLD:
                print(f"  CipherFB kl={kl} primer={primer} ({gp_to_text(primer)}) {mode}: {matches2}/{NW}")
                print(f"    Text: {spaced_text(dec2)}")
                print(f"    Matches: {', '.join(details2)}")
    
    if best_info:
        pr, m, mc, d, p = best_info
        print(f"  kl={kl}: best autokey={mc} primer={pr}({gp_to_text(pr)}) {m}")

print("Autokey scan complete.")

# ===== 6. AFFINE PER COLUMN =====
print(f"\n{'='*80}")
print("6. AFFINE CIPHER PER COLUMN (k=13)")
print(f"{'='*80}")

K = 13
columns = [[] for _ in range(K)]
col_positions = [[] for _ in range(K)]
for i in range(N):
    columns[i % K].append(cipher[i])
    col_positions[i % K].append(i)

# For each column, try all affine transformations: plain = (a * cipher + b) % 29
# where gcd(a, 29) = 1 (a must be coprime with 29, so a in {1..28} since 29 is prime)
# Total: 28 * 29 = 812 per column

# LP frequency distribution (from decoded corpus)
corpus_freq = Counter(full_corpus)
corpus_total = sum(corpus_freq.values())
expected_freq = {i: corpus_freq.get(i, 0) / corpus_total for i in range(MOD)}

best_affine_keys = []
for col_idx in range(K):
    col = columns[col_idx]
    col_n = len(col)
    if col_n < 2:
        continue
    
    best_chi = float('inf')
    best_ab = None
    
    for a in range(1, MOD):  # a coprime with 29 (all 1-28 since 29 is prime)
        for b in range(MOD):
            # Decrypt column
            dec_col = [(a * c + b) % MOD for c in col]
            # Chi-squared against LP frequency
            col_counts = Counter(dec_col)
            chi = 0
            for v in range(MOD):
                observed = col_counts.get(v, 0)
                expected = expected_freq.get(v, 1/MOD) * col_n
                if expected > 0:
                    chi += (observed - expected) ** 2 / expected
            
            if chi < best_chi:
                best_chi = chi
                best_ab = (a, b)
    
    best_affine_keys.append(best_ab)
    # print(f"  Col {col_idx:2d}: best affine a={best_ab[0]:2d} b={best_ab[1]:2d} chi={best_chi:.2f}")

# Apply best affine keys and check words
plain_affine = [0] * N
for i in range(N):
    col_idx = i % K
    a, b = best_affine_keys[col_idx]
    plain_affine[i] = (a * cipher[i] + b) % MOD

matches_aff, details_aff = count_word_matches(plain_affine)
print(f"  Best affine (chi-squared): {matches_aff}/{NW} matches")
print(f"  Text: {spaced_text(plain_affine)}")
if details_aff:
    print(f"  Matches: {', '.join(details_aff)}")

# ===== 7. LP WORD-BASED KEYWORD VIGENERE =====
print(f"\n{'='*80}")
print("7. LP WORD KEYWORD VIGENERE (all unique words from decoded texts)")
print(f"{'='*80}")

# Extract unique words from LP decoded text
lp_words_set = set()
# Use known LP vocabulary  
lp_vocabulary = [
    'WISDOM', 'TRUTH', 'SACRED', 'DIVINE', 'DIVINITY', 'PRIMUS', 'PILGRIM',
    'INSTAR', 'CONSUMPTION', 'PRESERVATION', 'ADHERENCE', 'EMERGENCE',
    'CIRCUMFERENCE', 'PRIMALITY', 'COMMUNION', 'INSTRUCTION', 'COMMAND',
    'WARNING', 'PARABLE', 'SILENCE', 'WHISPER', 'SEEKER', 'QUEST',
    'TRIAD', 'PURPOSE', 'ORGANIZED', 'FEAST', 'GATHER', 'PARTAKE',
    'TRANSFORMED', 'SOLITARY', 'STRUGGLE', 'WEALTH', 'ATTACHED',
    'PREPARED', 'DESTROY', 'LOSS', 'RUIN', 'SOME', 'WITHIN', 'DEPTHS',
    'BEING', 'PATH', 'FORWARD', 'SHINE', 'FORTH', 'MEET', 'MINDS',
    'WELCOME', 'SHARE', 'FREELY', 'GIVEN', 'BRING', 'FORM', 'GROUPS',
    'UNITED', 'NATURE', 'PRIME', 'CONTEMPLATE', 'FINAL', 'MASS',
    'NEVER', 'BECOME', 'WHAT', 'GREAT', 'CABAL', 'LIBER', 'END',
    'LIKE', 'THROUGH', 'WORKING', 'TOGETHER', 'COMES', 'PRIMES',
    'LET', 'ALL', 'OWN', 'YOU', 'YOUR', 'THE', 'AND', 'FOR',
    'FROM', 'INTO', 'WITH', 'THAT', 'HAVE', 'THIS', 'NOT', 'BUT',
    'ARE', 'HAS', 'BEEN', 'WILL', 'ONLY', 'LOOK', 'EACH', 'GROUP',
    'KOAN', 'INTUS', 'AMASS', 'CICADA',
    # More esoteric
    'GEMATRIA', 'FIBONACCI', 'TOTIENT', 'BEAUTIFUL', 'MYSTERY',
    'ENLIGHTENMENT', 'AWAKENING', 'CONSCIOUSNESS', 'ILLUMINATION',
    'TRANSCENDENCE', 'INITIATION', 'REVELATION', 'UNDERSTANDING',
    'COMPREHENSION', 'APOTHEOSIS', 'GNOSIS', 'SOPHIA', 'LOGOS',
    'HERMES', 'THOTH', 'MERCURY', 'MINERVA', 'ATHENA',
    'KNOWLEDGE', 'SPIRIT', 'FREEDOM', 'LIBERTY', 'JUSTICE',
    'HARMONY', 'BALANCE', 'ORDER', 'CHAOS', 'CREATION',
    'BEGINNING', 'ENDING', 'REBIRTH', 'DEATH', 'LIFE',
]

for keyword in lp_vocabulary:
    gp_key = eng_to_gp(keyword)
    if gp_key is None:
        continue
    kl = len(gp_key)
    if kl < 1 or kl > 20:
        continue
    
    for offset in range(kl):
        key_stream = []
        for i in range(N):
            key_stream.append(gp_key[(i + offset) % kl])
        
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt_text(cipher, key_stream, mode)
            matches, details = count_word_matches(plain)
            if matches >= THRESHOLD:
                print(f"  {keyword} (kl={kl}) offset={offset} {mode}: {matches}/{NW} matches")
                print(f"    Text: {spaced_text(plain)}")
                print(f"    Matches: {', '.join(details)}")

print("LP keyword Vigenere scan complete.")

# ===== 8. CHECK: IS P54 A SIMPLE SUBSTITUTION? =====
print(f"\n{'='*80}")
print("8. SIMPLE SUBSTITUTION CHECK (mono-alphabetic)")
print(f"{'='*80}")

# Raw IoC
freq = Counter(cipher)
ioc_raw = sum(f * (f-1) for f in freq.values()) / (N * (N - 1)) * MOD
print(f"  Raw IoC * 29 = {ioc_raw:.3f} (English ~1.7, random ~1.0)")

if ioc_raw > 1.4:
    print("  IoC suggests possible monoalphabetic substitution!")
    # Try frequency-based substitution
    # Sort cipher symbols by frequency (descending)
    cipher_freq_sorted = sorted(freq.items(), key=lambda x: -x[1])
    # Sort expected GP frequency by frequency (descending)
    exp_freq_sorted = sorted(expected_freq.items(), key=lambda x: -x[1])
    
    mapping = {}
    for i, (cipher_sym, _) in enumerate(cipher_freq_sorted):
        if i < len(exp_freq_sorted):
            mapping[cipher_sym] = exp_freq_sorted[i][0]
    
    plain_mono = [mapping.get(c, c) for c in cipher]
    matches_mono, details_mono = count_word_matches(plain_mono)
    print(f"  Frequency substitution: {matches_mono}/{NW} matches")
    print(f"  Text: {spaced_text(plain_mono)}")
else:
    print("  IoC too low for monoalphabetic - consistent with polyalphabetic")

# ===== 9. SPECIAL: TOTIENT CIPHER WITH LOW THRESHOLD =====
print(f"\n{'='*80}")
print("9. TOTIENT CIPHER RE-SCAN (threshold 8, offsets 0-10000)")
print(f"{'='*80}")

for start_idx in range(0, 10001):
    for mode in ['SUB', 'ADD', 'BEAU']:
        key_stream = [totient(primes[start_idx + i]) % MOD for i in range(N)]
        plain = decrypt_text(cipher, key_stream, mode)
        matches, details = count_word_matches(plain)
        if matches >= THRESHOLD:
            print(f"  Totient offset={start_idx} {mode}: {matches}/{NW} matches")
            print(f"    Text: {spaced_text(plain)}")
            print(f"    Matches: {', '.join(details)}")
    
    # Also try primes directly (not totient)
    for mode in ['SUB', 'ADD', 'BEAU']:
        key_stream = [primes[start_idx + i] % MOD for i in range(N)]
        plain = decrypt_text(cipher, key_stream, mode)
        matches, details = count_word_matches(plain)
        if matches >= THRESHOLD:
            print(f"  Primes offset={start_idx} {mode}: {matches}/{NW} matches")
            print(f"    Text: {spaced_text(plain)}")
            print(f"    Matches: {', '.join(details)}")

print("Totient/Prime re-scan complete.")

print(f"\n{'='*80}")
print("=== ALL SCANS COMPLETE ===")
print(f"{'='*80}")
