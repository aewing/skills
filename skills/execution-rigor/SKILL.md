---
name: execution-rigor
description: Use for long-horizon execution tasks that need attention to detail, real verification, and high autonomy — quality control, adversarial review, and finishing work for real instead of calling it done half-finished. The user invoking this is signaling: no shortcuts and no half-measures.
---

# Execution Rigor

A recurrent execution loop for tasks where the failure mode is _"called done but actually half-finished."_ Sibling to `truth-loop` (which handles thorny _reasoning_); this one handles thorny _execution_.

The thing that breaks long-running execution work isn't lack of capability — it's the slow drift toward shortcuts: a `// TODO` instead of a fix, a skipped flaky test, a typed-`any` to make the compiler shut up, a "this works" claim where nobody actually ran it. This skill exists to make those drifts visible and forbidden, and to halt-and-re-plan rather than push through them.

The user invoking this is signaling: **don't take the easy way. If something is hard, say it's hard. If something is broken, fix it for real or surface the tradeoff. No half-measures.**

## When to use this

- The user explicitly invokes it ("do it right", "no workarounds", "the good stuff")
- A multi-step task where prior attempts produced incomplete work
- Tasks crossing more than one subsystem
- Anything where "looks done" and "is done" are likely to diverge

## When NOT to use this

- Small mechanical tasks (single-file edit, typo fix, simple refactor). Overhead dominates.
- Pure exploration / research questions — that's `truth-loop`'s job.
- When the user wants a fast answer or has explicitly de-scoped quality.

## Execution State

Maintain a single state object across phases. Update it as you go. Reference _the state_, not "what I said earlier."

```json
{
	"task": "<one sentence — what we're actually trying to accomplish>",
	"definition_of_done": [
		"<observable predicate 1: e.g., 'the package test suite passes with no skipped tests'>",
		"<observable predicate 2: e.g., 'binary X produces output Y on input Z'>",
		"<...>"
	],
	"lateral_check": "<one sentence — is there a sideways path that means we're solving the wrong problem?>",
	"todos": "<reference to the task-list tool — that's the source of truth, not this state>",
	"verification_log": [
		{
			"claim": "X works",
			"evidence": "ran the test command → 12 passed, 0 failed",
			"iteration": 1
		}
	],
	"tripwires_hit": [
		{
			"type": "skipped_test|todo_added|type_assertion|silent_catch|...",
			"location": "file:line",
			"resolution": "fixed|surfaced_to_user|forbidden_and_redone"
		}
	],
	"stuck_attempts": [{ "task": "...", "approach": "...", "failure_mode": "...", "iteration": 1 }],
	"deferred": [
		{
			"item": "...",
			"reason": "<not 'no time' — must be a real reason>",
			"user_acknowledged": true
		}
	],
	"convergence": "<diverging|stalling|progressing|nearly_done>"
}
```

## Phases

### 1. CONTRACT — definition-of-done up front

**Before any work starts**, write down what "done" means as **observable predicates**, not vibes.

Bad: "The feature works well." "Tests pass." "Code is clean."
Good: "`npm test` passes with zero skips and zero `.todo` files. The checkout service returns the documented response shape on a realistic 100-item input. The change loads in the main app without contract changes, verified by running one user journey end-to-end."

**Each predicate must be runnable.** If you can't write the command that verifies it, the predicate is too vague. Refine it.

If the user gave a vague task, **propose a concrete CONTRACT and ask for confirmation before proceeding.** This is the single highest-leverage moment of the whole skill — a sloppy CONTRACT means the loop converges to the wrong place.

### 2. MAP — territory + lateral scan

Explore what's affected. Use a subagent (an `Explore`-type agent in Claude Code) for breadth or `grep`/`Read` for known targets. Identify:

