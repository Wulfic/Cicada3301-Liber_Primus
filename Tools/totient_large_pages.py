#!/usr/bin/env python3
"""
Totient (phi(prime)) cipher attack on large unsolved pages P32, P44, P50.

Tests:
1. Pure totient cipher with prime offset scan (0 to MAX_OFFSET)
2. Caesar + totient (applying known Caesar shifts first)
3. All 3 modes (SUB, ADD, BEAU) 
4. With and without F-skip
5. Using first WINDOW runes for fast screening, full text for verification
"""

import sys, os, math, re
from pathlib import Path

# GP mapping
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29

# English scoring
COMMON_WORDS = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE','OUR',
    'OUT','HAS','HIS','HOW','ITS','HAD','WHO','OIL','SIT','NOW','OLD','NEW','WAY','MAY','DAY',
    'TOO','USE','MAN','HIM','DID','GET','HAS','HIM','HIS','HOW','ITS','LET','SAY','SHE','END',
    'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','CALL','EACH','MAKE',
    'LIKE','LONG','LOOK','MANY','COME','MORE','OVER','SUCH','TAKE','THAN','THEM','THEN',
    'WHAT','WHEN','INTO','TIME','VERY','JUST','KNOW','SOME','BACK','ONLY','YEAR','MOST',
    'GOOD','GIVE','ALSO','MOST','FIND','HERE','SELF','HOLY','DEEP','WITHIN','BEING','SACRED',
    'THERE','THEIR','WHICH','WOULD','ABOUT','OTHER','THESE','AFTER','FIRST','COULD',
    'THOSE','SHALL','WORLD','STILL','FOUND','GREAT','EVERY','NEVER','WHERE','MIGHT',
    'WHILE','SHOULD','THROUGH','PILGRIM','WELCOME','WISDOM','INSTRUCTION','COMMAND',
    'JOURNEY','TRUTH','DIVINE','DIVINITY','EMERGE','INSTAR','INTELLIGENCE','INNOCENCE',
    'ILLUSION','CERTAINTY','REALITY','STRUGGLE','SUFFERING','NECESSARY','ULTIMATELY',
    'DISCOVER','PILGRIMAGE','SHAPE','ARRIVE','OUTSIDE','GOING','VOID','SHADOW','CABAL',
    'PRIMUS','LIBER','CIRCUMFERENCE','PRESERVATION','MOBIUS','CONSUMPTION','EMERGENCE',
    'AETHEREAL','CARNAL','ANALOG','CICADA','SECRET','KNOWLEDGE','POWER','LIGHT','DARK',
    'FIRE','WATER','EARTH','SPIRIT','MIND','BODY','SOUL','DEATH','LIFE','NATURE','REASON',
    'ORDER','CHAOS'}

# Common English bigrams for scoring
GOOD_BIGRAMS = {'TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','TI','ES','OR','TE','OF',
    'ED','IS','IT','AL','AR','ST','TO','NT','NG','SE','HA','AS','OU','IO','LE','VE','CO',
    'ME','DE','HI','RI','RO','IC','NE','EA','RA','CE','LI','CH','LL','BE','MA','SI','OM',
    'UR'}

def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

