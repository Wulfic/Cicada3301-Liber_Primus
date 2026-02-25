#!/usr/bin/env python3
"""
Mathematical Constants as Key Streams for Liber Primus
======================================================
Tests digits of pi, e, phi, sqrt(2), sqrt(3) etc.
in various bases (10 mod 29, base 29, paired digits)
as potential cipher key streams.

Also tests: Fibonacci with page-specific seeds,
digit sequences of mathematical constants,
and Collatz from page-specific starting values.
"""

import os, sys, math
from collections import Counter
from decimal import Decimal, getcontext

# High precision
getcontext().prec = 5000

RUNE_TO_SHIFT = {
    '\u16a0': 0, '\u16a2': 1, '\u16a6': 2, '\u16a9': 3, '\u16b1': 4,
    '\u16b3': 5, '\u16b7': 6, '\u16b9': 7, '\u16bb': 8, '\u16be': 9,
    '\u16c1': 10, '\u16c2': 11, '\u16c7': 12, '\u16c8': 13, '\u16c9': 14,
    '\u16cb': 15, '\u16cf': 16, '\u16d2': 17, '\u16d6': 18, '\u16d7': 19,
    '\u16da': 20, '\u16dd': 21, '\u16df': 22, '\u16de': 23, '\u16aa': 24,
    '\u16ab': 25, '\u16a3': 26, '\u16e1': 27, '\u16e0': 28, '\u16c4': 11
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

def decode(shifts):
    return ''.join(SHIFT_TO_ENGLISH.get(s, '?') for s in shifts)

def score_text(text):
    t = text.upper()
    bigrams = ['TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','ES','OR',
               'TE','ED','IS','IT','AL','AR','ST','TO','HA','OU','SE','WH']
    score = sum(t.count(bg) * 10 for bg in bigrams)
    words = ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','WAS','ONE','OUR',
             'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','SOME',
             'WHEN','WHAT','THERE','WHICH','SHALL','EACH','FIND','WISDOM','TRUTH']
    for w in words: score += t.count(w) * len(w) * 5
    return score

def sieve_primes(n):
    primes = []
    c = 2
    while len(primes) < n:
        if all(c % p for p in primes if p*p <= c):
            primes.append(c)
        c += 1
    return primes

def parse_shifts(rune_text):
    return [RUNE_TO_SHIFT[ch] for ch in rune_text if ch in RUNE_TO_SHIFT]

