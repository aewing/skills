---
name: truth-loop
description: Use when the user asks for thorny reasoning, root-cause analysis, architecture judgment, adversarial synthesis, or a recurrent loop that must converge on truth rather than plausibility.
---

# Truth Loop

A recurrent reasoning loop for tasks where the failure mode is *"looked defensible, but reasoned around the hard part."* Sibling to `execution-rigor` (which handles thorny execution); this one handles thorny *reasoning*.

The thing that breaks long-running reasoning work is not lack of intelligence. It is narrative gravity: the first plausible explanation starts organizing the evidence, contradictions get softened, and the answer becomes a polished story instead of a true model. This skill exists to make that drift visible and forbidden.

The user invoking this is signaling: **do not settle for plausible. Separate fact from inference, keep alternatives alive, and let evidence change the shape of the answer.**

## When to use this

- The user explicitly invokes it ("fully understand it", "think deeply", "reconsider every decision")
- Root cause is uncertain or prior attempts contradicted each other
- The task crosses architecture, runtime ownership, project rules, product intent, or system boundaries
- A decision needs evidence, tradeoffs, and falsifiers before implementation
- "Looks right" and "is right" are likely to diverge

## When NOT to use this

- Small mechanical edits, typo fixes, or direct commands
- Execution-heavy work with a clear definition of done - use `execution-rigor`
- Cases where the user explicitly wants a fast answer over a careful one
- Situations where the correct next step is already known and only needs implementation

## Reasoning State

Maintain a single state object across phases. Update it as the model changes. Reference *the state*, not "what I said earlier." If the harness provides no built-in state surface, keep the object in a local scratch file and update it as the model changes.

```json
{
  "task": "<one sentence - what question are we actually trying to answer?>",
  "central_question": "<the decision or explanation the loop must converge on>",
  "decision_criteria": [
    "<observable or principled criterion 1>",
    "<observable or principled criterion 2>"
  ],
  "known_facts": [
    { "claim": "X is true", "evidence": "file:line, command output, doc, runtime observation", "confidence": "high|medium|low" }
  ],
  "unknowns": [
    { "question": "...", "why_it_matters": "...", "how_to_resolve": "..." }
  ],
  "assumptions": [
    { "claim": "...", "basis": "...", "how_to_disprove": "...", "status": "untested|supported|weakened|false" }
  ],
  "competing_hypotheses": [
    { "id": "H1", "claim": "...", "predicts": ["..."], "would_be_disconfirmed_by": ["..."], "status": "live|favored|rejected" }
  ],
  "lateral_check": "<one sentence - are we solving the wrong problem?>",
  "reasoning_log": [
    { "iteration": 1, "move": "mapped evidence|tested assumption|rejected hypothesis|changed model", "why": "..." }
  ],
  "contradictions": [
    { "fact_a": "...", "fact_b": "...", "resolution": "unresolved|resolved: ..." }
  ],
  "adversary_flags": [
    { "type": "unfalsified_assumption|story_fitting|missing_hypothesis|weak_evidence|...", "resolution": "fixed|accepted_with_reason|reopened_loop" }
  ],
  "conclusion": "<current answer, or null if not converged>",
  "falsifier": "<one observable that would change the conclusion>",
  "convergence": "<diverging|mapping|contested|narrowing|nearly_done|sealed>"
}
```

## Phases

### 1. FRAME - name the real question

Before reasoning starts, write the central question in a form that can be answered.

Bad: "Figure out the auth issue." "Review the architecture." "Is this good?"

Good: "Why does the payments service report the provider unconfigured even though the deployment manifest declares the credentials, and which runtime binding path is actually broken?" "Should this behavior live in the app route, a feature package, or a runtime-surface package under the project's architecture rules?"

Define decision criteria up front. If the user gave a vague task and the wrong frame would waste work, propose the frame and ask for confirmation. If the likely frame is obvious, proceed and state it.

### 2. MAP - facts before interpretation

Gather the territory:

- Project rules, AGENTS/CLAUDE/constitution documents, and owner boundaries
- Public surface, runtime path, package exports, and app integration points
- Primary evidence from files, commands, logs, tests, screenshots, or docs
- Existing sibling patterns that solved a similar problem
- One lateral candidate that may mean the current question is wrong-shaped

Record facts as facts and interpretations as interpretations. A file comment, old doc, or prior memory note is evidence of intent, not proof of current runtime behavior.

### 3. HYPOTHESES - keep alternatives alive

Generate at least two live hypotheses unless the evidence already makes one impossible. Each hypothesis needs:

- What it claims
- What it predicts you should observe
- What would disconfirm it
- What evidence currently supports or weakens it

If you only have one hypothesis, keep mapping. A single-hypothesis loop is usually confirmation bias with better formatting.

### 4. INTERROGATE - seek the evidence that can hurt

Test assumptions against primary evidence. Prefer checks that can change your mind:

