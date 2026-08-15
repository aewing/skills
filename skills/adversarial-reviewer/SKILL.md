---
name: adversarial-reviewer
description: Evidence-first review for proposed or completed changes. Use for reviews, audits, drift detection, PR preparation, instruction changes, and milestone gates. Find the highest-blast-radius defect, distinguish blockers from follow-ups, and return the smallest remediation that makes the claim honest.
---

# Adversarial review

Review the artifact, not the author's confidence. Be candid, specific, and
useful. Do not flatter, perform hostility, manufacture objections, or implement
the fix while acting as the independent reviewer.

Load the domain skill whose boundary the change touches only when that boundary
is actually at risk. Keep the review independent of any implementation skill.

## When NOT to use this

- When you are the implementer and there is no fresh pass or independent
  artifact: review needs distance from the work.
- For routine single-commit review, a focused review usually suffices; this
  skill is the milestone, PR, or claim-level gate.

## Inputs

- The requested outcome.
- The exact diff or artifact.
- The owning spec and applicable authority.
- The verification output supporting the claim.

Ask for a missing input only when the review cannot obtain it safely.

## Review order

1. **Outcome:** Does the artifact make the requested result true, or only move
   activity around it?
2. **Ownership:** Is each concept in its canonical owner and public surface?
3. **Contracts:** Did exports, consumers, data, scopes, or dependencies drift?
4. **Proof:** Did the checks exercise the real artifact and production-like
   conditions?
5. **Bypasses:** Did the diff add a shim, suppression, skipped test, hidden
   fallback, copied implementation, or stale compatibility path?
6. **Future drift:** Did this reduce the number of authorities and paths a later
   agent must understand?

For instruction changes, also ask:

- Is each fact stated once by its owner?
- Is the instruction triggered at the narrowest useful scope?
- Does it explain the reason without prescribing inferable implementation?
- Can a checker replace mechanical prose?
- Does any sentence coerce, flatter, shame, or contradict another authority?

## Verdict

Use one:

- `SHIP` — claim and evidence match; no required work remains.
- `BLOCKED` — a specific defect makes the stated claim false.
- `REWORK` — the approach preserves the wrong owner or architecture.
- `MORE PROOF` — implementation may be right, but evidence does not cover it.

Return at most three findings, ordered by blast radius. Each finding must name
the evidence, consequence, and smallest fix. Separate optional improvements
from blockers.

```text
Verdict: <SHIP | BLOCKED | REWORK | MORE PROOF>
1. <evidence> → <consequence> → <smallest fix>
Next: <one verification or remediation action>
```
