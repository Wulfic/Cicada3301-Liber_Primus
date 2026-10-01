"""Add a merged PR's author to CONTRIBUTORS.md. Dry-run unless --write.

Run by .github/workflows/contributors.yml on every PR merged into main:

    python tools/add_contributor.py --login certified-retart --pr 1 --write

One row per login: a contributor already listed keeps their first PR. The maintainer and bot accounts are skipped.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRIBUTORS = ROOT / "CONTRIBUTORS.md"
REPO_URL = "https://github.com/Wulfic/Cicada3301-Liber_Primus"
MAINTAINER = "wulfic"
START, END = "<!-- contributors:start -->", "<!-- contributors:end -->"
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")


def listed_logins(text: str) -> set[str]:
    """Lower-cased logins already in the contributors table."""
    return {m.lower() for m in re.findall(r"^\| \[([^\]]+)\]", table(text), re.MULTILINE)}


def table(text: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError(f"expected exactly one {START} … {END} block")
    return text.split(START, 1)[1].split(END, 1)[0]


def add_contributor(text: str, login: str, pr: int) -> tuple[str, str]:
    """Return (new text, reason). The text is unchanged unless the reason is 'added'."""
    if login.endswith("[bot]"):
        return text, "skipped: bot account"
    if not LOGIN.fullmatch(login) or "--" in login:
        raise ValueError(f"not a GitHub login: {login!r}")
    if pr < 1:
        raise ValueError(f"not a PR number: {pr}")
    if login.lower() == MAINTAINER:
        return text, "skipped: maintainer"
    if login.lower() in listed_logins(text):
        return text, "skipped: already listed"
    row = f"| [{login}](https://github.com/{login}) | [#{pr}]({REPO_URL}/pull/{pr}) |\n"
    head, tail = text.split(END, 1)
    return f"{head}{row}{END}{tail}", "added"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--login", required=True, help="GitHub login of the PR author")
    parser.add_argument("--pr", required=True, type=int, help="number of the merged PR")
    parser.add_argument("--file", type=Path, default=CONTRIBUTORS)
    parser.add_argument("--write", action="store_true", help="write the file (default: dry run)")
    args = parser.parse_args(argv)

    try:
        text = args.file.read_text("utf-8")
        new_text, reason = add_contributor(text, args.login, args.pr)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"{args.login} (#{args.pr}): {reason}; {len(listed_logins(new_text))} contributors listed")
    if new_text != text:
        if args.write:
            with open(args.file, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_text)
            print(f"wrote {args.file}")
        else:
            print("dry run: pass --write to save")
    return 0


if __name__ == "__main__":
    sys.exit(main())
