"""Regression: the LP2 49–51 grid includes all three scans and the 2021 community cells."""

from __future__ import annotations

import hashlib
import math
import unittest
from collections import Counter
from dataclasses import replace
from itertools import islice

from tools import run_stage_n
from tools.lpcore import keys
from tools.lpcore.ciphers import primes
from tools.lpcore.corpus import REPO_ROOT, load_corpus
from tools.rebuild_page_files import page_runes_text

CORPUS = load_corpus()


class TestFullGridExtraction(unittest.TestCase):
    def test_all_three_pages_and_current_payload(self) -> None:
        tokens = keys.grid_tokens(CORPUS)
        counts = {scan: sum(w.kind == "number" and w.scan == scan for w in CORPUS.words)
                  for scan in (66, 67, 68)}
        self.assertEqual(counts, {66: 80, 67: 104, 68: 72})
        self.assertEqual(len(tokens), 256)
        payload = bytes(keys.grid_bytes(CORPUS))
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         "3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290")
        frequencies = Counter(payload)
        self.assertEqual(len(frequencies), 161)
        entropy = -sum((count / len(payload)) * math.log2(count / len(payload))
                       for count in frequencies.values())
        self.assertAlmostEqual(entropy, 7.169654589725435, places=12)
        for scan in keys.GRID_SCANS:
            path = REPO_ROOT / "pages" / f"page_{scan:02d}" / "runes.txt"
            self.assertEqual(path.read_text(encoding="utf-8"), page_runes_text(CORPUS, scan))

    def test_prime_byte_keys_continue_past_200(self) -> None:
        streams = run_stage_n.byte_keys(CORPUS)
        expected = list(islice(primes(), 256))
        self.assertEqual(streams["primes mod 256"], [p % 256 for p in expected])
        self.assertEqual(streams["phi(prime) mod 256"], [(p - 1) % 256 for p in expected])

    def test_missing_grid_page_is_rejected(self) -> None:
        incomplete = replace(CORPUS, words=[w for w in CORPUS.words if w.scan != 68])
        with self.assertRaisesRegex(ValueError, r"unexpected grid tokens:.*184"):
            keys.grid_tokens(incomplete)


if __name__ == "__main__":
    unittest.main()
