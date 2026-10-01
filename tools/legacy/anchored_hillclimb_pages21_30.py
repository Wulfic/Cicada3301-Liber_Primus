#!/usr/bin/env python3
"""Batch anchored hillclimb across pages 21..30 and modes (sub, add, beaufort).
For each page and each mode this script:
 - decrypts using the verified key and the mode
 - generates top transposition candidate (columnar/primes) by word-score
 - transliterates candidate to ASCII
 - runs mono-sub hillclimb anchored to letters 'THE' with 20 restarts x 50k iters (1M total)
 - saves results to data/anchored_results/p{page}_{mode}.json

Run time: expect ~2-3 minutes per run (per page-mode); total depends on pages.
"""
import json, time, os, itertools, heapq, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
PAGES = BASE / 'pages'
OUT = DATA / 'anchored_results'
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE / 'tools'))
import decrypt_page_with_verified_key as dpv
import solve_p21_30 as solver
import mono_sub_solver as mss

# tokens for transliteration (greedy)
TOKENS = ['TH','NG','EO','OE','AE','IO','EA', 'F','U','O','R','C','G','W','H','N','I','J','P','X','S','T','B','E','M','L','A','Y']
PHON = {
    'F':'f','U':'u','TH':'th','O':'o','R':'r','C':'c','G':'g','W':'w',
    'H':'h','N':'n','I':'i','J':'j','EO':'e','P':'p','X':'x','S':'s',
    'T':'t','B':'b','E':'e','M':'m','L':'l','NG':'ng','OE':'o','D':'d',
    'A':'a','AE':'ae','Y':'y','IO':'io','EA':'ea'
}

def transliterate_runeglish(s):
    i = 0
    out = []
    while i < len(s):
        matched = False
        for tok in TOKENS:
            if s.startswith(tok, i):
                out.append(PHON.get(tok, tok.lower()))
                i += len(tok)
                matched = True
                break
        if not matched:
            out.append(s[i].lower())
            i += 1
    return ''.join(out)


def reverse_columnar(text_indices, width, col_order=None):
    n = len(text_indices)
    nrows = (n + width - 1) // width
    full_cols = n % width if n % width != 0 else width
    if col_order is None:
        col_order = list(range(width))
    col_lengths = []
    for c in range(width):
        if n % width == 0:
            col_lengths.append(nrows)
        else:
            if c < full_cols:
                col_lengths.append(nrows)
            else:
                col_lengths.append(nrows - 1)
    columns = {}
    pos = 0
    for read_idx in range(width):
        col_idx = col_order[read_idx]
        clen = col_lengths[col_idx]
        columns[col_idx] = text_indices[pos:pos+clen]
        pos += clen
    result = []
    for row in range(nrows):
        for col in range(width):
            if row < len(columns.get(col, [])):
                result.append(columns[col][row])
    return result


def build_words_struct_from_runes(text):
    words = []
    current = []
    for ch in text:
        if ch in dpv.RUNE_TO_IDX:
            current.append(dpv.RUNE_TO_IDX[ch])
        elif ch in '- .\n\r':
            if current:
                words.append(current)
                current = []
    if current:
        words.append(current)
    return words


def words_from_indices(words_struct, indices):
    pos = 0
    res = []
    for w in words_struct:
        chunk = indices[pos:pos+len(w)]
        text = ''.join(dpv.IDX_TO_LETTER[i] for i in chunk)
        res.append((text, chunk))
        pos += len(w)
    return res


