#!/usr/bin/env python3
"""Comprehensive analysis of small unsolved pages in Liber Primus."""
import os
import re

RUNE_CHARS = set('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠᛂ')
GP = {
    'ᚠ':0,'ᚢ':1,'ᚦ':2,'ᚩ':3,'ᚱ':4,'ᚳ':5,'ᚷ':6,'ᚹ':7,
    'ᚻ':8,'ᚾ':9,'ᛁ':10,'ᛄ':11,'ᛇ':12,'ᛈ':13,'ᛉ':14,'ᛋ':15,
    'ᛏ':16,'ᛒ':17,'ᛖ':18,'ᛗ':19,'ᛚ':20,'ᛝ':21,'ᛟ':22,'ᛞ':23,
    'ᚪ':24,'ᚫ':25,'ᚣ':26,'ᛡ':27,'ᛠ':28,'ᛂ':11
}
GP_INV = {v: k for k, v in GP.items() if k != 'ᛂ'}
LETTERS = 'FUÞORC/GWNIJÆPXZSTBEMDLŊOEADÆYIAØ'
# Standard: 0=F,1=U,2=TH,3=O,4=R,5=C/K,6=G,7=W,8=H,9=N,10=I,11=J,12=EO,13=P,14=X,15=S/Z,16=T,17=B,18=E,19=M,20=L,21=NG,22=OE,23=D,24=A,25=AE,26=Y,27=IA/IO,28=EA
RUNEGLISH = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

pages_dir = os.path.join(os.path.dirname(__file__), 'LiberPrimus', 'pages')

unsolved_pages = []
all_pages = []

for d in sorted(os.listdir(pages_dir)):
    runes_path = os.path.join(pages_dir, d, 'runes.txt')
    readme_path = os.path.join(pages_dir, d, 'README.md')
    if not os.path.isfile(runes_path):
        continue
    with open(runes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    rune_count = sum(1 for c in content if c in RUNE_CHARS)
    
    status = 'unknown'
    if os.path.isfile(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme = f.read()
        if 'UNSOLVED' in readme:
            status = 'UNSOLVED'
        elif 'SOLVED' in readme:
            status = 'SOLVED'
    
    page_num = int(d.replace('page_', ''))
    
    if rune_count > 0:
        # Count words (separated by hyphens, dots, bullets, newlines, spaces, section markers)
        rune_text = ''
        for c in content:
            if c in RUNE_CHARS:
                rune_text += c
            elif c in '-.\n \t' + chr(8226) + '&$' + chr(167):  # bullet=•, section=§
                rune_text += ' '
        words = [w for w in rune_text.split() if w]
        word_count = len(words)
        word_lengths = [len(w) for w in words]
        
        # Get gematria values
        gematria_vals = [GP[c] for c in content if c in RUNE_CHARS]
        
        # Special chars
        special = []
        if chr(8226) in content: special.append('bullets')
        if '&' in content: special.append('&')
        if '$' in content: special.append('$')
        if chr(167) in content: special.append('§')
        if '.' in content: special.append('dots')
        has_hash = bool(re.search(r'[0-9a-f]{20,}', content))
        if has_hash: special.append('SHA-hash')
        has_quotes = '"' in content
        if has_quotes: special.append('quotes')
        has_numbers = any(c.isdigit() for c in content)
        if has_numbers: special.append('numbers')
        has_colon = ':' in content
        if has_colon: special.append('colons')
        
        # Frequency analysis
        freq = {}
        for v in gematria_vals:
            freq[v] = freq.get(v, 0) + 1
        
        # IoC
        n = len(gematria_vals)
        if n > 1:
            ioc = sum(f*(f-1) for f in freq.values()) / (n*(n-1))
        else:
            ioc = 0
        
        # Section breaks (& or blank lines between rune blocks)
        section_count = content.count('&') + content.count(chr(167))
        
        entry = {
            'page': page_num,
            'runes': rune_count,
            'words': word_count,
            'word_lengths': word_lengths,
            'ioc': ioc,
            'special': special,
            'content': content.strip(),
            'gematria': gematria_vals,
            'status': status,
            'freq': freq,
            'sections': section_count,
        }
        all_pages.append(entry)
        if status == 'UNSOLVED':
            unsolved_pages.append(entry)

print('=' * 90)
print('UNSOLVED PAGES WITH RUNE CONTENT (sorted by rune count)')
print('=' * 90)
print(f"{'Page':>5} | {'Runes':>6} | {'Words':>5} | {'IoC':>7} | {'Sects':>5} | Special")
print('-' * 90)
for p in sorted(unsolved_pages, key=lambda x: x['runes']):
    sp = ', '.join(p['special']) if p['special'] else '-'
    print(f"{p['page']:>5} | {p['runes']:>6} | {p['words']:>5} | {p['ioc']:>7.4f} | {p['sections']:>5} | {sp}")

print()
print('=' * 90)
print('RAW RUNE CONTENT OF SMALL UNSOLVED PAGES (< 250 runes)')
print('=' * 90)
for p in sorted(unsolved_pages, key=lambda x: x['runes']):
    if p['runes'] < 250:
        print(f"\n{'='*60}")
        print(f"PAGE {p['page']} ({p['runes']} runes, {p['words']} words, IoC={p['ioc']:.4f})")
        print(f"{'='*60}")
        print(f"Special: {p['special']}")
        print(f"Sections: {p['sections']}")
        print(f"Word lengths: {p['word_lengths']}")
        print(f"Gematria sum: {sum(p['gematria'])}")
        print(f"Gematria values: {p['gematria']}")
        
        # Runeglish (direct GP substitution - NOT decrypted)
        runeglish = ''.join(RUNEGLISH[v] for v in p['gematria'])
        print(f"Direct runeglish: {runeglish}")
        
        # Frequency distribution
        print(f"Freq distribution (val:count): ", end='')
        for v in sorted(p['freq'].keys()):
            print(f"{v}:{p['freq'][v]}", end=' ')
        print()
        
        print(f"Content:")
        print(p['content'])
        print()

# Also check for specific pages mentioned by user
print()
print('=' * 90)
print('SPECIFIC PAGES REQUESTED (33, 49, 52, 53, 54, 56) - INCLUDING SOLVED')
print('=' * 90)
target_pages = [33, 49, 52, 53, 54, 56]
for p in sorted(all_pages, key=lambda x: x['page']):
    if p['page'] in target_pages:
        print(f"\nPage {p['page']}: {p['runes']} runes, {p['words']} words, IoC={p['ioc']:.4f}, Status={p['status']}")
        print(f"  Special: {p['special']}, Word lengths: {p['word_lengths']}")
