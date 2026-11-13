"""Stage AI (TODO stage AI): the three OutGuess payloads share a head and a tail, byte for byte.

Run from the repo root:  python -m unittest tests.test_stage_ai -v
"""

from __future__ import annotations

import csv
import unittest

import numpy as np

from tools import run_stage_ai as ai
from tools.lpcore.corpus import REPO_ROOT

OUTGUESS = REPO_ROOT / "data" / "outguess"


def differing_span(a: bytes, b: bytes) -> tuple[int, int]:
    """[first, last + 1) of the bytes where a and b differ."""
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    return diff[0], diff[-1] + 1


class TestPayloadOverlap(unittest.TestCase):
    """The fact the stage rests on, re-derived from the files on disk."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.p = {k: (OUTGUESS / f"page_{k}.bin").read_bytes() for k in ("17", "21", "43")}

    def test_equal_length(self) -> None:
        self.assertEqual({len(v) for v in self.p.values()}, {58_152})

    def test_differing_spans(self) -> None:
        self.assertEqual(differing_span(self.p["17"], self.p["21"]), (1_417, 56_199))
        self.assertEqual(differing_span(self.p["17"], self.p["43"]), (1_417, 56_199))
        self.assertEqual(differing_span(self.p["21"], self.p["43"]), (2_004, 55_924))


class TestStageAIMachinery(unittest.TestCase):
    """The statistics and the declared verdict rule on inputs with a known answer."""

    def test_bad_input_is_refused(self) -> None:
        same = np.zeros(10, dtype=np.uint8)
        with self.assertRaises(ValueError):
            ai.differing_span(same, same.copy())
        with self.assertRaises(ValueError):
            ai.statistics(np.zeros(0, dtype=np.uint8))
        with self.assertRaises(ValueError):
            ai.in_depth(b"ab", b"abc", np.random.default_rng(0))

    def test_uniform_bytes_fire_nothing(self) -> None:
        x = np.random.default_rng(1).integers(0, 256, 50_000, dtype=np.uint8)
        self.assertEqual(ai.fires(ai.statistics(x)), "-")

    def test_ascii_depth_fires_bit_phase(self) -> None:
        rng = np.random.default_rng(2)
        x = rng.integers(0, 128, 50_000, dtype=np.uint8) ^ rng.integers(0, 128, 50_000, dtype=np.uint8)
        s = ai.statistics(x)
        self.assertIn("S1", ai.fires(s))
        self.assertEqual(s["zero_rates"][0], 1.0)            # bit 7 of ASCII ⊕ ASCII is always 0

    def test_simulated_raw_is_related_not_depth(self) -> None:
        f = ai.fires(ai.statistics(ai.simulated_raw(50_000, np.random.default_rng(3))))
        self.assertNotIn("S1", f)
        self.assertEqual(ai.verdict([f]), "RELATED")

    def test_verdict_rule(self) -> None:
        self.assertEqual(ai.verdict(["-", "S1", "-"]), "DEPTH")
        self.assertEqual(ai.verdict(["-", "S3", "S2+S3"]), "RELATED")
        self.assertEqual(ai.verdict(["-", "-", "-"]), "INDEPENDENT")


class TestStageAIRecorded(unittest.TestCase):
    """The recorded run (findings §33): valid controls, verdict RELATED, flat bit phase; recomputed from the payloads."""

    @classmethod
    def setUpClass(cls) -> None:
        with ai.RESULTS_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = {r["name"]: r for r in csv.DictReader(f, delimiter="\t")}
        with ai.CONTROLS_PATH.open(encoding="utf-8", newline="") as f:
            cls.controls = [tuple(r.values()) for r in csv.DictReader(f, delimiter="\t")]

    def test_recorded_controls_are_valid(self) -> None:
        self.assertEqual(len(self.controls), 248)
        self.assertEqual(ai.controls_pass(self.controls), [])

    def test_recorded_verdict(self) -> None:
        self.assertEqual(set(self.rows), {"17x21", "17x43", "21x43"})
        self.assertEqual({r["verdict"] for r in self.rows.values()}, {"RELATED"})
        self.assertEqual({r["fires"] for r in self.rows.values()}, {"S2+S3"})
        self.assertGreaterEqual(min(float(r["p_phase"]) for r in self.rows.values()), 0.3)
        self.assertGreaterEqual(min(float(r["z_agree"]) for r in self.rows.values()), 20.0)

    def test_statistics_recompute_from_the_payloads(self) -> None:
        p = ai.load_payloads()
        for name, (zero_bytes, run, z) in {"17x21": (737, 48, 20.018), "17x43": (1_060, 48, 24.616),
                                          "21x43": (738, 34, 20.153)}.items():
            a, b = name.split("x")
            lo, hi = ai.differing_span(p[a], p[b])
            s = ai.statistics(p[a][lo:hi] ^ p[b][lo:hi])
            self.assertEqual((s["zero_bytes"], s["longest_zero_run"]), (zero_bytes, run), name)
            self.assertAlmostEqual(s["z_agree"], z, places=3)
            self.assertAlmostEqual(s["chi2_phase"], float(self.rows[name]["chi2_phase"]), places=3)


if __name__ == "__main__":
    unittest.main()
