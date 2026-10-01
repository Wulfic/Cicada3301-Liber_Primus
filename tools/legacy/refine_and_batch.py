#!/usr/bin/env python3
"""Refinement runner: focused transposition + mono-sub for page 21,
then batch-run decrypt pipeline for pages 22-30.
"""
import sys, json, itertools, subprocess, heapq
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
PAGES = BASE / 'pages'

sys.path.insert(0, str(BASE / 'tools'))
import mono_sub_solver as mss
import solve_p21_30 as solver
import decrypt_page_with_verified_key as dpv


def load_verified_key_for(page):
    vks = dpv.load_verified_keys()
    return vks.get(str(page))


def load_page_words(page):
    text = dpv.load_page_runes(page)
    if not text:
        return None, None
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
    flat = [r for w in words for r in w]
    return flat, words


def indices_to_runeglish(indices):
    return ''.join(dpv.IDX_TO_LETTER[i] for i in indices)


TOKENS = ['TH','NG','EO','OE','AE','IO','EA', 'F','U','O','R','C','G','W','H','N','I','J','P','X','S','T','B','E','M','L','A','Y']
PHON = {
    'F':'f','U':'u','TH':'th','O':'o','R':'r','C':'c','G':'g','W':'w',
    'H':'h','N':'n','I':'i','J':'j','EO':'e','P':'p','X':'x','S':'s',
    'T':'t','B':'b','E':'e','M':'m','L':'l','NG':'ng','OE':'o','D':'d',
    'A':'a','AE':'ae','Y':'y','IO':'io','EA':'ea'
}


def transliterate_runeglish(runeglish_str):
    i = 0
    out = []
    s = runeglish_str
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


def words_from_indices(words_struct, indices):
    # words_struct is list of lists of rune indices lengths
    pos = 0
    res = []
    for w in words_struct:
        chunk = indices[pos:pos+len(w)]
        text = ''.join(dpv.IDX_TO_LETTER[i] for i in chunk)
        res.append((text, chunk))
        pos += len(w)
    return res


