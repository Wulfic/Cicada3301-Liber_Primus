#!/usr/bin/env python3
"""
Comprehensive P20 attack using P19's clue:
"REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR [KEY]"

Tests:
1. Prime-position extraction + Deor running key (Beaufort, SUB, ADD)
2. Prime-value extraction + Deor running key
3. Full page Deor running key
4. Deor refrain only as key
5. Various Deor tokenization methods
6. With and without F-skip
7. Word-level prime indexing
"""

import sys, os, math
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

# Standard Gematria Primus
GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
           'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
           'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

# Old English to GP mapping
OE2GP = {
    'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6, 'H': 8,
    'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9, 'O': 3, 'P': 13,
    'R': 4, 'S': 15, 'T': 16, 'U': 1, 'V': 1, 'W': 7, 'X': 14, 'Y': 26, 'Z': 14
}

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def calc_ioc(vals):
    if len(vals) < 2: return 0
    counts = Counter(vals)
    n = len(vals)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1) / 29) if n > 1 else 0

def score_english(text):
    """Score how English-like a decrypted text is."""
    common_words = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
                    'OUR','OUT','HIS','HAS','ITS','WHO','HOW','MAN','OLD','NEW','NOW','WAY',
                    'MAY','DAY','HAD','HIM','HAS','LET','SAY','SHE','TOO','USE','THAT','WITH',
                    'HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','SAID','EACH','WHICH',
                    'THEIR','THEM','THEN','THESE','SOME','WHEN','THAN','WHAT','WERE','THERE',
                    'INTO','LIKE','SELF','KNOW','MIND','MUST','FIND','WITHIN','BEING','SHALL',
                    'SEEK','PATH','FREE','TRUTH','WISDOM','LIGHT','DARK','SOUL','BODY',
                    'SPIRIT','DIVINE','SACRED','EVERY','ABOUT','WOULD','COULD','SHOULD',
                    'THOSE','AFTER','BEFORE','BETWEEN','THROUGH','UNDER','OVER','AGAIN',
                    'ONLY','ALSO','BOTH','JUST','VERY','EVEN','TYPE','FORM'}
    
    score = 0
    for word in common_words:
        if word in text:
            score += len(word) ** 2
    # Penalize uncommon bigrams
    bad_bigrams = set(['QQ','QX','QZ','XQ','ZQ','ZX','JJ','VV','KK','WW','XX','ZZ',
                       'JX','XJ','QJ','JQ','VX','XV','ZJ','JZ'])
    for i in range(len(text)-1):
        if text[i:i+2] in bad_bigrams:
            score -= 5
    return score

def tokenize_deor_method1(text):
    """Standard OE tokenization: handle TH/NG/EA/EO digraphs, Þ→TH, Ð→TH, Æ→AE"""
    text = text.upper()
    # Remove non-alpha chars
    cleaned = ''
    for ch in text:
        if ch.isalpha() or ch in 'ÞÐÆ':
            cleaned += ch
    
    # Replace special OE characters
    cleaned = cleaned.replace('Þ', 'TH').replace('Ð', 'TH').replace('Æ', 'AE')
    
    values = []
    i = 0
    while i < len(cleaned):
        # Check digraphs first
        if i + 1 < len(cleaned):
            di = cleaned[i:i+2]
            if di == 'TH':
                values.append(2)
                i += 2
                continue
            elif di == 'NG':
                values.append(21)
                i += 2
                continue
            elif di == 'EA':
                values.append(28)
                i += 2
                continue
            elif di == 'EO':
                values.append(12)
                i += 2
                continue
            elif di == 'OE':
                values.append(22)
                i += 2
                continue
            elif di == 'AE':
                values.append(25)
                i += 2
                continue
            elif di == 'IA':
                values.append(27)
                i += 2
                continue
        # Single char
        ch = cleaned[i]
        if ch in OE2GP:
            values.append(OE2GP[ch])
        i += 1
    return values

def tokenize_deor_method2(text):
    """Simple letter-by-letter: no digraphs, every letter maps individually"""
    text = text.upper()
    cleaned = ''
    for ch in text:
        if ch.isalpha() or ch in 'ÞÐÆ':
            cleaned += ch
    cleaned = cleaned.replace('Þ', 'TH').replace('Ð', 'TH').replace('Æ', 'AE')
    
    values = []
    for ch in cleaned:
        if ch in OE2GP:
            values.append(OE2GP[ch])
    return values

