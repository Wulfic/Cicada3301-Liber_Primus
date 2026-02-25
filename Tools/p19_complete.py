#!/usr/bin/env python3
"""Complete P19 decryption - find missing key values and full plaintext"""

GP = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4, '\u16B3':5, '\u16B7':6, '\u16B9':7,
    '\u16BB':8, '\u16BE':9, '\u16C1':10, '\u16C2':11, '\u16C4':11,
    '\u16C7':12, '\u16C8':13, '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23, '\u16AA':24, '\u16AB':25,
    '\u16A3':26, '\u16E1':27, '\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# Load P19
with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
    text = f.read()
p19_vals = [GP[ch] for ch in text if ch in GP]
print(f"P19: {len(p19_vals)} runes")
print(f"271 / 47 = {271 // 47} remainder {271 % 47}")

# Known key (first 43 values, ADD mode: plain = (cipher + key) % 29)
KNOWN_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 
             11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 
             21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

# Decode first 43 positions
first43 = [(p19_vals[i] + KNOWN_KEY[i]) % 29 for i in range(43)]
first43_text = ''.join(IDX2LAT[v] for v in first43)
print(f"First 43 plaintext: {first43_text}")

# If key length is 47, then positions 43-46 are unknown, 
# but position 47 reuses key[0]=24, position 48 uses key[1]=15, etc.

# First, let's see what we get at positions where key IS known (assuming length 47)
print("\n=== Decrypting positions where key is known (key length 47) ===")
full_plain = [None] * len(p19_vals)
for i in range(len(p19_vals)):
    key_idx = i % 47
    if key_idx < 43:
        full_plain[i] = (p19_vals[i] + KNOWN_KEY[key_idx]) % 29

# Print the known positions grouped
known_text = ""
for i in range(len(p19_vals)):
    if full_plain[i] is not None:
        known_text += IDX2LAT[full_plain[i]]
    else:
        known_text += "?"
print(f"Full text (? = unknown): {known_text}")

# Now let's try to figure out key[43..46] by looking at what makes sense
# With key length 47, the unknown positions are: 43,44,45,46, 90,91,92,93, 137,138,139,140, 184,185,186,187, 231,232,233,234
unknown_positions = [i for i in range(len(p19_vals)) if i % 47 >= 43]
print(f"\nUnknown positions ({len(unknown_positions)}): {unknown_positions}")
print(f"Cipher values at unknown positions:")
for pos in unknown_positions:
    key_idx = pos % 47
    print(f"  pos {pos} (key[{key_idx}]): cipher = {p19_vals[pos]} ({IDX2LAT[p19_vals[pos]]})")

# Brute force key[43..46] - only 29^4 = 707,281 combinations
# Score by: how many common letter patterns appear
print("\n=== Brute forcing key[43..46] ===")
# Common English digrams/trigrams in runeglish
# Most common rune frequencies in solved LP text match English-like distribution

best_score = -1
best_key = None

# For efficiency, we'll score based on whether the decoded text at unknown positions
# produces common GP values (frequent English letters)
# English letter frequency → GP: E(18), T(16), A(24), O(3), I(10), N(9), S(15), H(8), R(4)
common_gp = {18, 16, 24, 3, 10, 9, 15, 8, 4}  # top 9

for k43 in range(29):
    for k44 in range(29):
        for k45 in range(29):
            for k46 in range(29):
                trial_key = KNOWN_KEY + [k43, k44, k45, k46]
                score = 0
                for pos in unknown_positions:
                    key_idx = pos % 47
                    plain = (p19_vals[pos] + trial_key[key_idx]) % 29
                    if plain in common_gp:
                        score += 1
                if score > best_score:
                    best_score = score
                    best_key = [k43, k44, k45, k46]

print(f"Best frequency score: {best_score}/{len(unknown_positions)}")
print(f"Best key[43..46]: {best_key}")

# Now decode the full plaintext with the best key
full_key = KNOWN_KEY + best_key
full_plain_text = []
for i in range(len(p19_vals)):
    key_idx = i % 47
    plain = (p19_vals[i] + full_key[key_idx]) % 29
    full_plain_text.append(IDX2LAT[plain])
result = ''.join(full_plain_text)
print(f"\nFull plaintext with best key:")
print(result)

# Also try top N candidates
print("\n=== Top 20 candidates ===")
candidates = []
for k43 in range(29):
    for k44 in range(29):
        for k45 in range(29):
            for k46 in range(29):
                trial_key = KNOWN_KEY + [k43, k44, k45, k46]
                score = 0
                decoded = []
                for pos in unknown_positions:
                    key_idx = pos % 47
                    plain = (p19_vals[pos] + trial_key[key_idx]) % 29
                    decoded.append(plain)
                    if plain in common_gp:
                        score += 1
                candidates.append((score, [k43,k44,k45,k46], decoded))

candidates.sort(key=lambda x: -x[0])
for score, key_ext, decoded in candidates[:20]:
    # Show decoded text at unknown positions
    d_text = ''.join(IDX2LAT[v] for v in decoded)
    # Decode full text
    full_key = KNOWN_KEY + key_ext
    full_text = ''.join(IDX2LAT[(p19_vals[i] + full_key[i%47]) % 29] for i in range(len(p19_vals)))
    # Show just the segments around the unknowns
    seg1 = full_text[38:55]  # around pos 43-46
    seg2 = full_text[85:100]  # around pos 90-93
    print(f"key={key_ext}, score={score}, seg1=...{seg1}..., seg2=...{seg2}...")
