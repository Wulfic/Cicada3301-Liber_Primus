"""P02 Vigenere key recovery at period 35 (strongest IoC peak: 1.657)"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# English frequency in GP (approximate, from solved pages)
# F=0.065, U=0.025, TH=0.065, O=0.065, R=0.05, C=0.02, G=0.03, W=0.04, 
# H=0.06, N=0.06, I=0.06, J=0.005, EO=0.01, P=0.025, X=0.005, S=0.06,
# T=0.065, B=0.02, E=0.10, M=0.03, L=0.04, NG=0.02, OE=0.01, D=0.04, 
# A=0.07, AE=0.01, Y=0.02, IA=0.005, EA=0.005
# From actual solved Cicada text:
ENG_FREQ_29 = [0.0388, 0.0388, 0.0582, 0.0582, 0.0485, 0.0194, 0.0194, 0.0291,
               0.0485, 0.0582, 0.0679, 0.0097, 0.0097, 0.0194, 0.0097, 0.0582,
               0.0679, 0.0194, 0.0873, 0.0291, 0.0388, 0.0194, 0.0097, 0.0388,
               0.0679, 0.0097, 0.0194, 0.0097, 0.0097]

def load(p):
    with open('LiberPrimus/pages/page_%02d/runes.txt' % p, 'r', encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

def ioc(data):
    if len(data) < 2: return 0
    c = Counter(data)
    n = len(data)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)) * 29

def chi_squared(data, expected_freq, mod=29):
    """Chi-squared statistic between observed and expected"""
    n = len(data)
    if n == 0: return float('inf')
    c = Counter(data)
    chi = 0
    for i in range(mod):
        observed = c.get(i, 0)
        expected = expected_freq[i] * n
        if expected > 0:
            chi += (observed - expected) ** 2 / expected
    return chi

def recover_key_at_period(cipher, period, mode='SUB'):
    """Recover Vigenere key at given period using chi-squared"""
    key = []
    for col in range(period):
        column = [cipher[i] for i in range(col, len(cipher), period)]
        best_shift = 0
        best_chi = float('inf')
        for shift in range(29):
            if mode == 'SUB':
                decrypted = [(v - shift) % 29 for v in column]
            elif mode == 'ADD':
                decrypted = [(v + shift) % 29 for v in column]
            else:  # BEAU
                decrypted = [(shift - v) % 29 for v in column]
            chi = chi_squared(decrypted, ENG_FREQ_29)
            if chi < best_chi:
                best_chi = chi
                best_shift = shift
        key.append(best_shift)
    return key

def decrypt(cipher, key, mode='SUB'):
    period = len(key)
    result = []
    for i, c in enumerate(cipher):
        k = key[i % period]
        if mode == 'SUB':
            result.append((c - k) % 29)
        elif mode == 'ADD':
            result.append((c + k) % 29)
        else:
            result.append((k - c) % 29)
    return result

def score_english(text):
    bigrams = ['TH','HE','IN','AN','ER','ON','RE','AT','EN','ND','ST','OR','TE','ES','IS','IT','NT','TO','AR','SE','OU','ED','HA','OF']
    sc = 0
    for i in range(len(text)-1):
        if text[i:i+2] in bigrams:
            sc += 1
    # Also check common trigrams
    trigrams = ['THE','AND','ING','HER','HAT','HIS','THA','ERE','FOR','ENT','ION','TER','WAS','YOU','ITH','ALL','NOT','ARE','HAS','HER']
    for i in range(len(text)-2):
        if text[i:i+3] in trigrams:
            sc += 2
    return sc

p02 = load(2)
print("P02: %d runes" % len(p02))

# Verify IoC at various periods
print("\n=== Periodic IoC ===")
for per in [18, 35, 36, 43, 48]:
    cols = [[] for _ in range(per)]
    for i, v in enumerate(p02):
        cols[i % per].append(v)
    avg = sum(ioc(c) for c in cols) / per
    print("Period %d: avg IoC = %.3f %s" % (per, avg, '***' if avg > 1.4 else '**' if avg > 1.2 else ''))

# Key recovery at period 35
print("\n=== Key Recovery at Period 35 ===")
for mode in ['SUB', 'ADD', 'BEAU']:
    key = recover_key_at_period(p02, 35, mode)
    dec = decrypt(p02, key, mode)
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    ic = ioc(dec)
    key_text = ''.join(IDX[k] for k in key)
    print("\n%s mode:" % mode)
    print("  Key values: %s" % key)
    print("  Key text: %s" % key_text)
    print("  IoC: %.3f, Score: %d" % (ic, sc))
    print("  Text: %s" % text[:100])
    
    # Also try F-skip variant
    dec2 = []
    ki = 0
    for r in p02:
        if r == 0:
            dec2.append(0)
        else:
            k = key[ki % 35]
            if mode == 'SUB':
                dec2.append((r - k) % 29)
            elif mode == 'ADD':
                dec2.append((r + k) % 29)
            else:
                dec2.append((k - r) % 29)
            ki += 1
    text2 = ''.join(IDX[i] for i in dec2)
    sc2 = score_english(text2)
    ic2 = ioc(dec2)
    if sc2 > sc:
        print("  F-skip: IoC=%.3f, Score=%d" % (ic2, sc2))
        print("  F-skip text: %s" % text2[:100])

# Also try other strong periods
print("\n=== Key Recovery at Period 36 ===")
for mode in ['SUB', 'ADD', 'BEAU']:
    key = recover_key_at_period(p02, 36, mode)
    dec = decrypt(p02, key, mode)
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    ic = ioc(dec)
    print("  %s: IoC=%.3f, Score=%d  %s..." % (mode, ic, sc, text[:60]))

print("\n=== Key Recovery at Period 48 ===")
for mode in ['SUB', 'ADD', 'BEAU']:
    key = recover_key_at_period(p02, 48, mode)
    dec = decrypt(p02, key, mode)
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    ic = ioc(dec)
    print("  %s: IoC=%.3f, Score=%d  %s..." % (mode, ic, sc, text[:60]))

# Try the existing partial solution key length 43
print("\n=== Key Recovery at Period 43 (existing partial) ===")
for mode in ['SUB', 'ADD', 'BEAU']:
    key = recover_key_at_period(p02, 43, mode)
    dec = decrypt(p02, key, mode)
    text = ''.join(IDX[i] for i in dec)
    sc = score_english(text)
    ic = ioc(dec)
    print("  %s: IoC=%.3f, Score=%d  %s..." % (mode, ic, sc, text[:60]))

# Brute force all periods 2-60
print("\n=== Best results across all periods 2-60 ===")
best_results = []
for per in range(2, 61):
    for mode in ['SUB', 'ADD', 'BEAU']:
        key = recover_key_at_period(p02, per, mode)
        dec = decrypt(p02, key, mode)
        text = ''.join(IDX[i] for i in dec)
        sc = score_english(text)
        ic = ioc(dec)
        best_results.append((per, mode, sc, ic, text[:50], key))

best_results.sort(key=lambda x: -x[2])
for per, mode, sc, ic, txt, key in best_results[:15]:
    print("  period=%d %s: score=%d IoC=%.3f %s" % (per, mode, sc, ic, txt))

print("\nDone.")
