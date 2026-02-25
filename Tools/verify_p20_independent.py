"""
INDEPENDENT VERIFICATION of P20 partial solution.
The old analysis claimed:
  - 166 prime positions (we get 141)
  - IoC 1.89 on Beaufort(Deor) at prime positions
  - IoC 2.01 on shift-16 non-prime positions

Let's verify ALL claims from scratch.
"""
import os, sys, math
from collections import Counter

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# GP Mapping
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def to_english(gp_values):
    return ''.join(LATIN[v] for v in gp_values)

def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

def sieve_primes(n):
    """Sieve of Eratosthenes - returns set of primes up to n"""
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return set(i for i in range(2, n+1) if is_prime[i])

# === OE Tokenizer ===
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
           'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def tokenize_oe_text(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if text[i] == 'Þ' or text[i] == 'Ð':
            values.append(2); i += 1
        elif text[i] == 'Æ':
            values.append(25); i += 1
        elif i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH':
                values.append(2); i += 2
            elif digraph == 'NG':
                values.append(21); i += 2
            elif digraph == 'OE':
                values.append(22); i += 2
            elif digraph == 'AE':
                values.append(25); i += 2
            elif digraph in ('IA', 'IO'):
                values.append(27); i += 2
            elif digraph == 'EA':
                values.append(28); i += 2
            elif digraph == 'EO':
                values.append(12); i += 2
            elif text[i] in ENG2GP:
                values.append(ENG2GP[text[i]]); i += 1
            else:
                i += 1
        elif text[i] in ENG2GP:
            values.append(ENG2GP[text[i]]); i += 1
        else:
            i += 1
    return values

DEOR_OE = """Welund him be wurman wræces cunnade,
anhydig eorl earfoþa dreag,
hæfde him to gesiþþe sorge ond longaþ,
wintercealde wræce; wean oft onfond,
siþþan hine Niðhad on nede legde,
swoncre seonobende on syllan monn.
Þæs ofereode, þisses swa mæg.
Beadohilde ne wæs hyre broþra deaþ
on sefan swa sar swa hyre sylfre þing,
þæt heo gearolice ongieten hæfde
þæt heo eacen wæs; æfre ne meahte
þriste geþencan, hu ymb þæt sceolde.
Þæs ofereode, þisses swa mæg.
We þæt Mæðhilde monge gefrugnon
wurdon grundlease Geates frige,
þæt hi seo sorglufu slæp ealle binom.
Þæs ofereode, þisses swa mæg.
Ðeodric ahte þritig wintra
Mæringa burg; þæt wæs monegum cuþ.
Þæs ofereode, þisses swa mæg.
We geascodan Eormanrices
wylfenne geþoht; ahte wide folc
Gotena rices. Þæt wæs grim cyning.
Sæt secg monig sorgum gebunden,
wean on wenan, wyscte geneahhe
þæt þæs cynerices ofercumen wære.
Þæs ofereode, þisses swa mæg.
Siteð sorgcearig, sælum bedæled,
on sefan sweorceð, sylfum þinceð
þæt sy endeleas earfoða dæl.
Mæg þonne geþencan, þæt geond þas woruld
witig Dryhten wendeþ geneahhe,
eorle monegum are gesceawað,
wislicne blæd, sumum weana dæl.
Þæt ic bi me sylfum secgan wille,
þæt ic hwile wæs Heodeninga scop,
dryhtne dyre. Me wæs Deor noma.
Ahte ic fela wintra folgað tilne,
holdne hlaford, oþþæt Heorrenda nu,
leoðcræftig monn londryht geþah,
þæt me eorla hleo ær gesealde.
Þæs ofereode, þisses swa mæg."""

deor = tokenize_oe_text(DEOR_OE)

# === Load P20 ===
p20 = load_page(20)
print(f"P20 runes: {len(p20)}")
print(f"Deor tokens: {len(deor)}")

# === Count primes ===
primes_set = sieve_primes(len(p20))
prime_positions = sorted([i for i in range(len(p20)) if i in primes_set])
non_prime_positions = sorted([i for i in range(len(p20)) if i not in primes_set])

print(f"\nPrimes in [2, {len(p20)-1}]: {len(prime_positions)}")
print(f"First 20 primes: {prime_positions[:20]}")
print(f"Last 5 primes: {prime_positions[-5:]}")
print(f"Non-primes: {len(non_prime_positions)}")
print(f"Total: {len(prime_positions)} + {len(non_prime_positions)} = {len(prime_positions) + len(non_prime_positions)} (should be {len(p20)})")

