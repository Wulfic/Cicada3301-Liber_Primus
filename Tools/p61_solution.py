"""
P61 — Extract FULL solution text from best F-skip result.
Best: SUB off=0, mask=0010011001111000, score=298
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

with open('LiberPrimus/pages/page_61/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
f_pos = [i for i in range(N) if cipher[i] == 0]

DIVINITY = eng_to_gp("DIVINITY")
KL = len(DIVINITY)

# Best mask from exhaustive search
best_mask = 0b0010011001111000
lit_set = set()
for bit in range(len(f_pos)):
    if best_mask & (1 << bit):
        lit_set.add(f_pos[bit])

print(f"Literal F positions: {sorted(lit_set)}")
print(f"Encrypted F positions: {[p for p in f_pos if p not in lit_set]}")

# Decrypt
dec = []
k = 0  # offset = 0
for i in range(N):
    if i in lit_set:
        dec.append(0)  # literal F
    else:
        kv = DIVINITY[k % KL]
        dec.append((cipher[i] - kv) % MOD)
        k += 1

text = gp_to_lat(dec)
print(f"\nFULL DECRYPTED TEXT ({N} runes = {len(text)} chars in LAT):")
print(text)
print()

# Manual word segmentation
WORD_LIST = sorted(['WELCOME','PILGRIM','TO','THE','GREAT','JOURNEY','TOWARD',
    'END','OF','ALL','THINGS','IT','IS','NOT','AN','EASY','TRIP','BUT','FOR',
    'THOSE','WHO','FIND','THEIR','WAY','HERE','A','NECESSARY','AND','SACRED',
    'WHAT','YOU','WILL','HAVE','THAT','LIVES','HOLY','EACH','BEING','UNTO',
    'YOURSELF','INTELLIGENCE','INSTRUCTION','COMMAND','YOUR','OWN','SELF','LAW',
    'WISDOM','DIVINITY','TRUTH','BELIEVE','NOTHING','SEEK','WEB','DEEP','WITHIN',
    'HASHES','EXISTS','PAGE','DUTY','EVERY','PRESERVE','WEAK','CONSUME','ENOUGH',
    'FOLLOW','DOGMA','BELONG','CIRCUMFERENCE','LOSS','KOAN','MASTER',
    'KNOW','TRUE','FROM','THEY','HAS','BEEN','HIM','THEN','ONLY','ALSO','WOULD',
    'LESSON','DURING','JUST','WARNING','EXCEPT','BOOK','PRACTICE','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','WE','BECAUSE','TOO','MUCH','MOST',
    'WORTH','PRESERVING','STRONG','LATER','OBTAIN','NEED','LUCK','NOW','PRIMES',
    'TOTIENT','ENCRYPTED','SHOULD','PARABLE','LIKE','INSTAR','TUNNELING',
    'SURFACE','MUST','SHED','EMERGE','OUR','SOME','TEST','QUESTION','DO',
    'FOUR','UNREASONABLE','DAY','WAS','WHOSE','TEACHER','HIS','HER','HOW','WHEN',
    'THERE','THEM','AFTER','BEFORE','INTO','OVER','COULD','MAY','VERY','THESE',
    'OTHER','ABOUT','MORE','MAKE','FIRST','SUCH','UP','OUT','LONG','MANY',
    'PEOPLE','WORK','PART','TAKE','COME','BECOME','ACT','TWO','SAME','STILL',
    'BACK','GOOD','LITTLE','UNDER','WORLD','POWER','THING','PLACE','HAND',
    'HIGH','KEEP','LAST','LET','THOUGHT','POINT','WORD','GOING','WHERE','LEAVE',
    'TELL','CALL','STATE','THROUGH','THIS','WHICH','WITH','ARE','IN','ON','AT',
    'SO','HE','SHE','NO','AS','BE','GIVEN','IF','OR','BY','MY','THOUGH','CAME',
    'SAID','TOLD','GIVE','VOICE','MAN','NAME','CALLED','DOOR','WENT','DECIDED',
    'STUDENT','ASKED','STUDY','ONCE','COMPLETE','DARKNESS','AGAIN','FOUND',
    'HAD','NIGHT','LIGHT','DEATH','LIFE','BORN','MADE','KNEW','HEAR','SEE',
    'FEEL','TOUCH','ONE','KNOWN','THINK','UNDERSTOOD','BEGAN','GO','WALK',
    'AMONG','FIRST','LAST','START','RETURN','LOOK','OPEN','CLOSE','SPOKE',
    'ANSWERED','REPLIED','CONTINUED','ASKED','STEPPED','AWAY','FORWARD',
    'FOLLOWED','SEARCHING','UPON','DOWN','ABOVE','BELOW','BETWEEN','AROUND',
    'INSIDE','OUTSIDE','DARK','BRIGHT','OLD','NEW','YOUNG','ANCIENT','MODERN',
    'SPIRITUAL','PHYSICAL','MENTAL','BEYOND','ANOTHER','DIFFERENT','ENOUGH',
    'NEVER','ALWAYS','OFTEN','SOMETIMES','PERHAPS','MAYBE','RATHER','TOGETHER'], 
    key=lambda w: -len(w))

pos = 0; words = []; unk_buf = ''
while pos < len(text):
    found = False
    for w in WORD_LIST:
        wlen = len(w)
        if text[pos:pos+wlen] == w:
            if unk_buf:
                words.append(f'[{unk_buf}]')
                unk_buf = ''
            words.append(w)
            pos += wlen
            found = True
            break
    if not found:
        unk_buf += text[pos]
        pos += 1
if unk_buf:
    words.append(f'[{unk_buf}]')

print("WORD SEGMENTED:")
print(' '.join(words))

# Also try top 3 masks to see which gives best full text
print("\n\n===== COMPARING TOP MASKS =====")
top_masks = [
    (0b0010011001111000, "0010011001111000"),
    (0b0010011001110100, "0010011001110100"),
    (0b0010010101111000, "0010010101111000"),
]

for mask_val, mask_str in top_masks:
    lit = set()
    for bit in range(len(f_pos)):
        if mask_val & (1 << bit):
            lit.add(f_pos[bit])
    
    dec2 = []
    k = 0
    for i in range(N):
        if i in lit:
            dec2.append(0)
        else:
            kv = DIVINITY[k % KL]
            dec2.append((cipher[i] - kv) % MOD)
            k += 1
    text2 = gp_to_lat(dec2)
    # Find differences with best
    if mask_str != "0010011001111000":
        diffs = [(i, text[i] if i<len(text) else '?', text2[i] if i<len(text2) else '?') 
                 for i in range(max(len(text),len(text2))) if (i<len(text) and i<len(text2) and text[i]!=text2[i]) or (i>=len(text)) or (i>=len(text2))]
        print(f"\n  Mask {mask_str}: {len(diffs)} char diffs")
        for p, c1, c2 in diffs[:10]:
            print(f"    pos {p}: '{c1}' vs '{c2}'")

print("\n=== DONE ===")
