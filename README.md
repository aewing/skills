# Skills

A curated set of agent skills I actually use, published in the portable
[Agent Skills](https://agentskills.io) format (a folder per skill with a
`SKILL.md`). They are written to be workspace-agnostic: no project law, product
names, or private tooling baked in.

The theme is **rigor with calm**: make "looks done" stop passing for "done",
make "looks plausible" stop passing for "true", and keep the language between
humans and agents clear enough that neither side pressures the other.

## Install

### Claude Code (easiest)

Register this repository as a plugin marketplace, then install:

```
/plugin marketplace add aewing/skills
/plugin install rigor-skills@aewing-skills
```

or from the shell:

```
claude plugin marketplace add aewing/skills
claude plugin install rigor-skills@aewing-skills
```

### Any agent (copy installer)

```
git clone https://github.com/aewing/skills.git && cd skills && ./install.sh
```

Installs to `~/.claude/skills` by default; point it anywhere for other
harnesses:

```
./install.sh --target ~/.config/your-agent/skills
./install.sh --list
./install.sh --dry-run
```

## The skills

| Skill | What it is for |
| --- | --- |
| [execution-rigor](skills/execution-rigor/SKILL.md) | Long-horizon execution that finishes for real: observable definition-of-done, per-task verification, shortcut tripwire scans, and an adversarial pre-completion audit. Use when the failure mode is "called done but actually half-finished." |
| [truth-loop](skills/truth-loop/SKILL.md) | Reasoning that converges on truth rather than plausibility: hypotheses kept alive, evidence that can hurt, contradiction ledgers, and a falsifier on every conclusion. Use when the failure mode is "looked defensible, but reasoned around the hard part." |
| [goodtalk](skills/goodtalk/SKILL.md) | Audit and recode instruction language so humans and agents stop accidentally pressuring each other ("don't fuck with the model"). Research / standards / suggest / execute / recode / install / sync / publish modes with a portable standards contract. |

The pair works together: `execution-rigor` guards the doing, `truth-loop`
guards the thinking. `goodtalk` keeps the instructions they run under honest
and calm.

## Updating

Marketplace users:

```
/plugin marketplace update aewing-skills
```

Copy-install users: `git pull` in the checkout, then run `./install.sh` again.

## License

MIT — the skills are instruction and process text; take them, adapt them, and
publish what you learn. See [LICENSE](LICENSE).
