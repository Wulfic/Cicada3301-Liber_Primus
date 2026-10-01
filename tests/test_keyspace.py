"""Stage J: what the key's own statistics must be (rules declared in TODO.md before the run).

C10: the key is not English text (any text), as letters, prime values or φ(prime values), in any mode and shift.
C11: the cipher is not an autokey on its own ciphertext at any lag 2–1000.
C12: no earlier ciphertext rune (lag 1–1000) chooses the alphabet, c_i = σ_{c_{i−L}}(p_i), for any σ.
Each verdict pins the observed numbers; each statistic has a positive control.
"""

from __future__ import annotations

import random
import unittest
from collections import Counter

from tools.lpcore import detect, keys, leak, stats
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N, PRIME_VALUES
from tools.lpcore.verify import load_translation

CORPUS = load_corpus()
PLAIN = [r for w in keys.solved_plaintext_words(CORPUS, load_translation()) for r in w]
Q = detect.unigram(PLAIN)
LP2 = [CORPUS.segment_runes(s) for s in stats.UNSOLVED_SEGMENTS]
MAPPINGS = {
    "letters": list(range(N)),
    "prime values": [v % N for v in PRIME_VALUES],
    "phi(prime values)": [(v - 1) % N for v in PRIME_VALUES],
}
C10_EXCLUDE = -10.0                 # nats, declared
C11_BONFERRONI = 0.01 / 1998        # lags 2..1000 × (difference, sum), declared
C12_LAGS = range(1, 1001)
C12_BONFERRONI = 0.01 / len(C12_LAGS)


def split_like_lp2(stream: list[int]) -> list[list[int]]:
    out, j = [], 0
    for s in LP2:
        out.append(stream[j:j + len(s)])
        j += len(s)
    return out


def c12_p(streams: list[list[int]], lag: int) -> float:
    return stats.chi2_sf_wilson_hilferty(*stats.transition_chi2(streams, lag))


def counts(stream: list[int]) -> list[int]:
    c = Counter(stream)
    return [c[r] for r in range(N)]


def best_llr(cnt: list[int], mapping: list[int], mode: str, lam: float) -> float:
    """The hypothesis includes an unknown constant key offset: take the most favourable of the 29."""
    return max(stats.unigram_llr(cnt, stats.running_key_distribution(Q, mapping, mode, lam, a)) for a in range(N))


class TestC10EnglishRunningKey(unittest.TestCase):
    def test_distribution_mechanics(self) -> None:
        uniform_letters = stats.running_key_distribution(Q, MAPPINGS["letters"], "sub", lam=0.0)
        self.assertAlmostEqual(max(uniform_letters), 1 / N)               # a flat key gives a flat cipher
        for mode in detect.MODES:
            self.assertAlmostEqual(sum(stats.running_key_distribution(Q, MAPPINGS["prime values"], mode)), 1.0)
        # Prime values mod 29 are not a permutation (31 ≡ 2): even a flat letter key is not flat after mapping.
        self.assertLess(len(set(MAPPINGS["prime values"])), N)
        self.assertGreater(max(stats.running_key_distribution(Q, MAPPINGS["prime values"], "sub", lam=0.0)), 1.1 / N)

    def test_positive_controls(self) -> None:
        n = len(PLAIN)
        english = [(PLAIN[i] + PLAIN[(i + 1000) % n]) % N for i in range(n)]
        self.assertGreater(best_llr(counts(english), MAPPINGS["letters"], "sub", 1.0), -C10_EXCLUDE)
        primed = [(PLAIN[i] + PRIME_VALUES[PLAIN[(i + 1000) % n]]) % N for i in range(n)]
        self.assertGreater(best_llr(counts(primed), MAPPINGS["prime values"], "sub", 1.0), -C10_EXCLUDE)
        flat = [(p + k) % N for p, k in zip(PLAIN, keys.random_key(n, 5))]
        self.assertLess(best_llr(counts(flat), MAPPINGS["letters"], "sub", 1.0), C10_EXCLUDE)

    def test_no_english_running_key(self) -> None:
        cnt = counts([r for s in LP2 for r in s])
        worst = {}
        for lam in (1.0, 0.5, 0.25):
            for name, mapping in MAPPINGS.items():
                for mode in detect.MODES:
                    llr = best_llr(cnt, mapping, mode, lam)
                    worst[lam] = max(worst.get(lam, -1e9), llr)
                    with self.subTest(lam=lam, mapping=name, mode=mode):
                        self.assertLessEqual(llr, C10_EXCLUDE)            # verdict: excluded
        self.assertAlmostEqual(worst[1.0], -255.4, delta=0.1)
        self.assertAlmostEqual(worst[0.25], -14.4, delta=0.1)


