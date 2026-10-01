#!/usr/bin/env python3
"""Monoalphabetic substitution hillclimber for short ciphertexts.

Usage examples:
  python tools/mono_sub_solver.py -p 24 --variant prime_chars_1indexed
  python tools/mono_sub_solver.py -t PSMSOELAHHUEOTHEOXOEABBRAEOUTNMSTXCNOEEANGEOAJUOEAECTHFOOETHEACDOETHTFAEOIO
"""
import math
import random
import argparse
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / 'data'

def load_corpus_text():
    files = [DATA_DIR / 'self_reliance.txt', DATA_DIR / 'emerson_essays.txt', DATA_DIR / 'key_search_corpus.txt']
    txt = ''
    for p in files:
        if p.exists():
            txt += p.read_text(encoding='utf-8', errors='ignore') + '\n'
    return txt

def norm_letters(s):
    return ''.join([c for c in s.upper() if 'A' <= c <= 'Z'])

def build_quadgram(corpus_text):
    txt = norm_letters(corpus_text)
    counts = Counter()
    for i in range(len(txt) - 3):
        g = txt[i:i+4]
        counts[g] += 1
    total = sum(counts.values())
    floor = math.log(0.01 / total) if total > 0 else -15.0
    qg = {g: math.log(cnt / total) for g, cnt in counts.items()} if total > 0 else {}
    return qg, floor

def score_by_quadgram(text, qg, floor):
    s = 0.0
    txt = norm_letters(text)
    for i in range(len(txt)-3):
        g = txt[i:i+4]
        s += qg.get(g, floor)
    return s

def initial_mapping_from_freq(cipher_text, corpus_text):
    cipher_freq = Counter([c for c in cipher_text.upper() if 'A' <= c <= 'Z'])
    corpus_freq = Counter([c for c in norm_letters(corpus_text)])
    cipher_order = [c for c, _ in cipher_freq.most_common()]
    plain_order = [c for c, _ in corpus_freq.most_common()]
    # Fill rest of letters
    alphabet = [chr(ord('A')+i) for i in range(26)]
    for ch in alphabet:
        if ch not in cipher_order:
            cipher_order.append(ch)
        if ch not in plain_order:
            plain_order.append(ch)
    mapping = {c: p for c, p in zip(cipher_order, plain_order)}
    # Ensure complete mapping
    for ch in alphabet:
        mapping.setdefault(ch, ch)
    return mapping

def decode_with_map(cipher_text, mapping):
    out = []
    for ch in cipher_text:
        if 'A' <= ch <= 'Z':
            out.append(mapping.get(ch, '?'))
        elif 'a' <= ch <= 'z':
            up = ch.upper(); out.append(mapping.get(up, '?'))
        else:
            out.append(ch)
    return ''.join(out)

def random_swap(mapping):
    a, b = random.sample(list(mapping.keys()), 2)
    mapping[a], mapping[b] = mapping[b], mapping[a]
    return a, b

def undo_swap(mapping, a, b):
    mapping[a], mapping[b] = mapping[b], mapping[a]

def run_hillclimb(cipher_text, qg, floor, corpus_text, iters=8000, fixed=None):
    # initialize mapping
    mapping = initial_mapping_from_freq(cipher_text, corpus_text)
    cur_plain = decode_with_map(cipher_text, mapping)
    cur_score = score_by_quadgram(cur_plain, qg, floor)
    best_map = mapping.copy()
    best_score = cur_score
    best_plain = cur_plain

    T0 = 1.0
    fixed = set(fixed or [])
    keys = [k for k in mapping.keys() if k not in fixed]
    if not keys:
        keys = list(mapping.keys())

    for i in range(iters):
        T = T0 * (1 - i / iters)
        # pick two non-fixed letters to swap
        a, b = random.sample(keys, 2) if len(keys) >= 2 else random.sample(list(mapping.keys()), 2)
        # perform swap
        mapping[a], mapping[b] = mapping[b], mapping[a]
        cand_plain = decode_with_map(cipher_text, mapping)
        cand_score = score_by_quadgram(cand_plain, qg, floor)
        delta = cand_score - cur_score
        accept = False
        if delta > 0 or math.exp(delta / max(T, 1e-6)) > random.random():
            accept = True
            cur_score = cand_score
            cur_plain = cand_plain
            if cand_score > best_score:
                best_score = cand_score
                best_map = mapping.copy()
                best_plain = cand_plain
        if not accept:
            mapping[a], mapping[b] = mapping[b], mapping[a]

    return best_plain, best_map, best_score

