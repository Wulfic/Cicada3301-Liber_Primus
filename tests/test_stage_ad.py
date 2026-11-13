"""Stage AD (TODO stage AD): LP2's own ciphertext as the key, at any lag, forwards or backwards.

Run from the repo root:  python -m unittest tests.test_stage_ad -v
"""

from __future__ import annotations

import csv
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


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


class TestStageADRecorded(unittest.TestCase):
    """The recorded run (findings §28): valid, no pass, every ciphertext-autokey hypothesis at lags 11–12,863 excluded."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lags = {int(r["lag"]): r for r in read_tsv(ad.LAGS_PATH)}
        cls.top = read_tsv(ad.TOP_PATH)
        cls.controls = read_tsv(ad.CONTROLS_PATH)
        cls.c = ad.lp2_stream(load_corpus())

    def test_recorded_headline(self) -> None:
        self.assertEqual(sorted(self.lags), list(range(11, 12_946)))
        self.assertLess(max(float(r["nats"]) for r in self.top), ad.PASS)
        column = f"excluded_of_{len(ad.RELATIONS) * N}"
        open_lags = [lag for lag, r in self.lags.items() if lag <= 12_900 and int(r[column]) < 116]
        self.assertEqual(min(open_lags), 12_864)
        self.assertEqual(sum(int(r[column]) for lag, r in self.lags.items() if lag <= 12_900), 1_495_197)
        self.assertEqual(sum(int(r[column]) for lag, r in self.lags.items() if lag <= 12_863), 1_490_948)

    def test_named_lags_recompute(self) -> None:
        for lag in ad.NAMED_LAGS:
            row = self.lags[lag]
            self.assertAlmostEqual(ad.planted_F(self.c, TABLES, lag, "diff", 0), float(row["F_diff0"]), delta=0.006)
            best = max(ad.planted_F(self.c, TABLES, lag, rel, a) for rel in ad.RELATIONS for a in range(N))
            self.assertAlmostEqual(best, float(row["F_best"]), delta=0.006)
            self.assertLess(best, -3_600)

    def test_model_check_reaches_12900_and_200(self) -> None:
        auto = [r for r in self.controls if r["kind"] == "autokey"]
        self.assertTrue(all(float(r["min"]) > ad.EXCLUDE for r in auto))           # P_max = 12,900
        reuse = {}
        for r in self.controls:
            if r["kind"] == "reuse":
                reuse.setdefault(int(r["L_or_M"]), []).append(int(r["at_least_30"]) == int(r["draws"]))
        self.assertEqual(min(m for m, ok in reuse.items() if all(ok)), 200)          # M_min


if __name__ == "__main__":
    unittest.main()
