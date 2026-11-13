"""Stage AF (TODO stage AF): a key restarting at every unit with a per-unit shift.

Run from the repo root:  python -m unittest tests.test_stage_af -v
"""

from __future__ import annotations

import csv
import unittest
from math import comb

import numpy as np

from tools import run_stage_af as af
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N
from tools.run_stage_ab import Layout


def naive(cipher, positions, max_gap):
    units = []
    for x, t in zip(cipher, positions):
        if t == 0:
            units.append([])
        units[-1].append(int(x))
    total = 0
    for g in range(af.MIN_GAP, max_gap + 1):
        for t in range(max(map(len, units))):
            values = [(u[t + g] - u[t]) % N for u in units if len(u) > t + g]
            total += sum(comb(values.count(v), 2) for v in set(values))
    return total


class TestStageAFComponents(unittest.TestCase):
    def setUp(self) -> None:
        self.positions = np.concatenate([np.arange(n) for n in (12, 9, 15, 4, 12)])
        self.rng = np.random.default_rng(1)

    def test_difference_agreements_match_a_naive_count(self) -> None:
        cipher = self.rng.integers(0, 3, len(self.positions))
        for max_gap in (2, 5, 14):
            self.assertEqual(af.difference_agreements(cipher, self.positions, max_gap),
                             naive(cipher, self.positions, max_gap), max_gap)

    def test_analytic_mean_counts_position_pairs_held_by_two_units(self) -> None:
        lengths = [12, 9, 15, 4, 12]
        pairs = 0
        for g in range(af.MIN_GAP, 14 + 1):
            for t in range(15):
                pairs += comb(sum(1 for n in lengths if n > t + g), 2)
        self.assertAlmostEqual(af.analytic_mean(lengths, 14), pairs / N)

    def test_shifted_restart_keeps_the_statistic_exactly(self) -> None:
        """The shift cancels in every within-unit difference, so S(cipher) = S(plaintext), either convention."""
        plain = self.rng.integers(0, 4, len(self.positions))
        for beaufort in (False, True):
            cipher = af.shifted_restart(plain, self.positions, beaufort, self.rng)
            self.assertEqual(af.difference_agreements(cipher, self.positions, 14),
                             af.difference_agreements(plain, self.positions, 14))
            self.assertFalse(np.array_equal(cipher, plain))


class TestStageAFRecorded(unittest.TestCase):
    """The recorded run (findings §30): valid, no pass, all five unit types excluded."""

    @classmethod
    def setUpClass(cls) -> None:
        with af.RESULTS_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = {r["unit"]: r for r in csv.DictReader(f, delimiter="\t")}

    def test_recorded_headline(self) -> None:
        self.assertEqual(list(self.rows), list(af.UNITS))
        self.assertTrue(all(r["verdict"] == "EXCLUDED" for r in self.rows.values()))
        self.assertLess(max(abs(float(r["z_null"])) for r in self.rows.values()), 1.5)

    def test_lp2_statistics_and_analytic_means_recompute(self) -> None:
        layout = Layout(load_corpus())
        for u in af.UNITS:
            row = self.rows[u]
            self.assertEqual(af.difference_agreements(layout.runes, layout.positions[u]), int(row["S_LP2"]), u)
            self.assertAlmostEqual(af.analytic_mean(layout.unit_lengths[u]), float(row["analytic_mean"]), delta=6e-4)
            self.assertLess(int(row["S_LP2"]), min(float(row["E_lower"]), float(row["L_lower"])))


if __name__ == "__main__":
    unittest.main()
