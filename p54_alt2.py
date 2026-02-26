"""
P54 Focused Remaining Attacks (sections that were truncated/crashed)
- IoC analysis for all periods
- Kasiski examination  
- Running-key with hardcoded LP corpus
- Mathematical key sequences
- Affine per-column
- Totient/prime stream re-scan
- LP keyword Vigenère
"""
import sys, functools, os, math
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
print = functools.partial(print, flush=True)

# Redirect output to file
outf = open('p54_alt_results.txt', 'w', encoding='utf-8')
def log(msg=''):
    print(msg)
    outf.write(msg + '\n')
    outf.flush()

MOD = 29
GP_RUNES = '\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0'
GP = {}
for i, r in enumerate(GP_RUNES):
    GP[r] = i
GP['\u16C2'] = 11
IDX_TO_LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def gp_to_text(vals): return ''.join(IDX_TO_LAT[v] for v in vals)
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
            else: return None
    return result

cipher = [21, 25, 19, 10, 7, 15, 17, 14, 19, 15, 12, 6, 23, 2, 25, 0, 27, 24, 17, 5, 1, 7, 4, 17, 28, 0, 14, 10, 19, 1, 5, 13, 8, 21, 20, 12, 19, 15, 23, 27, 13, 0, 17, 8, 12, 5, 12, 18, 28, 18, 10, 6, 14, 6, 15, 18, 15, 12, 2, 2, 18, 15, 2, 22, 5, 28, 10, 19, 5, 14, 23, 11, 1, 17, 18, 10]
word_lens = [1, 4, 2, 2, 6, 6, 2, 1, 12, 6, 4, 2, 7, 7, 2, 4, 2, 3, 3]
N = len(cipher)
NW = len(word_lens)
word_starts = []
pos = 0
for wl in word_lens:
    word_starts.append(pos)
    pos += wl

# Dictionary
log("Loading dictionary...")
with open('wordlist.txt') as f:
    raw_words = f.read().strip().split('\n')
gp_dict = {}
for word in raw_words:
    word = word.strip().lower()
    if len(word) < 1 or len(word) > 25: continue
    gp = eng_to_gp(word)
    if gp is None: continue
    gplen = len(gp)
    if gplen < 1 or gplen > 15: continue
    gpt = tuple(gp)
    if gplen not in gp_dict: gp_dict[gplen] = set()
    gp_dict[gplen].add(gpt)
log(f"Dictionary: {sum(len(v) for v in gp_dict.values())} GP words")

def count_word_matches(plain):
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
    plain = []
    for i in range(len(cipher)):
        k = key_stream[i % len(key_stream)] % MOD if isinstance(key_stream, list) else key_stream[i] % MOD
        if mode == 'SUB': plain.append((cipher[i] - k) % MOD)
        elif mode == 'ADD': plain.append((cipher[i] + k) % MOD)
        elif mode == 'BEAU': plain.append((k - cipher[i]) % MOD)
    return plain

def spaced_text(plain):
    parts = []
    pos = 0
    for wl in word_lens:
        parts.append(gp_to_text(plain[pos:pos+wl]))
        pos += wl
    return ' '.join(parts)

