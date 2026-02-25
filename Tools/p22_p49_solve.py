#!/usr/bin/env python3
"""P22 solver: DIVINITY Beaufort + transposition reversal."""
import sys, os, math
from pathlib import Path
from collections import Counter

OUT = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'p22_p49_results.txt'), 'w', encoding='utf-8')
def pr(*a, **kw):
    print(*a, **kw)
    print(*a, **kw, file=OUT, flush=True)

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]

GOOD_BIGRAMS = {'TH','HE','IN','ER','AN','RE','ON','AT','EN','ND','TI','ES','OR','TE','OF',
    'ED','IS','IT','AL','AR','ST','TO','NT','NG','SE','HA','AS','OU','IO','LE','VE','CO',
    'ME','DE','HI','RI','RO','IC','NE','EA','RA','CE','LI','CH','LL','BE','MA','SI','OM','UR'}
COMMON_WORDS = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','ONE','OUR','OUT','HAS',
    'WHO','NOW','WAY','MAY','USE','MAN','END','THAT','WITH','HAVE','THIS','WILL','YOUR',
    'FROM','THEY','BEEN','EACH','MAKE','LIKE','INTO','TIME','JUST','KNOW','SOME','ONLY',
    'MOST','GOOD','ALSO','FIND','SELF','HOLY','DEEP','WITHIN','BEING','SACRED','THERE',
    'THEIR','WHICH','ABOUT','OTHER','THESE','SHALL','WORLD','GREAT','EVERY','NEVER',
    'SHOULD','THROUGH','PILGRIM','WELCOME','WISDOM','COMMAND','JOURNEY','TRUTH','DIVINE',
    'EMERGE','BELIEVE','UNTO','LAW','EARTH','FIRE'}

def load_runes(pnum):
    for fmt in [f"page_{pnum:02d}", f"page_{pnum}"]:
        p = Path(rf"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages\{fmt}\runes.txt")
        if p.exists():
            return [GP[ch] for ch in p.read_text(encoding='utf-8') if ch in GP]
    return []

def to_lat(idx): return ''.join(IDX2LAT[i] for i in idx)

def ioc29(idx):
    n = len(idx)
    if n < 2: return 0
    freq = Counter(idx)
    return 29.0 * sum(f*(f-1) for f in freq.values()) / (n*(n-1))

def score(lat):
    s = 0
    for i in range(len(lat)-1):
        if lat[i:i+2] in GOOD_BIGRAMS: s += 2
    u = lat.upper()
    for wl in range(3, min(13, len(u)+1)):
        for i in range(len(u)-wl+1):
            if u[i:i+wl] in COMMON_WORDS: s += wl*2
    return s

def decrypt(cipher, key, offset, mode, fskip=False):
    r = []; ki = offset; kl = len(key)
    for c in cipher:
        k = key[ki % kl]
        if mode == 'beau': p = (k - c) % MOD
        elif mode == 'sub': p = (c - k) % MOD
        else: p = (c + k) % MOD
        r.append(p)
        if not (fskip and p == 0): ki += 1
    return r

def rev_columnar(data, w):
    n = len(data); nr = math.ceil(n/w)
    full = n - w*(nr-1)
    cols = []; pos = 0
    for c in range(w):
        cl = nr if c < full else nr-1
        cols.append(data[pos:pos+cl]); pos += cl
    out = []
    for r in range(nr):
        for c in range(w):
            if r < len(cols[c]): out.append(cols[c][r])
    return out

def rev_col_row(data, w):
    n = len(data); nr = math.ceil(n/w)
    grid = [[None]*w for _ in range(nr)]
    idx = 0
    for c in range(w):
        for r in range(nr):
            if r*w+c < n: grid[r][c] = data[idx]; idx += 1
    return [grid[r][c] for r in range(nr) for c in range(w) if grid[r][c] is not None]

def rail_fence(data, rails):
    n = len(data)
    if rails <= 1 or rails >= n: return data
    fence = [[None]*n for _ in range(rails)]
    rail = 0; d = 1
    for i in range(n):
        fence[rail][i] = True; rail += d
        if rail == rails-1 or rail == 0: d = -d
    idx = 0
    for r in range(rails):
        for i in range(n):
            if fence[r][i]: fence[r][i] = data[idx]; idx += 1
    result = []; rail = 0; d = 1
    for i in range(n):
        result.append(fence[rail][i]); rail += d
        if rail == rails-1 or rail == 0: d = -d
    return result

