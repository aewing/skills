---
name: focus-group
description: Run clearly labeled synthetic focus groups and persona-based usability reviews for a product, feature, concept, workflow, or implementation. Use when asked for a focus group, user panel, simulated user testing, multi-perspective product review, participant profiles, testing procedures, or a repeatable way to turn varied user reactions into project-standard work items, design concepts, decisions, and feature requests. Do not use as a substitute for real human research or for an ordinary single-reviewer code review.
---

# Focus Group

Use this skill to put a product in a room with the people it may affect before
calling it obvious, useful, or ready. The room is synthetic: participants are
fictional composites used as disciplined evaluation lenses, not sampled humans
or evidence of market prevalence.

Combine three established practices when the subject needs them:

- a **focus group** for moderated reaction and discussion;
- **usability testing** for realistic task attempts;
- a **cognitive walkthrough** for expectation, action, feedback, and recovery.

The active project configuration lives at project-root-relative
`.focus-group/config.json`. Profile and procedure schemas ship with the skill in
[`references/config-contract.md`](references/config-contract.md). Review and
outcome details are loaded only for those modes:

- For `review`, read
  [`references/review-contract.md`](references/review-contract.md).
- For outcome routing or materialization, read
  [`references/outcome-contract.md`](references/outcome-contract.md).

## Command modes

These are command-like skill modes. `focus-group review` selects a procedure;
it does not claim that a `focus-group` executable exists unless a live command
descriptor and implementation prove that surface.

| Mode | Purpose | Mutation |
| --- | --- | --- |
| `focus-group standards [show\|init\|alter]` | Show, initialize, or revise the project configuration and outcome-routing policy | Writes only after the intended project scope and owner are clear |
| `focus-group profiles [list\|show\|create\|alter\|retire]` | Manage reusable participant profiles | Scoped profile edits; preserve ids and increment revisions |
| `focus-group procedures [list\|show\|create\|alter\|retire]` | Manage moderated testing procedures | Scoped procedure edits; preserve ids and increment revisions |
| `focus-group review <subject>` | Select a panel, exercise the subject, preserve the complete synthetic session, and synthesize findings | Creates the configured local session bundle and eligible local outcomes |
| `focus-group outcomes <run> [preview\|materialize]` | Validate, deduplicate, route, or retry the outcome ledger from a completed run | Project-local writes follow project standards; external writes remain explicit |
| `focus-group validate [config\|run\|outcomes]` | Check configuration, a complete run bundle, or an outcome manifest | Read-only |

## Non-negotiable distinctions

- Put `SYNTHETIC FOCUS GROUP — NOT HUMAN RESEARCH` at the top of every human-
  facing session artifact. Never describe the panel as respondents, customers,
  interviewees, or a sample of a population.
- Build people from goals, capabilities, context, access needs, constraints,
  and behavior. A grandmother is a person with a biography and specific skills,
  not shorthand for “bad at technology.” Do not infer beliefs or limitations
  from age, disability, culture, gender, or another protected trait.
- Separate `observed` evidence from `persona-inferred` reaction and
  `moderator-inferred` synthesis. A plausible fictional reaction is still an
  inference.
- Exercise the real artifact when it exists. A concept-only review may test
  comprehension and desirability hypotheses; it cannot claim task success.
- Preserve disagreement. Participants may value incompatible things, miss a
  problem, or reject the premise. Do not manufacture consensus to make the
  report tidy.
- A transcript contains the complete user-facing moderator and participant
  dialogue, task actions, observations, and follow-ups within the procedure's
  moderation budget. It never contains or requests private chain-of-thought.
- Every finding ends with exactly one disposition. No recommendation is allowed
  to float into a decorative “next steps” list.

## Procedure

### 1. Frame the session

Name the subject, decision to inform, target users, available artifact, and
questions the session can and cannot answer. Inspect the project authority and
work conventions before choosing output paths. Load the active configuration;
if it is absent, `standards init` creates the exact proposed configuration and
empty project-owned profile/procedure directories defined by the config
contract. It does not invent a universal persona baseline. Keep it proposed
until the project-specific library is complete, validated, and accepted.

### 2. Select the panel