# ===== LP CORPUS (HARDCODED from decoded.txt files) =====
# From prior session collection of all decoded pages
lp_decoded_texts = {
    'p58': 'SOMEWISDOMISNOT MEANTFOREVERYONE',
    'p59': 'AWARNINGPARABLECONSUMPTIONSHALLBRINGABOUTTHERUINOFTHESELF',
    'p60': 'WITHINTHEDEPTHSOFYOURBEINGISTHETRUTHWITHINTHESI LENCEOFTHESELFTHE WHISPEROFTHEDIVINETHEONLYPATHFORWARD ISWITHINLETTHESEEKERLOOKWITHINANDTHETRUTHWILLSHINEFORTH',
    'p61': 'ANINSTRUCTIONMEETWITHLIKEMINDSANDWELCOMEALLTOP ARTAKEINTHEQUEST INSTARFROMTHESOLITARYEMERGETRANSFORMEDINCOMMUNION',
    'p62': 'ANINSTRUCTIONSHAREFREELY ALLTHATHASBEENGIVENBRINGALLTHEPILGRIMSTOGATHERFORTHEFEASTOFTHEMIND',
    'p63': 'ACOMMANDFORMYOURSELVESINTOGROUPS BEORGANIZED LETEACHGROUPBEATRIADUNITEDINPURPOSE',
    'p67': 'LIKETHEINSTARITISTHROUGHSTRUGGLETHATWEEMERGESOMEWISDO MISAMASSGRE ATWEALTH',
    'p68': 'NEVERBECOMEATTACHEDTOWHATYOUOWNBEPREPAREDTODESTROYALLTHATYOUOWN',
    'p72': 'INTHEENDWISDOMCOMESLOSSANDPRESERVATIONWORKINGTOGETHER',
    'p74': 'AFINALDIVI NITYTHEPRIMESARESACREDLETTHESEEKERCONTEMPLATETHE NATUREOFTHEPRIME',
}

# Build LP corpus as GP values
full_corpus = []
for name in sorted(lp_decoded_texts.keys()):
    text = lp_decoded_texts[name].replace(' ', '')  # remove spaces  
    gp = eng_to_gp(text)
    if gp:
        full_corpus.extend(gp)

# Also try individual page corpora
page_corpora = {}
for name, text in lp_decoded_texts.items():
    text_clean = text.replace(' ', '')
    gp = eng_to_gp(text_clean)
    if gp:
        page_corpora[name] = gp

log(f"LP corpus: {len(full_corpus)} GP values from {len(page_corpora)} pages")

# LP frequency distribution
corpus_freq = Counter(full_corpus)
corpus_total = max(sum(corpus_freq.values()), 1)
expected_freq = {i: corpus_freq.get(i, 0) / corpus_total for i in range(MOD)}

THRESHOLD = 8

# ===== 1. IoC ANALYSIS =====
log(f"\n{'='*80}")
log("1. IoC ANALYSIS FOR ALL PERIODS 1-38")
log(f"{'='*80}")

for k in range(1, 39):
    columns = [[] for _ in range(k)]
    for i in range(N):
        columns[i % k].append(cipher[i])
    
    total_ioc = 0
    valid_cols = 0
    for col in columns:
        if len(col) < 2: continue
        counts = Counter(col)
        ioc = sum(c * (c-1) for c in counts.values()) / (len(col) * (len(col) - 1))
        total_ioc += ioc * MOD
        valid_cols += 1
    
    if valid_cols > 0:
        avg_ioc = total_ioc / valid_cols
        min_col = min(len(c) for c in columns)
        max_col = max(len(c) for c in columns)
        marker = " <<<<" if avg_ioc > 1.8 else ""
        log(f"  k={k:2d}: avg IoC*29={avg_ioc:.3f} ({min_col}-{max_col} entries/col){marker}")

# ===== 2. KASISKI EXAMINATION =====
log(f"\n{'='*80}")
log("2. KASISKI EXAMINATION")
log(f"{'='*80}")

for ngram_len in [2, 3, 4]:
    repeats = {}
    for i in range(N - ngram_len + 1):
        ng = tuple(cipher[i:i + ngram_len])
        if ng not in repeats: repeats[ng] = []
        repeats[ng].append(i)
    repeated = {ng: pos for ng, pos in repeats.items() if len(pos) > 1}
    if repeated:
        log(f"\n  Repeated {ngram_len}-grams:")
        for ng, positions in sorted(repeated.items(), key=lambda x: -len(x[1])):
            distances = [positions[j] - positions[j-1] for j in range(1, len(positions))]
            log(f"    {gp_to_text(ng):8s} ({ng}): pos={positions}, dist={distances}")

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
    log(f"\n  Most common factors of repeated distances:")
    for factor, count in factor_counts.most_common(20):
        log(f"    Factor {factor:3d}: {count} times")

