"""Stage J: what the key's own statistics must be (rules declared in TODO.md before the run).

C10: the key is not English text (any text), as letters, prime values or φ(prime values), in any mode and shift.
C11: the cipher is not an autokey on its own ciphertext at any lag 2–1000.
Each verdict pins the observed numbers; each statistic has a positive control.
"""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
