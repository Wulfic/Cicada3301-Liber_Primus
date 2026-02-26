#!/usr/bin/env python3
"""Quick P03 decryption verifier."""
RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
R2I = {r: i for i, r in enumerate(RUNES)}
R2I[chr(0x16C4)] = 11
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29

with open('LiberPrimus/pages/page_03/runes.txt', 'r', encoding='utf-8') as f:
    raw = f.read()
cipher = [R2I[ch] for ch in raw if ch in R2I]
print(f"Total runes: {len(cipher)}")
fpos = [i for i, v in enumerate(cipher) if v == 0]
print(f"F positions ({len(fpos)}): {fpos}")

KEY = [23, 10, 1, 10, 9, 10, 16, 26]

# Method A: SUB no skip
p = [(c - KEY[i % 8]) % MOD for i, c in enumerate(cipher)]
t = ''.join(LAT[x] for x in p)
print(f"\nA) SUB no-skip:\n{t[:200]}")

# Method B: SUB with F-skip where cipher=key[k%8] → plaintext F, skip
plain = []; k = 0
for c in cipher:
    if c == KEY[k % 8]:
        plain.append(0)
    else:
        plain.append((c - KEY[k % 8]) % MOD)
        k += 1
t2 = ''.join(LAT[x] for x in plain)
print(f"\nB) SUB F-skip(cipher==key):\n{t2[:200]}")

# Method C: SUB with F-skip where cipher==0 → literal F, skip
plain3 = []; k = 0
for c in cipher:
    if c == 0:
        plain3.append(0)
    else:
        plain3.append((c - KEY[k % 8]) % MOD)
        k += 1
t3 = ''.join(LAT[x] for x in plain3)
print(f"\nC) SUB F-skip(cipher==0):\n{t3[:200]}")

# Method D: Print rune-by-rune around position 48-60 for debugging
print("\n--- Debug positions 45-65 (SUB no-skip) ---")
for i in range(45, min(65, len(cipher))):
    c = cipher[i]
    ki = KEY[i % 8]
    p_val = (c - ki) % MOD
    rune_char = [k for k, v in R2I.items() if v == c and len(k) == 1][0] if c < 29 else '?'
    print(f"pos {i:3d}: cipher={c:2d}({rune_char}) key[{i%8}]={ki:2d} → plain={p_val:2d}={LAT[p_val]}")
