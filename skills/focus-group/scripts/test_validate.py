#!/usr/bin/env python3
"""Self-contained behavioral tests for the focus-group consistency checker."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import validate


class FocusGroupValidationTests(unittest.TestCase):
    profile_ids = ["direct-user", "newcomer", "access-user", "operator"]

    def write_json(self, path: Path, value: object) -> None:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def make_profile(self, profile_id: str) -> dict[str, object]:
        return {
            "schema": validate.PROFILE_SCHEMA,
            "id": profile_id,
            "revision": 1,
            "status": "active",
            "name": profile_id.replace("-", " ").title(),
            "role": "Synthetic evaluation lens",
            "summary": "A bounded profile used by validator tests.",
            "context": "Reviews an example feature to inform a product decision.",
            "goals": ["Complete the example task."],
            "capabilities": ["Reads structured product evidence."],
            "needs": ["Clear state and recovery."],
            "constraints": ["Has only the evidence in the test fixture."],
            "behaviors": ["Checks the result before trusting it."],
            "questions": ["What happens after the action?"],
            "voice": {
                "tone": "direct",
                "language": "plain",
                "challengeStyle": "asks for observable evidence",
            },
            "guardrails": ["Do not infer traits beyond this profile."],
        }

    def make_procedure(self) -> dict[str, object]:
        return {
            "schema": validate.PROCEDURE_SCHEMA,
            "id": "basic-review",
            "revision": 2,
            "status": "active",
            "name": "Basic review",
            "purpose": "Exercise one bounded example decision.",
            "suitableFor": ["validator tests"],
            "panel": {"minimum": 4, "maximum": 4},
            "inputs": ["An example feature."],
            "moderationBudget": {
                "maximumTasks": 1,
                "followUpRoundsPerPhase": 1,
                "stopWhen": "Every required record is captured.",
                "extensionRule": "Record the evidence gap before extending.",
            },
            "phases": [
                {
                    "id": "first-read",
                    "mode": "individual-reaction",
                    "instruction": "Capture an unprimed first interpretation.",
                    "requiredRecord": ["first interpretation"],
                }
            ],
            "dimensions": ["comprehension"],
            "stoppingConditions": ["The required record exists."],
            "requiredOutputs": sorted(validate.REQUIRED_OUTPUTS),
        }

    def make_config(self, status: str) -> dict[str, object]:
        active = status == "active"
        return {
            "schema": validate.CONFIG_SCHEMA,
            "id": "fixture-focus-group",
            "version": "1",
            "status": status,
            "library": {"profiles": "profiles", "procedures": "procedures"},
            "panel": {
                "minimum": 4,
                "maximum": 7,
                "profilePool": self.profile_ids if active else [],
                "selectionRules": [
                    "Every selected seat must add a causal product perspective."
                ],
            },
            "review": {
                "defaultProcedure": "basic-review" if active else None,
                "syntheticLabel": validate.SYNTHETIC_LABEL,
                "transcript": "full",
                "artifactResolution": "project-standard-first",
                "fallbackRunDirectory": ".focus-group/runs",
            },
            "outcomes": {
                "requiredDispositions": sorted(validate.DISPOSITIONS),
                "routingOrder": ["user-request", "needs-routing"],
                "externalWrites": "explicit",
                "deduplicateBy": "fingerprint",
            },
        }

    def make_config_root(self, directory: str, *, active: bool) -> Path:
        root = Path(directory) / ".focus-group"
        profiles = root / "profiles"
        procedures = root / "procedures"
        profiles.mkdir(parents=True)
        procedures.mkdir()
        if active:
            for profile_id in self.profile_ids:
                self.write_json(profiles / f"{profile_id}.json", self.make_profile(profile_id))
            self.write_json(procedures / "basic-review.json", self.make_procedure())
        self.write_json(root / "config.json", self.make_config("active" if active else "proposed"))
        return root

    def make_item(
        self,
        index: int,
        disposition: str,
        subject: str,
        *,
        evidence_class: str = "persona-inferred",
    ) -> dict[str, object]:
        finding = f"Example finding for {disposition}."
        owner = "" if disposition == "needs-routing" else "product owner"
        payloads: dict[str, dict[str, object]] = {
            "work-item": {
                "problem": "A bounded implementation problem.",
                "acceptance": ["The observable failure no longer occurs."],
            },
            "design-concept": {
                "designQuestion": "How should recovery remain visible?",
                "proofPlan": ["Exercise the revised recovery flow."],
            },
            "feature-request": {"userProblem": "The needed capability is absent."},
            "decision-record": {"decision": "Preserve the confirmation step."},
            "research-question": {
                "question": "Do real users recognize the recovery state?",
                "falsifier": "A real-user test shows recognition without help.",
            },
            "no-action": {"reason": "The positive behavior is already verified."},
            "needs-routing": {"missingRoute": "No design owner is discoverable."},
        }
        if disposition == "no-action":
            state, target = "not-applicable", None
        elif disposition == "needs-routing":
            state, target = "needs-routing", None
        else:
            state, target = "draft", "project-standard destination"
        return {
            "id": f"FG-{index:03d}",
            "findingId": f"F-{index:03d}",
            "title": f"Outcome for {disposition}",
            "finding": finding,
            "evidenceClass": evidence_class,
            "evidence": ["TRANSCRIPT.md#example"],
            "severity": "medium",
            "confidence": "medium",
            "participants": ["direct-user"],
            "disposition": disposition,
            "owner": owner,
            "payload": payloads[disposition],
            "route": {
                "kind": "project-standard",
                "target": target,
                "state": state,
                "receipt": None,
            },
            "fingerprint": validate.expected_fingerprint(
                subject, finding, owner, disposition
            ),
        }

    def validate_manifest(self, manifest: dict[str, object]) -> list[str]:
        with tempfile.TemporaryDirectory(prefix="focus-group-outcomes-") as directory:
            path = Path(directory) / "OUTCOMES.json"
            self.write_json(path, manifest)
            errors, _ = validate.validate_outcomes(path)
        return errors

    def make_run(self, directory: str) -> Path:
        root = self.make_config_root(directory, active=True)
        run = root / "runs" / "2026-08-22-example"
        run.mkdir(parents=True)
        budget = self.make_procedure()["moderationBudget"]
        participants = [
            {
                "id": profile_id,
                "revision": 1,
                "path": f".focus-group/profiles/{profile_id}.json",
                "selectionReason": f"{profile_id} changes what this review can notice.",
            }
            for profile_id in self.profile_ids
        ]
        session = {
            "schema": validate.SESSION_SCHEMA,
            "runId": run.name,
            "startedAt": "2026-08-22T00:00:00Z",
            "completedAt": "2026-08-22T00:05:00Z",
            "subject": "Example feature",
            "configuration": {
                "path": ".focus-group/config.json",
                "id": "fixture-focus-group",
                "version": "1",
                "status": "active",
                "panel": {"minimum": 4, "maximum": 7},
                "profilePool": self.profile_ids,
            },
            "procedure": {
                "id": "basic-review",
                "revision": 2,
                "path": ".focus-group/procedures/basic-review.json",
                "panel": {"minimum": 4, "maximum": 4},
                "moderationBudget": budget,
                "phaseIds": ["first-read"],
                "requiredOutputs": sorted(validate.REQUIRED_OUTPUTS),
            },
            "participants": participants,
            "files": {
                "participants": "PARTICIPANTS.md",
                "transcript": "TRANSCRIPT.md",
                "findings": "FINDINGS.md",
                "outcomes": "OUTCOMES.json",
            },
        }
        self.write_json(run / "SESSION.json", session)
        sources = "\n\n".join(
            f"## {profile_id}\n\nSource: `{profile_id}@1`"
            for profile_id in self.profile_ids
        )
        (run / "PARTICIPANTS.md").write_text(
            f"# {validate.SYNTHETIC_LABEL}\n\n{sources}\n", encoding="utf-8"
        )
        (run / "TRANSCRIPT.md").write_text(
            f"# {validate.SYNTHETIC_LABEL}\n\n## Phase 1 — First read\n\n"
            "Moderator: What do you expect?\n\nDirect User: A visible result.\n",
            encoding="utf-8",
        )
        (run / "FINDINGS.md").write_text(
            f"# {validate.SYNTHETIC_LABEL}\n\n## F-001 — Example finding\n\n"
            "The example has one routed finding.\n",
            encoding="utf-8",
        )
        manifest = {
            "schema": validate.OUTCOMES_SCHEMA,
            "runId": run.name,
            "subject": "Example feature",
            "items": [self.make_item(1, "work-item", "Example feature")],
        }
        self.write_json(run / "OUTCOMES.json", manifest)
        return run

    def test_active_and_proposed_configs_are_valid(self) -> None:
        for active, counts in ((True, (4, 1)), (False, (0, 0))):
            with self.subTest(active=active), tempfile.TemporaryDirectory() as directory:
                root = self.make_config_root(directory, active=active)
                errors, profiles, procedures = validate.validate_config(root)
                self.assertEqual(errors, [])
                self.assertEqual((profiles, procedures), counts)

    def test_procedure_without_moderation_budget_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_config_root(directory, active=True)
            procedure_path = root / "procedures" / "basic-review.json"
            procedure = json.loads(procedure_path.read_text(encoding="utf-8"))
            procedure.pop("moderationBudget")
            self.write_json(procedure_path, procedure)
            errors, _, _ = validate.validate_config(root)
        self.assertIn("moderationBudget: expected object", "\n".join(errors))

    def test_every_supported_disposition_forms_a_valid_draft(self) -> None:
        subject = "Example feature"
        manifest = {
            "schema": validate.OUTCOMES_SCHEMA,
            "runId": "2026-08-22-example",
            "subject": subject,
            "items": [
                self.make_item(index, disposition, subject)
                for index, disposition in enumerate(sorted(validate.DISPOSITIONS), start=1)
            ],
        }
        self.assertEqual(self.validate_manifest(manifest), [])

    def test_inferred_materialization_requires_explicit_adoption(self) -> None:
        subject = "Example feature"
        item = self.make_item(1, "work-item", subject)
        item["route"] = {
            "kind": "project-standard",
            "target": "canonical work item",
            "state": "materialized",
            "receipt": "work:123",
        }
        manifest = {
            "schema": validate.OUTCOMES_SCHEMA,
            "runId": "2026-08-22-inferred",
            "subject": subject,
            "items": [item],
        }
        self.assertIn("adoption: expected object", "\n".join(self.validate_manifest(manifest)))
        item["adoption"] = {
            "by": "product owner",
            "basis": "The owner accepts the synthetic hypothesis as project work.",
            "receipt": "decision:456",
        }
        self.assertEqual(self.validate_manifest(manifest), [])

    def test_observed_materialization_does_not_require_adoption(self) -> None:
        subject = "Example feature"
        item = self.make_item(1, "work-item", subject, evidence_class="observed")
        item["route"] = {
            "kind": "project-standard",
            "target": "canonical work item",
            "state": "materialized",
            "receipt": "work:123",
        }
        manifest = {
            "schema": validate.OUTCOMES_SCHEMA,
            "runId": "2026-08-22-observed",
            "subject": subject,
            "items": [item],
        }
        self.assertEqual(self.validate_manifest(manifest), [])

    def test_unknown_evidence_stays_research_shaped(self) -> None:
        subject = "Example feature"
        item = self.make_item(1, "work-item", subject, evidence_class="unknown")
        manifest = {
            "schema": validate.OUTCOMES_SCHEMA,
            "runId": "2026-08-22-unknown",
            "subject": subject,
            "items": [item],
        }
        self.assertIn(
            "unknown evidence must use research-question, no-action, or needs-routing",
            "\n".join(self.validate_manifest(manifest)),
        )

    def test_complete_run_and_command_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = self.make_run(directory)
            errors, outcomes = validate.validate_run(run)
            self.assertEqual(errors, [])
            self.assertEqual(outcomes, 1)
            completed = subprocess.run(
                [sys.executable, str(Path(validate.__file__)), "run", str(run)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("focus-group run valid: 1 findings and outcomes", completed.stdout)

    def test_run_rejects_missing_phase_snapshot_and_orphan_failures(self) -> None:
        mutations = {
            "missing file": lambda run: (run / "PARTICIPANTS.md").unlink(),
            "omitted phase": lambda run: (run / "TRANSCRIPT.md").write_text(
                (run / "TRANSCRIPT.md")
                .read_text(encoding="utf-8")
                .replace("## Phase 1 — First read", "## Debrief", 1),
                encoding="utf-8",
            ),
            "stale snapshot": lambda run: (run / "PARTICIPANTS.md").write_text(
                (run / "PARTICIPANTS.md")
                .read_text(encoding="utf-8")
                .replace("direct-user@1", "direct-user@2", 1),
                encoding="utf-8",
            ),
            "orphan finding": lambda run: (run / "FINDINGS.md").write_text(
                (run / "FINDINGS.md").read_text(encoding="utf-8")
                + "\n## F-002 — Orphan\n\nNo outcome.\n",
                encoding="utf-8",
            ),
        }
        expected = {
            "missing file": "PARTICIPANTS.md: file not found",
            "omitted phase": "expected 1 phase headings, found 0",
            "stale snapshot": "missing snapshot Source: `direct-user@1`",
            "orphan finding": "missing outcomes for F-002",
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                run = self.make_run(directory)
                mutate(run)
                errors, _ = validate.validate_run(run)
                self.assertIn(expected[name], "\n".join(errors))

    def test_revision_two_run_requires_a_budget_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = self.make_run(directory)
            session_path = run / "SESSION.json"
            session = json.loads(session_path.read_text(encoding="utf-8"))
            session["procedure"].pop("moderationBudget")
            self.write_json(session_path, session)
            errors, _ = validate.validate_run(run)
        self.assertIn("procedure.moderationBudget: expected object", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
