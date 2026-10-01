#!/usr/bin/env python3
"""Deterministic substitution + digraph sweep for top refined p21 candidates.

Reads `data/p21_bounded_refine_cond_fskip_top_results.txt`, extracts the top-N
`Snippet:` entries, applies a parameter grid of deterministic text transforms,
scores each variant using a quadgram model and lexical hits, and writes a
ranked output to `data/p21_refined_subsweep_top{N}.txt`.

Usage: python tools/p21_refined_subsweep.py --top 10
"""
import argparse
import itertools
import re
from pathlib import Path
import json
import sys

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
TOOLS = BASE / 'tools'
sys.path.insert(0, str(TOOLS))

import refine_and_batch as ref
import mono_sub_solver as mss
import solve_p21_30 as solver


def parse_refined_snippets(path, top_n=10):
    txt = Path(path).read_text(encoding='utf-8')
    snippets = []
    seen = set()
    for line in txt.splitlines():
        if line.startswith('Snippet:'):
            s = line.split('Snippet:', 1)[1].strip()
            if s and s not in seen:
                snippets.append(s)
                seen.add(s)
            if len(snippets) >= top_n:
                break
    return snippets


def build_trigram_set(corpus_text):
    txt = ''.join(ch for ch in corpus_text.upper() if 'A' <= ch <= 'Z')
    return set(txt[i:i+3] for i in range(len(txt)-2))


def apply_params(translit, params):
    t = translit.lower()
    # ph_map: if 'F' then replace 'ph' -> 'f'
    if params.get('ph_map') == 'F':
        t = t.replace('ph', 'f')
    # j_map: if 'I' map j->i
    if params.get('j_map') == 'I':
        t = t.replace('j', 'i')
    if params.get('k2c'):
        t = t.replace('k', 'c')
    if params.get('u2v'):
        t = t.replace('u', 'v')
    if params.get('x_rm'):
        t = t.replace('x', '')
    if params.get('f_rm'):
        t = t.replace('f', '')
    if params.get('dup_reduce'):
        t = re.sub(r'(.)\1+', r'\1', t)
    # simple final-e strip: remove trailing 'e'
    if params.get('final_e_strip') and t.endswith('e'):
        t = t[:-1]
    # normalize to letters only
    t = ''.join(ch for ch in t if 'a' <= ch <= 'z')
    return t


def score_variant(text, qg, floor, tri_set, common_words):
    # quadgram score (higher is better)
    qscore = mss.score_by_quadgram(text.upper(), qg, floor)
    # lexical hits (count occurrences of common words)
    lex = 0
    low = text.lower()
    for w in common_words:
        lw = w.lower()
        if len(lw) < 2:
            continue
        if lw in low:
            lex += low.count(lw)
    # trigram matches
    tri = 0
    for i in range(len(text)-2):
        if text[i:i+3].upper() in tri_set:
            tri += 1
    # composite score: prioritize quadgram, boost by lexical hits
    composite = qscore + lex * 8 + tri * 0.05
    return composite, qscore, lex, tri


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top', type=int, default=10)
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    # choose source refine file (prefer conditional fskip results)
    candidate_files = [
        DATA / 'p21_bounded_refine_cond_fskip_top_results.txt',
        DATA / 'p21_bounded_refine_top_results.txt'
    ]
    src = None
    for p in candidate_files:
        if p.exists():
            src = p
            break
    if src is None:
        print('No bounded-refine source file found in data/. Aborting.')
        return

    top_n = args.top
    snippets = parse_refined_snippets(src, top_n=top_n)
    if not snippets:
        print('No snippets found in', src)
        return

    # prepare scoring models
    corpus = mss.load_corpus_text()
    qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
    tri_set = build_trigram_set(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
    solver.load_wordlist()
    common_words = solver.COMMON_WORDS

    # parameter grid (deterministic)
    grid = {
        'j_map': ['', 'I'],
        'x_rm': [True, False],
        'f_rm': [False, True],
        'ph_map': ['PH', 'F'],
        'final_e_strip': [False, True],
        'dup_reduce': [False, True],
        'k2c': [False, True],
        'u2v': [False, True],
    }

    param_names = list(grid.keys())
    combos = list(itertools.product(*(grid[n] for n in param_names)))

    results = []
    for idx, snip in enumerate(snippets, 1):
        translit = ref.transliterate_runeglish(snip)
        for combo in combos:
            params = dict(zip(param_names, combo))
            transformed = apply_params(translit, params)
            if len(transformed) < 8:
                # skip tiny results
                continue
            composite, qscore, lex, tri = score_variant(transformed, qg, floor, tri_set, common_words)
            results.append({
                'candidate_index': idx,
                'base_snippet': snip,
                'params': params,
                'transformed': transformed,
                'composite': composite,
                'qscore': qscore,
                'lex': lex,
                'tri': tri,
            })

    # sort by composite descending
    results.sort(key=lambda r: (-r['composite'], -r['lex'], -r['tri']))

    out_path = Path(args.out) if args.out else DATA / f'p21_refined_subsweep_top{top_n}.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in results[:1000]:
            line = f"SCORE={int(r['composite'])} QG={r['qscore']:.2f} LEX={r['lex']} TRI={r['tri']} PARAMS={r['params']}\n{r['transformed'].upper()}\n\n"
            f.write(line)

    print(f'Wrote {len(results)} variants, top file: {out_path}')


if __name__ == '__main__':
    main()