# === Check: what did the old scripts use? ===
# Maybe they had positions 0-811 but also included 0 and 1?
# Or used a different is_prime?
print(f"\nis_prime(0) = {0 in primes_set}")
print(f"is_prime(1) = {1 in primes_set}")
print(f"is_prime(2) = {2 in primes_set}")

# Let me try the old-style is_prime that might have bugs
def old_is_prime(n):
    """Possibly buggy version from old scripts"""
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

old_primes = [i for i in range(len(p20)) if old_is_prime(i)]
print(f"Old-style is_prime count: {len(old_primes)}")

# Check with 1-indexed
primes_1idx = [i for i in range(1, len(p20)+1) if i in primes_set]
print(f"1-indexed primes: {len(primes_1idx)}")

# === CHECK THE BEAUFORT(DEOR) STREAM ===
# Using CORRECT prime positions (0-indexed, 141 primes)
print(f"\n{'='*80}")
print("BEAUFORT(DEOR) AT PRIME POSITIONS")
print(f"{'='*80}")

# Beaufort: stream[i] = (deor[prime_pos] - p20[prime_pos]) mod 29
# Need: prime_pos < len(deor) AND prime_pos < len(p20)
valid_primes = [p for p in prime_positions if p < len(deor) and p < len(p20)]
print(f"Valid prime positions (within both texts): {len(valid_primes)}")

beau_stream = [(deor[p] - p20[p]) % 29 for p in valid_primes]
ic_beau = ioc(beau_stream)
print(f"Beaufort IoC: {ic_beau:.4f}")
print(f"Text: {to_english(beau_stream)[:100]}")

# Also try SUB and ADD
sub_stream = [(p20[p] - deor[p]) % 29 for p in valid_primes]
add_stream = [(p20[p] + deor[p]) % 29 for p in valid_primes]
print(f"SUB IoC: {ioc(sub_stream):.4f}")
print(f"ADD IoC: {ioc(add_stream):.4f}")

# Try ALL shifts of the Beaufort result (maybe it needed a secondary shift)
print("\nBeau stream + secondary Caesar shifts:")
for shift in range(29):
    shifted_beau = [(v + shift) % 29 for v in beau_stream]
    ic = ioc(shifted_beau)
    if ic > 1.3:
        print(f"  Shift {shift:2d}: IoC={ic:.4f} | {to_english(shifted_beau)[:60]}")

# === Try: sequential Deor keys (not position-indexed) ===
print(f"\n{'='*80}")
print("BEAUFORT with SEQUENTIAL Deor key at prime positions")
print(f"{'='*80}")
# stream[i] = (deor[i] - p20[prime_i]) mod 29
for mode in ['BEAU', 'SUB', 'ADD']:
    for offset in range(50):
        if mode == 'BEAU':
            stream = [(deor[(i+offset) % len(deor)] - p20[valid_primes[i]]) % 29 for i in range(len(valid_primes))]
        elif mode == 'SUB':
            stream = [(p20[valid_primes[i]] - deor[(i+offset) % len(deor)]) % 29 for i in range(len(valid_primes))]
        else:
            stream = [(p20[valid_primes[i]] + deor[(i+offset) % len(deor)]) % 29 for i in range(len(valid_primes))]
        ic = ioc(stream)
        if ic > 1.3:
            print(f"  {mode} seqOff={offset}: IoC={ic:.4f} | {to_english(stream)[:60]}")

# === TRY: All possible shift values on both prime and non-prime positions ===
print(f"\n{'='*80}")
print("ALL SHIFTS ON PRIME-POSITION AND NON-PRIME-POSITION RUNES")
print(f"{'='*80}")

prime_runes = [p20[p] for p in prime_positions]
nonprime_runes = [p20[p] for p in non_prime_positions]

print(f"Prime runes ({len(prime_runes)}): IoC={ioc(prime_runes):.4f}")
print(f"Non-prime runes ({len(nonprime_runes)}): IoC={ioc(nonprime_runes):.4f}")

print("\nCaesar shifts on prime-position runes:")
for s in range(29):
    shifted = [(v + s) % 29 for v in prime_runes]
    ic = ioc(shifted)
    if ic > 1.2:
        print(f"  Shift {s:2d}: IoC={ic:.4f}")

