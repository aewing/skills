# Synthetic review contract

Load this reference for `focus-group review`.

## Research brief

Write a short brief before simulating the room:

- subject and artifact version;
- product decision the session informs;
- target users and excluded populations;
- research questions;
- selected procedure and why it fits;
- evidence available, unavailable, or stale;
- selected participants and the causal reason for each seat.

Do not broaden a feature review into a market-demand claim. If no working
artifact exists, label tasks as expectation walkthroughs rather than usability
tests.

## Panel selection

Use four to seven participants. Diversity is functional rather than decorative:
each seat should change what the panel can notice. Useful dimensions include
domain experience, technical fluency, access method, trust posture, frequency of
use, environmental constraint, responsibility for failures, and whether the
subject is used directly or integrated into another workflow.

Avoid panels built from a single axis such as age or job title. Do not include a
participant merely so the report can claim representation. When a real affected
population is not captured by a credible profile, record that as a real-user
research need.

## Moderation record

Before discussion starts, copy the procedure's `moderationBudget` into the
moderator guide and name the selected task count. Do not exceed
`maximumTasks` or `followUpRoundsPerPhase` by default. Stop when every required
record is captured and the procedure's `stopWhen` condition is met. If an
evidence gap justifies an extension, follow `extensionRule`: record the reason,
added task or round, and moderator decision in `SESSION.json` and the transcript
before continuing.

Every phase records:

1. moderator prompt;
2. participant expectation before action;
3. attempted action or concept reaction;
4. artifact response or cited evidence;
5. participant interpretation;
6. follow-up and cross-talk;
7. moderator close naming agreement, disagreement, and unresolved evidence.

Use participant voices consistently but sparingly. Voice fields affect cadence
and vocabulary; they do not license dialect parody, catchphrases, or exaggerated
confusion. Let a participant revise their view after seeing evidence.

The transcript is complete when another reviewer can reconstruct what was asked,
what each participant encountered, and why a finding appears in the synthesis.
Do not use omissions such as “discussion continued” or invent off-record
consensus. User-facing explanations are enough; private chain-of-thought is not
part of the artifact.

“Full” means every exchange inside the bounded session, including dissent and
approved extensions. It never means unbounded repetition, and the budget can
never be satisfied by truncating dialogue or replacing it with a summary.

## Evidence classes

Use exactly one primary evidence class per finding:

| Class | Meaning |
| --- | --- |
| `observed` | The moderator exercised or inspected the real artifact and recorded its response |
| `documented` | A current owner document, specification, design, or requirement directly supports the claim |
| `persona-inferred` | The reaction follows from a fictional profile and available context but was not observed from a human |
| `moderator-inferred` | The synthesis connects several session facts; the connection remains an inference |
| `unknown` | Evidence is insufficient; the finding is framed as a research question |

Never upgrade `persona-inferred` because several fictional participants repeat
it. Correlated simulation is not independent confirmation.

## Finding record

Each finding contains:

- stable id and concise title;
- claim and evidence class;
- exact artifact evidence or explicit lack of it;
- affected participant ids and any dissent;
- severity: `blocker`, `high`, `medium`, `low`, or `positive`;
- confidence: `high`, `medium`, or `low`;
- owner or owner-discovery state;
- smallest response that would change the result;
- one outcome disposition and fingerprint.

Severity describes product consequence, not how dramatically a participant
speaks. A positive finding still receives a disposition, commonly `no-action`,
`decision-record`, or a design principle worth preserving.

## Session bundle

Use the project-standard review/evidence location. If none exists, use the
configured fallback without inventing a second task backlog.

### `SESSION.json`

Record schema `focus-group/session@1`, run id, timestamps, subject, research
questions, artifact references, configuration version, selected profile ids and
revisions and causal `selectionReason` values, snapshotted configuration profile
pool and project panel bounds, procedure id and revision, procedure panel
bounds, moderation budget, phase ids, required outputs, evidence limits, any
moderation-budget extension, and paths to the other bundle files. These
snapshots keep completed runs valid when the active library later changes. Runs
captured before procedure revision 2 retain their original pre-budget snapshot
rather than pretending the later budget was applied retroactively.

### `PARTICIPANTS.md`

Start with the synthetic-research label. For each participant, include role,
context, goals, capabilities, needs, constraints, and guardrails plus the source
profile id/revision. Do not rewrite profiles to foreshadow the findings.

### `TRANSCRIPT.md`

Start with the label and research brief. Preserve the complete moderated record
by phase. Use one heading per snapshotted phase in the form
`## Phase <one-based number> — <readable phase title>`; the title includes the
meaningful words from the phase id. Prefix each action or evidence observation
with its evidence class. Participant quotations belong only to the fictional
participant named.

### `FINDINGS.md`

Lead with the decision informed, then the highest-severity observed finding,
strongest persona-based hypothesis, meaningful disagreement, positive behavior
to preserve, and limits. Include a table mapping every finding to its outcome
id.

### `OUTCOMES.json`

Follow [`outcome-contract.md`](outcome-contract.md). This is the machine-
readable completion surface for recommendations and project routing.

## Completion test

A review is complete only when:

- every selected profile and procedure revision is recorded;
- the transcript covers every procedure phase without placeholder omissions;
- every finding cites evidence and maps to one outcome;
- every outcome has a route state and stable fingerprint;
- created local artifacts exist, and external drafts are clearly not claimed as
  created tasks;
- limits name what only real users, production data, or a different artifact
  can answer.

Run the mechanical completion gate before reporting the review complete:

```bash
python3 /absolute/path/to/focus-group/scripts/validate.py run .focus-group/runs/YYYY-MM-DD-subject
```

The gate checks file presence, labels, snapshot consistency, participant and
phase coverage, placeholder omissions, outcome validity, and the exact
finding/outcome mapping. It deliberately does not score prose style or insight.
