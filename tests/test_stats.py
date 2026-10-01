"""Tests for tools/lpcore/stats.py and regression values for the LP2 fingerprint (2026-09-29)."""

from __future__ import annotations

import math
import unittest
from collections import Counter
from itertools import islice

from tools.lpcore import ciphers
from tools.lpcore.corpus import load_corpus
from tools.lpcore.keys import solved_plaintext_words
from tools.lpcore.solved import SOLVED_SECTIONS, decrypt_section
from tools.lpcore.stats import (
    UNSOLVED_SEGMENTS,
    difference_distribution,
    doublets_by_boundary,
    fibonacci_prime_square,
    homophonic_min_chi2,
    ioc,
    lag_repeats,
    predicted_doublet_rate,
)
from tools.lpcore.verify import load_translation

CORPUS = load_corpus()
UNSOLVED = [CORPUS.segment_runes(s) for s in UNSOLVED_SEGMENTS]


def binomial_z(hits: int, pairs: int, p: float = 1 / 29) -> float:
    return (hits - pairs * p) / math.sqrt(pairs * p * (1 - p))


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
        self.assertAlmostEqual(binomial_z(86, 12947), -17.36, places=2)

    def test_per_section_table(self) -> None:
        # Tracker §3.2: (runes, doublets) per section, and the per-section z of C6 (segment 10 has no power).
        table = {s: (len(r), lag_repeats([r], 1)[0]) for s, r in zip(UNSOLVED_SEGMENTS, UNSOLVED)}
        self.assertEqual(table, {7: (729, 4), 8: (1145, 6), 9: (1729, 9), 10: (9, 0), 11: (1894, 10),
                                 12: (1021, 11), 13: (1524, 13), 14: (1589, 12), 15: (3316, 21)})
        z = [binomial_z(*lag_repeats([r], 1)) for s, r in zip(UNSOLVED_SEGMENTS, UNSOLVED) if s != 10]
        self.assertAlmostEqual(max(z), -4.15, places=2)
        self.assertAlmostEqual(min(z), -8.88, places=2)

    def test_early_and_late_sections_do_not_differ(self) -> None:
        # C6: sections 7–11 (0.53 %) against 12–15 (0.77 %), two-proportion z test.
        early = lag_repeats([CORPUS.segment_runes(s) for s in range(7, 12)], 1)
        late = lag_repeats([CORPUS.segment_runes(s) for s in range(12, 16)], 1)
        self.assertEqual((early, late), ((29, 5501), (57, 7446)))
        pooled = (early[0] + late[0]) / (early[1] + late[1])
        z = (late[0] / late[1] - early[0] / early[1]) / math.sqrt(pooled * (1 - pooled) * (1 / early[1] + 1 / late[1]))
        self.assertAlmostEqual(math.erfc(abs(z) / math.sqrt(2)), 0.099, places=3)

    def test_unigrams_are_flat(self) -> None:
        counts = Counter(r for s in UNSOLVED for r in s)
        expected = 12956 / 29
        self.assertAlmostEqual(sum((counts[r] - expected) ** 2 / expected for r in range(29)), 26.36, places=2)
        for seg, runes in zip(UNSOLVED_SEGMENTS, UNSOLVED):
            if seg != 10:
                with self.subTest(segment=seg):
                    self.assertAlmostEqual(ioc(runes), 1.0, delta=0.02)

    def test_only_lag_one_is_depleted(self) -> None:
        rates = []
        for lag in range(2, 11):
            hits, total = lag_repeats(UNSOLVED, lag)
            rates.append(hits / total)
            with self.subTest(lag=lag):
                self.assertTrue(0.030 < hits / total < 0.040, f"lag {lag}: {hits}/{total}")
        self.assertEqual((round(100 * min(rates), 2), round(100 * max(rates), 2)), (3.38, 3.69))

    def test_suppression_ignores_word_boundaries(self) -> None:
        split = doublets_by_boundary(CORPUS)
        self.assertEqual(split["within-word"], (63, 10060))
        self.assertEqual(split["across-word"], (23, 2887))
        for doublets, pairs in split.values():
            self.assertLess(doublets / pairs, 0.01)      # both far below 1/29 = 3.45 %

    def test_per_word_shift_is_excluded(self) -> None:
        # C7: one shift per word keeps Δc = Δp inside words, so the within-word doublet rate would be the
        # plaintext's own: 52 / 2,175 = 2.39 %. LP2 has 63 / 10,060 (0.63 %).
        words = solved_plaintext_words(CORPUS, load_translation())
        plain = (sum(a == b for w in words for a, b in zip(w, w[1:])), sum(len(w) - 1 for w in words))
        self.assertEqual(plain, (52, 2175))
        hits, pairs = doublets_by_boundary(CORPUS)["within-word"]
        self.assertLess(binomial_z(hits, pairs, plain[0] / plain[1]), -10)

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
        rates = {name: round(100 * predicted_doublet_rate(dp, dk), 2) for name, dk in keys.items()}
        self.assertEqual(rates, {"english running key": 3.60, "phi(prime)": 3.20, "prime values": 3.20,
                                 "random": 3.45})                         # observed: 0.66
        for name, rate in rates.items():
            with self.subTest(key=name):
                self.assertGreater(rate, 3.0)