def refine_page21_and_batch():
    page = 21
    print(f"== Refinement: page {page} ==")
    key = load_verified_key_for(page)
    if not key:
        print('No verified key for page 21; aborting refinement')
        return

    flat, words = load_page_words(page)
    if flat is None:
        print('No runes.txt for page 21')
        return

    # decrypt with verified key (use sub mode by default)
    plain = dpv.decrypt_indices(flat, key, mode='sub')
    base_wordtuples = words_from_indices(words, plain)
    solver.load_wordlist()
    base_score = solver.score_word_sequence(base_wordtuples)
    print('Base word score:', base_score)

    # Candidate generation: columnar widths
    widths = [2,3,4,5,6,7]
    candidate_heap = []  # (-score, description, indices)
    def push_candidate(score, desc, inds):
        heapq.heappush(candidate_heap, (-score, desc, inds))
        # Keep heap to reasonable size
        if len(candidate_heap) > 30:
            heapq.heappop(candidate_heap)

    # Add base as candidate
    push_candidate(base_score, 'base', plain)

    for w in widths:
        if w >= len(plain):
            continue
        # natural column read
        rev = reverse_columnar(plain, w)
        wt = words_from_indices(words, rev)
        s = solver.score_word_sequence(wt)
        if s > base_score:
            push_candidate(s, f'columnar_w{w}_natural', rev)

        # reversed column order
        rev2 = reverse_columnar(plain, w, list(range(w-1, -1, -1)))
        wt2 = words_from_indices(words, rev2)
        s2 = solver.score_word_sequence(wt2)
        if s2 > base_score:
            push_candidate(s2, f'columnar_w{w}_reversed', rev2)

        # permutations for small widths
        if w <= 7:
            best_local = []
            for perm in itertools.permutations(range(w)):
                rev3 = reverse_columnar(plain, w, list(perm))
                wt3 = words_from_indices(words, rev3)
                s3 = solver.score_word_sequence(wt3)
                if s3 > base_score:
                    best_local.append((s3, perm, rev3))
            # keep top 3 local
            best_local.sort(reverse=True, key=lambda x: x[0])
            for s3, perm, rev3 in best_local[:3]:
                push_candidate(s3, f'columnar_w{w}_perm={perm}', rev3)

    # Prime-indexed reorders
    primes0 = [i for i in range(len(plain)) if solver.is_prime(i)]
    non_primes = [i for i in range(len(plain)) if i not in set(primes0)]
    reorder1 = [plain[i-1] for i in range(2, len(plain)+1) if solver.is_prime(i)] + [plain[i] for i in range(len(plain)) if i not in set(primes0)]
    wt4 = words_from_indices(words, reorder1)
    s4 = solver.score_word_sequence(wt4)
    push_candidate(s4, 'prime_first', reorder1)

    # prime-nonprime swap
    reorder2 = list(plain)
    prime_vals = [plain[i] for i in primes0]
    nonprime_vals = [plain[i] for i in non_primes]
    for i, p in enumerate(primes0):
        if i < len(nonprime_vals):
            reorder2[p] = nonprime_vals[i]
    for i, np_idx in enumerate(non_primes):
        if i < len(prime_vals):
            reorder2[np_idx] = prime_vals[i]
    wt5 = words_from_indices(words, reorder2)
    s5 = solver.score_word_sequence(wt5)
    push_candidate(s5, 'prime_nonprime_swap', reorder2)

    # Collect top candidates
    candidates = sorted(candidate_heap, key=lambda x: x[0])[:10]
    print('\nTop transposition candidates (by word-score):')
    for rank, (negscore, desc, inds) in enumerate(candidates, 1):
        print(f" {rank}. score={-negscore}, method={desc}")

    # Run mono-sub hillclimb on top candidates (limited)
    tops = candidates[:3]
    corpus = mss.load_corpus_text()
    qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
    best_overall = (None, -1e12, None, None)  # (desc, score, plain_text, mapping)
    for negscore, desc, inds in tops:
        runeg = indices_to_runeglish(inds)
        translit = transliterate_runeglish(runeg)
        cipher_text = ''.join(ch for ch in translit.upper() if 'A' <= ch <= 'Z')
        print(f"\nRunning mono-sub on candidate {desc}, cipher len={len(cipher_text)}")
        if len(cipher_text) < 20:
            print(' cipher too short, skipping')
            continue
        # multiple restarts
        best_score = -1e12
        best_plain = None
        best_map = None
        restarts = 6
        iters = 30000
        for r in range(restarts):
            plain_candidate, mapping, score = mss.run_hillclimb(cipher_text, qg, floor, corpus, iters=iters)
            print(f' restart {r+1}/{restarts} -> score={score}')
            if score > best_score:
                best_score = score
                best_plain = plain_candidate
                best_map = mapping
        print(' Best mono-sub score:', best_score)
        print(' Plain:', best_plain[:300])
        try:
            print(' Map:', mss.pretty_map(best_map))
        except Exception:
            pass
        if best_score > best_overall[1]:
            best_overall = (desc, best_score, best_plain, best_map)

    print('\n=== Page 21 refinement result ===')
    if best_overall[0]:
        print('Best candidate:', best_overall[0])
        print('Score:', best_overall[1])
        print('Plain snippet:', (best_overall[2] or '')[:400])


