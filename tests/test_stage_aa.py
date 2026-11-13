"""Stage AA (TODO stage AA): keyless sliding-context ciphers, tested by sliding-window repeat counts.

Run from the repo root:  python -m unittest tests.test_stage_aa -v
"""

from __future__ import annotations

import csv
import unittest
from collections import Counter

import numpy as np

from tools import run_stage_aa as aa
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N


def naive_separated_pairs(stream, n):
    s = list(stream)
    windows = [tuple(s[i:i + n]) for i in range(len(s) - n + 1)]
    return sum(1 for i in range(len(windows)) for j in range(i + n, len(windows)) if windows[i] == windows[j])


class TestStageAAComponents(unittest.TestCase):
    def test_separated_pairs_matches_a_naive_count(self) -> None:
        rng = np.random.default_rng(1)
        for length in (0, 3, 40, 211):
            stream = rng.integers(0, 3, length)
            for n in (1, 2, 3, 5):
                self.assertEqual(aa.separated_pairs(stream, n), naive_separated_pairs(stream, n), (length, n))
        self.assertEqual(aa.separated_pairs(np.zeros(10, dtype=np.int64), 3), naive_separated_pairs([0] * 10, 3))

    def test_separated_window_pairs_counts_every_pair_at_distance_n_or_more(self) -> None:
        for length in (0, 2, 5, 9, 30):
            for n in (1, 3, 4):
                m = max(0, length - n + 1)
                expected = sum(1 for i in range(m) for j in range(i + n, m))
                self.assertEqual(aa.separated_window_pairs(length, n), expected, (length, n))

    def test_statistic_modes(self) -> None:
        a, b = np.array([1, 2, 3, 1, 2, 3]), np.array([1, 2, 3, 4])
        self.assertEqual(aa.statistic([a, b], 3, "sec"), 1)            # (0, 3) within a
        self.assertEqual(aa.statistic([a, b], 3, "cont"), 5)           # 123 ×3 across the join, 231 and 312 once

    def test_context_cipher_is_decryptable(self) -> None:
        rng = np.random.default_rng(2)
        plain = rng.integers(0, N, 5_000)
        for w in (0, 1, 3):
            cipher = aa.context_encipher(plain, w, rng)
            padded = np.concatenate([np.full(w, aa.PAD), plain])
            seen: dict[tuple, int] = {}
            for i in range(len(plain)):
                key = (tuple(padded[i:i + w]), int(cipher[i]))      # same context and cipher rune → same plaintext
                self.assertEqual(seen.setdefault(key, int(plain[i])), int(plain[i]))

    def test_equal_plaintext_windows_give_equal_cipher_ngrams(self) -> None:
        """The positive-control logic: without the rule, K_n(cipher) ≥ K_{n+w}(plaintext), for any tables."""
        rng = np.random.default_rng(3)
        plain = np.tile(rng.integers(0, N, 60), 8)[:450]
        for w in (0, 1, 2, 4):
            cipher = aa.context_encipher(plain, w, rng)
            for n in (3, 5):
                self.assertGreaterEqual(aa.separated_pairs(cipher, n), aa.separated_pairs(plain, n + w), (w, n))
                self.assertGreater(aa.separated_pairs(plain, n + w), 0)

    def test_encipher_keeps_section_lengths(self) -> None:
        rng = np.random.default_rng(4)
        plain = [[tuple(int(x) for x in rng.integers(0, N, 3)) for _ in range(k)] for k in (5, 9)]
        for mode in aa.MODES:
            out = aa.encipher(plain, 2, mode, rng)
            self.assertEqual([len(s) for s in out], [15, 27])

    def test_verdict_rules(self) -> None:
        low, mins = {"E": 50.0, "L": 60.0}, {"E": 80, "L": 90}
        self.assertEqual(aa.cell_verdict(10, 12, low, mins), "EXCLUDED")
        self.assertEqual(aa.cell_verdict(55, 12, low, mins), "INCONCLUSIVE")
        self.assertEqual(aa.cell_verdict(10, 12, {"E": 10.0, "L": 60.0}, mins), "UNTESTABLE")
        self.assertEqual(aa.cell_verdict(10, 12, low, {"E": 11, "L": 90}), "UNTESTABLE")
        self.assertEqual(aa.width_verdict(["UNTESTABLE", "EXCLUDED", "INCONCLUSIVE"]), "EXCLUDED")
        self.assertEqual(aa.width_verdict(["UNTESTABLE", "INCONCLUSIVE"]), "INCONCLUSIVE")
        self.assertEqual(aa.width_verdict(["UNTESTABLE"] * 5), "UNTESTABLE")


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