def pretty_map(mapping):
    pairs = sorted(mapping.items())
    return ' '.join(f"{k}->{v}" for k, v in pairs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--page', type=int, help='page number to analyze')
    parser.add_argument('-v', '--variant', default='prime_chars_1indexed')
    parser.add_argument('-t', '--text', help='ciphertext to solve (overrides page)')
    parser.add_argument('--iters', type=int, default=8000)
    parser.add_argument('--restarts', type=int, default=1, help='number of restarts')
    parser.add_argument('--fixed', '-f', help='comma-separated fixed tokens or letters to anchor (e.g. THE,OUT or A,B,C)')
    args = parser.parse_args()

    if args.text:
        cipher_text = args.text.strip().upper()
    elif args.page:
        # import solver and get char stream
        import sys
        sys.path.insert(0, str(BASE / 'tools'))
        import solve_p21_30 as solver
        solver.load_wordlist()
        res = solver.analyze_page(args.page, verbose=False)
        if not res or not res.get('char_results'):
            print('No char-level results for page', args.page)
            return
        chosen = None
        for name, text, ioc, indices in res['char_results']:
            if name == args.variant:
                chosen = (name, text)
                break
        if not chosen:
            chosen = res['char_results'][0]
        cipher_text = chosen[1].upper()
    else:
        print('Provide --text or --page')
        return

    # Determine fixed anchors: either user-provided or via automatic segmentation
    fixed_chars = set()
    if args.fixed:
        for part in args.fixed.split(','):
            token = part.strip().upper()
            for ch in token:
                if 'A' <= ch <= 'Z':
                    fixed_chars.add(ch)
    else:
        try:
            import sys as _sys
            _sys.path.insert(0, str(BASE / 'tools'))
            import segment_runeglish as seg
            solver_mod = __import__('solve_p21_30')
            score_seg, seg_words = seg.segment_text(cipher_text, solver_mod.COMMON_WORDS, solver_mod.gp_word_matches_english)
            # anchor only a small, high-confidence set of tokens
            TRUSTY = {'THE','OUT','NO','DO','A','I','IN','ON','TO','OF','AND'}
            idx = 0
            for tok in seg_words:
                t = tok.upper()
                if t in TRUSTY:
                    for ch in t:
                        if 'A' <= ch <= 'Z':
                            fixed_chars.add(ch)
                idx += len(tok)
        except Exception:
            fixed_chars = set()

    corpus_text = load_corpus_text()
    qg, floor = build_quadgram(corpus_text if corpus_text else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')

    print('Cipher:', cipher_text)
    print('Building initial mapping and running hillclimb...')
    global_best_score = -1e9
    global_best_plain = None
    global_best_map = None
    for r in range(args.restarts):
        print(f' Restart {r+1}/{args.restarts}...')
        plain, mapping, score = run_hillclimb(cipher_text, qg, floor, corpus_text, iters=args.iters, fixed=fixed_chars)
        print(f'  -> score={score}')
        if score > global_best_score:
            global_best_score = score
            global_best_plain = plain
            global_best_map = mapping

    print('\nBest score:', global_best_score)
    print('Decoded:', global_best_plain)
    print('Mapping:', pretty_map(global_best_map))


if __name__ == '__main__':
    main()
