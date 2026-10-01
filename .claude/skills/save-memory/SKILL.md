---
name: save-memory
description: "Record a decision, gotcha, or session state to .agent/memory/. Use when: a real choice was made between alternatives, a bug took more than two attempts, something behaved contrary to its docs, an approach was tried and abandoned, a phase completed, or a session is ending. Memory is repo-local Markdown, not an MCP server."
argument-hint: "What to record (e.g. 'why we chose Drizzle over Prisma')"
---

# Save Memory — Write It Down or Lose It

Memory lives in `.agent/memory/` as plain Markdown. No MCP call, no network, no
silent failure. If it isn't in a file, it did not happen.

⚠️ **`.agent/` is gitignored — this tree is NOT committed.** It is local to
one working copy: a fresh clone has none of it.
Anything another checkout must know goes in `TODO.md`, `AGENTS.md`, or the commit message.

```
.agent/memory/
  decisions.md   append-only — what we chose, and why
  gotchas.md     append-only — traps, dead ends, environment quirks
  state.md       rewritten   — where we are right now, what's next
```

## When to Use — Specific Triggers

Don't wait for the end of the session. Write at the moment the thing happens, while the
reasoning is still in context.

| What just happened | Where it goes |
|---|---|
| Picked one approach over a real alternative | `decisions.md` |
| Reversed an earlier decision | `decisions.md` (new entry, link the old one) |
| Established a convention others must follow | `decisions.md` |
| A bug took more than 2 attempts to fix | `gotchas.md` |
| Something behaved contrary to its documentation | `gotchas.md` |
| An approach looked right, was tried, and failed | `gotchas.md` |
| A version/platform/environment quirk bit you | `gotchas.md` |
| Finished a phase, or the session is ending | `state.md` |

## What Does NOT Belong

Noise makes the real entries harder to find. Do not record:

- **What the code already says.** "Added a `validateEmail` function" is visible in the diff.
- **What git already stores.** Who changed what, when.
- **Obvious choices with no real alternative.** "Used the standard library's JSON parser."
- **Anything that only matters to the current conversation.**

The test: **would a competent developer hit this again in six months?** If not, skip it.

## Procedure

### Decisions and gotchas — append, never edit

Read the file first to match the existing format and avoid duplicating an entry, then
append at the bottom. **Never edit or delete a past entry.** If a decision was reversed,
append a new one that says so and references the original by date and title.

**`decisions.md` entry:**
```markdown
## 2026-08-12 — Short title
**Context:** what forced the decision
**Choice:** what we did
**Why:** the actual reason
**Rejected:** what we didn't do, and why not
**Affects:** src/path/to/file.ts
```

**`gotchas.md` entry:**
```markdown
## 2026-08-12 — Short title
**Symptom:** what you actually saw (error text, wrong output, hang)
**Cause:** the real root cause
**Fix:** what worked
**Dead ends:** what looked right but wasn't, and why
**Affects:** src/path/to/file.ts
```

Use today's real date. Fill every field — a `Rejected:` or `Dead ends:` line left blank
throws away the most valuable half of the entry.

### state.md — rewrite, don't append

`state.md` answers one question: *where am I right now?* Replace the contents; keep it
under ~30 lines so it stays cheap to read at the start of every session. History goes in
the append-only files.

Update it at **every phase boundary**, not just at session end. Under Copilot, context
can be truncated without warning — a current `state.md` is the difference between the next
turn resuming and the next turn restarting.

## Writing Rules

- **Write the reasoning, not the diff.** Git stores what changed; it cannot store why, or
  which three approaches failed first. The "why" is the entire point.
- **Be specific enough to act on.** "Had trouble with auth" is useless. "Supabase
  `getSession()` returns stale data on the server after a client-side login; use
  `getUser()` on the server instead" is worth the disk space.
- **Quote real error text** in `Symptom:`. Future-you will grep for the error string.
- **One entry per idea.** Don't bundle three discoveries into one wall of text.
- **Name real files** in `Affects:` so entries can be found from the code side.

## Rules

- **A session that changed real behavior and wrote nothing here is incomplete.**
- **Append-only means append-only** for `decisions.md` and `gotchas.md`. Rewriting history
  destroys the record of what was already tried, which is the entire value of the file.
- Never record secrets, tokens, passwords, or credentials — memory gets copied, pasted and shared.
- If a budget was exhausted (3 failed fixes), writing the `gotchas.md` entry is
  **mandatory**, not optional. That's the case the file exists for.