class TestStageAARecorded(unittest.TestCase):
    """The recorded run (findings §25): valid, no pass, w ≤ 2 (sec) and w ≤ 1 (cont) excluded, 21 widths untestable."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.results = read_tsv(aa.RESULTS_PATH)
        cls.verdicts = read_tsv(aa.VERDICTS_PATH)
        cls.controls = read_tsv(aa.CONTROLS_PATH)

    def test_recorded_headline(self) -> None:
        self.assertEqual([(int(r["n"]), r["mode"]) for r in self.results],
                         [(n, m) for n in aa.NGRAMS for m in aa.MODES])
        self.assertTrue(all(r["verdict"] == "NO PASS" for r in self.results))
        self.assertLess(max(abs(float(r["z_null"])) for r in self.results), 1.3)
        excluded = {(r["mode"], int(r["w"])) for r in self.verdicts if r["verdict"] == "EXCLUDED"}
        self.assertEqual(excluded, {("sec", 0), ("sec", 1), ("sec", 2), ("cont", 0), ("cont", 1)})
        self.assertEqual(Counter(r["verdict"] for r in self.verdicts), Counter({"EXCLUDED": 5, "UNTESTABLE": 21}))

    def test_lp2_counts_and_analytic_means_recompute(self) -> None:
        corpus = load_corpus()
        lp2 = aa.streams_of(aa.lp2_sections(corpus))
        sizes = [len(s) for s in lp2]
        self.assertEqual(sum(sizes), 12_956)
        for row in self.results:
            n, mode = int(row["n"]), row["mode"]
            self.assertEqual(aa.statistic(lp2, n, mode), int(row["K_LP2"]), (n, mode))
            self.assertAlmostEqual(aa.analytic_mean(sizes, n, mode), float(row["analytic_mean"]), delta=6e-4)
            if n <= aa.VALIDITY_MAX_N:                  # the validity rule: null mean within 3 s.e. of analytic
                se = float(row["null_sd"]) / np.sqrt(aa.NULL_DRAWS)
                self.assertLessEqual(abs(float(row["null_mean"]) - float(row["analytic_mean"])), 3 * se, (n, mode))

    def test_every_exclusion_follows_the_declared_rule(self) -> None:
        null_max = {(r["n"], r["mode"]): int(r["null_max"]) for r in self.results}
        k_lp2 = {(r["n"], r["mode"]): int(r["K_LP2"]) for r in self.results}
        by_cell: dict[tuple, dict] = {}
        for r in self.controls:
            by_cell.setdefault((r["n"], r["mode"], int(r["w"])), {})[r["source"]] = r
        for r in self.verdicts:
            for n in aa.NGRAMS:
                src = by_cell[(str(n), r["mode"], int(r["w"]))]
                lower = {s: float(v["log_lower_5sd"]) for s, v in src.items()}
                minimum = {s: int(v["min"]) for s, v in src.items()}
                expected = aa.cell_verdict(k_lp2[(str(n), r["mode"])], null_max[(str(n), r["mode"])], lower, minimum)
                self.assertEqual(r[f"n{n}"], expected, (r["mode"], r["w"], n))


if __name__ == "__main__":
    unittest.main()
