#!/usr/bin/env python3
"""
Mathematical Sequence Cipher Tester for Liber Primus Pages 18-54
================================================================
P32's number grid encodes Fibonacci via 3301-prime mapping.
This strongly hints that mathematical sequences may be the keystream.

Tests: Fibonacci, primes, totient, triangular, pi/e digits, etc.
"""
import sys, os, math, itertools
from pathlib import Path
from collections import Counter

# ── Gematria Primus ──────────────────────────────────────────────
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,
    '\u16B7':6,'\u16B9':7,'\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,
    '\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,
    '\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,
    '\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
           'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
# English frequency order for scoring
ENG_FREQ = {'A':8.2,'B':1.5,'C':2.8,'D':4.3,'E':12.7,'F':2.2,'G':2.0,
            'H':6.1,'I':7.0,'J':0.15,'K':0.77,'L':4.0,'M':2.4,'N':6.7,
            'O':7.5,'P':1.9,'Q':0.095,'R':6.0,'S':6.3,'T':9.1,'U':2.8,
            'V':0.98,'W':2.4,'X':0.15,'Y':2.0,'Z':0.074}
# GP frequency targets (approximate)
GP_FREQ = {0:2.2,1:2.8,2:3.7,3:7.5,4:6.0,5:2.8,6:2.0,7:2.4,8:6.1,
           9:6.7,10:7.0,11:0.15,12:0.5,13:1.9,14:0.15,15:6.3,16:9.1,
           17:1.5,18:12.7,19:2.4,20:4.0,21:0.5,22:0.5,23:4.3,24:8.2,
           25:0.5,26:2.0,27:0.5,28:0.5}

def load_runes(page_num):
    """Load rune indices from a page."""
    base = Path(__file__).parent.parent / "LiberPrimus" / "pages" / f"page_{page_num:02d}"
    rune_file = base / "runes.txt"
    if not rune_file.exists():
        return []
    text = rune_file.read_text(encoding='utf-8')
    indices = []
    for ch in text:
        if ch in GP:
            indices.append(GP[ch])
    return indices

def score_english(indices):
    """Score how English-like a decryption is (higher = better)."""
    if not indices:
        return 0
    total = len(indices)
    counts = Counter(indices)
    # Chi-squared against GP frequency distribution
    chi2 = 0
    for i in range(29):
        observed = counts.get(i, 0)
        expected = GP_FREQ.get(i, 1.0) * total / 100.0
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    # Lower chi2 = better fit; convert to positive score
    score = max(0, 200 - chi2)
    return score

def ioc(indices):
    """Index of Coincidence."""
    if len(indices) < 2:
        return 0
    n = len(indices)
    counts = Counter(indices)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1)) * 29  # Normalized for 29-letter alphabet

def decrypt(cipher, key_seq, mode='SUB'):
    """Decrypt cipher indices with key sequence."""
    result = []
    for i, c in enumerate(cipher):
        k = key_seq[i % len(key_seq)] if isinstance(key_seq, list) else key_seq[i]
        if mode == 'SUB':
            result.append((c - k) % 29)
        elif mode == 'ADD':
            result.append((c + k) % 29)
        elif mode == 'BEAU':
            result.append((k - c) % 29)
    return result

def decrypt_fskip(cipher, key_seq, mode='SUB'):
    """Decrypt with F-skip: when cipher=0 and result would be F(0), output F and don't advance key."""
    result = []
    ki = 0
    for c in cipher:
        if c == 0:  # F rune
            result.append(0)
            # Don't advance key
        else:
            k = key_seq[ki % len(key_seq)] if isinstance(key_seq, list) else key_seq[ki]
            if mode == 'SUB':
                result.append((c - k) % 29)
            elif mode == 'ADD':
                result.append((c + k) % 29)
            elif mode == 'BEAU':
                result.append((k - c) % 29)
            ki += 1
    return result

