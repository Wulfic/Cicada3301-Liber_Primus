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


class TestC19RecordedVerdicts(unittest.TestCase):
    """C19: the stage V run (findings §20). LP2 is recomputed; gate and power rows are read from the TSV."""

    EXCLUDED = {"English runes": 314_432, "English prime values": 314_432, "English Latin A-Z": 314_432,
                "decimal digits": 314_432, "hex digits": 314_001, "letters A-Z": 103_864}
    MAXIMUM = {"English runes": -27.88, "English prime values": -39.25, "English Latin A-Z": -32.65,
               "decimal digits": -51.04, "hex digits": -1.18, "letters A-Z": 6.51}
    TESTABLE_SURVIVORS = {"hex digits": 135, "letters A-Z": 10_197}

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = [line.split("\t") for line in
                    run_stage_v.OUT_PATH.read_text(encoding="utf-8").splitlines()[1:]]

    def test_lp2_exclusions_recompute(self) -> None:
        observed = run_stage_v.lp2_counts()
        for name, b in FAMILIES.items():
            llr = quagmire.best_llr(quagmire.log_models(run_stage_v.Q, b, ALPH), observed, ALPH)[0]
            with self.subTest(family=name):
                self.assertEqual(llr.size, 68 ** 3)
                self.assertEqual(int((llr <= run_stage_v.EXCLUDE).sum()), self.EXCLUDED[name])
                self.assertAlmostEqual(float(llr.max()), self.MAXIMUM[name], delta=0.01)
                self.assertLess(float(llr.max()), run_stage_v.LEAD)          # no lead in any family

    def test_family_total(self) -> None:
        self.assertEqual(sum(self.EXCLUDED.values()), 1_675_593)
        self.assertEqual(6 * 68 ** 3, 1_886_592)

    def test_lp2_sits_inside_the_flat_range(self) -> None:
        # Descriptive, after the run (findings §20): LP2 spares members the way a flat cipher does.
        flats = run_stage_v.flat_counts(run_stage_v.POWER_CIPHERS, run_stage_v.SEED + 1)
        observed = run_stage_v.lp2_counts()
        want = {"hex digits": (0.9937, 0.9984, 1.0, 9), "letters A-Z": (0.2286, 0.4360, 0.9380, 15)}
        for name, (low, median, high, at_or_above) in want.items():
            models = quagmire.log_models(run_stage_v.Q, FAMILIES[name], ALPH)
            frac = (quagmire.best_llr(models, flats, ALPH) <= run_stage_v.EXCLUDE).reshape(len(flats), -1).mean(axis=1)
            lp2 = float((quagmire.best_llr(models, observed, ALPH) <= run_stage_v.EXCLUDE).mean())
            with self.subTest(family=name):
                self.assertAlmostEqual(float(frac.min()), low, delta=1e-4)
                self.assertAlmostEqual(float(np.median(frac)), median, delta=1e-4)
                self.assertAlmostEqual(float(frac.max()), high, delta=1e-4)
                self.assertEqual(int((frac >= lp2).sum()), at_or_above)

    def test_gates_passed(self) -> None:
        g1 = [r for r in self.rows if r[0] == "gate_G1"]
        self.assertEqual(len(g1), 6)
        self.assertTrue(all(r[3].endswith(" ok") for r in g1))
        g2 = {r[1]: r[3] for r in self.rows if r[0] == "gate_G2"}
        self.assertEqual(g2["hex digits"], "testable 312810 / 314432")
        self.assertEqual(g2["letters A-Z"], "testable 41792 / 314432")

    def test_recorded_survivors(self) -> None:
        members = [r for r in self.rows if r[0] == "member"]
        for name, count in self.TESTABLE_SURVIVORS.items():
            with self.subTest(family=name):
                self.assertEqual(sum(r[1] == name and r[3].endswith("testable") and "untestable" not in r[3]
                                     for r in members), count)
        self.assertEqual(len(members), sum(self.TESTABLE_SURVIVORS.values()))   # no leads, so no other rows


if __name__ == "__main__":
    unittest.main()
