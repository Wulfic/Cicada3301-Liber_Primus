"""Investigate P71 decoded.txt discrepancy - how was it generated?"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English -> GP value
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':0}

def load(p):
    with open(f'LiberPrimus/pages/page_{p:02d}/runes.txt','r',encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def load_decoded(p):
    with open(f'LiberPrimus/pages/page_{p:02d}/decoded.txt','r',encoding='utf-8') as f:
        return f.read().strip()

p13_runes = load(13)
p71_runes = load(71)
p53_runes = load(53)

print(f"P13: {len(p13_runes)} runes")
print(f"P71: {len(p71_runes)} runes")
print(f"P53: {len(p53_runes)} runes")

# Direct gematria
p13_text = ''.join(IDX[i] for i in p13_runes)
p71_text = ''.join(IDX[i] for i in p71_runes)
p53_text = ''.join(IDX[i] for i in p53_runes)

print(f"\nP13 direct gematria: {p13_text}")
print(f"P71 direct gematria: {p71_text[:100]}...")
print(f"P53 direct gematria: {p53_text[:100]}...")

# Check if P13 is direct cleartext
starts_some = p13_text[:4]
print(f"\nP13 starts with: '{starts_some}' (expect 'SOME')")
p13_is_cleartext = 'SOME' in p13_text[:10]
print(f"P13 is cleartext: {p13_is_cleartext}")

# Load decoded texts
p71_decoded = load_decoded(71)
try:
    p13_decoded = load_decoded(13)
except:
    p13_decoded = "N/A"

print(f"\nP71 decoded.txt: {p71_decoded[:100]}")
print(f"P13 decoded.txt: {p13_decoded[:100]}")

# Are P13 and P71 runes the same?
print(f"\nP13 == P71? {p13_runes == p71_runes}")
print(f"P71[:len(p13)] == P13? {p71_runes[:len(p13_runes)] == p13_runes}")

# Check: maybe P13 is ALSO not cleartext, and uses same cipher as P71?
# P13 is in LP1 pages 00-16 which are supposedly all solved
# Let me check what P13 actually decodes to

# Convert decoded text to GP values
def text_to_gp(text):
    """Convert English text to GP values, handling digraphs"""
    vals = []
    i = 0
    text = text.upper()
    while i < len(text):
        if i+1 < len(text):
            di = text[i:i+2]
            if di in ['TH','NG','EO','OE','EA','AE','IA']:
                # Find index
                idx_map = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
                vals.append(idx_map[di])
                i += 2
                continue
        if text[i] in ENG2GP:
            vals.append(ENG2GP[text[i]])
        i += 1
    return vals

# Check if decoded.txt matches P13 runes directly
# (it might match without digraph handling)
print(f"\n--- Comparing P13 runes vs P13 decoded ---")
if p13_decoded != "N/A":
    p13_dec_gp = text_to_gp(p13_decoded)
    print(f"P13 decoded as GP values: {p13_dec_gp[:20]}")
    print(f"P13 runes:                {p13_runes[:20]}")
    match = sum(1 for a,b in zip(p13_dec_gp, p13_runes) if a==b)
    print(f"Direct match: {match}/{min(len(p13_dec_gp), len(p13_runes))}")

print("\n--- Comparing P71 runes vs P71 decoded ---")
p71_dec_gp = text_to_gp(p71_decoded)
print(f"P71 decoded as GP values: {p71_dec_gp[:20]}")
print(f"P71 runes:                {p71_runes[:20]}")
match71 = sum(1 for a,b in zip(p71_dec_gp, p71_runes) if a==b)
print(f"Direct match: {match71}/{min(len(p71_dec_gp), len(p71_runes))}")

# Try: what key values make P71 runes -> P71 decoded? 
# SUB mode: decoded[i] = (cipher[i] - key[i]) % 29
# ADD mode: decoded[i] = (cipher[i] + key[i]) % 29
# BEAU mode: decoded[i] = (key[i] - cipher[i]) % 29
print("\n--- Key recovery: P71 runes -> P71 decoded ---")
min_len = min(len(p71_dec_gp), len(p71_runes))
keys_sub = [(p71_runes[i] - p71_dec_gp[i]) % 29 for i in range(min_len)]
keys_add = [(p71_dec_gp[i] - p71_runes[i]) % 29 for i in range(min_len)]
keys_beau = [(p71_dec_gp[i] + p71_runes[i]) % 29 for i in range(min_len)]

print(f"SUB keys:  {keys_sub[:30]}")
print(f"ADD keys:  {keys_add[:30]}")
print(f"BEAU keys: {keys_beau[:30]}")

# Check if any key set is periodic
from collections import Counter
for name, keys in [("SUB", keys_sub), ("ADD", keys_add), ("BEAU", keys_beau)]:
    for period in range(1, 20):
        ok = True
        for i in range(period, len(keys)):
            if keys[i] != keys[i % period]:
                ok = False
                break
        if ok:
            print(f"  {name}: PERIODIC with period {period}! Key = {keys[:period]}")
            break

# Check: maybe the decoded text was produced by Atbash + shift (reversed gematria)
# Like pages 06-09: plain[i] = (28 - (rune[i] - shift)) % 29
print("\n--- Reversed gematria (Atbash + shift) ---")
for shift in range(29):
    result = [(28 - (r - shift)) % 29 for r in p71_runes]
    text = ''.join(IDX[i] for i in result)
    # Check if it starts with SOME
    if 'SOME' in text[:10] or 'WISDOM' in text[:20]:
        print(f"  Shift {shift}: {text[:80]}")
        
# Check all Caesar shifts
print("\n--- Caesar shifts on P71 ---")
for shift in range(29):
    result = [(r - shift) % 29 for r in p71_runes]
    text = ''.join(IDX[i] for i in result)
    if 'SOME' in text[:10]:
        print(f"  Caesar {shift}: {text[:80]}")

# Maybe P71 uses Totient cipher (like P55/P73)?
print("\n--- Totient cipher on P71 ---")
def get_primes(n):
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes

primes = get_primes(400)
for offset in range(20):
    result = []
    ki = 0
    for i, r in enumerate(p71_runes):
        if r == 0:  # F-skip
            result.append(0)
        else:
            p = primes[ki + offset]
            result.append((r - (p - 1)) % 29)
            ki += 1
    text = ''.join(IDX[i] for i in result)
    if 'SOME' in text[:15] or 'WISDOM' in text[:30]:
        print(f"  Totient offset {offset}: {text[:80]}")

# No F-skip version
for offset in range(20):
    result = []
    for i, r in enumerate(p71_runes):
        p = primes[i + offset]
        result.append((r - (p - 1)) % 29)
    text = ''.join(IDX[i] for i in result)
    if 'SOME' in text[:15] or 'WISDOM' in text[:30]:
        print(f"  Totient no-skip offset {offset}: {text[:80]}")

# Maybe P71 uses Vigenère with DIVINITY?
print("\n--- Vigenère DIVINITY on P71 ---")
DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]
for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29), ("BEAU", lambda c,k: (k-c)%29)]:
    for offset in range(len(DIVINITY)):
        # Standard Vigenère
        result = [mode_fn(p71_runes[i], DIVINITY[(i+offset) % len(DIVINITY)]) for i in range(len(p71_runes))]
        text = ''.join(IDX[i] for i in result)
        if 'SOME' in text[:10]:
            print(f"  {mode_name} offset {offset}: {text[:80]}")
        
        # F-skip
        result2 = []
        ki = offset
        for r in p71_runes:
            if r == 0:
                result2.append(0)
            else:
                result2.append(mode_fn(r, DIVINITY[ki % len(DIVINITY)]))
                ki += 1
        text2 = ''.join(IDX[i] for i in result2)
        if 'SOME' in text2[:10]:
            print(f"  {mode_name} F-skip offset {offset}: {text2[:80]}")

# Check: maybe P13 uses the same cipher and its decoded.txt is also wrong?
# Or maybe P13 IS cleartext and P71 decoded.txt was just COPIED from P13
print("\n=== CRITICAL: Is P13 direct gematria = cleartext? ===")
print(f"P13 direct gematria text: {p13_text}")
# Check if SOMEWISDOM appears
if 'SOMEWISDOM' in p13_text:
    print("YES - P13 IS direct cleartext ('SOMEWISDOM' found)")
else:
    print("NO - P13 is NOT direct cleartext")
    # What does P13 decode to?
    print(f"P13 text starts with: {p13_text[:30]}")

# Check P53 relationship
print("\n=== P53 vs P71 rune overlap ===")
print(f"P53 runes == P71[:232]? {p53_runes == p71_runes[:len(p53_runes)]}")
print(f"P53 len: {len(p53_runes)}, P71 len: {len(p71_runes)}")
