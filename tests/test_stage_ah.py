"""Stage AH (TODO stage AH): arithmetic functions mod 29 as the key; the sieved sequences against their definitions.

Run from the repo root:  python -m unittest tests.test_stage_ah -v
"""

from __future__ import annotations

import csv
import unittest
from itertools import islice
from math import gcd

import numpy as np

from tools import run_stage_ah as ah
from tools.lpcore import detect, keys
from tools.lpcore.ciphers import primes
from tools.lpcore.corpus import load_corpus
from tools.lpcore.verify import load_translation
from tools.lpcore.gematria import N


def phi(n: int) -> int:
    return sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)


class TestStageAHSequences(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seq = ah.sequences(300)

    def test_totient_and_derived_sequences_match_definitions(self) -> None:
        direct = [phi(n) for n in range(1, 301)]
        self.assertEqual(self.seq["totient"].tolist(), direct)
        self.assertEqual(self.seq["totient-sum"].tolist(), np.cumsum(direct).tolist())
        self.assertEqual(self.seq["totient-of-totient"].tolist(), [phi(x) for x in direct])
        self.assertEqual(self.seq["n-times-totient"].tolist(), [n * d for n, d in zip(range(1, 301), direct)])

    def test_sigma_and_prime_gaps_match_definitions(self) -> None:
        self.assertEqual(self.seq["sigma"].tolist(),
                         [sum(d for d in range(1, n + 1) if n % d == 0) for n in range(1, 301)])
        ps = list(islice(primes(), 301))
        self.assertEqual(self.seq["prime-gaps"].tolist(), [b - a for a, b in zip(ps, ps[1:])])

    def test_sources_are_raw_and_chain_mod_29(self) -> None:
        src = ah.sources(300)
        self.assertEqual(len(src), 12)
        raw, chain = src["totient raw"], src["totient chain"]
        self.assertEqual(raw[:6], [1, 1, 2, 2, 4, 2])
        self.assertEqual(chain, (np.cumsum(raw) % N).tolist())
        self.assertTrue(all(0 <= v < N for values in src.values() for v in values))


class TestStageAHRecorded(unittest.TestCase):
    """The recorded run (findings §32): no pass; every testable cell excluded; the best real decode recomputes."""

    @classmethod
    def setUpClass(cls) -> None:
        with ah.CANDIDATES_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = list(csv.DictReader(f, delimiter="\t"))
        with ah.CONTROLS_PATH.open(encoding="utf-8", newline="") as f:
            cls.controls = list(csv.DictReader(f, delimiter="\t"))

    def test_recorded_headline(self) -> None:
        self.assertEqual(len(self.rows), 10_440)
        self.assertLess(max(float(r["log_lr"]) for r in self.rows), detect.THRESHOLD)
        real = [r for r in self.rows if r["segment"] != "10"]
        self.assertAlmostEqual(max(float(r["log_lr"]) for r in real), -47.85, places=2)
        cells = {}
        for r in real:
            cells.setdefault((r["source"], r["segment"], r["mode"]), []).append(float(r["log_lr"]))
        self.assertEqual(len(cells), 324)
        self.assertTrue(all(max(v) <= ah.EXCLUDE for v in cells.values()))
        self.assertGreaterEqual(min(float(r["positive_log_lr"]) for r in self.controls), detect.THRESHOLD)
        self.assertLess(max(float(r["negative_log_lr"]) for r in self.controls), detect.THRESHOLD)

    def test_best_real_decode_recomputes(self) -> None:
        corpus = load_corpus()
        words = keys.solved_plaintext_words(corpus, load_translation())
        q = detect.unigram([r for w in words for r in w])
        key = ah.sources(ah.digit_count(12_956))["totient-of-totient chain"]
        self.assertAlmostEqual(ah.score(corpus.segment_runes(7), key, q, "sub", 2), -47.85, delta=0.006)


if __name__ == "__main__":
    unittest.main()
