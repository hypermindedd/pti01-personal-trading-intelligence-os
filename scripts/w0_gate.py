"""Reproducible W0 static gate. Prints sanitized JSON evidence to stdout."""

import hashlib
import json
from pathlib import Path

from pti01.contracts import load_json, validate_read_only_policy

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["config/read_only_policy.v0.1.json", "schemas/events/event-envelope.v0.1.schema.json", "docs/architecture/W0_ARCHITECTURE_v0.1.md", "docs/adr/ADR-0001-read-only-observer.md", "docs/contracts/EVENT_ENVELOPE_v0.1.md", "docs/contracts/STORAGE_LAYERS_v0.1.md"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    policy = load_json(ROOT / "config/read_only_policy.v0.1.json")
    validate_read_only_policy(policy)
    forbidden = sorted(cap for cap in policy["allowed_capabilities"] if cap.startswith("broker.") or cap.startswith("chart.object_"))
    result = "PASS" if not missing and not forbidden else "FAIL"
    evidence = {"project": "PTI.01", "wave": "W0", "gate": "STATIC_ARCHITECTURE_SAFETY_CONTRACT_GATE", "result": result, "canonical_claim": False, "lock_claim": False, "runtime_claim": False, "missing_required_files": missing, "forbidden_capabilities_in_allow_set": forbidden, "file_sha256": {name: digest(ROOT / name) for name in REQUIRED if (ROOT / name).is_file()}}
    print(json.dumps(evidence, sort_keys=True, indent=2))
    raise SystemExit(0 if result == "PASS" else 1)


if __name__ == "__main__":
    main()
