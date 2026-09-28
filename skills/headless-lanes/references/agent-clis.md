# Agent CLI headless recipes

Verified 2026-09-27 against the versions shown. CLIs change fast: re-run the
preflight proof before trusting any line here, and record corrections in the
user roster. Always close stdin (`</dev/null`) and wrap runs in your own
wall-clock backstop (`timeout`), since not every CLI has one.

**Exit codes lie.** Several CLIs exit 0 on provider errors, timeouts or
auto-denied tools. Judge a run by its payload: a final assistant message, no
error event, and the lane's own proof.

| CLI | Headless command | Auto-approve | Output | Resume | MCP |
|---|---|---|---|---|---|
| Claude Code (`claude`) *(`-p`, json, `--model`, `--settings` proven)* | `claude -p "<msg>" --model <id> --output-format json` | `--permission-mode acceptEdits` / `--dangerously-skip-permissions` in a sandbox; or `--allowedTools` | `json` (one object: `result`, `is_error`, `modelUsage`), `stream-json` | `--resume <id>`, `-c` | `claude mcp list/add`, `--mcp-config` |
| Codex (`codex`) *(unverified here)* | `codex exec "<msg>" -m <model> --json` | `--full-auto`, `--sandbox workspace-write` | `--json` NDJSON | `codex exec resume <id>` | `codex mcp` / `config.toml` |
| agy (Antigravity CLI) 1.2 | `agy -p "<msg>" --model <id> --output-format json --dangerously-skip-permissions --print-timeout 0 </dev/null` | `--dangerously-skip-permissions` (without it tools are auto-denied, exit 0, empty response) | `json` `{conversation_id,status,response,usage}`; `stream-json` | `--conversation <id>`, `-c` | `agy mcp list/add/enable` — but 1.2.12 print mode exposes no MCP tools to the model |
| Gemini CLI (`gemini`) *(unverified here)* | `gemini -p "<msg>" -m <id> --output-format json --yolo` | `--yolo` / `--approval-mode` | `json`, `stream-json` | `--resume` | `gemini mcp` / `settings.json` |
| opencode 2.0 | `opencode run "<msg>" -m <provider/model#variant> --format json --auto </dev/null` | `--auto` | NDJSON events (`tool_use`, `text`, `step_finish`, `error`) | `-s <session>`, `-c`, `--fork` | `opencode mcp list/add`; keys live in the `credential` table of `~/.local/share/opencode/opencode.db` (2.x; `account.json`/`auth.json` are not what it sends) |
| pi 0.87 | `pi -p "<msg>" --provider <p> --model <id> --mode json --session-id <uuid> </dev/null` | none needed (no permission gate); restrict with `--tools` | NDJSON (`message_end`, `tool_execution_*`, `agent_end`); json mode exits 0 on provider error (`stopReason:"error"`) | `--session-id <uuid>` (create or reuse), `-c`, `--fork` | no MCP; extensions (`-e`) and skills (`--skill`) instead |
| grok 1.0 *(from its headless docs; not called)* | `grok -p "<msg>" -m <id> --output-format json --always-approve --cwd <dir> </dev/null` | `--always-approve` | `json`, `streaming-json` | `-r <id>`, `-c` | `grok mcp list/add/doctor` |

## Readiness checks (no model call)

- `pi auth check --provider <p> --json` → exit 0 when ready.
- `opencode models <provider>` lists models; auth is only proven by a call.
- `agy models`, `grok models`, `claude` has `/status` only interactively.
- Cloud accounts: `npx wrangler whoami` (Cloudflare), `aws sts
  get-caller-identity` (AWS; Bedrock API keys can't call STS — probe
  `GET https://bedrock.<region>.amazonaws.com/foundation-models` with the
  bearer token instead).

## Provider notes

- **Amazon Bedrock.** A listed model isn't necessarily callable: check
  `GET /foundation-model-availability/<modelId>`. `agreementAvailability:
  NOT_AVAILABLE` means the model's Marketplace offer isn't accepted
  (`list-foundation-model-agreement-offers` → `create-foundation-model-
  agreement`, needs an IAM identity with that permission — Bedrock API-key
  users usually lack it). Harnesses: pi `--provider amazon-bedrock` with
  `AWS_BEARER_TOKEN_BEDROCK` (proven with tool calls); Claude Code with
  `CLAUDE_CODE_USE_BEDROCK=1` — if user settings pin env vars (e.g.
  `CLAUDE_CODE_USE_BEDROCK=0`, an expired `AWS_PROFILE`), override per run
  with `--settings '{"env":{"CLAUDE_CODE_USE_BEDROCK":"1","AWS_PROFILE":""}}'`.
  An ambient expired `AWS_PROFILE` can shadow a valid bearer token; unset it
  for the lane.
- **Finding the key a CLI really sends.** Point the provider's base URL at a
  local logging proxy and hash the `Authorization` header; compare with the
  hashes of candidate keys (config files, the CLI's database, `launchctl
  getenv`). Never print the keys themselves.
- **Cloudflare Workers AI** (not AI Gateway): pi or opencode provider
  `cloudflare-workers-ai`; billed per neuron on the account.
- **Subscriptions vs keys.** Prefer OAuth/subscription providers (ChatGPT via
  `openai-codex`, Google via agy/gemini, coding plans) and sponsored credit
  accounts; metered keys only with the user's say-so. OAuth tokens expire:
  a 401 means the user must log in again interactively.
