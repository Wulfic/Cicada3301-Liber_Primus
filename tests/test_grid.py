"""Stage N: the scan 66–67 grid bytes under LP-native keys (rules declared in TODO.md before the run)."""

from __future__ import annotations

import csv
import random
import unittest
from itertools import islice

from tools import run_stage_n
from tools.lpcore import detect, keys
from tools.lpcore.ciphers import primes
from tools.lpcore.corpus import load_corpus
from tools.lpcore.gematria import N
from tools.lpcore.verify import load_translation

CORPUS = load_corpus()
PLAIN = [r for w in keys.solved_plaintext_words(CORPUS, load_translation()) for r in w]
Q = detect.unigram(PLAIN)
INVERSE = {"xor": lambda p, k: p ^ k, "b-k": lambda p, k: (p + k) % 256, "b+k": lambda p, k: (p - k) % 256}


class TestStageN(unittest.TestCase):
    def test_an_end_hash(self) -> None:
        h = keys.an_end_hash(CORPUS)
        self.assertEqual(len(h), 64)
        self.assertEqual(h.hex()[:16], "36367763ab73783c")

    def test_pgp_header_check(self) -> None:
        self.assertTrue(run_stage_n.pgp_packet_fits(bytes([0x84, 3, 1, 2, 3])))             # old format, 1-octet length
        self.assertTrue(run_stage_n.pgp_packet_fits(bytes([0xC1, 2, 9, 9])))                # new format
        self.assertTrue(run_stage_n.pgp_packet_fits(bytes([0x85, 0, 3, 1, 2, 3])))          # old format, 2-octet length
        self.assertFalse(run_stage_n.pgp_packet_fits(bytes([0x84, 7, 1, 2, 3])))            # length does not fit
        rng = random.Random(1)
        hits = sum(run_stage_n.pgp_packet_fits(bytes(rng.randrange(256) for _ in range(184))) for _ in range(20000))
        self.assertEqual(hits, 33)                     # 0.17 %: (96/256)·(1/256) ≈ 0.15 %, so ≈ 0.12 false hits in 72

    def test_positive_controls_bytes(self) -> None:
        text = b"Within the deep web there exists a page that hashes to this. " * 4
        text = text[:184]
        for name, key in run_stage_n.byte_keys(CORPUS).items():
            for op, inverse in INVERSE.items():
                cipher = [inverse(p, key[i % len(key)]) for i, p in enumerate(text)]
                with self.subTest(key=name, op=op):
                    out = run_stage_n.apply_bytes(cipher, key, op)
                    self.assertEqual(out, text)
                    self.assertGreaterEqual(run_stage_n.printable_fraction(out), run_stage_n.PRINTABLE_PASS)

    def test_positive_control_runes(self) -> None:
        phi = [p - 1 for p in islice(primes(), 400)]
        cipher = [(p + k) % N for p, k in zip(PLAIN[700:884], phi)]
        self.assertGreater(detect.log_lr(cipher, phi, Q), detect.THRESHOLD)

    def test_recorded_verdict(self) -> None:
        with run_stage_n.OUT_PATH.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        byte_rows = [r for r in rows if r["reading"] == "bytes"]
        rune_rows = [r for r in rows if r["reading"] != "bytes"]
        self.assertEqual(len(byte_rows), 12 * 3 * 2)
        self.assertEqual(len(rune_rows), 2 * 2 * 3 * (N + 3))
        self.assertFalse([r for r in rows if r["verdict"] == "PASS"])                     # verdict: nothing decrypts
        self.assertAlmostEqual(max(float(r["printable"]) for r in byte_rows), 0.440, places=3)
        self.assertLess(max(float(r["log_lr_nats"]) for r in rune_rows), 0.0)
        # The file reproduces from code.
        fresh = run_stage_n.byte_results(CORPUS)
        self.assertEqual([r[4] for r in fresh], [r["printable"] for r in byte_rows])


if __name__ == "__main__":
    unittest.main()
