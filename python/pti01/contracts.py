"""W0 contract validators with no broker or terminal mutation surface."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

EVENT_TYPES = frozenset({"trade.transaction.observed", "trade.state.snapshot", "chart.object.observed", "chart.state.snapshot", "market.tick.observed", "market.bar.observed", "market.state.snapshot", "quality.gap.detected", "quality.reconciliation.recorded"})
SOURCES = frozenset({"MT5_TERMINAL", "MT5_CHART", "PTI_RECONCILER"})
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
EVENT_ID_RE = re.compile(r"^evt_[0-9A-HJKMNP-TV-Z]{26}$")


class ContractViolation(ValueError):
    """Raised when data cannot safely enter the PTI.01 event stream."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _datetime_utc(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ContractViolation(f"{field}: invalid date-time") from exc
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ContractViolation(f"{field}: UTC offset required")
    return parsed


def validate_event(event: dict[str, Any]) -> None:
    required = {"event_id", "stream_id", "sequence", "event_type", "observed_at_utc", "ingested_at_utc", "source", "schema_version", "payload", "payload_sha256", "provenance"}
    missing = sorted(required - event.keys())
    if missing:
        raise ContractViolation(f"missing required fields: {', '.join(missing)}")
    if not EVENT_ID_RE.fullmatch(event["event_id"]):
        raise ContractViolation("event_id: invalid canonical ULID form")
    if not isinstance(event["sequence"], int) or event["sequence"] < 0:
        raise ContractViolation("sequence: non-negative integer required")
    if event["event_type"] not in EVENT_TYPES:
        raise ContractViolation("event_type: unknown event type")
    if event["source"] not in SOURCES:
        raise ContractViolation("source: unknown source")
    if event["schema_version"] != "0.1.0":
        raise ContractViolation("schema_version: unsupported")
    observed = _datetime_utc(event["observed_at_utc"], "observed_at_utc")
    ingested = _datetime_utc(event["ingested_at_utc"], "ingested_at_utc")
    if ingested < observed:
        raise ContractViolation("clock regression: ingestion precedes observation")
    if not isinstance(event["payload"], dict):
        raise ContractViolation("payload: object required")
    if not SHA256_RE.fullmatch(event["payload_sha256"]):
        raise ContractViolation("payload_sha256: invalid")
    if sha256_json(event["payload"]) != event["payload_sha256"]:
        raise ContractViolation("payload_sha256: mismatch")
    provenance = event["provenance"]
    if not isinstance(provenance, dict) or provenance.get("capture_mode") != "READ_ONLY":
        raise ContractViolation("provenance.capture_mode: READ_ONLY required")
    if not provenance.get("collector") or not provenance.get("collector_version"):
        raise ContractViolation("provenance: collector identity required")


def validate_read_only_policy(policy: dict[str, Any]) -> None:
    if policy.get("mode") != "READ_ONLY" or policy.get("default_decision") != "DENY":
        raise ContractViolation("policy must be READ_ONLY and default-deny")
    allowed = set(policy.get("allowed_capabilities", []))
    forbidden = set(policy.get("forbidden_capabilities", []))
    if allowed & forbidden:
        raise ContractViolation("capability appears in both allow and deny sets")
    mutation_terms = ("order_send", "order_modify", "position_open", "position_close")
    if any(any(term in capability for term in mutation_terms) for capability in allowed):
        raise ContractViolation("broker mutation capability present in allow set")
    required = {"broker.order_send", "broker.order_modify", "broker.order_cancel", "broker.position_open", "broker.position_close", "broker.position_modify"}
    if not required.issubset(forbidden):
        raise ContractViolation("required broker mutation denial missing")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
