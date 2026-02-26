#!/usr/bin/env python3
"""
P20 Deep Investigation - Deor Poem Connection

Prior work found: Beaufort(Deor, P20@primes) gives IoC=1.89 on a 166-char stream.
This script verifies and extends that finding with the CORRECT GP mapping.

Also tests the 2x83 interleaved reading and other transposition methods.
"""

import os, sys, io, re
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# CORRECT GP mapping
GP_RUNES = list("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛂᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ")
GP_RUNE_TO_IDX = {r: i for i, r in enumerate(GP_RUNES)}
GP_RUNE_TO_IDX['\u16C4'] = 11  # ᛄ alias for J
GP_LETTERS = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
GP_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]

# Deor poem (Old English)
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

# Tokenize OE text with digraphs
OE_MAP_DIGRAPH = {
    'TH': 2, 'NG': 21, 'EA': 28, 'EO': 12, 'OE': 22, 'AE': 25, 'IA': 27
}
OE_MAP_SINGLE = {
    'A': 24, 'B': 17, 'C': 5, 'D': 23, 'E': 18, 'F': 0, 'G': 6, 'H': 8,
    'I': 10, 'J': 11, 'K': 5, 'L': 20, 'M': 19, 'N': 9, 'O': 3, 'P': 13,
    'R': 4, 'S': 15, 'T': 16, 'U': 1, 'V': 1, 'W': 7, 'X': 14, 'Y': 26, 'Z': 14
}

def tokenize_oe_digraph(text):
    """Tokenize Old English with digraph handling and OE char substitution"""
    text = text.upper().replace('Þ', 'TH').replace('Ð', 'TH').replace('Æ', 'AE')
    # Remove non-alpha
    cleaned = ''.join(ch for ch in text if ch.isalpha())
    values = []
    i = 0
    while i < len(cleaned):
        if i + 1 < len(cleaned):
            di = cleaned[i:i+2]
            if di in OE_MAP_DIGRAPH:
                values.append(OE_MAP_DIGRAPH[di])
                i += 2
                continue
        ch = cleaned[i]
        if ch in OE_MAP_SINGLE:
            values.append(OE_MAP_SINGLE[ch])
        i += 1
    return values

def tokenize_oe_single(text):
    """Tokenize Old English without digraphs (letter by letter)"""
    text = text.upper().replace('Þ', 'TH').replace('Ð', 'TH').replace('Æ', 'AE')
    cleaned = ''.join(ch for ch in text if ch.isalpha())
    values = []
    for ch in cleaned:
        if ch in OE_MAP_SINGLE:
            values.append(OE_MAP_SINGLE[ch])
    return values

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def calc_ioc(indices):
    if len(indices) < 10: return 0
    freq = Counter(indices)
    n = len(indices)
    ioc = sum(f*(f-1) for f in freq.values()) / (n*(n-1)) if n > 1 else 0
    return ioc * 29

def word_score(text):
    words = ['THE','AND','THAT','THIS','WITH','FROM','HAVE','WILL','YOUR','WHAT',
             'THERE','THEIR','BEEN','SOME','WERE','WHICH','WHEN','THEM','NOT','FOR',
             'BUT','ARE','ALL','CAN','YOU','ONE','HIS','HER','WAS','OUR','INTO',
             'THAN','LIKE','TIME','MORE','WOULD','OTHER','ABOUT']
    return sum(text.count(w) * len(w)**2 for w in words)

def idx_to_text(indices):
    return ''.join(GP_LETTERS[v] for v in indices)

# Load P20
path = 'LiberPrimus/pages/page_20/runes.txt'
with open(path, 'r', encoding='utf-8') as f:
    p20_text = f.read().strip()

p20_cipher = [GP_RUNE_TO_IDX[ch] for ch in p20_text if ch in GP_RUNE_TO_IDX]
n = len(p20_cipher)

