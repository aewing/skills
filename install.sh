#!/usr/bin/env bash
#
# aewing/skills — installer
# Copies the curated skills in ./skills into an agent skills directory.
#
# Default target: ~/.claude/skills  (Claude Code loads user skills from here)
# Override with:  --target PATH
# Preview with:   --dry-run
# List skills:    --list

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="${REPO_DIR}/skills"
TARGET="${HOME}/.claude/skills"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [--target DIR] [--dry-run] [--list]

  --target DIR   Install skills into DIR (default: ~/.claude/skills)
  --dry-run      Print what would be copied, copy nothing
  --list         List the skills in this repository and exit
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      [[ $# -ge 2 ]] || { echo "error: --target requires a directory" >&2; exit 2; }
      TARGET="$2"; shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    --list)
      echo "Skills in this repository:"
      for d in "${SKILLS_SRC}"/*/; do
        [ -d "$d" ] && [[ "$(basename "$d")" != "references" ]] && echo "  - $(basename "$d")"
      done
      exit 0
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -d "$SKILLS_SRC" ]] || { echo "error: no ./skills directory next to the installer" >&2; exit 1; }
[[ "$TARGET" != "/" && "$TARGET" != "$HOME" ]] || { echo "error: refusing to install into $TARGET" >&2; exit 1; }
[[ "$TARGET" != "$REPO_DIR" ]] || { echo "error: target cannot be this repository" >&2; exit 1; }

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Would install to: $TARGET"
  for d in "$SKILLS_SRC"/*/; do
    [ -d "$d" ] || continue
    echo "  cp -R \"$d\" \"$TARGET/$(basename "$d")\""
  done
  exit 0
fi

mkdir -p "$TARGET"
installed=()
for d in "$SKILLS_SRC"/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  rm -rf "$TARGET/$name"
  cp -R "$d" "$TARGET/$name"
  installed+=("$name")
done

echo "Installed ${#installed[@]} skills into $TARGET:"
printf '  - %s\n' "${installed[@]}"
echo
echo "Claude Code tip: skills in ~/.claude/skills load on the next session."
echo "If you use Claude Code plugins, the marketplace route is usually better:"
echo "  /plugin marketplace add aewing/skills"
echo "  /plugin install rigor-skills@aewing-skills"
