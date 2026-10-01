"""Tests for tools/lpcore/quagmire.py and the stage U results (TODO stage U, findings §19).

U1: a Quagmire cipher is the additive cipher on π₁(p), renamed by π₂, so equality-pattern statistics cannot see π.
C17: an iid key independent of the plaintext keeps the doublet rate in [2/29 − Σb², Σb²] under any labels.
C18: under random alphabets, C10's and C13's key families still make the cipher too uneven, except letters A–Z.
"""

from __future__ import annotations

import random
import unittest

import numpy as np

from tools.lpcore import flatness, keys, leak, quagmire, stats
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation
from tools import run_stage_u

CORPUS = load_corpus()
RESULTS = run_stage_u.OUT_PATH
PLAIN = [r for w in keys.solved_plaintext_words(CORPUS, load_translation()) for r in w]
Q = np.bincount(PLAIN, minlength=N) / len(PLAIN)
LP2_DOUBLETS, LP2_PAIRS = 86, 12947


def bigrams(stream: list[int]) -> np.ndarray:
    out = np.zeros((N, N))
    for a, b in zip(stream, stream[1:]):
        out[a, b] += 1
    return out / out.sum()


def random_distribution(rng: np.random.Generator) -> np.ndarray:
    """A key distribution from very uneven (a point mass, a few values) to near flat."""
    kind = rng.integers(3)
    if kind == 0:
        b = np.zeros(N)
        b[rng.integers(N)] = 1.0
        return b
    if kind == 1:
        b = np.zeros(N)
        b[rng.choice(N, size=rng.integers(2, N + 1), replace=False)] = 1.0
        return b / b.sum()
    return rng.dirichlet(np.full(N, 10 ** rng.uniform(-1, 2)))


class TestRelabellingInvariance(unittest.TestCase):
    """U1: c = π₂(π₁(p) + κ) equals π₂ applied to the additive cipher on π₁(p), rune for rune."""

    def test_equality_statistics_cannot_see_the_alphabets(self) -> None:
        rng = random.Random(19)
        plain = PLAIN[:2900]
        key = keys.random_key(len(plain), 7)
        for trial in range(5):
            pi1, pi2 = rng.sample(range(N), N), rng.sample(range(N), N)
            quag = quagmire.encrypt(plain, key, pi1, pi2, keep=0.19, seed=trial)
            additive = keys.encrypt_dodging([pi1[p] for p in plain], key, keep=0.19, seed=trial, rekey="fresh")
            self.assertEqual(quag, [pi2[v] for v in additive])
            for lag in range(1, 11):
                self.assertEqual(stats.lag_repeats([quag], lag), stats.lag_repeats([additive], lag))
            self.assertAlmostEqual(flatness.chi2_uniform(quag)[0], flatness.chi2_uniform(additive)[0], places=9)
            for lag in (1, 5):
                self.assertAlmostEqual(stats.transition_chi2([quag], lag)[0], stats.transition_chi2([additive], lag)[0],
                                       places=6)
            # Label-dependent: the lag-1 difference histogram (C4's Δ argument, L1, C14) changes.
            self.assertNotEqual(stats.difference_distribution(quag), stats.difference_distribution(additive))

    def test_encrypt_rejects_a_non_permutation(self) -> None:
        with self.assertRaises(ValueError):
            quagmire.encrypt([1, 2], [0, 0], [0] * N, list(range(N)), keep=0.19, seed=0)


