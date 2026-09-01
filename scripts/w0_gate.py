"""Reproducible W0 static gate. Prints sanitized JSON evidence to stdout."""

import hashlib
import json
import re
from pathlib import Path

from pti01.contracts import (
    load_json,
    validate_event_type_registry,
    validate_read_only_policy,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "config/read_only_policy.v0.1.json",
    "config/event_type_registry.v0.1.json",
    "config/source_surface_registry.v0.1.json",
    "schemas/events/event-envelope.v0.1.schema.json",
    "docs/adr/ADR-0001-read-only-observer.md",
    "docs/architecture/W0_ARCHITECTURE_v0.1.md",
    "docs/architecture/THREAT_MODEL_v0.1.md",
    "docs/architecture/W0_W1_INTERFACE_FREEZE_v0.1.md",
    "docs/contracts/EVENT_ENVELOPE_v0.1.md",
    "docs/contracts/EVENT_PAYLOAD_ADMISSION_v0.1.md",
    "docs/contracts/STORAGE_LAYERS_v0.1.md",
    "docs/contracts/FAILURE_RECONCILIATION_v0.1.md",
    "docs/contracts/IDENTITY_TIME_ORDERING_v0.1.md",
    "docs/contracts/EVENT_TAXONOMY_v0.1.md",
    "docs/contracts/LATENT_RULE_EPISTEMICS_v0.1.md",
]
EXCLUDED_INPUT_NAMES = {"IMG_2750.png", "IMG_2751.jpeg"}
MUTATION_PATTERNS = {
    "mt5_order_send": re.compile(
        r"\b(?:mt5|MetaTrader5)\s*\.\s*order_send\s*\("
    ),
    "trade_request_action": re.compile(
        r"\bTRADE_ACTION_(?:DEAL|PENDING|MODIFY|REMOVE|SLTP|CLOSE_BY)\b"
    ),
    "chart_mutation_api": re.compile(
        r"\bObject(?:Create|Set|Delete|Move)\s*\("
    ),
    "execution_adapter": re.compile(
        r"\b(?:Execution" r"Adapter|BrokerMutation" r"Adapter|Dispatch" r"Permit)\b"
    ),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_files(surface_registry):
    for root_name in surface_registry["classified_roots"]:
        root = ROOT / root_name
        if root.exists():
            yield from (
                p for p in root.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
            )


def scan_for_mutation_surface(surface_registry):
    hits = []
    for path in code_files(surface_registry):
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in MUTATION_PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                hits.append(
                    {
                        "path": str(path.relative_to(ROOT)),
                        "line": line,
                        "pattern": name,
                    }
                )
    return hits


def suspect_runtime_files(surface_registry):
    executable_extensions = set(surface_registry["executable_extensions"])
    suspects = []
    for root_name, classification in surface_registry["classified_roots"].items():
        if classification != "RUNTIME_CAPABLE":
            continue
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.name == ".gitkeep" and path.stat().st_size == 0:
                continue
            first_line = path.read_bytes()[:256].splitlines()[:1]
            has_shebang = bool(first_line and first_line[0].startswith(b"#!"))
            executable_bit = bool(path.stat().st_mode & 0o111)
            known_extension = path.suffix.lower() in executable_extensions
            if not known_extension or has_shebang or executable_bit:
                if not known_extension:
                    suspects.append(str(path.relative_to(ROOT)))
    return sorted(set(suspects))


def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    policy = load_json(ROOT / "config/read_only_policy.v0.1.json")
    registry = load_json(ROOT / "config/event_type_registry.v0.1.json")
    surface_registry = load_json(ROOT / "config/source_surface_registry.v0.1.json")
    if surface_registry.get("default_decision") != "DENY":
        raise ValueError("source surface registry must be default-deny")
    validate_read_only_policy(policy)
    validate_event_type_registry(registry)
    forbidden = sorted(
        cap
        for cap in policy["allowed_capabilities"]
        if cap.startswith("broker.") or cap.startswith("chart.object_")
    )
    mutation_hits = scan_for_mutation_surface(surface_registry)
    suspect_runtime = suspect_runtime_files(surface_registry)
    executable_extensions = set(surface_registry["executable_extensions"])
    classified_roots = set(surface_registry["classified_roots"])
    unclassified_executables = sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in executable_extensions
        and path.relative_to(ROOT).parts[0] not in classified_roots
    )
    present_excluded_inputs = sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path.name in EXCLUDED_INPUT_NAMES
    )
    failures = bool(
        missing or forbidden or mutation_hits or present_excluded_inputs
        or unclassified_executables or suspect_runtime
    )
    evidence = {
        "project": "PTI.01",
        "wave": "W0",
        "gate": "STATIC_ARCHITECTURE_SAFETY_CONTRACT_GATE",
        "result": "FAIL" if failures else "PASS",
        "canonical_claim": False,
        "lock_claim": False,
        "runtime_claim": False,
        "real_mt5_claim": False,
        "missing_required_files": missing,
        "active_event_type_count": len(registry["active_event_types"]),
        "reserved_event_type_count": len(registry["reserved_event_types"]),
        "forbidden_capabilities_in_allow_set": forbidden,
        "mutation_surface_hits": mutation_hits,
        "unclassified_executables": unclassified_executables,
        "suspect_runtime_files": suspect_runtime,
        "present_excluded_inputs": present_excluded_inputs,
        "file_sha256": {
            name: digest(ROOT / name)
            for name in REQUIRED
            if (ROOT / name).is_file()
        },
    }
    print(json.dumps(evidence, sort_keys=True, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
