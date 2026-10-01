# Project Guidelines

Claude Code auto-loads this file. The authoritative agent guidelines live in
AGENTS.md (shared across tools) — imported below so they apply every session.

@AGENTS.md

## Claude-specific orientation

**Start of a session:** read `MASTER_TRACKER.md` §1, then `TODO.md` "Active". Treat the tracker as stale if its test
count differs from `python -m unittest discover -s tests -t .`. To look up any constraint (C1…Cn, L1–L5) with its
test, use the register in `reference/findings/lp2_logic_findings_2026-09-29.md` §0.

**Skills** (`.claude/skills/`, tracked; `.gitignore` lists the ones this repo enables):

| Skill | Use it for |
|---|---|
| `lp-expert` | Any Cicada / Liber Primus question; current constraints C1…Cn; motifs and leads with test status (`lore.md`) |
| `lp-attack` | Turning an idea into one declared, deterministic test: exclusion check, detector choice, controls, TODO template, runner, write-up. Cipher-family catalog in `attack-catalog.md` |
| `lp-claim-audit` | Any claimed decryption or pattern, including our own: reproduce, count degrees of freedom, score the whole section |

If a skill disagrees with `MASTER_TRACKER.md` or the findings doc, the tracker wins. Fix the skill.

**Core API** (`tools/lpcore/`; never read runes any other way):

```python
from tools.lpcore.corpus import load_corpus          # .segment_runes(s), .rune_words(s), lp_location(scan)
from tools.lpcore.verify import load_translation      # solved English, for models and checks
from tools.lpcore import detect, stats, leak, keys   # detect.log_lr = drift-tolerant key test, pass ≥ 30 nats
```

Unsolved segments are `stats.UNSOLVED_SEGMENTS` (7–15). Positive controls come from `keys.encrypt_dodging`, and
plaintext models from `detect.unigram` over `keys.solved_plaintext_words`.

**Gotchas in this environment:**
- The harness suggests a `Co-Authored-By` trailer. AGENTS.md forbids AI co-authors, and AGENTS.md wins.
- Printing runes on Windows needs `PYTHONIOENCODING=utf-8`, or cp1252 raises `UnicodeEncodeError`.
- Write files with `newline="\n"`. The repo is LF (`.gitattributes`).
- Never edit `.claude/mcp.vscode-reference.json` into a tracked file: it holds tokens.
