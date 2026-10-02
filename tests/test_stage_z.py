"""Stage Z (TODO stage Z): word and block codebooks, tested by the repeat count K.

Run from the repo root:  python -m unittest tests.test_stage_z -v
"""

from __future__ import annotations

import csv
import unittest
from collections import Counter

import numpy as np

from tools import run_stage_z as z
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N

PLAIN = [[(2, 18), (13, 4, 10), (2, 18), (24, 4, 18), (2, 18), (13, 4, 10), (1,)],
         [(2, 18), (13, 4, 10), (24, 4, 18), (5, 3), (2, 18)]]


def naive_block_K(streams, n, mode, a):
    groups = streams if mode == "sec" else [[r for s in streams for r in s]]
    total = 0
    for g in groups:
        c = Counter(tuple(g[i:i + n]) for i in range(a, len(g) - n + 1, n))
        total += sum(v * (v - 1) // 2 for v in c.values())
    return total


class TestStageZComponents(unittest.TestCase):
    def test_declared_family_has_72_cells(self) -> None:
        cells = z.cells()
        self.assertEqual(len(cells), 72)
        self.assertEqual(len(set(cells)), 72)

    def test_block_K_matches_a_naive_count(self) -> None:
        rng = np.random.default_rng(1)
        streams = [rng.integers(0, 4, m) for m in (37, 50, 9)]
        for n in (2, 3, 5):
            for mode in z.MODES:
                for a in range(n):
                    self.assertEqual(z.block_K(streams, n, mode, a),
                                     naive_block_K([s.tolist() for s in streams], n, mode, a), (n, mode, a))

    def test_word_K_counts_pairs_of_words_of_two_or_more_runes(self) -> None:
        # section 0: (2,18)×3 → 3 pairs, (13,4,10)×2 → 1; section 1: (2,18)×2 → 1. (1,) is ignored.
        self.assertEqual(z.word_K(PLAIN, "sec"), 5)
        # across both: (2,18)×5 → 10, (13,4,10)×3 → 3, (24,4,18)×2 → 1.
        self.assertEqual(z.word_K(PLAIN, "all"), 14)

    def test_anti_doublet_is_identity_at_keep_1_and_matches_the_chain_at_keep_019(self) -> None:
        rng = np.random.default_rng(2)
        stream = rng.integers(0, N, 400_000)
        self.assertTrue(np.array_equal(z.anti_doublet(stream, rng, keep=1.0), stream))
        out = z.anti_doublet(stream, rng)
        rate = float((out[1:] == out[:-1]).mean())
        self.assertAlmostEqual(rate, z.doublet_probability(), delta=4 * np.sqrt(rate / len(out)))
        self.assertAlmostEqual(z.doublet_probability(), (0.19 + 0.81 / 29) / 29, places=12)

    def test_p_equal_is_uniform_without_the_rule_and_sums_like_a_chain(self) -> None:
        for n in (1, 2, 5):
            self.assertAlmostEqual(z.p_equal(n, keep=1.0) * N ** n, 1.0, places=12)
        self.assertGreater(z.p_equal(2), N ** -2)       # rare in-block doublets make the law less even: larger Σ P²
        # Monte Carlo: two independent 2-rune windows under the rule are equal with probability p_equal(2).
        rng = np.random.default_rng(3)
        a = z.anti_doublet(rng.integers(0, N, 2_000_000), rng)
        b = z.anti_doublet(rng.integers(0, N, 2_000_000), rng)
        eq = float(((a[0::2][:999_999] == b[0::2][:999_999]) & (a[1::2][:999_999] == b[1::2][:999_999])).mean())
        self.assertAlmostEqual(eq / z.p_equal(2), 1.0, delta=0.05)

    def test_tables_preserve_K_exactly_without_the_rule(self) -> None:
        """Positive-control logic: any injective table maps equal units to equal units, so K survives."""
        rng = np.random.default_rng(4)
        plain = [[tuple(int(x) for x in rng.integers(0, 3, int(rng.integers(1, 5)))) for _ in range(300)]
                 for _ in range(3)]
        for cell in z.cells()[:2] + [("Zb", 2, "sec", 1), ("Zb", 3, "cont", 2), ("Zb", 4, "sec", 0)]:
            cipher = z.encipher(cell, plain, rng, keep=1.0)
            self.assertEqual([[len(w) for w in s] for s in cipher], [[len(w) for w in s] for s in plain])
            self.assertEqual(z.statistic(cell, cipher), z.statistic(cell, plain), cell)

    def test_injective_table_refuses_an_impossible_map(self) -> None:
        with self.assertRaises(ValueError):
            z.injective_table([(i,) for i in range(30)], np.random.default_rng(5))
        self.assertEqual(len(set(z.injective_table([(i,) for i in range(29)], np.random.default_rng(5)).values())), 29)

    def test_log_lower_is_below_every_draw_for_tight_counts(self) -> None:
        self.assertLess(z.log_lower([100, 110, 120, 105, 95]), 95)
        self.assertGreater(z.log_lower([100, 110, 120, 105, 95]), 20)

    def test_verdict_rules(self) -> None:
        low = {"E": 50.0, "L": 60.0}
        mins = {"E": 80, "L": 90}
        self.assertEqual(z.verdict(10, 5.0, 2.0, 12, low, mins)[0], "EXCLUDED")
        self.assertEqual(z.verdict(55, 5.0, 2.0, 12, low, mins)[0], "PASS")
        self.assertEqual(z.verdict(10, 5.0, 2.0, 12, {"E": 10.0, "L": 60.0}, mins)[0], "UNTESTABLE")
        self.assertEqual(z.verdict(10, 5.0, 2.0, 12, low, {"E": 11, "L": 90})[0], "UNTESTABLE")
        self.assertEqual(z.verdict(13, 12.5, 2.0, 12, low, mins)[0], "EXCLUDED")


class TestStageZRecorded(unittest.TestCase):
    """The recorded run (findings §24): valid, no pass, 26 cells excluded and 46 untestable."""

    @classmethod
    def setUpClass(cls) -> None:
        with z.RESULTS_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = {r["cell"]: r for r in csv.DictReader(f, delimiter="	")}

    def test_recorded_headline(self) -> None:
        self.assertEqual(list(self.rows), [z.cell_name(c) for c in z.cells()])
        verdicts = Counter(r["verdict"] for r in self.rows.values())
        self.assertEqual(verdicts, Counter({"EXCLUDED": 26, "UNTESTABLE": 46}))
        self.assertTrue(all(r["validity"] in ("ok", "-") for r in self.rows.values()))
        self.assertLess(max(abs(float(r["z_null"])) for r in self.rows.values()), 1.4)
        excluded_n = {z.cell_name(c) for c in z.cells() if c[0] == "Zw" or c[1] <= 4}
        self.assertTrue(all(self.rows[name]["verdict"] == "EXCLUDED" for name in excluded_n))

    def test_lp2_counts_and_analytic_means_recompute(self) -> None:
        sections = z.lp2_sections(load_corpus())
        for cell in z.cells():
            row = self.rows[z.cell_name(cell)]
            self.assertEqual(z.statistic(cell, sections), int(row["K_LP2"]), cell)
            self.assertAlmostEqual(z.analytic_mean(cell, sections), float(row["analytic_mean"]), delta=6e-4)
            # every exclusion has LP2 below both sources' log-scale lower bound
            if row["verdict"] == "EXCLUDED":
                self.assertLess(int(row["K_LP2"]), min(float(row["E_lower"]), float(row["L_lower"])))


if __name__ == "__main__":
    unittest.main()
