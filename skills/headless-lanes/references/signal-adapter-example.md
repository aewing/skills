# Example signal adapter (vibes-style session messaging)

One small script every lane calls from its shell. Identity comes from the
environment, so the same brief works in any harness. Adapt the two `run`
calls to your substrate's send/list/mark-read commands.

```sh
#!/bin/sh
# lane-signal <to> <message>   send one signal
# lane-signal --inbox          print my unread messages, marking exactly those read
# Env: LANE_ID (sender), LANE_SESSION (substrate session id), LANE_ROOT (workspace root)
set -e
: "${LANE_ID:?}" "${LANE_SESSION:?}"
run() { vibes --workspace-root "$LANE_ROOT" tools run "$@" -s "$LANE_SESSION" -p "$LANE_ID" -f json 2>/dev/null; }
if [ "$1" = "--inbox" ]; then
  ids=$(mktemp)
  run session-collaborate -i '{"action":"list","unreadOnly":true}' | python3 -c '
import json,sys
t=sys.stdin.read(); ms=json.loads(t[t.index("{"):]).get("messages",[])
for m in ms: print("%s | %s" % (m.get("fromParticipantSlug"), m.get("content")))
open(sys.argv[1],"w").write("\n".join(m["id"] for m in ms))' "$ids"
  # Mark only what was printed: a blanket mark-read swallows messages that
  # arrive between the list and the mark.
  while read -r id; do [ -n "$id" ] && run session-collaborate -i "{\"action\":\"mark-read\",\"messageId\":\"$id\"}" >/dev/null; done < "$ids"
  rm -f "$ids"; exit 0
fi
to=$1; shift
run session-collaborate -i "$(python3 -c 'import json,sys;print(json.dumps({"action":"send","toParticipant":sys.argv[1],"content":sys.argv[2],"messageType":"info"}))' "$to" "$*")" >/dev/null && echo sent
```

Lessons from running it:
- Register the overseer's identity on the session before launch; recipients
  must exist.
- Never broadcast (`all` reaches every participant in the session).
- Pin the workspace root: a CLI started from another project's directory may
  load a different composition and fail.
- CLI calls can take 10–30 s; give lanes a 60 s tool timeout for it.
