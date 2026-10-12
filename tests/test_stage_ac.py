"""Stage AC (TODO stage AC): key reuse at any lag, periods over 1,000 and reused key stretches.

Run from the repo root:  python -m unittest tests.test_stage_ac -v
"""

from __future__ import annotations

import unittest

import numpy as np

from tools import run_stage_ac as ac
from tools.lpcore.gematria import N

TABLES = ac.score_tables(ac.plaintext_model())


def brute_max_segment(v):
    best = -np.inf
    for i in range(len(v)):
        for j in range(i, len(v)):
            best = max(best, float(np.sum(v[i:j + 1])))
    return max(best, 0.0)          # the empty segment counts, as in the cumulative-sum form


class TestStageACComponents(unittest.TestCase):
    def test_score_tables_are_likelihood_ratios(self) -> None:
        for r in range(len(ac.RELATIONS)):
            for a in (0, 7, 28):
                # Σ_x r(x) = 1, which is both E_flat[e^s] = 1 and E_model[e^−s] = 1
                self.assertAlmostEqual(float(np.exp(TABLES[r, a]).sum()), N, places=9)
        # diff is symmetric in x − a; sumrev mirrors sum
        self.assertTrue(np.allclose(TABLES[0, 0], TABLES[0, 0][(-np.arange(N)) % N]))
        self.assertTrue(np.allclose(TABLES[2, 0], TABLES[1, 0][(-np.arange(N)) % N]))

    def test_segment_stats_match_brute_force(self) -> None:
        rng = np.random.default_rng(1)
        x = rng.integers(0, N, 60)
        F, S = ac.segment_stats(TABLES[1], x)
        for a in (0, 5, 20):
            v = TABLES[1, a, x]
            self.assertAlmostEqual(F[a], float(v.sum()), places=9)
            self.assertAlmostEqual(S[a], brute_max_segment(v), places=9)

    def test_reverse_pairs_cover_every_pair_once(self) -> None:
        length = 40
        seen = set()
        for sigma in ac.reverse_sigmas(length):
            i, j = ac.reverse_pairs(sigma, length)
            self.assertTrue(np.all(j - i >= ac.MIN_SEPARATION) and np.all(j < length) and np.all(i >= 0))
            self.assertTrue(np.all(np.diff(i) == 1))
            seen |= set(zip(i.tolist(), j.tolist()))
        expected = {(i, j) for i in range(length) for j in range(i + ac.MIN_SEPARATION, length)}
        self.assertEqual(seen, expected)

    def test_scans_match_planted_cells(self) -> None:
        rng = np.random.default_rng(2)
        c = rng.integers(0, N, 300)
        F, S = ac.forward_scan(c, TABLES, [11, 57])
        self.assertAlmostEqual(F[1, 0, 3], ac.planted_F(c, TABLES, 57, "diff", 3), places=9)
        self.assertAlmostEqual(F[0, 2, 9], ac.planted_F(c, TABLES, 11, "sumrev", 9), places=9)
        S_rev = ac.reverse_scan(c, TABLES, [150])
        i, j = ac.reverse_pairs(150, 300)
        self.assertAlmostEqual(S_rev[0, 1, 4], brute_max_segment(TABLES[1, 4, (c[i] + c[j]) % N]), places=9)

    def test_keys_carry_the_declared_relations(self) -> None:
        rng = np.random.default_rng(3)
        k = ac.periodic_key(50, 400, "diff", 4, rng)
        self.assertTrue(np.array_equal(k[50:], (k[:-50] + 4) % N))
        k = ac.periodic_key(50, 400, "sum", 6, rng)
        self.assertTrue(np.array_equal(k[50:], (6 - k[:-50]) % N))
        key, i, j = ac.reuse_key(2000, 300, "reverse", "diff", 2, rng)
        self.assertTrue(np.array_equal(key[j:j + 300], (key[i:i + 300][::-1] + 2) % N))
        self.assertGreaterEqual(j, i + 300 + ac.MIN_SEPARATION)

    def test_planted_reuse_scores_high_without_noise(self) -> None:
        """A 2,000-rune reused stretch of LP-like text clears 30 nats; the same cell on a fresh key does not."""
        rng = np.random.default_rng(4)
        texts = ac.Plaintexts.__new__(ac.Plaintexts)
        texts.words = ac.keys.solved_plaintext_words(ac.load_corpus(), ac.load_translation())
        plain = texts.draw("L", 8000, rng)
        for orientation in ac.ORIENTATIONS:
            key, i, j = ac.reuse_key(8000, 2000, orientation, "diff", 11, rng)
            c = ac.encipher(plain, key, rng, "diff")
            self.assertGreater(ac.planted_S(c, TABLES, orientation, i, j, 2000, "diff", 11), ac.PASS)
            c0 = ac.encipher(plain, rng.integers(0, N, 8000), rng, "diff")
            self.assertLess(ac.planted_S(c0, TABLES, orientation, i, j, 2000, "diff", 11), ac.PASS)


if __name__ == "__main__":
    unittest.main()
