"""
Diagnostic & Attack Tool v3 - Fundamentally New Approaches
==========================================================
1. Periodic IoC Analysis (determine cipher type & key length)
2. Kasiski examination (repeated trigrams → key length)
3. Ciphertext autokey attack
4. Deor poem running key on ALL pages
5. 2x2 Hill cipher brute force (on select pages)
6. Difference analysis (consecutive character differences)
"""

import os, sys, math
from collections import Counter
from itertools import product

# ====== GEMATRIA PRIMUS MAPPINGS ======
RUNE_MAP = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28, '\U000016C4': 11  # alt ᛄ
}
LATIN = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]

def load_runes(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Extract only rune characters
    return [RUNE_MAP[c] for c in content if c in RUNE_MAP]

def to_latin(vals):
    return "".join(LATIN[v] for v in vals)

def calc_ioc(vals):
    if len(vals) < 2: return 0
    c = Counter(vals)
    n = len(vals)
    num = sum(v*(v-1) for v in c.values())
    return num / (n * (n-1)) * 29

def english_score(text):
    """Score based on common English digraphs and words."""
    score = 0
    common = ['THE','AND','ING','HER','ERE','ENT','THA','NTH','WAS','ETH',
              'FOR','ARE','BUT','NOT','YOU','ALL','CAN','HIS','ONE','OUR',
              'OUT','DAY','HAD','HAS','HIM','HOW','ITS','MAY','NEW','NOW',
              'OLD','SEE','WAY','WHO','DID','GET','HAS','HER','HIM','HIS',
              'HOW','MAN','MAY','OLD','OUR','OWN','SAY','SHE','THE','TWO',
              'WITH','THAT','THIS','FROM','HAVE','BEEN','SOME','WILL',
              'THEY','EACH','MAKE','LIKE','JUST','OVER','SUCH','TAKE',
              'KNOW','INTO','MOST','THAN','THEM','THEN','WHAT','WHEN',
              'WITHIN','SACRED','PRIMES','DIVINITY','CIPHER','TRUTH']
    upper = text.upper()
    for w in common:
        count = 0
        start = 0
        while True:
            pos = upper.find(w, start)
            if pos == -1: break
            count += 1
            start = pos + 1
        score += count * len(w) * len(w)
    return score

# ====== DEOR POEM TOKENIZATION ======
DEOR_TEXT = """Welund him be wurman wræces cunnade,
anhydig eorl earfoþa dreag,
hæfde him to gesiþþe sorge ond longaþ,
wintercealde wræce; wean oft onfond,
siþþan hine Niðhad on nede legde,
swoncre seonobende on syllan monn.
Þæs ofereode, þisses swa mæg.
Beadohilde ne wæs hyre broþra deaþ
on sefan swa sar swa hyre sylfre þing,
þæt heo gearolice ongieten hæfde
þæt heo eacen wæs; æfre ne meahte
þriste geþencan, hu ymb þæt sceolde.
Þæs ofereode, þisses swa mæg.
We þæt Mæðhilde monge gefrugnon
wurdon grundlease Geates frige,
þæt hi seo sorglufu slæp ealle binom.
Þæs ofereode, þisses swa mæg.
Ðeodric ahte þritig wintra
Mæringa burg; þæt wæs monegum cuþ.
Þæs ofereode, þisses swa mæg.
We geascodan Eormanrices
wylfenne geþoht; ahte wide folc
Gotena rices. Þæt wæs grim cyning.
Sæt secg monig sorgum gebunden,
wean on wenan, wyscte geneahhe
þæt þæs cynerices ofercumen wære.
Þæs ofereode, þisses swa mæg.
Siteð sorgcearig, sælum bedæled,
on sefan sweorceð, sylfum þinceð
þæt sy endeleas earfoða dæl.
Mæg þonne geþencan, þæt geond þas woruld
witig Dryhten wendeþ geneahhe,
eorle monegum are gesceawað,
wislicne blæd, sumum weana dæl.
Þæt ic bi me sylfum secgan wille,
þæt ic hwile wæs Heodeninga scop,
dryhtne dyre. Me wæs Deor noma.
Ahte ic fela wintra folgað tilne,
holdne hlaford, oþþæt Heorrenda nu,
leoðcræftig monn londryht geþah,
þæt me eorla hleo ær gesealde.
Þæs ofereode, þisses swa mæg."""

LATIN_TO_VAL = {
    'F': 0, 'U': 1, 'V': 1, 'TH': 2, 'Þ': 2, 'Ð': 2,
    'O': 3, 'R': 4, 'C': 5, 'K': 5, 'G': 6, 'W': 7, 'H': 8, 'N': 9,
    'I': 10, 'J': 11, 'EO': 12, 'Z': 14, 'S': 15, 'T': 16, 'B': 17,
    'E': 18, 'M': 19, 'L': 20, 'NG': 21, 'OE': 22, 'D': 23,
    'A': 24, 'AE': 25, 'Æ': 25, 'Y': 26, 'IA': 27, 'IO': 27, 'EA': 28
}

def tokenize_oe(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in LATIN_TO_VAL:
            values.append(LATIN_TO_VAL[text[i:i+2]])
            i += 2
        elif text[i] in LATIN_TO_VAL:
            values.append(LATIN_TO_VAL[text[i]])
            i += 1
        else:
            i += 1
    return values

# ====== ANALYSIS FUNCTIONS ======

def periodic_ioc_analysis(shifts, max_period=40):
    """Compute IoC for each column at period N. If a periodic cipher is used,
    the columns should have IoC closer to English (~1.5-1.9)."""
    results = []
    for period in range(1, min(max_period+1, len(shifts)//3)):
        columns_ioc = []
        for col in range(period):
            column = shifts[col::period]
            if len(column) >= 10:
                columns_ioc.append(calc_ioc(column))
        if columns_ioc:
            avg_ioc = sum(columns_ioc) / len(columns_ioc)
            results.append((period, avg_ioc, min(columns_ioc), max(columns_ioc)))
    return results

def kasiski_exam(shifts, min_len=3, max_len=5):
    """Find repeated sequences and compute GCD of their distances."""
    distances = {}
    for seq_len in range(min_len, max_len+1):
        for i in range(len(shifts) - seq_len):
            seq = tuple(shifts[i:i+seq_len])
            for j in range(i+1, len(shifts) - seq_len):
                if tuple(shifts[j:j+seq_len]) == seq:
                    d = j - i
                    if seq not in distances:
                        distances[seq] = []
                    distances[seq].append(d)
    
    # Collect all distances and find common factors
    all_dists = []
    for seq, dists in distances.items():
        all_dists.extend(dists)
    
    if not all_dists:
        return [], {}
    
    # Count factor frequencies
    factor_counts = Counter()
    for d in all_dists:
        for f in range(2, min(d+1, 60)):
            if d % f == 0:
                factor_counts[f] += 1
    
    return factor_counts.most_common(15), distances

def ciphertext_autokey(shifts, mode='sub'):
    """Ciphertext autokey: each cipher char is the key for the next."""
    result = []
    for i in range(len(shifts)):
        if i == 0:
            result.append(shifts[0])  # First char unknown without primer
        else:
            if mode == 'sub':
                result.append((shifts[i] - shifts[i-1]) % 29)
            elif mode == 'beaufort':
                result.append((shifts[i-1] - shifts[i]) % 29)
            elif mode == 'add':
                result.append((shifts[i] + shifts[i-1]) % 29)
    return result

def deor_running_key(shifts, deor_vals, mode='sub'):
    """Use entire Deor poem as running key."""
    result = []
    for i in range(len(shifts)):
        k = deor_vals[i % len(deor_vals)]
        if mode == 'sub':
            result.append((shifts[i] - k) % 29)
        elif mode == 'beaufort':
            result.append((k - shifts[i]) % 29)
        elif mode == 'add':
            result.append((shifts[i] + k) % 29)
    return result

def hill_2x2_decrypt(shifts, a, b, c, d):
    """Decrypt with 2x2 Hill cipher decryption matrix [[a,b],[c,d]]."""
    result = []
    for i in range(0, len(shifts)-1, 2):
        c1, c2 = shifts[i], shifts[i+1]
        p1 = (a * c1 + b * c2) % 29
        p2 = (c * c1 + d * c2) % 29
        result.extend([p1, p2])
    if len(shifts) % 2 == 1:
        result.append(shifts[-1])
    return result

def find_mod_inverse(a, m=29):
    """Extended Euclidean to find modular inverse."""
    if a == 0: return None
    g, x, _ = extended_gcd(a % m, m)
    if g != 1: return None
    return x % m

def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

# ====== MAIN ======
def main():
    repo = r"c:\Users\tyler\Repos\Cicada3301"
    pages_dir = os.path.join(repo, "LiberPrimus", "pages")
    
    # Unsolved pages
    unsolved = list(range(21, 55))  # 21-54
    
    # Load all page data
    page_data = {}
    for pn in unsolved:
        rpath = os.path.join(pages_dir, f"page_{pn:02d}", "runes.txt")
        if os.path.exists(rpath):
            shifts = load_runes(rpath)
            if len(shifts) >= 20:
                page_data[pn] = shifts
    
    # Also load P55 for verification
    p55_path = os.path.join(pages_dir, "page_55", "runes.txt")
    if os.path.exists(p55_path):
        p55_shifts = load_runes(p55_path)
        page_data[55] = p55_shifts
    
    print(f"Loaded {len(page_data)} pages.\n")
    
    # Prepare Deor key
    deor_vals = tokenize_oe(DEOR_TEXT)
    print(f"Deor poem: {len(deor_vals)} rune values\n")
    
    # ================================================================
    # ANALYSIS 1: PERIODIC IoC (Determine cipher type & key length)
    # ================================================================
    print("=" * 70)
    print("ANALYSIS 1: PERIODIC IoC ANALYSIS")
    print("If avg column IoC > 1.3 at period N, suggests Vigenère with key length N")
    print("=" * 70)
    
    for pn in sorted(page_data.keys()):
        if pn == 55: continue  # Skip verification page
        shifts = page_data[pn]
        raw_ioc = calc_ioc(shifts)
        results = periodic_ioc_analysis(shifts, max_period=50)
        
        # Find top 5 periods by avg IoC
        top5 = sorted(results, key=lambda x: -x[1])[:5]
        
        best_period, best_ioc = top5[0][0], top5[0][1]
        
        # Only print if something interesting (IoC > 1.15)
        if best_ioc > 1.15:
            print(f"\nPage {pn} (n={len(shifts)}, raw IoC={raw_ioc:.3f}):")
            print(f"  TOP PERIODS by avg column IoC:")
            for period, avg, mn, mx in top5:
                marker = " ***" if avg > 1.3 else ""
                print(f"    Period {period:3d}: avg={avg:.3f} min={mn:.3f} max={mx:.3f}{marker}")
        else:
            # Just show best in one line
            print(f"Page {pn} (n={len(shifts)}): best period={best_period} avg_IoC={best_ioc:.3f} raw_IoC={raw_ioc:.3f}")
    
    # ================================================================
    # ANALYSIS 2: KASISKI EXAMINATION (select pages)
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 2: KASISKI EXAMINATION (repeated sequences)")
    print("=" * 70)
    
    for pn in [21, 22, 25, 31, 32, 40, 50]:
        if pn not in page_data: continue
        shifts = page_data[pn]
        factors, distances = kasiski_exam(shifts)
        if factors:
            print(f"\nPage {pn}: Top factors from repeated trigrams:")
            for factor, count in factors[:10]:
                print(f"  Factor {factor:3d}: {count} occurrences")
            print(f"  Total repeated trigrams found: {len(distances)}")
        else:
            print(f"\nPage {pn}: No repeated trigrams found")
    
    # ================================================================
    # ANALYSIS 3: CIPHERTEXT AUTOKEY
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 3: CIPHERTEXT AUTOKEY")
    print("Ciphertext autokey: key[i] = cipher[i-1]")
    print("=" * 70)
    
    autokey_results = []
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        for mode in ['sub', 'beaufort', 'add']:
            plain = ciphertext_autokey(shifts, mode)
            ioc = calc_ioc(plain[1:])  # Skip first (unknown)
            lat = to_latin(plain[1:])
            sc = english_score(lat)
            if ioc > 1.2 or sc > 100:
                autokey_results.append((sc, ioc, pn, mode, lat[:100]))
    
    autokey_results.sort(reverse=True)
    print(f"\nResults with IoC > 1.2 or score > 100:")
    for sc, ioc, pn, mode, preview in autokey_results[:20]:
        print(f"  Page {pn} [{mode}]: IoC={ioc:.3f} score={sc} - {preview}")
    if not autokey_results:
        print("  (None found)")
    
    # Also try plaintext autokey on a few pages for comparison
    print("\n--- Also trying PLAINTEXT autokey (standard Vigenere autokey) ---")
    pt_autokey_results = []
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        for seed in range(29):
            # Plaintext autokey: P[i] = (C[i] - K[i]) % 29 where K[0]=seed, K[i]=P[i-1]
            plain = []
            k = seed
            for c in shifts:
                p = (c - k) % 29
                plain.append(p)
                k = p  # Plaintext feeds back
            ioc = calc_ioc(plain)
            lat = to_latin(plain)
            sc = english_score(lat)
            if ioc > 1.3 or sc > 120:
                pt_autokey_results.append((sc, ioc, pn, seed, lat[:100]))
    
    pt_autokey_results.sort(reverse=True)
    print(f"Results with IoC > 1.3 or score > 120:")
    for sc, ioc, pn, seed, preview in pt_autokey_results[:20]:
        print(f"  Page {pn} [seed={seed}]: IoC={ioc:.3f} score={sc} - {preview}")
    if not pt_autokey_results:
        print("  (None found)")
    
    # Also try: ciphertext autokey with Beaufort (P = K - C where K is running)
    print("\n--- Plaintext autokey BEAUFORT mode ---")
    pt_beau_results = []
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        for seed in range(29):
            plain = []
            k = seed
            for c in shifts:
                p = (k - c) % 29
                plain.append(p)
                k = p  # Plaintext feeds back
            ioc = calc_ioc(plain)
            lat = to_latin(plain)
            sc = english_score(lat)
            if ioc > 1.3 or sc > 120:
                pt_beau_results.append((sc, ioc, pn, seed, lat[:100]))
    
    pt_beau_results.sort(reverse=True)
    for sc, ioc, pn, seed, preview in pt_beau_results[:15]:
        print(f"  Page {pn} [seed={seed}]: IoC={ioc:.3f} score={sc} - {preview}")
    if not pt_beau_results:
        print("  (None found)")
    
    # ================================================================
    # ANALYSIS 4: DEOR POEM RUNNING KEY ON ALL PAGES
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 4: DEOR POEM AS RUNNING KEY")
    print(f"Deor key length: {len(deor_vals)}")
    print("=" * 70)
    
    deor_results = []
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        for mode in ['sub', 'beaufort', 'add']:
            for offset in range(0, len(deor_vals), max(1, len(deor_vals)//10)):
                # Try different starting positions in the Deor poem
                key = deor_vals[offset:] + deor_vals[:offset]
                plain = deor_running_key(shifts, key, mode)
                ioc = calc_ioc(plain)
                lat = to_latin(plain)
                sc = english_score(lat)
                if ioc > 1.2 or sc > 100:
                    deor_results.append((sc, ioc, pn, mode, offset, lat[:100]))
    
    deor_results.sort(reverse=True)
    print(f"\nAll results with IoC > 1.2 or score > 100:")
    for sc, ioc, pn, mode, offset, preview in deor_results[:20]:
        print(f"  Page {pn} [{mode} off={offset}]: IoC={ioc:.3f} score={sc} - {preview}")
    if not deor_results:
        print("  (None found)")
    
    # ================================================================
    # ANALYSIS 5: DIFFERENCE ANALYSIS (consecutive char differences)
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 5: DIFFERENCE ANALYSIS")
    print("Computing consecutive differences: d[i] = (c[i+1] - c[i]) % 29")
    print("If the cipher is additive with a slowly-changing key, diffs may show structure")
    print("=" * 70)
    
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        diffs = [(shifts[i+1] - shifts[i]) % 29 for i in range(len(shifts)-1)]
        diff_ioc = calc_ioc(diffs)
        if diff_ioc > 1.15:
            lat = to_latin(diffs)
            sc = english_score(lat)
            print(f"  Page {pn}: diff_IoC={diff_ioc:.3f} score={sc} [{lat[:60]}]")
    
    # Also try second differences
    print("\n--- Second differences: d2[i] = (c[i+2] - 2*c[i+1] + c[i]) % 29 ---")
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        d2 = [(shifts[i+2] - 2*shifts[i+1] + shifts[i]) % 29 for i in range(len(shifts)-2)]
        d2_ioc = calc_ioc(d2)
        if d2_ioc > 1.15:
            print(f"  Page {pn}: d2_IoC={d2_ioc:.3f}")
    
    # ================================================================
    # ANALYSIS 6: 2x2 HILL CIPHER (on select pages)
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 6: 2x2 HILL CIPHER BRUTE FORCE")
    print("Testing all 29^4 = 707,281 decryption matrices on select pages")
    print("=" * 70)
    
    # Test on pages 21, 31, 40, 50 as representatives
    test_pages = [21, 31, 40, 50]
    
    for pn in test_pages:
        if pn not in page_data: continue
        shifts = page_data[pn]
        print(f"\nPage {pn} (n={len(shifts)}):")
        
        best_results = []
        tested = 0
        
        for a in range(29):
            for b in range(29):
                for c_val in range(29):
                    for d in range(29):
                        # Check if matrix is invertible (det != 0 mod 29)
                        det = (a * d - b * c_val) % 29
                        if det == 0:
                            continue
                        
                        # Decrypt
                        plain = hill_2x2_decrypt(shifts, a, b, c_val, d)
                        ioc = calc_ioc(plain)
                        tested += 1
                        
                        if ioc > 1.4:
                            lat = to_latin(plain)
                            sc = english_score(lat)
                            best_results.append((sc, ioc, a, b, c_val, d, lat[:80]))
            
            # Progress
            if a % 10 == 9:
                print(f"  Progress: {a+1}/29 outer loop rows done ({tested} matrices tested)")
        
        best_results.sort(reverse=True)
        print(f"  Total matrices tested: {tested}")
        print(f"  Results with IoC > 1.4:")
        for sc, ioc, a, b, cv, d, preview in best_results[:10]:
            print(f"    Matrix [{a},{b};{cv},{d}] IoC={ioc:.3f} score={sc} - {preview}")
        if not best_results:
            print(f"    (None found with IoC > 1.4)")
    
    # ================================================================
    # ANALYSIS 7: VIGENERE KEY LENGTH ESTIMATION
    # (Friedman test / coincidence counting)
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 7: MUTUAL COINCIDENCE TEST")
    print("Comparing character frequencies between columns at each period")
    print("High mutual IoC suggests correct period")
    print("=" * 70)
    
    for pn in [21, 22, 25, 31, 32, 40, 50]:
        if pn not in page_data: continue
        shifts = page_data[pn]
        n = len(shifts)
        raw_ioc = calc_ioc(shifts)
        
        # Expected IoC for English in GP: ~1.73
        # Expected IoC for random: ~1.0
        # Friedman estimate of key length
        kp = 1.73  # Plaintext IoC estimate
        kr = 1.0   # Random IoC
        ko = raw_ioc  # Observed IoC
        
        if ko > kr:
            friedman_est = (kp - kr) / (ko - kr)
            print(f"  Page {pn}: Friedman key length estimate = {friedman_est:.1f} (raw IoC={raw_ioc:.3f})")
        else:
            print(f"  Page {pn}: raw IoC={raw_ioc:.3f} ≤ random (1.0), Friedman N/A → very long key or non-periodic")

    # ================================================================
    # ANALYSIS 8: KNOWN PLAINTEXT ATTACK (Cicada common titles)
    # ================================================================
    print("\n" + "=" * 70)
    print("ANALYSIS 8: KNOWN PLAINTEXT ATTACK")
    print("Try common Cicada titles at the start and derive key")
    print("=" * 70)
    
    # Common Cicada 3301 page titles
    titles_text = [
        "A KOAN", "SOME WISDOM", "AN INSTRUCTION", "A WARNING",
        "THE LOSS OF DIVINITY", "AN END", "A PARABLE", "WELCOME PILGRIM",
        "THE CIRCUMFERENCE", "A COMMANDMENT", "THE INSTAR"
    ]
    
    def text_to_vals(text):
        vals = []
        t = text.upper().replace(' ', '')
        i = 0
        while i < len(t):
            if i + 1 < len(t) and t[i:i+2] in ['TH', 'NG', 'OE', 'AE', 'EA', 'IA', 'EO']:
                vals.append(LATIN_TO_VAL[t[i:i+2]])
                i += 2
            elif t[i] in LATIN_TO_VAL:
                vals.append(LATIN_TO_VAL[t[i]])
                i += 1
            else:
                i += 1
        return vals
    
    kp_results = []
    for pn in sorted(page_data.keys()):
        if pn == 55: continue
        shifts = page_data[pn]
        for title in titles_text:
            tv = text_to_vals(title)
            if len(tv) > len(shifts):
                continue
            
            # Derive key assuming SUB: C = P + K → K = C - P
            key = [(shifts[i] - tv[i]) % 29 for i in range(len(tv))]
            key_lat = to_latin(key)
            
            # Now use this key (repeating) to decrypt the whole page
            key_len = len(key)
            plain = [(shifts[i] - key[i % key_len]) % 29 for i in range(len(shifts))]
            ioc = calc_ioc(plain)
            lat = to_latin(plain)
            sc = english_score(lat)
            
            if ioc > 1.3 or sc > 150:
                kp_results.append((sc, ioc, pn, title, key_lat, lat[:80]))
            
            # Also try Beaufort: C = K - P → K = C + P
            key_b = [(shifts[i] + tv[i]) % 29 for i in range(len(tv))]
            key_lat_b = to_latin(key_b)
            plain_b = [(key_b[i % len(key_b)] - shifts[i]) % 29 for i in range(len(shifts))]
            ioc_b = calc_ioc(plain_b)
            lat_b = to_latin(plain_b)
            sc_b = english_score(lat_b)
            
            if ioc_b > 1.3 or sc_b > 150:
                kp_results.append((sc_b, ioc_b, pn, f"{title}/BEAU", key_lat_b, lat_b[:80]))
    
    kp_results.sort(reverse=True)
    print(f"\nResults with IoC > 1.3 or score > 150:")
    for sc, ioc, pn, title, key, preview in kp_results[:20]:
        print(f"  Page {pn} [{title}]: key={key} IoC={ioc:.3f} score={sc}")
        print(f"    → {preview}")
    if not kp_results:
        print("  (None found)")

    # ================================================================
    # SAVE ALL RESULTS
    # ================================================================
    out_path = os.path.join(repo, "results_diagnostic_v3.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("DIAGNOSTIC ATTACK V3 RESULTS\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("PERIODIC IoC SUMMARY (best periods per page):\n")
        for pn in sorted(page_data.keys()):
            if pn == 55: continue
            shifts = page_data[pn]
            results = periodic_ioc_analysis(shifts, max_period=50)
            top3 = sorted(results, key=lambda x: -x[1])[:3]
            f.write(f"  P{pn}: raw_IoC={calc_ioc(shifts):.3f}")
            for period, avg, mn, mx in top3:
                f.write(f"  per={period}/avg={avg:.3f}")
            f.write("\n")
        
        f.write(f"\nAutokey results: {len(autokey_results)}\n")
        for item in autokey_results[:20]:
            f.write(f"  {item}\n")
        
        f.write(f"\nPT Autokey results: {len(pt_autokey_results)}\n")
        for item in pt_autokey_results[:20]:
            f.write(f"  {item}\n")
            
        f.write(f"\nDeor running key results: {len(deor_results)}\n")
        for item in deor_results[:20]:
            f.write(f"  {item}\n")
            
        f.write(f"\nKnown plaintext results: {len(kp_results)}\n")
        for item in kp_results[:20]:
            f.write(f"  {item}\n")
    
    print(f"\nResults saved to {out_path}")

if __name__ == "__main__":
    main()
