# Recode receipt

Goodtalk writes one JSON receipt per `recode` run under the configured receipt
directory. The receipt is evidence, not a new instruction source. Do not put
secrets or full untrusted payloads in it; hashes, bounded excerpts, and paths
are sufficient for audit.

The portable shape is:

```json
{
  "schema": "goodtalk/recode-receipt@1",
  "runId": "2026-08-13T00:00:00Z-example",
  "applied": true,
  "scope": "current-repository",
  "instructionSha256": null,
  "targets": ["**/*.md", "**/*.mdx", "natural-language-comments"],
  "compression": {
    "removedCategories": ["duplicate", "stale-process"],
    "parableDecisions": []
  },
  "byteDifference": {
    "measurement": "eligible-utf8-bytes",
    "target": null,
    "tolerance": null,
    "iterations": 1,
    "observed": 0.0,
    "stop": "signal-converged"
  },
  "changed": [
    {
      "path": "README.md",
      "inputSha256": "sha256:...",
      "outputSha256": "sha256:...",
      "regions": ["markdown-prose", "html-comment"],
      "transformations": [
        "unicode-nfc",
        "spacing-punctuation",
        "fact-order",
        "language-clarity"
      ]
    }
  ],
  "skipped": [
    {"path": "CONSTITUTION.md", "reason": "protected-owner"}
  ],
  "findings": [
    {
      "path": "README.md",
      "kind": "bidi-control",
      "region": "markdown-prose",
      "action": "removed-and-hashed"
    }
  ],
  "residualSignals": [],
  "unresolved": [],
  "verification": {
    "linksChecked": true,
    "structureChecked": true,
    "protectedRegionsUnchanged": true,
    "semanticGuardsPassed": true,
    "hiddenTextRescanned": true
  }
}
```

Implementations may add fields, but they must retain the schema identifier,
whether edits were applied, the effective scope, target interpretation,
changed-path hashes, compression and parable decisions, byte-difference
measurements, skipped/protected paths, findings, residual signals, unresolved
decisions, and verification results.

## Required receipt rules

- `instructionSha256` is `null` for bare `goodtalk recode`; when an
  instruction is supplied, store its digest rather than silently changing the
  effective target. A product may store the instruction text only when the
  user explicitly requests it and it contains no secret.
- Hash every changed file before and after the pass. A dry run records the
  input hash and the predicted or copied output hash according to the
  implementation contract; it never claims an applied edit.
- Record every protected or excluded path that a broad target discovered, so
  “all eligible” is falsifiable rather than an unreviewable wildcard.
- Measure byte difference only over eligible UTF-8 regions. Never add filler,
  padding, deterministic cadence, acrostics, zero-width characters, or another
  covert channel to reach a numeric target.
- Record removed categories and parable decisions. A parable is supplemental
  when the owner requires an explicit rule; it cannot replace a safety,
  authority, contract, or machine-checked invariant.
- Findings identify the class and region of a suspicious span without
  reproducing an injection payload. Store a short escaped excerpt only when
  needed for a human to locate it, and cap its length.
- Verification must prove that protected regions, code/identifier/string/URL
  tokens, and document structure were preserved to the extent promised by the
  selected operation. A failed proof makes the run unresolved, not successful.
- Receipts are evidence and should be excluded from later broad recodes by the
  active profile. They may be published only through the explicit publication
  path.
