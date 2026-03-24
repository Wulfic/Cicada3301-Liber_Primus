#!/usr/bin/env python3
"""Analyze the binary hint files from Cicada 3301 ISO."""
import os
from collections import Counter

def analyze_file(path, name):
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f'\n{"="*60}')
    print(f'{name}')
    print(f'{"="*60}')
    print(f'Size: {len(data)} bytes')
    print(f'Hex (first 64 bytes): {data[:64].hex()}')
    print(f'Hex (last 32 bytes): {data[-32:].hex()}')
    
    byte_freq = Counter(data)
    print(f'Unique byte values: {len(byte_freq)}/256')
    print(f'Most common: {byte_freq.most_common(5)}')
    
    expected = len(data) / 256
    chi2 = sum((c - expected)**2 / expected for c in byte_freq.values())
    print(f'Chi-squared (uniform): {chi2:.1f}')
    
    # Entropy
    import math
    entropy = -sum((c/len(data)) * math.log2(c/len(data)) for c in byte_freq.values())
    print(f'Entropy: {entropy:.4f} bits/byte (max 8.0)')
    
    # As mod-29 indices
    rune_interp = [b % 29 for b in data]
    rune_freq = Counter(rune_interp)
    rune_ioc = 29 * sum(c*(c-1) for c in rune_freq.values()) / (len(data)*(len(data)-1))
    print(f'As mod-29: IoC={rune_ioc:.4f}')
    
    # Try interpreting as UTF-8 text
    try:
        text = data.decode('utf-8')
        print(f'Valid UTF-8: YES, length={len(text)}')
        print(f'First 100 chars: {repr(text[:100])}')
    except:
        print(f'Valid UTF-8: NO')
    
    # Try interpreting as ASCII 
    ascii_chars = sum(1 for b in data if 32 <= b <= 126)
    print(f'ASCII printable bytes: {ascii_chars}/{len(data)} ({100*ascii_chars/len(data):.1f}%)')
    
    # Check for structure: repeating patterns
    for period in [29, 71, 83, 113, 116, 421]:
        if period < len(data):
            matches = sum(1 for i in range(period, len(data)) if data[i] == data[i-period])
            expected_matches = (len(data) - period) / 256
            ratio = matches / max(expected_matches, 1)
            if ratio > 1.5:
                print(f'Period {period}: {matches} matches (expected {expected_matches:.1f}, ratio {ratio:.1f}x)')
    
    return data

# Main analysis
folly = analyze_file('data/folly_hint.txt', 'FOLLY HINT')
folly_rev = analyze_file('data/folly_rev_hint.txt', 'FOLLY REV HINT')
wisdom = analyze_file('data/wisdom_hint.txt', 'WISDOM HINT')

print(f'\n{"="*60}')
print(f'CROSS-FILE ANALYSIS')
print(f'{"="*60}')
print(f'folly == wisdom: {folly == wisdom}')
print(f'folly reversed == folly_rev: {folly[::-1] == folly_rev}')

# XOR analysis
xor_f_fr = bytes([a ^ b for a, b in zip(folly, folly_rev)])
print(f'\nfolly XOR folly_rev:')
print(f'  First 64 hex: {xor_f_fr[:64].hex()}')
printable = sum(1 for b in xor_f_fr if 32 <= b <= 126)
print(f'  Printable: {printable}/{len(xor_f_fr)} ({100*printable/len(xor_f_fr):.1f}%)')
zero_bytes = sum(1 for b in xor_f_fr if b == 0)
print(f'  Zero bytes: {zero_bytes}/{len(xor_f_fr)}')

# Try each XOR byte
print('\nXOR with constant byte (looking for ASCII text):')
for xor_val in range(256):
    xored = bytes([b ^ xor_val for b in folly[:40]])
    if sum(1 for b in xored if 32 <= b <= 126 or b in [10, 13]) > 30:
        print(f'  XOR 0x{xor_val:02x}: {xored[:40]}')

print('\nXOR folly_rev with constant byte:')        
for xor_val in range(256):
    xored = bytes([b ^ xor_val for b in folly_rev[:40]])
    if sum(1 for b in xored if 32 <= b <= 126 or b in [10, 13]) > 30:
        print(f'  XOR 0x{xor_val:02x}: {xored[:40]}')

# Check sizes / factors
n = len(folly)
print(f'\n{n} = ', end='')
factors = []
temp = n
for p in range(2, 1000):
    while temp % p == 0:
        factors.append(p)
        temp //= p
if temp > 1:
    factors.append(temp)
print(' x '.join(str(f) for f in factors))

# Maybe it's a 2D grid?
for w in [29, 58, 116, 421, 8, 13]:
    if n % w == 0:
        h = n // w
        print(f'Grid: {w} x {h}')