# Tokenize Deor both ways
deor_digraph = tokenize_oe_digraph(DEOR_TEXT)
deor_single = tokenize_oe_single(DEOR_TEXT)

print("=" * 80)
print("P20 DEEP INVESTIGATION - DEOR POEM")
print("=" * 80)
print(f"P20 cipher: {n} runes")
print(f"Deor (digraph): {len(deor_digraph)} values")
print(f"Deor (single): {len(deor_single)} values")

# Phase 1: Extract prime-indexed positions and apply Deor
print("\n" + "=" * 80)
print("PHASE 1: Prime-indexed positions + Deor key")
print("=" * 80)

for idx_type in ['0-indexed', '1-indexed']:
    if idx_type == '0-indexed':
        prime_pos = [i for i in range(n) if is_prime(i)]
    else:
        prime_pos = [i-1 for i in range(1, n+1) if is_prime(i)]
    
    prime_cipher = [p20_cipher[p] for p in prime_pos]
    print(f"\n{idx_type}: {len(prime_pos)} prime positions (first 10: {prime_pos[:10]})")
    
    for tok_name, deor_key in [('digraph', deor_digraph), ('single', deor_single)]:
        for mode_name in ['sub', 'beaufort', 'add']:
            for key_method in ['sequential', 'positional']:
                if key_method == 'sequential':
                    key = [deor_key[i % len(deor_key)] for i in range(len(prime_cipher))]
                else:
                    key = [deor_key[p % len(deor_key)] for p in prime_pos]
                
                if mode_name == 'sub':
                    plain = [(prime_cipher[i] - key[i]) % 29 for i in range(len(prime_cipher))]
                elif mode_name == 'beaufort':
                    plain = [(key[i] - prime_cipher[i]) % 29 for i in range(len(prime_cipher))]
                else:
                    plain = [(prime_cipher[i] + key[i]) % 29 for i in range(len(prime_cipher))]
                
                ioc = calc_ioc(plain)
                text = idx_to_text(plain)
                ws = word_score(text)
                
                if ioc > 1.3 or ws > 20:
                    print(f"  {tok_name}/{mode_name}/{key_method}: IoC={ioc:.2f}, wscore={ws}")
                    print(f"    Text: {text[:100]}")
                    
                    # If high IoC, try transpositions
                    if ioc > 1.5:
                        print(f"    ** HIGH IoC! Trying transpositions...")
                        m = len(plain)
                        for rows in range(2, min(m, 50)):
                            if m % rows == 0:
                                cols = m // rows
                                # Column-major read
                                col_read = []
                                for c in range(cols):
                                    for r in range(rows):
                                        col_read.append(plain[r * cols + c])
                                col_text = idx_to_text(col_read)
                                col_ioc = calc_ioc(col_read)
                                col_ws = word_score(col_text)
                                
                                # Row-major transpose read
                                row_read = []
                                for r in range(rows):
                                    for c in range(cols):
                                        row_read.append(plain[c * rows + r])
                                row_text = idx_to_text(row_read)
                                row_ioc = calc_ioc(row_read)
                                row_ws = word_score(row_text)
                                
                                if col_ws > 30:
                                    print(f"      ColMajor {rows}x{cols}: ws={col_ws}, IoC={col_ioc:.2f}")
                                    print(f"        {col_text[:100]}")
                                if row_ws > 30:
                                    print(f"      RowMajor {rows}x{cols}: ws={row_ws}, IoC={row_ioc:.2f}")
                                    print(f"        {row_text[:100]}")

# Phase 2: Prime-VALUE positions + Deor key  
print("\n" + "=" * 80)
print("PHASE 2: Prime-VALUE runes (rune GP index is prime) + Deor key")
print("=" * 80)

# Indices that are prime: 2,3,5,7,11,13,17,19,23 → TH,O,C,W,J,P,B,M,D
prime_indices = {2, 3, 5, 7, 11, 13, 17, 19, 23}
prime_val_pos = [i for i in range(n) if p20_cipher[i] in prime_indices]
nonprime_val_pos = [i for i in range(n) if p20_cipher[i] not in prime_indices]

