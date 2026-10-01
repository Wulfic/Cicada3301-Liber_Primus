#!/usr/bin/env python3
from pathlib import Path

in_path = Path('data') / 'p24_candidate_full_width14_shift25.txt'
out_path = Path('data') / 'p24_candidate_processed.txt'
txt = in_path.read_text(encoding='utf-8')

rules = [
    ('NG','ING'),
    ('TH','TH'),
    ('EO','E'),
    ('OE','O'),
    ('AE','A'),
    ('IA','IA'),
    ('IO','I'),
    ('EA','E'),
    ('C','K'),
    ('U','V'),
]

processed = txt
for a,b in rules:
    processed = processed.replace(a, b)

# Insert spaces before common words heuristically (very rough)
processed = processed.replace('THE', ' THE ')
processed = processed.replace('THERE', ' THERE ')
processed = ' '.join(processed.split())
out_path.write_text(processed, encoding='utf-8')
print('Wrote', out_path)
