"""Stage AH (TODO stage AH): arithmetic functions mod 29 as the key; the sieved sequences against their definitions.

Run from the repo root:  python -m unittest tests.test_stage_ah -v
"""

from __future__ import annotations

import unittest
from itertools import islice
from math import gcd

import numpy as np

from tools import run_stage_ah as ah
from tools.lpcore.ciphers import primes
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


if __name__ == "__main__":
    unittest.main()
