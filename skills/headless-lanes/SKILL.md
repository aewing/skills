---
name: headless-lanes
description: Run a mission through headless worker agents (other agent CLIs, other providers) in parallel lanes from one overseer session that plans, assigns, reviews and lands — never executes lane work itself. Use when the user wants work fanned out to several agent CLIs/models, wants an orchestrator/overseer role, or says "lanes", "headless agents", "let them cook". Discovers the machine's agents, models and coordination substrate (MCP messaging/inbox/presence servers or similar), routes lanes by researched scorecards and the user's quality/speed/cost order, and writes a config that teaches the substrate.
---

# Headless Lanes

One overseer, many headless workers, one plan. The overseer scopes the whole
mission before anyone moves, puts each worker in its own room at the right
time, speaks in fixed signals, and accepts nothing it has not verified.
Workers are capable models: brief them like senior engineers and let them
cook inside their room.

**Doctrine.** Measure until certain, execute once, claim once when true.
No rehearsals, no arbitrary checkpoints, no step-by-step narration to the
user. Every lane has an owner, a room, a done-when test and a stop rule.
Silence means working; noise is a defect.

## Roles

- **Overseer (you).** Recon, plan, assign, brief, launch, monitor, review,
  land, debrief. You do not do lane work; if a lane fails twice, re-scope or
  reassign it, don't absorb it.
- **Worker.** One headless agent process running one lane brief. Owns only
  its room. Signals on the substrate. Proves its own work before claiming.
- **User.** Sets the mission, approves providers and the priority order
  (quality / speed / cost), and is told once when the mission is done.

## Phase 0 — Recon (before any plan)

Do all of this; record results in the roster (see Config).

1. **Substrate.** Find the coordination layer the agents can share:
   - MCP servers in each agent's config and the project (`.mcp.json`,
     agent config dirs) that offer messaging/inbox, presence, rooms/chat,
     claims/locks, tasks, or process management. A workspace CLI with the
     same features counts.
   - Read its docs/help: how an agent binds (command, identity), sends,
     reads and waits on an inbox, claims a path, and how the overseer sees
     all traffic.
   - If none exists, fall back to the file substrate (below). Say so.
2. **Agents.** Every agent CLI on PATH (e.g. `claude`, `codex`, `gemini`,
   `agy`, `opencode`, `pi`, `grok`, `aider`, `goose`, `amp`, `cursor-agent`,
   `qwen`, `crush`). For each: version, headless flags, auth state, models.
   Recipes: [references/agent-clis.md](references/agent-clis.md).
3. **Accounts.** Which providers are authenticated, and how (subscription
   OAuth, sponsored credits, pay-per-token key). Default to subscriptions and
   credits the user wants spent; metered keys only if the user says so.
   Prove each model is *callable* with a tiny invoke — catalogs list models
   an account can't use (unaccepted agreements, zero quotas, dead OAuth).
   Note usage limits and how to read them.
4. **Models.** Latest version of each family only; drop superseded ones.
5. **Scorecards.** Research current public results (SWE-bench Verified/Pro,
   Terminal-Bench, LiveCodeBench, tool-use, long-context, output speed and
   latency, price). Date-stamp every number and cite it; mark unverified.
   Turn them into "who's good at what" for the lane kinds in this mission.
6. **Ask the user once**, with everything above in front of them:
   which providers to rotate in, and the order of quality / speed / cost.
   Then stop asking; route by that order.

## Phase 1 — Preflight gates (per agent, before its first lane)

No gate, no lane.

- **Headless proof.** A tiny live call in a scratch dir with the exact
  command the lane will use (model, auto-approve, output format, cwd,
  `</dev/null`). Exit code and output recorded.
- **Substrate bind.** The agent, headless, from the lane's cwd, binds to
  the mission session under its lane identity, sends a signal to the
  overseer and reads its inbox; the overseer sees the message arrive. A
  config entry that lists as "connected" proves nothing: servers can die at
  startup from a different cwd, need an explicit session bind, or not be
  surfaced to the model in headless mode. Fix the bind, re-run the proof.
- **One signal path for every harness.** Wrap the substrate's send/read in
  a tiny helper script lanes call from their shell (every harness has one),
  with identity from the environment (`LANE_ID`, session id, workspace
  root). Harness-specific MCP binds are a bonus, not the contract.
- **Room scope.** It can write where its lane will work (sandbox, add-dir,
  permissions) and nowhere it shouldn't.
- **Limits.** Current usage/limit state known; a limited provider sits out
  and rotates back in when it clears.

## Phase 2 — The plan (one document)

Write `PLAN.md` in the lanes dir before launch. It contains:

- **Mission** in one sentence, and **done** as observable predicates.
- **Rooms**: disjoint sets of paths (and shared resources: ports, GPUs,
  databases, the git index). Every writable path belongs to one room.
  Shared files get a single owner or a sequence, never two writers.
- **Lanes**: `id, agent, model, room, depends_on, done_when, stop_rule`.
  Up to the concurrency cap (default 10) at once; the rest queue.
