#!/usr/bin/env python3
"""Segment Runeglish text extracted from character-level prime extraction.

Usage: python tools/segment_runeglish.py <page_num> [prime_chars_0indexed|prime_chars_1indexed]
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools"))

import solve_p21_30 as solver


def segment_text(rg_text, common_words, gp_matcher, max_word_len=18):
    text = rg_text.replace(' ', '').upper()
    n = len(text)
    # dp[i] = (score, words_list)
    dp = [(-10**9, []) for _ in range(n+1)]
    dp[0] = (0, [])

    for i in range(n):
        if dp[i][0] < -1e8:
            continue
        for L in range(1, max_word_len+1):
            j = i + L
            if j > n:
                break
            w = text[i:j]
            score = 0
            if w in common_words:
                score += len(w) * 10
            else:
                matches = gp_matcher(w)
                if matches:
                    score += len(w) * 8
                elif len(w) <= 2:
                    score -= 1
                else:
                    score -= 3
            new_score = dp[i][0] + score
            if new_score > dp[j][0]:
                dp[j] = (new_score, dp[i][1] + [w])

    return dp[n]


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/segment_runeglish.py <page_num> [prime_chars_0indexed|prime_chars_1indexed]")
        return
    page = int(sys.argv[1])
    variant = sys.argv[2] if len(sys.argv) > 2 else 'prime_chars_0indexed'

    solver.load_wordlist()
    res = solver.analyze_page(page, verbose=False)
    if not res:
        print(f"No analysis result for page {page}")
        return

    char_results = res.get('char_results', [])
    picked = None
    for name, text, ioc, indices in char_results:
        if name == variant:
            picked = (name, text, ioc, indices)
            break
    if not picked and char_results:
        picked = char_results[0]

    if not picked:
        print("No character-level results found.")
        return

    name, text, ioc, indices = picked
    print(f"Selected {name} (IoC={ioc:.4f})")
    print(text[:400])

    # Try segmentation
    score, words = segment_text(text, solver.COMMON_WORDS, solver.gp_word_matches_english)
    print(f"Best segmentation score={score}")
    print(' '.join(words))
    # Show GP->English candidate matches for each token
    print("\nCandidates:")
    for w in words:
        matches = solver.gp_word_matches_english(w)
        print(f"  {w} -> {matches}")


if __name__ == '__main__':
    main()
