# Focus-group outcome contract

Load this reference for the outcome phase of `review` and for
`focus-group outcomes`.

The outcome ledger prevents synthetic research from dying as a handsome report.
Every finding is either materialized in the project's canonical system or given
an explicit reason it should not be.

## Dispositions

| Disposition | Use when | Expected payload |
| --- | --- | --- |
| `work-item` | A bounded implementation, repair, documentation, or validation task is ready | problem, owner, acceptance, evidence, dependencies |
| `design-concept` | The response needs interaction, content, visual, service, or architecture exploration before implementation | design question, constraints, concept, alternatives, proof plan |
| `feature-request` | A user capability is missing but solution and priority remain product decisions | user problem, desired capability, affected profiles, evidence, non-prescribed options |
| `decision-record` | The panel reveals a durable product choice or tradeoff worth preserving | decision, context, alternatives, consequence, owner |
| `research-question` | The claim needs real users, analytics, production evidence, or another experiment | question, population/evidence needed, falsifier, urgency |
| `no-action` | The product already handles the concern, the positive behavior should simply be preserved, or the issue is intentionally declined | reason, evidence, decision owner |
| `needs-routing` | A useful finding has no discoverable canonical owner or project destination | missing owner/destination, attempted discovery, bounded decision needed |

Do not use `needs-routing` as a generic backlog. It is a failed routing state
that names the exact missing project decision.

## Destination discovery

Resolve destinations in this order:

1. explicit destination in the current user request;
2. active `.focus-group/config.json` routing policy;
3. the project's authority router, owning spec, contribution guide, and named
   work or design system;
4. an existing artifact of the same type in the subject's owner;
5. `needs-routing` in the session ledger.

Do not create a new `TODO.md`, issue directory, proposal tree, design folder, or
external project merely because no route was found. The session bundle may hold
the payload until the project owner chooses its canonical destination.

## Manifest

`OUTCOMES.json` uses schema `focus-group/outcomes@1`:

```json
{
  "schema": "focus-group/outcomes@1",
  "runId": "2026-08-22-example",
  "subject": "Example feature",
  "items": [
    {
      "id": "FG-001",
      "findingId": "F-001",
      "title": "Make recovery visible after a failed import",
      "finding": "Participants could not tell whether retry was safe.",
      "evidenceClass": "observed",
      "evidence": ["TRANSCRIPT.md#task-2", "src/import.ts:88"],
      "severity": "high",
      "confidence": "high",
      "participants": ["gloria-grandmother", "priya-operator"],
      "disposition": "work-item",
      "owner": "import feature owner",
      "payload": {
        "problem": "Failure state has no recovery guidance.",
        "acceptance": ["A failed import names whether retry is safe and exposes the retry action."],
        "dependencies": []
      },
      "route": {
        "kind": "project-standard",
        "target": "<resolved canonical system>",
        "state": "draft",
        "receipt": null
      },
      "fingerprint": "sha256:f862494c0a1b1e63a4db2ecd66e22a7c62b0227ab0ea31ed06e5d56641189501"
    }
  ]
}
```

Allowed route states:

- `draft` — payload is ready but no project write occurred;
- `materialized` — canonical local or external artifact exists and `receipt`
  identifies it;
- `needs-approval` — destination is known but an external or protected write is
  not authorized;
- `needs-routing` — canonical destination or owner is unknown;
- `not-applicable` — valid only for `no-action`.

## Evidence promotion

Evidence class controls what may become accepted project state; a plausible
payload is not permission to promote a fictional reaction.

| Evidence class | Draft/approval behavior | Materialization behavior |
| --- | --- | --- |
| `observed`, `documented` | Any evidence-compatible disposition may remain a draft or await approval | May materialize with the ordinary route receipt |
| `persona-inferred`, `moderator-inferred` | May form drafts, including work-item-shaped hypotheses | A `work-item`, `feature-request`, or `decision-record` also requires explicit adoption by a responsible authority |
| `unknown` | Must use `research-question`, `needs-routing`, or justified `no-action` | May only record or materialize that research/routing/no-action result; it cannot become an implementation, feature, design, or decision claim |

The adoption record is top-level so it cannot be confused with a fictional
participant's evidence:

```json
{
  "adoption": {
    "by": "<responsible human or project authority>",
    "basis": "<why this hypothesis is being accepted as project work>",
    "receipt": "<decision comment, approval id, or other inspectable receipt>"
  }
}
```

Approval is not retroactive evidence. Keep the original evidence class and
finding unchanged; adoption records the real decision to own the hypothesis.
`design-concept` and `research-question` may materialize as explicitly
exploratory artifacts without adoption because they do not claim accepted
implementation scope or a durable product decision.

## Predictability rules

- Map every finding id to exactly one outcome item.
- Use stable ids within the run. Build the fingerprint by Unicode-NFC
  normalizing, case-folding, trimming, and collapsing whitespace in `subject`,
  `finding`, `owner`, and `disposition`; JSON-encode that four-string array with
  UTF-8 and no extra whitespace; then prefix its SHA-256 hex digest with
  `sha256:`. A retry with the same fingerprint updates the route receipt; it
  does not create a duplicate task.
- Keep the finding claim and evidence stable while materializing. Project-
  specific formatting may change; the evidence identity may not.
- Treat `FINDINGS.md` as the review-time record and `OUTCOMES.json` as the
  mutable delivery ledger. Later materialization updates the outcome route and
  receipt without rewriting the historical transcript or finding.
- Put acceptance criteria on `work-item`; do not disguise an open design or
  research question as implementation-ready work.
- Put a user problem on `feature-request`; do not prescribe the moderator's
  favorite solution as user truth.
- Link a `design-concept` to the constraint and proof plan that will decide
  whether it graduates to work.
- Record `owner` even when the route remains a draft. If no owner is discoverable,
  use `needs-routing` rather than inventing one.
- Materialized items retain the focus-group run id and finding id for provenance.
- Inferred `work-item`, `feature-request`, and `decision-record` items retain an
  `adoption` record when materialized. Never relabel them `observed` merely
  because an owner accepts the work.

## Materialization

`outcomes preview` validates the manifest, resolves destinations, checks for an
existing fingerprint, and shows the exact local or external writes without
performing them.

`outcomes materialize` performs reversible local writes authorized by the
current task and project rules. It may perform external writes only when the
user already authorized that destination or approves at the write boundary.
After each write, record its canonical id/path and observed state in `receipt`,
then validate the manifest again.

Materialization is incomplete if the report says “task created” while the route
state is `draft` or `needs-approval`.

## Validation

```bash
python3 /absolute/path/to/focus-group/scripts/validate.py outcomes .focus-group/runs/YYYY-MM-DD-subject/OUTCOMES.json
```

The checker rejects unknown dispositions or route states, duplicate ids or
fingerprints, missing evidence, invalid severity/confidence, work items without
acceptance criteria, unsupported promotion from `unknown`, inferred accepted
work without adoption, non-actionable outcomes without an owner, and
`no-action` items that pretend to be materialized work.