def load_p20():
    path = 'c:/Users/tyler/Repos/Cicada3301/LiberPrimus/pages/page_20/runes.txt'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    vals = [GP[ch] for ch in text if ch in GP]
    return vals

def load_deor():
    path = 'c:/Users/tyler/Repos/Cicada3301/Analysis/Reference_Docs/deor_poem.txt'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Extract only Old English section (before MODERN ENGLISH)
    if 'DEOR POEM (MODERN ENGLISH' in text:
        text = text[:text.index('DEOR POEM (MODERN ENGLISH')]
    # Remove the header line
    lines = text.strip().split('\n')
    oe_lines = [l for l in lines if l.strip() and 'DEOR POEM' not in l]
    oe_text = '\n'.join(oe_lines)
    return oe_text

def decrypt(cipher, key, mode):
    """Decrypt cipher with key using specified mode."""
    n = len(cipher)
    result = []
    for i in range(n):
        k = key[i % len(key)]
        c = cipher[i]
        if mode == 'sub':
            result.append((c - k) % 29)
        elif mode == 'beau':
            result.append((k - c) % 29)
        elif mode == 'add':
            result.append((c + k) % 29)
    return result

def vals_to_text(vals):
    return ''.join(IDX2LAT[v] for v in vals)

def main():
    print("=" * 70)
    print("P20 COMPREHENSIVE DEOR ATTACK")
    print("=" * 70)
    
    p20 = load_p20()
    deor_oe = load_deor()
    
    print(f"P20 runes: {len(p20)}")
    
    # Two tokenization methods for Deor
    deor_m1 = tokenize_deor_method1(deor_oe)
    deor_m2 = tokenize_deor_method2(deor_oe)
    
    print(f"Deor method 1 (with digraphs): {len(deor_m1)} values")
    print(f"Deor method 2 (letter-by-letter): {len(deor_m2)} values")
    print(f"Deor m1 first 20: {[IDX2LAT[v] for v in deor_m1[:20]]}")
    print(f"Deor m2 first 20: {[IDX2LAT[v] for v in deor_m2[:20]]}")
    
    # Also extract the refrain only
    refrain = "THAES OFEREODE THISSES SWA MAEG"
    refrain_vals = []
    for ch in refrain.upper():
        if ch in ENG2GP:
            refrain_vals.append(ENG2GP[ch])
    print(f"Refrain: {len(refrain_vals)} values = {vals_to_text(refrain_vals)}")
    
    results = []
    
    # ============================================
    # TEST 1: Prime positions (0-indexed) + Deor
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 1: Prime POSITIONS (0-indexed) + Deor key")
    print("=" * 70)
    
    prime_positions_0 = [i for i in range(len(p20)) if is_prime(i)]
    prime_positions_1 = [i for i in range(1, len(p20)+1) if is_prime(i)]
    
    for label, primes in [("0-indexed", prime_positions_0), ("1-indexed", [p-1 for p in prime_positions_1])]:
        for tok_label, deor_key in [("digraph", deor_m1), ("letter", deor_m2)]:
            # Extract cipher values at prime positions
            prime_cipher = [p20[p] for p in primes if p < len(p20)]
            # Get corresponding Deor key values at those positions
            for mode in ['sub', 'beau', 'add']:
                # Method A: Deor key at prime position index
                key_a = [deor_key[p % len(deor_key)] for p in primes if p < len(p20)]
                plain_a = [(prime_cipher[i] - key_a[i]) % 29 if mode == 'sub' else
                           (key_a[i] - prime_cipher[i]) % 29 if mode == 'beau' else
                           (prime_cipher[i] + key_a[i]) % 29
                           for i in range(len(prime_cipher))]
                ioc_a = calc_ioc(plain_a)
                text_a = vals_to_text(plain_a)
                score_a = score_english(text_a)
                
                # Method B: Deor key indexed sequentially (0,1,2,3,...)
                key_b = [deor_key[i % len(deor_key)] for i in range(len(prime_cipher))]
                plain_b = [(prime_cipher[i] - key_b[i]) % 29 if mode == 'sub' else
                           (key_b[i] - prime_cipher[i]) % 29 if mode == 'beau' else
                           (prime_cipher[i] + key_b[i]) % 29
                           for i in range(len(prime_cipher))]
                ioc_b = calc_ioc(plain_b)
                text_b = vals_to_text(plain_b)
                score_b = score_english(text_b)
                
                if ioc_a > 1.3 or score_a > 20:
                    results.append((ioc_a, score_a, f"PRIME_{label}_{tok_label}_{mode}_keyAtPos", text_a[:100]))
                if ioc_b > 1.3 or score_b > 20:
                    results.append((ioc_b, score_b, f"PRIME_{label}_{tok_label}_{mode}_keySeq", text_b[:100]))
    
    # ============================================
    # TEST 2: Prime VALUES + Deor
    # ============================================
    print("\nTEST 2: Prime VALUE runes + Deor key")
    
    prime_val_indices = [i for i, v in enumerate(p20) if is_prime(v)]
    nonprime_val_indices = [i for i, v in enumerate(p20) if not is_prime(v)]
    
    prime_stream = [p20[i] for i in prime_val_indices]
    nonprime_stream = [p20[i] for i in nonprime_val_indices]
    
    print(f"  Prime-valued runes: {len(prime_stream)} at {len(set(prime_stream))} unique values")
    print(f"  Non-prime-valued runes: {len(nonprime_stream)}")
    
    for tok_label, deor_key in [("digraph", deor_m1), ("letter", deor_m2)]:
        for mode in ['sub', 'beau', 'add']:
            # Decrypt non-prime stream with Deor
            np_key = [deor_key[i % len(deor_key)] for i in range(len(nonprime_stream))]
            np_plain = [(nonprime_stream[i] - np_key[i]) % 29 if mode == 'sub' else
                        (np_key[i] - nonprime_stream[i]) % 29 if mode == 'beau' else
                        (nonprime_stream[i] + np_key[i]) % 29
                        for i in range(len(nonprime_stream))]
            ioc = calc_ioc(np_plain)
            text = vals_to_text(np_plain)
            score = score_english(text)
            if ioc > 1.3 or score > 20:
                results.append((ioc, score, f"PRIMEVAL_nonprime_{tok_label}_{mode}", text[:100]))
    
    # ============================================
    # TEST 3: Full P20 + Deor running key
    # ============================================
    print("\nTEST 3: Full P20 + Deor running key (various offsets)")
    
    for tok_label, deor_key in [("digraph", deor_m1), ("letter", deor_m2)]:
        for mode in ['sub', 'beau', 'add']:
            for offset in range(0, len(deor_key), max(1, len(deor_key)//20)):
                shifted_key = deor_key[offset:] + deor_key[:offset]
                plain = decrypt(p20, shifted_key, mode)
                ioc = calc_ioc(plain)
                text = vals_to_text(plain)
                score = score_english(text)
                if ioc > 1.3 or score > 30:
                    results.append((ioc, score, f"FULL_{tok_label}_{mode}_off{offset}", text[:100]))
    
    # ============================================
    # TEST 4: Deor refrain as key
    # ============================================
    print("\nTEST 4: Deor refrain 'THAES OFEREODE THISSES SWA MAEG' as key")
    
    refrain_variants = [
        ("refrain_eng", refrain_vals),
        ("refrain_oe_m1", tokenize_deor_method1("Þæs ofereode, þisses swa mæg")),
        ("refrain_oe_m2", tokenize_deor_method2("Þæs ofereode, þisses swa mæg")),
    ]
    
    for ref_label, ref_key in refrain_variants:
        if not ref_key:
            continue
        for mode in ['sub', 'beau', 'add']:
            plain = decrypt(p20, ref_key, mode)
            ioc = calc_ioc(plain)
            text = vals_to_text(plain)
            score = score_english(text)
            if ioc > 1.3 or score > 20:
                results.append((ioc, score, f"{ref_label}_{mode}", text[:100]))
            
            # Also with F-skip
            plain_fs = []
            ki = 0
            for i in range(len(p20)):
                if p20[i] == 0:  # F rune
                    plain_fs.append(0)
                else:
                    k = ref_key[ki % len(ref_key)]
                    if mode == 'sub':
                        plain_fs.append((p20[i] - k) % 29)
                    elif mode == 'beau':
                        plain_fs.append((k - p20[i]) % 29)
                    else:
                        plain_fs.append((p20[i] + k) % 29)
                    ki += 1
            ioc_fs = calc_ioc(plain_fs)
            text_fs = vals_to_text(plain_fs)
            score_fs = score_english(text_fs)
            if ioc_fs > 1.3 or score_fs > 20:
                results.append((ioc_fs, score_fs, f"{ref_label}_{mode}_fskip", text_fs[:100]))
    
    # ============================================
    # TEST 5: "DEOR" as a 4-letter key
    # ============================================
    print("\nTEST 5: 'DEOR' as 4-letter Vigenère key")
    
    deor_short = [23, 18, 3, 4]  # D=23, E=18, O=3, R=4
    deor_short2 = [23, 12, 3, 4]  # D=23, EO=12, O=3, R=4
    
    for label, key in [("DEOR_std", deor_short), ("DEOR_eo", deor_short2)]:
        for mode in ['sub', 'beau', 'add']:
            plain = decrypt(p20, key, mode)
            ioc = calc_ioc(plain)
            text = vals_to_text(plain)
            score = score_english(text)
            if ioc > 1.3 or score > 20:
                results.append((ioc, score, f"{label}_{mode}", text[:100]))
            
            # F-skip variant
            plain_fs = []
            ki = 0
            for i in range(len(p20)):
                if p20[i] == 0:
                    plain_fs.append(0)
                else:
                    k = key[ki % len(key)]
                    if mode == 'sub':
                        plain_fs.append((p20[i] - k) % 29)
                    elif mode == 'beau':
                        plain_fs.append((k - p20[i]) % 29)
                    else:
                        plain_fs.append((p20[i] + k) % 29)
                    ki += 1
            ioc_fs = calc_ioc(plain_fs)
            text_fs = vals_to_text(plain_fs)
            score_fs = score_english(text_fs)
            if ioc_fs > 1.3 or score_fs > 20:
                results.append((ioc_fs, score_fs, f"{label}_{mode}_fskip", text_fs[:100]))
    
    # ============================================
    # TEST 6: Word-level prime indexing
    # ============================================
    print("\nTEST 6: Word-level prime indexing + Deor")
    
    # Read P20 with word boundaries
    path = 'c:/Users/tyler/Repos/Cicada3301/LiberPrimus/pages/page_20/runes.txt'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Split into words by dots
    words = []
    current_word = []
    for ch in text:
        if ch in GP:
            current_word.append(GP[ch])
        elif ch == '\u2022' or ch == '\n':
            if current_word:
                words.append(current_word)
                current_word = []
    if current_word:
        words.append(current_word)
    
    print(f"  Total words: {len(words)}")
    
    # Extract words at prime positions (1-indexed)
    prime_words = []
    for i in range(len(words)):
        if is_prime(i + 1):  # 1-indexed: word 2, 3, 5, 7, 11, ...
            prime_words.extend(words[i])
    
    print(f"  Runes in prime-indexed words: {len(prime_words)}")
    
    for tok_label, deor_key in [("digraph", deor_m1), ("letter", deor_m2)]:
        for mode in ['sub', 'beau', 'add']:
            key = [deor_key[i % len(deor_key)] for i in range(len(prime_words))]
            plain = [(prime_words[i] - key[i]) % 29 if mode == 'sub' else
                     (key[i] - prime_words[i]) % 29 if mode == 'beau' else
                     (prime_words[i] + key[i]) % 29
                     for i in range(len(prime_words))]
            ioc = calc_ioc(plain)
            text = vals_to_text(plain)
            score = score_english(text)
            if ioc > 1.3 or score > 20:
                results.append((ioc, score, f"PRIMEWORD_{tok_label}_{mode}", text[:100]))
    
    # ============================================
    # TEST 7: Rearranging primes - Fibonacci ordering
    # ============================================
    print("\nTEST 7: 'Rearranging primes' - various permutations")
    
    # The P32 grid showed Fibonacci connection to primes
    # What if we index primes by Fibonacci numbers?
    fibs = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    primes_list = [p for p in range(2, 2000) if is_prime(p)]
    
    # Get prime at Fibonacci index
    fib_primes = [primes_list[f] for f in fibs if f < len(primes_list)]
    print(f"  Fibonacci-indexed primes: {fib_primes}")
    
    # Use these as key values mod 29
    fib_prime_key = [p % 29 for p in fib_primes]
    print(f"  Fib-prime key mod 29: {fib_prime_key}")
    
    for mode in ['sub', 'beau', 'add']:
        plain = decrypt(p20, fib_prime_key, mode)
        ioc = calc_ioc(plain)
        text = vals_to_text(plain)
        score = score_english(text)
        if ioc > 1.3 or score > 20:
            results.append((ioc, score, f"FIB_PRIMES_{mode}", text[:100]))
    
    # ============================================ 
    # TEST 8: Combined approach - Deor on primes + something else on composites
    # ============================================
    print("\nTEST 8: Combined - Deor on prime positions, shift on others")
    
    for tok_label, deor_key in [("digraph", deor_m1)]:
        for mode in ['beau', 'sub']:
            for shift in range(29):
                combined = []
                prime_idx = 0
                composite_idx = 0
                for i in range(len(p20)):
                    if is_prime(i):
                        k = deor_key[prime_idx % len(deor_key)]
                        if mode == 'beau':
                            combined.append((k - p20[i]) % 29)
                        else:
                            combined.append((p20[i] - k) % 29)
                        prime_idx += 1
                    else:
                        combined.append((p20[i] - shift) % 29)
                        composite_idx += 1
                
                ioc = calc_ioc(combined)
                text = vals_to_text(combined)
                score = score_english(text)
                if ioc > 1.3 or score > 30:
                    results.append((ioc, score, f"COMBINED_{mode}_shift{shift}", text[:100]))
    
    # ============================================
    # RESULTS
    # ============================================
    print("\n" + "=" * 70)
    print("TOP RESULTS")
    print("=" * 70)
    
    results.sort(key=lambda x: (-x[0], -x[1]))
    
    if not results:
        print("No results above threshold!")
        # Print best IoC from all the prime position tests for reference
        print("\nReference - Prime position + Deor Beaufort (method 1, 0-indexed):")
        primes = [i for i in range(len(p20)) if is_prime(i)]
        deor = deor_m1
        cipher = [p20[p] for p in primes]
        key = [deor[p % len(deor)] for p in primes]
        plain = [(key[i] - cipher[i]) % 29 for i in range(len(cipher))]
        print(f"  IoC: {calc_ioc(plain):.4f}")
        print(f"  Length: {len(plain)}")
        print(f"  Text: {vals_to_text(plain)[:150]}")
        
        # Also show 1-indexed
        primes1 = [i-1 for i in range(1, len(p20)+1) if is_prime(i)]
        cipher1 = [p20[p] for p in primes1 if p < len(p20)]
        key1 = [deor[p % len(deor)] for p in primes1 if p < len(p20)]
        plain1 = [(key1[i] - cipher1[i]) % 29 for i in range(len(cipher1))]
        print(f"\nReference - Prime position + Deor Beaufort (method 1, 1-indexed):")
        print(f"  IoC: {calc_ioc(plain1):.4f}")
        print(f"  Length: {len(plain1)}")
        print(f"  Text: {vals_to_text(plain1)[:150]}")
        
        # Sequential key
        key_seq = [deor[i % len(deor)] for i in range(len(cipher))]
        plain_seq = [(key_seq[i] - cipher[i]) % 29 for i in range(len(cipher))]
        print(f"\nReference - Prime position + Deor Beaufort (method 1, key sequential):")
        print(f"  IoC: {calc_ioc(plain_seq):.4f}")
        print(f"  Text: {vals_to_text(plain_seq)[:150]}")
    else:
        for ioc, score, label, text in results[:20]:
            print(f"  IoC={ioc:.4f} Score={score:4d} {label}")
            print(f"    {text}")
            print()

if __name__ == '__main__':
    main()
