"""CONTRIBUTORS.md: wulfic is the main contributor; a merged PR's author is added once (tools/add_contributor.py)."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tools.add_contributor import CONTRIBUTORS, END, START, add_contributor, listed_logins, main

SAMPLE = f"# Contributors\n\n{START}\n| Contributor | First merged PR |\n|---|---|\n| [alice](x) | [#1](y) |\n{END}\n"


class TestContributorsFile(unittest.TestCase):
    def test_wulfic_is_main_contributor_and_pr1_author_listed(self) -> None:
        text = CONTRIBUTORS.read_text("utf-8")
        main_section = text.split("## Main contributor", 1)[1].split("\n## ", 1)[0]
        self.assertIn("[wulfic](https://github.com/Wulfic)", main_section)
        self.assertIn("certified-retart", listed_logins(text))


class TestAddContributor(unittest.TestCase):
    def test_adds_new_login_once(self) -> None:
        text, reason = add_contributor(SAMPLE, "bob-2", 7)
        self.assertEqual(reason, "added")
        self.assertEqual(listed_logins(text), {"alice", "bob-2"})
        self.assertTrue(text.endswith(f"/pull/7) |\n{END}\n"))
        again, reason = add_contributor(text, "Bob-2", 9)
        self.assertEqual((again, reason), (text, "skipped: already listed"))

    def test_skips_maintainer_and_bots(self) -> None:
        self.assertEqual(add_contributor(SAMPLE, "Wulfic", 3), (SAMPLE, "skipped: maintainer"))
        self.assertEqual(add_contributor(SAMPLE, "dependabot[bot]", 3), (SAMPLE, "skipped: bot account"))

    def test_rejects_bad_input(self) -> None:
        for login in ("", "-bob", "bob-", "a--b", "bob|x", "bob](evil)", "x" * 40, "$(id)"):
            with self.subTest(login=login), self.assertRaises(ValueError):
                add_contributor(SAMPLE, login, 3)
        with self.assertRaises(ValueError):
            add_contributor(SAMPLE, "bob", 0)
        for broken in (SAMPLE.replace(END, ""), SAMPLE + START, f"{END}\n{START}\n"):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                add_contributor(broken, "bob", 3)

    def test_cli_dry_run_and_bad_input_leave_file_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CONTRIBUTORS.md"
            path.write_text(SAMPLE, "utf-8", newline="\n")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--login", "bob", "--pr", "2", "--file", str(path)]), 0)
                self.assertEqual(path.read_text("utf-8"), SAMPLE)
                self.assertEqual(main(["--login", "bad|login", "--pr", "2", "--file", str(path), "--write"]), 1)
                self.assertEqual(path.read_text("utf-8"), SAMPLE)
                self.assertEqual(main(["--login", "bob", "--pr", "2", "--file", str(path), "--write"]), 0)
            self.assertEqual(listed_logins(path.read_text("utf-8")), {"alice", "bob"})


if __name__ == "__main__":
    unittest.main()