def refine_single_page(page, restarts=4, iters=20000, widths=[2,3,4,5,6,7]):
    print(f"\n== Refinement: page {page} ==")
    key = load_verified_key_for(page)
    if not key:
        print(f' No verified key for page {page}; skipping')
        return None

    flat, words = load_page_words(page)
    if flat is None:
        print(f' No runes.txt for page {page}; skipping')
        return None

    plain = dpv.decrypt_indices(flat, key, mode='sub')
    base_wordtuples = words_from_indices(words, plain)
    solver.load_wordlist()
    base_score = solver.score_word_sequence(base_wordtuples)
    print(' Base word score:', base_score)

    candidate_heap = []
    def push_candidate(score, desc, inds):
        heapq.heappush(candidate_heap, (-score, desc, inds))
        if len(candidate_heap) > 30:
            heapq.heappop(candidate_heap)

    push_candidate(base_score, 'base', plain)

    for w in widths:
        if w >= len(plain):
            continue
        rev = reverse_columnar(plain, w)
        wt = words_from_indices(words, rev)
        s = solver.score_word_sequence(wt)
        if s > base_score:
            push_candidate(s, f'columnar_w{w}_natural', rev)

        rev2 = reverse_columnar(plain, w, list(range(w-1, -1, -1)))
        wt2 = words_from_indices(words, rev2)
        s2 = solver.score_word_sequence(wt2)
        if s2 > base_score:
            push_candidate(s2, f'columnar_w{w}_reversed', rev2)

        if w <= 7:
            best_local = []
            for perm in itertools.permutations(range(w)):
                rev3 = reverse_columnar(plain, w, list(perm))
                wt3 = words_from_indices(words, rev3)
                s3 = solver.score_word_sequence(wt3)
                if s3 > base_score:
                    best_local.append((s3, perm, rev3))
            best_local.sort(reverse=True, key=lambda x: x[0])
            for s3, perm, rev3 in best_local[:3]:
                push_candidate(s3, f'columnar_w{w}_perm={perm}', rev3)

    primes0 = [i for i in range(len(plain)) if solver.is_prime(i)]
    non_primes = [i for i in range(len(plain)) if i not in set(primes0)]
    reorder1 = [plain[i-1] for i in range(2, len(plain)+1) if solver.is_prime(i)] + [plain[i] for i in range(len(plain)) if i not in set(primes0)]
    wt4 = words_from_indices(words, reorder1)
    s4 = solver.score_word_sequence(wt4)
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
    wt5 = words_from_indices(words, reorder2)
    s5 = solver.score_word_sequence(wt5)
    push_candidate(s5, 'prime_nonprime_swap', reorder2)

    candidates = sorted(candidate_heap, key=lambda x: x[0])[:10]
    print(' Top transposition candidates:')
    for rank, (negscore, desc, inds) in enumerate(candidates, 1):
        print(f"  {rank}. score={-negscore}, method={desc}")

    tops = candidates[:3]
    corpus = mss.load_corpus_text()
    qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
    best_overall = (None, -1e12, None, None)
    for negscore, desc, inds in tops:
        runeg = indices_to_runeglish(inds)
        translit = transliterate_runeglish(runeg)
        cipher_text = ''.join(ch for ch in translit.upper() if 'A' <= ch <= 'Z')
        print(f" Running mono-sub on {desc}, len={len(cipher_text)}")
        if len(cipher_text) < 20:
            continue
        best_score = -1e12
        best_plain = None
        best_map = None
        for r in range(restarts):
            plain_candidate, mapping, score = mss.run_hillclimb(cipher_text, qg, floor, corpus, iters=iters)
            print(f'  restart {r+1}/{restarts} -> score={score}')
            if score > best_score:
                best_score = score
                best_plain = plain_candidate
                best_map = mapping
        print('  Best mono-sub score:', best_score)
        print('  Plain snippet:', (best_plain or '')[:200])
        best_overall = best_overall if best_overall[1] > best_score else (desc, best_score, best_plain, best_map)

    print('\n=== Result for page', page, '===')
    if best_overall[0]:
        print(' Best candidate:', best_overall[0])
        print(' Score:', best_overall[1])
        print(' Snippet:', (best_overall[2] or '')[:400])
    return best_overall


if __name__ == '__main__':
    # Run refinement for pages 21..30
    results = {}
    for p in range(21, 31):
        res = refine_single_page(p, restarts=4, iters=20000)
        results[p] = res
    print('\n=== Summary ===')
    for p in range(21, 31):
        r = results.get(p)
        if r and r[0]:
            print(f'P{p}: best={r[0]}, score={r[1]}')
        else:
            print(f'P{p}: no candidate')
