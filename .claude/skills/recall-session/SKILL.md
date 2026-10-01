---
name: recall-session
description: "Start or resume a work session. Use when: beginning a new conversation on an existing project, resuming after a break, onboarding to a codebase, or needing to establish what was done and what's next. Reads .agent/memory/, TODO.md, and git state to produce a focused session brief."
argument-hint: "Project area of focus (e.g. 'auth service' or 'the whole project')"
---

# Session Kickoff — Recall Before You Touch Anything

> **In this repo, read these first, in this order:** `MASTER_TRACKER.md` §1 (resume here) → `TODO.md` "Active"
> → `.agent/memory/state.md` → `git log --oneline -10`. For any research question, load `lp-expert`
> (current constraints and leads) before proposing work, and `lp-attack` before running anything.
> The tracker's test count must match `python -m unittest discover -s tests -t .`. If it doesn't, the tracker is stale.

Two minutes of recall prevents duplicate work, contradicted decisions, and re-running an
approach that already failed. Starting blind is the most expensive way to begin.

## When to Use

- First message in a new conversation about an existing project
- Resuming after any break longer than an hour
- Taking over work someone (or some other session) started
- "What was I doing?" — any time context is fuzzy

## Procedure

### Step 1 — Read the state file

```
read_file(".agent/memory/state.md")
```

This is deliberately short. It tells you the current task, the next action, open blockers,
and anything short-lived worth knowing (a running dev server, a disabled test).

If it doesn't exist, this is a fresh project — go to `plan-work`.

### Step 2 — Search memory for the area you're about to touch

Don't read the whole memory files — grep them for the relevant area:

```
grep_search(query: "<feature|module|library name>", includePattern: ".agent/memory/*.md")
```

You are looking for two specific things:

- **In `decisions.md`** — has this already been decided? Proposing a rewrite of something
  that was deliberately chosen last month wastes everyone's time.
- **In `gotchas.md`** — has this already failed? The dead-ends section exists so you don't
  re-run a dead end.

**Read the `Rejected:` and `Dead ends:` lines specifically.** Those are the highest-value
content in the file and the easiest to skim past.

### Step 3 — Read TODO.md

- Unchecked items → still pending
- Recently checked → just finished, likely still fresh in the code
- Anything marked blocked → needs attention or a decision

### Step 4 — Check git state

```powershell
git log --oneline -10
git status
```

Uncommitted work is a strong signal that the last session ended mid-task. Cross-reference
it against `state.md` — if they disagree, **`git status` is the truth** and `state.md`
is stale.

### Step 5 — Produce the session brief

Report back, **10 bullets maximum**:

1. **Where things stand** — from `state.md` + git log
2. **Relevant prior decisions** — anything from `decisions.md` that constrains this work
3. **Known traps** — anything from `gotchas.md` in this area
4. **Blockers or open questions**
5. **Recommended next action** — one, specific, actionable

If you need more than 10 bullets, you're transcribing rather than summarizing.

### Step 6 — Flag anything stale

Memory reflects what was true when it was written. If a decision references a file, flag,
or dependency, **verify it still exists** before recommending action on it:

```
file_search(query: "<path from the memory entry>")
```

Say so explicitly when memory and reality disagree — a confidently stated stale fact is
worse than no memory at all.

## Rules

- **No code before steps 1–4 are done.** This is the whole point of the skill.
- **Never contradict a recorded decision without acknowledging it.** If you think a past
  decision was wrong, say which entry you're overriding and why, then append a new
  decision recording the reversal.
- Empty memory means a genuinely new project — go to `plan-work`, don't stall.
- **Update `state.md` at the end of the session** via `save-memory`. Recall only works if
  someone did the recording.
