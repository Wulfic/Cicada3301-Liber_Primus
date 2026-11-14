"""Stage AK (TODO stage AK): label coincidences.

Run from the repo root:  python -m unittest tests.test_stage_ak -v
"""

from __future__ import annotations

import csv
import unittest
from collections import Counter

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


class TestStageAKRecorded(unittest.TestCase):
    """The recorded run (findings §35): valid controls, nothing fires, 285 of 307 labels excluded."""

    @classmethod
    def setUpClass(cls) -> None:
        with ak.RESULTS_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = {r["label"]: r for r in csv.DictReader(f, delimiter="\t")}
        with ak.CONTROLS_PATH.open(encoding="utf-8", newline="") as f:
            cls.negative = list(csv.DictReader(f, delimiter="\t"))

    def test_negative_control_never_fires(self) -> None:
        self.assertEqual(len(self.negative), ak.N_NEG)
        zs = [float(v) for r in self.negative for k, v in r.items() if k != "draw" and v != "nan"]
        self.assertLess(max(zs), ak.Z_FIRE)

    def test_recorded_verdicts(self) -> None:
        self.assertEqual(len(self.rows), 307)
        self.assertEqual(Counter(r["status"] for r in self.rows.values()),
                         {"excluded": 285, "no pairs": 15, "untestable": 6, "not excluded": 1})
        self.assertEqual(self.rows["line x i mod 18"]["status"], "not excluded")
        self.assertLess(max(float(r["z"]) for r in self.rows.values() if r["z"] != "nan"), 3.3)
        for r in self.rows.values():
            if r["family"] != "line":
                self.assertEqual(r["status"], "excluded", r["label"])

    def test_cited_positive_control_strength(self) -> None:
        """§35's positive mean z by family: contexts 9.2 (three runes) and 41.1–48.8 (two), units ≥ 19.5 except lines."""
        def pos_z(r: dict[str, str]) -> float:
            return (float(r["pos_mean"]) - float(r["null_mean"])) / float(r["null_sd"])
        rows = [r for r in self.rows.values() if float(r["null_sd"]) > 0]
        two = [pos_z(r) for r in rows if r["family"] == "context" and r["label"].count(",") == 1]
        self.assertAlmostEqual(min(two), 41.1, delta=0.05)
        self.assertAlmostEqual(max(two), 48.8, delta=0.05)
        self.assertAlmostEqual(pos_z(self.rows["c[i-1],c[i-2],c[i-3]"]), 9.2, delta=0.05)
        units = [pos_z(r) for r in rows if r["family"] not in ("context", "line")]
        self.assertAlmostEqual(min(units), 19.5, delta=0.05)
        self.assertAlmostEqual(max(units), 470.7, delta=0.05)
        self.assertEqual(len(rows), 292)

    def test_headline_k_recomputes_from_the_corpus(self) -> None:
        layout = ak.build_layout(load_corpus())
        for lags, k in (((1, 2), 3569), ((1, 2, 3), 127)):
            codes = ak.context_codes(layout.runes, layout.seg_pos, lags)
            self.assertEqual(ak.coincidences(codes, layout.runes), k)
            name = ",".join(f"c[i-{a}]" for a in lags)
            self.assertEqual(int(self.rows[name]["K"]), k)


if __name__ == "__main__":
    unittest.main()
