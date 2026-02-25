#!/usr/bin/env python3
"""
Novel Structural Attack Vectors for Liber Primus
================================================
Tests non-standard approaches:
1. Word-boundary key reset with various streams
2. Per-word reversed rune order
3. Page 22 focused attack (Friedman key~19)
4. Separator-encoded information
5. GP prime values (not shifts) as cipher/key space
6. Rune-as-binary (5-bit encoding)
7. Position-dependent transformations
"""

import os, sys, math
from collections import Counter

RUNE_TO_SHIFT = {
    '\u16a0': 0, '\u16a2': 1, '\u16a6': 2, '\u16a9': 3, '\u16b1': 4,
    '\u16b3': 5, '\u16b7': 6, '\u16b9': 7, '\u16bb': 8, '\u16be': 9,
    '\u16c1': 10, '\u16c2': 11, '\u16c7': 12, '\u16c8': 13, '\u16c9': 14,
    '\u16cb': 15, '\u16cf': 16, '\u16d2': 17, '\u16d6': 18, '\u16d7': 19,
    '\u16da': 20, '\u16dd': 21, '\u16df': 22, '\u16de': 23, '\u16aa': 24,
    '\u16ab': 25, '\u16a3': 26, '\u16e1': 27, '\u16e0': 28, '\u16c4': 11
}

SHIFT_TO_GP_PRIME = {
    0: 2, 1: 3, 2: 5, 3: 7, 4: 11, 5: 13, 6: 17, 7: 19, 8: 23, 9: 29,
    10: 31, 11: 37, 12: 41, 13: 43, 14: 47, 15: 53, 16: 59, 17: 61,
    18: 67, 19: 71, 20: 73, 21: 79, 22: 83, 23: 89, 24: 97, 25: 101,
    26: 103, 27: 107, 28: 109
}

SHIFT_TO_ENGLISH = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X', 15: 'S',
    16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG', 22: 'OE', 23: 'D',
    24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

def calc_ioc(shifts):
    if len(shifts) < 2: return 0
    freq = Counter(shifts)
    n = len(shifts)
    return sum(f*(f-1) for f in freq.values()) / (n*(n-1)) * 29

def decode_to_runeglish(shifts):
    return ''.join(SHIFT_TO_ENGLISH.get(s, '?') for s in shifts)

def score_text(text):
    t = text.upper()
    bigrams = ['TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','ES','OR','TE','ED','IS','IT','AL','AR','ST','TO']
    score = sum(t.count(bg) * 10 for bg in bigrams)
    words = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','WAS','ONE','OUR',
             'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','SOME',
             'WHEN','WHAT','THERE','WHICH','SHALL','EACH','FIND','WISDOM','TRUTH']
    for w in words: score += t.count(w) * len(w) * 3
    return score

def sieve_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        if all(c % p for p in primes if p*p <= c):
            primes.append(c)
        c += 1
    return primes

def parse_rune_words(rune_text):
    """Parse rune text into list of words (each word is list of shift values).
    Also returns the full ordered shift list and word boundary positions."""
    words = []
    current = []
    full_shifts = []
    word_starts = []  # position in full_shifts where each word starts
    
    for ch in rune_text:
        if ch in RUNE_TO_SHIFT:
            if not current:
                word_starts.append(len(full_shifts))
            shift = RUNE_TO_SHIFT[ch]
            current.append(shift)
            full_shifts.append(shift)
        elif ch in '-\u2022 \n':
            if current:
                words.append(current)
                current = []
        elif ch == '.':
            if current:
                words.append(current)
                current = []
    if current:
        words.append(current)
    
    return words, full_shifts, word_starts

