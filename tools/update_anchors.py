import json
from pathlib import Path

IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
LP_MAP = {'F':0,'U':1,'TH':2,'O':3,'R':4,'C':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,'EO':12,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,'NG':21,'OE':22,'D':23,'A':24,'AE':25,'Y':26,'IO':27,'EA':28,'V':1,'Q':5,'K':5,'Z':14}

def encode(phrase):
    runes = []; i = 0; w = phrase.upper().replace(' ', '')
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LP_MAP:
            runes.append(LP_MAP[w[i:i+2]]); i += 2
        elif w[i] in LP_MAP:
            runes.append(LP_MAP[w[i]]); i += 1
        else:
            i += 1
    return runes

a = json.loads(Path('data/key_anchors.json').read_text())
before = len(a['anchors'])
print('Before:', before, 'anchors')

phrase = 'THELOSSOFDIUINITY'
enc = encode(phrase)
print('Adding', len(enc), 'positions for', phrase, 'at 4325')
print('Encoded:', [IDX_TO[v] for v in enc])

added = 0
for i, v in enumerate(enc):
    pos_str = str(4325 + i)
    if pos_str not in a['anchors']:
        a['anchors'][pos_str] = v
        added += 1
    else:
        existing = a['anchors'][pos_str]
        if existing != v:
            print('CONFLICT at pos', pos_str, ': existing=', IDX_TO[existing], ', new=', IDX_TO[v])

print('Added', added, 'new anchor positions')
print('After:', len(a['anchors']), 'anchors')
Path('data/key_anchors.json').write_text(json.dumps(a, indent=2))
print('Saved key_anchors.json')
