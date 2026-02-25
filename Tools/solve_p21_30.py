#!/usr/bin/env python3
"""
Comprehensive solver for Pages 21-30: Autokey, F-skip Vigenère, Progressive key.
These pages show IoC ~2.0 with standard Vigenère using P63 keywords but text remains scrambled.
"""
import sys, os, math
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}

IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,
          'Y':26,'Z':15}

# English bigram log-probabilities for scoring
COMMON_BIGRAMS = {
    'TH':6.0,'HE':5.5,'IN':4.5,'ER':4.0,'AN':4.0,'RE':3.5,'ON':3.5,'AT':3.5,
    'EN':3.5,'ND':3.0,'TI':3.0,'ES':3.0,'OR':3.0,'TE':3.0,'OF':3.0,'ED':3.0,
    'IS':3.0,'IT':3.0,'AL':2.5,'AR':2.5,'ST':2.5,'TO':2.5,'NT':2.5,'NG':2.5,
    'SE':2.5,'HA':2.5,'AS':2.5,'OU':2.5,'IO':2.5,'LE':2.5,'VE':2.5,'CO':2.5,
    'ME':2.5,'DE':2.5,'HI':2.5,'RI':2.5,'RO':2.5,'IC':2.5,'NE':2.0,'EA':2.0,
    'RA':2.0,'CE':2.0,'LI':2.0,'CH':2.0,'LL':2.0,'BE':2.0,'MA':2.0,'SI':2.0,
    'OM':2.0,'UR':2.0
}

COMMON_WORDS = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HAD','HER','WAS','ONE',
                'OUR','OUT','DAY','GET','HAS','HIM','HIS','HOW','ITS','MAY','NEW','NOW','OLD',
                'SEE','WAY','WHO','DID','LET','SAY','SHE','TOO','USE','THAT','WITH','HAVE',
                'THIS','WILL','YOUR','FROM','THEY','BEEN','HAVE','MANY','SOME','THEM','THAN',
                'EACH','MAKE','LIKE','LONG','LOOK','MANY','OVER','SUCH','TAKE','INTO','JUST',
                'KNOW','BEING','WITHIN','SACRED','WISDOM','INSTRUCTION','WELCOME','PILGRIM',
                'DIVINITY','TRUTH','PRIME','TOTIENT','CIPHER','SELF','MIND','REALITY']

def keyword_to_gp(keyword):
    result = []
    i = 0
    kw = keyword.upper()
    while i < len(kw):
        if i+1 < len(kw):
            di = kw[i:i+2]
            if di in ('TH','NG','EO','OE','EA','AE','IA'):
                digraph_map = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
                result.append(digraph_map[di])
                i += 2
                continue
        if kw[i] in ENG2GP:
            result.append(ENG2GP[kw[i]])
            i += 1
        else:
            i += 1
    return result

def load_runes(page):
    path = f'LiberPrimus/pages/page_{page:02d}/runes.txt'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [GP[c] for c in text if c in GP]

def to_runeglish(indices):
    return ''.join(IDX2LAT[i] for i in indices)

def score_text(text):
    """Score runeglish text using bigrams and word matches."""
    score = 0
    # Bigram scoring
    i = 0
    while i < len(text) - 1:
        bi = text[i:i+2]
        if bi in COMMON_BIGRAMS:
            score += COMMON_BIGRAMS[bi]
        i += 1
    
    # Word scoring
    for word in COMMON_WORDS:
        if word in text:
            score += len(word) * 3
    
    return score

def ioc(indices):
    """Index of Coincidence * 29"""
    N = len(indices)
    if N < 2: return 0
    freq = [0] * 29
    for i in indices:
        freq[i] += 1
    return 29 * sum(f*(f-1) for f in freq) / (N*(N-1))

# ===== Cipher implementations =====

def vigenere_sub(cipher, key):
    return [(cipher[i] - key[i % len(key)]) % 29 for i in range(len(cipher))]

def vigenere_add(cipher, key):
    return [(cipher[i] + key[i % len(key)]) % 29 for i in range(len(cipher))]

def vigenere_beau(cipher, key):
    return [(key[i % len(key)] - cipher[i]) % 29 for i in range(len(cipher))]

def autokey_sub(cipher, key_seed):
    """Autokey SUB: p[i] = (c[i] - k[i]) % 29, where k = seed || p[0], p[1], ..."""
    plain = []
    key_stream = list(key_seed)
    for i in range(len(cipher)):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            k = plain[i - len(key_seed)]
        p = (cipher[i] - k) % 29
        plain.append(p)
    return plain

