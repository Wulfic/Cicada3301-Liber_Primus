"""Tests for tools/lpcore/stats.py and regression values for the LP2 fingerprint (2026-09-29)."""

from __future__ import annotations

import unittest
from itertools import islice

from tools.lpcore import ciphers
from tools.lpcore.corpus import load_corpus
from tools.lpcore.solved import SOLVED_SECTIONS, decrypt_section
from tools.lpcore.stats import (
    UNSOLVED_SEGMENTS,
    difference_distribution,
    doublets_by_boundary,
    fibonacci_prime_square,
    ioc,
    lag_repeats,
    predicted_doublet_rate,
)
from tools.lpcore.verify import load_translation

CORPUS = load_corpus()
UNSOLVED = [CORPUS.segment_runes(s) for s in UNSOLVED_SEGMENTS]


class TestStatPrimitives(unittest.TestCase):
    def test_ioc(self) -> None:
        self.assertAlmostEqual(ioc(list(range(29)) * 100), 1.0, delta=0.02)
        self.assertEqual(ioc([5] * 50), 29.0)
        with self.assertRaises(ValueError):
            ioc([1])

    def test_lag_repeats(self) -> None:
        self.assertEqual(lag_repeats([[1, 1, 2, 2]], 1), (2, 3))
        self.assertEqual(lag_repeats([[1, 2, 1], [3]], 2), (1, 1))
        with self.assertRaises(ValueError):
            lag_repeats([[1, 2]], 0)

    def test_predicted_doublet_rate_flat_key_is_one_in_29(self) -> None:
        skewed = [0.5] + [0.5 / 28] * 28
        self.assertAlmostEqual(predicted_doublet_rate(skewed, [1 / 29] * 29), 1 / 29)
        with self.assertRaises(ValueError):
            difference_distribution([3])


class TestLP2Fingerprint(unittest.TestCase):
    """Regression values measured 2026-09-29 on canonical data; they match the 2026 community figures."""

    def test_doublet_deficit(self) -> None:
        self.assertEqual(sum(len(s) for s in UNSOLVED), 12956)
        self.assertEqual(lag_repeats(UNSOLVED, 1), (86, 12947))

    def test_only_lag_one_is_depleted(self) -> None:
        for lag in range(2, 11):
            hits, total = lag_repeats(UNSOLVED, lag)
            with self.subTest(lag=lag):
                self.assertTrue(0.030 < hits / total < 0.040, f"lag {lag}: {hits}/{total}")

    def test_suppression_ignores_word_boundaries(self) -> None:
        split = doublets_by_boundary(CORPUS)
        self.assertEqual(split["within-word"], (63, 10060))
        self.assertEqual(split["across-word"], (23, 2887))
        for doublets, pairs in split.values():
            self.assertLess(doublets / pairs, 0.01)      # both far below 1/29 = 3.45 %

    def test_no_plaintext_f_passthrough(self) -> None:
        # LP1's "plaintext F left unenciphered" would inflate ᚠ well above 1/29. It does not.
        f_count = sum(s.count(0) for s in UNSOLVED)
        self.assertEqual(f_count, 458)
        self.assertLess(f_count, 12956 / 29 + 3 * (12956 / 29) ** 0.5)

    def test_additive_ciphers_cannot_produce_the_deficit(self) -> None:
        translation = load_translation()
        plain = []
        for section in SOLVED_SECTIONS:
            words, english = decrypt_section(CORPUS, translation, section)
            plain += [r for w in words[:len(english)] for r in w]
        dp = difference_distribution(plain)
        keys = {
            "english running key": dp,
            "phi(prime)": difference_distribution([k % 29 for k in islice(ciphers.totient_prime_stream(), 15000)]),
            "prime values": difference_distribution([k % 29 for k in islice(ciphers.primes(), 15000)]),
            "random": [1 / 29] * 29,
        }
        for name, dk in keys.items():
            with self.subTest(key=name):
                self.assertGreater(predicted_doublet_rate(dp, dk), 0.03)   # observed: 0.0066


class TestFibonacciPrimeSquare(unittest.TestCase):
    def test_square_on_scan_32_is_fully_explained(self) -> None:
        cells = [int(w.text) for w in CORPUS.words if w.scan == 32 and w.kind == "number"]
        grid = [cells[i:i + 4] for i in range(0, 16, 4)]
        spiral = [(1, 1), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1),
                  (0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0)]
        self.assertEqual([grid[r][c] for r, c in spiral], fibonacci_prime_square())


if __name__ == "__main__":
    unittest.main()
