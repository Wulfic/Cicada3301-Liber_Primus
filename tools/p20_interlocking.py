#!/usr/bin/env python3
"""P20 dual-stream interlocking cipher investigation."""
import sys; sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path; from collections import Counter

def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    i=5
    while i*i<=n:
        if n%i==0 or n%(i+2)==0: return False
        i+=6
    return True

RUNE_TO_IDX={chr(k):v for k,v in [(0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),(0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),(0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),(0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),(0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
IDX_TO=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
M=29

flat20=[RUNE_TO_IDX[ch] for ch in Path('pages/page_20/runes.txt').read_text(encoding='utf-8') if ch in RUNE_TO_IDX]
PRIME_IDX={i for i in range(29) if is_prime(i)}
prime_s=[v for v in flat20 if v in PRIME_IDX]
nonprime_s=[v for v in flat20 if v not in PRIME_IDX]
print(f'P20 prime-idx stream: {len(prime_s)} | non-prime: {len(nonprime_s)}')

ENG2GP={'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':0,'R':4,'S':15,'T':16,'U':1,'V':17,'W':7,'X':14,'Y':26,'Z':15}
deor_raw=Path('data/deor_poem.txt').read_text(encoding='utf-8').split('DEOR POEM (MODERN ENGLISH')[0].upper()
dstream=[]; i=0
DG_MAP={'TH':2,'AE':25,'NG':21,'OE':22,'EO':12,'IO':27,'EA':28}
while i<len(deor_raw):
    dg=deor_raw[i:i+2] if i+1<len(deor_raw) else ''
    if dg in DG_MAP: dstream.append(DG_MAP[dg]); i+=2; continue
    if deor_raw[i] in ENG2GP: dstream.append(ENG2GP[deor_raw[i]])
    i+=1
print(f'Deor stream: {len(dstream)} values')

def ioc(v):
    c=Counter(v); n=len(v)
    return sum(x*(x-1) for x in c.values())/(n*(n-1)) if n>1 else 0

def decode_words(vals):
    return ''.join(IDX_TO[x] for x in vals)

best_ioc=0; best_off=0; best_mode='?'; best_pl=[]
for mode in ['beaufort','sub','add']:
    for off in range(min(len(dstream)-len(prime_s)+1, 600)):
        key=dstream[off:off+len(prime_s)]
        if len(key)<len(prime_s): break
        if mode=='beaufort': pl=[(key[i]-prime_s[i])%M for i in range(len(prime_s))]
        elif mode=='sub': pl=[(prime_s[i]-key[i])%M for i in range(len(prime_s))]
        else: pl=[(prime_s[i]+key[i])%M for i in range(len(prime_s))]
        ic=ioc(pl)
        if ic>best_ioc:
            best_ioc=ic; best_off=off; best_mode=mode; best_pl=pl[:]
            print(f'  New best prime: mode={mode} off={off} IoC={ic:.4f} text={decode_words(pl[:60])}')
print(f'\nBest prime-stream: mode={best_mode} off={best_off} IoC={best_ioc:.4f}')
print(f'Prime decoded: {decode_words(best_pl[:100])}')

# Test prime_pl as running key for non-prime stream
print('\nTesting prime_pl as key for non-prime stream:')
best2=0
for mode2 in ['sub','add','beaufort']:
    for rep_off in range(min(len(best_pl), 100)):
        ext_key=(best_pl*((len(nonprime_s)//len(best_pl))+2))[rep_off:rep_off+len(nonprime_s)]
        if mode2=='sub': pl2=[(nonprime_s[i]-ext_key[i])%M for i in range(len(nonprime_s))]
        elif mode2=='add': pl2=[(nonprime_s[i]+ext_key[i])%M for i in range(len(nonprime_s))]
        else: pl2=[(ext_key[i]-nonprime_s[i])%M for i in range(len(nonprime_s))]
        ic2=ioc(pl2)
        if ic2>1.3:
            txt2=decode_words(pl2[:80])
            print(f'  HIT: mode={mode2} rep_off={rep_off} IoC={ic2:.4f} -> {txt2}')
        if ic2>best2: best2=ic2
print(f'Best IoC non-prime from prime_pl: {best2:.4f}')

# Also test: non-prime stream with direct Caesar shift -2 (mod 29) = shift +27
print('\nNon-prime stream Caesar shifts:')
for shift in range(29):
    pl_c = [(v-shift)%M for v in nonprime_s]
    ic_c = ioc(pl_c)
    if ic_c > 1.5:
        print(f'  Caesar {shift}: IoC={ic_c:.4f} text={decode_words(pl_c[:80])}')
    elif shift == 16 or shift == 27 or shift == 2:  # specifically test shift 16 (note: -2 = +27)
        print(f'  Caesar {shift}: IoC={ic_c:.4f} text[:60]={decode_words(pl_c[:60])}')
