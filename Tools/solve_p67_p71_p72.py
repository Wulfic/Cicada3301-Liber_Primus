#!/usr/bin/env python3
"""Solve P67 (mirrors P09), verify P71 and P72."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}

IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def load_runes(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    indices = []
    rune_chars = []
    for ch in text:
        if ch in GP:
            indices.append(GP[ch])
            rune_chars.append(ch)
    return indices, rune_chars

def decode_shift_rev(indices, shift):
    """Shift + Reversed Gematria: (28 - (idx - shift)) % 29"""
    result = []
    for idx in indices:
        shifted = (idx - shift) % 29
        reversed_val = (28 - shifted) % 29
        result.append(IDX2LAT[reversed_val])
    return ''.join(result)

def decode_sub_rev(indices, shift):
    """SUB_REV mode from batch attack: (28 - (idx - shift)) % 29"""
    result = []
    for idx in indices:
        val = (28 - (idx - shift)) % 29
        result.append(IDX2LAT[val])
    return ''.join(result)

def decode_direct(indices):
    """Direct gematria (no cipher)"""
    return ''.join(IDX2LAT[i] for i in indices)

# ===== P67 =====
print("=" * 60)
print("PAGE 67 (mirrors P09)")
print("=" * 60)

p67_path = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages', 'page_67', 'runes.txt')
p09_path = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages', 'page_09', 'runes.txt')

p67_idx, _ = load_runes(p67_path)
p09_idx, _ = load_runes(p09_path)

print(f"P67 rune count: {len(p67_idx)}")
print(f"P09 rune count: {len(p09_idx)}")
print(f"Identical: {p67_idx == p09_idx}")

# P09 solution: "Shift 3 down reversed Gematria"
# Try various shift+reversed combinations
print("\nShift + Reversed Gematria decryptions of P67:")
for shift in range(29):
    text = decode_shift_rev(p67_idx, shift)
    # Check if it starts with known plaintext
    if 'ANINSTRUCTION' in text.replace(' ','') or 'DOFOUR' in text:
        print(f"  *** SHIFT {shift}: {text}")
    elif shift <= 5:
        print(f"  Shift {shift}: {text}")

# Also try direct reversed gematria (shift=0)
print("\nDirect gematria (no cipher):")
print(f"  {decode_direct(p67_idx)}")

# P64 (mirrors P06-08) used CAESAR_2 SUB_REV. Check what works for P09/P67.
# SUB_REV formula: (28 - (idx - shift)) % 29
print("\nSUB_REV mode (same formula, trying all shifts):")
for shift in range(29):
    text = decode_sub_rev(p67_idx, shift)
    if 'ANINSTRUCTION' in text.replace(' ','') or 'DOFOUR' in text or 'UNREASONABLE' in text:
        print(f"  *** SHIFT {shift}: {text}")

# Maybe P09 uses a DIFFERENT formula. Let me try all simple combinations:
print("\nTrying all simple cipher formulas:")
for shift in range(29):
    # (idx + shift) % 29
    text1 = ''.join(IDX2LAT[(i + shift) % 29] for i in p67_idx)
    # (idx - shift) % 29
    text2 = ''.join(IDX2LAT[(i - shift) % 29] for i in p67_idx)
    # (shift - idx) % 29 (Beaufort)
    text3 = ''.join(IDX2LAT[(shift - i) % 29] for i in p67_idx)
    # Atbash + shift
    text4 = ''.join(IDX2LAT[(28 - i + shift) % 29] for i in p67_idx)
    text5 = ''.join(IDX2LAT[(28 - i - shift) % 29] for i in p67_idx)
    
    for label, text in [('ADD', text1), ('SUB', text2), ('BEAU', text3), ('ATBASH+ADD', text4), ('ATBASH-SUB', text5)]:
        clean = text.replace(' ', '')
        if any(w in clean for w in ['ANINSTRUCTION', 'DOFOUR', 'UNREASONABLE', 'EACHDAY']):
            print(f"  *** {label} shift={shift}: {text}")

print()

# ===== P71 =====
print("=" * 60)
print("PAGE 71 (mirrors P13)")
print("=" * 60)

p71_dec = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages', 'page_71', 'decoded.txt')
with open(p71_dec, 'r', encoding='utf-8') as f:
    text = f.read().strip()
print(f"Decoded text: {text}")
# Insert spaces for readability
known_p13 = "SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN"
print(f"Expected (P13): {known_p13}")
# Compare
clean = text.upper().replace('U', 'V')  # In GP, V maps to U
print(f"Match: {'SOMEWISDOM' in text}")

# ===== P72 =====
print("\n" + "=" * 60)
print("PAGE 72 (mirrors P14 header)")
print("=" * 60)

p72_dec = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages', 'page_72', 'decoded.txt')
with open(p72_dec, 'r', encoding='utf-8') as f:
    text = f.read().strip()
print(f"Decoded text: {text}")
print(f"This is the section header for the Koan (mirrors P14)")

# Check P13 decoded for comparison
p13_path = os.path.join(os.path.dirname(__file__), '..', 'LiberPrimus', 'pages', 'page_13', 'runes.txt')
if os.path.exists(p13_path):
    p13_idx, _ = load_runes(p13_path)
    print(f"\nP13 rune count: {len(p13_idx)}")
    print(f"P13 direct gematria: {decode_direct(p13_idx)}")
