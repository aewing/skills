# Focus-group configuration contract

Load this reference for `standards`, `profiles`, `procedures`, or configuration
validation. The project configuration is a policy selector and reusable library,
not a product specification or work backlog.

## Layout

```text
.focus-group/
|-- config.json
|-- profiles/
|   `-- <profile-id>.json
|-- procedures/
|   `-- <procedure-id>.json
`-- runs/                       Generated only when the project has no narrower session path
```

`config.json` uses schema `focus-group/config@1`. Profile files use
`focus-group/profile@1`; procedure files use `focus-group/procedure@1`.
Lowercase kebab-case ids are stable. Alter an object by incrementing `revision`;
retire it with `status: "retired"` rather than reusing its id for another
character or procedure.

## Reproducible initialization

`standards init` creates the `profiles/` and `procedures/` directories plus the
exact proposed configuration below. It does not copy universal personas or
procedures: those are project-owned judgments, and pretending otherwise would
turn one repository's assumptions into everybody's users.

```json
{
  "schema": "focus-group/config@1",
  "id": "project-focus-group",
  "version": "1",
  "status": "proposed",
  "library": {
    "profiles": "profiles",
    "procedures": "procedures"
  },
  "panel": {
    "minimum": 4,
    "maximum": 7,
    "profilePool": [],
    "selectionRules": [
      "Every selected seat must add a causal product perspective, not demographic decoration.",
      "Include a direct user and a newcomer or infrequent user when the subject has an end-user surface.",
      "Include a relevant access or environmental constraint when it can change task completion.",
      "Include a builder or operator only when they integrate, maintain, support, or bear failure cost.",
      "Include an agent only when an agent uses, integrates, operates, or is affected by the subject."
    ]
  },
  "review": {
    "defaultProcedure": null,
    "syntheticLabel": "SYNTHETIC FOCUS GROUP — NOT HUMAN RESEARCH",
    "transcript": "full",
    "artifactResolution": "project-standard-first",
    "fallbackRunDirectory": ".focus-group/runs"
  },
  "outcomes": {
    "requiredDispositions": [
      "work-item",
      "design-concept",
      "feature-request",
      "decision-record",
      "research-question",
      "no-action",
      "needs-routing"
    ],
    "routingOrder": [
      "user-request",
      "focus-group-config",
      "project-authority-and-owner",
      "existing-canonical-artifact",
      "needs-routing"
    ],
    "externalWrites": "explicit",
    "deduplicateBy": "fingerprint"
  }
}
```

A proposed configuration may have an empty profile pool and no default
procedure. Activate it only after the project has created enough distinct
profiles to satisfy `panel.minimum`, created at least one bounded procedure,
selected an active default procedure, passed validation, and accepted the
project location. Initialization is therefore structurally reproducible without
claiming a portable user baseline.

## Configuration fields

| Field | Meaning |
| --- | --- |
| `schema`, `id`, `version`, `status` | Bundle identity and lifecycle |
| `library.profiles`, `library.procedures` | Directories relative to the config root |
| `panel.minimum`, `panel.maximum` | Allowed participant count |
| `panel.profilePool` | Active profiles eligible for causal selection; order has no selection meaning, this is not a selected panel, and it may exceed `panel.maximum` |
| `panel.selectionRules` | Project-specific coverage rules |
| `review.defaultProcedure` | Procedure id used when the request does not select one |
| `review.syntheticLabel` | Required label on every human-facing artifact |
| `review.fallbackRunDirectory` | Session evidence path only when project standards name no narrower path |
| `outcomes.requiredDispositions` | Complete disposition vocabulary |
| `outcomes.routingOrder` | Authority order for choosing destinations |
| `outcomes.externalWrites` | Approval behavior at remote write boundaries |
| `outcomes.deduplicateBy` | Stable identity rule for retries |

`standards alter` changes defaults or routing policy. It does not edit a profile
or procedure as a side effect. Validate the complete library after every
configuration change.

## Profile contract

A profile is a fictional composite with enough concrete context to produce a
distinct, bounded evaluation lens.

Required fields:

- `schema`, `id`, `revision`, `status`, `name`, `role`, and `summary`;
- `context`: what the person is doing and why the subject appears in their life;
- non-empty `goals`, `capabilities`, `needs`, `constraints`, `behaviors`, and
  `questions` arrays;
- `voice`: `tone`, `language`, and `challengeStyle` for transcript consistency;
- `guardrails`: assumptions the moderator must not make about this profile.

### `profiles create <id>`

1. Name the missing product perspective and the decision it could change.
2. Prefer situational constraints over demographics. Include demographic or
   access information only when it causally changes the interaction.
3. Write concrete capabilities alongside limitations.
4. Give the participant at least one goal unrelated to finding faults.
5. Add guardrails against the most tempting stereotype.
6. Validate the new file and check that its lens does not duplicate an existing
   active profile.

### `profiles alter <id>`

Preserve `id`, increment `revision`, and make the narrow requested change. Show
the semantic difference in the response. An altered profile affects future runs
only; completed sessions retain their recorded revision and snapshot. If the
person has become a different evaluation lens, create a new profile instead.

## Procedure contract

A procedure codifies a research decision, not a script full of interchangeable
questions.

Required fields:

- `schema`, `id`, `revision`, `status`, `name`, `purpose`, and `suitableFor`;
- `panel.minimum` and `panel.maximum` within the project panel limits;
- non-empty `inputs`, `phases`, `dimensions`, `stoppingConditions`, and
  `requiredOutputs` arrays;
- `moderationBudget.maximumTasks`, positive
  `moderationBudget.followUpRoundsPerPhase`, and explicit
  `moderationBudget.stopWhen` and `moderationBudget.extensionRule` strings;
- each phase has a unique `id`, a `mode`, a moderator `instruction`, and a
  `requiredRecord` list;
- `requiredOutputs` includes participant profiles, full transcript, findings,
  and outcomes.

### `procedures create <id>`

Define the research question, artifact required, phase order, task or discussion
mode, evidence captured at each phase, stopping conditions, and result needed by
the product decision. Reuse an existing procedure when only the subject or
participant wording differs.

### `procedures alter <id>`

Preserve `id`, increment `revision`, and state which decision or measured failure
justifies the procedural change. Completed runs keep their original revision.
Retire a procedure if its evidence model changes incompatibly.

## Validation

From the repository root:

```bash
python3 /absolute/path/to/focus-group/scripts/validate.py config .focus-group
```

The checker proves structural consistency, id uniqueness, profile-pool
existence, procedure panel and moderation bounds, required output coverage, and
known outcome vocabulary. It also accepts the exact empty proposed initializer
without mistaking it for an active standard. It cannot prove that a profile is
humane or that a procedure asks a useful research question; review those
judgments directly.
