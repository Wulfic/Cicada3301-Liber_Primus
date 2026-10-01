#!/usr/bin/env python3
"""
Refine verified_keys.json keys by fixing singleton-failing positions.
For each page: find which singletons fail, compute the 2 possible key values
that would make each singleton decrypt to I or A, then try all combos.
"""

import sys, os, json
from collections import Counter, defaultdict
from pathlib import Path

N = 29

RUNES = list("\u16A0\u16A2\u16A6\u16A9\u16B1\u16B3\u16B7\u16B9\u16BB\u16BE\u16C1\u16C4\u16C7\u16C8\u16C9\u16CB\u16CF\u16D2\u16D6\u16D7\u16DA\u16DD\u16DF\u16DE\u16AA\u16AB\u16A3\u16E1\u16E0")
RUNEGLISH = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
             "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
GP = {r: i for i, r in enumerate(RUNES)}
SEPS = set(".-\u2022 \n")

def load_page(pn):
    path = Path(f"pages/page_{pn:02d}/runes.txt")
    if not path.exists(): return None, None
    text = path.read_text(encoding='utf-8')
    flat = []; words = []; current = []
    for ch in text:
        if ch in GP:
            current.append(GP[ch])
            flat.append(GP[ch])
        elif ch in SEPS:
            if current: words.append(current); current = []
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
    else:
        return [(key[i % kl] - flat[i]) % N for i in range(len(flat))]

def get_singleton_info(flat, words, key, mode):
    """Get singleton position, cipher value, current decrypted value, and key position."""
    kl = len(key)
    pos = 0
    singles = []
    for w in words:
        if len(w) == 1:
            cv = flat[pos]
            kp = pos % kl
            kv = key[kp]
            if mode == "sub": pv = (cv - kv) % N
            elif mode == "add": pv = (cv + kv) % N
            else: pv = (kv - cv) % N
            singles.append({
                'pos': pos, 'cipher': cv, 'key_pos': kp, 'key_val': kv,
                'plain': pv, 'ok': pv in (10, 24),
                'runeglish': RUNEGLISH[pv],
            })
        pos += len(w)
    return singles

def required_key_vals(cipher_val, mode):
    """For a singleton to decrypt to I(10) or A(24), what key values are needed?"""
    results = []
    for target in (10, 24):
        if mode == "sub":
            # target = (cipher - key) % N => key = (cipher - target) % N
            kv = (cipher_val - target) % N
        elif mode == "add":
            # target = (cipher + key) % N => key = (target - cipher) % N
            kv = (target - cipher_val) % N
        else:  # beaufort
            # target = (key - cipher) % N => key = (target + cipher) % N
            kv = (target + cipher_val) % N
        results.append((target, kv))
    return results  # [(10, kv_for_I), (24, kv_for_A)]

def vals_to_words(vals, words):
    pos = 0; result = []
    for w in words:
        rg = ''.join(RUNEGLISH[vals[pos+i]] for i in range(len(w)))
        result.append(rg)
        pos += len(w)
    return result

ENGLISH_BIGRAMS = {
    (16,8): 50, (8,18): 40, (10,9): 30, (18,4): 25, (24,9): 30,
    (9,23): 25, (16,10): 20, (10,16): 18, (10,15): 15,
    (24,20): 15, (15,16): 20, (18,9): 15, (24,16): 18,
    (16,18): 15, (8,24): 12, (18,15): 12, (3,0): 12,
    (0,3): 10, (4,18): 10, (24,4): 10, (16,3): 10,
}

def bigram_score(vals):
    return sum(ENGLISH_BIGRAMS.get((vals[i], vals[i+1]), 0) for i in range(len(vals)-1))