def load_runes(page_num):
    """Load rune indices from page file."""
    base = Path(r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages")
    rune_file = base / f"page_{page_num:02d}" / "runes.txt"
    if not rune_file.exists():
        rune_file = base / f"page_{page_num}" / "runes.txt"
    if not rune_file.exists():
        print(f"  [!] runes.txt not found for page {page_num}")
        return []
    
    text = rune_file.read_text(encoding='utf-8')
    indices = []
    for ch in text:
        if ch in GP:
            indices.append(GP[ch])
    return indices

def to_latin(indices):
    """Convert GP indices to Latin approximation."""
    return ''.join(IDX2LAT[i] for i in indices)

def score_text(latin):
    """Score Latin text for English-likeness."""
    s = 0
    # Bigram scoring
    for i in range(len(latin)-1):
        bg = latin[i:i+2]
        if bg in GOOD_BIGRAMS:
            s += 2
    # Word scoring (check 3-12 letter windows)
    upper = latin.upper()
    for wlen in range(3, min(13, len(upper)+1)):
        for i in range(len(upper) - wlen + 1):
            w = upper[i:i+wlen]
            if w in COMMON_WORDS:
                s += wlen * 2
    return s

def totient_decrypt(cipher, primes, offset, mode='sub', f_skip=True, caesar_shift=0):
    """
    Decrypt using totient cipher.
    plaintext[i] = mode(cipher[i] - caesar_shift, (prime[key_idx]-1)) mod 29
    """
    result = []
    key_idx = offset
    max_key = len(primes)
    
    for c in cipher:
        if key_idx >= max_key:
            break
        
        # Apply Caesar shift first
        c_shifted = (c - caesar_shift) % MOD
        
        # Totient key: phi(prime) = prime - 1 for primes
        tkey = (primes[key_idx] - 1) % MOD
        
        if mode == 'sub':
            p = (c_shifted - tkey) % MOD
        elif mode == 'add':
            p = (c_shifted + tkey) % MOD
        elif mode == 'beau':
            p = (tkey - c_shifted) % MOD
        
        result.append(p)
        
        if f_skip and p == 0:  # F - don't advance
            pass
        else:
            key_idx += 1
    
    return result

def fast_score(cipher_window, primes, offset, mode, f_skip, caesar_shift):
    """Quick score on a window of ciphertext."""
    dec = totient_decrypt(cipher_window, primes, offset, mode, f_skip, caesar_shift)
    if not dec:
        return 0
    lat = to_latin(dec)
    return score_text(lat)

def main():
    # Generate primes - need enough for offset + page_length
    MAX_OFFSET = 20000
    MAX_RUNES = 2000
    print("Generating primes...")
    prime_limit = (MAX_OFFSET + MAX_RUNES) * 15  # Rough estimate: nth prime ~ n*ln(n)
    primes = sieve_primes(prime_limit)
    print(f"  Generated {len(primes)} primes (up to {primes[-1]})")
    
    if len(primes) < MAX_OFFSET + MAX_RUNES:
        print(f"  [!] Need more primes, re-sieving...")
        primes = sieve_primes(prime_limit * 3)
        print(f"  Generated {len(primes)} primes")
    
    pages = {
        32: {'caesar': 11},
        44: {'caesar': 5},
        50: {'caesar': 6},
    }
    
    WINDOW = 80  # First N runes for fast screening
    MODES = ['sub', 'add', 'beau']
    FSKIP_OPTIONS = [True, False]
    TOP_K = 20  # Keep top K candidates per config
    
    for page_num, info in pages.items():
        print(f"\n{'='*70}")
        print(f"PAGE {page_num} (known Caesar shift: {info['caesar']})")
        print(f"{'='*70}")
        
        cipher = load_runes(page_num)
        if not cipher:
            continue
        print(f"  Loaded {len(cipher)} runes")
        
        window = cipher[:WINDOW]
        
        # Test configurations
        caesar_shifts = [0, info['caesar']]  # No Caesar and known Caesar
        
        all_results = []
        
        for caesar in caesar_shifts:
            for mode in MODES:
                for f_skip in FSKIP_OPTIONS:
                    config_tag = f"C{caesar}_{mode}_fskip{int(f_skip)}"
                    
                    # Phase 1: Fast scan on window
                    best_in_config = []
                    
                    for offset in range(0, MAX_OFFSET):
                        if offset + WINDOW > len(primes):
                            break
                        sc = fast_score(window, primes, offset, mode, f_skip, caesar)
                        if sc > 30:  # Threshold for meaningful signal
                            best_in_config.append((sc, offset))
                    
                    # Keep top K
                    best_in_config.sort(reverse=True)
                    best_in_config = best_in_config[:TOP_K]
                    
                    if best_in_config:
                        print(f"\n  Config: {config_tag}")
                        print(f"  Top scores (window={WINDOW}): ", end="")
                        for sc, off in best_in_config[:5]:
                            print(f"off={off}:{sc}", end="  ")
                        print()
                        
                        # Phase 2: Full text verification on top candidates
                        for sc_win, offset in best_in_config[:5]:
                            full_dec = totient_decrypt(cipher, primes, offset, mode, f_skip, caesar)
                            full_lat = to_latin(full_dec)
                            full_sc = score_text(full_lat)
                            
                            preview = full_lat[:120]
                            all_results.append((full_sc, caesar, mode, f_skip, offset, preview))
                            
                            if full_sc > 100:
                                print(f"    ** FULL offset={offset} full_score={full_sc}: {preview}...")
                            elif full_sc > 50:
                                print(f"    offset={offset} full_score={full_sc}: {preview[:80]}...")
        
        # Summary for this page
        all_results.sort(reverse=True)
        print(f"\n  TOP 10 RESULTS for Page {page_num}:")
        for i, (sc, caesar, mode, f_skip, offset, preview) in enumerate(all_results[:10]):
            print(f"    #{i+1} score={sc} C{caesar} {mode} fskip={int(f_skip)} off={offset}")
            print(f"         {preview[:100]}")
    
    # Also test combined Caesar+Vigenere with DIVINITY on these pages
    # (in case the Caesar layer is real and the second layer is DIVINITY-based)
    print(f"\n{'='*70}")
    print("BONUS: Caesar + DIVINITY Vigenère test")
    print(f"{'='*70}")
    
    DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]
    kl = len(DIVINITY)
    
    for page_num, info in pages.items():
        cipher = load_runes(page_num)
        if not cipher:
            continue
        caesar = info['caesar']
        
        print(f"\n  Page {page_num} (Caesar {caesar} + DIVINITY):")
        
        best_score = 0
        best_config = None
        
        for mode in MODES:
            for offset in range(kl):
                for f_skip in [True, False]:
                    # Apply Caesar first
                    shifted = [(c - caesar) % MOD for c in cipher]
                    
                    # Then DIVINITY Vigenère (with optional F-skip)
                    dec = []
                    ki = offset
                    for c in shifted:
                        key_val = DIVINITY[ki % kl]
                        if mode == 'sub':
                            p = (c - key_val) % MOD
                        elif mode == 'add':
                            p = (c + key_val) % MOD
                        elif mode == 'beau':
                            p = (key_val - c) % MOD
                        
                        if f_skip and p == 0 and c == 0:
                            dec.append(0)
                            # don't advance key
                        else:
                            dec.append(p)
                            ki += 1
                    
                    lat = to_latin(dec)
                    sc = score_text(lat)
                    
                    if sc > best_score:
                        best_score = sc
                        best_config = (mode, offset, f_skip, lat[:120])
        
        if best_config:
            mode, offset, f_skip, preview = best_config
            print(f"    Best: score={best_score} {mode} off={offset} fskip={int(f_skip)}")
            print(f"    {preview}")

    # Test running key cipher using solved page plaintext
    print(f"\n{'='*70}")
    print("BONUS: Running key with P61 plaintext")
    print(f"{'='*70}")
    
    # P61 solved plaintext (GP indices)
    p61_text = "WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOUARDTHEENDOFALLTHINGSITISNOTANEASYTRIPBUTFORTHOSEUHOFINDHEIRWAYHEREITISANECESSARYONEALONGTHEUAYYOUUILLFINDANENDTOALLSTRUGGLEANDSUFFERINGYOURINNOCENCEYOURILLUSIONSYOURCERTAINTYANDYOURREALITYULTIMATELYYOUUILLDISCOUERANENDTOSELFITISTHROUGHTHISPILGRIMAGETHATUESHAPEOURSELUESANDOURREALITIESJOURNEYDEEPUITHINYOUUILLARRIUEOUTSIDELIKETHEINSTARITISONLY THROUGHGOINGUITHINTHATUEYMAYEMERGE"
    
    # Convert to GP indices
    ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,
              'L':20,'M':19,'N':9,'O':3,'P':13,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,
              'X':14,'Y':26}
    
    running_key_gp = []
    i = 0
    while i < len(p61_text):
        ch = p61_text[i].upper()
        # Check digraphs
        if i + 1 < len(p61_text):
            di = p61_text[i:i+2].upper()
            if di == 'TH':
                running_key_gp.append(2); i += 2; continue
            elif di == 'NG':
                running_key_gp.append(21); i += 2; continue
            elif di == 'EO':
                running_key_gp.append(12); i += 2; continue
            elif di == 'OE':
                running_key_gp.append(22); i += 2; continue
            elif di == 'EA':
                running_key_gp.append(28); i += 2; continue
            elif di == 'AE':
                running_key_gp.append(25); i += 2; continue
            elif di == 'IA':
                running_key_gp.append(27); i += 2; continue
        if ch in ENG2GP:
            running_key_gp.append(ENG2GP[ch])
        i += 1
    
    print(f"  Running key length: {len(running_key_gp)} GP values")
    
    for page_num, info in pages.items():
        cipher = load_runes(page_num)
        if not cipher:
            continue
        
        print(f"\n  Page {page_num}:")
        usable = min(len(cipher), len(running_key_gp))
        
        best_score = 0
        best_config = None
        
        for caesar in [0, info['caesar']]:
            for mode in MODES:
                dec = []
                for i in range(usable):
                    c = (cipher[i] - caesar) % MOD
                    k = running_key_gp[i]
                    if mode == 'sub':
                        p = (c - k) % MOD
                    elif mode == 'add':
                        p = (c + k) % MOD
                    elif mode == 'beau':
                        p = (k - c) % MOD
                    dec.append(p)
                
                lat = to_latin(dec)
                sc = score_text(lat)
                
                if sc > best_score:
                    best_score = sc
                    best_config = (caesar, mode, lat[:120])
        
        if best_config:
            caesar, mode, preview = best_config
            print(f"    Best: score={best_score} C{caesar} {mode}")
            print(f"    {preview}")

if __name__ == '__main__':
    main()
