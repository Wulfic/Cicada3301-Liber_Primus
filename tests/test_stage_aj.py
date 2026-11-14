"""Stage AJ (TODO stage AJ, findings §34): anatomy of the 86 surviving doublets.

Run from the repo root:  python -m unittest tests.test_stage_aj -v
"""

from __future__ import annotations

import csv
import unittest

import numpy as np

from tools import run_stage_aj as aj
from tools.lpcore.corpus import load_corpus


def read_tsv(path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


class TestStageAJMachinery(unittest.TestCase):

    def test_contiguous_positions(self) -> None:
        start, end = aj.contiguous_positions(np.array([5, 5, 5, 2, 7, 7]))
        self.assertEqual(start.tolist(), [0, 1, 2, 0, 0, 1])
        self.assertEqual(end.tolist(), [2, 1, 0, 0, 1, 0])

    def test_non_contiguous_units_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            aj.contiguous_positions(np.array([1, 2, 1]))

    def test_decile_cells_keep_ties_and_drop_empty_cells(self) -> None:
        cells, labels = aj.decile_cells(np.array([0] * 50 + list(range(1, 51))))
        self.assertEqual(len(set(cells[:50].tolist())), 1)        # all ties in one cell
        self.assertEqual(sorted(set(cells.tolist())), list(range(len(labels))))

    def test_distinct_draws_have_no_repeats(self) -> None:
        rows = aj.distinct_draws(np.random.default_rng(1), np.arange(12_947), 86, 500)   # LP2's pool size
        self.assertEqual(rows.shape, (500, 86))
        self.assertTrue(all(len(set(r.tolist())) == 86 for r in rows))

    def test_small_pool_is_refused_not_looped(self) -> None:
        with self.assertRaises(ValueError):
            aj.distinct_draws(np.random.default_rng(1), np.arange(200), 86, 1)

    def test_statistics_on_a_known_draw(self) -> None:
        cells = np.array([0, 0, 1, 1])
        tests = [aj.Test("x", "x", cells, ("a", "b")), aj.Test("t", "t", cells, ("a", "b"), "topk")]
        stats = aj.statistics(tests, np.array([[0, 1]]))
        self.assertAlmostEqual(stats[0, 0], 2.0)                  # (2-1)²/1 + (0-1)²/1
        self.assertEqual(stats[0, 1], 2)


class TestStageAJRecorded(unittest.TestCase):
    """The recorded run: valid controls, nothing fires, T4 untestable; key counts recomputed from the corpus."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = {r["test"]: r for r in read_tsv(aj.RESULTS_PATH)}
        cls.controls = read_tsv(aj.CONTROLS_PATH)

    def test_required_controls_pass(self) -> None:
        by = {(r["control"], r["test"]): int(r["fires_of_100"]) for r in self.controls}
        self.assertLessEqual(by[("negative null", "all")], aj.NEGATIVE_MAX_FIRES)
        self.assertGreaterEqual(by[("M3 pure, random 6 runes", "T2")], aj.POWER_REQUIRED)
        self.assertGreaterEqual(by[("M3 pure, named 5 runes", "T3")], aj.POWER_REQUIRED)
        self.assertEqual(by[("M3 mixture phi=0.5", "T2")], 100)

    def test_only_t4_is_untestable(self) -> None:
        weak = {r["test"] for r in self.controls
                if r["control"].startswith("planted") and int(r["fires_of_100"]) < aj.POWER_REQUIRED}
        self.assertEqual(weak, {"T4"})

    def test_nothing_fires(self) -> None:
        self.assertEqual(len(self.rows), aj.N_TESTS)
        self.assertEqual({r["status"] for r in self.rows.values()}, {"silent", "untestable"})
        self.assertGreater(min(float(r["p"]) for r in self.rows.values()), 0.01)

    def test_counts_recompute_from_the_corpus(self) -> None:
        tests, doublet = aj.build_tests(load_corpus())
        self.assertEqual((len(doublet), int(doublet.sum())), (12_947, 86))
        survivors = np.flatnonzero(doublet)
        identity = np.bincount(tests[0].cells[survivors], minlength=29)
        self.assertEqual(" ".join(map(str, identity)), self.rows["T1"]["observed"])
        self.assertEqual(int(np.sort(identity)[-aj.TOP_K:].sum()), 32)
        self.assertEqual(int(identity[list(aj.NAMED)].sum()), 10)
        self.assertEqual(np.bincount(tests[3].cells[survivors], minlength=4).tolist(), [23, 44, 19, 0])  # §15

    def test_cited_null_figures(self) -> None:
        """§34's null median of T2 (32), T3's null mean (14.9), and T4's planted χ² (about 32, under the fire line)."""
        tests, doublet = aj.build_tests(load_corpus())
        n = len(doublet)
        rng = np.random.default_rng(34)
        null = aj.statistics(tests, aj.distinct_draws(rng, np.arange(n), aj.N_SURVIVORS, 20_000))
        self.assertEqual(np.median(null[:, 1]), 32)
        self.assertAlmostEqual(aj.N_SURVIVORS * tests[0].share[list(aj.NAMED)].sum(), 14.9, places=1)
        cell0 = np.flatnonzero(tests[3].cells == 0)
        k0 = round(aj.N_SURVIVORS * (tests[3].share[0] + aj.PLANT_EXCESS))
        self.assertEqual(k0, 40)
        planted = aj.statistics(tests, aj.mixed_draws(rng, n, cell0, k0, 200,
                                                      outside=np.setdiff1d(np.arange(n), cell0)))[:, 3]
        self.assertAlmostEqual(float(np.median(planted)), 32, delta=1.5)


if __name__ == "__main__":
    unittest.main()
