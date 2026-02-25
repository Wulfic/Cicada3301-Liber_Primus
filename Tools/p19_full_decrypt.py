"""Full P19 decryption with word boundaries, all methods."""
import os

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
OLD_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# Parse page 19 with word structure
with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

# Build word-structured cipher
words = []
current = []
all_runes = []
for c in raw:
    if c in GP:
        v = GP[c]
        current.append(v)
        all_runes.append(v)
    elif c in '•:.\'-\n\r \t' and current:
        words.append(current)
        current = []
if current:
    words.append(current)

print(f"Total runes: {len(all_runes)}")
print(f"Total words: {len(words)}")
print(f"Word lengths: {[len(w) for w in words]}")
print()

# === Decrypt ALL with old key, ADD, show with word boundaries ===
print("="*80)
print("FULL DECRYPTION: Old key (period 47), ADD, with word boundaries")
print("="*80)
decrypted = [(all_runes[i] + OLD_KEY[i % 47]) % 29 for i in range(len(all_runes))]

pos = 0
for wi, word in enumerate(words):
    n = len(word)
    word_dec = decrypted[pos:pos+n]
    word_lat = ''.join(LATIN[v] for v in word_dec)
    word_cipher = ''.join(LATIN[v] for v in word)
    print(f"  w{wi:02d} [{pos:3d}-{pos+n-1:3d}]: {word_lat:20s}  (cipher: {word_cipher})")
    pos += n

# === Also try Beaufort: plain = (key - cipher) % 29 ===
print()
print("="*80)
print("FULL DECRYPTION: Old key (period 47), BEAUFORT, with word boundaries")
print("="*80)
decrypted_b = [(OLD_KEY[i % 47] - all_runes[i]) % 29 for i in range(len(all_runes))]

pos = 0
for wi, word in enumerate(words):
    n = len(word)
    word_dec = decrypted_b[pos:pos+n]
    word_lat = ''.join(LATIN[v] for v in word_dec)
    print(f"  w{wi:02d} [{pos:3d}-{pos+n-1:3d}]: {word_lat:20s}")
    pos += n

# === Try: Key only advances on non-separator positions (same as above, just confirming) ===
# Already done above since `all_runes` strips separators.

# === Try different key periods near 47 ===
print()
print("="*80)
print("TESTING KEY PERIODS around 47")
print("="*80)

# The first 45 runes are known. Derive key values for those positions.
# Known plaintext GP values:
known_plain = [4,18,24,4,4,24,9,6,10,9,6,  # REARRANGING (11)
               2,18,                          # THE (2)
               13,4,10,19,18,15,              # PRIMES (6)
               9,1,19,17,18,4,15,             # NUMBERS (7)
               7,10,20,20,                    # WILL (4)
               15,8,3,7,                      # SHOW (4)
               24,                            # A (1)
               13,24,2,                       # PATH (3)
               16,3,                          # TO (2)
               2,18,                          # THE (2)
               23,12,4]                       # DEOR (3)

print(f"Known plaintext: {len(known_plain)} runes")

# Derive key at each position
derived_key = [(known_plain[i] - all_runes[i]) % 29 for i in range(len(known_plain))]
print(f"Derived key values (first {len(derived_key)}): {derived_key}")
print(f"  As text: {''.join(LATIN[v] for v in derived_key)}")

# Compare with old key
print(f"\nOld key:               {OLD_KEY}")
match_count = sum(1 for i in range(min(len(derived_key), len(OLD_KEY))) if derived_key[i] == OLD_KEY[i])
print(f"Matches with old key (first {min(len(derived_key), len(OLD_KEY))} positions): {match_count}")

# Check all possible periods from 2 to 50
print(f"\nPeriod analysis (mismatches / total checks):")
for period in range(2, 55):
    mismatches = 0
    checks = 0
    for i in range(len(derived_key)):
        for j in range(i + period, len(derived_key), period):
            checks += 1
            if derived_key[i] != derived_key[j]:
                mismatches += 1
    if checks > 0:
        pct = 100 * mismatches / checks
        marker = " <-- OLD PERIOD" if period == 47 else ""
        if pct < 30 or period == 47:
            print(f"  Period {period:3d}: {mismatches:3d}/{checks:3d} = {pct:5.1f}%{marker}")

# === What if we need to remove/skip J runes for the key cycle? ===
print()
print("="*80)
print("KEY EXPERIMENT: Skip J runes (value 11) for key positioning")
print("="*80)

# Maybe J runes are literal (plaintext J) and key doesn't advance
key_idx = 0
dec_skip_j = []
for i, v in enumerate(all_runes):
    if v == 11:  # J rune
        dec_skip_j.append(11)  # literal J
    else:
        dec_skip_j.append((v + OLD_KEY[key_idx % 47]) % 29)
        key_idx += 1

pos = 0
print(f"Decrypt with J-skip (J literal, key advances on non-J only):")
for wi, word in enumerate(words[:20]):
    n = len(word)
    word_dec = dec_skip_j[pos:pos+n]
    word_lat = ''.join(LATIN[v] for v in word_dec)
    print(f"  w{wi:02d}: {word_lat}")
    pos += n

# === What if key was derived from 255-rune cipher (J excluded) ===
print()
print("="*80)  
print("KEY EXPERIMENT: Use old key on current cipher but skip J in key index")
print("="*80)

# Concept: positions with J don't consume a key element
j_rune_positions = set()
rune_idx = 0
for c in raw:
    if c in GP:
        if c in ['\u16C4', '\u16C2']:
            j_rune_positions.add(rune_idx)
        rune_idx += 1

key_idx = 0
dec_jskip = []
for i, v in enumerate(all_runes):
    dec_jskip.append((v + OLD_KEY[key_idx % 47]) % 29)
    if i not in j_rune_positions:
        key_idx += 1  # Only advance key on non-J positions

pos = 0
for wi, word in enumerate(words[:20]):
    n = len(word)
    word_dec = dec_jskip[pos:pos+n]
    word_lat = ''.join(LATIN[v] for v in word_dec)
    word_cipher = ''.join(LATIN[v] for v in word)
    print(f"  w{wi:02d}: {word_lat:20s}  (cipher: {word_cipher})")
    pos += n
