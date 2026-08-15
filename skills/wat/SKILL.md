---
name: wat
description: ADHD-friendly response overlay. Use for status, summaries, handoffs, or whenever the user asks for short, plain, easy-to-scan writing. Lead with the answer, keep one screen, preserve evidence, and expose one next action.
---

# Wat

A response overlay for short, plain, easy-to-scan answers. Keep the project's
writing guide as the content authority; this overlay changes presentation only,
never the work or proof required.

Use this shape:

```text
**Answer —** one sentence.

**Done**
- Up to three one-line results with proof.

**Next**
- → One action.

**Need you**
- One bounded decision. Omit when work can continue.
```

For example, instead of:

```text
Alright, so I looked into the build failure. After checking the logs I noticed
the test helper was importing from the old path, and there were two failures in
the network layer. I also cleaned up a few things and ran the suite twice to be
sure. The fix is in and I think we're good to merge once CI passes.
```

write:

```text
**Answer —** Build failure was a stale import in the test helper; fix is in.

**Done**
- `tests/helpers.ts` now imports from `lib/` — test suite 128 passed, 0 failed.

**Next**
- → Merge once CI passes.

**Need you**
- (omitted — work can continue)
```

Rules:

- Answer first. Use plain words and one idea per line.
- Keep each section to three bullets and the whole reply to one screen.
- Bold only the words a skimming reader must catch.
- Cut setup, task recaps, narration, and filler before cutting evidence.
- Use exact file links and copyable commands when they save explanation.
- Add a table or diagram only when it is clearer than three sentences.
- Do not use emojis unless asked.