def indices_to_text(indices):
    """Convert GP indices to runeglish text."""
    return ''.join(IDX2LAT[i] for i in indices)

# ── Mathematical Sequences ──────────────────────────────────────

def fibonacci_seq(n):
    """Generate first n Fibonacci numbers."""
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

def primes_sieve(n):
    """Generate primes up to n using sieve."""
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]

def prime_list(count):
    """Get first 'count' primes."""
    primes = []
    candidate = 2
    while len(primes) < count:
        if all(candidate % p != 0 for p in primes if p * p <= candidate):
            primes.append(candidate)
        candidate += 1
    return primes

def totient(n):
    """Euler's totient function."""
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

def triangular_seq(n):
    """Generate first n triangular numbers."""
    return [i*(i+1)//2 for i in range(n)]

def pi_digits(n):
    """Generate digits of pi using a spigot-like approach."""
    # Use mpmath for precision if available, otherwise use string constant
    PI_STR = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989"
    return [int(d) for d in PI_STR[:n]]

def e_digits(n):
    """Generate digits of e."""
    E_STR = "27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190115738341879307021540891499348841675092447614606680822648001684774118537423454424371075390777449920695517027618386062613313845830007520449338265602976067371132007093287091274437470472306969772093101416928368190255151086574637721112523897844250569536967707854499699679468644549059879316368892300987931277361782154249992295763514822082698951936680331825288693984964651058209392398294887933203625094431173012381970684161403970198376793206832823764648042953118023287825098194558153017567173613320698112509961818815930416903515988885193458072738667385894228792284998920868058257492796104841984443634632449684875602336248270419786232090021609902353043699418491463140934317381436405462531520961836908887070167683964243781405927145635490613031072085103837505101157477041718986106873969655212671546889570350354"
    return [int(d) for d in E_STR[:n]]

def golden_ratio_digits(n):
    """Generate digits of golden ratio phi."""
    PHI_STR = "16180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374847540880753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752087668925017116962070322210432162695486262963136144381497587012203408058879544547492461856953648644492410443207713449470495903998111153224318265847117532250843684731600340378766227579162164891855993726975529067772266012022029696935762259085488767013095813753395522390363226900413513186015117850698901104851447363498033254924301609701983219777560148907787459078831672254400769455071476802869753562197653844208756701743390805454782861093906960327088641270921171640016200068120175916009658335942007479536782893992327322500281001160939117985607702625468699100429927028662808798127260200013729865025558515610510929369382806713816280564734769364011128685199953184847463117403934353005184923709441503287957015621791810504777096737177085485091672432527522851481810645746401791972405299758908060578165082698873442053938324329668082906844803714710728400362038942688407505710709339093883823515150825044963856141094627478873"
    return [int(d) for d in PHI_STR[:n]]

# ── Main Test Engine ──────────────────────────────────────────────

def test_sequence_cipher(cipher, seq_name, sequence_gen, max_offset=100, modes=None, fskip_variants=True):
    """Test a mathematical sequence as keystream."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    best_results = []
    
    for offset in range(max_offset):
        # Generate sequence starting at offset
        needed = n + offset + 10
        try:
            raw_seq = sequence_gen(needed)
        except:
            break
        
        key_stream = [raw_seq[offset + i] % 29 for i in range(n)]
        
        for mode in modes:
            # Standard decrypt
            plain = decrypt(cipher, key_stream, mode)
            sc = score_english(plain)
            ic = ioc(plain)
            
            if sc > 80 or ic > 1.2:
                text = indices_to_text(plain[:60])
                best_results.append((sc, ic, f"{seq_name} offset={offset} {mode}", text))
            
            # F-skip variant
            if fskip_variants:
                plain_fs = decrypt_fskip(cipher, key_stream, mode)
                sc_fs = score_english(plain_fs)
                ic_fs = ioc(plain_fs)
                if sc_fs > 80 or ic_fs > 1.2:
                    text_fs = indices_to_text(plain_fs[:60])
                    best_results.append((sc_fs, ic_fs, f"{seq_name} offset={offset} {mode} F-skip", text_fs))
    
    return best_results

def test_totient_cipher(cipher, max_offset=200, modes=None, fskip_variants=True):
    """Test Euler totient-based cipher (known to work for P55/P73)."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    primes = prime_list(n + max_offset + 10)
    best_results = []
    
    for offset in range(max_offset):
        key_stream = [(primes[offset + i] - 1) % 29 for i in range(n)]  # φ(p) = p-1 for primes
        
        for mode in modes:
            plain = decrypt(cipher, key_stream, mode)
            sc = score_english(plain)
            ic = ioc(plain)
            
            if sc > 80 or ic > 1.2:
                text = indices_to_text(plain[:60])
                best_results.append((sc, ic, f"Totient prime_offset={offset} {mode}", text))
            
            if fskip_variants:
                plain_fs = decrypt_fskip(cipher, key_stream, mode)
                sc_fs = score_english(plain_fs)
                ic_fs = ioc(plain_fs)
                if sc_fs > 80 or ic_fs > 1.2:
                    text_fs = indices_to_text(plain_fs[:60])
                    best_results.append((sc_fs, ic_fs, f"Totient prime_offset={offset} {mode} F-skip", text_fs))
    
    return best_results

def test_fibonacci_mod29(cipher, max_offset=500, modes=None, fskip_variants=True):
    """Test Fibonacci(n) mod 29 as keystream - the P32 grid clue!"""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    # Generate enough Fibonacci numbers
    fib = fibonacci_seq(n + max_offset + 10)
    best_results = []
    
    for offset in range(max_offset):
        key_stream = [fib[offset + i] % 29 for i in range(n)]
        
        for mode in modes:
            plain = decrypt(cipher, key_stream, mode)
            sc = score_english(plain)
            ic = ioc(plain)
            
            if sc > 80 or ic > 1.2:
                text = indices_to_text(plain[:60])
                best_results.append((sc, ic, f"Fibonacci offset={offset} {mode}", text))
            
            if fskip_variants:
                plain_fs = decrypt_fskip(cipher, key_stream, mode)
                sc_fs = score_english(plain_fs)
                ic_fs = ioc(plain_fs)
                if sc_fs > 80 or ic_fs > 1.2:
                    text_fs = indices_to_text(plain_fs[:60])
                    best_results.append((sc_fs, ic_fs, f"Fibonacci offset={offset} {mode} F-skip", text_fs))
    
    return best_results

def test_prime_index_cipher(cipher, max_offset=200, modes=None):
    """Test prime ordinal index mod 29 as keystream."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    best_results = []
    
    for offset in range(max_offset):
        key_stream = [(offset + i) % 29 for i in range(n)]  # Simple linear
        # Not interesting; let's use prime ordinal of sequential primes
        pass
    
    # Actually: key[i] = prime_index(prime(offset+i)) mod 29 = (offset+i) mod 29
    # That's just a linear sequence. Let's instead try:
    # key[i] = i-th prime mod 29
    primes = prime_list(n + max_offset + 10)
    for offset in range(max_offset):
        key_stream = [primes[offset + i] % 29 for i in range(n)]
        
        for mode in modes:
            plain = decrypt(cipher, key_stream, mode)
            sc = score_english(plain)
            ic = ioc(plain)
            
            if sc > 80 or ic > 1.2:
                text = indices_to_text(plain[:60])
                best_results.append((sc, ic, f"Prime_mod29 offset={offset} {mode}", text))
    
    return best_results

def test_digit_ciphers(cipher, max_offset=200, modes=None):
    """Test pi, e, phi digits as keystream."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    best_results = []
    
    digit_sources = [
        ("Pi_digits", pi_digits),
        ("E_digits", e_digits),
        ("Phi_digits", golden_ratio_digits),
    ]
    
    for name, gen_fn in digit_sources:
        needed = n + max_offset + 10
        try:
            digits = gen_fn(needed)
        except:
            continue
        
        for offset in range(min(max_offset, len(digits) - n)):
            key_stream = [digits[offset + i] % 29 for i in range(n)]
            
            for mode in modes:
                plain = decrypt(cipher, key_stream, mode)
                sc = score_english(plain)
                ic = ioc(plain)
                
                if sc > 80 or ic > 1.2:
                    text = indices_to_text(plain[:60])
                    best_results.append((sc, ic, f"{name} offset={offset} {mode}", text))
    
    return best_results

def test_3301_sequences(cipher, max_offset=100, modes=None):
    """Test 3301-related sequences as keystream."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    best_results = []
    
    # 1. (3301 * i + c) mod 29 for various c
    for c in range(29):
        key_stream = [(3301 * (i + 1) + c) % 29 for i in range(n)]
        for mode in modes:
            plain = decrypt(cipher, key_stream, mode)
            sc = score_english(plain)
            ic = ioc(plain)
            if sc > 80 or ic > 1.2:
                text = indices_to_text(plain[:60])
                best_results.append((sc, ic, f"3301*i+{c} mod29 {mode}", text))
    
    # 2. 3301^i mod 29
    key_stream = [pow(3301, i, 29) for i in range(n)]
    for mode in modes:
        plain = decrypt(cipher, key_stream, mode)
        sc = score_english(plain)
        ic = ioc(plain)
        if sc > 80 or ic > 1.2:
            text = indices_to_text(plain[:60])
            best_results.append((sc, ic, f"3301^i mod29 {mode}", text))
    
    return best_results

def test_combined_fib_prime(cipher, modes=None):
    """Test combinations: Fibonacci index of primes, prime-indexed Fibonacci, etc."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    best_results = []
    primes = prime_list(n + 100)
    fib = fibonacci_seq(max(primes[:n+100]) + 10 if primes else n + 100)
    
    # Fibonacci(prime(i)) mod 29
    key_stream = []
    for i in range(n):
        p = primes[i]
        if p < len(fib):
            key_stream.append(fib[p] % 29)
        else:
            key_stream.append(0)
    
    for mode in modes:
        plain = decrypt(cipher, key_stream, mode)
        sc = score_english(plain)
        ic = ioc(plain)
        if sc > 80 or ic > 1.2:
            text = indices_to_text(plain[:60])
            best_results.append((sc, ic, f"Fib(prime(i)) mod29 {mode}", text))
    
    # Prime(Fibonacci(i)) mod 29 - only for small Fibonacci values
    fib_small = fibonacci_seq(min(n, 50))
    for offset in range(10):
        key_stream = []
        for i in range(n):
            fi = fib_small[i % len(fib_small)]
            if fi < len(primes):
                key_stream.append(primes[fi] % 29)
            else:
                key_stream.append(0)
        for mode in modes:
            plain = decrypt(cipher, key_stream, mode)
            sc = score_english(plain)
            ic = ioc(plain)
            if sc > 80 or ic > 1.2:
                text = indices_to_text(plain[:60])
                best_results.append((sc, ic, f"Prime(Fib(i)) mod29 {mode}", text))
    
    return best_results

def test_cumulative_sequences(cipher, modes=None):
    """Test cumulative (running sum) sequences."""
    if modes is None:
        modes = ['SUB', 'ADD', 'BEAU']
    
    n = len(cipher)
    best_results = []
    
    # Cumulative sum of primes mod 29
    primes = prime_list(n + 10)
    cum_sum = [0] * n
    cum_sum[0] = primes[0]
    for i in range(1, n):
        cum_sum[i] = cum_sum[i-1] + primes[i]
    
    key_stream = [s % 29 for s in cum_sum]
    for mode in modes:
        plain = decrypt(cipher, key_stream, mode)
        sc = score_english(plain)
        ic = ioc(plain)
        if sc > 80 or ic > 1.2:
            text = indices_to_text(plain[:60])
            best_results.append((sc, ic, f"CumulativePrimes mod29 {mode}", text))
    
    # Cumulative Fibonacci mod 29
    fib = fibonacci_seq(n + 10)
    cum_fib = [0] * n
    cum_fib[0] = fib[0]
    for i in range(1, n):
        cum_fib[i] = cum_fib[i-1] + fib[i]
    
    key_stream = [s % 29 for s in cum_fib]
    for mode in modes:
        plain = decrypt(cipher, key_stream, mode)
        sc = score_english(plain)
        ic = ioc(plain)
        if sc > 80 or ic > 1.2:
            text = indices_to_text(plain[:60])
            best_results.append((sc, ic, f"CumulativeFib mod29 {mode}", text))
    
    return best_results

# ── Main ──────────────────────────────────────────────────────────

def main():
    # Test pages - focus on largest unsolved pages first
    test_pages = [32, 44, 50, 40, 34, 36, 38, 42, 46, 48, 52, 54,
                  18, 20, 22, 24, 26, 28, 30, 
                  21, 23, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53]
    
    all_results = []
    
    for page in test_pages:
        cipher = load_runes(page)
        if not cipher or len(cipher) < 10:
            continue
        
        print(f"\n{'='*70}")
        print(f"PAGE {page:02d} ({len(cipher)} runes)")
        print(f"{'='*70}")
        
        page_results = []
        
        # 1. Fibonacci mod 29 (P32 clue! - test many offsets)
        print(f"  Testing Fibonacci mod 29 (500 offsets)...")
        results = test_fibonacci_mod29(cipher, max_offset=500)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # 2. Totient/prime cipher (known working for P55/P73)
        print(f"  Testing Totient cipher (200 offsets)...")
        results = test_totient_cipher(cipher, max_offset=200)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # 3. Prime values mod 29
        print(f"  Testing Prime mod 29 (200 offsets)...")
        results = test_prime_index_cipher(cipher, max_offset=200)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # 4. Pi, e, phi digits
        print(f"  Testing Pi/E/Phi digits (200 offsets)...")
        results = test_digit_ciphers(cipher, max_offset=200)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # 5. 3301-related sequences
        print(f"  Testing 3301 sequences...")
        results = test_3301_sequences(cipher)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # 6. Combined Fibonacci+Prime
        print(f"  Testing combined Fib+Prime...")
        results = test_combined_fib_prime(cipher)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # 7. Cumulative sequences
        print(f"  Testing cumulative sequences...")
        results = test_cumulative_sequences(cipher)
        page_results.extend(results)
        if results:
            print(f"    Found {len(results)} hits!")
        
        # Report best results for this page
        if page_results:
            page_results.sort(key=lambda x: (-x[0], -x[1]))
            print(f"\n  *** TOP RESULTS FOR PAGE {page:02d} ***")
            for sc, ic, desc, text in page_results[:10]:
                print(f"    Score={sc:.1f} IoC={ic:.3f} | {desc}")
                print(f"      Text: {text}")
            all_results.extend([(page, sc, ic, desc, text) for sc, ic, desc, text in page_results])
        else:
            print(f"  No hits above threshold (score>80 or IoC>1.2)")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"GLOBAL SUMMARY - ALL PAGES")
    print(f"{'='*70}")
    
    if all_results:
        all_results.sort(key=lambda x: (-x[1], -x[2]))
        for page, sc, ic, desc, text in all_results[:30]:
            print(f"  P{page:02d} Score={sc:.1f} IoC={ic:.3f} | {desc}")
            print(f"        {text}")
    else:
        print("  NO RESULTS FOUND above thresholds.")
    
    print(f"\nTotal results: {len(all_results)}")

if __name__ == '__main__':
    main()
