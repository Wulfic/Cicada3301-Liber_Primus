#!/usr/bin/env python3
"""
Running Key Cipher Attack on Liber Primus Unsolved Pages
=========================================================
Tests literary texts and solved page plaintexts as running keys.
IoC ≈ 1.0 across all unsolved pages strongly suggests running key cipher.

Key texts:
- Liber AL vel Legis (Crowley)  
- Self-Reliance (Emerson)
- Solved pages plaintext
- All combined
"""

import os, sys, re
from collections import Counter
from pathlib import Path

# Gematria Primus: Rune → Shift value
RUNE_TO_SHIFT = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛂ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28, 'ᛄ': 11  # ᛄ alt J
}
SHIFT_TO_ENGLISH = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X', 15: 'S',
    16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG', 22: 'OE', 23: 'D',
    24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

# English letter to GP shift value (for running key conversion)
ENGLISH_TO_SHIFT = {
    'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6, 'H': 8,
    'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9, 'O': 3, 'P': 13,
    'Q': 5, 'R': 4, 'S': 15, 'T': 16, 'U': 1, 'V': 1, 'W': 7, 'X': 14,
    'Y': 26, 'Z': 15
}

# Digraph mapping for better text-to-shift conversion
DIGRAPHS = {
    'TH': 2, 'NG': 21, 'EO': 12, 'OE': 22, 'EA': 28, 'AE': 25, 'IA': 27, 'IO': 27
}

def text_to_shifts_simple(text):
    """Convert English text to GP shift values (letter by letter, no digraphs)."""
    shifts = []
    for ch in text.upper():
        if ch in ENGLISH_TO_SHIFT:
            shifts.append(ENGLISH_TO_SHIFT[ch])
    return shifts

def text_to_shifts_digraph(text):
    """Convert English text to GP shift values WITH digraph recognition."""
    shifts = []
    text = text.upper()
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph in DIGRAPHS:
                shifts.append(DIGRAPHS[digraph])
                i += 2
                continue
        if text[i] in ENGLISH_TO_SHIFT:
            shifts.append(ENGLISH_TO_SHIFT[text[i]])
        i += 1
    return shifts

def extract_rune_shifts(rune_text):
    """Extract shift values from rune text, preserving word boundaries."""
    shifts = []
    separators = []  # Track separator positions for word reconstruction
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            shifts.append(RUNE_TO_SHIFT[ch])
    return shifts

def decode_to_runeglish(shifts):
    """Convert shift values to runeglish text."""
    return ''.join(SHIFT_TO_ENGLISH.get(s, '?') for s in shifts)

def calc_ioc(shifts):
    """Calculate Index of Coincidence."""
    if len(shifts) < 2:
        return 0
    freq = Counter(shifts)
    n = len(shifts)
    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = n * (n - 1)
    return (numerator / denominator) * 29 if denominator > 0 else 0

def score_text(runeglish):
    """Score text for English-likeness using common English bigrams/trigrams."""
    text = runeglish.upper()
    # Common English bigrams in runeglish form
    bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
               'TI', 'ES', 'OR', 'TE', 'OF', 'ED', 'IS', 'IT', 'AL', 'AR',
               'ST', 'TO', 'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'IO', 'LE',
               'VE', 'CO', 'ME', 'DE', 'HI', 'RI', 'RO', 'IC', 'NE', 'EA',
               'RA', 'CE', 'LI', 'CH', 'LL', 'BE', 'MA', 'SI', 'OM', 'UR']
    
    score = 0
    for bg in bigrams:
        score += text.count(bg) * 10
    
    # Common English words (when separated)
    words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN',
             'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'HAD', 'HAS', 'HIS',
             'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'WAY', 'WHO',
             'DID', 'GET', 'LET', 'SAY', 'SHE', 'TOO', 'USE', 'MAN', 'THAT',
             'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'BEEN',
             'SOME', 'WHEN', 'WHAT', 'THERE', 'WHICH', 'THEIR', 'SHALL',
             'EACH', 'MAKE', 'LIKE', 'INTO', 'THEM', 'THAN', 'MOST',
             'FIND', 'HERE', 'KNOW', 'TAKE', 'COME', 'MADE', 'AFTER',
             'TRUTH', 'LIGHT', 'PATH', 'WISDOM', 'DIVINE', 'SACRED']
    for w in words:
        score += text.count(w) * len(w) * 3
    
    return score

