"""
Check if P03 and P04 use F-skip with DIVINITY.
Also run deeper F-skip analysis on all remaining unsolved pages with 
ALL keywords (not just DIVINITY), exhaustive where possible.
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

def score_text(text):
    s = 0
    for w in ['WISDOM','THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS',
              'WHICH','ARE','WITHIN','HOLY','LIVES','EACH','BEING','UNTO',
              'YOURSELF','INTELLIGENCE','INSTRUCTION','COMMAND','YOUR','OWN',
              'SELF','LAW','SACRED','DIVINITY','PILGRIM','TRUTH','BELIEVE',
              'NOTHING','FIND','SEEK','WEB','DEEP','HASHES','EXISTS','END',
              'PAGE','DUTY','EVERY','PRESERVE','WEAK','CONSUME','ENOUGH',
              'FOLLOW','DOGMA','BELONG','CIRCUMFERENCE','LOSS','KOAN','MASTER',
              'WHAT','HAVE','KNOW','TRUE','FROM','THEY','WILL','THEIR','HAS',
              'WELCOME','STUDY','HERE','ASKED','STUDENT','NAME','CALLED',
              'DOOR','WENT','DECIDED','MAN','CAME','SAID','TOLD','GIVE',
              'VOICE','LESSON','DURING','JUST','WARNING','EXCEPT','BOOK',
              'PRACTICE','THREE','BEHAVIORS','CAUSE','CONSUMPTION','WE',
              'BECAUSE','TOO','MUCH','MOST','THINGS','WORTH','PRESERVING',
              'TOTIENT','ENCRYPTED','SHOULD','PARABLE','LIKE','INSTAR',
              'TUNNELING','SURFACE','MUST','SHED','EMERGE','OUR','SOME',
              'TEST','YOUR','QUESTION','DO','FOUR','UNREASONABLE','DAY',
              'STRUGGLE','SUFFERING','INNOCENCE','ILLUSIONS','CERTAINTY',
              'REALITY','ULTIMATELY','DISCOVER','PILGRIMAGE','SHAPE',
              'OURSELVES','REALITIES','JOURNEY','ARRIVE','OUTSIDE','GOING',
              'NECESSARY','ALONG','WAY','TRIP','EASY']:
        c = text.count(w)
        s += c * len(w)
    return s

DIVINITY = eng_to_gp("DIVINITY")

def load_page(pn):
    path = f'LiberPrimus/pages/page_{pn:02d}/runes.txt'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    return [GP[c] for c in raw if c in GP]

# ===== CHECK P03 and P04 =====
print("="*80)
print("CHECKING P03 AND P04 (already solved with DIVINITY)")
print("="*80)

for pn in [3, 4]:
    cipher = load_page(pn)
    if cipher is None:
        print(f"  P{pn:02d}: runes not found")
        continue
    N = len(cipher)
    f_pos = [i for i in range(N) if cipher[i] == 0]
    print(f"\n  P{pn:02d}: {N} runes, {len(f_pos)} F runes")
    
    # Standard Vigenère
    for off in range(8):
        dec = [(cipher[i] - DIVINITY[(i+off)%8]) % MOD for i in range(N)]
        text = gp_to_lat(dec)
        sc = score_text(text)
        if sc > 20:
            print(f"    Standard SUB off={off}: score={sc:3d} | {text[:80]}")
    
    # All-F-literal
    for off in range(8):
        dec = []; k = off
        for i in range(N):
            if cipher[i] == 0:
                dec.append(0)
            else:
                dec.append((cipher[i] - DIVINITY[k%8]) % MOD)
                k += 1
        text = gp_to_lat(dec)
        sc = score_text(text)
        if sc > 20:
            print(f"    F-skip SUB off={off}: score={sc:3d} | {text[:80]}")

# ===== Now check a broader set of unsolved pages =====
print("\n" + "="*80)
print("CHECKING ALL REMAINING UNSOLVED PAGES (18-54, 58, 60)")
print("="*80)

# Load all known keywords
KEYWORDS = {
    'DIVINITY': eng_to_gp('DIVINITY'),
    'FIRFUMFERENFE': eng_to_gp('FIRFUMFERENFE'),
    'CIRCUMFERENCE': eng_to_gp('CIRCUMFERENCE'),
    'YAHEOOPYJ': [26,24,8,18,3,3,13,26,11],
    'SACRED': eng_to_gp('SACRED'),
    'PILGRIM': eng_to_gp('PILGRIM'),
    'WISDOM': eng_to_gp('WISDOM'),
    'TRUTH': eng_to_gp('TRUTH'),
    'INSTAR': eng_to_gp('INSTAR'),
    'INTUS': eng_to_gp('INTUS'),
    'LIBER': eng_to_gp('LIBER'),
    'CABAL': eng_to_gp('CABAL'),
    'MOBIUS': eng_to_gp('MOBIUS'),
    'SHADOW': eng_to_gp('SHADOW'),
    'VOID': eng_to_gp('VOID'),
    'AETHEREAL': eng_to_gp('AETHEREAL'),
    'EMERGENCE': eng_to_gp('EMERGENCE'),
    'CONSUMPTION': eng_to_gp('CONSUMPTION'),
    'DECEPTION': eng_to_gp('DECEPTION'),
    'PRESERVATION': eng_to_gp('PRESERVATION'),
    'KOAN': eng_to_gp('KOAN'),
    'WELCOME': eng_to_gp('WELCOME'),
}

# Pages to test thoroughly
pages_to_test = list(range(18, 55)) + [58, 60]
# Skip already solved: 55-74 range

for pn in pages_to_test:
    cipher = load_page(pn)
    if cipher is None or len(cipher) < 10:
        continue
    N = len(cipher)
    f_pos = [i for i in range(N) if cipher[i] == 0]
    n_f = len(f_pos)
    
    # Only do exhaustive if n_f <= 14 (keep manageable)
    if n_f > 14 or n_f == 0:
        continue  # Skip pages with too many F's for exhaustive search
    
    best_page = []
    
    for kname, key in KEYWORDS.items():
        kl = len(key)
        
        # Exhaustive F-skip
        for f_mask in range(2**n_f):
            lit_set = set()
            for bit in range(n_f):
                if f_mask & (1 << bit):
                    lit_set.add(f_pos[bit])
            
            for off in range(kl):
                for mode in ['SUB']:  # SUB only for speed
                    dec = []
                    k = off
                    for i in range(N):
                        if i in lit_set:
                            dec.append(0)
                        else:
                            kv = key[k % kl]
                            dec.append((cipher[i] - kv) % MOD)
                            k += 1
                    text = gp_to_lat(dec)
                    sc = score_text(text)
                    if sc >= 80:
                        mask_str = format(f_mask, f'0{n_f}b')
                        best_page.append((sc, kname, off, mask_str, text[:100]))
    
    if best_page:
        best_page.sort(reverse=True)
        print(f"\n  P{pn:02d} ({N} runes, {n_f} F): Top 3:")
        for sc, kn, off, mask, text in best_page[:3]:
            print(f"    score={sc:4d} {kn:15s} off={off} mask={mask}: {text}")

print("\n=== DONE ===")
