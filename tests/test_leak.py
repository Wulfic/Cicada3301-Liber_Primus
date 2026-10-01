"""Stage H: what separates the 86 surviving doublets (predictions declared in TODO.md before the run, 2026-10-01).

Each verdict test pins the observed numbers and asserts the pre-declared verdict rule. Each statistic also has a
positive control: a synthetic stream with the effect built in must be detected.
"""

from __future__ import annotations

import math
import random
import unittest
from itertools import islice

from tools.lpcore import ciphers, keys, leak, stats
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N, runes_to_indices
from tools.lpcore.leak import Pair
from tools.lpcore.solved import DIVINITY, SOLVED_SECTIONS, decrypt_section
from tools.lpcore.verify import load_translation

CORPUS = load_corpus()
PAIRS = leak.adjacent_pairs(CORPUS)
BONFERRONI_L3 = 0.01 / 62           # 31 periods × 2 indexings
CIRCUMFERENCES = tuple(runes_to_indices("ᚳᛁᚱᚳᚢᛗᚠᛖᚱᛖᚾᚳᛖᛋ"))


def synthetic_pairs(doublet_at: set[int], n: int = 12000, line_every: int = 25) -> list[Pair]:
    """n pairs in one segment; doublets at the given positions, Δ = 1 elsewhere; a line break every `line_every`."""
    return [Pair(0, i, i, 0, 0 if i in doublet_at else 1, i % line_every == line_every - 1, False) for i in range(n)]


def lp_plaintext() -> list[int]:
    translation = load_translation()
    plain: list[int] = []
    for section in SOLVED_SECTIONS:
        words, english = decrypt_section(CORPUS, translation, section)
        plain += [r for w in words[:len(english)] for r in w]
    return plain


class TestHelpers(unittest.TestCase):
    def test_layout_agrees_with_the_word_parser(self) -> None:
        layout = leak.rune_layout(CORPUS)
        self.assertEqual(len(layout), len(CORPUS.all_runes()))
        for w in CORPUS.rune_words():
            self.assertEqual(layout[w.rune_offset], (w.scan, w.line), w.text)

    def test_pairs_reproduce_the_fingerprint(self) -> None:
        self.assertEqual(len(PAIRS), 12947)
        self.assertEqual(sum(p.is_doublet for p in PAIRS), 86)

    def test_tail_probabilities(self) -> None:
        self.assertAlmostEqual(leak.binom_sf(1, 3, 0.5), 7 / 8)
        self.assertAlmostEqual(leak.binom_cdf(1, 3, 0.5), 4 / 8)
        direct = 1 - sum(math.exp(-15) * 15 ** j / math.factorial(j) for j in range(20))
        self.assertAlmostEqual(leak.poisson_sf(20, 15.0), direct, places=12)
        self.assertAlmostEqual(leak.chi2_sf_even_df(3.0, 2), math.exp(-1.5))
        self.assertAlmostEqual(leak.chi2_sf_even_df(15.507, 8), 0.05, places=3)   # table value
        with self.assertRaises(ValueError):
            leak.chi2_sf_even_df(1.0, 3)

    def test_key_switch_mechanics(self) -> None:
        plain = lp_plaintext()
        k1 = [DIVINITY[i % 8] for i in range(len(plain))]
        # Key 2 = key 1: the switch changes nothing, so the stream is plain key-1 encryption.
        self.assertEqual(leak.key_switch_ideal(plain, k1, k1), [(p + k) % N for p, k in zip(plain, k1)])
        # Key 2 = key 1 + 1 everywhere: a switched rune can never equal the previous one.
        k2 = [(k + 1) % N for k in k1]
        self.assertEqual(leak.doublet_rate(leak.key_switch_ideal(plain, k1, k2))[0], 0)


