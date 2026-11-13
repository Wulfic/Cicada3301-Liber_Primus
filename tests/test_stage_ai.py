"""Stage AI (TODO stage AI): the three OutGuess payloads share a head and a tail, byte for byte.

Run from the repo root:  python -m unittest tests.test_stage_ai -v
"""

from __future__ import annotations

import unittest

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


if __name__ == "__main__":
    unittest.main()
