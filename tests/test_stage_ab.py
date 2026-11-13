"""Stage AB (TODO stage AB): a key restarting at every section, paragraph, clause, line or page.

Run from the repo root:  python -m unittest tests.test_stage_ab -v
"""

from __future__ import annotations

import csv
import unittest
from math import comb

import numpy as np

from tools import run_stage_ab as ab
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N

LAYOUT = ab.Layout(load_corpus())


def naive_agreements(cipher, positions):
    total = 0
    for i in range(len(cipher)):
        for j in range(i + 1, len(cipher)):
            total += positions[i] == positions[j] and cipher[i] == cipher[j]
    return total


class TestStageABComponents(unittest.TestCase):
    def test_layout_matches_the_corpus(self) -> None:
        self.assertEqual(len(LAYOUT), 12_956)
        self.assertEqual(LAYOUT.section_sizes, [729, 1145, 1729, 9, 1894, 1021, 1524, 1589, 3316])
        self.assertEqual({u: len(v) for u, v in LAYOUT.unit_lengths.items()},
                         {"segment": 9, "paragraph": 15, "clause": 168, "line": 594, "page": 55})
        for u in ab.UNITS:
            self.assertEqual(sum(LAYOUT.unit_lengths[u]), 12_956)
            pos = LAYOUT.positions[u]
            self.assertEqual(int((pos == 0).sum()), len(LAYOUT.unit_lengths[u]))   # one start per unit
            self.assertTrue(np.all((pos[1:] == pos[:-1] + 1) | (pos[1:] == 0)))

    def test_agreements_match_a_naive_count(self) -> None:
        rng = np.random.default_rng(1)
        cipher = rng.integers(0, 4, 120)
        positions = np.concatenate([np.arange(n) for n in (30, 25, 40, 25)])
        self.assertEqual(ab.agreements(cipher, positions), naive_agreements(cipher, positions))

    def test_analytic_mean_counts_same_position_pairs(self) -> None:
        self.assertAlmostEqual(ab.analytic_mean([3, 2, 1]), (comb(3, 2) + comb(2, 2)) / N)
        self.assertAlmostEqual(ab.analytic_mean([5]), 0.0)

    def test_restart_cipher_keeps_agreements_under_any_alphabets(self) -> None:
        """Equal plaintext at an equal in-unit position gives equal cipher, so K(cipher) = K(plaintext) exactly."""
        rng = np.random.default_rng(2)
        positions = LAYOUT.positions["page"]
        plain = rng.integers(0, 5, len(positions))
        cipher = ab.restart_encipher(plain, positions, rng)
        self.assertEqual(ab.agreements(cipher, positions), ab.agreements(plain, positions))
        self.assertFalse(np.array_equal(cipher, plain))

    def test_rule_keeps_section_lengths_and_cuts_doublets(self) -> None:
        rng = np.random.default_rng(3)
        out = ab.with_rule(np.zeros(len(LAYOUT), dtype=np.int64), LAYOUT.section_sizes, rng)
        self.assertEqual(len(out), len(LAYOUT))
        self.assertLess(float((out[1:] == out[:-1]).mean()), 0.25)

    def test_verdict_rules(self) -> None:
        low, mins = {"E": 50.0, "L": 60.0}, {"E": 80, "L": 90}
        self.assertEqual(ab.verdict(10, 5.0, 2.0, 12, low, mins)[0], "EXCLUDED")
        self.assertEqual(ab.verdict(55, 5.0, 2.0, 12, low, mins)[0], "PASS")
        self.assertEqual(ab.verdict(10, 5.0, 2.0, 12, {"E": 10.0, "L": 60.0}, mins)[0], "UNTESTABLE")


class TestStageABRecorded(unittest.TestCase):
    """The recorded run (findings §26): valid, no pass, all five unit types excluded."""

    @classmethod
    def setUpClass(cls) -> None:
        with ab.RESULTS_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = {r["unit"]: r for r in csv.DictReader(f, delimiter="\t")}

    def test_recorded_headline(self) -> None:
        self.assertEqual(list(self.rows), list(ab.UNITS))
        self.assertTrue(all(r["verdict"] == "EXCLUDED" for r in self.rows.values()))
        self.assertLess(max(abs(float(r["z_null"])) for r in self.rows.values()), 3.0)
        for r in self.rows.values():                     # LP2 sits below the null maximum and both bounds
            self.assertLess(int(r["K_LP2"]), int(r["null_max"]))
            self.assertLess(int(r["K_LP2"]), min(float(r["E_lower"]), float(r["L_lower"])))

    def test_lp2_agreements_and_analytic_means_recompute(self) -> None:
        for u in ab.UNITS:
            row = self.rows[u]
            self.assertEqual(ab.agreements(LAYOUT.runes, LAYOUT.positions[u]), int(row["K_LP2"]), u)
            self.assertAlmostEqual(ab.analytic_mean(LAYOUT.unit_lengths[u]), float(row["analytic_mean"]), delta=6e-4)
            se = float(row["null_sd"]) / np.sqrt(ab.NULL_DRAWS)
            self.assertLessEqual(abs(float(row["null_mean"]) - float(row["analytic_mean"])), 3 * se, u)


if __name__ == "__main__":
    unittest.main()
