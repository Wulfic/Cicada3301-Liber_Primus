import sys, os
sys.stdout.reconfigure(encoding='utf-8')
GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load(p):
    with open('LiberPrimus/pages/page_%02d/runes.txt' % p, 'r', encoding='utf-8') as f:
        return [GP[c] for c in f.read() if c in GP]

p13 = load(13)
p71 = load(71)
p53 = load(53)
print("P13=%d P71=%d P53=%d runes" % (len(p13), len(p71), len(p53)))

t13 = ''.join(IDX[i] for i in p13)
t71 = ''.join(IDX[i] for i in p71)
print("P13 direct:", t13[:60])
print("P71 direct:", t71[:60])
print("P13 cleartext?", t13[:4] == 'SOME')

# Load P71 decoded
with open('LiberPrimus/pages/page_71/decoded.txt','r',encoding='utf-8') as f:
    d71 = f.read().strip()
print("P71 decoded:", d71[:80])

# P71 runes same as P13?
print("P71==P13?", p71 == p13)
print("P71[:125]==P13?", p71[:len(p13)] == p13)

# Convert decoded to GP
ENG = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26}
d71_gp = [ENG.get(c, -1) for c in d71.upper() if c in ENG]
print("\nP71 decoded GP[:20]:", d71_gp[:20])
print("P71 runes[:20]:    ", p71[:20])

# Key recovery
mn = min(len(d71_gp), len(p71))
ks = [(p71[i] - d71_gp[i]) % 29 for i in range(mn)]
ka = [(d71_gp[i] - p71[i]) % 29 for i in range(mn)]
kb = [(d71_gp[i] + p71[i]) % 29 for i in range(mn)]
print("\nSUB keys[:30]:", ks[:30])
print("ADD keys[:30]:", ka[:30])
print("BEAU keys[:30]:", kb[:30])

# Check periodicity
for nm, kk in [("SUB",ks),("ADD",ka),("BEAU",kb)]:
    for per in range(1, 30):
        ok = all(kk[i] == kk[i % per] for i in range(per, len(kk)))
        if ok:
            print("%s: periodic=%d key=%s" % (nm, per, kk[:per]))
            break

# Reversed gematria
print("\nReversed gematria shifts:")
for sh in range(29):
    r = [(28 - (v - sh)) % 29 for v in p71]
    tx = ''.join(IDX[i] for i in r)
    if 'SOME' in tx[:10]:
        print("  shift %d: %s" % (sh, tx[:80]))

# Caesar
for sh in range(29):
    r = [(v - sh) % 29 for v in p71]
    tx = ''.join(IDX[i] for i in r)
    if 'SOME' in tx[:10]:
        print("  Caesar %d: %s" % (sh, tx[:80]))

print("\nDone.")