class TestC11CiphertextAutokey(unittest.TestCase):
    def p_value(self, streams: list[list[int]], lag: int, sign: int) -> float:
        chi2, _ = stats.lag_combination_chi2(streams, lag, sign)
        return leak.chi2_sf_even_df(chi2, N - 1)

    def test_positive_controls(self) -> None:
        plain = (PLAIN * 5)[:sum(map(len, LP2))]
        for lag in (7, 500):
            for sign in (1, -1):
                c = keys.random_key(lag, lag)
                for i in range(lag, len(plain)):
                    c.append((plain[i] - sign * c[i - lag]) % N)
                streams, j = [], 0
                for s in LP2:
                    streams.append(c[j:j + len(s)])
                    j += len(s)
                with self.subTest(lag=lag, sign=sign):
                    self.assertLess(self.p_value(streams, lag, sign), C11_BONFERRONI)

    def test_no_ciphertext_autokey(self) -> None:
        results = [(self.p_value(LP2, lag, sign), lag, sign) for lag in range(2, 1001) for sign in (1, -1)]
        p, lag, sign = min(results)
        self.assertGreater(p, C11_BONFERRONI)                                 # verdict: nothing flagged
        self.assertEqual((lag, sign), (880, -1))
        self.assertAlmostEqual(p, 5.59e-4, delta=0.01e-4)


class TestC12CiphertextSelectedAlphabets(unittest.TestCase):
    def test_wilson_hilferty(self) -> None:
        self.assertAlmostEqual(stats.chi2_sf_wilson_hilferty(783.0, 783), 0.5, delta=0.01)
        # Agrees with the exact even-df tail where both apply.
        for x in (700.0, 800.0, 900.0):
            self.assertAlmostEqual(stats.chi2_sf_wilson_hilferty(x, 782), leak.chi2_sf_even_df(x, 782), delta=2e-3)

    def test_calibration_on_random_streams(self) -> None:
        # Declared: about 1 % of lags at p < 0.01 (allowed 0–3 %), none flagged. Observed 0.2 %: conservative.
        ps = [c12_p(split_like_lp2(keys.random_key(sum(map(len, LP2)), 101)), lag) for lag in C12_LAGS]
        self.assertLessEqual(sum(p < 0.01 for p in ps) / len(ps), 0.03)
        self.assertGreater(min(ps), C12_BONFERRONI)

    def test_positive_controls(self) -> None:
        plain = (PLAIN * 5)[:sum(map(len, LP2))]
        for lag in (1, 500):
            rng = random.Random(lag)
            sigma = [rng.sample(range(N), N) for _ in range(N)]
            c = keys.random_key(lag, lag)
            for i in range(lag, len(plain)):
                c.append(sigma[c[i - lag]][plain[i]])
            with self.subTest(lag=lag):
                self.assertLess(c12_p(split_like_lp2(c), lag), C12_BONFERRONI)

    def test_no_ciphertext_selected_alphabet(self) -> None:
        p, lag = min((c12_p(LP2, lag), lag) for lag in C12_LAGS)
        self.assertGreater(p, C12_BONFERRONI)                                   # verdict: nothing flagged
        self.assertEqual(lag, 142)
        self.assertAlmostEqual(p, 3.92e-3, delta=0.01e-3)
        chi2, df = stats.transition_chi2(LP2, 1)
        self.assertEqual(df, 783)
        self.assertAlmostEqual(chi2, 785.5, delta=0.1)                          # lag 1 off the diagonal: flat


if __name__ == "__main__":
    unittest.main()
