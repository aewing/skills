---
name: verification-hygiene
description: Verify code, package, test, deletion, and delivery claims against the real artifact. Use after changes or before saying work is done. Select the narrowest proof that can falsify the claim, then cover every layer the requested outcome depends on.
---

# Verification hygiene

Use the owning repository's check, test, build, dependency, and boundary gates;
do not copy command catalogs into this skill.

## When NOT to use this

- Design or exploration with no claim on the line yet — there is nothing to
  falsify.
- When a narrower, already-passing owner gate directly covers the claim; this
  skill is for choosing and proving the narrowest check, not ritual re-running.

## Procedure

1. Write the exact claim being verified.
2. Choose the narrowest command or observation that can prove it false.
3. Run it in the owning repository and record the exit code and useful output.
4. Exercise the shipping surface when the claim reaches CLI, TUI, browser,
   worker, storage, auth, secrets, or deployment behavior.
5. Run broader owner gates required by the changed dependency or boundary.
6. Inspect the diff for hidden bypasses, then report only the tier proved.

## Required consequences

- Source change: run the owning package check and focused behavioral tests.
- Dependency change: run that repository's dependency and cycle gates.
- Boundary or export change: run its boundary or architecture gate and build or
  pack the public artifact.
- Delete or rename: grep every consumer before removal.
- CLI/TUI/web change: invoke the real entrypoint; types alone are insufficient.
- Storage or cloud API change: exercise the owner and at least one borrower path.
- Workspace or tooling change: run the workspace's canonical check before handoff.

## Reject false green

Reopen the work if the change introduces a skipped test, type suppression,
silent catch, fixture that mocks the subject, hard-coded passing result, or a
comment that defers the requested implementation. Do not delete a failing test;
repair the product or rewrite the test against the current contract.

A unit test proves only its execution path. A 200 proves only the request it
made. A deploy proves only provider acceptance. Match the evidence to the claim.

## Report

Keep the evidence copyable and short:

```text
Claim: <what is now true>
Proof: <command or observation> — exit <n>
Artifact: <real surface exercised>
Unknown: <remaining unproved part, or none>
```
