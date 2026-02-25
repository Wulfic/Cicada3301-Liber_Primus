"""
COMPREHENSIVE ATTACK with CORRECT GP mapping.
1. Loads rune files correctly (skipping note lines)
2. Uses verified RUNE_TO_INDEX mapping
3. Tests all known cipher methods on all pages
4. Validates against known solutions first
"""
import os, sys, math
from collections import Counter

# ===== CORRECT GP MAP =====
RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
              'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def load_page(pn):
    """Load page runes, skipping note/comment lines"""
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Skip lines that start with ASCII text (notes/comments)
    rune_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        # If line starts with ASCII letter, it's a comment
        if stripped and stripped[0].isascii() and stripped[0].isalpha():
            continue
        rune_lines.append(stripped)
    text = '\n'.join(rune_lines)
    return [RUNE_TO_INDEX[c] for c in text if c in RUNE_TO_INDEX]

def keyword_to_gp(word):
    result = []; i = 0; word = word.upper()
    while i < len(word):
        if i+1 < len(word):
            di = word[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap:
                result.append(dmap[di]); i += 2; continue
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if word[i] in smap: result.append(smap[word[i]])
        i += 1
    return result

def ioc29(vals):
    if len(vals) < 2: return 0
    ct = Counter(vals); n = len(vals)
    return 29 * sum(c*(c-1) for c in ct.values()) / (n*(n-1))

def vals_to_text(vals):
    return ''.join(GP_LETTERS[v] for v in vals)

def vigenere(cipher, key, mode='SUB'):
    result = []; kl = len(key)
    for i, c in enumerate(cipher):
        k = key[i % kl]
        if mode == 'SUB': result.append((c - k) % 29)
        elif mode == 'ADD': result.append((c + k) % 29)
        elif mode == 'BEAU': result.append((k - c) % 29)
    return result

def totient_decrypt(cipher, offset=0, mode='SUB'):
    """Totient cipher: key[i] = phi(prime[i+offset]) % 29"""
    result = []
    for i, c in enumerate(cipher):
        p = prime_at(i + offset)
        k = (p - 1) % 29  # phi(p) = p-1 for prime p
        if mode == 'SUB': result.append((c - k) % 29)
        elif mode == 'ADD': result.append((c + k) % 29)
    return result

# Simple prime generator
_primes_cache = []
def prime_at(n):
    """Get the nth prime (0-indexed: prime_at(0)=2)"""
    while len(_primes_cache) <= n:
        if not _primes_cache:
            _primes_cache.append(2)
        else:
            candidate = _primes_cache[-1] + 1
            while True:
                is_prime = True
                for p in _primes_cache:
                    if p*p > candidate: break
                    if candidate % p == 0:
                        is_prime = False; break
                if is_prime:
                    _primes_cache.append(candidate); break
                candidate += 1
    return _primes_cache[n]

# Pre-generate enough primes
for i in range(5000): prime_at(i)

def score_english(vals):
    """Quick English score based on common bigrams"""
    if len(vals) < 10: return 0
    text = vals_to_text(vals).upper()
    # Common English bigrams in GP
    score = 0
    common_bi = ['TH','HE','IN','EN','NT','RE','ER','AN','TI','ON','AT','ES','ST',
                 'AR','ND','TO','IS','IT','HA','OF','OR','OU','NO','SE','ED']
    for i in range(len(text)-1):
        bi = text[i:i+2]
        if bi in common_bi:
            score += 1
    return score / (len(text) - 1) if len(text) > 1 else 0

# ===== PHASE 1: VALIDATE KNOWN SOLUTIONS =====
print("=" * 80)
print("PHASE 1: VALIDATE KNOWN SOLUTIONS (correct GP mapping)")
print("=" * 80)

validations = [
    (3, 'DIVINITY', 'SUB', "WELCOME"),
    (4, 'DIVINITY', 'SUB', "IT IS THROUGH"),
    (14, 'FIRFUMFERENFE', 'SUB', None),
    (15, 'FIRFUMFERENFE', 'SUB', None),
]

divinity = keyword_to_gp('DIVINITY')
firfum = keyword_to_gp('FIRFUMFERENFE')

for pn, kw_name, mode, expected in validations:
    cipher = load_page(pn)
    if not cipher: print(f"  P{pn:02d}: NO DATA"); continue
    key = keyword_to_gp(kw_name)
    dec = vigenere(cipher, key, mode)
    ic = ioc29(dec)
    text = vals_to_text(dec)[:80]
    status = "OK" if ic > 1.5 else "FAIL"
    print(f"  P{pn:02d} ({len(cipher)} runes): {kw_name} {mode} IoC={ic:.4f} [{status}]")
    print(f"    {text}")

# Test P03 with continuation to P04
p03 = load_page(3)
p04 = load_page(4)
if p03 and p04:
    combined = p03 + p04
    dec = vigenere(combined, divinity, 'SUB')
    ic = ioc29(dec)
    text = vals_to_text(dec)
    print(f"\n  P03+P04 combined ({len(combined)} runes): IoC={ic:.4f}")
    print(f"    {text[:100]}")
    print(f"    ...{text[-60:]}")

# Test totient on P55
p55 = load_page(55)
if p55:
    for off in range(100):
        dec = totient_decrypt(p55, off, 'SUB')
        ic = ioc29(dec)
        if ic > 1.4:
            text = vals_to_text(dec)[:60]
            print(f"  P55 totient off={off}: IoC={ic:.4f} -> {text}")

# ===== PHASE 2: COMPREHENSIVE SCAN ALL PAGES 18-54 =====
print("\n" + "=" * 80)
print("PHASE 2: COMPREHENSIVE SCAN - Pages 18-54")
print("=" * 80)

KEYWORDS = ['DIVINITY','FIRFUMFERENFE','CABAL','SHADOWS','AETHEREAL','OBSCURA',
            'MOURNFUL','VOID','CARNAL','MOBIUS','ANALOG','BUFFERS','FORM','DEOR',
            'TOTIENT','ENCRYPT','YAHEOOPYJ','CIRCUMFERENCE','CONSUMPTION',
            'PRESERVATION','ADHERENCE','WISDOM','INSTRUCTION','PILGRIMAGE',
            'INSTAR','WELCOME','WARNING','SACRED','PRIMES','KOAN','MASTER']

for pn in range(18, 55):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 10: continue
    raw_ioc = ioc29(cipher)
    
    best = (0, '', '', 0, [])
    
    # Test 1: All keywords x modes
    for kw_name in KEYWORDS:
        key = keyword_to_gp(kw_name)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            dec = vigenere(cipher, key, mode)
            ic = ioc29(dec)
            if ic > best[0]:
                best = (ic, kw_name, mode, 0, dec)
    
    # Test 2: Caesar shifts 0-28
    for shift in range(29):
        dec = [(c + shift) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best[0]:
            best = (ic, f'CAESAR_{shift}', 'SHIFT', 0, dec)
    
    # Test 3: Reversed gematria
    for shift in range(29):
        dec = [(28 - c + shift) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best[0]:
            best = (ic, f'REV_{shift}', 'REV', 0, dec)
    
    # Test 4: Totient cipher (sample offsets)
    for off in [0, 1, 5, 10, 50, 100, 200, 500, 1000, 2000]:
        for mode in ['SUB', 'ADD']:
            dec = totient_decrypt(cipher, off, mode)
            ic = ioc29(dec)
            if ic > best[0]:
                best = (ic, f'TOTIENT_off{off}', mode, 0, dec)
    
    ic, method, mode, _, dec = best
    text = vals_to_text(dec)[:60]
    marker = " *** ENGLISH! ***" if ic > 1.6 else " ** signal **" if ic > 1.4 else ""
    if ic > 1.3 or pn in [18,19,20,32,44,50]:
        print(f"  P{pn:02d} ({len(cipher):4d}): raw={raw_ioc:.3f} best={ic:.4f} {method} {mode}{marker}")
        print(f"    {text}")

# ===== PHASE 3: DEEP SCAN ON HIGH-POTENTIAL PAGES =====
print("\n" + "=" * 80)
print("PHASE 3: DEEP KEYWORD SCAN with all offsets (Pages 21-30)")
print("=" * 80)

for pn in range(21, 31):
    cipher = load_page(pn)
    if not cipher: continue
    raw_ioc = ioc29(cipher)
    print(f"\n--- Page {pn}: {len(cipher)} runes, raw IoC={raw_ioc:.4f} ---")
    
    hits = []
    for kw_name in KEYWORDS:
        key = keyword_to_gp(kw_name)
        if not key: continue
        for mode in ['SUB', 'ADD', 'BEAU']:
            for off in range(len(key)):
                shifted = key[off:] + key[:off]
                dec = vigenere(cipher, shifted, mode)
                ic = ioc29(dec)
                if ic > 1.3:
                    hits.append((ic, kw_name, mode, off, dec))
    
    hits.sort(reverse=True)
    if hits:
        for ic, kw, mode, off, dec in hits[:3]:
            text = vals_to_text(dec)[:60]
            marker = " *** ENGLISH ***" if ic > 1.6 else ""
            print(f"  {kw} {mode} off={off}: IoC={ic:.4f}{marker}")
            print(f"    {text}")
    else:
        print(f"  No keyword produces IoC > 1.3")

# ===== PHASE 4: PAGES 55-74 VALIDATION =====
print("\n" + "=" * 80)
print("PHASE 4: VALIDATE PAGES 55-74 (should be solved)")
print("=" * 80)

for pn in range(55, 75):
    cipher = load_page(pn)
    if not cipher or len(cipher) < 5: continue
    raw_ioc = ioc29(cipher)
    
    # Direct gematria (Caesar 0)
    text_direct = vals_to_text(cipher)[:60]
    
    # Best Caesar
    best_caesar = (0, 0)
    for s in range(29):
        dec = [(c + s) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best_caesar[0]:
            best_caesar = (ic, s)
    
    # Best reversed
    best_rev = (0, 0)
    for s in range(29):
        dec = [(28 - c + s) % 29 for c in cipher]
        ic = ioc29(dec)
        if ic > best_rev[0]:
            best_rev = (ic, s)
    
    # Totient
    best_tot = (0, 0)
    for off in range(200):
        dec = totient_decrypt(cipher, off, 'SUB')
        ic = ioc29(dec)
        if ic > best_tot[0]:
            best_tot = (ic, off)
    
    # DIVINITY
    dec_div = vigenere(cipher, divinity, 'SUB')
    ic_div = ioc29(dec_div)
    
    winner = max([
        (raw_ioc, f'direct'),
        (best_caesar[0], f'caesar_{best_caesar[1]}'),
        (best_rev[0], f'rev_{best_rev[1]}'),
        (best_tot[0], f'totient_{best_tot[1]}'),
        (ic_div, 'DIVINITY_SUB'),
    ])
    
    ic, method = winner
    marker = " SOLVED" if ic > 1.5 else ""
    print(f"  P{pn:02d} ({len(cipher):3d}): raw={raw_ioc:.3f} best={ic:.4f} [{method}]{marker}")
    if ic > 1.5:
        if 'direct' in method:
            print(f"    {text_direct}")
        elif 'DIVINITY' in method:
            print(f"    {vals_to_text(dec_div)[:60]}")
        elif 'totient' in method:
            off = int(method.split('_')[1])
            dec = totient_decrypt(cipher, off, 'SUB')
            print(f"    {vals_to_text(dec)[:60]}")
        elif 'caesar' in method:
            s = int(method.split('_')[1])
            dec = [(c + s) % 29 for c in cipher]
            print(f"    {vals_to_text(dec)[:60]}")
        elif 'rev' in method:
            s = int(method.split('_')[1])
            dec = [(28 - c + s) % 29 for c in cipher]
            print(f"    {vals_to_text(dec)[:60]}")
