"""Stage Y (TODO stage Y): the grid under every long byte source on disk, at every offset.

Run from the repo root:  python -m unittest tests.test_stage_y -v
"""

from __future__ import annotations

import csv
import unittest

import numpy as np

from tools import run_stage_y as y
from tools.lpcore import keys
from tools.lpcore.corpus import load_corpus

TEXT = np.frombuffer((b"THE PRIMES ARE SACRED. THE TOTIENT FUNCTION IS SACRED. ALL THINGS SHOULD BE ENCRYPTED. "
                      * 4)[:256], dtype=np.uint8)


class TestStageYComponents(unittest.TestCase):
    def test_null_cdf_is_exact(self) -> None:
        """The closed form sums to 1, has the uniform mean, and matches a Monte Carlo draw."""
        self.assertEqual(sum(y._null_counts()), 256 ** 256)
        self.assertAlmostEqual(y.null_mean(), 256 * (1 - (255 / 256) ** 256), places=9)
        draws = np.random.default_rng(7).integers(0, 256, (20_000, 256), dtype=np.uint8)
        d = y.distinct(draws)
        self.assertAlmostEqual(float((d <= 155).mean()), y.null_cdf(155), delta=0.01)
        self.assertLess(y.null_cdf(y.THRESHOLD), 4e-17)

    def test_distinct_matches_python(self) -> None:
        rng = np.random.default_rng(1)
        blocks = rng.integers(0, 256, (5, 256), dtype=np.uint8)
        blocks[0] = TEXT
        self.assertEqual(y.distinct(blocks).tolist(), [len(set(b.tolist())) for b in blocks])

    def test_encrypt_inverts_decrypt_for_every_op(self) -> None:
        k = np.random.default_rng(2).integers(0, 256, 256, dtype=np.uint8)
        for op in y.OPS:
            self.assertTrue(np.array_equal(y.decrypt(y.encrypt(TEXT, k, op), k, op), TEXT), op)

    def test_unread_inverts_read(self) -> None:
        for r in y.READINGS:
            self.assertTrue(np.array_equal(y.read(y.unread(TEXT, r), r), TEXT), r)
        self.assertEqual(int(y.read(np.arange(256, dtype=np.uint8), "C")[1]), 8)

    def test_key_windows_wrap_cyclically(self) -> None:
        source = bytes(range(250)) + bytes(range(50))
        w = y.key_windows(source)
        self.assertEqual(w.shape, (300, 256))
        self.assertEqual(w[299, :3].tolist(), [49, 0, 1])
        self.assertEqual(w[0].tolist(), list(source[:256]))

    def test_search_finds_a_plant_and_only_at_its_phase(self) -> None:
        """Positive control in miniature: plain text keyed at phase 777 under C-rev / k−g passes there and only there.

        k − g = −(g − k) is a byte bijection, so those two ops always share D. XOR differs from subtraction only by
        carries, so ASCII under the wrong one of them can pass too, at the same phase.
        """
        source = np.random.default_rng(3).integers(0, 256, 2_000, dtype=np.uint8).tobytes()
        windows = y.key_windows(source)
        grid = y.unread(y.encrypt(TEXT, windows[777], "k-g"), "C-rev")
        found = y.search(grid, windows)
        hits = y.passes(found)
        self.assertIn(("C-rev", "k-g", 777, len(set(TEXT.tolist()))), hits)
        self.assertEqual({(r, o) for r, _, o, _ in hits}, {("C-rev", 777)})
        for r in y.READINGS:
            self.assertTrue(np.array_equal(found[(r, "g-k")], found[(r, "k-g")]), r)

    def test_sources_have_the_declared_lengths(self) -> None:
        self.assertEqual(sum(len(s) for s in y.sources().values()), 179_071)


def load_tsv(path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


RESULTS = load_tsv(y.RESULTS_PATH)
CONTROLS = load_tsv(y.CONTROLS_PATH)
GRID = np.array(keys.grid_bytes(load_corpus()), dtype=np.uint8)


class TestStageYResults(unittest.TestCase):
    def test_stage_y_tsv_matches_the_grid(self) -> None:
        """Recompute every row for the three sources a fresh search can afford (page_43.bin, page_00, onion-2)."""
        self.assertEqual(len(RESULTS), 6 * len(y.READINGS) * len(y.OPS))
        self.assertEqual(sum(int(r["trials"]) for r in RESULTS), 2_865_136)
        srcs = y.sources()
        for name in ("page_43.bin", "page_00-hex", "onion-2-hex"):
            found = y.search(GRID, y.key_windows(srcs[name]))
            for r in (r for r in RESULTS if r["source"] == name):
                d = found[(r["reading"], r["op"])]
                self.assertEqual((int(r["min_D"]), int(r["phase_at_min"])), (int(d.min()), int(d.argmin())),
                                 (name, r["reading"], r["op"]))

    def test_stage_y_nothing_passes(self) -> None:
        """Findings §23: every cell excluded; the lowest D over all trials is 139, at the null's own level."""
        self.assertEqual({r["verdict"] for r in RESULTS}, {"EXCLUDED"})
        self.assertEqual(min(int(r["min_D"]) for r in RESULTS), 139)
        self.assertGreater(min(int(r["min_D"]) for r in RESULTS), y.THRESHOLD)

    def test_stage_y_run_was_valid(self) -> None:
        positives = [r for r in CONTROLS if r["kind"] == "positive"]
        negatives = [r for r in CONTROLS if r["kind"] == "negative"]
        self.assertEqual((len(positives), len(negatives)), (24, 18))
        self.assertEqual({r["verdict"] for r in CONTROLS}, {"PASS"})
        self.assertLessEqual(max(int(r["D"]) for r in positives), 64)
        self.assertEqual(min(int(r["D"]) for r in negatives), 136)
        self.assertEqual({r["passing_trials"] for r in negatives}, {"0"})


if __name__ == "__main__":
    unittest.main()