print(f"Prime-value rune positions: {len(prime_val_pos)}")
print(f"Non-prime-value rune positions: {len(nonprime_val_pos)}")

for positions, label in [(prime_val_pos, 'PRIME-val'), (nonprime_val_pos, 'NONPRIME-val')]:
    cipher_subset = [p20_cipher[p] for p in positions]
    
    for tok_name, deor_key in [('digraph', deor_digraph), ('single', deor_single)]:
        for mode_name in ['sub', 'beaufort', 'add']:
            key = [deor_key[i % len(deor_key)] for i in range(len(cipher_subset))]
            
            if mode_name == 'sub':
                plain = [(cipher_subset[i] - key[i]) % 29 for i in range(len(cipher_subset))]
            elif mode_name == 'beaufort':
                plain = [(key[i] - cipher_subset[i]) % 29 for i in range(len(cipher_subset))]
            else:
                plain = [(cipher_subset[i] + key[i]) % 29 for i in range(len(cipher_subset))]
            
            ioc = calc_ioc(plain)
            text = idx_to_text(plain)
            ws = word_score(text)
            
            if ioc > 1.3 or ws > 20:
                print(f"  {label}/{tok_name}/{mode_name}: IoC={ioc:.2f}, wscore={ws}")
                print(f"    Text: {text[:100]}")

# Phase 3: Full page Deor running key
print("\n" + "=" * 80)
print("PHASE 3: Full page Deor running key")
print("=" * 80)

for tok_name, deor_key in [('digraph', deor_digraph), ('single', deor_single)]:
    for mode_name in ['sub', 'beaufort', 'add']:
        for offset in range(0, min(100, len(deor_key) - n)):
            key = deor_key[offset:offset+n]
            
            if mode_name == 'sub':
                plain = [(p20_cipher[i] - key[i]) % 29 for i in range(n)]
            elif mode_name == 'beaufort':
                plain = [(key[i] - p20_cipher[i]) % 29 for i in range(n)]
            else:
                plain = [(p20_cipher[i] + key[i]) % 29 for i in range(n)]
            
            ioc = calc_ioc(plain)
            text = idx_to_text(plain)
            ws = word_score(text)
            
            if ioc > 1.3 or ws > 40:
                print(f"  {tok_name}/{mode_name}/offset={offset}: IoC={ioc:.2f}, wscore={ws}")
                print(f"    Text: {text[:100]}")

# Phase 4: Dual-layer - Deor on prime positions, Caesar on non-prime positions
print("\n" + "=" * 80)
print("PHASE 4: Dual-layer (Deor@prime + Caesar@non-prime)")
print("=" * 80)

for tok_name, deor_key in [('digraph', deor_digraph), ('single', deor_single)]:
    for mode_name in ['beaufort', 'sub', 'add']:
        # Decrypt prime-index positions with Deor
        prime_pos_0 = [i for i in range(n) if is_prime(i)]
        key_seq = [deor_key[j % len(deor_key)] for j in range(len(prime_pos_0))]
        
        # Also try positional keying
        for key_method in ['sequential']:
            for shift in range(29):
                result = [0] * n
                j = 0
                for i in range(n):
                    if is_prime(i):
                        k = deor_key[j % len(deor_key)] if key_method == 'sequential' else deor_key[i % len(deor_key)]
                        if mode_name == 'sub':
                            result[i] = (p20_cipher[i] - k) % 29
                        elif mode_name == 'beaufort':
                            result[i] = (k - p20_cipher[i]) % 29
                        else:
                            result[i] = (p20_cipher[i] + k) % 29
                        j += 1
                    else:
                        result[i] = (p20_cipher[i] - shift) % 29
                
                ioc = calc_ioc(result)
                text = idx_to_text(result)
                ws = word_score(text)
                
                if ioc > 1.2 or ws > 50:
                    print(f"  {tok_name}/{mode_name}/{key_method}/shift={shift}: IoC={ioc:.2f}, wscore={ws}")
                    print(f"    Text: {text[:120]}")

