"""Stage AD (TODO stage AD): LP2's own ciphertext as the key, at any lag, forwards or backwards.

Run from the repo root:  python -m unittest tests.test_stage_ad -v
"""

from __future__ import annotations

import unittest

import numpy as np

from tools import run_stage_ad as ad
from tools.lpcore import keys
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation

TABLES = ad.score_tables(ad.plaintext_model())


class TestStageADComponents(unittest.TestCase):
    def test_score_tables_are_likelihood_ratios(self) -> None:
        for r in range(len(ad.RELATIONS)):
            for a in (0, 13, 28):
                self.assertAlmostEqual(float(np.exp(TABLES[r, a]).sum()), N, places=9)    # E_flat[e^s] = 1

    def test_each_relation_recovers_its_plaintext(self) -> None:
        """For every relation, the combination x of (c_i, c_j) maps back to p_j through x − a or a − x."""
        rng = np.random.default_rng(1)
        for r, rel in enumerate(ad.RELATIONS):
            for _ in range(200):
                p, ci, a = (int(v) for v in rng.integers(0, N, 3))
                cj = ad.encipher_rune(p, ci, rel, a)
                x = ad.combine(np.array([ci]), np.array([cj]))[r][0]
                implied = (x - a) % N if rel in ("diff", "sum") else (a - x) % N
                self.assertEqual(implied, p, (rel, p, ci, a))

    def test_autokey_streams_follow_the_relation_except_at_redraws(self) -> None:
        rng = np.random.default_rng(2)
        plain = rng.integers(0, N, 3000).tolist()
        for rel in ad.RELATIONS:
            c = ad.autokey_encipher(plain, rel, 5, rng, lag=40)
            ok = [ad.encipher_rune(plain[j], int(c[j - 40]), rel, 5) == c[j] for j in range(40, 3000)]
            self.assertGreater(np.mean(ok), 0.95)
            self.assertLess(np.mean(ok), 1.0)                     # the rule re-drew some doublets

    def test_planted_cells_score_high_and_scans_agree(self) -> None:
        rng = np.random.default_rng(3)
        texts = ad.Plaintexts.__new__(ad.Plaintexts)
        texts.words = keys.solved_plaintext_words(load_corpus(), load_translation())
        plain = texts.draw("L", 4000, rng)
        for orientation in ad.ORIENTATIONS:
            i, j = ad.reuse_positions(4000, 300, rng)
            c = ad.autokey_encipher(plain, "sumrev", 7, rng, reuse=(orientation, i, j, 300))
            self.assertGreater(ad.planted_S(c, TABLES, orientation, i, j, 300, "sumrev", 7), ad.PASS)
        c = ad.autokey_encipher(plain, "diffrev", 3, rng, lag=500)
        F, _ = ad.forward_scan(c, TABLES, [500])
        self.assertAlmostEqual(F[0, 1, 3], ad.planted_F(c, TABLES, 500, "diffrev", 3), places=9)
        self.assertGreater(F[0, 1, 3], 100)
        self.assertLess(F[0, 0, 3], -100)                         # the wrong relation scores like noise


if __name__ == "__main__":
    unittest.main()
