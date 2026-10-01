---
name: guard-destructive
description: "Gate any irreversible operation, and build guards into code that destroys. Use when: deleting files or records, overwriting anything, rewriting git history, force-pushing, dropping/truncating/migrating a database, pruning containers or volumes, destroying infrastructure, killing processes, or writing any code whose job is to delete, overwrite, reset, or migrate."
argument-hint: "The operation you're about to run, or the destructive feature you're about to write"
---

# Guard Destructive — Nothing Irreversible Without a Guard

Two different jobs, same doctrine:

- **Part A — operations you run.** Never destroy state you cannot restore.
- **Part B — code you write.** Anything that deletes, overwrites, or migrates ships with
  its own guard, or it isn't finished.

The failure mode is always the same: the command was *correct for what you thought the
target was*. `rm -rf $DIR` is fine until `$DIR` is empty. `DELETE FROM users` is fine
until the `WHERE` clause got dropped. **You do not get to find out afterwards.**

---

## What counts as destructive

Not "dangerous-sounding". The test is mechanical — **would a mistake here lose state that
isn't reproducible from what's on disk and committed?** If yes, it's destructive.

| Class | Examples |
|---|---|
| Filesystem | `rm`, `rm -rf`, `Remove-Item -Recurse -Force`, `rmdir /s`, `truncate`, `> file`, `mv` onto an existing path, `Set-Content`/`Out-File` over a file you haven't read |
| Git — local | `reset --hard`, `clean -fd`, `checkout -- .`, `restore`, `branch -D`, `stash drop`/`clear`, `commit --amend`, `rebase`, `filter-branch`, `gc --prune=now` |
| Git — shared | `push --force`, `push --mirror`, deleting a remote branch or tag, deleting a release |
| Data | `DROP`, `TRUNCATE`, `DELETE`/`UPDATE` without a `WHERE`, migration `down`, seed/reset scripts, `FLUSHALL`, index rebuilds |
| Containers / infra | `docker system prune`, `docker volume rm`, `compose down -v`, `kubectl delete`, `terraform apply` or `destroy`, any cloud console/CLI delete |
| Outward-facing | Publishing a package, closing an issue or PR, commenting publicly, cutting a release, anything other people see |
| Process / service | `kill -9` on something you didn't start, stopping a service, restarting a shared daemon |

**Overwriting counts as deleting.** Writing a file you never read is destruction with
extra steps — the previous contents are gone and you never knew what they were.

> **`Write` over an existing file is destructive.** Read it first, or use `Edit`. This is
> the single most common way an agent silently destroys work.

---

## Part A — The five gates

Every destructive operation clears **all five**, in order, before it runs. No exceptions,
no "this one's obviously fine" — obviously-fine is the exact category that gets people.

### 1. Resolve the target. Never act on an unexpanded pattern.

List it before you touch it. What you delete is the output you just read, not the glob you
typed.

```powershell
Get-ChildItem -Recurse .\build\        # see it
git status --short                     # see it
```

No variable in a destructive command until you have printed its value. No wildcard until
you have expanded it. An empty or unset variable turns a scoped delete into a root delete.

### 2. Prove it's recoverable. Name the copy.

Answer out loud, with a specific location: **"if this is wrong, where does the data come
back from?"** Committed to git? A backup you just made and verified? A snapshot?

If the honest answer is *nowhere* — **make the copy first**, then destroy. A backup you
haven't verified is not a backup.

### 3. Dry-run it.

Almost every serious tool has one. Use it and read the output — the whole point is to
find out the target list isn't what you assumed.

```powershell
git clean -nd                     # -n = dry run; ALWAYS before -f
rsync --dry-run ...
terraform plan
kubectl delete --dry-run=client ...
npm publish --dry-run
```

Tool has no dry-run? Build one: run the `SELECT` before the `DELETE`, the `Get-ChildItem`
before the `Remove-Item`, the `COUNT(*)` before the `TRUNCATE`. **Print what would be
affected and read it.**

### 4. Narrow the scope to the smallest thing that works.

- Delete the file, not the directory
- One branch by name, not `-fd`
- `WHERE id = @id`, not the whole table
- One container, not `system prune`
- Never a destructive command inside a `&&` chain or a loop — **one command, read the
  output, then decide the next one**. Chained destruction can't be inspected mid-flight.

### 5. Write the undo, then confirm with the user.

**Before running it, write the exact command that reverses it.** If you cannot write one,
you don't have a plan — you have a hope, and hope is not a rollback strategy. That line
goes in the `Rollback:` field in `TODO.md`.

Then confirm, quoting the real command and the real blast radius:

```
Destructive op:   git clean -fd
Targets:          build/, .cache/, src/scratch-notes.md   ← resolved, from `git clean -nd`
Blast radius:     3 untracked paths deleted; scratch-notes.md is NOT in git
Recoverable from: build/ and .cache/ regenerate; scratch-notes.md — nothing
Undo:             none for scratch-notes.md
```

Paste that block **before** the command runs. If it's part of a planned task, the same
information goes into `TODO.md` under `Rollback:`.

---

## Absolute stops

These need **explicit, in-the-moment instruction from the user**, naming the operation.
A general "go fix the build" is not authorization. Neither is a plan you wrote yourself.

