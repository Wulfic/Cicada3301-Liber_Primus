"""
P62 — F-skip DIVINITY hypothesis.
Key insight: 121 runes - 9 F_runes = 112 non-F runes = 14 * 8 (DIVINITY length).
If F runes are literal (output F, don't advance key), the key cycles EXACTLY.
"""
import os
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

DIGRAPHS_ORDERED = [('TH',2),('NG',21),('EA',28),('OE',22),('EO',12),('AE',25),('IA',27)]
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
    while i < len(text):
        found = False
        for dg, val in DIGRAPHS_ORDERED:
            if text[i:i+len(dg)] == dg:
                result.append(val)
                i += len(dg)
                found = True
                break
        if not found:
            if text[i] in ENG2GP:
                result.append(ENG2GP[text[i]])
            i += 1
    return result

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

with open('LiberPrimus/pages/page_62/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)

# Find F positions
f_positions = [i for i in range(N) if cipher[i] == 0]
non_f_count = N - len(f_positions)
print(f"P62: {N} runes, F positions ({len(f_positions)}): {f_positions}")
print(f"Non-F runes: {non_f_count} = {non_f_count//8} * 8 + {non_f_count%8}")

DIVINITY = eng_to_gp("DIVINITY")
KL = len(DIVINITY)
print(f"DIVINITY: {DIVINITY} = {gp_to_lat(DIVINITY)}")

# ===== F-SKIP DECRYPTION =====
print("\n" + "="*80)
print("F-SKIP VIGENÈRE WITH DIVINITY KEY")
print("="*80)

def f_skip_decrypt(cipher, key, init_off, mode='SUB'):
    """Decrypt with F-skip: F runes are literal, key only advances for non-F runes."""
    result = []
    k = init_off
    kl = len(key)
    for i in range(len(cipher)):
        if cipher[i] == 0:
            result.append(0)  # Literal F
        else:
            kv = key[k % kl]
            if mode == 'SUB':
                result.append((cipher[i] - kv) % MOD)
            elif mode == 'ADD':
                result.append((cipher[i] + kv) % MOD)
            elif mode == 'BEAU':
                result.append((kv - cipher[i]) % MOD)
            k += 1
    return result

# Score by word count
def score_text(text):
    s = 0
    for w in ['WISDOM','THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS','WHICH','ARE',
              'WITHIN','HOLY','LIVES','EACH','BEING','UNTO','YOURSELF','INTELLIGENCE',
              'INSTRUCTION','COMMAND','YOUR','OWN','SELF','LAW','SACRED','DIVINITY',
              'PILGRIM','TRUTH','BELIEVE','NOTHING','FIND']:
        c = text.count(w)
        s += c * len(w)
    return s

best_results = []
for mode in ['SUB', 'ADD', 'BEAU']:
    for off in range(KL):
        dec = f_skip_decrypt(cipher, DIVINITY, off, mode)
        text = gp_to_lat(dec)
        sc = score_text(text)
        best_results.append((sc, mode, off, text, dec))

best_results.sort(reverse=True)
print("\nAll F-skip results (sorted by score):")
for sc, mode, off, text, dec in best_results[:16]:
    print(f"  {mode:5s} off={off}: score={sc:3d} | {text[:120]}")

# Print the BEST result in detail
print("\n" + "="*80)
print("BEST F-SKIP RESULT - DETAILED")
print("="*80)

best_sc, best_mode, best_off, best_text, best_dec = best_results[0]
print(f"Mode: {best_mode}, offset: {best_off}, score: {best_sc}")
print(f"Full text: {best_text}")
print(f"GP values: {best_dec}")

# Show word boundaries (insert spaces at DIVINITY key restarts)
print("\n--- Word-segmented view ---")
# Try to segment into words
import re
# Known words in Cicada context
WORD_LIST = ['WISDOM','YOU','ARE','A','BEING','UNTO','YOURSELF','LAW','EACH','INTELLIGENCE',
             'IS','HOLY','FOR','ALL','THAT','LIVES','AN','INSTRUCTION','COMMAND','YOUR','OWN','SELF',
             'THE','AND','HAVE','WHAT','WE','NOT','THIS','WHICH','WITH','BUT','FROM','THEY',
             'WILL','THEIR','HAS','DO','WITHIN','FIND','BELIEVE','NOTHING','SACRED','TRUTH',
             'PILGRIM','TEST','SEEK','KNOW','TRUE','DEEP','WEB','HASHES','EXISTS','END','PAGE',
             'DUTY','EVERY','PRESERVE','WEAK','CONSUME','ENOUGH','FOLLOW','DOGMA','BELONG',
             'CIRCUMFERENCE','DIVINITY','LOSS','PARABLE','INSTAR','KOAN','MASTER','LOSS',
             'PRACTICE','THREE','BEHAVIORS','CAUSE']

# Greedy word matching
pos = 0
words = []
while pos < len(best_text):
    found = False
    for wlen in range(min(20, len(best_text)-pos), 0, -1):
        chunk = best_text[pos:pos+wlen]
        if chunk in WORD_LIST:
            words.append(chunk)
            pos += wlen
            found = True
            break
    if not found:
        words.append(best_text[pos])
        pos += 1

print(' '.join(words))

# ===== ALSO TEST: F-skip with separator advancement =====
print("\n" + "="*80)
print("F-SKIP + SEPARATOR ADVANCEMENT")
print("="*80)

# Read raw for separator positions
char_stream = []
rune_idx = 0
for ch in raw:
    if ch in GP:
        char_stream.append(('R', GP[ch], rune_idx))
        rune_idx += 1
    elif ch == '\u2022':
        char_stream.append(('S', None, None))
    elif ch == '\n':
        char_stream.append(('N', None, None))

# Compute cumulative sep/nl before each rune
sep_before = [0]*N
nl_before = [0]*N
cs = cn = 0
for item in char_stream:
    if item[0] == 'S': cs += 1
    elif item[0] == 'N': cn += 1
    elif item[0] == 'R':
        sep_before[item[2]] = cs
        nl_before[item[2]] = cn

def f_skip_sep_decrypt(cipher, key, init_off, sep_adv, nl_adv, mode='SUB'):
    """F-skip + separator/newline key advancement."""
    result = []
    k = init_off
    kl = len(key)
    for i in range(len(cipher)):
        if cipher[i] == 0:
            result.append(0)  # Literal F
        else:
            extra = sep_before[i] * sep_adv + nl_before[i] * nl_adv
            ki = (k + extra) % kl
            kv = key[ki]
            if mode == 'SUB':
                result.append((cipher[i] - kv) % MOD)
            elif mode == 'ADD':
                result.append((cipher[i] + kv) % MOD)
            elif mode == 'BEAU':
                result.append((kv - cipher[i]) % MOD)
            k += 1
    return result

best_sep = []
for mode in ['SUB', 'ADD', 'BEAU']:
    for off in range(KL):
        for sa in range(5):
            for na in range(5):
                dec = f_skip_sep_decrypt(cipher, DIVINITY, off, sa, na, mode)
                text = gp_to_lat(dec)
                sc = score_text(text)
                if sc >= 30:
                    best_sep.append((sc, mode, off, sa, na, text))

best_sep.sort(reverse=True)
print(f"\nTop 20 F-skip + separator results (score >= 30):")
for sc, mode, off, sa, na, text in best_sep[:20]:
    print(f"  {mode:5s} off={off} sep_adv={sa} nl_adv={na}: score={sc:3d} | {text[:100]}")

# ===== KEY RECOVERY for best F-skip result =====
print("\n" + "="*80)
print("KEY RECOVERY FROM BEST F-SKIP RESULT")
print("="*80)

# Take the best result and recover what key was actually used
best_sc, best_mode, best_off, best_text, best_dec = best_results[0]

# The key used at each non-F position
key_used = []
k = best_off
for i in range(N):
    if cipher[i] == 0:
        key_used.append(('F-skip', 0))
    else:
        ki = k % KL
        key_used.append(('key', DIVINITY[ki]))
        k += 1

# Show which DIVINITY position was used for each rune
print("Rune | Cipher | KeyIdx | Key | Plain | Lat")
for i in range(N):
    if cipher[i] == 0:
        print(f"  {i:3d} |   F(0) |  skip  |  -  |  F(0) |  F")
    else:
        ki_label = key_used[i]
        print(f"  {i:3d} | {LAT[cipher[i]]:3s}({cipher[i]:2d}) | D[{(best_off + sum(1 for j in range(i) if cipher[j]!=0))%KL}]   | {LAT[DIVINITY[(best_off + sum(1 for j in range(i) if cipher[j]!=0))%KL]]:3s}({DIVINITY[(best_off + sum(1 for j in range(i) if cipher[j]!=0))%KL]:2d}) | {LAT[best_dec[i]]:3s}({best_dec[i]:2d}) |  {LAT[best_dec[i]]}")

print("\n=== DONE ===")
