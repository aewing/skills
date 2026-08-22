#!/usr/bin/env python3
"""Validate focus-group configuration, run bundles, and outcome manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROFILE_SCHEMA = "focus-group/profile@1"
PROCEDURE_SCHEMA = "focus-group/procedure@1"
CONFIG_SCHEMA = "focus-group/config@1"
OUTCOMES_SCHEMA = "focus-group/outcomes@1"
SESSION_SCHEMA = "focus-group/session@1"
SYNTHETIC_LABEL = "SYNTHETIC FOCUS GROUP — NOT HUMAN RESEARCH"

DISPOSITIONS = {
    "work-item",
    "design-concept",
    "feature-request",
    "decision-record",
    "research-question",
    "no-action",
    "needs-routing",
}
ROUTE_STATES = {
    "draft",
    "materialized",
    "needs-approval",
    "needs-routing",
    "not-applicable",
}
EVIDENCE_CLASSES = {
    "observed",
    "documented",
    "persona-inferred",
    "moderator-inferred",
    "unknown",
}
SEVERITIES = {"blocker", "high", "medium", "low", "positive"}
CONFIDENCES = {"high", "medium", "low"}
REQUIRED_OUTPUTS = {
    "participant-profiles",
    "full-transcript",
    "findings",
    "outcomes",
}
ADOPTION_GATED_DISPOSITIONS = {
    "work-item",
    "feature-request",
    "decision-record",
}
INFERRED_EVIDENCE_CLASSES = {"persona-inferred", "moderator-inferred"}
UNKNOWN_EVIDENCE_DISPOSITIONS = {"research-question", "no-action", "needs-routing"}
REQUIRED_RUN_FILES = {
    "SESSION.json",
    "PARTICIPANTS.md",
    "TRANSCRIPT.md",
    "FINDINGS.md",
    "OUTCOMES.json",
}
PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:discussion continued|transcript (?:omitted|truncated)|TODO)\b",
    re.IGNORECASE,
)


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{path}: file not found")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}:{exc.lineno}:{exc.colno}: {exc.msg}")
    return None


def require_mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: expected object")
        return {}
    return value


def require_string(mapping: dict[str, Any], key: str, label: str, errors: list[str]) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}.{key}: expected non-empty string")
        return ""
    return value.strip()


def require_string_list(
    mapping: dict[str, Any], key: str, label: str, errors: list[str]
) -> list[str]:
    value = mapping.get(key)
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        errors.append(f"{label}.{key}: expected non-empty string array")
        return []
    return [item.strip() for item in value]


def require_string_array(
    mapping: dict[str, Any],
    key: str,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool,
) -> list[str]:
    value = mapping.get(key)
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        qualifier = "string array" if allow_empty else "non-empty string array"
        errors.append(f"{label}.{key}: expected {qualifier}")
        return []
    return [item.strip() for item in value]


def require_positive_int(
    mapping: dict[str, Any], key: str, label: str, errors: list[str]
) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        errors.append(f"{label}.{key}: expected positive integer")
        return 0
    return value


def resolve_library(root: Path, raw: Any, label: str, errors: list[str]) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        errors.append(f"config.library.{label}: expected relative directory")
        return root / label
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"config.library.{label}: path must stay inside config root")
        return root / label
    path = root / relative
    if not path.is_dir():
        errors.append(f"config.library.{label}: directory not found: {path}")
    return path


def validate_profile(path: Path, errors: list[str]) -> tuple[str, str]:
    raw = require_mapping(load_json(path, errors), str(path), errors)
    label = str(path)
    if raw.get("schema") != PROFILE_SCHEMA:
        errors.append(f"{label}.schema: expected {PROFILE_SCHEMA}")
    profile_id = require_string(raw, "id", label, errors)
    if profile_id and not ID_PATTERN.fullmatch(profile_id):
        errors.append(f"{label}.id: expected lowercase kebab-case")
    if profile_id and path.stem != profile_id:
        errors.append(f"{label}.id: must match filename")
    require_positive_int(raw, "revision", label, errors)
    status = require_string(raw, "status", label, errors)
    if status not in {"active", "retired"}:
        errors.append(f"{label}.status: expected active or retired")
    for key in ("name", "role", "summary", "context"):
        require_string(raw, key, label, errors)
    for key in (
        "goals",
        "capabilities",
        "needs",
        "constraints",
        "behaviors",
        "questions",
        "guardrails",
    ):
        require_string_list(raw, key, label, errors)
    voice = require_mapping(raw.get("voice"), f"{label}.voice", errors)
    for key in ("tone", "language", "challengeStyle"):
        require_string(voice, key, f"{label}.voice", errors)
    return profile_id, status


def validate_procedure(
    path: Path, project_minimum: int, project_maximum: int, errors: list[str]
) -> tuple[str, str]:
    raw = require_mapping(load_json(path, errors), str(path), errors)
    label = str(path)
    if raw.get("schema") != PROCEDURE_SCHEMA:
        errors.append(f"{label}.schema: expected {PROCEDURE_SCHEMA}")
    procedure_id = require_string(raw, "id", label, errors)
    if procedure_id and not ID_PATTERN.fullmatch(procedure_id):
        errors.append(f"{label}.id: expected lowercase kebab-case")
    if procedure_id and path.stem != procedure_id:
        errors.append(f"{label}.id: must match filename")
    require_positive_int(raw, "revision", label, errors)
    status = require_string(raw, "status", label, errors)
    if status not in {"active", "retired"}:
        errors.append(f"{label}.status: expected active or retired")
    for key in ("name", "purpose"):
        require_string(raw, key, label, errors)
    for key in (
        "suitableFor",
        "inputs",
        "dimensions",
        "stoppingConditions",
        "requiredOutputs",
    ):
        require_string_list(raw, key, label, errors)

    panel = require_mapping(raw.get("panel"), f"{label}.panel", errors)
    panel_minimum = require_positive_int(panel, "minimum", f"{label}.panel", errors)
    panel_maximum = require_positive_int(panel, "maximum", f"{label}.panel", errors)
    if panel_minimum and panel_maximum and panel_minimum > panel_maximum:
        errors.append(f"{label}.panel: minimum exceeds maximum")
    if project_minimum and panel_minimum and panel_minimum < project_minimum:
        errors.append(f"{label}.panel.minimum: below project minimum {project_minimum}")
    if project_maximum and panel_maximum and panel_maximum > project_maximum:
        errors.append(f"{label}.panel.maximum: above project maximum {project_maximum}")

    budget = require_mapping(
        raw.get("moderationBudget"), f"{label}.moderationBudget", errors
    )
    require_positive_int(
        budget, "maximumTasks", f"{label}.moderationBudget", errors
    )
    require_positive_int(
        budget, "followUpRoundsPerPhase", f"{label}.moderationBudget", errors
    )
    require_string(budget, "stopWhen", f"{label}.moderationBudget", errors)
    require_string(budget, "extensionRule", f"{label}.moderationBudget", errors)

    phases = raw.get("phases")
    if not isinstance(phases, list) or not phases:
        errors.append(f"{label}.phases: expected non-empty phase array")
    else:
        phase_ids: set[str] = set()
        for index, phase_raw in enumerate(phases):
            phase_label = f"{label}.phases[{index}]"
            phase = require_mapping(phase_raw, phase_label, errors)
            phase_id = require_string(phase, "id", phase_label, errors)
            if phase_id in phase_ids:
                errors.append(f"{phase_label}.id: duplicate {phase_id}")
            phase_ids.add(phase_id)
            if phase_id and not ID_PATTERN.fullmatch(phase_id):
                errors.append(f"{phase_label}.id: expected lowercase kebab-case")
            require_string(phase, "mode", phase_label, errors)
            require_string(phase, "instruction", phase_label, errors)
            require_string_list(phase, "requiredRecord", phase_label, errors)

    outputs = set(raw.get("requiredOutputs", []))
    missing_outputs = REQUIRED_OUTPUTS - outputs
    if missing_outputs:
        errors.append(
            f"{label}.requiredOutputs: missing {', '.join(sorted(missing_outputs))}"
        )
    return procedure_id, status


def validate_config(root: Path) -> tuple[list[str], int, int]:
    errors: list[str] = []
    config_path = root / "config.json"
    config = require_mapping(load_json(config_path, errors), str(config_path), errors)
    if config.get("schema") != CONFIG_SCHEMA:
        errors.append(f"{config_path}.schema: expected {CONFIG_SCHEMA}")
    for key in ("id", "version"):
        require_string(config, key, str(config_path), errors)
    config_status = config.get("status")
    if config_status not in {"active", "proposed"}:
        errors.append(f"{config_path}.status: expected active or proposed")

    library = require_mapping(config.get("library"), "config.library", errors)
    profiles_dir = resolve_library(root, library.get("profiles"), "profiles", errors)
    procedures_dir = resolve_library(root, library.get("procedures"), "procedures", errors)

    panel = require_mapping(config.get("panel"), "config.panel", errors)
    project_minimum = require_positive_int(panel, "minimum", "config.panel", errors)
    project_maximum = require_positive_int(panel, "maximum", "config.panel", errors)
    if project_minimum and project_maximum and project_minimum > project_maximum:
        errors.append("config.panel: minimum exceeds maximum")
    if project_minimum and project_minimum < 4:
        errors.append("config.panel.minimum: must be at least 4")
    if project_maximum and project_maximum > 7:
        errors.append("config.panel.maximum: must be at most 7")
    profile_pool = require_string_array(
        panel,
        "profilePool",
        "config.panel",
        errors,
        allow_empty=config_status == "proposed",
    )
    require_string_list(panel, "selectionRules", "config.panel", errors)
    if len(profile_pool) != len(set(profile_pool)):
        errors.append("config.panel.profilePool: duplicate profile id")
    if (
        config_status == "active"
        and project_minimum
        and len(profile_pool) < project_minimum
    ):
        errors.append("config.panel.profilePool: fewer profiles than panel minimum")

    profile_states: dict[str, str] = {}
    profile_paths = sorted(profiles_dir.glob("*.json")) if profiles_dir.is_dir() else []
    if config_status == "active" and not profile_paths:
        errors.append(f"{profiles_dir}: no profile files")
    for path in profile_paths:
        profile_id, status = validate_profile(path, errors)
        if profile_id in profile_states:
            errors.append(f"{path}.id: duplicate profile id {profile_id}")
        profile_states[profile_id] = status
    for profile_id in profile_pool:
        if profile_id not in profile_states:
            errors.append(f"config.panel.profilePool: unknown id {profile_id}")
        elif profile_states[profile_id] != "active":
            errors.append(f"config.panel.profilePool: retired id {profile_id}")

    procedure_states: dict[str, str] = {}
    procedure_paths = sorted(procedures_dir.glob("*.json")) if procedures_dir.is_dir() else []
    if config_status == "active" and not procedure_paths:
        errors.append(f"{procedures_dir}: no procedure files")
    for path in procedure_paths:
        procedure_id, status = validate_procedure(
            path, project_minimum, project_maximum, errors
        )
        if procedure_id in procedure_states:
            errors.append(f"{path}.id: duplicate procedure id {procedure_id}")
        procedure_states[procedure_id] = status

    review = require_mapping(config.get("review"), "config.review", errors)
    default_procedure_raw = review.get("defaultProcedure")
    if config_status == "proposed" and default_procedure_raw is None:
        default_procedure = ""
    else:
        default_procedure = require_string(
            review, "defaultProcedure", "config.review", errors
        )
    label = require_string(review, "syntheticLabel", "config.review", errors)
    if label != SYNTHETIC_LABEL:
        errors.append("config.review.syntheticLabel: required synthetic-research label changed")
    if review.get("transcript") != "full":
        errors.append("config.review.transcript: expected full")
    require_string(review, "artifactResolution", "config.review", errors)
    require_string(review, "fallbackRunDirectory", "config.review", errors)
    if default_procedure and default_procedure not in procedure_states:
        errors.append(f"config.review.defaultProcedure: unknown id {default_procedure}")
    elif default_procedure and procedure_states[default_procedure] != "active":
        errors.append(f"config.review.defaultProcedure: retired id {default_procedure}")

    outcomes = require_mapping(config.get("outcomes"), "config.outcomes", errors)
    configured_dispositions = set(
        require_string_list(
            outcomes, "requiredDispositions", "config.outcomes", errors
        )
    )
    if configured_dispositions != DISPOSITIONS:
        missing = DISPOSITIONS - configured_dispositions
        unknown = configured_dispositions - DISPOSITIONS
        if missing:
            errors.append(
                "config.outcomes.requiredDispositions: missing "
                + ", ".join(sorted(missing))
            )
        if unknown:
            errors.append(
                "config.outcomes.requiredDispositions: unknown "
                + ", ".join(sorted(unknown))
            )
    require_string_list(outcomes, "routingOrder", "config.outcomes", errors)
    if outcomes.get("externalWrites") != "explicit":
        errors.append("config.outcomes.externalWrites: expected explicit")
    if outcomes.get("deduplicateBy") != "fingerprint":
        errors.append("config.outcomes.deduplicateBy: expected fingerprint")

    return errors, len(profile_paths), len(procedure_paths)


def normalize_fingerprint_part(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def expected_fingerprint(
    subject: str, finding: str, owner: str, disposition: str
) -> str:
    canonical = json.dumps(
        [
            normalize_fingerprint_part(subject),
            normalize_fingerprint_part(finding),
            normalize_fingerprint_part(owner),
            normalize_fingerprint_part(disposition),
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_outcomes(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    manifest = require_mapping(load_json(path, errors), str(path), errors)
    if manifest.get("schema") != OUTCOMES_SCHEMA:
        errors.append(f"{path}.schema: expected {OUTCOMES_SCHEMA}")
    require_string(manifest, "runId", str(path), errors)
    subject = require_string(manifest, "subject", str(path), errors)
    items = manifest.get("items")
    if not isinstance(items, list):
        errors.append(f"{path}.items: expected array")
        return errors, 0

    ids: set[str] = set()
    finding_ids: set[str] = set()
    fingerprints: set[str] = set()
    required = {
        "id",
        "findingId",
        "title",
        "finding",
        "evidenceClass",
        "evidence",
        "severity",
        "confidence",
        "participants",
        "disposition",
        "owner",
        "payload",
        "route",
        "fingerprint",
    }

    for index, item_raw in enumerate(items):
        label = f"{path}.items[{index}]"
        item = require_mapping(item_raw, label, errors)
        missing = required - set(item)
        if missing:
            errors.append(f"{label}: missing {', '.join(sorted(missing))}")
        item_id = require_string(item, "id", label, errors)
        finding_id = require_string(item, "findingId", label, errors)
        require_string(item, "title", label, errors)
        finding = require_string(item, "finding", label, errors)
        evidence_class = require_string(item, "evidenceClass", label, errors)
        evidence = require_string_list(item, "evidence", label, errors)
        severity = require_string(item, "severity", label, errors)
        confidence = require_string(item, "confidence", label, errors)
        participants = require_string_list(item, "participants", label, errors)
        disposition = require_string(item, "disposition", label, errors)
        owner_raw = item.get("owner")
        owner = owner_raw.strip() if isinstance(owner_raw, str) else ""
        payload = require_mapping(item.get("payload"), f"{label}.payload", errors)
        route = require_mapping(item.get("route"), f"{label}.route", errors)
        fingerprint = require_string(item, "fingerprint", label, errors)

        if item_id in ids:
            errors.append(f"{label}.id: duplicate {item_id}")
        ids.add(item_id)
        if finding_id in finding_ids:
            errors.append(f"{label}.findingId: duplicate {finding_id}")
        finding_ids.add(finding_id)
        if fingerprint in fingerprints:
            errors.append(f"{label}.fingerprint: duplicate")
        fingerprints.add(fingerprint)

        if evidence_class not in EVIDENCE_CLASSES:
            errors.append(f"{label}.evidenceClass: unknown {evidence_class}")
        if severity not in SEVERITIES:
            errors.append(f"{label}.severity: unknown {severity}")
        if confidence not in CONFIDENCES:
            errors.append(f"{label}.confidence: unknown {confidence}")
        if disposition not in DISPOSITIONS:
            errors.append(f"{label}.disposition: unknown {disposition}")
        if not evidence:
            errors.append(f"{label}.evidence: at least one evidence reference is required")
        if not participants:
            errors.append(f"{label}.participants: at least one profile id is required")

        require_string(route, "kind", f"{label}.route", errors)
        state = require_string(route, "state", f"{label}.route", errors)
        if state not in ROUTE_STATES:
            errors.append(f"{label}.route.state: unknown {state}")
        target = route.get("target")
        receipt = route.get("receipt")
        if state in {"draft", "materialized", "needs-approval"} and (
            not isinstance(target, str) or not target.strip()
        ):
            errors.append(f"{label}.route.target: required for state {state}")
        if state == "materialized" and (
            not isinstance(receipt, str) or not receipt.strip()
        ):
            errors.append(f"{label}.route.receipt: required for materialized outcome")

        if (
            evidence_class in INFERRED_EVIDENCE_CLASSES
            and disposition in ADOPTION_GATED_DISPOSITIONS
            and state == "materialized"
        ):
            adoption = require_mapping(item.get("adoption"), f"{label}.adoption", errors)
            for key in ("by", "basis", "receipt"):
                require_string(adoption, key, f"{label}.adoption", errors)

        if (
            evidence_class == "unknown"
            and disposition not in UNKNOWN_EVIDENCE_DISPOSITIONS
        ):
            errors.append(
                f"{label}.disposition: unknown evidence must use research-question, "
                "no-action, or needs-routing"
            )

        if disposition == "needs-routing":
            if state != "needs-routing":
                errors.append(f"{label}.route.state: needs-routing disposition requires needs-routing")
            require_string(payload, "missingRoute", f"{label}.payload", errors)
        elif disposition == "no-action":
            if state != "not-applicable":
                errors.append(f"{label}.route.state: no-action requires not-applicable")
            require_string(payload, "reason", f"{label}.payload", errors)
            if not owner:
                errors.append(f"{label}.owner: decision owner required for no-action")
        else:
            if state in {"needs-routing", "not-applicable"}:
                errors.append(
                    f"{label}.route.state: actionable disposition cannot use {state}"
                )
            if not owner:
                errors.append(f"{label}.owner: required for actionable disposition")

        if disposition == "work-item":
            require_string(payload, "problem", f"{label}.payload", errors)
            require_string_list(payload, "acceptance", f"{label}.payload", errors)
        elif disposition == "design-concept":
            require_string(payload, "designQuestion", f"{label}.payload", errors)
            require_string_list(payload, "proofPlan", f"{label}.payload", errors)
        elif disposition == "feature-request":
            require_string(payload, "userProblem", f"{label}.payload", errors)
        elif disposition == "decision-record":
            require_string(payload, "decision", f"{label}.payload", errors)
        elif disposition == "research-question":
            require_string(payload, "question", f"{label}.payload", errors)
            require_string(payload, "falsifier", f"{label}.payload", errors)

        if subject and finding and disposition in DISPOSITIONS:
            expected = expected_fingerprint(subject, finding, owner, disposition)
            if fingerprint != expected:
                errors.append(f"{label}.fingerprint: expected {expected}")

    return errors, len(items)


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"{path}: file not found")
        return ""


def validate_run(run_directory: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    missing_files = sorted(
        filename
        for filename in REQUIRED_RUN_FILES
        if not (run_directory / filename).is_file()
    )
    for filename in missing_files:
        errors.append(f"{run_directory / filename}: file not found")

    session_path = run_directory / "SESSION.json"
    session = require_mapping(load_json(session_path, errors), str(session_path), errors)
    if session.get("schema") != SESSION_SCHEMA:
        errors.append(f"{session_path}.schema: expected {SESSION_SCHEMA}")
    run_id = require_string(session, "runId", str(session_path), errors)
    if run_id and run_id != run_directory.name:
        errors.append(f"{session_path}.runId: must match run directory name")
    subject = require_string(session, "subject", str(session_path), errors)
    for key in ("startedAt", "completedAt"):
        require_string(session, key, str(session_path), errors)

    configuration = require_mapping(
        session.get("configuration"), f"{session_path}.configuration", errors
    )
    for key in ("path", "id", "version", "status"):
        require_string(configuration, key, f"{session_path}.configuration", errors)
    configuration_pool_ids = require_string_list(
        configuration,
        "profilePool",
        f"{session_path}.configuration",
        errors,
    )
    configuration_pool = set(configuration_pool_ids)
    if len(configuration_pool_ids) != len(configuration_pool):
        errors.append(
            f"{session_path}.configuration.profilePool: duplicate profile id"
        )
    configuration_panel = require_mapping(
        configuration.get("panel"),
        f"{session_path}.configuration.panel",
        errors,
    )
    project_minimum = require_positive_int(
        configuration_panel,
        "minimum",
        f"{session_path}.configuration.panel",
        errors,
    )
    project_maximum = require_positive_int(
        configuration_panel,
        "maximum",
        f"{session_path}.configuration.panel",
        errors,
    )
    if project_minimum and project_maximum and project_minimum > project_maximum:
        errors.append(f"{session_path}.configuration.panel: minimum exceeds maximum")
    if project_minimum and project_minimum < 4:
        errors.append(f"{session_path}.configuration.panel.minimum: must be at least 4")
    if project_maximum and project_maximum > 7:
        errors.append(f"{session_path}.configuration.panel.maximum: must be at most 7")

    procedure = require_mapping(
        session.get("procedure"), f"{session_path}.procedure", errors
    )
    require_string(procedure, "id", f"{session_path}.procedure", errors)
    procedure_revision = require_positive_int(
        procedure, "revision", f"{session_path}.procedure", errors
    )
    require_string(procedure, "path", f"{session_path}.procedure", errors)
    phase_ids = require_string_list(
        procedure, "phaseIds", f"{session_path}.procedure", errors
    )
    if len(phase_ids) != len(set(phase_ids)):
        errors.append(f"{session_path}.procedure.phaseIds: duplicate phase id")
    required_outputs = set(
        require_string_list(
            procedure, "requiredOutputs", f"{session_path}.procedure", errors
        )
    )
    missing_outputs = REQUIRED_OUTPUTS - required_outputs
    if missing_outputs:
        errors.append(
            f"{session_path}.procedure.requiredOutputs: missing "
            + ", ".join(sorted(missing_outputs))
        )
    procedure_panel = require_mapping(
        procedure.get("panel"), f"{session_path}.procedure.panel", errors
    )
    procedure_minimum = require_positive_int(
        procedure_panel, "minimum", f"{session_path}.procedure.panel", errors
    )
    procedure_maximum = require_positive_int(
        procedure_panel, "maximum", f"{session_path}.procedure.panel", errors
    )
    if (
        procedure_minimum
        and procedure_maximum
        and procedure_minimum > procedure_maximum
    ):
        errors.append(f"{session_path}.procedure.panel: minimum exceeds maximum")
    if procedure_revision >= 2:
        moderation_budget = require_mapping(
            procedure.get("moderationBudget"),
            f"{session_path}.procedure.moderationBudget",
            errors,
        )
        require_positive_int(
            moderation_budget,
            "maximumTasks",
            f"{session_path}.procedure.moderationBudget",
            errors,
        )
        require_positive_int(
            moderation_budget,
            "followUpRoundsPerPhase",
            f"{session_path}.procedure.moderationBudget",
            errors,
        )
        require_string(
            moderation_budget,
            "stopWhen",
            f"{session_path}.procedure.moderationBudget",
            errors,
        )
        require_string(
            moderation_budget,
            "extensionRule",
            f"{session_path}.procedure.moderationBudget",
            errors,
        )

    participants_raw = session.get("participants")
    selected_ids: set[str] = set()
    participant_revisions: dict[str, int] = {}
    if not isinstance(participants_raw, list) or not participants_raw:
        errors.append(f"{session_path}.participants: expected non-empty array")
        participants_raw = []
    for index, participant_raw in enumerate(participants_raw):
        participant_label = f"{session_path}.participants[{index}]"
        participant = require_mapping(participant_raw, participant_label, errors)
        participant_id = require_string(participant, "id", participant_label, errors)
        revision = require_positive_int(participant, "revision", participant_label, errors)
        require_string(participant, "path", participant_label, errors)
        require_string(participant, "selectionReason", participant_label, errors)
        if participant_id in selected_ids:
            errors.append(f"{participant_label}.id: duplicate {participant_id}")
        selected_ids.add(participant_id)
        if participant_id and revision:
            participant_revisions[participant_id] = revision

    selected_count = len(selected_ids)
    if procedure_minimum and selected_count < procedure_minimum:
        errors.append(
            f"{session_path}.participants: fewer than procedure minimum "
            f"{procedure_minimum}"
        )
    if procedure_maximum and selected_count > procedure_maximum:
        errors.append(
            f"{session_path}.participants: exceeds procedure maximum "
            f"{procedure_maximum}"
        )

    if project_minimum and selected_count < project_minimum:
        errors.append(
            f"{session_path}.participants: fewer than project minimum {project_minimum}"
        )
    if project_maximum and selected_count > project_maximum:
        errors.append(
            f"{session_path}.participants: exceeds project maximum {project_maximum}"
        )
    for participant_id in sorted(selected_ids - configuration_pool):
        errors.append(
            f"{session_path}.participants: {participant_id} is not in snapshotted "
            "configuration profilePool"
        )

    files = require_mapping(session.get("files"), f"{session_path}.files", errors)
    expected_file_map = {
        "participants": "PARTICIPANTS.md",
        "transcript": "TRANSCRIPT.md",
        "findings": "FINDINGS.md",
        "outcomes": "OUTCOMES.json",
    }
    for key, expected in expected_file_map.items():
        if files.get(key) != expected:
            errors.append(f"{session_path}.files.{key}: expected {expected}")

    human_artifacts: dict[str, str] = {}
    expected_first_line = f"# {SYNTHETIC_LABEL}"
    for filename in ("PARTICIPANTS.md", "TRANSCRIPT.md", "FINDINGS.md"):
        path = run_directory / filename
        content = read_text(path, errors) if path.is_file() else ""
        human_artifacts[filename] = content
        first_line = content.splitlines()[0] if content else ""
        if first_line != expected_first_line:
            errors.append(f"{path}: first line must be {expected_first_line}")

    participants_text = human_artifacts.get("PARTICIPANTS.md", "")
    documented_snapshots = re.findall(
        r"^Source: `([a-z0-9]+(?:-[a-z0-9]+)*)@(\d+)`$",
        participants_text,
        re.MULTILINE,
    )
    if len(documented_snapshots) != len(set(documented_snapshots)):
        errors.append(f"{run_directory / 'PARTICIPANTS.md'}: duplicate source snapshot")
    for participant_id, revision in participant_revisions.items():
        source = f"Source: `{participant_id}@{revision}`"
        if source not in participants_text:
            errors.append(
                f"{run_directory / 'PARTICIPANTS.md'}: missing snapshot {source}"
            )
    expected_snapshots = {
        (participant_id, str(revision))
        for participant_id, revision in participant_revisions.items()
    }
    for participant_id, revision in sorted(
        set(documented_snapshots) - expected_snapshots
    ):
        errors.append(
            f"{run_directory / 'PARTICIPANTS.md'}: unexpected snapshot "
            f"Source: `{participant_id}@{revision}`"
        )

    transcript_text = human_artifacts.get("TRANSCRIPT.md", "")
    placeholder = PLACEHOLDER_PATTERN.search(transcript_text)
    if placeholder:
        errors.append(
            f"{run_directory / 'TRANSCRIPT.md'}: placeholder omission "
            f"{placeholder.group(0)!r}"
        )
    phase_headings = re.findall(
        r"^## Phase\s+(\d+)\s+(?:—|-)\s+(.+?)\s*$", transcript_text, re.MULTILINE
    )
    if len(phase_headings) != len(phase_ids):
        errors.append(
            f"{run_directory / 'TRANSCRIPT.md'}: expected {len(phase_ids)} phase "
            f"headings, found {len(phase_headings)}"
        )
    for index, (phase_id, (number, heading)) in enumerate(
        zip(phase_ids, phase_headings), start=1
    ):
        if number != str(index):
            errors.append(
                f"{run_directory / 'TRANSCRIPT.md'}: expected Phase {index}, found "
                f"Phase {number}"
            )
        expected_words = {
            word for word in phase_id.split("-") if word not in {"and", "or", "the"}
        }
        heading_words = set(re.findall(r"[a-z0-9]+", heading.casefold()))
        if not expected_words.issubset(heading_words):
            errors.append(
                f"{run_directory / 'TRANSCRIPT.md'}: phase heading {heading!r} "
                f"does not identify {phase_id}"
            )

    findings_text = human_artifacts.get("FINDINGS.md", "")
    finding_ids = re.findall(r"^## (F-\d{3})\b", findings_text, re.MULTILINE)
    if not finding_ids:
        errors.append(f"{run_directory / 'FINDINGS.md'}: no finding sections")
    if len(finding_ids) != len(set(finding_ids)):
        errors.append(f"{run_directory / 'FINDINGS.md'}: duplicate finding id")

    outcomes_path = run_directory / "OUTCOMES.json"
    outcome_count = 0
    if outcomes_path.is_file():
        outcome_errors, outcome_count = validate_outcomes(outcomes_path)
        errors.extend(outcome_errors)
        manifest = require_mapping(
            load_json(outcomes_path, errors), str(outcomes_path), errors
        )
        if run_id and manifest.get("runId") != run_id:
            errors.append(f"{outcomes_path}.runId: does not match SESSION.json")
        if subject and manifest.get("subject") != subject:
            errors.append(f"{outcomes_path}.subject: does not match SESSION.json")
        items = manifest.get("items", [])
        outcome_finding_ids = {
            item.get("findingId")
            for item in items
            if isinstance(item, dict) and isinstance(item.get("findingId"), str)
        }
        finding_id_set = set(finding_ids)
        if finding_id_set != outcome_finding_ids:
            missing = sorted(finding_id_set - outcome_finding_ids)
            orphaned = sorted(outcome_finding_ids - finding_id_set)
            if missing:
                errors.append(
                    f"{outcomes_path}: missing outcomes for {', '.join(missing)}"
                )
            if orphaned:
                errors.append(
                    f"{outcomes_path}: outcomes without findings {', '.join(orphaned)}"
                )
        for index, item in enumerate(items if isinstance(items, list) else []):
            if not isinstance(item, dict):
                continue
            item_participants = item.get("participants", [])
            if not isinstance(item_participants, list):
                continue
            for participant_id in sorted(set(item_participants) - selected_ids):
                errors.append(
                    f"{outcomes_path}.items[{index}].participants: "
                    f"unselected profile {participant_id}"
                )

    return errors, outcome_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    config_parser = subparsers.add_parser("config", help="validate a config root")
    config_parser.add_argument("root", type=Path)
    run_parser = subparsers.add_parser("run", help="validate a completed run bundle")
    run_parser.add_argument("directory", type=Path)
    outcomes_parser = subparsers.add_parser("outcomes", help="validate OUTCOMES.json")
    outcomes_parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    if args.command == "config":
        errors, profiles, procedures = validate_config(args.root.resolve())
        success = f"focus-group config valid: {profiles} profiles, {procedures} procedures"
    elif args.command == "run":
        errors, outcomes = validate_run(args.directory.resolve())
        success = f"focus-group run valid: {outcomes} findings and outcomes"
    else:
        errors, outcomes = validate_outcomes(args.manifest.resolve())
        success = f"focus-group outcomes valid: {outcomes} items"

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"focus-group validation failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(success)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