def load_page(pages_dir, p):
    path = os.path.join(pages_dir, f'page_{p:02d}', 'runes.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None

# Generate pi digits using mpmath or manually
def pi_digits(n_digits):
    """Return first n_digits of pi after decimal point."""
    try:
        from mpmath import mp
        mp.dps = n_digits + 10
        s = mp.nstr(mp.pi, n_digits + 2, strip_zeros=False)
        # Remove '3.'
        digits = [int(c) for c in s if c.isdigit()]
        return digits[:n_digits]
    except ImportError:
        # Fallback: hardcoded first 200 digits of pi
        pi_str = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491"
        return [int(c) for c in pi_str[:n_digits]]

def e_digits(n_digits):
    """Return first n_digits of e."""
    try:
        from mpmath import mp
        mp.dps = n_digits + 10
        s = mp.nstr(mp.e, n_digits + 2, strip_zeros=False)
        digits = [int(c) for c in s if c.isdigit()]
        return digits[:n_digits]
    except ImportError:
        e_str = "27182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218174135966290435729003342952605956307381323286279434907632338298807531952510190115738341879307021540891499348841675092447614606680822648001684774118537423454424371075390777449920695517027618386062613313845830007520449338265602976067371132007093287091274437470472306969772093101416928368190255151086574637721112523897844250569536967707854499699679468644549059879316368892300987931277361782154249992295763514822082698951936680331825288693984964651058209392398294887933203625094431173012381970684161403970198376793206832823764648042953118023287825098194558153017567173613320698112509961818815930416903515988885193458072738667385894228792284998920868058257492796104841984443634632449684875602336248270419786232090021609902353043699418491463140934317381436405462531520961836908887070167683964243781405927145635490613031072085103837505101157477041718986106873969655212671546889570350354"
        return [int(c) for c in e_str[:n_digits]]

def sqrt2_digits(n_digits):
    """Return first n_digits of sqrt(2)."""
    try:
        from mpmath import mp
        mp.dps = n_digits + 10
        s = mp.nstr(mp.sqrt(2), n_digits + 2, strip_zeros=False)
        digits = [int(c) for c in s if c.isdigit()]
        return digits[:n_digits]
    except ImportError:
        s = "14142135623730950488016887242096980785696718753769480731766797379907324784621070388503875343276415727350138462309122970249248360558507372126441214970999358314132226659275055927557999505011527820605714701095599716059702745345968461428740648873113526398066501130024042068840674461339540504614413471461015737835141011269930812288684542665204119310295123584382831851429808078048018694377096282656737554904131892360567842527563127468725474598731616152888089518557959750554421954842943776759338223598895734803014523685622157665855779087682612278937700609185825507673574568528912072484899050068522975502429327115892082705814924277286843445548073790849332769832238413191536080735715773287925594279516263459108005260276903262547903801928299458920576107312048016103085004990078107752217588244206827451768116845916787476212600530458218685174752900262479665760047825249719812505497659401519825412666658284560449914478329803309417078110530035946044416157918159478118567026057359152885223169929981079991919072748694631929159696875744407443152805655935752646674498191380363899218017268803752129978440556387521796753399303498026165879735993146845965722976613233989098651643965117674613680742279768009852011651703908145735084270059786688825696682027090621805"
        return [int(c) for c in s[:n_digits]]

def phi_digits(n_digits):
    """Return first n_digits of golden ratio phi."""
    try:
        from mpmath import mp
        mp.dps = n_digits + 10
        s = mp.nstr(mp.phi, n_digits + 2, strip_zeros=False)
        digits = [int(c) for c in s if c.isdigit()]
        return digits[:n_digits]
    except ImportError:
        s = "16180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374847540880753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752087668925017116962070322210432162695486262963136144381497587012203408058879544547492461856953648644492410443207713449470495658467885098743394422125448770664780915884607499887124007652170575179788341662562494075890697040002812104276217711177780531531714101170466659914669798731761356006708748071013179523689427521948435305678300228785699782977834784587822891109762500302696156170025046433824377648610283831268330372429267526311653392473167111211588186385133162038400522216579128667529465490681131715993432359734949850904094762132229810172610705"
        return [int(c) for c in s[:n_digits]]

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(base_dir)
    pages_dir = os.path.join(repo_dir, 'LiberPrimus', 'pages')
    
    PRIMES = sieve_primes(3000)
    
    modes = {
        'sub': lambda c, k: (c - k) % 29,
        'beaufort': lambda c, k: (k - c) % 29,
        'add': lambda c, k: (c + k) % 29,
    }
    
    # Load pages
    pages = {}
    for p in range(18, 55):
        rt = load_page(pages_dir, p)
        if rt:
            shifts = parse_shifts(rt)
            if len(shifts) > 20:
                pages[p] = shifts
    
    print("=" * 80)
    print("MATHEMATICAL CONSTANTS AS KEY STREAMS")
    print("=" * 80)
    
    # Generate digit streams
    N = 2500  # enough for largest pages
    
    pi_d = pi_digits(N)
    e_d = e_digits(N)
    sqrt2_d = sqrt2_digits(N)
    phi_d = phi_digits(N)
    
    print(f"Pi first 10 digits: {pi_d[:10]}")
    print(f"E first 10 digits: {e_d[:10]}")
    print(f"Sqrt2 first 10: {sqrt2_d[:10]}")
    print(f"Phi first 10: {phi_d[:10]}")
    
    # Build key streams from digits
    key_streams = {}
    
    for name, digits in [('pi', pi_d), ('e', e_d), ('sqrt2', sqrt2_d), ('phi', phi_d)]:
        # Method 1: single digits mod 29 (0-9 only, limited range)
        key_streams[f'{name}_d1'] = [d % 29 for d in digits]
        
        # Method 2: pairs of digits as 2-digit numbers mod 29
        paired = []
        for i in range(0, len(digits)-1, 2):
            paired.append((digits[i]*10 + digits[i+1]) % 29)
        key_streams[f'{name}_d2'] = paired
        
        # Method 3: triples of digits mod 29
        tripled = []
        for i in range(0, len(digits)-2, 3):
            tripled.append((digits[i]*100 + digits[i+1]*10 + digits[i+2]) % 29)
        key_streams[f'{name}_d3'] = tripled
        
        # Method 4: sliding window pairs mod 29
        sliding = []
        for i in range(len(digits)-1):
            sliding.append((digits[i]*10 + digits[i+1]) % 29)
        key_streams[f'{name}_slide2'] = sliding
        
        # Method 5: XOR consecutive digits mod 29
        xor_stream = []
        for i in range(len(digits)-1):
            xor_stream.append((digits[i] ^ digits[i+1]) % 29)
        key_streams[f'{name}_xor'] = xor_stream
    
    # Method 6: Convert constants to base 29
    # pi in base 29: we convert the fractional part
    # pi = 3.14159... in base 29
    # fractional part = 0.14159... 
    # multiply by 29 repeatedly to get base-29 digits
    for name, digits in [('pi', pi_d), ('e', e_d), ('sqrt2', sqrt2_d), ('phi', phi_d)]:
        # Reconstruct the number from decimal digits
        # First digit is the integer part
        int_part = digits[0]
        # Build fractional part
        frac_digits = digits[1:1000]  # Use 1000 decimal digits
        
        # Convert to base 29
        # frac = sum(d * 10^(-i) for i, d in enumerate(frac_digits, 1))
        # Instead, work with integers: frac_val = integer formed by digits / 10^len
        base29 = []
        # Use Decimal for precision
        getcontext().prec = 1500
        frac_str = "0." + "".join(str(d) for d in frac_digits[:1000])
        frac = Decimal(frac_str)
        
        for _ in range(N):
            frac *= 29
            digit = int(frac)
            base29.append(digit % 29)
            frac -= digit
        
        key_streams[f'{name}_base29'] = base29
    
    print(f"\nGenerated {len(key_streams)} key streams")
    
    # Test all streams on all pages
    all_hits = []
    
    for stream_name, stream in key_streams.items():
        for page_num in sorted(pages.keys()):
            cipher = pages[page_num]
            n = len(cipher)
            if len(stream) < n: continue
            
            for mode_name, mode_func in modes.items():
                plain = [mode_func(cipher[i], stream[i]) for i in range(n)]
                ioc = calc_ioc(plain)
                if ioc > 1.3:
                    text = decode(plain)
                    s = score_text(text)
                    all_hits.append((ioc, s, page_num, stream_name, mode_name, text[:150]))
    
    if all_hits:
        all_hits.sort(key=lambda x: (x[0], x[1]), reverse=True)
        print(f"\nTop results (IoC > 1.3):")
        for i, (ioc, s, pn, sname, mode, text) in enumerate(all_hits[:15]):
            print(f"  {i+1}. P{pn} {sname}/{mode}: IoC={ioc:.3f} score={s}")
            print(f"     {text[:120]}")
    else:
        print("\nNo results with IoC > 1.3")
    
    # ==================== OFFSET SCAN ON CONSTANTS ====================
    print("\n" + "=" * 80)
    print("OFFSET SCAN: Mathematical constants with various starting offsets")
    print("Maybe the stream starts at a specific offset, not position 0")
    print("=" * 80)
    
    # Only test base29 streams and d2 streams (most promising)
    test_streams = {k: v for k, v in key_streams.items() if 'base29' in k or 'd2' in k}
    
    # Focus on largest pages for signal
    target_pages = sorted(pages.keys(), key=lambda p: len(pages[p]), reverse=True)[:5]
    
    for stream_name, full_stream in test_streams.items():
        for page_num in target_pages:
            cipher = pages[page_num]
            n = len(cipher)
            
            best_ioc = 0
            best_offset = 0
            best_mode = ''
            
            max_offset = min(len(full_stream) - n, 500)
            if max_offset < 1: continue
            
            for offset in range(max_offset):
                stream = full_stream[offset:offset+n]
                for mode_name, mode_func in modes.items():
                    plain = [mode_func(cipher[i], stream[i]) for i in range(n)]
                    ioc = calc_ioc(plain)
                    if ioc > best_ioc:
                        best_ioc = ioc
                        best_offset = offset
                        best_mode = mode_name
            
            if best_ioc > 1.15:
                stream = full_stream[best_offset:best_offset+n]
                mode_func = modes[best_mode]
                plain = [mode_func(cipher[i], stream[i]) for i in range(n)]
                text = decode(plain)
                s = score_text(text)
                print(f"  P{page_num} {stream_name} offset={best_offset} {best_mode}: IoC={best_ioc:.3f} score={s}")
                print(f"    {text[:120]}")
    
    # ==================== FIBONACCI WITH PAGE-SPECIFIC SEEDS ====================
    print("\n" + "=" * 80)
    print("FIBONACCI WITH VARIOUS SEEDS")
    print("fib[0]=a, fib[1]=b, fib[n]=fib[n-1]+fib[n-2] mod 29")
    print("=" * 80)
    
    target_pages = sorted(pages.keys(), key=lambda p: len(pages[p]), reverse=True)[:5]
    
    for page_num in target_pages:
        cipher = pages[page_num]
        n = len(cipher)
        best_ioc = 0
        best_info = None
        
        for a in range(29):
            for b in range(29):
                fib = [a, b]
                for _ in range(n):
                    fib.append((fib[-1] + fib[-2]) % 29)
                
                for mode_name, mode_func in modes.items():
                    plain = [mode_func(cipher[i], fib[i]) for i in range(n)]
                    ioc = calc_ioc(plain)
                    if ioc > 1.35:
                        text = decode(plain)
                        s = score_text(text)
                        if ioc > best_ioc:
                            best_ioc = ioc
                            best_info = (ioc, s, a, b, mode_name, text[:120])
        
        if best_info:
            ioc, s, a, b, mode, text = best_info
            print(f"  P{page_num} fib({a},{b}) {mode}: IoC={ioc:.3f} score={s}")
            print(f"    {text[:120]}")
        else:
            print(f"  P{page_num}: No Fibonacci hits")
    
    # ==================== COLLATZ-BASED STREAMS ====================
    print("\n" + "=" * 80)
    print("COLLATZ SEQUENCE STARTING VALUES")
    print("=" * 80)
    
    target_pages = sorted(pages.keys(), key=lambda p: len(pages[p]), reverse=True)[:3]
    
    for page_num in target_pages:
        cipher = pages[page_num]
        n = len(cipher)
        best_ioc = 0
        best_info = None
        
        for start in range(1, 5000):
            # Generate Collatz sequence
            collatz = []
            x = start
            for _ in range(n + 10):
                collatz.append(x % 29)
                if x == 1:
                    x = start  # restart cycle
                elif x % 2 == 0:
                    x = x // 2
                else:
                    x = 3 * x + 1
            
            for mode_name, mode_func in modes.items():
                plain = [mode_func(cipher[i], collatz[i]) for i in range(n)]
                ioc = calc_ioc(plain)
                if ioc > best_ioc:
                    best_ioc = ioc
                    if ioc > 1.35:
                        text = decode(plain)
                        s = score_text(text)
                        best_info = (ioc, s, start, mode_name, text[:120])
        
        if best_info:
            ioc, s, start, mode, text = best_info
            print(f"  P{page_num} collatz({start}) {mode}: IoC={ioc:.3f} score={s}")
            print(f"    {text[:120]}")
        else:
            print(f"  P{page_num}: Best Collatz IoC={best_ioc:.3f} (< 1.35)")
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
