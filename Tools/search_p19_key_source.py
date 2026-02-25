#!/usr/bin/env python3
"""
Search ALL LP pages for sequences matching the P19 key.
If the running key comes from another page's rune values, we'll find it.
"""

import os, glob
from collections import Counter

GP = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4, '\u16B3':5, '\u16B7':6, '\u16B9':7,
    '\u16BB':8, '\u16BE':9, '\u16C1':10, '\u16C2':11, '\u16C4':11,
    '\u16C7':12, '\u16C8':13, '\u16C9':14, '\u16CB':15, '\u16CF':16, '\u16D2':17, '\u16D6':18,
    '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23, '\u16AA':24, '\u16AB':25,
    '\u16A3':26, '\u16E1':27, '\u16E0':28
}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

# P19 known key (ADD mode, first 43 values)
KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

# Load all pages
pages = {}
for page_dir in sorted(glob.glob('LiberPrimus/pages/page_*/runes.txt')):
    page_num = int(page_dir.split('page_')[1].split('/')[0].split('\\')[0])
    try:
        with open(page_dir, 'r', encoding='utf-8') as f:
            text = f.read()
        vals = [GP[ch] for ch in text if ch in GP]
        if vals:
            pages[page_num] = vals
    except:
        pass

print(f"Loaded {len(pages)} pages")

# Search each page for matching subsequence
print("\n=== Direct key match (key values as rune values) ===")
for pnum, vals in sorted(pages.items()):
    for offset in range(len(vals) - len(KEY)):
        matches = sum(1 for i in range(len(KEY)) if vals[offset + i] == KEY[i])
        if matches >= 15:
            pct = 100 * matches / len(KEY)
            print(f"  P{pnum} offset {offset}: {matches}/{len(KEY)} ({pct:.0f}%) match")

# Also try: key could be from another page's PLAINTEXT
# For solved pages, we'd need the plaintext values
# But let me check if any page's runes, after a simple transform (Caesar, atbash),
# match the key

print("\n=== Key match with Caesar shift ===")
for shift in range(29):
    shifted_key = [(k + shift) % 29 for k in KEY]
    for pnum, vals in sorted(pages.items()):
        for offset in range(len(vals) - len(KEY)):
            matches = sum(1 for i in range(len(KEY)) if vals[offset + i] == shifted_key[i])
            if matches >= 20:
                pct = 100 * matches / len(KEY)
                print(f"  shift={shift}, P{pnum} offset {offset}: {matches}/{len(KEY)} ({pct:.0f}%)")

# Also search in concatenated all pages
print("\n=== Key match in ALL pages concatenated ===")
all_vals = []
page_offsets = {}
for pnum in sorted(pages.keys()):
    page_offsets[len(all_vals)] = pnum
    all_vals.extend(pages[pnum])
print(f"Total runes: {len(all_vals)}")

best_matches = []
for offset in range(len(all_vals) - len(KEY)):
    matches = sum(1 for i in range(len(KEY)) if all_vals[offset + i] == KEY[i])
    if matches >= 10:
        # Find which page this offset is in
        page = None
        for start_off in sorted(page_offsets.keys(), reverse=True):
            if offset >= start_off:
                page = page_offsets[start_off]
                break
        best_matches.append((matches, offset, page))

best_matches.sort(key=lambda x: -x[0])
for m, off, p in best_matches[:15]:
    print(f"  {m}/{len(KEY)} at global offset {off} (P{p})")

# Check the Deor poem text as a KEY source
print("\n=== Check Deor poem text as P19 key ===")
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
special = {'\u00de': 2, '\u00fe': 2, '\u00d0': 23, '\u00f0': 23, '\u00e6': 25}

with open('Analysis/Reference_Docs/deor_poem.txt', 'r', encoding='utf-8') as f:
    deor_text = f.read()

deor_vals = []
for ch in deor_text:
    if ch in special:
        deor_vals.append(special[ch])
    elif ch.upper() in ENG2GP:
        deor_vals.append(ENG2GP[ch.upper()])

print(f"Deor GP values: {len(deor_vals)}")
for offset in range(len(deor_vals) - len(KEY)):
    matches = sum(1 for i in range(len(KEY)) if deor_vals[offset + i] == KEY[i])
    if matches >= 8:
        print(f"  Deor offset {offset}: {matches}/{len(KEY)} match")

# Also try: what if the key is DERIVED from P19 cipher via autokey?
# Autokey: key[i] = plain[i-k] for some k
# We know plain[0:43] and cipher[0:43]
# If autokey: key[i] = plain[i-47] for period 47 autokey
# But we showed P19 is NOT autokey. Let me verify once more.

print("\n=== P19 autokey check ===")
with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
    text = f.read()
p19_cipher = [GP[ch] for ch in text if ch in GP]

# Known plaintext for first 43
p19_plain = [(p19_cipher[i] + KEY[i]) % 29 for i in range(43)]

# Check if key[i] = plain[i-1] (autokey with lag 1 from position 1 onwards)
for lag in range(1, 43):
    matches = sum(1 for i in range(lag, 43) if KEY[i] == p19_plain[i - lag])
    if matches > 10:
        print(f"  Autokey lag {lag}: {matches}/{43-lag} matches")

# Check if key[i] = cipher[i-1]
for lag in range(1, 43):
    matches = sum(1 for i in range(lag, 43) if KEY[i] == p19_cipher[i - lag])
    if matches > 10:
        print(f"  Cipher autokey lag {lag}: {matches}/{43-lag} matches")

print("\nDone.")
