"""Tests for stage V: Quagmire with named keyword alphabets, scored with labels (TODO stage V, findings §20).

The vectorised best LLR over mode × offset must equal a brute-force `stats.unigram_llr` for any member, and the
identity member must reproduce C13's numbers.
"""

from __future__ import annotations

import itertools
import random
import unittest

import numpy as np

from tools import run_stage_v
from tools.lpcore import detect, quagmire, stats
from tools.lpcore.gematria import N
from tools.lpcore.solved import DIVINITY

FAMILIES = run_stage_v.families()
NAMES, ALPH = run_stage_v.alphabets()


def brute_best(counts: list[int], b: list[float], pi1: list[int], pi2: list[int], pi3: list[int]) -> float:
    best = -np.inf
    for mode, (s, t) in quagmire.MODE_SIGNS.items():
        for a in range(N):
            r = [0.0] * N
            for p, k in itertools.product(range(N), range(N)):
                r[pi2[(s * pi1[p] + t * pi3[k] + a) % N]] += run_stage_v.Q[p] * b[k]
            best = max(best, stats.unigram_llr(counts, r))
    return best


class TestKeywordAlphabets(unittest.TestCase):
    def test_keyed_alphabet(self) -> None:
        k = quagmire.keyed_alphabet(DIVINITY)
        self.assertEqual(k[:6], [23, 10, 1, 9, 16, 26])                # D I U N T Y, repeats dropped
        self.assertEqual(sorted(k), list(range(N)))
        self.assertEqual([k[i] for i in quagmire.inverse(k)], list(range(N)))
        with self.assertRaises(ValueError):
            quagmire.keyed_alphabet([29])
        with self.assertRaises(ValueError):
            quagmire.inverse([0] * N)

    def test_declared_family_size(self) -> None:
        self.assertEqual(len(run_stage_v.keywords()), 34)
        self.assertEqual(len(NAMES), 68)
        self.assertEqual(NAMES[0], "id")
        self.assertEqual(len({tuple(p) for p in ALPH}), len(ALPH))

    def test_identity_models_equal_cipher_distribution(self) -> None:
        b = FAMILIES["hex digits"]
        models = quagmire.log_models(run_stage_v.Q, b, ALPH)
        for m, mode in enumerate(quagmire.MODE_SIGNS):
            want = np.log(N * np.array(stats.cipher_distribution(run_stage_v.Q, list(b), mode)))
            np.testing.assert_allclose(models[0, m], want, atol=1e-12)

    def test_best_llr_equals_brute_force(self) -> None:
        rng = random.Random(29)
        counts = [rng.randrange(300, 600) for _ in range(N)]
        b = FAMILIES["letters A-Z"]
        sub = np.array([ALPH[0], ALPH[5], ALPH[12]])                      # id and two keyword alphabets
        got = quagmire.best_llr(quagmire.log_models(run_stage_v.Q, b, sub), counts, sub)[0]
        for i1, i2, i3 in [(0, 0, 0), (1, 2, 0), (2, 1, 1), (1, 1, 2)]:
            with self.subTest(member=(i1, i2, i3)):
                want = brute_best(counts, list(b), list(sub[i1]), list(sub[i2]), list(sub[i3]))
                self.assertAlmostEqual(got[i1 * 3 + i3, i2], want, places=8)

    def test_chunking_does_not_change_the_result(self) -> None:
        models = quagmire.log_models(run_stage_v.Q, FAMILIES["decimal digits"], ALPH[:9])
        counts = np.array([[10 + (i * 7 + c) % 13 for c in range(N)] for i in range(3)])
        np.testing.assert_allclose(quagmire.best_llr(models, counts, ALPH[:9], budget=1),
                                   quagmire.best_llr(models, counts, ALPH[:9]))

    def test_identity_member_reproduces_c13(self) -> None:
        observed = run_stage_v.lp2_counts()
        want = {"decimal digits": -214.3, "hex digits": -19.5, "letters A-Z": -14.3, "English Latin A-Z": -121.7}
        for name, value in want.items():
            models = quagmire.log_models(run_stage_v.Q, FAMILIES[name], ALPH[:1])
            with self.subTest(family=name):
                self.assertAlmostEqual(float(quagmire.best_llr(models, observed, ALPH[:1])[0, 0, 0]), value, delta=0.1)

    def test_q_is_c13s_model(self) -> None:
        self.assertEqual(run_stage_v.Q, detect.unigram(run_stage_v.PLAIN))


if __name__ == "__main__":
    unittest.main()
