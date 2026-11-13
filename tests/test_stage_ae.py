"""Stage AE (TODO stage AE): periodic keys under any alphabets, every lag of the continuous stream.

Run from the repo root:  python -m unittest tests.test_stage_ae -v
"""

from __future__ import annotations

import csv
import math
import unittest

import numpy as np

from tools import run_stage_ae as ae
from tools.lpcore import stats
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N


class TestStageAEComponents(unittest.TestCase):
    def test_lag_agreements_match_direct_counts(self) -> None:
        rng = np.random.default_rng(1)
        c = rng.integers(0, N, 700)
        agree = ae.lag_agreements(c)
        self.assertEqual(int(agree[0]), 700)
        for L in (1, 11, 345, 699):
            self.assertEqual(int(agree[L]), int(np.count_nonzero(c[L:] == c[:-L])), L)
        self.assertEqual(stats.lag_scan([c.tolist()], [11])[0][1], int(agree[11]))

    def test_periodic_tabula_agrees_exactly_where_the_plaintext_does(self) -> None:
        rng = np.random.default_rng(2)
        plain = rng.integers(0, 4, 2000)
        alphabets = np.argsort(rng.random((37, N)), axis=1)
        c = alphabets[np.arange(2000) % 37, plain]                 # no rule: the identity is exact
        self.assertEqual(int(ae.lag_agreements(c)[37]), int(np.count_nonzero(plain[37:] == plain[:-37])))
        c_rule = ae.periodic_tabula(plain, 37, rng)
        self.assertEqual(len(c_rule), 2000)

    def test_rules(self) -> None:
        self.assertAlmostEqual(ae.pass_threshold(12_956), 0.01 / 12_935)
        self.assertTrue(ae.excluded(345, 10_000))                  # 3.45 % against p_H = 5 %
        self.assertFalse(ae.excluded(480, 10_000))
        self.assertLess(ae.upper_p(700, 10_000, 1 / 29), 1e-30)
        self.assertGreater(ae.upper_p(345, 10_000, 1 / 29), 0.4)
        self.assertLessEqual(math.exp(ae.EXCLUDE_LOG), 4.6e-5)


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


class TestStageAERecorded(unittest.TestCase):
    """The recorded run (findings §29): valid, no pass, every lag 11–4,907 excluded under any alphabets."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lags = {int(r["lag"]): r for r in read_tsv(ae.LAGS_PATH)}
        cls.controls = read_tsv(ae.CONTROLS_PATH)

    def test_recorded_headline(self) -> None:
        self.assertEqual(sorted(self.lags), list(range(11, 12_946)))
        self.assertGreater(min(float(r["upper_p_null"]) for r in self.lags.values()), ae.pass_threshold(12_956))
        excluded = {lag for lag, r in self.lags.items() if r["verdict"] == "EXCLUDED"}
        self.assertEqual(len(excluded), 10_030)
        self.assertEqual(min(set(self.lags) - excluded), 4_908)
        self.assertTrue({1033, 1729, 3301} <= excluded)

    def test_lp2_agreements_and_verdicts_recompute(self) -> None:
        c = ae.lp2_stream(load_corpus())
        agree = ae.lag_agreements(c)
        for lag in (11, 1033, 1729, 3301, 4908, 6002, 12_589):
            row = self.lags[lag]
            n = 12_956 - lag
            self.assertEqual(int(agree[lag]), int(row["agreements"]), lag)
            self.assertEqual(ae.excluded(int(agree[lag]), n), row["verdict"] == "EXCLUDED", lag)

    def test_controls_were_caught_and_never_excluded(self) -> None:
        self.assertTrue(all(int(r["excluded"]) == 0 for r in self.controls))
        self.assertTrue(all(int(r["passed"]) == int(r["draws"]) for r in self.controls))
        self.assertGreater(min(float(r["rate_min"]) for r in self.controls), ae.P_H)


if __name__ == "__main__":
    unittest.main()
