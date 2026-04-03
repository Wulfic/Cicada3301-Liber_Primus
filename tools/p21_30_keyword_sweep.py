#!/usr/bin/env python3
"""
Systematic test: ALL P63 keywords × ALL modes on ALL P21-30 pages.
Also compare with verified_keys.json to find the real source of high IoC claims.
"""

import sys, os, json
from collections import Counter
from pathlib import Path

N = 29

RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP = {r: i for i, r in enumerate(RUNES)}
SEPS = set(".-\u2022 \n")

DIGRAPHS = {"TH":2, "EO":12, "NG":21, "OE":22, "AE":25, "IA":27, "EA":28}
SINGLES_MAP = {"F":0, "U":1, "V":1, "O":3, "R":4, "C":5, "K":5, "G":6, "W":7,
               "H":8, "N":9, "I":10, "J":11, "P":13, "X":14, "S":15, "T":16,
               "B":17, "E":18, "M":19, "L":20, "D":23, "A":24, "Y":26}

def parse_keyword(word):
    indices = []
    word = word.upper()
    i = 0
    while i < len(word):
        if i+1 < len(word) and word[i:i+2] in DIGRAPHS:
            indices.append(DIGRAPHS[word[i:i+2]])
            i += 2
        elif word[i] in SINGLES_MAP:
            indices.append(SINGLES_MAP[word[i]])
            i += 1
        else:
            i += 1
    return indices

def load_page(pn):
    path = Path(f"pages/page_{pn:02d}/runes.txt")
    if not path.exists(): return None, None
    text = path.read_text(encoding='utf-8')
    flat = []
    words = []
    current = []
    for ch in text:
        if ch in GP:
            current.append(GP[ch])
            flat.append(GP[ch])
        elif ch in SEPS:
            if current:
                words.append(current)
                current = []
    if current: words.append(current)
    return flat, words

def ioc(vals):
    n = len(vals)
    if n < 2: return 0.0
    freq = Counter(vals)
    return sum(f*(f-1) for f in freq.values()) * N / (n*(n-1))

def decrypt(flat, key, mode):
    kl = len(key)
    if mode == "sub":
        return [(flat[i] - key[i % kl]) % N for i in range(len(flat))]
    elif mode == "add":
        return [(flat[i] + key[i % kl]) % N for i in range(len(flat))]
    else:  # beaufort
        return [(key[i % kl] - flat[i]) % N for i in range(len(flat))]

def check_singletons(vals, words):
    pos = 0
    total = 0
    passing = 0
    for w in words:
        if len(w) == 1:
            total += 1
            if vals[pos] in (10, 24):
                passing += 1
        pos += len(w)
    return total, passing

def vals_to_words(vals, words):
    pos = 0
    result = []
    for w in words:
        rg = ''.join(RUNEGLISH[vals[pos+i]] for i in range(len(w)))
        result.append(rg)
        pos += len(w)
    return result

def main():
    os.chdir(Path(__file__).parent.parent)
    
    # All keywords from P63 magic square
    KEYWORDS = {
        "SHADOWS": parse_keyword("SHADOWS"),
        "AETHEREAL": parse_keyword("AETHEREAL"),
        "BUFFERS": parse_keyword("BUFFERS"),
        "VOID": parse_keyword("VOID"),
        "CARNAL": parse_keyword("CARNAL"),
        "OBSCURA": parse_keyword("OBSCURA"),
        "FORM": parse_keyword("FORM"),
        "MOBIUS": parse_keyword("MOBIUS"),
        "ANALOG": parse_keyword("ANALOG"),
        "MOURNFUL": parse_keyword("MOURNFUL"),
        "CABAL": parse_keyword("CABAL"),
        "DIVINITY": parse_keyword("DIVINITY"),
        "ENCRYPT": parse_keyword("ENCRYPT"),
        "ENCRYPTION": parse_keyword("ENCRYPTION"),
        "TOTIENT": parse_keyword("TOTIENT"),
        "DEOR": parse_keyword("DEOR"),
        "FIRFUMFERENFE": parse_keyword("FIRFUMFERENFE"),
        "CICADA": parse_keyword("CICADA"),
    }
    
    # Load verified keys
    vk_path = Path("data/verified_keys.json")
    verified_keys = {}
    if vk_path.exists():
        with open(vk_path) as f:
            vk_data = json.load(f)
        for k, v in vk_data.items():
            verified_keys[int(k)] = v
    
    modes = ["sub", "add", "beaufort"]
    
    print("=" * 80)
    print("SYSTEMATIC KEYWORD TEST: ALL keywords x ALL modes x P21-30")
    print("=" * 80)
    
    for pn in range(21, 31):
        flat, words = load_page(pn)
        if flat is None: continue
        
        nr = len(flat)
        n_singles_total = sum(1 for w in words if len(w) == 1)
        
        print(f"\n{'='*80}")
        print(f"P{pn}: {nr} runes, {len(words)} words, {n_singles_total} singletons")
        print(f"{'='*80}")
        
        results = []
        
        # Test all keywords x modes
        for kw_name, kw_vals in KEYWORDS.items():
            for mode in modes:
                plain = decrypt(flat, kw_vals, mode)
                ic = ioc(plain)
                t, p = check_singletons(plain, words)
                results.append((ic, p, t, kw_name, mode, len(kw_vals), plain))
        
        # Test verified key if available
        if pn in verified_keys:
            vk = verified_keys[pn]
            for mode in modes:
                plain = decrypt(flat, vk, mode)
                ic = ioc(plain)
                t, p = check_singletons(plain, words)
                results.append((ic, p, t, f"verified_key(len={len(vk)})", mode, len(vk), plain))
        
        # Sort by IoC descending
        results.sort(key=lambda x: -x[0])
        
        print(f"\n  Top 15 by IoC:")
        for i, (ic, p, t, name, mode, kl, plain) in enumerate(results[:15]):
            rg = vals_to_words(plain, words)
            text_preview = ' '.join(rg[:10])
            print(f"  {i+1:2d}. IoC={ic:.4f} sing={p}/{t} [{name:18s}] {mode:8s} (kl={kl:2d}) | {text_preview}...")
        
        # Find best with ALL singletons passing
        best_singleton = None
        for ic, p, t, name, mode, kl, plain in results:
            if t > 0 and p == t:
                best_singleton = (ic, p, t, name, mode, kl, plain)
                break
        
        if best_singleton:
            ic, p, t, name, mode, kl, plain = best_singleton
            rg = vals_to_words(plain, words)
            print(f"\n  BEST with all singletons passing: IoC={ic:.4f} [{name}] {mode} | {' '.join(rg[:15])}...")
        else:
            print(f"\n  NO keyword/mode combo passes all singletons!")
            # Show best singleton ratio
            best_ratio = max(results, key=lambda x: x[1]/max(x[2],1))
            ic, p, t, name, mode, kl, plain = best_ratio
            rg = vals_to_words(plain, words)
            print(f"  Best singleton ratio: {p}/{t} IoC={ic:.4f} [{name}] {mode}")
    
    print(f"\n{'='*80}")
    print("DONE")
    print("="*80)

if __name__ == "__main__":
    main()
