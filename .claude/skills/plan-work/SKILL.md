---
name: plan-work
description: "Plan before implementing. Use when: starting a feature, designing architecture, evaluating competing approaches, scoping a refactor, or attacking a non-obvious bug. Produces a written plan in TODO.md and a self-critique pass before any code is written."
argument-hint: "The problem or decision to plan through"
---

# Plan Work — Write It Down Before You Write Code

> **In this repo:** AGENTS.md has no tiers. Plan anything past a typo in `TODO.md` under "Active". A
> **research hypothesis** uses the stage template in `lp-attack` (step 6), which adds the model, family size,
> pre-declared pass, exclude and inconclusive thresholds, and controls. That template is mandatory, because a
> result whose threshold was set after the run is not evidence. Stages are lettered (A–O are done, see TODO "Done").

Reasoning happens natively. What this skill enforces is that the reasoning **leaves an
artifact**. A plan that lives only in the chat window cannot be checked, cannot survive a
truncated context, and cannot be reviewed. Write it to `TODO.md`.

> Replaces the old `think-plan` skill. The `think` MCP server was dropped — the round-trip
> added latency without improving the output, and an MCP call leaves no evidence that the
> step happened. A file does.

## When to Use

- Anything past a one-line fix
- Choosing between two viable approaches
- A refactor touching more than 2 files
- A bug whose cause isn't obvious after one read
- Before writing tests — deciding which edge cases actually matter

**Skip it** for typos, comments, single-line fixes. Planning a typo is theatre,
and theatre is how an instructions file loses credibility.

## Procedure

### Step 1 — Frame the problem before solving it

Answer these explicitly. Vagueness here produces a plan that dissolves on contact with the code.

- **What is actually being asked?** Restate it in one sentence.
- **What does done look like?** How will you *prove* it works — which test, which command?
- **What constraints are real?** Existing patterns, stack, performance, backward compat.
- **What is unknown?** Anything requiring `code-explore` or `research-docs` first.

If step 1 produces an unknown that changes the shape of the plan, **stop and resolve it
first.** Planning around a guess wastes the whole plan.

### Step 2 — Consider at least two approaches

One approach is not a decision, it's an assumption. Name a real alternative and say why
it loses. If you genuinely can't name a second approach, that's a signal you don't
understand the problem yet — go back to step 1.

For each: what it costs, what it risks, what it makes hard later.

### Step 3 — Write the plan to TODO.md

Not to the chat. To the file.

```markdown
## <Task name>

**Goal:** <one sentence — what "done" means>
**Approach:** <the chosen approach, and the one-line reason it beat the alternative>
**Not doing:** <explicit out-of-scope list — this is what stops scope creep>
**Blast radius:** <what this destroys or overwrites, and where it comes back from —
                  or "none: additive only">

- [ ] 1. <concrete step — names a real file>
- [ ] 2. <concrete step>
- [ ] 3. <test that proves it works>

**Rollback:** <the exact command that undoes this — not "revert the change">
```

Rules for the step list:
- **Each step names a real file or command.** "Implement the feature" is not a step.
- **Each step is independently verifiable.** You should be able to build after each one.
- **Tests are steps, not an afterthought** appended at the end.
- **Any destructive step is called out as destructive**, with its own undo command. Run
  `guard-destructive` when you reach it — planning it is not the same as gating it.
- **More than ~8 steps** — split it into stages with commits between.

**`Blast radius:` and `Rollback:` are mandatory fields**, including when the answer is
"none, this is purely additive". Writing "none" is a claim you've checked; leaving it blank
is a claim you haven't. `Rollback: git revert <commit>` only counts if the change is
actually confined to the repo — it does not undo a dropped table or a deleted file.

### Step 4 — Critique your own plan before executing

Read the plan back and attack it. Answer each:

1. **What breaks?** Which existing caller, test, or consumer does this disturb?
2. **What did I assume?** List assumptions unverified in the actual code. Verify them now.
3. **What's the failure mode?** If step 3 fails halfway, what state is the repo in?
   **If the answer involves lost data rather than a broken build, stop and re-plan** —
   reorder so the irreversible step is last, and comes after a verified backup.
4. **What's missing?** Error handling, logging, edge cases, the empty/null case.
5. **Am I rebuilding something?** Did `code-explore` confirm this doesn't already exist?
6. **Is this the smallest thing that works?** Cut anything not serving the stated goal.

**Fix the plan before writing code.** If the critique finds a structural flaw, go back to
step 1 — not step 3. A patched bad plan is still a bad plan.

### Step 5 — Record the decision

If step 2 involved a real choice between alternatives, use `save-memory` to append it to
`.agent/memory/decisions.md` **before implementing** — while the reasoning is fresh and
the rejected alternative is still in your head. Written afterward, the `Rejected:` field
is always thinner and less honest.

## Rules

- **The plan goes in `TODO.md`.** If it's only in chat, the step didn't happen.
- **Always name a rejected alternative.** No alternative means no decision was made.
- **`Blast radius:` and `Rollback:` are never blank** — "none, additive only" is a valid
  answer; an empty field is not.
- **Irreversible steps go last**, after everything reversible has been verified.
- **Check `.agent/memory/decisions.md` first** — don't re-plan something already settled.
- **Update `TODO.md` as you execute.** A plan that doesn't track reality is worse than none,
  because the next session trusts it.
- If the critique in step 4 finds nothing, you critiqued it too gently. Try harder or
  admit the task is trivial.
