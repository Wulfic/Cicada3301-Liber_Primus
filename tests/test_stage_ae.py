"""Stage AE (TODO stage AE): periodic keys under any alphabets, every lag of the continuous stream.

Run from the repo root:  python -m unittest tests.test_stage_ae -v
"""

from __future__ import annotations

import math
import unittest

import numpy as np

from tools import run_stage_ae as ae
from tools.lpcore import stats
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


if __name__ == "__main__":
    unittest.main()