def main():
    os.chdir(Path(__file__).parent.parent)
    
    # Load verified keys
    with open("data/verified_keys.json") as f:
        vk_data = json.load(f)
    
    modes = ["sub", "add", "beaufort"]
    
    print("=" * 80)
    print("VERIFIED KEY REFINEMENT VIA SINGLETON CONSTRAINT")
    print("=" * 80)
    
    for pn in range(21, 55):  # Test all unsolved pages
        flat, words = load_page(pn)
        if flat is None: continue
        
        pn_str = str(pn)
        if pn_str not in vk_data: continue
        vk = vk_data[pn_str]
        kl = len(vk)
        nr = len(flat)
        
        # Try all 3 modes with verified key
        for mode in modes:
            singles = get_singleton_info(flat, words, vk, mode)
            if not singles: continue
            
            total = len(singles)
            passing = sum(1 for s in singles if s['ok'])
            failing = [s for s in singles if not s['ok']]
            
            if passing == total:
                # Already passes — check IoC
                plain = decrypt(flat, vk, mode)
                ic = ioc(plain)
                bg = bigram_score(plain)
                rg = vals_to_words(plain, words)
                print(f"\nP{pn} [{mode:8s}] kl={kl} ALL {total} SINGLETONS PASS! IoC={ic:.4f} bg={bg}")
                print(f"  Text: {' '.join(rg[:15])}...")
                continue
            
            if len(failing) > 12:
                continue  # Too many failures, skip
            
            # Check for conflicts: if two singletons map to same key_pos
            # but require different key values, that combo is impossible
            kp_constraints = defaultdict(list)
            for s in failing:
                req = required_key_vals(s['cipher'], mode)
                kp_constraints[s['key_pos']].append({
                    'pos': s['pos'],
                    'required': req,  # [(10, kv_I), (24, kv_A)]
                })
            
            # For each key position with constraints, find valid key values
            kp_valid = {}
            impossible = False
            for kp, constraints in kp_constraints.items():
                # Each constraint allows 2 key values. Find intersection across all constraints at this kp.
                valid_kvs = None
                for c in constraints:
                    kvs = set(kv for _, kv in c['required'])
                    if valid_kvs is None:
                        valid_kvs = kvs
                    else:
                        valid_kvs &= kvs
                
                if not valid_kvs:
                    # Conflict! No single key value satisfies all singletons at this key position
                    impossible = True
                    break
                kp_valid[kp] = sorted(valid_kvs)
            
            if impossible:
                # Check if it's close
                if total - passing <= 3:
                    plain = decrypt(flat, vk, mode)
                    ic = ioc(plain)
                    print(f"\nP{pn} [{mode:8s}] kl={kl} {passing}/{total} singles | IoC={ic:.4f} | CONFLICT at key positions (can't fix all)")
                continue
            
            # Try all combinations of valid key values
            from itertools import product as iprod
            
            kp_list = sorted(kp_valid.keys())
            combos = list(iprod(*[kp_valid[kp] for kp in kp_list]))
            
            best = None
            for combo in combos:
                # Create modified key
                new_key = list(vk)
                for kp, kv in zip(kp_list, combo):
                    new_key[kp] = kv
                
                # Decrypt and score
                plain = decrypt(flat, new_key, mode)
                ic = ioc(plain)
                bg = bigram_score(plain)
                
                # Verify ALL singletons now pass
                all_ok = True
                pos = 0
                for w in words:
                    if len(w) == 1:
                        if plain[pos] not in (10, 24):
                            all_ok = False
                            break
                    pos += len(w)
                
                if all_ok:
                    score = ic * 100 + bg * 0.5
                    if best is None or score > best['score']:
                        best = {
                            'key': new_key, 'mode': mode, 'ioc': ic, 'bg': bg,
                            'score': score, 'combo': combo,
                            'plain': plain,
                        }
            
            if best:
                rg = vals_to_words(best['plain'], words)
                n_changed = sum(1 for i in range(kl) if vk[i] != best['key'][i])
                print(f"\nP{pn} [{mode:8s}] kl={kl} REFINED: {passing}/{total} -> ALL pass | IoC={best['ioc']:.4f} bg={best['bg']} | {n_changed} key positions changed")
                print(f"  Changed: {dict(zip(kp_list, best['combo']))}")
                print(f"  Text: {' '.join(rg[:20])}...")
                
                # Also show longer text
                full_text = ' '.join(rg)
                if len(full_text) > 200:
                    print(f"  Full: {full_text[:200]}...")
                else:
                    print(f"  Full: {full_text}")
            else:
                if total - passing <= 5:
                    plain = decrypt(flat, vk, mode)
                    ic = ioc(plain)
                    print(f"\nP{pn} [{mode:8s}] kl={kl} {passing}/{total} singles | IoC={ic:.4f} | {len(combos)} combos tested, none fix all singletons")
    
    print(f"\n{'='*80}")
    print("REFINEMENT COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
