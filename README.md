# Skills

A curated set of agent skills I actually use, published in the portable
[Agent Skills](https://agentskills.io) format (a folder per skill with a
`SKILL.md`). They are written to be workspace-agnostic: no project law, product
names, or private tooling baked in.

The theme is **rigor with calm**: make "looks done" stop passing for "done",
make "looks plausible" stop passing for "true", keep long work moving, and keep
the language between humans and agents clear enough that neither side pressures
the other.

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

### Rigor core

| Skill | What it is for |
| --- | --- |
| [execution-rigor](skills/execution-rigor/SKILL.md) | Long-horizon execution that finishes for real: observable definition-of-done, per-task verification, shortcut tripwire scans, and an adversarial pre-completion audit. Use when the failure mode is "called done but actually half-finished." |
| [truth-loop](skills/truth-loop/SKILL.md) | Reasoning that converges on truth rather than plausibility: hypotheses kept alive, evidence that can hurt, contradiction ledgers, and a falsifier on every conclusion. Use when the failure mode is "looked defensible, but reasoned around the hard part." |
| [goodtalk](skills/goodtalk/SKILL.md) | Audit and recode instruction language so humans and agents stop accidentally pressuring each other ("don't fuck with the model"). Research / standards / suggest / execute / recode / install / sync / publish modes with a portable standards contract. |

The pair works together: `execution-rigor` guards the doing, `truth-loop`
guards the thinking. `goodtalk` keeps the instructions they run under honest
and calm.

### Moving and proving work

| Skill | What it is for |
| --- | --- |
| [keep-going](skills/keep-going/SKILL.md) | Maintain progress on multi-step, long-running work: explicit remaining state, one causal unit at a time, milestone reviews, honest handoffs. |
| [coherence-engine](skills/coherence-engine/SKILL.md) | Focus and pruning for long-horizon tasks: flow perception, cut what does not serve the core intent, autonomy with a clear reversible/irreversible line. |
| [verification-hygiene](skills/verification-hygiene/SKILL.md) | Prove claims against the real artifact: the narrowest falsifying check, required consequences per change type, and rejection of false green. |
| [adversarial-reviewer](skills/adversarial-reviewer/SKILL.md) | Evidence-first review with one verdict (SHIP / BLOCKED / REWORK / MORE PROOF), highest blast radius first, smallest honest remediation. |
| [focus-group](skills/focus-group/SKILL.md) | Run clearly labeled synthetic user panels with causal participant selection, complete bounded transcripts, evidence-aware findings, and predictable project-owned outcomes. |

### Responses and craft

| Skill | What it is for |
| --- | --- |
| [wat](skills/wat/SKILL.md) | ADHD-friendly response overlay: answer first, one screen, evidence kept, one next action. For status, summaries, and handoffs. |
| [roast-review](skills/roast-review/SKILL.md) | Evidence-backed critique: funny, ruthless, specific reduction to the target's weaknesses and self-owns, plus a concrete escape plan (ROAST.md / PROPOSAL.md / EVIDENCE.md). |
| [tui-design](skills/tui-design/SKILL.md) | Terminal UI craft: layout paradigms, keyboard and focus models, semantic color, animation, and anti-pattern and compatibility checklists. Framework-agnostic. |

## Contributing back

Each skill is a plain folder; the source of truth is the `SKILL.md` plus any
`references/` it links. Improvements usually land as: a sharper description
(that is what triggers the skill), one more "when NOT to use this" line, or a
smaller replacement for a wordy rule.

The repo governs itself: the active language profile is
`.goodtalk/standards.json`, and goodtalk runs against this repo use it. To set
up the same for your project, copy the starter at
`skills/goodtalk/examples/standards.json.starter` or run `goodtalk standards
init`.

## Updating

Marketplace users:

```
/plugin marketplace update aewing-skills
```

Copy-install users: `git pull` in the checkout, then run `./install.sh` again.

## License

MIT — the skills are instruction and process text; take them, adapt them, and
publish what you learn. See [LICENSE](LICENSE).
