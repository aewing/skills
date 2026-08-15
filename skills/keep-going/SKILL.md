---
name: keep-going
description: Maintain progress on multi-step, long-running, or open-ended work. Use for migrations, rollouts, audits, recovery, infrastructure, curation, or any goal with several dependent verification units. Keep explicit remaining state, choose the next causal unit, verify it, and continue until the agreed outcome is complete or genuinely blocked.
---

# Keep going

Maintain one outcome and an explicit work model. Do not ask the user to choose a
next step that follows directly from the stated goal and repository authority.

## Loop

1. Restate the outcome and current falsifier in one sentence.
2. Split remaining work into the smallest units with an owner, observable done
   condition, and proof command.
3. Choose the unit that removes the largest causal blocker or risk.
4. Load only the owning package spec and skills triggered by that unit.
5. Implement, run the proof, inspect the artifact, and update remaining state.
6. Review the cumulative delta at meaningful milestones.
7. Continue while a safe, in-scope unit remains.

Use the plan tool for multi-step state when available. Do not create a markdown
status file unless that repository declares it as the canonical work record.

## Decision boundary

Continue through reversible implementation choices. Ask the user only when a
missing choice changes product direction, canonical ownership, safety, external
communication, or irreversible state. Lead with the recommended choice and its
consequence.

When blocked:

- reproduce the exact blocker;
- finish independent work around it;
- name the missing authority, access, artifact, or decision;
- provide one concrete unblock action.

Do not replace forward work with repeated status summaries. Do not turn nearby,
unrelated debt into the task.

## Milestone review

Use `adversarial-reviewer` on the raw cumulative diff and verification evidence.
Use `verification-hygiene` before any completion claim. Load a domain skill
(runtime, storage, infrastructure, or feature-family) only when its boundary is
actually touched.

## Handoff

Hand off result-first: the answer, up to three proved changes, one next action,
and one bounded human decision only if required. Completion means the agreed
outcome is observed in the real artifact, not merely that the work list became
tidy.