class TestSolvedPlaintextLetters(unittest.TestCase):
    """Letter counts the skills and C2 rely on: 2,901 solved plaintext runes, three runes never used."""

    def test_letter_counts(self) -> None:
        plain = [r for w in solved_plaintext_words(CORPUS, load_translation()) for r in w]
        counts = Counter(plain)
        self.assertEqual(len(plain), 2901)
        self.assertEqual({name: counts[i] for name, i in (("AE", 25), ("EO", 12), ("OE", 22))},
                         {"AE": 0, "EO": 0, "OE": 0})
        self.assertEqual({name: counts[i] for name, i in (("J", 11), ("X", 14), ("IA", 27), ("EA", 28), ("F", 0))},
                         {"J": 3, "X": 5, "IA": 16, "EA": 18, "F": 44})
        self.assertEqual(len(counts), 26)
        self.assertAlmostEqual(counts[0] / len(plain), 0.015, places=3)   # C2: F-passthrough adds ≈ 190 ᚠ


class TestHomophonic(unittest.TestCase):
    """Stage Q (declared in TODO.md): no homophonic substitution of LP-English is flat enough. Excluded if min χ² ≥ 200."""

    def test_controls(self) -> None:
        flat, _ = homophonic_min_chi2([1 / 29] * 29, 12956)
        self.assertAlmostEqual(flat, 0.0)
        # 26 letters, three of them at double weight: one spare rune each makes the cipher exactly flat.
        q = [2 / 29] * 3 + [1 / 29] * 23 + [0.0] * 3
        chi2, alloc = homophonic_min_chi2(q, 12956)
        self.assertAlmostEqual(chi2, 0.0)
        self.assertEqual(alloc, (2, 2, 2) + (1,) * 23 + (0, 0, 0))
        with self.assertRaises(ValueError):
            homophonic_min_chi2([1.0] + [0.0] * 27, 100)

    def test_homophonic_substitution_is_excluded(self) -> None:
        counts = Counter(r for w in solved_plaintext_words(CORPUS, load_translation()) for r in w)
        total = sum(counts.values())
        chi2, alloc = homophonic_min_chi2([counts[x] / total for x in range(29)], 12956)
        self.assertAlmostEqual(chi2, 4802.0, delta=0.5)                  # LP2 observes 26.4 (C2)
        self.assertEqual({x: a for x, a in enumerate(alloc) if a > 1}, {3: 2, 18: 3})   # O ×2, E ×3: the best case
        smoothed = [(counts[x] + 1) / (total + 26) if counts[x] else 0.0 for x in range(29)]
        self.assertGreaterEqual(homophonic_min_chi2(smoothed, 12956)[0], 200.0)   # rare-letter rates, padded
        self.assertGreaterEqual(chi2, 200.0)                              # verdict: excluded


class TestFibonacciPrimeSquare(unittest.TestCase):
    def test_square_on_scan_32_is_fully_explained(self) -> None:
        cells = [int(w.text) for w in CORPUS.words if w.scan == 32 and w.kind == "number"]
        grid = [cells[i:i + 4] for i in range(0, 16, 4)]
        spiral = [(1, 1), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1),
                  (0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0)]
        self.assertEqual([grid[r][c] for r, c in spiral], fibonacci_prime_square())


if __name__ == "__main__":
    unittest.main()
