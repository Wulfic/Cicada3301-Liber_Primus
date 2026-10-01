"""Verify key parsing correction for P17 and P28"""
GP = {chr(k):v for k,v in [(0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),(0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),(0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),(0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),(0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
IDX = {0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',27:'IA',28:'EA'}

def load_runes(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    words = []; current = []
    for ch in text:
        if ch in GP: current.append(GP[ch])
        elif ch == '\u2022' or ch in '-. \n':
            if current: words.append(current); current = []
    if current: words.append(current)
    flat = [r for w in words for r in w]
    return flat, words

def ioc(r):
    n = len(r); freq = [0]*29
    for x in r: freq[x] += 1
    return sum(f*(f-1) for f in freq)/(n*(n-1))*29 if n > 1 else 0

def decrypt_sub(flat, key):
    return [(flat[i] - key[i % len(key)]) % 29 for i in range(len(flat))]

def to_text(words, dec):
    pos = 0; result = []
    for w in words:
        dw = dec[pos:pos+len(w)]
        result.append(''.join(IDX[d] for d in dw))
        pos += len(w)
    return result

def check_singles(words, dec):
    pos = 0; result = []
    for w in words:
        if len(w) == 1:
            result.append(IDX[dec[pos]])
        pos += len(w)
    return result

# P17 with correct key (EO digraph)
flat17, words17 = load_runes('pages/page_17/runes.txt')
key_correct = [26, 24, 8, 12, 3, 13, 26, 11]  # Y-A-H-EO-O-P-Y-J
dec17 = decrypt_sub(flat17, key_correct)
text17 = to_text(words17, dec17)
singles17 = check_singles(words17, dec17)

print("P17 with corrected 8-element key (SUB):")
print(' '.join(text17))
print(f"\nSingle-rune words: {singles17}")
print(f"IoC: {ioc(dec17):.4f}")

# P28 with DEOR - test both parsings
flat28, words28 = load_runes('pages/page_28/runes.txt')

deor3 = [23, 12, 4]  # D-EO-R (digraph)
deor4 = [23, 18, 3, 4]  # D-E-O-R (no digraph)

dec28_3 = decrypt_sub(flat28, deor3)
dec28_4 = decrypt_sub(flat28, deor4)

text28_3 = to_text(words28, dec28_3)
text28_4 = to_text(words28, dec28_4)
singles28_3 = check_singles(words28, dec28_3)
singles28_4 = check_singles(words28, dec28_4)

print(f"\n\nP28 DEOR(3-elem, digraph): IoC={ioc(dec28_3):.4f}")
print(f"  Singles: {singles28_3}")
print(f"  Text: {' '.join(text28_3[:20])}")

print(f"\nP28 DEOR(4-elem, no digraph): IoC={ioc(dec28_4):.4f}")
print(f"  Singles: {singles28_4}")
print(f"  Text: {' '.join(text28_4[:20])}")

# Check if any singles are I or A
for label, singles in [("P17", singles17), ("P28(3)", singles28_3), ("P28(4)", singles28_4)]:
    ia_count = sum(1 for s in singles if s in ('I', 'A'))
    print(f"\n{label}: {ia_count}/{len(singles)} singles are I or A")
