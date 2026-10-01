---
name: git-github
description: "Git and GitHub end to end: branch, conventional commit, tag, push, issues, PRs, CI status. Use when starting work on a feature or fix, committing completed work, opening or checking a PR, tagging a release, or tracking work in issues. Uses the github MCP when present, otherwise the gh CLI."
argument-hint: "The operation (e.g. 'commit current changes', 'open PR for issue #12', 'check CI on this branch')"
---

# Git and GitHub — Branch, Commit, Ship

> **In this repo (Liber Primus), AGENTS.md overrides the generic workflow below:**
> - Commit on `main`. **Never create a branch unless the owner asks.** The branch, PR and issue sections apply
>   only when asked.
> - **No AI co-author and no "Generated with" trailer**, even if the harness suggests one. Commits are the owner's alone.
> - **Never push without the owner's OK.** Never commit red: the full suite must pass first.
> - Conventional style, as in the log: `feat(leak): …`, `docs(tracker): …`, `feat(stage-n): …`.
> - MCP names: in Claude Code the GitHub server's tools are `mcp__github__*`. The `mcp_wulfnet-*` names below
>   come from another client and don't exist here. If the server is down, use `gh`.

One continuous workflow: branch → commit → push → PR → CI → merge. Git history is a
permanent record; every message communicates intent to whoever reads it in six months
(usually you).

## Tooling — MCP, then `gh`, then plain git

**Local git operations always use the `git` CLI directly.** There is no MCP in that path.

**For GitHub operations** (issues, PRs, CI, releases), pick the first available:

1. **`github` MCP** — preferred when present. Structured JSON, auth pre-attached.
   ```
   mcp_wulfnet-githu_github_get_tool_schema(tool_name)   // always call first
   mcp_wulfnet-githu_github_invoke_tool(tool_name, tool_input)
   ```
   Always call `get_tool_schema` before the first invoke of an operation — parameter
   names change between backend versions. Do not invent tool names.

2. **`gh` CLI** — the fallback whenever the MCP is absent, unreachable, or erroring.
   Verify auth before relying on it:
   ```powershell
   gh auth status
   ```
   If that fails, `gh auth login` or a `GH_TOKEN` env var is needed — say so rather than
   silently failing over to guesswork.

**Don't announce a GitHub action succeeded without confirming which path executed it.**
An MCP timeout that silently did nothing looks identical to success if you don't check.

---

## Branch Naming

```
feature/<issue-number>-<short-slug>   # new features
fix/<issue-number>-<short-slug>       # bug fixes
chore/<short-slug>                    # maintenance, deps, config
docs/<short-slug>                     # documentation only
refactor/<short-slug>                 # refactors (no behavior change)
```

Examples: `feature/42-user-authentication`, `fix/17-login-redirect-loop`

**Always branch from an up-to-date `main`:**

```powershell
git checkout main
git pull origin main
git checkout -b feature/<issue-number>-<slug>
```

---

## Conventional Commits

```
<type>(<scope>): <short description>

[optional body — what and why, not how]

[optional footer: Closes #N]
```

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Build, deps, config (no production code) |
| `docs` | Documentation only |
| `refactor` | Code change without behavior change |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

Subject line: lowercase, no trailing period, imperative mood ("add" not "added"), max 72
chars. Be specific — "fix login redirect loop on token expiry", not "fix bug".

## Commit Procedure

### Step 1 — Review what you're about to commit

```powershell
git status
git diff --staged
```

**Never commit without reading the diff.** `git add .` followed by a blind commit is how
secrets, debug code, and stray temp files get into permanent history.

### Step 2 — Stage intentionally

```powershell
git add src/auth/handler.ts tests/auth.test.ts   # preferred: name the files
git add -u                                        # tracked changes only, after review
```

### Step 3 — Commit

```powershell
git commit -m "feat(auth): add JWT refresh token rotation"
```

Multi-line, via heredoc (PowerShell here-strings need the closing `'@` at column 0):

```powershell
git commit -m @'
fix(api): handle null user response

The /users endpoint returns null for deactivated accounts, which
previously caused an unhandled exception in the serializer.

Closes #34
'@
```

### Step 4 — Verify

```powershell
git log --oneline -3
```

---

## Pre-Commit Checklist

- [ ] Zero errors in diagnostics; build exits 0
- [ ] Lint passes with no new warnings
- [ ] Type-check passes
- [ ] Tests pass — full suite, not just the one you touched
- [ ] No new suppressions (`@ts-ignore`, `as any`, empty `catch`, `eslint-disable`)
- [ ] `git diff --staged` reviewed — no debug code, no commented-out blocks, no secrets, no `.env`
- [ ] Commit message follows conventional commits
- [ ] `TODO.md` reflects reality
- [ ] `.agent/memory/` updated if anything non-obvious was decided or discovered