- Files / modules in scope
- Existing patterns in this codebase to follow (don't invent new ones if a sibling already solved a similar problem)
- **Lateral candidate**: name one _adjacent_ approach that might mean we're solving the wrong problem. ("Should this even be a new arch, or a flag on the existing one?")

If the lateral candidate is more compelling than the planned approach, **stop and surface it to the user.** Don't push through to be helpful — `execution-rigor` is supposed to defend against helpful-shaped wrongness.

### 3. PLAN — task-list breakdown

Break the work into tracked tasks. Each task must:

- Be independently completable
- Have its own _runnable verification_ (which predicate from CONTRACT does this satisfy, or how is it locally verified?)
- Be small enough that a "stuck" signal is meaningful (if a task takes more than ~30 minutes, it's too big — split it)

Mark one task as the active slot at a time. Mark a task complete only after VERIFY for that task passes.

### 4. EXECUTE — do the work

Use the right tools. Read before edit. Edit instead of full-write when possible. Don't over-comment. Don't add abstractions for hypothetical futures. Follow the codebase's existing conventions.

**Forbidden under this skill** (tripwire signatures — see phase 6):

- Adding `// TODO` / `// FIXME` / `// HACK` for the work the user actually asked for
- `it.skip` / `test.skip` / `.todo` to bypass a failing test
- `as any` / `as unknown as X` / `@ts-ignore` / `@ts-expect-error` to silence a real type error
- `try { ... } catch {}` (silent error swallowing)
- `// eslint-disable` / `// biome-ignore` to silence a real lint error
- "For now" / "temporarily" comments without an explicit ticket and user sign-off
- Mocking the thing being tested ("test passes against mock that always returns success")
- Hardcoding test fixtures so a broken assertion looks green

If you find yourself reaching for one of these, **halt and surface the tradeoff to the user.** Most of the time the user will help find a real fix.

### 5. VERIFY — run it, don't just claim it

After each task: **run the verification.** Not "type-check passes in my head" — actually run the test command, actually run the binary, actually open the UI, actually exec the command.

For each verification, log: { claim, evidence (command + output), iteration }. The verification log is your defense against the "looks defensible" failure mode caught by ADVERSARY in `truth-loop` runs.

**Special rule for UI / frontend changes:** type-check + test pass ≠ feature works. If the change is user-facing, you must verify in a browser (or say explicitly: "I cannot verify the UI; here's what I changed and how to check it manually"). Do not claim a UI feature works without seeing it.

If verification fails, the task is **not** complete. Fix or re-PLAN.

### 6. TRIPWIRE — scan for shortcut signatures

Between iterations (and definitely before declaring done), grep your changes for the forbidden patterns above. Specifically:

```bash
# Adjust language as appropriate
grep -nE 'TODO|FIXME|HACK|XXX' <changed-files>
grep -nE '\.skip\(|\.todo\(|@ts-ignore|@ts-expect-error|as any|as unknown as|eslint-disable|biome-ignore' <changed-files>
grep -nE 'catch\s*\([^)]*\)\s*\{\s*\}' <changed-files>  # silent catch
```

For each hit:

1. Was this introduced by _this_ task? Pre-existing tripwires get logged and surfaced so the user can decide; do not silently accept them.
2. If introduced: either fix properly, or escalate to the user with the specific tradeoff. Do not silently accept.

Log every tripwire hit and its resolution in `state.tripwires_hit`.

### 7. STUCK-CHECK — re-MAP after repeated failure

If the same task fails verification twice with the _same approach_, **stop trying variants.** Halt and re-MAP from a different angle. Stuck-loops produce slop.

The signal that you're stuck (not just iterating):

- Two consecutive attempts failed for related reasons
- "Let me try X" without an articulated reason why X solves what the previous failure was caused by
- Edits getting smaller and more local while the failing test stays red — you're polishing the surface around a deeper problem

When stuck: write a one-paragraph diagnosis ("the previous approach failed because Y; the lateral pivot is Z"), then re-PLAN. If you can't articulate why the previous approach failed, you don't understand the bug yet — go investigate before editing more code.

### 8. ADVERSARY — pre-completion audit

Before marking the whole task done, spawn a subagent (a general-purpose agent in Claude Code) with this brief:

> You are an adversarial auditor. The primary executor claims this task is done:
> [task]
>
> The CONTRACT predicates were:
> [definition_of_done]
>
> The verification log is:
> [verification_log]
>
> The tripwires logged are:
> [tripwires_hit]
>
> Your only job: find where the primary may have called this done while skipping work. Specifically look for:
>
> - Predicates in CONTRACT that don't have a corresponding entry in verification_log
> - Verifications that ran something _adjacent to_ but not actually the predicate (e.g., "build passed" instead of "test passed")
> - Tripwires "fixed" by being moved or renamed rather than addressed
> - Tasks marked complete without evidence
> - "Deferred" items that should not have been deferred
> - Anything that smells like reward-hacking on the appearance of completeness
>
> Be specific. Cite file:line or predicate id. If you find nothing, say so plainly. Under 350 words.

Fold flags into `state.tripwires_hit` and address them. Do not skip this phase — in a prior run, ADVERSARY caught a load-bearing reward-hack the rest of the loop missed.

### 9. OUROBOROS — fresh-perspective completeness check

Spawn a fresh subagent with **only**:

- The original task statement
- The final state of the changed files (or a summary of what changed)
- _Not_ the verification log, _not_ the task list, _not_ the state object

Brief:

> Here is the original task and the final state of the relevant code/system. If you came in cold and were told this task was done, would you agree? If not, what specifically is missing or wrong? Under 200 words.

If the fresh agent disagrees materially, run one more EXECUTE/VERIFY pass with their objection added. If they agree, proceed to EMIT.

### 10. EMIT — final state + evidence + falsifier

Final response **must include**:

1. **What was built** — direct, file-level. No padding.
2. **Verification evidence** — for each CONTRACT predicate, the command that proved it + the output (or a pointer to the verification_log line). If a predicate wasn't verified, say so explicitly and _don't_ claim done.
3. **Tripwires encountered + resolutions** — be honest about what shortcuts were tempting and how they were addressed.
4. **Deferred (with user-acknowledged reason)** — if anything was deferred, the explicit reason and the fact the user signed off. If nothing was deferred, say so.
5. **Falsifier** — one specific observable that would change your mind about completeness. "I'd reconsider this 'done' if X turned out to be Y."
6. **What we didn't check** — honest gaps. (This is the spot where over-confidence usually leaks in.)

## Extras that pay off

- **Variation tax.** Every "let me try a different approach" must include a one-sentence diagnosis of why the previous approach failed. No diagnosis = you don't understand the problem yet = stop editing and investigate.
- **Sunk-cost detector.** If a task has been "almost done" for 3+ iterations, halt and re-PLAN. The thing that's "almost done" is often actually wrong-shaped, and another iteration won't fix the shape.
- **Pre-mortem on fragility.** For each successful test, briefly answer: "what's the smallest realistic input that breaks this?" If you can name one, write a test for it. If you can't, you haven't thought hard enough — try again.
- **Evidence-trail discipline.** Every claim ("X works", "Y is fixed") gets tagged with the evidence (test name + output, screenshot, command). No bare assertions. Bare assertions are reward-hacking on appearance.
- **Refusal pattern.** If asked mid-loop to "just make it work" via a forbidden shortcut, the skill explicitly refuses, names the tradeoff, and offers the proper fix path. The whole point is the user invoked this _to be defended against the shortcut_; honoring the shortcut request betrays the brief.
- **Liminal mode tagging.** Each iteration declares its mode in `state.convergence`: `diverging` (re-MAP), `stalling` (STUCK-CHECK), `progressing`, or `nearly_done` (start ADVERSARY/OUROBOROS prep). Names the kind of pass.
- **Anti-completion-bias.** When `convergence: nearly_done`, deliberately spend one extra cycle looking for what could be wrong, _before_ the ADVERSARY phase. The cost is small; the cost of declaring done while still wrong is large.

## Rules of engagement

- **The user can always interrupt.** They can de-scope, redirect, or accept a workaround with explicit sign-off. Surface the tradeoff; don't decide for them.
- **No silent compromise.** If you take any shortcut, log it in `state.deferred` with the reason and the user's sign-off. If there's no sign-off, you're not done.
- **Memory respect.** Treat the project's explicit feedback and defaults — for example "no back-compat shims" or "no pre-existing issues" — as pre-stated CONTRACT.
- **Honest convergence.** When you mark `nearly_done`, you should be able to point at the verification log and the CONTRACT and say "every predicate has a green check." If you can't, you're not nearly done — you're optimistic.