# ===== 3. RUNNING-KEY CIPHER =====
log(f"\n{'='*80}")
log("3. RUNNING-KEY CIPHER (LP decoded text as key)")
log(f"{'='*80}")

for page_name, page_gp in page_corpora.items():
    if len(page_gp) < N: continue
    max_offset = len(page_gp) - N
    for offset in range(max_offset + 1):
        key_stream = page_gp[offset:offset + N]
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt_text(cipher, key_stream, mode)
            matches, details = count_word_matches(plain)
            if matches >= THRESHOLD:
                log(f"  {page_name} off={offset} {mode}: {matches}/{NW} matches")
                log(f"    Text: {spaced_text(plain)}")
                log(f"    Matches: {', '.join(details)}")

if len(full_corpus) >= N:
    max_offset = len(full_corpus) - N
    for offset in range(max_offset + 1):
        key_stream = full_corpus[offset:offset + N]
        for mode in ['SUB', 'ADD', 'BEAU']:
            plain = decrypt_text(cipher, key_stream, mode)
            matches, details = count_word_matches(plain)
            if matches >= THRESHOLD:
                log(f"  CORPUS off={offset} {mode}: {matches}/{NW}")
                log(f"    Text: {spaced_text(plain)}")
                log(f"    Matches: {', '.join(details)}")

log("Running-key scan complete.")

# ===== 4. MATHEMATICAL KEY SEQUENCES =====
log(f"\n{'='*80}")
log("4. MATHEMATICAL KEY SEQUENCES")
log(f"{'='*80}")

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

primes = sieve_primes(200000)

