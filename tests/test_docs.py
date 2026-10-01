"""The docs cite only things that exist: test names, repo paths, `lpcore` names, and relative links (TODO stage Q).

AGENTS.md: "Every number cited in a doc has a test or a named script that reproduces it." This cannot check the
numbers themselves (the cited tests do). It checks that each citation still points at something real, and that every
constraint the tracker names has a row in the findings register.
"""

from __future__ import annotations

import importlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINDINGS = ROOT / "reference" / "findings" / "lp2_logic_findings_2026-09-29.md"
DOCS = [ROOT / name for name in ("MASTER_TRACKER.md", "README.md", "TODO.md", "AGENTS.md")] + [FINDINGS]
MODULES = ("alphabets", "ciphers", "corpus", "detect", "fastdetect", "gematria", "keys", "leak", "solved", "stats",
           "verify")
PATH_PREFIXES = ("tools/", "tests/", "data/", "reference/", "pages/")
PLACEHOLDER = re.compile(r"[<>*]|XX|_N\b|\.\.\.|…")


def test_names() -> set[str]:
    return {m for f in (ROOT / "tests").glob("test_*.py") for m in re.findall(r"def (test_\w+)", f.read_text("utf-8"))}


def doc_problems(text: str, doc_dir: Path, tests: set[str]) -> list[str]:
    """Every citation in `text` that points at nothing."""
    problems = []
    for span in re.findall(r"`([^`\n]+)`", text):
        span = span.strip()
        if re.fullmatch(r"test_\w+", span):
            if span not in tests:
                problems.append(f"no test named {span}")
        elif span.startswith(PATH_PREFIXES) and not PLACEHOLDER.search(span) and " " not in span:
            if not (ROOT / span).exists():
                problems.append(f"no path {span}")
        elif (m := re.match(rf"({'|'.join(MODULES)})\.(\w+)", span)) and m.group(2) != "py":
            module = importlib.import_module(f"tools.lpcore.{m.group(1)}")
            if not hasattr(module, m.group(2)):
                problems.append(f"no name {m.group(0)}")
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if not (doc_dir / target.split("#")[0]).exists():
            problems.append(f"broken link {target}")
    return problems


class TestDocCitations(unittest.TestCase):
    TESTS = test_names()

    def test_checker_catches_bogus_citations(self) -> None:
        bogus = "`test_no_such_thing` `stats.no_such_name` `tools/no_such_file.py` [x](no/such/file.md) `pages/page_XX/`"
        self.assertEqual(len(doc_problems(bogus, ROOT, self.TESTS)), 4)
        real = "`test_doublet_deficit` `stats.lag_repeats(U, 1)` `leak.py` `tools/lpcore/leak.py` [t](TODO.md#active)"
        self.assertEqual(doc_problems(real, ROOT, self.TESTS), [])

    def test_every_citation_resolves(self) -> None:
        for doc in DOCS:
            with self.subTest(doc=doc.name):
                self.assertEqual(doc_problems(doc.read_text("utf-8"), doc.parent, self.TESTS), [])


class TestConstraintRegister(unittest.TestCase):
    def test_every_tracker_constraint_has_a_tested_row(self) -> None:
        tracker = (ROOT / "MASTER_TRACKER.md").read_text("utf-8")
        highest = max(int(n) for n in re.findall(r"\bC(\d+)\b", tracker))
        register = FINDINGS.read_text("utf-8").split("## 0. Constraint register", 1)[1].split("\n## ", 1)[0]
        tests = test_names()
        for n in range(1, highest + 1):
            with self.subTest(constraint=f"C{n}"):
                row = re.search(rf"^\| C{n} \|.*$", register, re.MULTILINE)
                self.assertIsNotNone(row, f"C{n} has no register row")
                cited = re.findall(r"`(test_\w+)`", row.group(0)) if row else []
                self.assertTrue(cited, f"C{n} cites no test")
                self.assertTrue(set(cited) <= tests, f"C{n} cites a missing test")


if __name__ == "__main__":
    unittest.main()