- **Sequence**: who enters which room when. Dependencies are explicit
  (lane B starts on A's DONE), not timed.
- **Assignment**: each lane's model chosen from the scorecards by the user's
  order, with a one-line reason. Hard reasoning / cross-cutting design /
  risky edits → strongest model. Bulk mechanical edits, triage, docs →
  fastest model that clears the bar. Review lanes use a different model
  family than the lane they review.
- **Integration**: how lanes land (commit rules, who merges, order), and
  the final verification the overseer runs across all lanes.

## Phase 3 — Lane briefs

One file per lane, `lanes/<id>.md`, from
[references/lane-brief.md](references/lane-brief.md). A brief is the
worker's whole world: identity, mission context, its room, forbidden paths,
done-when commands, signals, inbox cadence, commit rules, stop rules, report
format. Write it so a strong engineer with no other context succeeds. Trust
the worker with method; be exact about scope and proof.

## Phase 4 — Launch

- One detached process per lane (`nohup`, a process manager, or the
  substrate's own runner), stdout/stderr to `lanes/<id>.log`, pid recorded.
  stdin closed. Prevent sleep for long runs.
- Judge a finished process by its payload, not its exit code: several CLIs
  exit 0 on provider errors, timeouts and auto-denied tools.
- Pass identity in the environment and brief (lane id, overseer address).
- Start only lanes whose dependencies are DONE and whose rooms are free.

## Signals

Short, fixed, on the substrate (subject line or first token):

| From | Signal | Meaning |
|---|---|---|
| worker | `CLAIMED <lane>` | started, room held |
| worker | `BLOCKED <lane>: <what>` | cannot proceed; says exactly what it needs |
| worker | `DONE <lane>: <proof>` | done-when met; commands and results attached |
| worker | `RELEASED <lane>` | room free (after DONE or ABORT) |
| overseer | `GO <lane>` | start / continue |
| overseer | `REVISE <lane>: <gap>` | proof insufficient; what to fix |
| overseer | `HOLD <lane>` / `ABORT <lane>` | pause / stop and release |
| overseer | `ACCEPT <lane>` | verified and landed |

No progress chatter. A worker messages only to claim, block, finish or
release, and only to the overseer (never broadcast); it checks its inbox at
start, before each commit, and before claiming DONE. The overseer registers
its own identity on the session before launch so lanes can address it, and
gives every lane a distinct identity (substrate launchers often reuse one
per harness).

## Phase 5 — Monitor

- Watch the substrate inbox and each lane's log/process — not the systems
  under test (don't perturb what's being measured).
- **Dead air, not deadlines.** A lane is stuck when its log, files and
  messages stop advancing for the dead-air window, or it loops on no-op
  steps. A long single generation is not dead air. Wall-clock limits are a
  generous backstop only.
- On BLOCKED: answer, re-scope, or reassign — fast.
- On usage limits: rotate the lane to the next provider in the user's order
  with the same brief and its progress notes.

## Mid-flight

- **A lane that stops early** (context or turn limit, before its report):
  resume the *same* session with one directive ("write the report now, then
  DONE"); relaunching loses the work.
- **BLOCKED at a room edge is correct behavior.** If the need is real,
  expand the room explicitly (name the files and the purpose), log it, and
  resume the same session.
- **Added scope goes by inbox** (`GO <lane>: ...`) to a running lane: lanes
  read their inbox before DONE, so the message lands in time.
- **One writer per file at a time.** Sequence lanes that share a file
  (review → fix → follow-up), even when each is small.
- Answer a lane's disclosure (e.g. an accidental read of a live service)
  with an explicit acknowledgement, so it can finish.

## Phase 6 — Review and land

- Run the lane's done-when commands yourself. Read the diff against the
  room: anything outside it is a REVISE.
- Hunt for fake-done: skipped tests, stubs, silent catches, weakened
  assertions, claims without output.
- Rebuild and rerun the lane's tests yourself in a clean copy (the
  committed tree plus the lane's files), and spot-check its key claims in
  the code: a lane's own summary is a claim, not proof.
- ACCEPT only verified work; land it per the plan (explicit paths, never
  sweep in other lanes' or other people's files). Land each lane as soon as
  it's accepted: small commits keep later lanes building on verified code.
- When all lanes are accepted, run the mission's done predicates end to
  end. Then report to the user once: what landed, proof, what's open.

## Phase 7 — Debrief

Update the roster with what the mission taught: per agent/model, lanes run,
accepted first time vs revised, dead-air stops, limits hit, speed. These
observed scorecards outrank public ones next time.

## Config (what this skill writes)

- **User** (`~/.config/headless-lanes/roster.md`): agents, headless
  commands, auth kind, models, limits, scorecards with dates, observed
  results, the user's provider list and priority order.
- **Project** (`<repo>/.lanes/SUBSTRATE.md`): how agents in this project
  bind the substrate, identify, message, read inboxes, claim rooms, and the
  project's commit/test rules. Linked from the project's agent instructions
  (AGENTS.md / CLAUDE.md) so every agent, headless or not, learns it.
- **Mission** (`<repo>/.lanes/<mission>/`): `PLAN.md`, `lanes/*.md`,
  logs, pids, `LEDGER.md` (signals and decisions, append-only).

Templates: [references/config-templates.md](references/config-templates.md).

## File substrate (fallback)

When no messaging layer exists: each lane gets
`.lanes/<mission>/inbox/<lane>/` (overseer writes, worker reads) and
`outbox/<lane>/` (worker writes); messages are files named
`<utc-timestamp>-<SIGNAL>.md`; claims are `claims/<room>.lock` holding the
lane id. Same signals, same cadence.

## Failure modes this prevents

- Two agents editing one file; a worker "helpfully" fixing another room.
- Lanes launched on an agent whose substrate bind silently fails.
- Artifacts left in the tree (scratch files, logs, stray branches):
  briefs name where scratch goes, and review checks `git status`.
- The overseer doing the work and losing the plan.
- "Done" without proof; progress reported instead of results.