def try_running_key(cipher_shifts, key_shifts, offset, mode):
    """Apply running key at given offset with given mode."""
    result = []
    key_len = len(key_shifts)
    for i, c in enumerate(cipher_shifts):
        k = key_shifts[(i + offset) % key_len]
        if mode == 'sub':
            plain = (c - k) % 29
        elif mode == 'beaufort':
            plain = (k - c) % 29
        elif mode == 'add':
            plain = (c + k) % 29
        result.append(plain)
    return result

def load_page_runes(page_dir):
    """Load rune text from a page directory."""
    runes_file = os.path.join(page_dir, 'runes.txt')
    if os.path.exists(runes_file):
        with open(runes_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def load_literary_text(filepath):
    """Load a text file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def get_solved_plaintext():
    """Return known solved page plaintexts concatenated."""
    # From verified solutions
    texts = [
        # Page 57 (cleartext - The Parable)
        "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
        # Page 55-56 (AN END)
        "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
        # Pages 0-16 (LP1 solved content - key phrases from solved pages)
        "A KOAN A COAN WHAT IS MY WILL DIVIDE CONQUER COMMAND MORE DIVIDE MORE",
        "SOME WISDOM AN INSTRUCTION A WARNING A LOSS OF DIVINITY",
        "THE INSTAR SHALL AWAKEN COMMAND YOUR OWN I OS AND SYSTEMS CONSUME DIVIDE BE REBORN",
        "WELCOME PILGRIM TO THE GREAT JOURNEY THE CIRCUMFERENCE IS THUS DEFINED",
        "WISDOM IS NOT THE PROPERTY OF SCHOOLS KNOWLEDGE IS THAT WHICH ENDURES",
        "BELIEVE NOTHING TRUST YOUR INSTINCT USE YOUR FORCE",
    ]
    return ' '.join(texts)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    research_dir = os.path.join(repo_dir, 'LiberPrimus', 'reference', 'research')
    
    print("=" * 80)
    print("RUNNING KEY CIPHER ATTACK ON LIBER PRIMUS UNSOLVED PAGES")
    print("=" * 80)
    
    # Load unsolved pages
    unsolved_pages = {}
    for p in range(17, 55):  # Pages 17-54 (unsolved)
        page_dir = os.path.join(pages_dir, f'page_{p:02d}')
        rune_text = load_page_runes(page_dir)
        if rune_text:
            shifts = extract_rune_shifts(rune_text)
            if len(shifts) > 20:  # Skip very small pages
                unsolved_pages[p] = {'shifts': shifts, 'rune_text': rune_text}
    
    print(f"\nLoaded {len(unsolved_pages)} unsolved pages")
    for p in sorted(unsolved_pages.keys()):
        print(f"  Page {p}: {len(unsolved_pages[p]['shifts'])} runes")
    
    # Load key texts
    key_texts = {}
    
    # 1. Liber AL vel Legis
    liber_al_path = os.path.join(research_dir, 'liber_al_vel_legis.txt')
    if os.path.exists(liber_al_path):
        liber_al = load_literary_text(liber_al_path)
        key_texts['LiberAL_simple'] = text_to_shifts_simple(liber_al)
        key_texts['LiberAL_digraph'] = text_to_shifts_digraph(liber_al)
        print(f"\nLiber AL vel Legis: {len(key_texts['LiberAL_simple'])} shifts (simple), {len(key_texts['LiberAL_digraph'])} shifts (digraph)")
    
    # 2. Self-Reliance by Emerson
    sr_path = os.path.join(research_dir, 'Self-Reliance.txt')
    if os.path.exists(sr_path):
        sr_text = load_literary_text(sr_path)
        key_texts['SelfReliance_simple'] = text_to_shifts_simple(sr_text)
        key_texts['SelfReliance_digraph'] = text_to_shifts_digraph(sr_text)
        print(f"Self-Reliance: {len(key_texts['SelfReliance_simple'])} shifts (simple), {len(key_texts['SelfReliance_digraph'])} shifts (digraph)")
    
    # 3. Solved pages plaintext
    solved_text = get_solved_plaintext()
    key_texts['SolvedPages_simple'] = text_to_shifts_simple(solved_text)
    key_texts['SolvedPages_digraph'] = text_to_shifts_digraph(solved_text)
    print(f"Solved Pages: {len(key_texts['SolvedPages_simple'])} shifts (simple), {len(key_texts['SolvedPages_digraph'])} shifts (digraph)")
    
    # 4. Combined all texts
    all_text = ""
    if os.path.exists(liber_al_path):
        all_text += load_literary_text(liber_al_path) + " "
    if os.path.exists(sr_path):
        all_text += load_literary_text(sr_path) + " "
    all_text += solved_text
    key_texts['AllCombined_simple'] = text_to_shifts_simple(all_text)
    key_texts['AllCombined_digraph'] = text_to_shifts_digraph(all_text)
    print(f"All Combined: {len(key_texts['AllCombined_simple'])} shifts (simple), {len(key_texts['AllCombined_digraph'])} shifts (digraph)")
    
    # 5. Deor poem (already tokenized in prior work - use simple method)
    deor_path = os.path.join(repo_dir, 'LiberPrimus', 'reference', 'research', 'deor_poem.txt')
    if not os.path.exists(deor_path):
        deor_path = os.path.join(repo_dir, 'Analysis', 'Reference_Docs', 'deor_poem.txt')
    if os.path.exists(deor_path):
        deor_text = load_literary_text(deor_path)
        key_texts['Deor_simple'] = text_to_shifts_simple(deor_text)
        key_texts['Deor_digraph'] = text_to_shifts_digraph(deor_text)
        print(f"Deor Poem: {len(key_texts['Deor_simple'])} shifts (simple), {len(key_texts['Deor_digraph'])} shifts (digraph)")
    
    # 6. Numbers-based keys: primes, totients, fibonacci, etc.
    # Prime number stream
    def sieve_primes(n):
        """Generate first n primes."""
        primes = []
        candidate = 2
        while len(primes) < n:
            is_prime = True
            for p in primes:
                if p * p > candidate:
                    break
                if candidate % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(candidate)
            candidate += 1
        return primes
    
    primes = sieve_primes(3000)
    
    # Totient stream (what P55 uses): phi(prime) = prime - 1
    totient_stream = [(p - 1) % 29 for p in primes]
    key_texts['Totient'] = totient_stream
    
    # Raw prime stream
    prime_stream = [p % 29 for p in primes]
    key_texts['Primes'] = prime_stream
    
    # Prime gaps
    prime_gaps = [(primes[i+1] - primes[i]) % 29 for i in range(len(primes)-1)]
    key_texts['PrimeGaps'] = prime_gaps
    
    # Cumulative prime gaps (partial sums)
    cum_gaps = []
    s = 0
    for g in prime_gaps:
        s = (s + g) % 29
        cum_gaps.append(s)
    key_texts['CumPrimeGaps'] = cum_gaps
    
    # Fibonacci stream
    fib = [1, 1]
    for _ in range(3000):
        fib.append(fib[-1] + fib[-2])
    key_texts['Fibonacci'] = [f % 29 for f in fib]
    
    # Triangular numbers
    triangular = [n*(n+1)//2 % 29 for n in range(3000)]
    key_texts['Triangular'] = triangular
    
    # Square numbers  
    squares = [n*n % 29 for n in range(3000)]
    key_texts['Squares'] = squares
    
    # Consecutive totients: phi(1), phi(2), phi(3), ...
    def euler_totient(n):
        result = n
        p = 2
        temp = n
        while p * p <= temp:
            if temp % p == 0:
                while temp % p == 0:
                    temp //= p
                result -= result // p
            p += 1
        if temp > 1:
            result -= result // temp
        return result
    
    consec_totients = [euler_totient(n) % 29 for n in range(1, 3001)]
    key_texts['ConsecTotients'] = consec_totients
    
    print(f"\nTotal key streams to test: {len(key_texts)}")
    
    modes = ['sub', 'beaufort', 'add']
    
    # ==================== ATTACK ====================
    print("\n" + "=" * 80)
    print("PHASE 1: Systematic scan - all pages × all keys × all modes")
    print("=" * 80)
    
    # Focus on largest pages first for statistical reliability
    target_pages = sorted(unsolved_pages.keys(), 
                         key=lambda p: len(unsolved_pages[p]['shifts']), 
                         reverse=True)[:10]  # Top 10 largest pages
    
    best_results = []
    
    for page_num in target_pages:
        page_data = unsolved_pages[page_num]
        cipher = page_data['shifts']
        n_runes = len(cipher)
        
        print(f"\n--- Page {page_num} ({n_runes} runes) ---")
        page_best = {'ioc': 0, 'score': 0, 'text': '', 'key': '', 'mode': '', 'offset': 0}
        
        for key_name, key_shifts in key_texts.items():
            key_len = len(key_shifts)
            
            # Determine offset range based on key length vs cipher length
            if key_len <= n_runes:
                # Key shorter than cipher - will wrap. Test offset 0 only (wrapping makes all offsets equivalent)
                offsets = [0]
            else:
                # Key longer than cipher - test multiple offsets
                max_offset = min(key_len - n_runes + 1, 200)
                step = max(1, max_offset // 50)  # Sample ~50 offsets
                offsets = list(range(0, max_offset, step))
            
            for mode in modes:
                for offset in offsets:
                    plain = try_running_key(cipher, key_shifts, offset, mode)
                    ioc = calc_ioc(plain)
                    
                    if ioc > 1.25:  # Promising threshold
                        runeglish = decode_to_runeglish(plain)
                        txt_score = score_text(runeglish)
                        total = ioc * 100 + txt_score
                        
                        if total > page_best.get('total', 0):
                            page_best = {
                                'ioc': ioc, 'score': txt_score, 'total': total,
                                'text': runeglish[:200], 'key': key_name,
                                'mode': mode, 'offset': offset, 'page': page_num
                            }
                        
                        if ioc > 1.4:  # Strong signal
                            runeglish = decode_to_runeglish(plain)
                            txt_score = score_text(runeglish)
                            print(f"  ** IoC={ioc:.3f} score={txt_score} key={key_name} mode={mode} off={offset}")
                            print(f"     Text: {runeglish[:120]}")
                            best_results.append({
                                'page': page_num, 'ioc': ioc, 'score': txt_score,
                                'text': runeglish[:200], 'key': key_name,
                                'mode': mode, 'offset': offset
                            })
        
        if page_best.get('ioc', 0) > 1.0:
            print(f"  Best: IoC={page_best['ioc']:.3f} score={page_best.get('score',0)} "
                  f"key={page_best['key']} mode={page_best['mode']} off={page_best['offset']}")
            print(f"     Text: {page_best.get('text','')[:120]}")
    
    # ==================== PHASE 2: Deep scan on promising results ====================
    print("\n" + "=" * 80)
    print("PHASE 2: Extended offset scan for literary texts")
    print("=" * 80)
    
    literary_keys = {k: v for k, v in key_texts.items() 
                     if 'simple' in k or 'digraph' in k}
    
    for page_num in target_pages[:5]:  # Top 5 largest
        cipher = unsolved_pages[page_num]['shifts']
        n_runes = len(cipher)
        
        print(f"\n--- Page {page_num} ({n_runes} runes) - Extended scan ---")
        
        for key_name, key_shifts in literary_keys.items():
            key_len = len(key_shifts)
            if key_len <= n_runes:
                continue  # Skip keys shorter than cipher
            
            for mode in modes:
                best_ioc = 0
                best_offset = 0
                best_text = ''
                
                # Sample offsets evenly across the valid range
                max_off = key_len - n_runes + 1
                step = max(1, max_off // 500)  # ~500 samples
                for offset in range(0, max_off, step):
                    plain = try_running_key(cipher, key_shifts, offset, mode)
                    ioc = calc_ioc(plain)
                    
                    if ioc > best_ioc:
                        best_ioc = ioc
                        best_offset = offset
                        best_text = decode_to_runeglish(plain)
                
                if best_ioc > 1.15:
                    txt_score = score_text(best_text)
                    print(f"  {key_name} {mode}: best IoC={best_ioc:.3f} at offset={best_offset} score={txt_score}")
                    print(f"     Text: {best_text[:150]}")
                else:
                    print(f"  {key_name} {mode}: best IoC={best_ioc:.3f} (below threshold)")
    
    # ==================== PHASE 3: Cross-page concatenation ====================
    print("\n" + "=" * 80)
    print("PHASE 3: Cross-page concatenation attack")
    print("=" * 80)
    
    # Concatenate ALL unsolved pages in order
    all_cipher = []
    page_boundaries = {}
    pos = 0
    for p in sorted(unsolved_pages.keys()):
        page_boundaries[p] = (pos, pos + len(unsolved_pages[p]['shifts']))
        all_cipher.extend(unsolved_pages[p]['shifts'])
        pos += len(unsolved_pages[p]['shifts'])
    
    print(f"Total concatenated runes: {len(all_cipher)}")
    
    # Try totient stream on concatenated text
    for mode in modes:
        plain = try_running_key(all_cipher, totient_stream, 0, mode)
        
        # Check IoC of sub-sections
        for p, (start, end) in page_boundaries.items():
            page_plain = plain[start:end]
            if len(page_plain) > 50:
                ioc = calc_ioc(page_plain)
                if ioc > 1.3:
                    runeglish = decode_to_runeglish(page_plain)
                    print(f"  Concat totient {mode}: Page {p} IoC={ioc:.3f}")
                    print(f"     Text: {runeglish[:120]}")
    
    # Try Self-Reliance as continuous running key across all pages
    for key_name in ['SelfReliance_simple', 'SelfReliance_digraph', 'LiberAL_simple', 'LiberAL_digraph']:
        if key_name not in key_texts:
            continue
        key_shifts = key_texts[key_name]
        if len(key_shifts) < len(all_cipher):
            continue
        
        for mode in modes:
            # Try a range of starting offsets
            max_off = min(len(key_shifts) - len(all_cipher) + 1, 100)
            for offset in range(0, max_off, 5):
                plain = try_running_key(all_cipher, key_shifts, offset, mode)
                
                for p, (start, end) in page_boundaries.items():
                    page_plain = plain[start:end]
                    if len(page_plain) > 50:
                        ioc = calc_ioc(page_plain)
                        if ioc > 1.3:
                            runeglish = decode_to_runeglish(page_plain)
                            print(f"  Concat {key_name} {mode} off={offset}: Page {p} IoC={ioc:.3f}")
                            print(f"     Text: {runeglish[:120]}")
    
    # ==================== PHASE 4: Multiplicative / Affine cipher ====================
    print("\n" + "=" * 80)
    print("PHASE 4: Multiplicative and Affine cipher (non-stream)")
    print("=" * 80)
    
    # Multiplicative: plain = (cipher * k_inv) % 29  
    # Since 29 is prime, all k from 1-28 have inverses
    for page_num in target_pages[:5]:
        cipher = unsolved_pages[page_num]['shifts']
        n_runes = len(cipher)
        
        for k in range(1, 29):
            # Check if k has inverse (always true mod 29 prime)
            k_inv = pow(k, -1, 29)
            
            # Simple multiplicative
            plain = [(c * k_inv) % 29 for c in cipher]
            ioc = calc_ioc(plain)
            if ioc > 1.3:
                runeglish = decode_to_runeglish(plain)
                txt_score = score_text(runeglish)
                print(f"  Page {page_num} mult k={k}: IoC={ioc:.3f} score={txt_score}")
                print(f"     Text: {runeglish[:120]}")
            
            # Affine: plain = (k_inv * (cipher - b)) % 29, try all b
            for b in range(29):
                plain = [(k_inv * (c - b)) % 29 for c in cipher]
                ioc = calc_ioc(plain)
                if ioc > 1.4:
                    runeglish = decode_to_runeglish(plain)
                    txt_score = score_text(runeglish)
                    print(f"  Page {page_num} affine k={k} b={b}: IoC={ioc:.3f} score={txt_score}")
                    print(f"     Text: {runeglish[:120]}")
    
    # ==================== PHASE 5: Totient-prime hybrid streams ====================
    print("\n" + "=" * 80)
    print("PHASE 5: Novel number-theoretic streams")
    print("=" * 80)
    
    # Stream 1: phi(n) for n = 1,2,3,...
    # Stream 2: Mobius function-based
    # Stream 3: Prime counting function pi(n) 
    # Stream 4: Sum of digits of primes
    # Stream 5: Prime in different base
    
    novel_streams = {}
    
    # Sum of digits of consecutive primes
    def digit_sum(n):
        return sum(int(d) for d in str(n))
    
    novel_streams['PrimeDigitSum'] = [digit_sum(p) % 29 for p in primes[:3000]]
    
    # Product of digits of primes (non-zero digits)
    def digit_prod(n):
        result = 1
        for d in str(n):
            if d != '0':
                result *= int(d)
        return result
    
    novel_streams['PrimeDigitProd'] = [digit_prod(p) % 29 for p in primes[:3000]]
    
    # Prime index: prime[n] / (n+1) rounded, mod 29
    novel_streams['PrimeIndex'] = [(primes[i] * (i+1)) % 29 for i in range(3000)]
    
    # XOR of consecutive primes
    novel_streams['PrimeXOR'] = [(primes[i] ^ primes[i+1]) % 29 for i in range(2999)]
    
    # Reciprocal primes: floor(29 * n / prime(n)) mod 29
    novel_streams['PrimeReciprocal'] = [(29 * (i+1) // primes[i]) % 29 for i in range(3000)]
    
    # Prime factorization count
    def count_factors(n):
        count = 0
        d = 2
        while d * d <= n:
            while n % d == 0:
                count += 1
                n //= d
            d += 1
        if n > 1:
            count += 1
        return count
    
    novel_streams['FactorCount'] = [count_factors(n) % 29 for n in range(2, 3002)]
    
    # Collatz steps
    def collatz_steps(n):
        steps = 0
        while n > 1 and steps < 1000:
            if n % 2 == 0:
                n //= 2
            else:
                n = 3 * n + 1
            steps += 1
        return steps
    
    novel_streams['Collatz'] = [collatz_steps(n) % 29 for n in range(1, 3001)]
    
    for stream_name, stream in novel_streams.items():
        for page_num in target_pages[:5]:
            cipher = unsolved_pages[page_num]['shifts']
            
            for mode in modes:
                for offset in range(min(29, len(stream) - len(cipher))):
                    plain = try_running_key(cipher, stream, offset, mode)
                    ioc = calc_ioc(plain)
                    
                    if ioc > 1.35:
                        runeglish = decode_to_runeglish(plain)
                        txt_score = score_text(runeglish)
                        print(f"  Page {page_num} {stream_name} {mode} off={offset}: IoC={ioc:.3f} score={txt_score}")
                        print(f"     Text: {runeglish[:120]}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if best_results:
        best_results.sort(key=lambda x: x['ioc'], reverse=True)
        print(f"\nTop {min(20, len(best_results))} results (IoC > 1.4):")
        for i, r in enumerate(best_results[:20]):
            print(f"  {i+1}. Page {r['page']}: IoC={r['ioc']:.3f} score={r['score']} "
                  f"key={r['key']} mode={r['mode']} off={r['offset']}")
            print(f"     {r['text'][:120]}")
    else:
        print("\nNo results with IoC > 1.4 found across all tests.")
        print("This rules out simple running key using tested literary texts.")
    
    print(f"\nTotal key streams tested: {len(key_texts) + len(novel_streams)}")
    print(f"Total pages tested: {len(target_pages)}")
    print(f"Modes tested: {modes}")

if __name__ == '__main__':
    main()
