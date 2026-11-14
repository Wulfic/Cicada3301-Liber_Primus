"""Stage AK (TODO stage AK): label coincidences.

Run from the repo root:  python -m unittest tests.test_stage_ak -v
"""

from __future__ import annotations

import unittest

import numpy as np

from tools import run_stage_ak as ak
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N


class TestStageAKMachinery(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.layout = ak.build_layout(load_corpus())

    def test_family_size(self) -> None:
        labs = ak.labels()
        self.assertEqual(len(labs), 307)
        self.assertEqual(sum(lab.family == "context" for lab in labs), 67)

    def test_layout(self) -> None:
        self.assertEqual(len(self.layout.runes), 12_956)
        self.assertEqual(self.layout.seg_sizes, (729, 1145, 1729, 9, 1894, 1021, 1524, 1589, 3316))
        self.assertEqual(int(self.layout.units["stretch"].max()), 9 + 86)   # 9 segment starts, 86 survivors

    def test_coincidences_counts_same_label_same_rune_pairs(self) -> None:
        codes = np.array([0, 0, 0, 1, 1, -1])
        runes = np.array([3, 3, 3, 4, 5, 3])
        self.assertEqual(ak.coincidences(codes, runes), 3)                  # C(3,2) in label 0; the -1 is ignored

    def test_context_codes_never_cross_a_segment_start(self) -> None:
        codes = ak.context_codes(self.layout.runes, self.layout.seg_pos, (1, 2, 3))
        self.assertTrue((codes[self.layout.seg_pos < 3] == -1).all())
        self.assertTrue((codes[self.layout.seg_pos >= 3] >= 0).all())
        i = int(np.flatnonzero(self.layout.seg_pos == 5)[0])
        c = self.layout.runes
        self.assertEqual(codes[i], (c[i - 1] * N + c[i - 2]) * N + c[i - 3])

    def test_chain_cipher_is_monoalphabetic_per_context(self) -> None:
        """Under the positive model, c − p is one value per context except at re-keyed doublets."""
        rng = np.random.default_rng(5)
        p = rng.integers(N, size=len(self.layout.runes))
        c = ak.chain_encipher(p, self.layout.seg_pos, (1, 2), rng)
        codes = ak.context_codes(c, self.layout.seg_pos, (1, 2))
        ok = codes >= 0
        shifts: dict[int, set[int]] = {}
        for code, d in zip(codes[ok], ((c - p) % N)[ok]):
            shifts.setdefault(int(code), set()).add(int(d))
        mixed = sum(len(v) > 1 for v in shifts.values())
        self.assertLess(mixed / len(shifts), 0.6)    # re-keys touch some contexts; most stay single-valued

    def test_english_under_a_context_key_raises_k(self) -> None:
        """With English plaintext each class is a monoalphabetic sample: K rises well above a flat stream's."""
        rng = np.random.default_rng(6)
        p = ak.english(self.layout, ak.emerson_words(), rng)
        c = ak.chain_encipher(p, self.layout.seg_pos, (1, 2), rng)
        codes = ak.context_codes(c, self.layout.seg_pos, (1, 2))
        self.assertGreater(ak.coincidences(codes, c), 1.5 * ak.coincidences(codes, rng.integers(N, size=len(c))))

    def test_zero_variance_labels_never_fire(self) -> None:
        mu, sd, mx = np.array([0.0, 5.0]), np.array([0.0, 1.0]), np.array([0.0, 6.0])
        self.assertEqual(ak.fires(np.array([0.0, 20.0]), mu, sd, mx).tolist(), [False, True])
        self.assertTrue(np.isnan(ak.zscore(np.array([0.0, 1.0]), mu, sd)[0]))


if __name__ == "__main__":
    unittest.main()
