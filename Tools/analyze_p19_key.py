"""Analyze P19's key structure to find patterns."""

def sieve_primes(n):
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(2, n+1) if sieve[i]]

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

KEY47 = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

print(f"P19 key ({len(KEY47)} values): {KEY47}")
key_text = ' '.join(LATIN[v] for v in KEY47)
print(f"Key as GP letters: {key_text}")
key_primes = [GP_PRIMES[v] for v in KEY47]
print(f"Key as primes: {key_primes}")
print()

# Generate totient stream  
primes = sieve_primes(50000)
totient_stream = [totient(p) % 29 for p in primes[:5000]]

print("Searching for KEY47 in totient stream (first 5000 primes)...")
found = False
for start in range(len(totient_stream) - 47):
    if totient_stream[start:start+47] == KEY47:
        print(f"  MATCH at offset {start}! (prime={primes[start]})")
        found = True
        break
if not found:
    print("  No exact match found")

# Best partial consecutive matches
print("\nBest consecutive matches in totient stream:")
best_len = 0
best_starts = []
for start in range(len(totient_stream) - 47):
    match_len = 0
    for i in range(47):
        if totient_stream[start + i] == KEY47[i]:
            match_len += 1
        else:
            break
    if match_len > best_len:
        best_len = match_len
        best_starts = [(start, match_len)]
    elif match_len == best_len and match_len > 2:
        best_starts.append((start, match_len))
print(f"  Best consecutive: {best_len} values")
for s, ml in best_starts[:5]:
    print(f"    At offset {s} (prime={primes[s]}): totient={totient_stream[s:s+ml]}, key={KEY47[:ml]}")

# Count how many individual positions match at each offset
print("\nBest positional matches (count of matching positions out of 47):")
scores = []
for start in range(min(4000, len(totient_stream) - 47)):
    count = sum(1 for i in range(47) if totient_stream[start+i] == KEY47[i])
    scores.append((count, start))
scores.sort(reverse=True)
for count, start in scores[:10]:
    print(f"  Offset {start} (prime={primes[start]}): {count}/47 matches")

# Random expectation: each position has 1/29 chance of matching, so E[matches] = 47/29 ≈ 1.62
print(f"\n  Random expectation: {47/29:.2f}/47 matches")

# Key analysis
from collections import Counter
freq = Counter(KEY47)
print(f"\nValue frequencies: {dict(sorted(freq.items()))}")
print(f"Last 4 values all 28 (EA): {KEY47[-4:]}")
key_concat = ''.join(LATIN[v] for v in KEY47)
print(f"Key concatenated: {key_concat}")
print(f"Key lowercase: {key_concat.lower()}")

# Differences
diffs = [(KEY47[i+1] - KEY47[i]) % 29 for i in range(46)]
print(f"\nDifferences mod 29: {diffs}")

# Check: is the key the totient of SOMETHING ELSE?
# Maybe totient(key_prime[i]) gives something useful?
key_tots = [totient(GP_PRIMES[v]) % 29 for v in KEY47]
print(f"\nTotient of GP_PRIMES[key_val] mod 29: {key_tots}")

# Maybe the key IS the plaintext of P19 XOR'd with something?
# We know P19 plaintext starts with REARRANGINGTHEPRIMESNUMBERS...
# R=4, E=18, A=24, R=4, R=4, A=24, N=9, G=6, I=10, N=9, G=6, T=16, H=8, E=18, P=13, R=4, I=10, M=19, E=18, S=15, N=9, U=1, M=19, B=17, E=18, R=4, S=15
p19_plain_start = [4,18,24,4,4,24,9,6,10,9,6,16,8,18,13,4,10,19,18,15,9,1,19,17,18,4,15]
print(f"\nP19 plaintext start (27 vals): {p19_plain_start}")
print(f"Key start (27 vals):            {KEY47[:27]}")
# diff = (key - plain) mod 29
diff_kp = [(KEY47[i] - p19_plain_start[i]) % 29 for i in range(27)]
print(f"Key - Plain mod 29:             {diff_kp}")
# sum = (key + plain) mod 29
sum_kp = [(KEY47[i] + p19_plain_start[i]) % 29 for i in range(27)]
print(f"Key + Plain mod 29:             {sum_kp}")

# Check if P19's ciphertext follows any pattern
import os
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}

def load(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                return [GP[c] for c in f.read() if c in GP]
    return None

p19 = load(19)
if p19:
    print(f"\nP19 ciphertext ({len(p19)} runes): {p19[:47]}")
    # If plain = (cipher + key) % 29, then cipher = (plain - key) % 29
    # Or equivalently: key = (plain - cipher) % 29
    # Let's verify by decrypting first few runes
    decrypted = [(p19[i] + KEY47[i % 47]) % 29 for i in range(47)]
    print(f"Decrypted first 47: {''.join(LATIN[v] for v in decrypted)}")
    
    # Compute what the key stream actually is: key[i] = (plain[i] - cipher[i]) % 29
    # We already have KEY47 which repeats. Let's verify it's truly periodic
    # by computing key[i] for positions > 47
    if len(p19) > 94:
        keys_from_cipher = [(decrypted_val - p19[i]) % 29 for i, decrypted_val in 
                           enumerate([(p19[j] + KEY47[j % 47]) % 29 for j in range(len(p19))])]
        # Check periodicity
        for period in range(1, 100):
            periodic = True
            for i in range(len(keys_from_cipher)):
                if keys_from_cipher[i] != keys_from_cipher[i % period]:
                    periodic = False
                    break
            if periodic:
                print(f"\nKey is periodic with period {period}")
                break

# Now check: does the hint tell us something?
# "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR"
# What if we take the PRIME values of each rune in the key and rearrange them?
print("\n=== REARRANGING PRIMES ANALYSIS ===")
print("Key as GP primes:", key_primes)
print("Key primes sorted:", sorted(key_primes))
print("Key primes unique:", sorted(set(key_primes)))
print(f"Sum of key primes: {sum(key_primes)}")
print(f"Product of key primes mod 29: {1}")  # too large
prod = 1
for p in key_primes:
    prod = (prod * p) % 29
print(f"Product of key primes mod 29: {prod}")

# Check: rearrange key by sorting prime values
sorted_by_prime = sorted(range(47), key=lambda i: key_primes[i])
rearranged_key = [KEY47[i] for i in sorted_by_prime]
print(f"\nKey rearranged by prime value: {rearranged_key}")
rearranged_text = ''.join(LATIN[v] for v in rearranged_key)
print(f"Rearranged key text: {rearranged_text}")