# Phase 5: Verify the 166-stream claim
print("\n" + "=" * 80)
print("PHASE 5: Verify 166-stream (Deor@primes - P20@primes)")
print("=" * 80)

# The reported stream was 166 chars. Let me find what gives exactly 166 positions.
# Also try extracting based on sequential prime numbering vs position-based
# primes up to 574 (0-indexed): about 105
# 1-indexed primes up to 575: about 105

# 166 might be prime-VALUE positions
print(f"0-indexed prime positions: {len([i for i in range(n) if is_prime(i)])}")
print(f"1-indexed prime positions: {len([i for i in range(1, n+1) if is_prime(i)])}")
print(f"Prime-value positions (GP index is prime): {len(prime_val_pos)}")
print(f"Non-prime-value positions: {len(nonprime_val_pos)}")

# Check if P20 has a specific rune count that gives 166 in some way
# Maybe it's the number of composite (non-prime) indexed positions?
composite_pos = [i for i in range(n) if not is_prime(i)]
print(f"Composite (non-prime) positions: {len(composite_pos)}")

# Or: runes whose sequential prime (GP_PRIMES[idx]) is in some list?
# Let me check the actual claimed stream
CLAIMED_STREAM = "HOEEDOEBDMEATHLNTHRAIATOEYMYFYTXECCLTPSYTOGNIAOCDWYGDHCFPSMXMOXEOOEAEITYHYOTHTHYWSMFFEOEMTIASFLTEOENEAUOEIAAOECGWEJJDBOETAFHFBGGDTHHWGLARLEEPCMESYEOOENEOCTWFMTHTGEHGW"
print(f"\nClaimed stream length (Latin chars): {len(CLAIMED_STREAM)}")
print(f"Claimed stream: {CLAIMED_STREAM[:80]}")

# The claimed stream is in Latin letters (including digraphs like TH, NG, EO)
# So 166 Latin characters ≠ 166 GP indices. Let me count GP indices:
claimed_indices = []
i = 0
while i < len(CLAIMED_STREAM):
    if i + 1 < len(CLAIMED_STREAM):
        di = CLAIMED_STREAM[i:i+2]
        if di in ['TH', 'NG', 'EO', 'OE', 'AE', 'IA', 'EA']:
            claimed_indices.append(OE_MAP_DIGRAPH.get(di, 0))
            i += 2
            continue
    ch = CLAIMED_STREAM[i]
    if ch in OE_MAP_SINGLE:
        claimed_indices.append(OE_MAP_SINGLE[ch])
    i += 1
print(f"Claimed stream as GP indices: {len(claimed_indices)} values")
print(f"IoC of claimed stream: {calc_ioc(claimed_indices):.4f}")

# Now try to reproduce this stream with various methods
best_match = None
best_match_count = 0

for idx_type in ['0-indexed', '1-indexed']:
    if idx_type == '0-indexed':
        prime_pos = [i for i in range(n) if is_prime(i)]
    else:
        prime_pos = [i-1 for i in range(1, n+1) if is_prime(i)]
    
    for tok_name, deor_key in [('digraph', deor_digraph), ('single', deor_single)]:
        for mode_name in ['sub', 'beaufort', 'add']:
            for key_method in ['sequential', 'positional']:
                prime_cipher = [p20_cipher[p] for p in prime_pos]
                if key_method == 'sequential':
                    key = [deor_key[i % len(deor_key)] for i in range(len(prime_cipher))]
                else:
                    key = [deor_key[p % len(deor_key)] for p in prime_pos]
                
                if mode_name == 'sub':
                    stream = [(prime_cipher[i] - key[i]) % 29 for i in range(len(prime_cipher))]
                elif mode_name == 'beaufort':
                    stream = [(key[i] - prime_cipher[i]) % 29 for i in range(len(prime_cipher))]
                else:
                    stream = [(prime_cipher[i] + key[i]) % 29 for i in range(len(prime_cipher))]
                
                stream_text = idx_to_text(stream)
                ioc = calc_ioc(stream)
                
                # Check overlap with claimed stream
                min_len = min(len(stream), len(claimed_indices))
                matches = sum(1 for i in range(min_len) if stream[i] == claimed_indices[i])
                
                if ioc > 1.3 or matches > min_len * 0.5:
                    print(f"\n  {idx_type}/{tok_name}/{mode_name}/{key_method}: IoC={ioc:.2f}, matches={matches}/{min_len}")
                    print(f"    Stream: {stream_text[:100]}")

