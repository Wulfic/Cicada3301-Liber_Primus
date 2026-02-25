"""
Attack short unsolved pages: P58 (11 runes), P60 (13 runes), P02 (?).
Also try all Caesar shifts + common keyword Vigenère on these.
Brute force is feasible for very short pages.
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

def load_page(pn):
    path = f'LiberPrimus/pages/page_{pn:02d}/runes.txt'
    if not os.path.exists(path):
        return None, None
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    cipher = [GP[c] for c in raw if c in GP]
    return cipher, raw

# Known Cicada titles (likely what short pages contain)
KNOWN_TITLES = [
    "AN INSTRUCTION", "A WARNING", "A KOAN", "A PARABLE", "SOME WISDOM",
    "THE LOSS OF DIVINITY", "WELCOME", "AN END", "INTUS", "EPILOGUE",
    "AN INVITATION", "A LESSON", "THE BEGINNING", "THE END", "EMERGENCE",
    "INSTAR", "CIRCUMFERENCE", "A TEST", "THE TEST", "KNOW THIS",
    "A RIDDLE", "THE TRUTH", "SACRED", "PRIME", "SEEK", "FIND",
    "AN EXERCISE", "THE EXERCISE", "THE WAY", "THE PATH",
    "ADHERENCE", "PRESERVATION", "DECEPTION", "CONSUMPTION",
    "THE PRIMES", "HENGALLA", "SOME",
]

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

for pn in [2, 58, 60]:
    cipher, raw = load_page(pn)
    if cipher is None:
        print(f"\nP{pn:02d}: FILE NOT FOUND")
        continue
    
    N = len(cipher)
    print(f"\n{'='*80}")
    print(f"PAGE {pn:02d}: {N} runes")
    print(f"  Cipher: {cipher}")
    print(f"  LAT: {gp_to_lat(cipher)}")
    if raw:
        print(f"  Raw (first 200): {repr(raw[:200])}")
    
    # Caesar shifts
    print(f"\n  --- Caesar shifts ---")
    for shift in range(MOD):
        dec_sub = [(c - shift) % MOD for c in cipher]
        dec_add = [(c + shift) % MOD for c in cipher]
        text_sub = gp_to_lat(dec_sub)
        text_add = gp_to_lat(dec_add)
        # Check if matches any known title
        for title in KNOWN_TITLES:
            tgp = eng_to_gp(title)
            if len(tgp) <= N:
                if dec_sub[:len(tgp)] == tgp:
                    print(f"    Caesar SUB shift={shift}: '{title}' matches! Full: {text_sub}")
                if dec_add[:len(tgp)] == tgp:
                    print(f"    Caesar ADD shift={shift}: '{title}' matches! Full: {text_add}")
    
    # Vigenère with keywords
    print(f"\n  --- Vigenère keyword search ---")
    for kname, key in KEYWORDS.items():
        kl = len(key)
        for mode in ['SUB', 'ADD', 'BEAU']:
            for off in range(kl):
                dec = []
                for i in range(N):
                    kv = key[(i + off) % kl]
                    if mode == 'SUB': dec.append((cipher[i] - kv) % MOD)
                    elif mode == 'ADD': dec.append((cipher[i] + kv) % MOD)
                    else: dec.append((kv - cipher[i]) % MOD)
                text = gp_to_lat(dec)
                for title in KNOWN_TITLES:
                    tgp = eng_to_gp(title)
                    if len(tgp) <= N and dec[:len(tgp)] == tgp:
                        print(f"    {kname} {mode} off={off}: '{title}' matches! Full: {text}")
    
    # Atbash
    dec_at = [(MOD - 1 - c) % MOD for c in cipher]
    text_at = gp_to_lat(dec_at)
    print(f"\n  Atbash: {text_at}")
    
    # Reverse
    dec_rev = list(reversed(cipher))
    text_rev = gp_to_lat(dec_rev)
    print(f"  Reversed: {text_rev}")
    
    # Reverse + Caesar
    for shift in range(MOD):
        dec = [(c - shift) % MOD for c in reversed(cipher)]
        text = gp_to_lat(dec)
        for title in KNOWN_TITLES:
            tgp = eng_to_gp(title)
            if len(tgp) <= N and dec[:len(tgp)] == tgp:
                print(f"  Rev+Caesar shift={shift}: '{title}' matches! Full: {text}")

    # Direct gematria (no cipher)
    text_direct = gp_to_lat(cipher)
    print(f"  Direct: {text_direct}")
    
    # Brute force kl=1 all values
    print(f"\n  --- Brute force kl=1 ---")
    for k in range(MOD):
        dec = [(c - k) % MOD for c in cipher]
        text = gp_to_lat(dec)
        # Simple check: does it start with known English words?
        tstr = text
        good_starts = ['THE','AN','A','SOME','WELCOME','INTUS','HENGALLA']
        for gs in good_starts:
            if tstr.startswith(gs):
                print(f"    k={k} SUB: starts with '{gs}': {text}")

print("\n=== DONE ===")