Choose four to seven profiles whose differences are causal for this subject.
Cover the direct user, a newcomer, a relevant access or environmental
constraint, a builder or operator when they bear product cost, and a skeptical
or trust-sensitive participant when the product asks for adoption or data.
Include an agent only when an agent actually uses, operates, integrates, or is
affected by the subject.

Prefer an existing profile. Create one when the required perspective is missing,
then validate it. Snapshot each selected profile id and revision into the run so
later profile edits cannot rewrite history.

Treat `panel.profilePool` as eligible lenses, not a default panel. Record the
causal reason for every selected seat in the research brief and snapshot only
that selected panel in `SESSION.json`.

### 3. Choose or codify the procedure

Select the narrowest procedure that answers the research question. Use concept
panels for propositions, task walkthroughs for interaction, access-and-
constraints reviews for inclusive failure modes, and shipping reviews for a
combined gate. Create a procedure when the decision requires a genuinely new
sequence, evidence rule, or output—not merely different moderator wording.
Honor its task and follow-up budget. If the evidence gap warrants an extension,
record the extension under the procedure's explicit rule before continuing.

### 4. Moderate against evidence

Follow the configured phases. Record the moderator prompt, each participant's
response, task action, visible product response, follow-up, cross-talk, and
phase close. Stop when required records are saturated under the procedure's
`moderationBudget`; a full transcript preserves the bounded session rather than
rewarding repetition. Let profiles notice different evidence; do not give every
participant every finding. Mark unexercised or unavailable surfaces plainly.

### 5. Synthesize findings

Create stable finding ids. Each finding records the evidence, affected
participants, evidence class, severity, confidence, product owner, and smallest
useful response. Distinguish a repeated panel theme from several profiles
repeating the same assumption supplied by the moderator.

### 6. Produce and route outcomes

Give every finding exactly one disposition:

- `work-item`
- `design-concept`
- `feature-request`
- `decision-record`
- `research-question`
- `no-action`
- `needs-routing`

Resolve the destination from the user request, active focus-group config,
project authority files, and canonical work system—in that order. Never invent
`TODO.md`, a proposal folder, or a second backlog when the project already owns
that artifact elsewhere. Use a stable fingerprint to detect an existing item.

Keep inferred hypotheses as drafts unless the outcome contract permits their
materialization. Inferred work items, feature requests, and decision records
need an explicit adoption record at materialization; unknown evidence stays a
research question, routing problem, or justified no-action.

Materialize reversible, project-local artifacts when the selected `review` mode
and project policy authorize them. Preview remote or external tasks and ask at
the write boundary unless that write was already authorized. Record the final
route state even when the result is `no-action` or `needs-routing`.

### 7. Verify the run

The configured session bundle contains:

1. `SESSION.json` — subject, question, artifact, config, profile revisions,
   procedure revision, evidence limits, and run timestamps;
2. `PARTICIPANTS.md` — readable snapshots of the selected profiles;
3. `TRANSCRIPT.md` — the complete labeled synthetic dialogue and task record;
4. `FINDINGS.md` — evidence-backed synthesis and disagreements;
5. `OUTCOMES.json` — machine-readable dispositions and routing receipts.

Run `python3 /absolute/path/to/focus-group/scripts/validate.py config
.focus-group` before a session and `python3
/absolute/path/to/focus-group/scripts/validate.py outcomes
.focus-group/runs/YYYY-MM-DD-subject/OUTCOMES.json` after synthesis. Then run
`python3 /absolute/path/to/focus-group/scripts/validate.py run
.focus-group/runs/YYYY-MM-DD-subject` before claiming session completion.
Confirm that every materialized item exists in its canonical owner and that the
ledger contains no duplicate fingerprint or orphan finding.

## Output

Lead with the decision the session informs. Then report:

- panel and procedure used;
- strongest observed finding and strongest persona-based hypothesis;
- disagreements that change the product decision;
- outcome counts by disposition and route state;
- created artifacts or tasks with their canonical paths/ids;
- limits requiring real users or additional evidence.

Do not report a synthetic session as product validation. Its honest claim is
that a consistent set of perspectives exercised the available evidence and
produced traceable hypotheses and project-owned outcomes.
