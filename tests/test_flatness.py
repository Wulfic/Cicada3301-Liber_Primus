"""Tests for tools/lpcore/flatness.py and the stage T headline numbers (TODO stage T, findings §18)."""

from __future__ import annotations

import math
import random
import unittest

import numpy as np

from tools.lpcore import flatness, keys
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.stats import UNSOLVED_SEGMENTS
from tools.run_stage_s import PRIME_PHASES, family
from tools.run_stage_t import ALPHA, LP2_RUNES, MC_TRIALS, PLAIN, S, SECTIONS, SEED, pooled

CORPUS = load_corpus()
LP2 = [r for seg in UNSOLVED_SEGMENTS for r in CORPUS.segment_runes(seg)]


class TestDistributions(unittest.TestCase):
    def test_central_cdf(self) -> None:
        self.assertAlmostEqual(flatness.chi2_cdf_even(27.336, 28), 0.5, places=4)    # median of χ²₂₈
        self.assertAlmostEqual(flatness.chi2_cdf_even(41.337, 28), 0.95, places=4)
        for x in (5.0, 12.461, 26.36, 60.0):
            self.assertAlmostEqual(flatness.chi2_cdf_small(x, 28), flatness.chi2_cdf_even(x, 28), places=12)
        self.assertAlmostEqual(flatness.chi2_cdf_small(12.461, 28), 0.005, places=4)  # table: 0.5 % point
        with self.assertRaises(ValueError):
            flatness.chi2_cdf_even(10.0, 27)

    def test_noncentral_cdf_matches_simulation(self) -> None:
        self.assertEqual(flatness.noncentral_chi2_cdf(26.36, 28, 0.0), flatness.chi2_cdf_small(26.36, 28))
        rng = np.random.default_rng(1)
        shift = np.r_[math.sqrt(40.0), np.zeros(27)]
        sim = ((rng.standard_normal((200_000, 28)) + shift) ** 2).sum(axis=1)
        self.assertAlmostEqual(float(np.mean(sim <= 40.0)), flatness.noncentral_chi2_cdf(40.0, 28, 40.0), delta=0.002)

    def test_lambda_max_inverts_the_cdf(self) -> None:
        lam = flatness.lambda_max(26.36, 28, 1e-4)
        self.assertAlmostEqual(flatness.noncentral_chi2_cdf(26.36, 28, lam), 1e-4, delta=1e-9)

    def test_boundary(self) -> None:
        self.assertEqual(flatness.boundary(lambda v: 0.0 if v <= 37 else 1.0, 0.5), 37)
        self.assertEqual(flatness.boundary(lambda v: 1.0, 0.5), 0)
        with self.assertRaises(ValueError):
            flatness.boundary(lambda v: 0.0, 0.5, v_max=100)


class TestRandomTabulaModel(unittest.TestCase):
    def test_v_eff(self) -> None:
        self.assertAlmostEqual(flatness.v_eff(list(range(29)) * 3), 29.0)
        self.assertAlmostEqual(flatness.v_eff([0, 0, 0, 1]), 1.6)

    def test_mean_noncentrality_matches_exact_mixtures(self) -> None:
        # Exact λ of random-σ mixtures, averaged over draws, against n·(29Σq² − 1)/V.
        q = np.bincount(PLAIN, minlength=N) / len(PLAIN)
        rng = np.random.default_rng(7)
        for v in (29, 256):
            lams = []
            for _ in range(300):
                mix = np.mean([q[rng.permutation(N)] for _ in range(v)], axis=0)
                lams.append(LP2_RUNES * N * float(np.sum((mix - 1 / N) ** 2)))
            with self.subTest(v=v):
                self.assertAlmostEqual(np.mean(lams) / flatness.mean_noncentrality(LP2_RUNES, S, v), 1.0, delta=0.05)

    def test_gate_a_on_synthetic_ciphers(self) -> None:
        res = pooled(256, 20, SEED + 256_000)
        want = flatness.DF + flatness.mean_noncentrality(LP2_RUNES, S, 256)
        self.assertAlmostEqual(np.mean([c for c, _ in res]) / want, 1.0, delta=0.15)

    def test_additive_tabula_is_invisible(self) -> None:
        # A Latin-square tabula under a uniform key is flat: the bound says nothing about it.
        rng = random.Random(5)
        plain = [rng.choice(PLAIN) for _ in range(LP2_RUNES)]
        chi2, _ = flatness.chi2_uniform(keys.encrypt_dodging(plain, keys.random_key(LP2_RUNES, 5), keep=0.19, seed=5,
                                                             rekey="fresh"))
        self.assertLess(chi2, 60.0)


class TestStageTResult(unittest.TestCase):
    """Headline numbers of stage T (findings §18). Excluded means P ≤ 1e-4."""

    def test_lp2_statistics(self) -> None:
        chi2, n = flatness.chi2_uniform(LP2)
        self.assertEqual(n, 12956)
        self.assertAlmostEqual(chi2, 26.36, places=2)
        self.assertAlmostEqual(flatness.lambda_max(chi2, 28, ALPHA), 42.52, places=2)
        total = sum(flatness.chi2_uniform(CORPUS.segment_runes(s))[0] for s in SECTIONS)
        self.assertAlmostEqual(total, 194.14, places=2)

    def test_pooled_boundary(self) -> None:
        chi2, n = flatness.chi2_uniform(LP2)
        self.assertEqual(flatness.boundary(lambda v: flatness.random_tabula_p(chi2, n, S, v), ALPHA), 168)
        self.assertLess(flatness.random_tabula_p(chi2, n, S, 29), 1e-11)      # any ≤ 29-class key
        self.assertGreater(flatness.random_tabula_p(chi2, n, S, 255), ALPHA)  # raw bytes: not excluded

    def test_named_classings(self) -> None:
        chi2, n = flatness.chi2_uniform(LP2)
        verdict = {}
        for name, (key, _, cyclic) in family(PLAIN).items():
            stream = key if cyclic else key[:PRIME_PHASES + LP2_RUNES]
            verdict[name] = flatness.random_tabula_p(chi2, n, S, flatness.v_eff(stream)) <= ALPHA
        self.assertEqual(sorted(k for k, out in verdict.items() if not out),
                         ["hint raw", "hint-reversed raw", "page_17.bin raw", "page_21.bin raw", "page_43.bin raw"])
        self.assertEqual(sum(verdict.values()), 15)

    def test_per_section_boundary(self) -> None:
        sec = [CORPUS.segment_runes(s) for s in SECTIONS]
        sizes = [len(r) for r in sec]
        total = sum(flatness.chi2_uniform(r)[0] for r in sec)
        draws = flatness.chi2_draws(MC_TRIALS, len(SECTIONS), SEED)
        self.assertEqual(flatness.boundary(lambda v: flatness.per_section_p(total, sizes, S, v, draws), ALPHA,
                                           v_max=100_000), 174)


if __name__ == "__main__":
    unittest.main()