print("\nCaesar shifts on non-prime-position runes:")
for s in range(29):
    shifted = [(v + s) % 29 for v in nonprime_runes]
    ic = ioc(shifted)
    if ic > 1.2:
        print(f"  Shift {s:2d}: IoC={ic:.4f}")

# === READ THE OLD SCRIPTS to find the 166 discrepancy ===
print(f"\n{'='*80}")
print("CHECKING OLD SCRIPT METHODOLOGY")
print(f"{'='*80}")

# Check if the old analysis might have used the FIRST 166 primes (prime[0]=2, prime[1]=3, ...)
# rather than primes < 812
def sieve_first_n_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        if all(candidate % p != 0 for p in primes if p*p <= candidate):
            primes.append(candidate)
        candidate += 1
    return primes

first_166_primes = sieve_first_n_primes(166)
print(f"166th prime: {first_166_primes[-1]}")
print(f"First 166 primes max: {max(first_166_primes)}")
# 166th prime is 991, which is > 811. So not all of them fit in P20.
# But maybe old code used these as indices mod 812?

# How about: maybe they counted words as delimited by F (value 0)?
f_count = sum(1 for v in p20 if v == 0)
print(f"F-runes in P20: {f_count}")
print(f"Words if delimited by F: {f_count + 1}")

# Check how many positions DON'T have F (non-F runes)
non_f = [i for i, v in enumerate(p20) if v != 0]
print(f"Non-F positions: {len(non_f)}")

# What if "prime positions" means positions where p20[i] is a prime GP value?
prime_gp_values = {2, 3, 5, 7, 11, 13, 17, 19, 23}
prime_valued = [i for i, v in enumerate(p20) if v in prime_gp_values]
non_prime_valued = [i for i, v in enumerate(p20) if v not in prime_gp_values]
print(f"Runes with prime GP VALUES: {len(prime_valued)}")
print(f"Runes with non-prime GP VALUES: {len(non_prime_valued)}")

# Check: maybe there are 166 WORDS and they used word boundaries?
words = []
current_word = []
for v in p20:
    if v == 0:  # F rune as delimiter
        if current_word:
            words.append(current_word)
            current_word = []
    else:
        current_word.append(v)
if current_word:
    words.append(current_word)
print(f"Words (F-delimited): {len(words)}")
print(f"Word lengths: {[len(w) for w in words[:20]]}...")

# === TRY THE "CORRECT" 166 INTERPRETATION ===
# Maybe 166 = number of words. Try extracting first character of each word?
print(f"\n{'='*80}")
print("WORD-BASED ANALYSIS")
print(f"{'='*80}")

# First char of each word
first_chars = [w[0] for w in words]
print(f"First chars ({len(first_chars)}): IoC={ioc(first_chars):.4f}")
print(f"  As text: {to_english(first_chars)[:80]}")

# Last char of each word
last_chars = [w[-1] for w in words]
print(f"Last chars ({len(last_chars)}): IoC={ioc(last_chars):.4f}")

# Word lengths
word_lengths = [len(w) for w in words]
print(f"Word length distribution: {Counter(word_lengths)}")
print(f"  Mean: {sum(word_lengths)/len(word_lengths):.2f}")

# Prime-indexed words (word 2, 3, 5, 7, ...)
prime_words_concat = []
for i, w in enumerate(words):
    if i in primes_set:
        prime_words_concat.extend(w)
print(f"\nPrime-indexed words concatenated: {len(prime_words_concat)} runes, IoC={ioc(prime_words_concat):.4f}")

# Apply Beaufort(Deor) to prime-indexed words
if prime_words_concat:
    beau_words = [(deor[i % len(deor)] - prime_words_concat[i]) % 29 for i in range(len(prime_words_concat))]
    print(f"  Beaufort(Deor) IoC: {ioc(beau_words):.4f}")
    print(f"  Text: {to_english(beau_words)[:80]}")

# Non-prime-indexed words
nonprime_words_concat = []
for i, w in enumerate(words):
    if i not in primes_set:
        nonprime_words_concat.extend(w)
print(f"\nNon-prime-indexed words concatenated: {len(nonprime_words_concat)} runes, IoC={ioc(nonprime_words_concat):.4f}")

# Caesar shifts on non-prime words
for s in range(29):
    shifted = [(v + s) % 29 for v in nonprime_words_concat]
    ic = ioc(shifted)
    if ic > 1.2:
        print(f"  Shift {s:2d}: IoC={ic:.4f}")

print("\nDone.")