- `rm -rf` / `Remove-Item -Recurse -Force` on any path resolving to `/`, `~`, a drive
  root, or the repo root
- `git push --force` to a shared branch — use `--force-with-lease`, on your own branch,
  after saying so
- `git reset --hard` or `git clean -fd` while uncommitted work exists
- Dropping, truncating, or restoring over any database this session did not create
- `docker volume rm`, `docker compose down -v`, `docker system prune`
- `terraform destroy`, or deleting any cloud resource
- Deleting or rewriting `.agent/memory/`, `.env`, credentials, or anything holding state
  the repo can't regenerate
- Deleting a test, adding a suppression, or using `--no-verify` to get past a gate
- Reverting, amending, or rebasing away work that isn't yours

**"I assumed that's what you meant" is not authorization.** When the instruction is
ambiguous and the action is irreversible, the correct move is to stop and ask — the cost
of one question is seconds, and the cost of being wrong is unbounded.

---

## Part B — Guards in the code you write

A feature that deletes, overwrites, resets, or migrates is **not done** when it works. It
is done when it is hard to misuse. Every one of these applies to code you write:

**Default to safe.**
- `--dry-run` is the *default*; `--force` / `--yes` is the opt-in. Not the other way round.
- Interactive confirmation before the act, and the prompt states **what** and **how many**:
  `"Delete 1,432 records from `sessions` older than 2026-01-01? [y/N]"`. A prompt that
  doesn't show the count teaches people to hit enter.
- Non-interactive contexts (CI, scripts) require an explicit flag — never silently assume
  yes because there's no TTY.

**Scope by construction, not by convention.**
- Parameterised queries only. A delete filter built by string concatenation is one typo
  from unbounded.
- **Refuse to run with an empty filter.** `if (!filter) throw` — not "if no filter, match
  everything", which is the default that has destroyed more data than any bug.
- Path operations: resolve the path, then *assert* it's inside the intended root before
  touching it. Reject `..`, symlinks, and absolute paths that came from input.

**Make it reversible.**
- Soft-delete (tombstone + timestamp) over hard delete for anything referenced elsewhere.
- Every migration `up` has a `down`, and the `down` has been run at least once. An
  untested `down` is a comment.
- Back up first, **verify the backup**, then destroy. In that order, always.

**Fail closed.**
- If the guard cannot determine that the operation is safe, it refuses. Uncertainty
  resolves to "don't", never to "proceed".
- Cap the blast radius: if a delete would affect more than N rows/files, stop and require
  an explicit override. Runaway deletes are usually a bad filter, not a big job.

**Leave evidence.**
- Log before *and* after: what was targeted, how many, by whom, and **the recovery path**.
  An error path with no log is a bug (see `AGENTS.md`).
- The post-log states the actual count affected. A mismatch against the pre-log is how
  you find out the filter was wrong while it's still fixable.

**Prove the guard works.**
- A test that calls the destructive path with a bad input and asserts **nothing was
  destroyed.** Not just that the happy path deletes correctly.
- A guard without a test is decoration. It will be refactored away by someone who assumes
  it's dead code, and no test will fail.

---

## Mechanical enforcement — and its limits

This repo ships **no** `.claude/settings.json`, so nothing mechanical blocks a destructive
command here: the five gates are the guard. If you add one, `permissions.deny` (unrecoverable
operations, blocked) and `permissions.ask` (destructive-shaped operations, always prompt) fire
in Claude Code without depending on any agent remembering this file.

**Know what they don't cover**, so you don't trust them past their range:

- They match on **command prefix**. `cd sub && rm -rf ../..` does not look like `rm` to a
  prefix matcher. Wrapping a command in `sh -c`, a script, or an npm task hides it too.
- Coverage for the `PowerShell` tool is **unverified** — the `Bash(...)` rules are the
  reliable path. Assume PowerShell is ungated.
- Copilot has no permission layer at all. There, this document is the *only* guard.

**So: the rules are a seatbelt, not a sandbox.** They catch the obvious literal mistake.
The five gates catch the rest, and they are what you actually run on.

> **Optional escalation.** A `PreToolUse` hook of `type: "prompt"` on `Bash|PowerShell`
> can classify each command semantically and catch the compound-command cases the prefix
> matcher misses. It costs a model call on *every* shell invocation — real latency on
> every `ls`. Deliberately not enabled by default; turn it on in `.claude/settings.json`
> if this repo starts touching production state.

---

## Rules

- **Read before you overwrite.** `Write` to an existing file without reading it is data loss.
- **Expand every wildcard and print every variable** before it appears in a destructive command.
- **No dry-run available means you build one.** Print the target list and read it.
- **Write the undo command before the destructive one.** No undo, no run.
- **One destructive command at a time.** Never chained, never in a loop.
- **Narrowest possible scope**, every time.
- **Confirm outward-facing and irreversible actions**, quoting the exact command.
- **Uncertainty resolves to "stop and ask."** Never to "probably fine."
- **Code that destroys ships with dry-run, a confirmation showing counts, a refusal on
  empty filters, logging, and a test proving the guard blocks.**
- **Approval for one destructive action does not extend to the next one.**
