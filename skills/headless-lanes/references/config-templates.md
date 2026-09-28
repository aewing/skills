# Config templates

## User roster — `~/.config/headless-lanes/roster.md`

Written in recon, updated in debrief. Plain markdown so any agent can read it.

```markdown
# Headless lanes roster (updated <date>)

## Priority
<e.g. quality > speed > cost>. Providers to rotate in: <list, in order>.
Account rules: <e.g. subscriptions and sponsored credits only; no metered keys>.

## Agents
| id | CLI + version | headless command (proven <date>) | auth | substrate bind |
|---|---|---|---|---|

## Models (latest only)
| model | via (agent/provider) | strengths | public scores (source, date) | observed (lanes, first-pass accept %, dead-air stops) |
|---|---|---|---|---|

## Limits and gotchas
- <provider>: <limit, how to read it, what a limit error looks like>
- <cli>: <exit-code lies, auth quirks, config overrides>

## Routing (derived)
- hard design / risky edits → <model>
- bulk mechanical → <model>
- tests → <model>
- review (other family) → <model>
- long-context reading → <model>
- shell/ops → <model>
```

## Project substrate — `<repo>/.lanes/SUBSTRATE.md`

Linked from AGENTS.md / CLAUDE.md. Teaches any agent the project's
coordination layer in one page.

```markdown
# Coordination substrate: <name>

## Bind
- MCP: <server name, command with pinned root/identity, how to verify>
- CLI fallback: <exact command prefix that works from any cwd>
- Identity: <how a lane names itself; how participants register>

## Messages
- Send to the overseer: <exact command>
- Read my inbox: <exact command>
- Never broadcast; address the overseer (or a named lane) only.

## Claims
- Claim a room: <lock command, lease, renew>  (or: "rooms are assigned in PLAN.md")

## Project rules
- Build/test: <commands>
- Commits: <branch, explicit paths, message style, who commits>
- Never touch: <paths, other people's uncommitted work, locks>
```

## Mission dir — `<repo>/.lanes/<mission>/`

```
PLAN.md          mission, done predicates, rooms, lanes, sequence, assignment
lanes/<id>.md    lane briefs
logs/<id>.log    lane stdout/stderr (or the substrate's launch logs)
LEDGER.md        append-only: time, signal, lane, decision
```

Keep `.lanes/` out of commits unless the project wants plans versioned
(`.git/info/exclude` keeps it local without touching `.gitignore`).