class TestC17DoubletBound(unittest.TestCase):
    def test_key_difference_distribution(self) -> None:
        rng = np.random.default_rng(1)
        for _ in range(20):
            b = random_distribution(rng)
            k = quagmire.key_difference_distribution(b)
            self.assertAlmostEqual(k.sum(), 1.0)
            fourier = np.real(np.fft.ifft(np.abs(np.fft.fft(b)) ** 2))          # (1/29)Σ_f |b̂(f)|² ω^{fe}
            np.testing.assert_allclose(k, fourier, atol=1e-12)
            lo, hi = quagmire.doublet_rate_interval(b)
            self.assertTrue(lo - 1e-12 <= k.min() and k.max() <= hi + 1e-12)

    def test_interval_holds_under_any_labels(self) -> None:
        pairs = bigrams(PLAIN)
        rng = np.random.default_rng(17)
        for _ in range(1000):
            b = random_distribution(rng)
            rate = quagmire.doublet_rate(pairs, rng.permutation(N), b)
            lo, hi = quagmire.doublet_rate_interval(b)
            self.assertTrue(lo - 1e-12 <= rate <= hi + 1e-12, (rate, lo, hi))

    def test_a_constant_key_keeps_the_plaintext_doublets(self) -> None:
        b = np.zeros(N)
        b[3] = 1.0
        rate = quagmire.doublet_rate(bigrams(PLAIN), np.random.default_rng(2).permutation(N), b)
        plain_rate = sum(x == y for x, y in zip(PLAIN, PLAIN[1:])) / (len(PLAIN) - 1)
        self.assertAlmostEqual(rate, plain_rate)

    def test_synthetic_rate_matches_the_exact_rate(self) -> None:
        rng = np.random.default_rng(5)
        plain = (PLAIN * 10)[:25000]
        pi1, pi2 = rng.permutation(N), rng.permutation(N)
        b = random_distribution(np.random.default_rng(11))
        key = list(rng.choice(N, size=len(plain), p=b))
        cipher = quagmire.encrypt(plain, key, list(pi1), list(pi2), keep=1.0, seed=0)   # keep 1.0: no dodging
        hits = sum(x == y for x, y in zip(cipher, cipher[1:]))
        want = quagmire.doublet_rate(bigrams(plain), pi1, b) * (len(plain) - 1)
        self.assertLess(abs(hits - want), 5 * want ** 0.5 + 5)

    def test_lp2_needs_a_key_at_least_as_uneven_as_english(self) -> None:
        rate = LP2_DOUBLETS / LP2_PAIRS
        self.assertAlmostEqual(quagmire.min_key_coincidence(rate), 0.06232, places=5)
        # Statistical version: excluded if even the lowest possible rate leaves P(X ≤ 86) ≤ 1e-4.
        boundary = self.coincidence_boundary()
        self.assertAlmostEqual(boundary, 0.05925, places=5)
        verdicts = {name: leak.binom_cdf(LP2_DOUBLETS, LP2_PAIRS, quagmire.doublet_rate_interval(b)[0]) <= 1e-4
                    for name, b in self.key_families().items()}
        self.assertEqual(verdicts, {"flat": True, "letters A-Z": True, "base-60 digits": True, "two-digit groups": True,
                                    "bytes": True, "English runes": False, "hex digits": False,
                                    "decimal digits": False})

    @staticmethod
    def coincidence_boundary() -> float:
        """The largest Σb² whose lowest possible doublet rate still gives P(X ≤ 86) ≤ 1e-4 (bisection)."""
        lo, hi = 1 / N, 2 / N
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if leak.binom_cdf(LP2_DOUBLETS, LP2_PAIRS, 2 / N - mid) <= 1e-4 else (lo, mid)
        return lo

    @staticmethod
    def key_families() -> dict[str, np.ndarray]:
        def vals(count: int) -> np.ndarray:
            return np.array(stats.values_distribution([1] * count))
        return {"flat": np.full(N, 1 / N), "letters A-Z": vals(26), "base-60 digits": vals(60),
                "two-digit groups": vals(100), "bytes": vals(256), "English runes": Q,
                "hex digits": vals(16), "decimal digits": vals(10)}


