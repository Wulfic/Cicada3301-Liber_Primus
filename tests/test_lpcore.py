"""Tests for tools/lpcore.

Run from the repo root:  python -m unittest discover -s tests -t . -v
"""

from __future__ import annotations

import unittest

from tools.lpcore import ciphers
from tools.lpcore.corpus import CorpusError, load_corpus, lp_location, parse_master, scan_for_master_page
from tools.lpcore.gematria import gematria_sum, runes_to_indices, word_matches
from tools.lpcore.solved import ERRATA, FIRFUMFERENFE, SOLVED_BY_SEGMENT, SOLVED_SECTIONS, decrypt_section
from tools.lpcore.verify import (
    AlignmentError,
    compare_words,
    english_words,
    interrupter_positions,
    load_translation,
    render_words,
    split_like,
)

CORPUS = load_corpus()
TRANSLATION = load_translation()

def w(text: str) -> tuple[int, ...]:
    return tuple(runes_to_indices(text))


class TestCorpusStructure(unittest.TestCase):
    def test_page_and_segment_totals(self) -> None:
        self.assertEqual(len(CORPUS.pages), 73)
        self.assertEqual(len(CORPUS.all_runes()), 15933)
        lp2 = sum(len(p.runes) for p in CORPUS.pages if p.lp_part == "LP2")
        self.assertEqual(lp2, 13136)

    def test_segment_rune_counts(self) -> None:
        expected = [184, 515, 157, 778, 755, 319, 89,                 # LP1, all solved
                    729, 1145, 1729, 9, 1894, 1021, 1524, 1589, 3316,  # LP2 unsolved
                    85, 95]                                           # AN END, PARABLE
        self.assertEqual([len(CORPUS.segment_runes(s)) for s in range(18)], expected)

    def test_scan_mapping_matches_the_images(self) -> None:
        # Facts read off the scans by eye on 2026-09-29.
        self.assertTrue(CORPUS.page_by_scan(59).raw.lstrip().startswith("ᛞ-ᛉᚾᛗᚦ-ᛁᛄᚱ-ᛈᛉᚢᚫᚦᛒᚠᛄᚦ-ᚠᚪᛝᛖ"))
        self.assertEqual(len(CORPUS.page_by_scan(66).runes), 66)       # 3 rune lines, then base-60
        self.assertEqual(len(CORPUS.page_by_scan(67).runes), 0)        # base-60 grid only
        self.assertIn("ᚹᚹᛈ-ᚠᛡᛚᛉᛒᚾ-ᚳᛗᚾᚱᛗ", CORPUS.page_by_scan(68).raw)
        self.assertIsNone(CORPUS.page_by_scan(0))
        self.assertIsNone(CORPUS.page_by_scan(2))

    def test_section_starts(self) -> None:
        firsts = {s: CORPUS.rune_words(s)[0].text for s in (7, 8, 9, 11, 12, 13, 14, 15, 16, 17)}
        self.assertEqual(firsts[7], "ᛋᚻᛖᚩᚷᛗᛡᚠ")
        self.assertEqual(firsts[9], "ᛉᛁᛉᛗ")
        self.assertEqual(firsts[16], "ᚫᛄ")
        self.assertEqual(firsts[17], "ᛈᚪᚱᚪᛒᛚᛖ")
        self.assertEqual(CORPUS.rune_words(16)[0].scan, 73)
        self.assertEqual(CORPUS.rune_words(17)[0].scan, 74)

    def test_scan_helpers(self) -> None:
        self.assertEqual(scan_for_master_page(0), 1)
        self.assertEqual(scan_for_master_page(1), 3)
        self.assertEqual(scan_for_master_page(15), 17)
        self.assertEqual(scan_for_master_page(72), 74)
        self.assertEqual(lp_location(17), ("LP2", 0))
        self.assertEqual(lp_location(16), ("LP1", 16))
        with self.assertRaises(CorpusError):
            scan_for_master_page(73)
        with self.assertRaises(CorpusError):
            lp_location(75)

    def test_words_cross_page_breaks(self) -> None:
        # LP2 p0 ends mid-word; the word continues on p1 (…ᚹ% ᚪᛁᛗᛋᚾ-).
        self.assertIn("ᚹᚪᛁᛗᛋᚾ", [x.text for x in CORPUS.rune_words(7)])

    def test_parser_rejects_malformed_input(self) -> None:
        with self.assertRaises(CorpusError):
            parse_master("no runes at all")
        with self.assertRaises(CorpusError):
            parse_master("ᚠ-ᚢ%ᚦ$%")  # wrong page and segment counts
        good = CORPUS.source.read_text(encoding="utf-8")
        with self.assertRaises(CorpusError):
            parse_master(good.replace("ᚠᚢᛚᛗ", "ᚠᚢ#ᛗ", 1))  # unknown character


