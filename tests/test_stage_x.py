"""Stage X (TODO stage X, findings §22): key-free structure of the grid's 256 bytes.

Run from the repo root:  python -m unittest tests.test_stage_x -v
"""

from __future__ import annotations

import bz2
import csv
import gzip
import lzma
import unittest
import zlib

import numpy as np

from tools import run_stage_x as x
from tools.lpcore import keys
from tools.lpcore.corpus import load_corpus

TEXT = (b"THE PRIMES ARE SACRED. THE TOTIENT FUNCTION IS SACRED. ALL THINGS SHOULD BE ENCRYPTED. " * 4)[:256]


def brute_coincidences(block: list[int], period: int) -> int:
    return sum(block[i] == block[j] for i in range(len(block)) for j in range(i + 1, len(block))
               if i % period == j % period)


class TestStageXComponents(unittest.TestCase):
    def test_coincidences_match_brute_force(self) -> None:
        rng = np.random.default_rng(1)
        blocks = rng.integers(0, 40, (4, 256), dtype=np.uint8)
        for p in (1, 2, 7, 64, 127, 128):
            got = x.coincidences(blocks, p).tolist()
            self.assertEqual(got, [brute_coincidences(b.tolist(), p) for b in blocks], p)

    def test_coincidences_ignore_any_per_column_bijection(self) -> None:
        """The X2 premise: a repeating key of length p, or any σ per residue class, leaves C_p unchanged."""
        rng = np.random.default_rng(2)
        plain = np.frombuffer(TEXT, dtype=np.uint8)
        for p in (1, 5, 32, 100):
            sigmas = np.stack([rng.permutation(256) for _ in range(p)])
            cipher = sigmas[np.arange(256) % p, plain].astype(np.uint8)
            self.assertEqual(x.coincidences(cipher[None], p)[0], x.coincidences(plain[None], p)[0])
            xor_key = rng.integers(0, 256, p, dtype=np.uint8)
            self.assertEqual(x.coincidences((plain ^ xor_key[np.arange(256) % p])[None], p)[0],
                             x.coincidences(plain[None], p)[0])

    def test_english_has_power_and_uniform_does_not(self) -> None:
        plain = np.frombuffer(TEXT, dtype=np.uint8)[None]
        self.assertGreater(x.coincidences(plain, 64)[0], 15)
        null = np.concatenate([x.coincidences(chunk, 64) for chunk in x.null_blocks(2_000)])
        self.assertLess(abs(null.mean() - x.within_pairs(64) / 256), 0.2)

    def test_column_major_reads_down_the_32_by_8_grid(self) -> None:
        rows = np.arange(256)
        cols = x.column_major(rows)
        self.assertEqual(cols[:3].tolist(), [0, 8, 16])
        self.assertEqual(cols[31:34].tolist(), [248, 1, 9])
        self.assertEqual(sorted(cols.tolist()), rows.tolist())

    def test_decoders_reach_end_of_real_streams_only(self) -> None:
        raw = zlib.compressobj(9, zlib.DEFLATED, -15)
        streams = {"zlib raw deflate": raw.compress(TEXT) + raw.flush(), "zlib": zlib.compress(TEXT),
                   "gzip": gzip.compress(TEXT), "bz2": bz2.compress(TEXT), "lzma auto": lzma.compress(TEXT)}
        for name, data in streams.items():
            self.assertEqual(x.decode(name, data)[:2], (True, len(TEXT)), name)
        for name in ("zlib", "gzip", "bz2", "lzma auto"):
            self.assertFalse(x.decode(name, TEXT)[0], name)
            self.assertTrue(x.decode(name, TEXT)[2], f"{name} reports its error")

    def test_sieve_and_primality(self) -> None:
        primes = x.primes_below(10**6)
        self.assertEqual((len(primes), primes[:5], primes[-1]), (78498, [2, 3, 5, 7, 11], 999983))
        bases = primes[:25]
        self.assertTrue(x.probable_prime(2**127 - 1, bases))
        self.assertFalse(x.probable_prime(561, bases))
        self.assertFalse(x.probable_prime((2**61 - 1) * (2**89 - 1), bases))

    def test_two_sided_p(self) -> None:
        null = np.arange(1000)
        self.assertAlmostEqual(x.two_sided_p(null, 499.5), 1.0)
        self.assertLess(x.two_sided_p(null, -1), 0.003)
        self.assertLess(x.two_sided_p(null, 2000), 0.003)


def read_tsv(path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


GRID = np.array(keys.grid_bytes(load_corpus()), dtype=np.uint8)
PERIODIC = read_tsv(x.PERIODIC_PATH)
OTHER = read_tsv(x.OTHER_PATH)


def contiguous_cutoff(reading: str, cls: str) -> int:
    excluded = {int(r["period"]) for r in PERIODIC if r["reading"] == reading and r[f"verdict_{cls}"] == "EXCLUDED"}
    cut = 0
    while cut + 1 in excluded:
        cut += 1
    return cut


class TestStageXResults(unittest.TestCase):
    def test_stage_x_tsv_matches_the_grid(self) -> None:
        self.assertEqual(len(PERIODIC), 256)
        readings = {"R": GRID, "C": x.column_major(GRID)}
        for r in PERIODIC:
            p = int(r["period"])
            self.assertEqual(int(r["coincidences"]), x.coincidences(readings[r["reading"]][None], p)[0])
            self.assertEqual(int(r["pairs"]), x.within_pairs(p))

    def test_stage_x_no_periodic_structure(self) -> None:
        self.assertEqual([r for r in PERIODIC if r["structure"] == "PASS"], [])
        self.assertAlmostEqual(min(float(r["null_p_ge"]) for r in PERIODIC), 0.00313, places=5)

    def test_stage_x_exclusion_ranges(self) -> None:
        """Every period up to the cutoff is excluded for that plaintext class (findings §22)."""
        expected = {("R", "EN"): 102, ("C", "EN"): 112, ("R", "RUNES"): 102, ("C", "RUNES"): 118,
                    ("R", "HEX"): 102, ("C", "HEX"): 122, ("R", "B64"): 22, ("C", "B64"): 28}
        for (reading, cls), cut in expected.items():
            self.assertEqual(contiguous_cutoff(reading, cls), cut, (reading, cls))

    def test_stage_x_grid_is_not_an_rsa_modulus(self) -> None:
        rows = x.x3_rows(GRID)
        self.assertEqual([r[-1] for r in rows], ["EXCLUDED as RSA modulus"] * 4)
        self.assertEqual([r[4] for r in rows], ["prime=False"] * 4)
        self.assertIn("[2, 3, 7, 13, 29, 179]", rows[0][5])

    def test_stage_x_uniform_and_no_stream(self) -> None:
        self.assertEqual({r["verdict"] for r in OTHER if r["part"] == "X1"}, {"consistent"})
        self.assertEqual({r["verdict"] for r in OTHER if r["part"] == "X4"}, {"EXCLUDED"})
        for reading, data in x.readings_bytes(GRID).items():
            for name in x.DECODERS:
                self.assertFalse(x.decode(name, data)[0], (reading, name))


if __name__ == "__main__":
    unittest.main()