- Run the command whose failure defines the problem
- Read the owning implementation rather than only the consumer
- Compare docs against current code
- Trace runtime registration/resolution instead of assuming import intent
- Inspect logs or real UI/TUI artifacts when user-facing behavior is at issue

Every "probably", "obviously", "just", or "should" is a tripwire unless it is backed by a fact in `known_facts`.

### 5. SYNTHESIZE - choose the model that explains more

When the evidence narrows, synthesize:

- State the favored hypothesis
- Explain why it beats the alternatives
- Account for contradictory evidence instead of ignoring it
- Name the remaining assumptions
- Name the falsifier

Do not change the decision criteria to fit the answer. If the answer does not satisfy the original frame, re-frame explicitly and explain why.

### 6. STUCK-CHECK - re-map after repeated failure

If two iterations do not add new evidence or only restate the same model, stop and re-map:

- What assumption has gone untested?
- What evidence would actually decide this?
- What lateral framing might make the contradiction disappear?
- Are we reasoning from docs when runtime evidence is needed?
- Are we trying to justify an implementation that should be replaced?

Write a one-paragraph diagnosis before continuing. No diagnosis means you are not stuck productively; you are looping.

### 7. ADVERSARY - pre-conclusion audit

Before declaring a conclusion, run an adversarial pass. Use a subagent when available; otherwise perform the pass yourself explicitly.

Brief:

> You are an adversarial reasoner. The primary loop claims this conclusion:
> [conclusion]
>
> The central question was:
> [central_question]
>
> The known facts are:
> [known_facts]
>
> The competing hypotheses were:
> [competing_hypotheses]
>
> Your only job: find where the primary may have produced a plausible story instead of a true model. Specifically look for:
> - Assumptions that were never tested
> - Missing competing hypotheses
> - Evidence that is adjacent to, but not actually about, the central question
> - Contradictions that were handwaved
> - Architecture or ownership rules bypassed by convenience
> - Conclusions stronger than the evidence permits
> - Anything that smells like reward-hacking on the appearance of insight
>
> Be specific. Cite evidence handles where possible. If you find nothing, say so plainly. Under 350 words.

Fold flags into `state.adversary_flags` and address material ones. If ADVERSARY changes the answer, reopen the loop.

### 8. OUROBOROS - cold completeness check

Do a fresh-perspective pass with only:

- The original question
- The proposed conclusion
- The strongest evidence
- The falsifier

Ask:

> If I came in cold, would this answer convince me? What would I still ask before acting on it?

If the objection is material, add it to unknowns and run another MAP/HYPOTHESES/INTERROGATE cycle.

### 9. EMIT - conclusion, evidence, falsifier

Final response must include:

1. **Answer** - direct conclusion, not a tour of the reasoning.
2. **Why** - the decisive evidence and why alternatives lost.
3. **Falsifier** - one observable that would change the conclusion.
4. **Uncertainty** - what remains unknown or lower-confidence.
5. **Next action** - the smallest action implied by the conclusion.

Do not hide uncertainty to sound useful. A bounded "I do not know yet" is better than an unearned answer.

## Reasoning Tripwires

These are not automatically forbidden, but they must trigger scrutiny:

- "Probably", "obviously", "just", "should", "clearly" without evidence
- The first plausible explanation becomes the only explanation
- Docs or comments are treated as current behavior without runtime proof
- A consumer-local fix is accepted before owner/runtime boundaries are traced
- A contradiction is described as "edge case" instead of resolved
- The answer changes but the frame and decision criteria are not updated
- Absence of evidence is treated as evidence of absence
- The loop starts implementing before root cause is understood
- The final answer has no falsifier

## Extras that pay off

- **Contradiction ledger.** Any fact that does not fit the favored model gets written down. The model is not allowed to win by forgetting hard evidence.
- **Alternative tax.** Every conclusion must name the strongest rejected hypothesis and why it lost.
- **Falsifier discipline.** If no observation could change the answer, it is not reasoning; it is a stance.
- **Lateral honesty.** If the best answer is "we asked the wrong question", say that early.
- **Evidence gradient.** Prefer runtime observation over source intent, source intent over docs, docs over memory, memory over vibes.
- **Convergence tagging.** Each iteration declares `state.convergence`: `diverging`, `mapping`, `contested`, `narrowing`, `nearly_done`, or `sealed`.
- **Anti-narrative bias.** When the answer starts sounding elegant, spend one more pass looking for the ugly fact that breaks it.

## Rules of engagement

- **The user can interrupt.** They can de-scope, redirect, or ask for a fast answer; name the tradeoff.
- **No silent confidence inflation.** Confidence must track evidence quality.
- **Memory respect.** Prior feedback and recorded memory are evidence, but drift-prone claims still need verification when cheap.
- **Runtime-first.** Prefer reasoning that eventually touches the real runtime path over source-only inference.
- **Honest convergence.** `sealed` means the conclusion answers the central question, accounts for alternatives, names uncertainty, and has a falsifier.