class TestPositiveControls(unittest.TestCase):
    def test_l1_detects_a_nudge(self) -> None:
        # 361 would-be doublets pushed to Δ = +1 on top of a flat background.
        pairs = [Pair(0, i, i, 0, i % 28 + 1, False, False) for i in range(12586)]
        pairs += [Pair(0, 0, 0, 0, 1, False, False)] * 361
        self.assertGreater(max(leak.delta_z_scores(pairs)), 3.5)

    def test_l2_detects_a_per_line_rule(self) -> None:
        # Line-break pairs every 25th position; 3.45 % of them are doublets, none within lines.
        breaks = [i for i in range(12000) if i % 25 == 24]
        stats = leak.doublets_by_break(synthetic_pairs(set(breaks[::29])))
        self.assertGreaterEqual(stats["line-break"][0] / stats["line-break"][1], 0.025)

    def test_l3_detects_a_period(self) -> None:
        top, p = leak.phase_test(synthetic_pairs(set(range(0, 12000, 5 * 28))), 5, along_stream=True)
        self.assertEqual(top, 86)
        self.assertLess(p, BONFERRONI_L3)

    def test_l4_detects_clustering(self) -> None:
        clustered = set(range(0, 12000, 1000)) | set(range(3000, 3086))
        self.assertGreater(leak.dispersion_index(synthetic_pairs(clustered), 500), 2.0)


class TestLeakVerdicts(unittest.TestCase):
    def test_l1_suppressed_doublets_spread_evenly(self) -> None:
        counts = leak.delta_counts(PAIRS)
        self.assertEqual(counts[0], 86)
        z = leak.delta_z_scores(PAIRS)
        self.assertEqual(max(range(1, N), key=lambda d: abs(z[d])), 17)   # 404, the largest deviation (low)
        self.assertLess(max(abs(v) for v in z), 3.5)                     # verdict: no nudge

    def test_l2_rule_spans_line_and_page_breaks(self) -> None:
        stats = leak.doublets_by_break(PAIRS)
        self.assertEqual(stats, {"within-line": (82, 12362), "line-break": (4, 585), "page-break": (0, 48)})
        within = stats["within-line"][0] / stats["within-line"][1]
        hits, n = stats["line-break"]
        self.assertLess(hits / n, 0.025)                                  # verdict: not a per-line rule
        self.assertGreater(leak.binom_sf(hits, n, within), 0.01)

    def test_l3_no_period_in_survivor_positions(self) -> None:
        results = [leak.phase_test(PAIRS, m, along) for along in (False, True) for m in range(2, 33)]
        best = min(p for _, p in results)
        self.assertGreater(best, BONFERRONI_L3)                           # verdict: no period
        self.assertAlmostEqual(best, 0.0355, places=3)                    # m = 27 along the stream

    def test_l4_survivors_are_homogeneous_and_unclustered(self) -> None:
        chi2, df, p = leak.section_chi2(PAIRS)
        self.assertEqual(df, 8)
        self.assertAlmostEqual(chi2, 5.33, places=2)
        self.assertGreater(p, 0.01)                                       # promotes C6 to a test
        self.assertTrue(0.5 <= leak.dispersion_index(PAIRS, 500) <= 2.0)

    def test_l5_key_switch_cannot_leave_86_doublets(self) -> None:
        plain = lp_plaintext()
        n = len(plain)
        self.assertEqual(n, 2901)
        key_pairs = {
            "DIVINITY/CIRCUMFERENCES": ([DIVINITY[i % 8] for i in range(n)], [CIRCUMFERENCES[i % 14] for i in range(n)]),
            # Degenerate: φ(p) = p − 1, so key 2 is always key 1 + 1 and no switched rune can repeat.
            "phi(prime)/primes": ([k % N for k in islice(ciphers.totient_prime_stream(), n)],
                                  [k % N for k in islice(ciphers.primes(), n)]),
        }
        observed = {}
        for name, (k1, k2) in key_pairs.items():
            for kind, encrypt in (("ideal", leak.key_switch_ideal), ("literal", leak.key_switch_literal)):
                hits, total = leak.doublet_rate(encrypt(plain, k1, k2))
                observed[name, kind] = (hits, total)
                with self.subTest(keys=name, kind=kind):
                    self.assertLess(leak.poisson_sf(86, hits / total * len(PAIRS)) if hits else 0.0, 1e-6)
        self.assertEqual(observed["DIVINITY/CIRCUMFERENCES", "ideal"], (6, 2900))
        self.assertEqual(observed["DIVINITY/CIRCUMFERENCES", "literal"], (10, 2898))
        self.assertEqual(observed["phi(prime)/primes", "ideal"], (0, 2900))