def totient(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0: temp //= p
            result -= result // p
        p += 1
    if temp > 1: result -= result // temp
    return result

gp_primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

pi_str = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
e_str = "27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274"

seq_generators = {
    'primes': lambda n,o: [primes[o+i] % MOD for i in range(n)],
    'primes-1': lambda n,o: [(primes[o+i]-1) % MOD for i in range(n)],
    'totient_primes': lambda n,o: [totient(primes[o+i]) % MOD for i in range(n)],
    'fibonacci': lambda n,o: (lambda: (fib:=[1,1], [fib.append(fib[-1]+fib[-2]) for _ in range(n+o-2)], [fib[o+i]%MOD for i in range(n)]))()[-1],
    'triangular': lambda n,o: [((o+i)*(o+i+1)//2)%MOD for i in range(n)],
    'squares': lambda n,o: [((o+i)**2)%MOD for i in range(n)],
    'powers_of_2': lambda n,o: [(pow(2,o+i,MOD*1000))%MOD for i in range(n)],
    'powers_of_3': lambda n,o: [(pow(3,o+i,MOD*1000))%MOD for i in range(n)],
    'prime_gaps': lambda n,o: [(primes[o+i+1]-primes[o+i])%MOD for i in range(n)],
    'natural': lambda n,o: [(o+i)%MOD for i in range(n)],
    'pi_digits': lambda n,o: [int(pi_str[o+i])%MOD for i in range(min(n,len(pi_str)-o))],
    'e_digits': lambda n,o: [int(e_str[o+i])%MOD for i in range(min(n,len(e_str)-o))],
    'gp_prime_idx': lambda n,o: [gp_primes[(o+i)%29]%MOD for i in range(n)],
    'cumulative_primes': lambda n,o: (lambda: (s:=[0], [s.append(s[-1]+primes[i]) for i in range(n+o)], [s[o+i]%MOD for i in range(n)]))()[-1],
}

for seq_name, gen_fn in seq_generators.items():
    best_score = 0
    best_info = None
    for offset in range(min(500, 15000)):
        try:
            ks = gen_fn(N, offset)
            if ks is None or len(ks) < N: continue
        except: continue
        for mode in ['SUB','ADD','BEAU']:
            plain = decrypt_text(cipher, ks, mode)
            matches, details = count_word_matches(plain)
            if matches > best_score:
                best_score = matches
                best_info = (offset, mode, matches, details, plain)
            if matches >= THRESHOLD:
                log(f"  {seq_name} off={offset} {mode}: {matches}/{NW}")
                log(f"    Text: {spaced_text(plain)}")
                log(f"    Matches: {', '.join(details)}")
    if best_info:
        o,m,mc,d,p = best_info
        log(f"  {seq_name}: BEST={mc} off={o} {m} -> {', '.join(d[:5])}")

log("Math sequences complete.")

# ===== 5. AFFINE PER COLUMN (k=13) =====
log(f"\n{'='*80}")
log("5. AFFINE CIPHER PER COLUMN (k=13)")
log(f"{'='*80}")

K = 13
columns = [[] for _ in range(K)]
for i in range(N):
    columns[i % K].append(cipher[i])

best_affine_keys = []
for col_idx in range(K):
    col = columns[col_idx]
    col_n = len(col)
    if col_n < 2:
        best_affine_keys.append((1, 0))
        continue
    best_chi = float('inf')
    best_ab = (1, 0)
    for a in range(1, MOD):
        for b in range(MOD):
            dec_col = [(a * c + b) % MOD for c in col]
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
    log(f"  Col {col_idx:2d}: a={best_ab[0]:2d} b={best_ab[1]:2d} chi={best_chi:.2f}")

plain_affine = [0] * N
for i in range(N):
    a, b = best_affine_keys[i % K]
    plain_affine[i] = (a * cipher[i] + b) % MOD

matches_aff, details_aff = count_word_matches(plain_affine)
log(f"  Affine result: {matches_aff}/{NW} matches")
log(f"  Text: {spaced_text(plain_affine)}")
if details_aff:
    log(f"  Matches: {', '.join(details_aff)}")

# ===== 6. MONO-ALPHABETIC CHECK =====
log(f"\n{'='*80}")
log("6. MONO-ALPHABETIC CHECK")
log(f"{'='*80}")

freq = Counter(cipher)
ioc_raw = sum(f * (f-1) for f in freq.values()) / (N * (N - 1)) * MOD
log(f"  Raw IoC * 29 = {ioc_raw:.3f} (English ~1.7, random ~1.0)")

# ===== 7. TOTIENT/PRIME RE-SCAN (lower threshold, expanded range) =====
log(f"\n{'='*80}")
log("7. TOTIENT/PRIME RE-SCAN (threshold 8, offsets 0-10000)")
log(f"{'='*80}")

best_totient = (0, None)
best_prime = (0, None)

for start_idx in range(0, 10001):
    for mode in ['SUB', 'ADD', 'BEAU']:
        # Totient of primes
        ks_t = [totient(primes[start_idx + i]) % MOD for i in range(N)]
        plain_t = decrypt_text(cipher, ks_t, mode)
        mt, dt = count_word_matches(plain_t)
        if mt > best_totient[0]:
            best_totient = (mt, (start_idx, mode, dt, plain_t))
        if mt >= THRESHOLD:
            log(f"  Totient off={start_idx} {mode}: {mt}/{NW}")
            log(f"    Text: {spaced_text(plain_t)}")
            log(f"    Matches: {', '.join(dt)}")
        
        # Primes directly
        ks_p = [primes[start_idx + i] % MOD for i in range(N)]
        plain_p = decrypt_text(cipher, ks_p, mode)
        mp, dp = count_word_matches(plain_p)
        if mp > best_prime[0]:
            best_prime = (mp, (start_idx, mode, dp, plain_p))
        if mp >= THRESHOLD:
            log(f"  Primes off={start_idx} {mode}: {mp}/{NW}")
            log(f"    Text: {spaced_text(plain_p)}")
            log(f"    Matches: {', '.join(dp)}")
    
    if start_idx % 2000 == 0:
        log(f"  ... scanned to offset {start_idx}")

log(f"  Best totient: {best_totient[0]} matches")
if best_totient[1]:
    o,m,d,p = best_totient[1]
    log(f"    offset={o} {m} -> {', '.join(d[:8])}")
log(f"  Best primes: {best_prime[0]} matches")
if best_prime[1]:
    o,m,d,p = best_prime[1]
    log(f"    offset={o} {m} -> {', '.join(d[:8])}")

log("Totient/prime scan complete.")

# ===== 8. F-SKIP CONSIDERATIONS =====
log(f"\n{'='*80}")
log("8. F-SKIP ANALYSIS")
log(f"{'='*80}")

f_positions = [i for i in range(N) if cipher[i] == 0]
log(f"  F(0) rune positions: {f_positions}")
log(f"  F(0) count: {len(f_positions)}")

# If F runes pass through, the non-F cipher has 73 runes
non_f_cipher = [(i, cipher[i]) for i in range(N) if cipher[i] != 0]
log(f"  Non-F cipher length: {len(non_f_cipher)}")

# Check IoC for non-F cipher only
for k in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,19,37,73]:
    cols = [[] for _ in range(k)]
    for idx, (orig_pos, val) in enumerate(non_f_cipher):
        cols[idx % k].append(val)
    total_ioc = 0
    valid = 0
    for col in cols:
        if len(col) < 2: continue
        counts = Counter(col)
        ioc = sum(c*(c-1) for c in counts.values()) / (len(col)*(len(col)-1))
        total_ioc += ioc * MOD
        valid += 1
    if valid > 0:
        avg = total_ioc / valid
        min_c = min(len(c) for c in cols)
        marker = " <<<<" if avg > 1.8 else ""
        log(f"  F-skip IoC k={k:2d}: avg*29={avg:.3f} ({min_c}-{max(len(c) for c in cols)} entries/col){marker}")

# Try totient on non-F positions only (P55-style)
log(f"\n  Totient on non-F positions (P55-style), offsets 0-10000:")
non_f_vals = [v for _, v in non_f_cipher]
non_f_N = len(non_f_vals)

best_fskip_tot = (0, None)
for start_idx in range(0, 10001):
    for mode in ['SUB','ADD','BEAU']:
        ks = [totient(primes[start_idx + i]) % MOD for i in range(non_f_N)]
        dec_nf = []
        if mode == 'SUB': dec_nf = [(non_f_vals[i] - ks[i]) % MOD for i in range(non_f_N)]
        elif mode == 'ADD': dec_nf = [(non_f_vals[i] + ks[i]) % MOD for i in range(non_f_N)]
        elif mode == 'BEAU': dec_nf = [(ks[i] - non_f_vals[i]) % MOD for i in range(non_f_N)]
        
        # Reconstruct full plaintext with F at F positions
        full_plain = [0] * N
        nf_idx = 0
        for i in range(N):
            if cipher[i] == 0:
                full_plain[i] = 0  # F passes through
            else:
                full_plain[i] = dec_nf[nf_idx]
                nf_idx += 1
        
        mt, dt = count_word_matches(full_plain)
        if mt > best_fskip_tot[0]:
            best_fskip_tot = (mt, (start_idx, mode, dt, full_plain))
        if mt >= THRESHOLD:
            log(f"  FSkip-Totient off={start_idx} {mode}: {mt}/{NW}")
            log(f"    Text: {spaced_text(full_plain)}")
            log(f"    Matches: {', '.join(dt)}")
    
    if start_idx % 2000 == 0:
        log(f"  ... F-skip scanned to offset {start_idx}")

log(f"  Best F-skip totient: {best_fskip_tot[0]} matches")
if best_fskip_tot[1]:
    o,m,d,p = best_fskip_tot[1]
    log(f"    offset={o} {m} -> {', '.join(d[:8])}")

log(f"\n{'='*80}")
log("=== ALL SCANS COMPLETE ===")
log(f"{'='*80}")
outf.close()