**Never use `--no-verify`.** The hook is this checklist enforcing itself; skipping it
commits exactly what it existed to stop.

---

## Issues and Pull Requests

### Create an issue

MCP: `create_issue` — verify the exact name via `get_tool_schema` first.

`gh` fallback:
```powershell
gh issue create --title "<clear, specific title>" --body "<repro steps or acceptance criteria>" --label bug
```

### Open a PR

MCP: `create_pull_request`.

`gh` fallback:
```powershell
gh pr create --base main --head <branch> --title "<title>" --body "<description>

Closes #34"
```

**Link the issue in the body with `Closes #N`** so GitHub auto-closes it on merge. Don't
close issues by hand — the link is what creates the audit trail.

### Check CI before asking for review

MCP: `list_workflow_runs`.

`gh` fallback:
```powershell
gh pr checks <pr-number>
gh run list --branch <branch> --limit 5
gh run view <run-id> --log-failed    # read the actual failure, don't guess
```

**Never open a PR on a red branch.** "CI will probably pass" is not a status check.

---

## Tagging Releases

Semantic versioning — `MAJOR.MINOR.PATCH`:

```powershell
git tag -a v1.2.0 -m "Release v1.2.0 — adds JWT refresh token rotation"
git push origin v1.2.0
```

Annotated tags (`-a`) for releases, never lightweight ones — they carry the tagger, date,
and message.

---

## Branch Cleanup

```powershell
git checkout main
git pull origin main
git branch -d feature/<slug>
```

`-d` refuses to delete unmerged work; that refusal is a safety feature. Don't reach for
`-D` without checking why it objected.

---

## Destructive Git — the commands that lose work

Git is mostly append-only, which makes the handful of commands that *aren't* especially
dangerous: they look like ordinary workflow and they delete work that was never committed.
**Uncommitted and untracked work has no reflog.** Run `guard-destructive`'s five gates
before any of these.

| Command | What it destroys | Do this first |
|---|---|---|
| `reset --hard` | All uncommitted changes, silently | `git stash -u` or `git status --short` and read it |
| `clean -fd` | **Untracked files — unrecoverable, no reflog** | `git clean -nd` and read the list |
| `checkout -- .` / `restore` | Uncommitted changes to those paths | `git diff` first |
| `branch -D` | An unmerged branch | `git log <branch> --not main` — see what's actually there |
| `stash drop` / `clear` | Stashed work | `git stash list` and `git stash show -p` |
| `commit --amend` | The previous commit's message and contents | Only ever on an unpushed commit |
| `rebase` | Linear history, and any commit you drop | Branch first: `git branch backup/<slug>` |
| `push --force` | **Everyone else's history** | Don't — see below |
| `filter-branch` / `filter-repo` | The entire history | Full clone backup first |
| `gc --prune=now` | The reflog — your last recovery net | Basically never; let git do it |

**Force-pushing.** Plain `--force` overwrites whatever is on the remote, including commits
someone else pushed thirty seconds ago that you've never seen. If a force-push is genuinely
required:

```powershell
git push --force-with-lease origin feature/<slug>
```

`--force-with-lease` refuses when the remote moved under you — that refusal is the entire
point. **Only on your own feature branch, only after saying so explicitly.** Never on
`main`, never on a branch someone else has checked out.

**The recovery net, when you get it wrong:**

```powershell
git reflog                       # committed work is here for ~90 days
git reset --hard HEAD@{2}        # back to a known-good point
git fsck --lost-found            # dangling commits, when reflog isn't enough
```

That net covers **committed** work only. `git clean -fd` on untracked files and
`git checkout -- .` over uncommitted edits leave nothing to recover. Those two deserve the
most caution precisely because they look the most routine.

---

## Rules

- **Never commit directly to `main`** — branch and PR, always
- **Never commit red** — zero errors, green suite, or it doesn't go in
- **Never commit secrets or `.env`** — and note that adding a pattern to `.gitignore` does
  **not** untrack an already-tracked file; that needs `git rm --cached` too
- **Confirm before anything outward-facing** — pushing, opening a PR, commenting on an
  issue, or cutting a release is visible to other people and awkward to undo
- **Never force-push without explicit confirmation**, and then only `--force-with-lease`,
  and only to your own branch — plain `--force` rewrites history for everyone
- **Never `reset --hard` or `clean -fd` with uncommitted work present.** Stash first, or
  don't run it. Untracked files have no reflog and do not come back
- **Deleting a remote branch, tag, or release is destructive and outward-facing** — it
  breaks other people's checkouts and any link pointing at it. Confirm explicitly
- **One logical change per commit** — don't bundle unrelated work
- If `git status` shows files you don't recognize, investigate before staging anything —
  and never resolve that confusion with `git clean`