class TestC3MarkerLetter(unittest.TestCase):
    """Stage Q (declared in TODO.md): do the survivors mark one plaintext letter x?

    Model M_x: c_i = c_{i−1} + (p_i − x)·k_i, k_i ≠ 0, so a doublet sits exactly where p_i = x. x is excluded if
    the count is off (two-sided Poisson p < 10⁻⁶) or the doublets' word positions are not x's (LLR ≤ −10).
    """

    COUNT_P = 1e-6
    LLR_EXCLUDE = -10.0
    WORDS = keys.solved_plaintext_words(CORPUS, load_translation())
    NG, IA, EA = 21, 27, 28

    @classmethod
    def letter_rate(cls, x: int) -> float:
        return sum(w.count(x) for w in cls.WORDS) / sum(len(w) for w in cls.WORDS)

    @staticmethod
    def count_p(lam: float) -> float:
        return min(1.0, 2 * min(leak.poisson_cdf(86, lam), leak.poisson_sf(86, lam))) if lam else 0.0

    def test_helpers(self) -> None:
        self.assertEqual([leak.word_class(i, 3) for i in range(3)], ["initial", "medial", "final"])
        self.assertEqual(leak.word_class(0, 1), "sole")
        with self.assertRaises(ValueError):
            leak.word_class(2, 2)
        self.assertEqual(leak.word_stream_doublet_classes([(1, 2), (2,), (2, 3, 3)]), ["sole", "initial", "final"])
        direct = sum(math.exp(-20) * 20 ** j / math.factorial(j) for j in range(9))
        self.assertAlmostEqual(leak.poisson_cdf(8, 20.0), direct, places=12)
        self.assertAlmostEqual(leak.poisson_cdf(86, 196.4) + leak.poisson_sf(87, 196.4), 1.0, places=12)
        with self.assertRaises(ValueError):
            leak.marker_letter_llr(["medial"], self.WORDS, 25)          # AE never occurs in the plaintext

    def test_controls(self) -> None:
        # Positive: run M_x itself over the solved text five times (12,956 runes in words). Negative: 86 doublets
        # at random rune positions of the same text. Only NG, IA and EA need the positional rule (see the verdict).
        rng = random.Random(3)
        words = (self.WORDS * 5)
        for x in (self.NG, self.IA, self.EA):
            c, cipher_words = 0, []
            for w in words:
                out = []
                for p in w:
                    c = (c + (p - x) * rng.randrange(1, N)) % N
                    out.append(c)
                cipher_words.append(out)
            positive = leak.word_stream_doublet_classes(cipher_words)
            self.assertEqual(len(positive), 5 * sum(w.count(x) for w in self.WORDS))
            cells = [leak.word_class(i, len(w)) for w in words for i in range(len(w))]
            negative = rng.sample(cells, 86)
            with self.subTest(letter=x):
                self.assertGreaterEqual(leak.marker_letter_llr(positive[:86], self.WORDS, x), 10.0)
                self.assertLessEqual(leak.marker_letter_llr(negative, self.WORDS, x), self.LLR_EXCLUDE)

    def test_every_letter_is_excluded(self) -> None:
        classes = leak.doublet_classes(CORPUS)
        self.assertEqual(sorted(classes), sorted(["initial"] * 23 + ["medial"] * 44 + ["final"] * 19))
        not_by_count = []
        for x in range(N):
            lam = self.letter_rate(x) * len(PAIRS)
            if self.count_p(lam) < self.COUNT_P:
                continue
            not_by_count.append(x)
            with self.subTest(letter=x):
                self.assertLessEqual(leak.marker_letter_llr(classes, self.WORDS, x), self.LLR_EXCLUDE)
        self.assertEqual(not_by_count, [self.NG, self.IA, self.EA])     # EA's rate matches 0.66 %: coincidence
        llr = {x: round(leak.marker_letter_llr(classes, self.WORDS, x), 1) for x in not_by_count}
        self.assertEqual(llr, {self.NG: -106.4, self.IA: -149.4, self.EA: -67.7})

    def test_f_would_end_two_rune_words(self) -> None:
        # M_F: OF and IF would put doublets at the end of 2-rune words. LP2 has 448 two-rune words; 10 of the 178 in
        # the solved text end in F, so M_F predicts about 25. One is observed.
        two = [w for w in self.WORDS if len(w) == 2]
        lp2_two = [w.runes for s in stats.UNSOLVED_SEGMENTS for w in CORPUS.rune_words(s) if len(w.runes) == 2]
        predicted = len(lp2_two) * sum(w[1] == 0 for w in two) / len(two)
        self.assertEqual((len(lp2_two), len(two)), (448, 178))
        self.assertAlmostEqual(predicted, 25.2, places=1)
        observed = 0
        for s in stats.UNSOLVED_SEGMENTS:
            cells = [(r, i, len(w.runes)) for w in CORPUS.rune_words(s) for i, r in enumerate(w.runes)]
            observed += sum(a == b and (i, size) == (1, 2) for (a, _, _), (b, i, size) in zip(cells, cells[1:]))
        self.assertEqual(observed, 1)
        self.assertLess(leak.poisson_cdf(observed, predicted), 1e-6)


