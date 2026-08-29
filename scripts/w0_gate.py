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
CODE_ROOTS = ("python", "config", "schemas")
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
        r"\b(?:ExecutionAdapter|BrokerMutationAdapter|DispatchPermit)\b"
    ),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_files():
    for root_name in CODE_ROOTS:
        root = ROOT / root_name
        if root.exists():
            yield from (p for p in root.rglob("*") if p.is_file())


def scan_for_mutation_surface():
    hits = []
    for path in code_files():
        if path.suffix.lower() not in {
            ".py",
            ".json",
            ".yaml",
            ".yml",
            ".mq5",
            ".mqh",
        }:
            continue
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


def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    policy = load_json(ROOT / "config/read_only_policy.v0.1.json")
    registry = load_json(ROOT / "config/event_type_registry.v0.1.json")
    validate_read_only_policy(policy)
    validate_event_type_registry(registry)
    forbidden = sorted(
        cap
        for cap in policy["allowed_capabilities"]
        if cap.startswith("broker.") or cap.startswith("chart.object_")
    )
    mutation_hits = scan_for_mutation_surface()
    present_excluded_inputs = sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file() and path.name in EXCLUDED_INPUT_NAMES
    )
    failures = bool(
        missing or forbidden or mutation_hits or present_excluded_inputs
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