def main():
    pr("="*70)
    pr("PAGE 22 SOLVER")
    pr("="*70)
    
    cipher = load_runes(22)
    pr(f"Loaded {len(cipher)} runes, raw IoC={ioc29(cipher):.4f}")
    
    configs = []
    for mode in ['beau','sub','add']:
        for off in range(8):
            for fs in [False, True]:
                dec = decrypt(cipher, DIVINITY, off, mode, fs)
                ic = ioc29(dec); lat = to_lat(dec); sc = score(lat)
                configs.append((ic, sc, mode, off, fs, dec, lat))
    
    configs.sort(reverse=True)
    pr("\nTop 10 by IoC:")
    for i, (ic, sc, m, o, fs, dec, lat) in enumerate(configs[:10]):
        pr(f"  #{i+1} IoC={ic:.4f} sc={sc} {m} off={o} fs={int(fs)}: {lat[:100]}")
    
    pr("\n--- Transposition reversal ---")
    best_all = []
    
    for ic, sc, m, o, fs, dec, lat in configs[:5]:
        tag = f"{m} off={o} fs={int(fs)}"
        best_all.append((sc, tag, lat))
        
        for w in range(2, 30):
            for name, fn in [('COL', rev_columnar), ('ROW', rev_col_row)]:
                try:
                    rv = fn(dec, w); rl = to_lat(rv); rs = score(rl)
                    if rs > sc + 30:
                        best_all.append((rs, f"{tag}+{name}_w{w}", rl))
                except: pass
        
        for rails in range(2, 15):
            try:
                rv = rail_fence(dec, rails); rl = to_lat(rv); rs = score(rl)
                if rs > sc + 30:
                    best_all.append((rs, f"{tag}+RAIL_r{rails}", rl))
            except: pass
        
        rv = list(reversed(dec)); rl = to_lat(rv); rs = score(rl)
        best_all.append((rs, f"{tag}+REV", rl))
        
        n = len(dec)
        for ns in range(2, 8):
            sl = n // ns
            rem = n % ns
            streams = []; pos = 0
            for s in range(ns):
                l = sl + (1 if s < rem else 0)
                streams.append(dec[pos:pos+l]); pos += l
            rv = []
            for i in range(sl+1):
                for s in range(ns):
                    if i < len(streams[s]): rv.append(streams[s][i])
            rl = to_lat(rv); rs = score(rl)
            if rs > sc + 30:
                best_all.append((rs, f"{tag}+DEINT_{ns}", rl))
    
    best_all.sort(reverse=True)
    pr("\n--- TOP 20 P22 ---")
    for i, (sc, tag, lat) in enumerate(best_all[:20]):
        pr(f"  #{i+1} sc={sc} {tag}: {lat[:120]}")
    
    pr("\n\n" + "="*70)
    pr("PAGE 49 SOLVER")  
    pr("="*70)
    
    cipher49 = load_runes(49)
    pr(f"Loaded {len(cipher49)} runes, raw IoC={ioc29(cipher49):.4f}")
    
    KEYS = {
        'DIVINITY': [23,10,1,10,9,10,16,26],
        'FIRFUMFER': [0,10,4,0,1,19,0,18,4,18,9,0,18],
        'MOBIUS': [19,3,17,10,1,15],
        'CICADA': [5,10,5,24,23,24],
        'PRESERVAT': [13,4,18,15,18,4,1,24,16,10,3,9],
        'EMERGENCE': [18,19,18,4,6,18,9,5,18],
        'INSTAR': [10,9,15,16,24,4],
        'PILGRIM': [13,10,20,6,4,10,19],
        'WELCOME': [7,18,20,5,3,19,18],
        'WISDOM': [7,10,15,23,3,19],
        'SACRED': [15,24,5,4,18,23],
        'SHADOW': [15,8,24,23,3,7],
        'VOID': [1,3,10,23],
        'CABAL': [5,24,17,24,20],
        'TRUTH': [16,4,1,2],
        'BELIEVE': [17,18,20,10,18,1,18],
    }
    
    all49 = []
    for kn, kv in KEYS.items():
        kl = len(kv)
        for mode in ['beau','sub','add']:
            for off in range(kl):
                for fs in [False, True]:
                    dec = decrypt(cipher49, kv, off, mode, fs)
                    ic = ioc29(dec); lat = to_lat(dec); sc = score(lat)
                    all49.append((ic, sc, kn, mode, off, fs, lat))
    
    all49.sort(key=lambda x: x[0], reverse=True)
    pr("\nTop 10 P49 by IoC:")
    for i, (ic, sc, kn, m, o, fs, lat) in enumerate(all49[:10]):
        pr(f"  #{i+1} IoC={ic:.4f} sc={sc} {kn} {m} off={o} fs={int(fs)}: {lat[:100]}")
    
    all49.sort(key=lambda x: x[1], reverse=True)
    pr("\nTop 10 P49 by score:")
    for i, (ic, sc, kn, m, o, fs, lat) in enumerate(all49[:10]):
        pr(f"  #{i+1} IoC={ic:.4f} sc={sc} {kn} {m} off={o} fs={int(fs)}: {lat[:100]}")
    
    pr("\n--- P49 Transposition ---")
    best49_ioc = sorted(all49, key=lambda x: x[0], reverse=True)[:3]
    best49_all = []
    for ic, sc, kn, m, o, fs, lat_orig in best49_ioc:
        dec = decrypt(cipher49, KEYS[kn], o, m, fs)
        tag = f"{kn} {m} off={o} fs={int(fs)}"
        for w in range(2, 20):
            for name, fn in [('COL', rev_columnar), ('ROW', rev_col_row)]:
                try:
                    rv = fn(dec, w); rl = to_lat(rv); rs = score(rl)
                    if rs > 40: best49_all.append((rs, f"{tag}+{name}_w{w}", rl))
                except: pass
        for rails in range(2, 12):
            try:
                rv = rail_fence(dec, rails); rl = to_lat(rv); rs = score(rl)
                if rs > 40: best49_all.append((rs, f"{tag}+RAIL_r{rails}", rl))
            except: pass
    
    if best49_all:
        best49_all.sort(reverse=True)
        pr("\nTop P49 transposition results:")
        for i, (sc, tag, lat) in enumerate(best49_all[:10]):
            pr(f"  #{i+1} sc={sc} {tag}: {lat[:100]}")
    
    pr("\nDone.")
    OUT.close()

if __name__ == '__main__':
    main()