class TestC14SkipNext(unittest.TestCase):
    """Stage O (declared in TODO.md): is the re-keying 'skip to the next key value'? Excluded if LLR ≤ −10."""

    @staticmethod
    def repeating_key(n: int, repeat: float, seed: int) -> list[int]:
        rng = random.Random(seed)
        key = [rng.randrange(N)]
        for _ in range(n - 1):
            key.append(key[-1] if rng.random() < repeat else rng.randrange(N))
        return key

    @staticmethod
    def as_pairs(c: list[int]) -> list[Pair]:
        return [Pair(0, i, i, c[i], c[i + 1], False, False) for i in range(len(c) - 1)]

    def test_controls(self) -> None:
        plain = lp_plaintext()
        dp = stats.difference_distribution(plain)
        big = (plain * 5)[:12956]
        for seed in (1, 2, 3):
            skip = keys.encrypt_dodging(big, self.repeating_key(2 * len(big), 0.19, seed), keep=0.0, seed=seed)
            fresh = keys.encrypt_dodging(big, keys.random_key(2 * len(big), seed), keep=0.19, seed=seed, rekey="fresh")
            with self.subTest(seed=seed):
                self.assertGreaterEqual(leak.skip_next_llr(self.as_pairs(skip), dp), 10.0)
                self.assertLessEqual(leak.skip_next_llr(self.as_pairs(fresh), dp), -10.0)
                # A skip-next rule with a 19 %-repeating key reproduces LP2's doublet rate by itself.
                rate = sum(a == b for a, b in zip(skip, skip[1:])) / (len(skip) - 1)
                self.assertTrue(0.005 < rate < 0.009)

    def test_skip_next_is_excluded(self) -> None:
        dp = stats.difference_distribution(lp_plaintext())
        llr = leak.skip_next_llr(PAIRS, dp)
        self.assertLessEqual(llr, -10.0)                                        # verdict: excluded
        self.assertAlmostEqual(llr, -21.34, delta=0.01)

    def test_exclusion_survives_a_held_out_model(self) -> None:
        # Δp model from disjoint halves of the solved text: LP2 stays ≤ −10 under both. (Out-of-sample controls
        # score +7…+29, lower than in-sample but never negative.)
        translation = load_translation()
        others = [s.segment for s in SOLVED_SECTIONS if s.segment not in (1, 3)]
        halves = (keys.solved_plaintext_words(CORPUS, translation, exclude=others),
                  keys.solved_plaintext_words(CORPUS, translation, exclude=(1, 3)))
        for words in halves:
            dp = stats.difference_distribution([r for w in words for r in w])
            self.assertLessEqual(leak.skip_next_llr(PAIRS, dp), -10.0)


if __name__ == "__main__":
    unittest.main()
