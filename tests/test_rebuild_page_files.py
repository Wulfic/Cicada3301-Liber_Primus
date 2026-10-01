"""Guard tests for tools/rebuild_page_files.py — bad input in, nothing destroyed.

All tests run against a throwaway fake repo in a temp dir; the real pages/ is never touched.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.lpcore.corpus import load_corpus
from tools.lpcore.verify import load_translation
from tools.rebuild_page_files import (
    SCANS,
    RefusedError,
    _assert_inside,
    apply,
    page_runes_text,
    pages_dirty,
    plan,
)

CORPUS = load_corpus()
TRANSLATION = load_translation()
OLD = "legacy content\n"


def make_fake_repo(root: Path) -> None:
    for scan in SCANS:
        folder = root / "pages" / f"page_{scan:02d}"
        (folder / "images").mkdir(parents=True)
        (folder / "images" / f"{scan:02d}.jpg").write_bytes(b"\xff\xd8fake")
        (folder / "runes.txt").write_text(OLD, encoding="utf-8")
        (folder / "README.md").write_text(OLD, encoding="utf-8")


def snapshot(root: Path) -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8") for p in (root / "pages").rglob("*") if p.suffix in (".txt", ".md")}


class TestRebuildGuards(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        make_fake_repo(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_dirty_tree_refuses_and_writes_nothing(self) -> None:
        before = snapshot(self.root)
        writes = plan(self.root, CORPUS, TRANSLATION)
        with self.assertRaises(RefusedError):
            apply(writes, dirty=True)
        self.assertEqual(snapshot(self.root), before)

    def test_missing_image_refuses_before_any_write(self) -> None:
        (self.root / "pages" / "page_42" / "images" / "42.jpg").unlink()
        before = snapshot(self.root)
        with self.assertRaises(RefusedError):
            plan(self.root, CORPUS, TRANSLATION)
        self.assertEqual(snapshot(self.root), before)

    def test_path_outside_pages_is_refused(self) -> None:
        with self.assertRaises(RefusedError):
            _assert_inside(self.root / "pages" / ".." / "outside.txt", self.root / "pages")

    def test_clean_write_then_idempotent(self) -> None:
        writes = plan(self.root, CORPUS, TRANSLATION)
        self.assertEqual(apply(writes, dirty=False), 150)
        self.assertEqual((self.root / "pages" / "page_59" / "runes.txt").read_text(encoding="utf-8"),
                         page_runes_text(CORPUS, 59))
        # Second run: nothing to do, so even a dirty tree is fine and nothing is written.
        self.assertEqual(apply(plan(self.root, CORPUS, TRANSLATION), dirty=True), 0)

    def test_git_status_fails_closed_outside_a_repo(self) -> None:
        with self.assertRaises(RefusedError):
            pages_dirty(self.root / "does-not-exist")


class TestGeneratedContent(unittest.TestCase):
    def test_page_files_match_scans(self) -> None:
        self.assertTrue(page_runes_text(CORPUS, 59).startswith("ᛞ-ᛉᚾᛗᚦ-ᛁᛄᚱ"))
        scan67 = page_runes_text(CORPUS, 67)                   # base-60 grid only
        self.assertTrue(scan67.startswith("2M-0w-3L-3D"))
        self.assertFalse(any("ᚠ" <= ch <= "᛿" for ch in scan67))
        self.assertEqual(page_runes_text(CORPUS, 0), "")       # title page
        self.assertTrue(page_runes_text(CORPUS, 1).startswith("ᚱ-ᛝᚱᚪᛗᚹ"))   # A WARNING


if __name__ == "__main__":
    unittest.main()