def autokey_add(cipher, key_seed):
    """Autokey ADD: p[i] = (c[i] + k[i]) % 29"""
    plain = []
    key_stream = list(key_seed)
    for i in range(len(cipher)):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            k = plain[i - len(key_seed)]
        p = (cipher[i] + k) % 29
        plain.append(p)
    return plain

def autokey_beau(cipher, key_seed):
    """Autokey Beaufort: p[i] = (k[i] - c[i]) % 29"""
    plain = []
    key_stream = list(key_seed)
    for i in range(len(cipher)):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            k = plain[i - len(key_seed)]
        p = (k - cipher[i]) % 29
        plain.append(p)
    return plain

def autokey_cipher_key_sub(cipher, key_seed):
    """Autokey using CIPHERTEXT as key extension: p[i] = (c[i] - k[i]) % 29, k = seed || c[0], c[1], ..."""
    plain = []
    for i in range(len(cipher)):
        if i < len(key_seed):
            k = key_seed[i]
        else:
            k = cipher[i - len(key_seed)]
        p = (cipher[i] - k) % 29
        plain.append(p)
    return plain

def autokey_cipher_key_add(cipher, key_seed):
    plain = []
    for i in range(len(cipher)):
        if i < len(key_seed):
            k = key_seed[i]
        else:
            k = cipher[i - len(key_seed)]
        p = (cipher[i] + k) % 29
        plain.append(p)
    return plain

def autokey_cipher_key_beau(cipher, key_seed):
    plain = []
    for i in range(len(cipher)):
        if i < len(key_seed):
            k = key_seed[i]
        else:
            k = cipher[i - len(key_seed)]
        p = (k - cipher[i]) % 29
        plain.append(p)
    return plain

def fskip_vigenere_sub(cipher, key):
    """F-skip Vigenère SUB: if c[i]=0 and (c[i]-key[ki])%29==0, output F literally, don't advance key"""
    plain = []
    ki = 0
    for c in cipher:
        if c == 0:  # F rune
            p = (c - key[ki % len(key)]) % 29
            if p == 0:  # plaintext would be F too
                plain.append(0)
                # Don't advance key
            else:
                plain.append(p)
                ki += 1
        else:
            p = (c - key[ki % len(key)]) % 29
            plain.append(p)
            ki += 1
    return plain

def fskip_vigenere_beau(cipher, key):
    """F-skip Vigenère Beaufort"""
    plain = []
    ki = 0
    for c in cipher:
        if c == 0:
            p = (key[ki % len(key)] - c) % 29
            if p == 0:
                plain.append(0)
            else:
                plain.append(p)
                ki += 1
        else:
            p = (key[ki % len(key)] - c) % 29
            plain.append(p)
            ki += 1
    return plain

def fskip_vigenere_add(cipher, key):
    """F-skip Vigenère ADD"""
    plain = []
    ki = 0
    for c in cipher:
        if c == 0:
            p = (c + key[ki % len(key)]) % 29
            if p == 0:
                plain.append(0)
            else:
                plain.append(p)
                ki += 1
        else:
            p = (c + key[ki % len(key)]) % 29
            plain.append(p)
            ki += 1
    return plain

def progressive_vigenere_sub(cipher, key, step=1):
    """Progressive Vigenère: key shifts by 'step' each full repeat"""
    plain = []
    for i in range(len(cipher)):
        repeat = i // len(key)
        k = (key[i % len(key)] + repeat * step) % 29
        plain.append((cipher[i] - k) % 29)
    return plain

def progressive_vigenere_beau(cipher, key, step=1):
    plain = []
    for i in range(len(cipher)):
        repeat = i // len(key)
        k = (key[i % len(key)] + repeat * step) % 29
        plain.append((k - cipher[i]) % 29)
    return plain

# ===== Page data =====
PAGE_KEYS = {
    21: ('CABAL', 'beau'),
    22: ('DIVINITY', 'beau'),
    23: ('ENCRYPTION', 'add'),
    24: ('OBSCURA', 'beau'),
    # 25: CORRUPTED DATA - skip
    26: ('ENCRYPT', 'add'),
    27: ('SHADOWS', 'add'),
    28: ('DEOR', 'sub'),
    29: ('TOTIENT', 'beau'),
    30: ('MOURNFUL', 'add'),
}

ALL_KEYWORDS = ['CABAL', 'DIVINITY', 'ENCRYPTION', 'OBSCURA', 'ENCRYPT', 'SHADOWS',
                'DEOR', 'TOTIENT', 'MOURNFUL', 'PILGRIM', 'WISDOM', 'SACRED',
                'CONSUMPTION', 'PRESERVATION', 'ADHERENCE', 'CIRCUMFERENCE',
                'FIRFUMFERENFE', 'MOBIUS', 'VOID', 'PRIMUS', 'LIBER', 'KOAN']