def load_page(pages_dir, p):
    path = os.path.join(pages_dir, f'page_{p:02d}', 'runes.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    PRIMES = sieve_primes(3000)
    TOTIENTS = [(p - 1) % 29 for p in PRIMES]
    
    print("=" * 80)
    print("NOVEL STRUCTURAL ATTACKS ON LIBER PRIMUS")
    print("=" * 80)
    
    # Load pages
    pages = {}
    for p in range(17, 55):
        rt = load_page(pages_dir, p)
        if rt:
            words, shifts, wstarts = parse_rune_words(rt)
            if len(shifts) > 20:
                pages[p] = {'text': rt, 'words': words, 'shifts': shifts, 'wstarts': wstarts}
    
    print(f"Loaded {len(pages)} pages")
    
    best_results = []
    
    # ==================== TEST 1: Word-reset stream cipher ====================
    print("\n" + "=" * 80)
    print("TEST 1: Word-boundary key reset")
    print("Key stream resets to beginning at each word boundary")
    print("Streams: totients, primes, fibonacci, position, consecutive ints")
    print("=" * 80)
    
    fib = [1, 1]
    for _ in range(200): fib.append(fib[-1] + fib[-2])
    
    streams = {
        'totient': TOTIENTS,
        'prime': [p % 29 for p in PRIMES],
        'position': list(range(200)),  # 0,1,2,...
        'fibonacci': [f % 29 for f in fib],
        'squares': [i*i % 29 for i in range(200)],
        'triangular': [i*(i+1)//2 % 29 for i in range(200)],
    }
    
    modes = {
        'sub': lambda c, k: (c - k) % 29,
        'beaufort': lambda c, k: (k - c) % 29,
        'add': lambda c, k: (c + k) % 29,
    }
    
    for page_num in sorted(pages.keys()):
        pdata = pages[page_num]
        words = pdata['words']
        cipher = pdata['shifts']
        n = len(cipher)
        
        for stream_name, stream in streams.items():
            for mode_name, mode_func in modes.items():
                # Apply stream resetting at each word
                plain = []
                for word in words:
                    for i, c in enumerate(word):
                        if i < len(stream):
                            plain.append(mode_func(c, stream[i] % 29))
                        else:
                            plain.append(c)  # If word longer than stream, leave as is
                
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"  Page {page_num} {stream_name}/{mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    Text: {text[:150]}")
                    best_results.append({'page': page_num, 'test': 'word_reset',
                                        'stream': stream_name, 'mode': mode_name,
                                        'ioc': ioc, 'score': s, 'text': text[:200]})
    
    # ==================== TEST 2: Reversed words + stream ====================
    print("\n" + "=" * 80)
    print("TEST 2: Reverse runes within each word, then apply stream")
    print("=" * 80)
    
    for page_num in sorted(pages.keys()):
        pdata = pages[page_num]
        words = pdata['words']
        
        # Create reversed-word cipher
        reversed_shifts = []
        for word in words:
            reversed_shifts.extend(word[::-1])
        
        for stream_name in ['totient', 'prime']:
            stream = streams[stream_name]
            for mode_name, mode_func in modes.items():
                # Apply stream continuously to reversed-word text
                plain = [mode_func(reversed_shifts[i], stream[i % len(stream)]) for i in range(len(reversed_shifts))]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"  Page {page_num} reversed+{stream_name}/{mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    Text: {text[:150]}")
    
    # ==================== TEST 3: Page 22 focused attack ====================
    print("\n" + "=" * 80)
    print("TEST 3: Page 22 focused attack (Friedman key length ~ 19)")
    print("131 runes, IoC=1.039 - try Vigenere with periods 17-23")
    print("=" * 80)
    
    if 22 in pages:
        cipher = pages[22]['shifts']
        n = len(cipher)
        
        for period in range(2, 30):
            # Split into columns
            columns = [[] for _ in range(period)]
            for i, s in enumerate(cipher):
                columns[i % period].append(s)
            
            # Check avg IoC of columns
            col_iocs = [calc_ioc(col) for col in columns if len(col) >= 3]
            avg_ioc = sum(col_iocs) / len(col_iocs) if col_iocs else 0
            
            if avg_ioc > 1.2:
                print(f"  Period {period}: avg column IoC = {avg_ioc:.3f} (columns: {[f'{x:.2f}' for x in col_iocs[:5]]}...)")
                
                # Try to solve each column as Caesar
                for mode_name, mode_func in modes.items():
                    best_key = []
                    for col in columns:
                        best_shift = 0
                        best_col_score = -1
                        for shift in range(29):
                            decrypted = [mode_func(c, shift) for c in col]
                            text = decode_to_runeglish(decrypted)
                            s = score_text(text)
                            ioc_col = calc_ioc(decrypted)
                            combined = ioc_col * 10 + s
                            if combined > best_col_score:
                                best_col_score = combined
                                best_shift = shift
                        best_key.append(best_shift)
                    
                    # Decrypt with best key
                    plain = [mode_func(cipher[i], best_key[i % period]) for i in range(n)]
                    ioc = calc_ioc(plain)
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    
                    if ioc > 1.3 or s > 100:
                        key_str = ','.join(str(k) for k in best_key)
                        print(f"    Period {period} {mode_name}: IoC={ioc:.3f} score={s} key=[{key_str}]")
                        print(f"    Text: {text[:150]}")
        
        # Also try ALL 29 Caesar shifts on the whole page
        for shift in range(29):
            for mode_name, mode_func in modes.items():
                plain = [mode_func(c, shift) for c in cipher]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"    Caesar shift={shift} {mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    Text: {text[:150]}")
    
    # ==================== TEST 4: GP prime values as cipher space ====================
    print("\n" + "=" * 80)
    print("TEST 4: Work in GP prime value space (not shift space)")
    print("cipher_prime op key_prime -> plain_prime")
    print("=" * 80)
    
    ALL_GP_PRIMES = sorted(SHIFT_TO_GP_PRIME.values())  # [2,3,5,...,109]
    PRIME_TO_SHIFT = {v: k for k, v in SHIFT_TO_GP_PRIME.items()}
    
    target_pages = sorted(pages.keys(), key=lambda p: len(pages[p]['shifts']), reverse=True)[:5]
    
    for page_num in target_pages:
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        cipher_primes = [SHIFT_TO_GP_PRIME[s] for s in cipher]
        
        # Try: plain_prime = cipher_prime XOR key
        for stream_name in ['totient', 'prime']:
            stream_vals = [PRIMES[i] for i in range(n)] if stream_name == 'prime' else [PRIMES[i]-1 for i in range(n)]
            
            # XOR
            xor_result = [cp ^ sv for cp, sv in zip(cipher_primes, stream_vals)]
            # Map back: find closest GP prime
            plain = []
            for val in xor_result:
                # Find closest GP prime
                closest = min(ALL_GP_PRIMES, key=lambda p: abs(p - (val % 110)))
                plain.append(PRIME_TO_SHIFT[closest])
            
            ioc = calc_ioc(plain)
            if ioc > 1.2:
                text = decode_to_runeglish(plain)
                print(f"  Page {page_num} XOR {stream_name}: IoC={ioc:.3f}")
                print(f"    Text: {text[:150]}")
        
        # Try: (cipher_prime * key_prime) mod 29
        for key_prime in ALL_GP_PRIMES:
            plain = [(cp * key_prime) % 29 for cp in cipher_primes]
            ioc = calc_ioc(plain)
            if ioc > 1.3:
                text = decode_to_runeglish(plain)
                s = score_text(text)
                print(f"  Page {page_num} mult_prime key={key_prime}: IoC={ioc:.3f} score={s}")
                print(f"    Text: {text[:150]}")
    
    # ==================== TEST 5: Interleaved/deinterleaved reading ====================
    print("\n" + "=" * 80)
    print("TEST 5: Reading order transformations")
    print("Read runes in non-sequential order, then apply simple shifts")
    print("=" * 80)
    
    for page_num in target_pages[:5]:
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        
        # Try various reading orders
        reading_orders = {
            'reverse': list(range(n-1, -1, -1)),
            'even_odd': list(range(0, n, 2)) + list(range(1, n, 2)),
            'odd_even': list(range(1, n, 2)) + list(range(0, n, 2)),
        }
        
        # Add rail fence (zigzag) with different numbers of rails
        for rails in [2, 3, 5, 7, 11, 13]:
            if rails >= n: continue
            # Generate zigzag reading order
            rows = [[] for _ in range(rails)]
            row, direction = 0, 1
            for i in range(n):
                rows[row].append(i)
                if row == 0: direction = 1
                elif row == rails - 1: direction = -1
                row += direction
            order = []
            for r in rows: order.extend(r)
            reading_orders[f'zigzag_{rails}'] = order
        
        # Add columnar transposition
        for ncols in [7, 11, 13, 17, 19, 23, 29]:
            if ncols >= n: continue
            order = []
            for col in range(ncols):
                for row in range(0, n, ncols):
                    if row + col < n:
                        order.append(row + col)
            reading_orders[f'columnar_{ncols}'] = order
        
        for order_name, order in reading_orders.items():
            if len(order) != n:
                continue
            
            reordered = [cipher[order[i]] for i in range(n)]
            
            # Check IoC of reordered text (pure transposition)
            ioc = calc_ioc(reordered)  # Same as original, transposition preserves freq
            
            # Apply totient stream to reordered
            for mode_name, mode_func in modes.items():
                plain = [mode_func(reordered[i], TOTIENTS[i]) for i in range(n)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"  Page {page_num} {order_name}+totient/{mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    Text: {text[:150]}")
    
    # ==================== TEST 6: Cumulative/progressive key ====================
    print("\n" + "=" * 80)
    print("TEST 6: Progressive/cumulative key transformations")
    print("Key depends on previous plaintext or ciphertext values")
    print("=" * 80)
    
    for page_num in target_pages[:5]:
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        
        # Progressive: key[i] = sum(cipher[0:i]) mod 29
        for mode_name, mode_func in modes.items():
            cum_sum = 0
            plain = []
            for i, c in enumerate(cipher):
                plain.append(mode_func(c, cum_sum % 29))
                cum_sum += c
            
            ioc = calc_ioc(plain)
            if ioc > 1.2:
                text = decode_to_runeglish(plain)
                s = score_text(text)
                print(f"  Page {page_num} cumsum_cipher/{mode_name}: IoC={ioc:.3f} score={s}")
                print(f"    Text: {text[:150]}")
        
        # Progressive: key[i] = product(cipher[0:i]) mod 29
        for mode_name, mode_func in modes.items():
            cum_prod = 1
            plain = []
            for i, c in enumerate(cipher):
                plain.append(mode_func(c, cum_prod % 29))
                cum_prod = (cum_prod * max(c, 1)) % 29  # Avoid multiplying by 0
            
            ioc = calc_ioc(plain)
            if ioc > 1.2:
                text = decode_to_runeglish(plain)
                s = score_text(text)
                print(f"  Page {page_num} cumprod_cipher/{mode_name}: IoC={ioc:.3f} score={s}")
                print(f"    Text: {text[:150]}")
        
        # Another: key[i] = cipher[i-1] XOR cipher[i-2] (position-dependent feedback)
        for mode_name, mode_func in modes.items():
            plain = [mode_func(cipher[0], 0)]  # First char with key=0
            for i in range(1, n):
                key = (cipher[i-1] + (cipher[i-2] if i >= 2 else 0)) % 29
                plain.append(mode_func(cipher[i], key))
            
            ioc = calc_ioc(plain)
            if ioc > 1.2:
                text = decode_to_runeglish(plain)
                s = score_text(text)
                print(f"  Page {page_num} feedback/{mode_name}: IoC={ioc:.3f} score={s}")
                print(f"    Text: {text[:150]}")
    
    # ==================== TEST 7: Beaufort with page number as part of key ====================
    print("\n" + "=" * 80)
    print("TEST 7: Page number incorporated into key stream")
    print("key[i] = f(i, page_number)")
    print("=" * 80)
    
    for page_num in sorted(pages.keys()):
        cipher = pages[page_num]['shifts']
        n = len(cipher)
        
        # key = totient(prime[i + page_offset]) for various page-derived offsets
        for offset_func_name, offset in [
            ('page_num', page_num),
            ('page_num_squared', page_num * page_num),
            ('prime[page]', PRIMES[page_num] if page_num < len(PRIMES) else page_num),
            ('totient(page)', (PRIMES[page_num]-1) if page_num < len(PRIMES) else page_num),
        ]:
            for mode_name, mode_func in modes.items():
                key_stream = TOTIENTS[offset:offset+n]
                if len(key_stream) < n:
                    key_stream = TOTIENTS[:n]  # Fallback
                
                plain = [mode_func(cipher[i], key_stream[i]) for i in range(n)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode_to_runeglish(plain)
                    s = score_text(text)
                    print(f"  Page {page_num} totient+{offset_func_name}/{mode_name}: IoC={ioc:.3f} score={s}")
                    print(f"    Text: {text[:150]}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if best_results:
        best_results.sort(key=lambda x: x.get('ioc', 0), reverse=True)
        print(f"\nTop results:")
        for i, r in enumerate(best_results[:15]):
            print(f"  {i+1}. Page {r['page']}: IoC={r['ioc']:.3f} score={r['score']} "
                  f"[{r.get('test','')}/{r.get('stream','')}/{r.get('mode','')}]")
            print(f"     {r['text'][:120]}")
    else:
        print("No compelling results found across all novel approaches.")
    
    print("\nDone.")

if __name__ == '__main__':
    main()