# Phase 6: What if the key repeats from Deor refrain only?
print("\n" + "=" * 80)
print("PHASE 6: Deor refrain as repeating key")
print("=" * 80)

# "Þæs ofereode, þisses swa mæg" = "THAES OFEREODE THISSES SWA MAEG"
refrain_text = "THAES OFEREODE THISSES SWA MAEG"
refrain_digraph = tokenize_oe_digraph(refrain_text)
refrain_single = tokenize_oe_single(refrain_text)

print(f"Refrain (digraph): {len(refrain_digraph)} values = {idx_to_text(refrain_digraph)}")
print(f"Refrain (single): {len(refrain_single)} values = {idx_to_text(refrain_single)}")

for tok_name, ref_key in [('digraph', refrain_digraph), ('single', refrain_single)]:
    for mode_name in ['sub', 'beaufort', 'add']:
        key = (ref_key * ((n // len(ref_key)) + 1))[:n]
        
        if mode_name == 'sub':
            plain = [(p20_cipher[i] - key[i]) % 29 for i in range(n)]
        elif mode_name == 'beaufort':
            plain = [(key[i] - p20_cipher[i]) % 29 for i in range(n)]
        else:
            plain = [(p20_cipher[i] + key[i]) % 29 for i in range(n)]
        
        ioc = calc_ioc(plain)
        text = idx_to_text(plain)
        ws = word_score(text)
        
        if ioc > 1.2 or ws > 30:
            print(f"  {tok_name}/{mode_name}: IoC={ioc:.2f}, wscore={ws}")
            print(f"    Text: {text[:100]}")

# Phase 7: P20 with Deor poem where Deor index = totient of sequential primes
print("\n" + "=" * 80)
print("PHASE 7: Deor[totient(prime[i])] as key (rearranging primes)")
print("=" * 80)

def sieve_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit+1, i):
                sieve[j] = False
    return [i for i in range(limit+1) if sieve[i]]

PRIMES = sieve_primes(10000)

for tok_name, deor_key in [('digraph', deor_digraph), ('single', deor_single)]:
    for mode_name in ['sub', 'beaufort', 'add']:
        for start in range(50):
            key = []
            for i in range(n):
                prime_idx = start + i
                if prime_idx < len(PRIMES):
                    deor_idx = (PRIMES[prime_idx] - 1) % len(deor_key)
                    key.append(deor_key[deor_idx])
                else:
                    key.append(0)
            
            if mode_name == 'sub':
                plain = [(p20_cipher[i] - key[i]) % 29 for i in range(n)]
            elif mode_name == 'beaufort':
                plain = [(key[i] - p20_cipher[i]) % 29 for i in range(n)]
            else:
                plain = [(p20_cipher[i] + key[i]) % 29 for i in range(n)]
            
            ioc = calc_ioc(plain)
            if ioc > 1.3:
                text = idx_to_text(plain)
                ws = word_score(text)
                print(f"  {tok_name}/{mode_name}/start={start}: IoC={ioc:.2f}, wscore={ws}")
                if ws > 20:
                    print(f"    Text: {text[:100]}")

print("\n\nDONE.")
