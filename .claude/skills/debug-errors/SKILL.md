---
name: debug-errors
description: "Systematic error triage with a hard attempt budget. Use when: build fails, type errors appear, runtime exceptions occur, diagnostics return problems, or something that worked stopped working. Drives to zero errors, or to a documented blocker — never to a suppression."
argument-hint: "The error message or a description of the failure"
---

# Debug Errors — Triage to Zero, or to a Documented Stop

Fix root causes, not symptoms. Never apply a fix you can't explain. **This loop has a
budget of 3** — see below. Grinding past it produces worse code than stopping does.

## When to Use

- Diagnostics return errors (`get_errors`)
- A build or typecheck exits non-zero
- A runtime exception appears in logs
- "It was working and now it's not"

> **Assertion failures belong to `test-iterate`, not here.** This skill is for errors;
> that one is for a test that ran correctly and reported the wrong answer.

---

## The Budget

| Attempt | What you do |
|---|---|
| 1 | Diagnose, form a hypothesis, apply the minimal fix. |
| 2 | **Re-diagnose from scratch.** Attempt 1 failing means the diagnosis was wrong, not the fix. Do not patch the patch. |
| 3 | Last attempt. Narrow it — add logging, isolate in a scratch file, bisect the change. |
| 4 | **STOP.** Write to `.agent/memory/gotchas.md` and report to the user. |

**Stopping at 3 is a correct, professional outcome.** A clear report — "here is the error,
here are three hypotheses I tested, here is what each ruled out, here is where I'd look
next" — is far more useful than a fourth guess that mutates unrelated code.

**What is never acceptable** is widening the fix so the symptom disappears: adding
`@ts-ignore` / `as any` / `# type: ignore`, an empty `catch`, an `eslint-disable`, or
deleting the code that surfaced the error. That converts a visible bug into an invisible one.

---

## Procedure

### Step 1 — Collect every error before fixing any

```
get_errors()                    // whole workspace
get_errors(filePaths: [...])    // or scoped to changed + related files
```

Do not start fixing from a partial list. Errors cascade — the 12th message is often the
only real one, and fixing #1 in isolation can be fixing a symptom of #12.

**Find the first error, not the last.** Compilers report cascades; the first failure is
usually the true one.

### Step 2 — Read the actual output

For runtime errors, get the full stack trace:

```powershell
Get-Content .\logs\app.log -Tail 50
```

Read the **whole** trace, not the last line. The root cause is usually several frames up,
in the caller. If the trace is truncated or unhelpful, that's a signal to add logging
(step 5) rather than to guess.

### Step 3 — Read the code in context

```
read_file(filePath, startLine, endLine)
```

At least 20 lines either side. The reported line is where the problem *surfaced*, not
where it *originated* — that's usually the caller or the type definition.

For type errors, read the type itself before touching anything:

```
grep_search(query: "interface <TypeName>|type <TypeName>", isRegexp: true)
```

### Step 4 — State the hypothesis before editing

Write it out explicitly — one sentence each:

- **Symptom:** the exact error text
- **Hypothesis:** why it happens, mechanically
- **Prediction:** what changes if the hypothesis is right
- **Minimal fix:** the smallest edit that tests it

**A fix without a stated hypothesis is a guess**, and guesses create new errors while
hiding old ones. If you can't fill in "Hypothesis", you haven't read enough yet — go back
to step 3.

### Step 5 — When you can't form a hypothesis, get data

Don't guess harder. Make the failure observable:

- Add logging around the failure point — inputs, state, branch taken
- Re-run and read the real values
- Isolate the failing piece in a scratch file
- Bisect: what was the last state where this worked?

Adding logging is progress, not a detour. It also usually stays in as the error-path
logging the code should have had.

### Step 6 — Apply the minimal fix, one at a time

One change. Then re-check:

```
get_errors()
```

**Never stack multiple fixes before re-checking.** If you change three things and the
error count drops, you've learned nothing about which one mattered — and you may have
added two new problems masked by the fix to the first.

If the fix requires a third-party API you're not certain of, use `research-docs` before
writing it. Inventing an API signature from memory is how attempt 2 gets burned.

### Step 7 — Verify to zero

Repeat 3–6 until `get_errors()` is clean, then run the real build via `build-run`.
Zero diagnostics **and** a clean build. Diagnostics alone are not proof — they don't
catch everything a bundler does.

### Step 8 — Record it

If the bug took more than 2 attempts, or the cause was non-obvious, append to
`.agent/memory/gotchas.md` via `save-memory`. **If you exhausted the budget, this is
mandatory** — that is exactly the case the file exists for.

Include the dead ends. "We tried X, it doesn't work because Y" is what stops the next
session from burning an hour on X.

## Rules

- **Budget of 3.** Then stop and report. No exceptions.
- **Two failures means the diagnosis is wrong**, not the fix. Re-diagnose, don't re-patch.
- **No suppressions.** Ever, without an explicit written justification the user has agreed to.
- **Read before you edit.** Always.
- **One fix per verification cycle.**
- **Never delete code to make an error go away** unless deleting it is genuinely the fix.

## Error Pattern Reference

| Pattern | Likely cause |
|---|---|
| `Cannot find module` | Missing install, wrong path, missing path alias in tsconfig |
| `Property X does not exist on type Y` | Stale type, wrong generic, needs a narrowing guard |
| `is not assignable to type` | Read **both** types fully before touching either |
| `undefined is not a function` | Wrong import shape (default vs named), or missing `await` |
| `Cannot read properties of undefined` | Missing null check, or an async result used before it resolved |
| `ENOENT: no such file` | Wrong CWD — check where the process actually starts |
| `EADDRINUSE` | Leaked dev server from an earlier run; kill it |
| Works locally, fails in CI | Env var, case-sensitive path, or install-order difference |
| Intermittent failure | Race condition, shared state between tests, or real clock/timezone dependency |