class TestC18Machinery(unittest.TestCase):
    def test_noncentral_cdf_matches_the_reference(self) -> None:
        lams = np.array([0.0, 0.3, 10.0, 42.5, 87.0, 300.0, 707.0])
        for df, x in ((28, 26.36), (224, 194.14), (28, 60.0), (2, 1.0)):
            got = quagmire.noncentral_cdf(x, df, lams)
            want = [flatness.noncentral_chi2_cdf(x, df, lam) for lam in lams]
            np.testing.assert_allclose(got, want, rtol=1e-9, atol=1e-300)
        with self.assertRaises(ValueError):
            quagmire.noncentral_cdf(1.0, 3, lams)

    def test_family_p_drops_only_negligible_draws(self) -> None:
        lams = np.random.default_rng(3).gamma(2.0, 150.0, size=20000)
        full = float(np.mean(quagmire.noncentral_cdf(26.36, 28, lams)))
        self.assertAlmostEqual(quagmire.family_p(26.36, 28, lams), full, delta=1e-15)

    def test_mean_noncentrality_formula(self) -> None:
        rng = np.random.default_rng(4)
        s = float(np.sum(Q ** 2))
        for b in (Q, np.array(stats.values_distribution([1] * 10)), np.array(stats.values_distribution([1] * 26))):
            lam = 12956 * quagmire.deviations(Q, b, 20000, rng, tied=False)
            want = quagmire.mean_noncentrality(12956, s, float(np.sum(b ** 2)))
            self.assertAlmostEqual(lam.mean() / want, 1.0, delta=0.03)
        self.assertLess(float(np.max(quagmire.deviations(Q, np.full(N, 1 / N), 100, rng, tied=True))), 1e-25)

    def test_deviation_matches_a_direct_convolution(self) -> None:
        rng = np.random.default_rng(8)
        b = np.array(stats.values_distribution([1] * 16))
        state = rng.bit_generator.state
        delta = quagmire.deviations(Q, b, 1, rng, tied=False)[0]
        rng.bit_generator.state = state
        p1, p3 = quagmire.random_permutations(1, rng)[0], quagmire.random_permutations(1, rng)[0]
        r = np.zeros(N)
        for p in range(N):
            for k in range(N):
                r[(p1[p] + p3[k]) % N] += Q[p] * b[k]
        self.assertAlmostEqual(delta, N * float(np.sum((r - 1 / N) ** 2)), places=12)


class TestStageUResult(unittest.TestCase):
    """Headline numbers of stage U (findings §19). Excluded means P ≤ 1e-4 on both the raw and corrected χ²."""

    def test_recorded_verdicts(self) -> None:
        rows = [line.split("\t") for line in RESULTS.read_text("utf-8").splitlines()[1:]]
        lp2 = {(r[1], r[2], r[3]): r[5].split(";")[0] for r in rows if r[0] == "lp2"}
        self.assertEqual(len(lp2), 24)
        self.assertEqual({k for k, v in lp2.items() if v != "EXCLUDED"},
                         {("letters A-Z", v, s) for v in ("I", "T") for s in ("pooled", "per-section")})
        self.assertTrue(all(v == "untestable" for k, v in lp2.items() if k[0] == "letters A-Z"))
        gates = [r for r in rows if r[0] == "gate_G3"]
        self.assertEqual(len(gates), 24)
        self.assertTrue(all(r[4] == "0/20" for r in gates))                      # no false exclusion: run valid
        self.assertEqual(sum(r[5] == "testable" for r in rows if r[0] == "gate_G2"), 20)
        worst = max(float(r[4].split(" / ")[1]) for r in rows if r[0] == "lp2" and r[1] != "letters A-Z")
        self.assertAlmostEqual(worst, 1.68e-11, delta=0.01e-11)

    def test_pooled_rows_recompute(self) -> None:
        sizes = run_stage_u.section_sizes()
        fams = run_stage_u.families()
        lp2 = [r for seg in stats.UNSOLVED_SEGMENTS for r in CORPUS.segment_runes(seg)]
        chi2 = flatness.chi2_uniform(lp2)[0]
        for f_i, name in enumerate(fams):
            if name not in ("English runes", "hex digits"):
                continue
            lams = run_stage_u.lambdas(fams[name], False, "pooled", sizes, run_stage_u.DRAWS_LP2,
                                       run_stage_u.SEED + 100 * f_i)
            with self.subTest(family=name):
                p = quagmire.family_p(chi2, flatness.DF, lams)
                self.assertLess(p, 1e-12)
                self.assertEqual(int(np.sum(lams <= flatness.lambda_max(chi2, flatness.DF, 1e-4))), 0)
        self.assertAlmostEqual(float(np.sum(fams["letters A-Z"] ** 2)), 1 / 26)


if __name__ == "__main__":
    unittest.main()
