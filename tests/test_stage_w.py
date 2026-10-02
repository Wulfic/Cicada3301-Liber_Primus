"""Stage W (TODO stage W, findings §21): the long named byte keys as random tabulae, in step, with flat negatives.

Run from the repo root:  python -m unittest tests.test_stage_w -v
"""

from __future__ import annotations

import csv
import unittest

from tools import run_stage_w
from tools.lpcore import alphabets, detect
from tools.lpcore.corpus import load_corpus
from tools.lpcore.stats import UNSOLVED_SEGMENTS
from tools.run_stage_s import ALPHA, PLAIN, family

CORPUS = load_corpus()
LP2 = [r for s in UNSOLVED_SEGMENTS for r in CORPUS.segment_runes(s)]


def read_tsv(path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def control_tuples(rows: list[dict[str, str]]) -> list[tuple]:
    """Control rows in the runner's tuple layout (only key, alignment, kind and score are read by `verdicts`)."""
    return [(r["key"], r["alignment"], r["kind"], int(r["runes"]), int(r["seed"]), int(r["phase"]),
             int(r["best_phase"]), float(r["log_mean_lr"])) for r in rows]


class TestStageWRules(unittest.TestCase):
    def test_rules_on_synthetic_rows(self) -> None:
        def ctl(kind: str, value: float) -> tuple:
            return ("k", "15", kind, 0, 0, 0, 0, value)
        strong = [ctl("positive", 40.0)] * run_stage_w.SEEDS
        self.assertEqual(run_stage_w.verdicts(strong, [("k", "15", -5.0)]), (False, {("k", "15"): "EXCLUDED"}))
        self.assertEqual(run_stage_w.verdicts(strong, [("k", "15", 31.0)])[1], {("k", "15"): "PASS"})
        weak = strong[:-1] + [ctl("positive", 29.9)]
        self.assertEqual(run_stage_w.verdicts(weak, [("k", "15", -5.0)])[1], {("k", "15"): "untestable"})
        self.assertTrue(run_stage_w.verdicts(strong + [ctl("flat-negative", 30.0)], [("k", "15", -5.0)])[0])
        self.assertTrue(run_stage_w.verdicts(strong + [ctl("lp2-null", 30.0)], [("k", "15", -5.0)])[0])


class TestStageWRecorded(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decodes = read_tsv(run_stage_w.CANDIDATES_PATH)
        cls.controls = read_tsv(run_stage_w.CONTROLS_PATH)

    def test_recorded_family_is_complete(self) -> None:
        self.assertEqual(len(self.decodes), 5 * 10)
        self.assertEqual(len(self.controls), 5 * 10 * 2 * run_stage_w.SEEDS + 5)
        self.assertEqual({r["key"] for r in self.decodes}, set(run_stage_w.CLASSINGS))

    def test_lp2_decodes_equal_stage_s(self) -> None:
        # Declared: the detector, α and keys are stage S's, so the LP2 numbers were fixed before this stage ran.
        expected = run_stage_w.stage_s_values()
        for r in self.decodes:
            with self.subTest(key=r["key"], alignment=r["alignment"]):
                self.assertAlmostEqual(float(r["log_mean_lr"]), expected[(r["key"], r["alignment"])], places=2)

    def test_verdicts_follow_the_declared_rules(self) -> None:
        controls = control_tuples(self.controls)
        decodes = [(r["key"], r["alignment"], float(r["log_mean_lr"])) for r in self.decodes]
        void, verdict = run_stage_w.verdicts(controls, decodes)
        self.assertFalse(void)
        self.assertEqual(verdict,
                         {(r["key"], r["alignment"]): r["verdict"] for r in self.decodes})
        self.assertNotIn("PASS", verdict.values())

    def test_recorded_headline(self) -> None:
        # Findings §21: 12 cells excluded, the rest untestable; LP2 at most +0.84, every negative far below +30.
        excluded = {(r["key"], r["alignment"]) for r in self.decodes if r["verdict"] == "EXCLUDED"}
        expected = {(k, a) for k in run_stage_w.CLASSINGS for a in ("7-15", "15")}
        expected |= {("page_21.bin raw", "11"), ("page_43.bin raw", "11")}
        self.assertEqual(excluded, expected)
        self.assertAlmostEqual(max(float(r["log_mean_lr"]) for r in self.decodes), 0.84, places=2)
        negatives = [float(r["log_mean_lr"]) for r in self.controls if r["kind"] != "positive"]
        self.assertAlmostEqual(max(negatives), 0.64, places=2)                  # void line is +30
        continuous = [float(r["log_mean_lr"]) for r in self.controls
                      if r["kind"] == "positive" and r["alignment"] == "7-15"]
        self.assertAlmostEqual(min(continuous), 1634.27, places=2)

    def test_a_continuous_decode_reproduces(self) -> None:
        key, phases, cyclic = family(PLAIN)["hint raw"]
        value, _, _ = alphabets.log_mean_lr(LP2, key, phases, ALPHA, cyclic=cyclic)
        row = next(r for r in self.decodes if r["key"] == "hint raw" and r["alignment"] == "7-15")
        self.assertAlmostEqual(value, float(row["log_mean_lr"]), places=2)
        self.assertLess(value, detect.THRESHOLD)


if __name__ == "__main__":
    unittest.main()
