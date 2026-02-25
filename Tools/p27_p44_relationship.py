"""Exploit P27=P44[:234] relationship to understand the cipher layers.
P27 (234 runes) = P44[:234] (identical ciphertext)
P27 keyword: SHADOWS, ADD mode (IoC ~2.10)
P44 best Caesar: shift 23
Try: Caesar 23 + SHADOWS ADD on P44, or SHADOWS ADD alone, etc."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# All keywords from P63
KEYWORDS = {
    'CABAL': [5,24,17,24,20],
    'DIVINITY': [23,10,1,10,9,10,16,26],
    'ENCRYPTION': [18,9,5,4,26,13,16,10,3,9],
    'OBSCURA': [3,17,15,5,1,4,24],
    'ENCRYPT': [18,9,5,4,26,13,16],
    'SHADOWS': [15,8,24,23,3,7,15],
    'DEOR': [23,18,3,4],
    'TOTIENT': [16,3,16,10,18,9,16],
    'MOURNFUL': [19,3,1,4,9,0,1,20],
}

# P21-30 assignments from P63
PAGE_KEYS = {
    21: ('CABAL', 'BEAU'),
    22: ('DIVINITY', 'BEAU'),
    23: ('ENCRYPTION', 'ADD'),
    24: ('OBSCURA', 'BEAU'),
    # 25: CABAL/BEAU (CORRUPTED)
    26: ('ENCRYPT', 'ADD'),
    27: ('SHADOWS', 'ADD'),
    28: ('DEOR', 'SUB'),
    29: ('TOTIENT', 'BEAU'),
    30: ('MOURNFUL', 'ADD'),
}

def load(p):
    with open('LiberPrimus/pages/page_%02d/runes.txt' % p, 'r', encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def ioc(data):
    if len(data) < 2: return 0
    c = Counter(data)
    n = len(data)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)) * 29

def apply_vig(data, key, mode):
    kl = len(key)
    result = []
    for i, c in enumerate(data):
        k = key[i % kl]
        if mode == 'SUB': result.append((c - k) % 29)
        elif mode == 'ADD': result.append((c + k) % 29)
        else: result.append((k - c) % 29)
    return result

def score_text(text):
    bigrams = ['TH','HE','IN','AN','ER','ON','RE','AT','EN','ND','ST','OR','TE','ES','IS','IT','NT','TO','AR','SE','OU','ED','HA','OF']
    sc = sum(1 for i in range(len(text)-1) if text[i:i+2] in bigrams)
    words = ['THE','AND','THAT','WITH','THIS','FROM','HAVE','WILL','YOUR','THEM','THAN','EACH','MAKE','SOME','WERE','BEEN','NOT','ALL','ARE','FOR','WAS','BUT']
    for w in words:
        if w in text:
            sc += len(w)
    return sc

p27 = load(27)
p44 = load(44)
p53 = load(53)
p71 = load(71)

print("P27: %d, P44: %d, P53: %d, P71: %d runes" % (len(p27), len(p44), len(p53), len(p71)))
print("P27 == P44[:234]:", p27 == p44[:len(p27)])
print("P53 == P71[:232]:", p53 == p71[:len(p53)])

# === Test 1: SHADOWS ADD on P27 ===
print("\n=== Test 1: SHADOWS ADD on P27 (234 runes) ===")
key = KEYWORDS['SHADOWS']
dec27 = apply_vig(p27, key, 'ADD')
t27 = ''.join(IDX[i] for i in dec27)
print("IoC: %.3f, Score: %d" % (ioc(dec27), score_text(t27)))
print("Text:", t27[:80])

# === Test 2: SHADOWS ADD on P44 (full 1433 runes) ===
print("\n=== Test 2: SHADOWS ADD on full P44 (1433 runes) ===")
dec44s = apply_vig(p44, key, 'ADD')
t44s = ''.join(IDX[i] for i in dec44s)
print("IoC: %.3f, Score: %d" % (ioc(dec44s), score_text(t44s)))
print("Text[:80]:", t44s[:80])
# Check IoC of first 234 vs rest
print("  First 234 IoC: %.3f" % ioc(dec44s[:234]))
print("  Rest IoC: %.3f" % ioc(dec44s[234:]))

# === Test 3: Caesar 23 on P44, then SHADOWS ADD ===
print("\n=== Test 3: Caesar 23 then SHADOWS ADD on P44 ===")
p44_caesar = [(v - 23) % 29 for v in p44]
dec44cs = apply_vig(p44_caesar, key, 'ADD')
t44cs = ''.join(IDX[i] for i in dec44cs)
print("IoC: %.3f, Score: %d" % (ioc(dec44cs), score_text(t44cs)))
print("Text[:80]:", t44cs[:80])

# === Test 4: SHADOWS ADD on P44, then Caesar (various shifts) ===
print("\n=== Test 4: SHADOWS ADD then Caesar on P44 ===")
for sh in range(29):
    dec = [(v - sh) % 29 for v in dec44s]
    t = ''.join(IDX[i] for i in dec)
    sc = score_text(t)
    if sc > 80:
        print("  Caesar %d: IoC=%.3f score=%d %s..." % (sh, ioc(dec), sc, t[:60]))

# === Test 5: Try ALL keywords on P44 ===
print("\n=== Test 5: All keywords on P44 (1433 runes) ===")
for kname, kvals in KEYWORDS.items():
    for mode in ['SUB', 'ADD', 'BEAU']:
        dec = apply_vig(p44, kvals, mode)
        t = ''.join(IDX[i] for i in dec)
        sc = score_text(t)
        ic = ioc(dec)
        if ic > 1.3 or sc > 80:
            print("  %s %s: IoC=%.3f score=%d %s..." % (kname, mode, ic, sc, t[:60]))

# === Test 6: Combined keyword + Caesar on P44 ===
print("\n=== Test 6: Keyword + Caesar on P44 ===")
best = []
for kname, kvals in KEYWORDS.items():
    for mode in ['SUB', 'ADD', 'BEAU']:
        for sh in range(29):
            # Caesar first, then keyword
            p44c = [(v - sh) % 29 for v in p44]
            dec = apply_vig(p44c, kvals, mode)
            t = ''.join(IDX[i] for i in dec)
            sc = score_text(t)
            ic = ioc(dec)
            best.append((sc, ic, kname, mode, sh, t[:60]))
            
            # Keyword first, then Caesar
            dec2 = apply_vig(p44, kvals, mode)
            dec2c = [(v - sh) % 29 for v in dec2]
            t2 = ''.join(IDX[i] for i in dec2c)
            sc2 = score_text(t2)
            ic2 = ioc(dec2c)
            best.append((sc2, ic2, kname + '+Caesar', mode, sh, t2[:60]))

best.sort(key=lambda x: -x[0])
for sc, ic, kn, mode, sh, txt in best[:10]:
    print("  %s %s shift=%d: IoC=%.3f score=%d %s..." % (kn, mode, sh, ic, sc, txt))

# === Test 7: Periodic IoC of P44 after SHADOWS ADD ===
print("\n=== Test 7: Periodic IoC of P44 after SHADOWS ADD ===")
for per in range(2, 50):
    cols = [[] for _ in range(per)]
    for i, v in enumerate(dec44s):
        cols[i % per].append(v)
    avg = sum(ioc(c) for c in cols) / per
    if avg > 1.3:
        print("  Period %d: %.3f %s" % (per, avg, '***' if avg > 1.5 else '**'))

# === Test 8: Same analysis for P27: Periodic IoC after SHADOWS ADD ===
print("\n=== Test 8: Periodic IoC of P27 after SHADOWS ADD ===")
for per in range(2, 50):
    cols = [[] for _ in range(per)]
    for i, v in enumerate(dec27):
        cols[i % per].append(v)
    avg = sum(ioc(c) for c in cols) / per
    if avg > 1.3:
        print("  Period %d: %.3f %s" % (per, avg, '***' if avg > 1.5 else '**'))

print("\nDone.")
