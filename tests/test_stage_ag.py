"""Stage AG (TODO stage AG): constants and number streams in base 29 as the key; exact digit generators.

Run from the repo root:  python -m unittest tests.test_stage_ag -v
"""

from __future__ import annotations

import csv
import unittest
from itertools import count, islice

from tools import run_stage_ag as ag
from tools.lpcore import detect, keys
from tools.lpcore.corpus import load_corpus
from tools.lpcore.verify import load_translation
from tools.lpcore.ciphers import primes
from tools.lpcore.gematria import N

PI_60 = "3141592653589793238462643383279502884197169399375105820974944"
E_60 = "2718281828459045235360287471352662497757247093699959574966967"


def decimal_prefix(digits: list[int], base: int, places: int) -> str:
    """floor(x · 10^places) from base-`base` digits with a one-digit integer part."""
    value = sum(d * base ** (len(digits) - 1 - i) for i, d in enumerate(digits))
    return str(value * 10 ** places // base ** (len(digits) - 1))


class TestDigitGenerators(unittest.TestCase):
    def test_base_digits(self) -> None:
        self.assertEqual(keys.base_digits(0), [0])
        self.assertEqual(keys.base_digits(28), [28])
        self.assertEqual(keys.base_digits(29), [1, 0])
        self.assertEqual(keys.base_digits(3301), [3, 26, 24])          # 3·841 + 26·29 + 24
        self.assertEqual(keys.base_digits(255, 16), [15, 15])
        with self.assertRaises(ValueError):
            keys.base_digits(-1)

    def test_pi_and_e_match_their_known_expansions(self) -> None:
        self.assertEqual(decimal_prefix(keys.constant_digits("pi", 60), N, 60), PI_60)
        self.assertEqual(decimal_prefix(keys.constant_digits("e", 60), N, 60), E_60)
        self.assertEqual(decimal_prefix(keys.constant_digits("pi", 60, base=10), 10, 59), PI_60[:60])

    def test_other_constants_agree_with_floats(self) -> None:
        import math
        for name, x in (("phi", (1 + math.sqrt(5)) / 2), ("sqrt2", math.sqrt(2)), ("sqrt3", math.sqrt(3)),
                        ("ln2", math.log(2))):
            d = keys.constant_digits(name, 12)
            value = sum(v * N ** (len(d) - 1 - i) for i, v in enumerate(d)) / N ** (len(d) - 1)
            self.assertAlmostEqual(value, x, places=12, msg=name)
        d = keys.constant_digits("sqrt3301", 12)                          # integer part 57 = [1, 28]
        self.assertEqual(d[:2], [1, 28])
        self.assertAlmostEqual(sum(v * N ** (11 - i) for i, v in enumerate(d)) / N ** 10, math.sqrt(3301), places=9)

    def test_digits_are_stable_under_more_precision(self) -> None:
        for name in keys.CONSTANTS:
            self.assertEqual(keys.constant_digits(name, 500), keys.constant_digits(name, 900)[:500], name)

    def test_concatenated_streams(self) -> None:
        ce = keys.concatenated_digits(primes(), 40)
        self.assertEqual(ce[:9], [2, 3, 5, 7, 11, 13, 17, 19, 23])
        self.assertEqual(ce[9:13], [1, 0, 1, 2])                        # 29 = [1, 0], 31 = [1, 2]
        self.assertEqual(keys.concatenated_digits(count(1), 31)[27:31], [28, 1, 0, 1])
        self.assertEqual(keys.concatenated_digits((p - 1 for p in primes()), 4), [1, 2, 4, 6])
        self.assertEqual(list(islice(primes(), 3)), [2, 3, 5])


class TestStageAGFamily(unittest.TestCase):
    def test_family_shape(self) -> None:
        fam = ag.sources(2_000)
        self.assertEqual(len(fam), 10)
        self.assertTrue(all(len(v) == 2_000 and min(v) >= 0 and max(v) < N for v in fam.values()))
        self.assertEqual(ag.digit_count(12_956), 1_000 + 2 * 12_956 + 2)


class TestStageAGRecorded(unittest.TestCase):
    """The recorded run (findings §31): no pass; every testable cell excluded; the best real decode recomputes."""

    @classmethod
    def setUpClass(cls) -> None:
        with ag.CANDIDATES_PATH.open(encoding="utf-8", newline="") as f:
            cls.rows = list(csv.DictReader(f, delimiter="\t"))
        with ag.CONTROLS_PATH.open(encoding="utf-8", newline="") as f:
            cls.controls = list(csv.DictReader(f, delimiter="\t"))

    def test_recorded_headline(self) -> None:
        self.assertEqual(len(self.rows), 8_700)
        self.assertLess(max(float(r["log_lr"]) for r in self.rows), detect.THRESHOLD)
        real = [r for r in self.rows if r["segment"] != "10"]
        self.assertAlmostEqual(max(float(r["log_lr"]) for r in real), -56.0, places=2)
        cells = {}
        for r in real:
            cells.setdefault((r["source"], r["segment"], r["mode"]), []).append(float(r["log_lr"]))
        self.assertEqual(len(cells), 270)
        self.assertTrue(all(max(v) <= ag.EXCLUDE for v in cells.values()))
        self.assertGreaterEqual(min(float(r["positive_log_lr"]) for r in self.controls), detect.THRESHOLD)
        self.assertLess(max(float(r["negative_log_lr"]) for r in self.controls), detect.THRESHOLD)

    def test_best_real_decode_recomputes(self) -> None:
        corpus = load_corpus()
        words = keys.solved_plaintext_words(corpus, load_translation())
        q = detect.unigram([r for w in words for r in w])
        key = keys.constant_digits("pi", ag.digit_count(12_956))
        self.assertAlmostEqual(ag.score(corpus.segment_runes(7), key, q, "add", 13), -56.0, delta=0.006)


if __name__ == "__main__":
    unittest.main()