# ===== Main solver =====
print("=" * 70)
print("PAGES 21-30 COMPREHENSIVE SOLVER")
print("=" * 70)

best_results = []

for page in [21, 22, 23, 24, 26, 27, 28, 29, 30]:  # Skip 25 (corrupted)
    cipher = load_runes(page)
    suggested_kw, suggested_mode = PAGE_KEYS[page]
    
    print(f"\n{'='*60}")
    print(f"PAGE {page} ({len(cipher)} runes) - Suggested: {suggested_kw} {suggested_mode}")
    print(f"{'='*60}")
    
    page_best_score = 0
    page_best_desc = ""
    page_best_text = ""
    
    for kw_name in ALL_KEYWORDS:
        key = keyword_to_gp(kw_name)
        if not key:
            continue
        
        # Test all cipher variants
        variants = {}
        
        # Standard Vigenère (baseline)
        variants[f'{kw_name}_vig_sub'] = vigenere_sub(cipher, key)
        variants[f'{kw_name}_vig_add'] = vigenere_add(cipher, key) 
        variants[f'{kw_name}_vig_beau'] = vigenere_beau(cipher, key)
        
        # Autokey (plaintext-extended)
        variants[f'{kw_name}_ak_sub'] = autokey_sub(cipher, key)
        variants[f'{kw_name}_ak_add'] = autokey_add(cipher, key)
        variants[f'{kw_name}_ak_beau'] = autokey_beau(cipher, key)
        
        # Autokey (ciphertext-extended)
        variants[f'{kw_name}_akc_sub'] = autokey_cipher_key_sub(cipher, key)
        variants[f'{kw_name}_akc_add'] = autokey_cipher_key_add(cipher, key)
        variants[f'{kw_name}_akc_beau'] = autokey_cipher_key_beau(cipher, key)
        
        # F-skip Vigenère
        variants[f'{kw_name}_fskip_sub'] = fskip_vigenere_sub(cipher, key)
        variants[f'{kw_name}_fskip_add'] = fskip_vigenere_add(cipher, key)
        variants[f'{kw_name}_fskip_beau'] = fskip_vigenere_beau(cipher, key)
        
        # Progressive Vigenère (steps 1-5)
        for step in range(1, 6):
            variants[f'{kw_name}_prog{step}_sub'] = progressive_vigenere_sub(cipher, key, step)
            variants[f'{kw_name}_prog{step}_beau'] = progressive_vigenere_beau(cipher, key, step)
        
        for desc, plain in variants.items():
            text = to_runeglish(plain)
            sc = score_text(text)
            ic = ioc(plain)
            
            if sc > page_best_score:
                page_best_score = sc
                page_best_desc = desc
                page_best_text = text
            
            # Report high-scoring results
            if sc > 150:
                print(f"  {desc}: score={sc:.0f} IoC={ic:.3f}")
                print(f"    {text[:80]}")
    
    # Also try with key offsets 1-28
    key = keyword_to_gp(suggested_kw)
    for offset in range(1, 29):
        shifted_key = [(k + offset) % 29 for k in key]
        for mode_name, func in [('sub', vigenere_sub), ('add', vigenere_add), ('beau', vigenere_beau)]:
            plain = func(cipher, shifted_key)
            text = to_runeglish(plain)
            sc = score_text(text)
            if sc > page_best_score:
                page_best_score = sc
                page_best_desc = f'{suggested_kw}_off{offset}_{mode_name}'
                page_best_text = text
        
        # Autokey with offset
        for mode_name, func in [('ak_sub', autokey_sub), ('ak_add', autokey_add), ('ak_beau', autokey_beau)]:
            plain = func(cipher, shifted_key)
            text = to_runeglish(plain)
            sc = score_text(text)
            if sc > page_best_score:
                page_best_score = sc
                page_best_desc = f'{suggested_kw}_off{offset}_{mode_name}'
                page_best_text = text
    
    print(f"\n  BEST P{page}: {page_best_desc} score={page_best_score:.0f}")
    print(f"    {page_best_text[:100]}")
    best_results.append((page, page_best_score, page_best_desc, page_best_text[:100]))

print("\n" + "=" * 70)
print("SUMMARY OF BEST RESULTS")
print("=" * 70)
for page, score, desc, text in best_results:
    print(f"P{page:02d}: score={score:>7.0f} | {desc}")
    print(f"      {text}")
