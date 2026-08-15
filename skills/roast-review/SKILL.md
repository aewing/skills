---
name: roast-review
description: >-
  Produce an evidence-backed roast of a concept, proposal, feature, product
  surface, workflow, or implementation: a funny, ruthless, specific reduction
  to its weaknesses, cultural misalignment, and technical self-owns, followed
  by a concrete escape plan. Use when asked to roast, brutally review, sharpen,
  or pressure-test, or to create docs/proposals/{subject}/ROAST.md, PROPOSAL.md,
  and EVIDENCE.md.
---

# Roast Review

Use this skill to make critique memorable without making it sloppy. The roast is
not a vibe-check with jokes sprinkled on top. It is evidence compression: find
the target's claimed identity, prove the contradiction, then write the shortest
funny line that makes the weakness impossible to unsee.

This is inspired by roast craft, not imitation of any comic's voice. The target
is the artifact, decision, surface, or concept. Do not attack protected traits,
private people, bodies, trauma, or facts you cannot prove.

## Workflow

### 1. Frame the Target

Name the subject and create `docs/proposals/{subject}/` unless the user gives a
different path. Normalize `{subject}` to a short slug.

Before writing jokes, answer:
- What does this thing think it is?
- What job or culture does it claim to serve?
- What would "aligned" mean in this project?
- What evidence would prove it is pretending?

Common alignment rails in a serious repo: real artifact verification,
package-owned public surfaces, runtime facts over source intent, no fake
renderers, no secret-handling theater, and no summary pretending to be proof.
Use the project's own stated rules when they are stronger.

### 2. Gather Receipts

Read the real artifact. Use files, docs, diffs, screenshots, logs, command
output, issues, PR comments, or live behavior as evidence. Every serious punch
in `ROAST.md` must trace to `EVIDENCE.md`.

Collect receipts in this shape:
- claim: the weakness or contradiction
- proof: file:line, command output, screenshot, URL, or observed behavior
- cultural read: why this violates the project's taste, law, or common sense
- repair handle: where the proposal can fix it

If you cannot prove a joke, either cut it or mark it as a hunch in
`EVIDENCE.md` and keep it out of the main roast.

### 3. Find the Roast Premise

A roast premise is usually one of these contradictions:
- self-image vs behavior: "It calls itself the public surface but arrives wearing app-local glue."
- confidence vs competence: loud claims, missing proof.
- sophistication vs simple failure: elaborate architecture dodging the obvious job.
- culture mismatch: the thing borrows the project's aesthetic while violating its own stated rules.
- overfitting: solves one demo path while making the real workflow worse.
- borrowed status: uses serious nouns without doing serious work.
- false economy: saves one hour now by billing the next five agents.

Reduce the target to one sentence:

```text
This is <claimed identity> that actually behaves like <embarrassing but accurate mechanism>.
```

That sentence is the roast's spine. Everything else is a tag.

### 4. Write Like a Sniper

Prefer specific, local, topical lines over generic insults. The best roast line
contains:
- a real noun from the artifact,
- a visible contradiction,
- a surprising compression,
- and a fixable implication.

Use the craft loop:
1. setup: name the factual self-presentation.
2. turn: expose the contradiction.
3. tag: escalate once with a sharper, project-local image.

Good line shape:

```text
It says "production-ready" with the confidence of a launch announcement, then
imports the sibling package like it found a side door at a fire inspection.
```

Cut any line that is only mean, only clever, or only true. The target is
funny-truth: a joke that still works when the reader opens the receipt.

### 5. Produce the Folder

Write exactly these files unless the user asks for more:

`ROAST.md`
- Title and one-line verdict.
- The core premise: what the subject thinks it is vs what it is.
- 5-12 numbered roast hits, each specific enough to trace to receipts.
- A "fatal vibe mismatch" section naming the deepest cultural flaw.
- A "best line that is also true" pull quote.
- End with the shortest possible diagnosis, not a soft summary.

`PROPOSAL.md`
- One-line objective: how the subject escapes the roast.
- Ordered remediation plan, grouped into coherent phases if needed.
- Owner surface for each fix: app, package, descriptor, docs, tests, runtime, etc.
- Verification plan using real commands or real artifact checks.
- Non-goals and tradeoffs if relevant.

`EVIDENCE.md`
- Source map: files, commands, URLs, screenshots, logs, or observed behavior.
- Receipts table: claim, evidence, why it matters, linked roast hit.
- Open questions and weak evidence called out honestly.
- Repro steps for any behavioral claim.

## Decision Tree

Use this before publishing:

1. Can I cite the receipt? If no, cut or move to open questions.
2. Is the punch about the artifact's choices, not identity or protected traits?
3. Does the line reveal a weakness a serious reviewer would also care about?
4. Is it local to the subject, or could it be pasted onto anything? If generic, rewrite.
5. Does `PROPOSAL.md` make the roast escapable? If not, the critique is theater.
6. Would the target's owner recognize the truth even if they hated the tone?

## Composition Contract

For implementation or architecture targets, load the project's architecture and
boundary rules before writing, so the cultural verdict is grounded in the actual
owner surfaces and stated law. Sanity-check receipts for fairness and verify
code-facing claims against the real artifact before you publish the roast.