def generate_transposition_candidates(plain, words_struct, solver_mod, max_keep=5):
    candidate_heap = []
    def push_candidate(score, desc, inds):
        heapq.heappush(candidate_heap, (-score, desc, inds))
        if len(candidate_heap) > 50:
            heapq.heappop(candidate_heap)

    base_wordtuples = words_from_indices(words_struct, plain)
    base_score = solver_mod.score_word_sequence(base_wordtuples)
    push_candidate(base_score, 'base', plain)

    widths = [2,3,4,5,6,7]
    for w in widths:
        if w >= len(plain):
            continue
        rev = reverse_columnar(plain, w)
        wt = words_from_indices(words_struct, rev)
        s = solver_mod.score_word_sequence(wt)
        push_candidate(s, f'columnar_w{w}_natural', rev)

        rev2 = reverse_columnar(plain, w, list(range(w-1, -1, -1)))
        wt2 = words_from_indices(words_struct, rev2)
        s2 = solver_mod.score_word_sequence(wt2)
        push_candidate(s2, f'columnar_w{w}_reversed', rev2)

        if w <= 7:
            best_local = []
            for perm in itertools.permutations(range(w)):
                rev3 = reverse_columnar(plain, w, list(perm))
                wt3 = words_from_indices(words_struct, rev3)
                s3 = solver_mod.score_word_sequence(wt3)
                if s3 >= base_score:
                    best_local.append((s3, perm, rev3))
            best_local.sort(reverse=True, key=lambda x: x[0])
            for s3, perm, rev3 in best_local[:3]:
                push_candidate(s3, f'columnar_w{w}_perm={perm}', rev3)

    # prime-based reorderings
    primes0 = [i for i in range(len(plain)) if solver_mod.is_prime(i)]
    non_primes = [i for i in range(len(plain)) if i not in set(primes0)]
    if primes0:
        reorder1 = [plain[i-1] for i in range(2, len(plain)+1) if solver_mod.is_prime(i)] + [plain[i] for i in range(len(plain)) if i not in set(primes0)]
        wt4 = words_from_indices(words_struct, reorder1)
        s4 = solver_mod.score_word_sequence(wt4)
        push_candidate(s4, 'prime_first', reorder1)

        reorder2 = list(plain)
        prime_vals = [plain[i] for i in primes0]
        nonprime_vals = [plain[i] for i in non_primes]
        for i, p in enumerate(primes0):
            if i < len(nonprime_vals):
                reorder2[p] = nonprime_vals[i]
        for i, np_idx in enumerate(non_primes):
            if i < len(prime_vals):
                reorder2[np_idx] = prime_vals[i]
        wt5 = words_from_indices(words_struct, reorder2)
        s5 = solver_mod.score_word_sequence(wt5)
        push_candidate(s5, 'prime_nonprime_swap', reorder2)

    # return sorted candidates (desc by score)
    candidates = sorted(candidate_heap, key=lambda x: x[0])
    # normalize to (desc, score, inds)
    out = [ (desc, -neg, inds) for (neg, desc, inds) in candidates ]
    # sort by score desc
    out.sort(key=lambda x: x[1], reverse=True)
    return out[:max_keep]


def run_batch(pages=list(range(21,31)), modes=['sub','add','beaufort'], restarts=20, iters=50000, fixed_letters=set(list('THE'))):
    solver.load_wordlist()
    corpus = mss.load_corpus_text()
    qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')

    results_summary = []
    vks = dpv.load_verified_keys()

    for page in pages:
        print(f"\n=== Page {page} ===")
        key = vks.get(str(page))
        if not key:
            print(' No verified key, skipping')
            continue
        runes_text = dpv.load_page_runes(page)
        if not runes_text:
            print(' No runes.txt, skipping')
            continue
        flat = dpv.extract_indices(runes_text)
        words_struct = build_words_struct_from_runes(runes_text)

        for mode in modes:
            print(f' Page {page} mode {mode} -> generating candidates...')
            plain = dpv.decrypt_indices(flat, key, mode=mode)
            candidates = generate_transposition_candidates(plain, words_struct, solver)
            if not candidates:
                print('  No candidates found, using base')
                candidates = [('base', 0.0, plain)]
            # choose top candidate
            desc, cand_score, inds = candidates[0]
            runeg = dpv.indices_to_runeglish(inds)
            translit = transliterate_runeglish(runeg)
            cipher_text = ''.join(ch for ch in translit.upper() if 'A' <= ch <= 'Z')
            print(f"  Top candidate: {desc} (word-score={cand_score:.2f}), cipher_len={len(cipher_text)}")
            if len(cipher_text) < 20:
                print('  Cipher too short, skipping mono-sub')
                continue

            best_score = -1e12
            best_plain = None
            best_map = None
            best_restart = None
            t0 = time.time()
            for r in range(restarts):
                print(f'   restart {r+1}/{restarts}... ', end='', flush=True)
                plain_candidate, mapping, score = mss.run_hillclimb(cipher_text, qg, floor, corpus, iters=iters, fixed=fixed_letters)
                print(f'score={score:.4f}')
                if score > best_score:
                    best_score = score
                    best_plain = plain_candidate
                    best_map = mapping
                    best_restart = r+1
            elapsed = time.time() - t0

            out = {
                'page': page,
                'mode': mode,
                'candidate_desc': desc,
                'candidate_word_score': cand_score,
                'cipher_len': len(cipher_text),
                'restarts': restarts,
                'iters_per_restart': iters,
                'total_iters': restarts * iters,
                'fixed_letters': list(fixed_letters),
                'best_score': best_score,
                'best_restart': best_restart,
                'best_plain_snippet': (best_plain or '')[:2000],
                'mapping': None,
                'elapsed_s': elapsed,
                'timestamp': time.time()
            }
            try:
                out['mapping'] = mss.pretty_map(best_map) if best_map else None
            except Exception:
                out['mapping'] = str(best_map)

            out_path = OUT / f'p{page}_{mode}.json'
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(out, f, indent=2)
            print(f'  Saved result to {out_path}')
            results_summary.append(out)

    # write summary
    summary_path = OUT / 'summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, indent=2)
    print('\nBatch complete. Summary saved to', summary_path)


if __name__ == '__main__':
    # default params: 20 restarts x 50k iters -> 1,000,000 iterations per run
    run_batch()