class TestGematria(unittest.TestCase):
    def test_spelling_rules(self) -> None:
        self.assertTrue(word_matches(w("ᚳᚹᛖᛋᛏᛡᚾ"), "QUESTION"))   # LP writes CWESTION
        self.assertTrue(word_matches(w("ᛒᛖᛁᛝ"), "BEING"))           # B,E,I,NG
        self.assertTrue(word_matches(w("ᛒᛖᛝ"), "BEING"))            # B,E,ING
        self.assertTrue(word_matches(w("ᛖᚢᛖᚱᚣ"), "EVERY"))          # V written U
        self.assertFalse(word_matches(w("ᛒᛖᛝ"), "BEINGS"))
        self.assertFalse(word_matches(w("ᚦᛖ"), "TEH"))

    def test_magic_square_word_values(self) -> None:
        # The LP1 p5 magic square mixes numbers with words whose prime sums are those numbers.
        self.assertEqual(gematria_sum(w("ᛋᚻᚪᛞᚩᚹᛋ")), 341)   # SHADOWS

    def test_scan05_square_parses_into_a_magic_square(self) -> None:
        # Regression: grid numbers must end at a line break ("18/226" once parsed as 18226).
        seg = [x for x in CORPUS.words if x.segment == 2]
        start = next(i for i, x in enumerate(seg) if x.text == "ᚦᛁᛋ") + 1   # after KNOW THIS
        rows: dict[int, list[int]] = {}
        for x in seg[start:]:
            rows.setdefault(x.line, []).append(int(x.text) if x.kind == "number" else gematria_sum(x.runes))
        grid = [rows[k] for k in sorted(rows)]
        self.assertEqual([len(r) for r in grid], [5] * 5)
        sums = [sum(r) for r in grid] + [sum(c) for c in zip(*grid)]
        sums += [sum(grid[i][i] for i in range(5)), sum(grid[i][4 - i] for i in range(5))]
        self.assertEqual(set(sums), {1033})


class TestCipherPrimitives(unittest.TestCase):
    def test_primes_and_totients(self) -> None:
        self.assertEqual([p for p, _ in zip(ciphers.primes(), range(10))],
                         [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        self.assertEqual([k for k, _ in zip(ciphers.totient_prime_stream(), range(6))],
                         [1, 2, 4, 6, 10, 12])
        self.assertEqual(next(ciphers.totient_prime_stream(offset=2)), 4)

    def test_skip_does_not_consume_key(self) -> None:
        out = ciphers.apply_stream([5, 0, 5], ciphers.repeating_key([1, 2]), skip={1})
        self.assertEqual(out, [4, 0, 3])

    def test_bad_parameters_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            ciphers.apply_stream([1], ciphers.constant_key(1), mode="xor")
        with self.assertRaises(ValueError):
            ciphers.repeating_key([])

    def test_invert_is_an_involution(self) -> None:
        xs = list(range(29))
        self.assertEqual(ciphers.invert(ciphers.invert(xs)), xs)


class TestVerifyHelpers(unittest.TestCase):
    def test_english_words(self) -> None:
        self.assertEqual(english_words('"I DON\'T HAVE A VOICE," 2 WE'), ["I", "DONT", "HAVE", "A", "VOICE", "WE"])

    def test_alignment_errors(self) -> None:
        with self.assertRaises(AlignmentError):
            interrupter_positions([w("ᚩᚠ")], ["OF", "EXTRA"])
        with self.assertRaises(AlignmentError):
            interrupter_positions([w("ᚩᚠᚠᚠᚠᚠ")], ["OF"])      # no 6-rune spelling of OF
        with self.assertRaises(AlignmentError):
            split_like([1, 2, 3], [w("ᚠ")])

    def test_interrupters_come_from_english_only(self) -> None:
        # ᚠ at offset 1 is plaintext F of "OF"; the ᚠ in the second word is an enciphered letter.
        self.assertEqual(interrupter_positions([w("ᚩᚠ"), w("ᚠᚠ")], ["OF", "AT"]), {1})

    def test_render_words_takes_the_spelling_from_the_english(self) -> None:
        # ᚳ is C/K, ᚢ is U/V: one rune word renders as whichever word the English says it is.
        know, can, voice = w("ᚳᚾᚩᚹ"), w("ᚳᚪᚾ"), w("ᚢᚩᛁᚳᛖ")
        self.assertEqual(render_words([know, can, voice], ["KNOW", "CAN", "VOICE"]), ["KNOW", "CAN", "VOICE"])
        self.assertEqual(render_words([know, can], ["KNOW"]), ["KNOW", "CAN"])   # no English: canonical spelling
        with self.assertRaises(AlignmentError):
            render_words([know], ["SNOW"])                                       # runes do not spell it
        with self.assertRaises(AlignmentError):
            render_words([know], ["KNOW", "EXTRA"])


class TestSolvedSectionsReproduce(unittest.TestCase):
    """Every solved section must decrypt from CANONICAL runes to the published English exactly."""

    def test_every_solved_section(self) -> None:
        self.assertEqual(len(SOLVED_SECTIONS), 9)
        for section in SOLVED_SECTIONS:
            with self.subTest(segment=section.segment, group=section.group):
                plain_words, english = decrypt_section(CORPUS, TRANSLATION, section)
                mismatches = compare_words(plain_words[:len(english)], english)
                self.assertEqual(mismatches, [], f"segment {section.segment}: first mismatches {mismatches[:8]}")

    def test_wrong_key_is_detected(self) -> None:
        # Guard against a vacuous comparison: a wrong key must produce mismatches.
        welcome = SOLVED_BY_SEGMENT[1]
        plain_words, english = decrypt_section(CORPUS, TRANSLATION, welcome, method=("vigenere", FIRFUMFERENFE))
        self.assertGreater(len(compare_words(plain_words, english)), 50)

    def test_rendered_plaintext_keeps_k(self) -> None:
        # User report 2026-10-01: rendered solves read CNOW, LICE, BOOC. Every K of the English must survive.
        rendered, english = [], []
        for section in SOLVED_SECTIONS:
            plain_words, eng = decrypt_section(CORPUS, TRANSLATION, section)
            rendered += render_words(plain_words[:len(eng)], eng)
            english += eng
        self.assertEqual(rendered, english)
        self.assertEqual(sum(x.count("K") for x in rendered), sum(x.count("K") for x in english))
        self.assertEqual(sum(x.count("K") for x in english), 19)                  # pinned: solved English has 19 K
        self.assertNotIn("CNOW", rendered)

    def test_only_documented_errata(self) -> None:
        self.assertEqual(set(ERRATA), {(1, 95), (4, 24)})


if __name__ == "__main__":
    unittest.main()
