"""W0 contract validators with no broker or terminal mutation surface."""

from __future__ import annotations

import hashlib
import json
import re
import math
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

PAYLOAD_REQUIRED_FIELDS = {
    "trade.transaction.observed": frozenset(
        {"trade_lifecycle_id", "transaction_kind", "symbol", "volume"}
    ),
    "trade.state.snapshot": frozenset({"snapshot_id", "completeness", "positions"}),
    "chart.object.observed": frozenset(
        {"object_lifecycle_id", "object_type", "state"}
    ),
    "chart.state.snapshot": frozenset({"snapshot_id", "completeness", "objects"}),
    "market.tick.observed": frozenset({"symbol", "bid", "ask"}),
    "market.bar.observed": frozenset(
        {"symbol", "timeframe", "open", "high", "low", "close"}
    ),
    "market.state.snapshot": frozenset(
        {"snapshot_id", "symbol", "timeframes", "completeness"}
    ),
    "quality.gap.detected": frozenset(
        {"affected_stream_id", "expected_sequence", "observed_sequence", "reason"}
    ),
    "quality.reconciliation.recorded": frozenset(
        {"snapshot_id", "replay_boundary", "disposition", "discrepancies"}
    ),
}
ALLOWED_CAPABILITIES = frozenset({
    "observe.account_metadata_sanitized", "observe.trade_transactions",
    "observe.chart_objects", "observe.market_ticks", "observe.market_bars",
    "snapshot.multi_timeframe_state", "persist.raw_append_only",
    "derive.versioned_features", "replay.deterministic",
})
TOP_LEVEL_FIELDS = frozenset({
    "event_id", "stream_id", "sequence", "event_type", "observed_at_utc",
    "source_time_utc", "ingested_at_utc", "source", "source_instance_id",
    "schema_version", "event_registry_version", "payload_schema_version",
    "payload", "payload_sha256", "previous_event_sha256", "provenance",
})
PROVENANCE_FIELDS = frozenset({
    "collector", "collector_version", "capture_mode", "terminal_build",
})
EVENT_TYPES = frozenset(PAYLOAD_REQUIRED_FIELDS)
SOURCES = frozenset({"MT5_TERMINAL", "MT5_CHART", "PTI_RECONCILER"})
EPISTEMIC_CLASSES = frozenset({"OBSERVED", "QUALITY", "DERIVED", "MODEL"})
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
EVENT_ID_RE = re.compile(r"^evt_[0-9A-HJKMNP-TV-Z]{26}$")
ROOT = Path(__file__).resolve().parents[2]


class ContractViolation(ValueError):
    """Raised when data cannot safely enter the PTI.01 event stream."""


def canonical_json(value: Any) -> bytes:
    value = _canonical_value(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode()


def _canonical_value(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractViolation("canonical_json: non-finite number")
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, dict):
        return {
            unicodedata.normalize("NFC", key): _canonical_value(item)
            for key, item in value.items()
        }
    return value


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _datetime_utc(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ContractViolation(f"{field}: invalid date-time") from exc
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.utcoffset().total_seconds() != 0
    ):
        raise ContractViolation(f"{field}: UTC offset required")
    return parsed


def _validate_payload(event_type: str, payload: dict[str, Any]) -> None:
    registry = load_json(ROOT / "config/event_type_registry.v0.1.json")
    active = registry.get("active_event_types", {})
    if event_type not in active:
        raise ContractViolation("event_type: unknown, reserved or forbidden event type")
    required = frozenset(active[event_type]["required_payload_fields"])
    missing = sorted(
        field for field in required if field not in payload or payload[field] is None
    )
    if missing:
        raise ContractViolation(
            f"payload: missing required fields for {event_type}: {', '.join(missing)}"
        )
    schemas = {
        "trade.transaction.observed": {"trade_lifecycle_id": str, "transaction_kind": str, "symbol": str, "volume": (int, float, str)},
        "trade.state.snapshot": {"snapshot_id": str, "completeness": str, "positions": list},
        "chart.object.observed": {"object_lifecycle_id": str, "object_type": str, "state": dict},
        "chart.state.snapshot": {"snapshot_id": str, "completeness": str, "objects": list},
        "market.tick.observed": {"symbol": str, "bid": (int, float, str), "ask": (int, float, str)},
        "market.bar.observed": {"symbol": str, "timeframe": str, "open": (int, float, str), "high": (int, float, str), "low": (int, float, str), "close": (int, float, str)},
        "market.state.snapshot": {"snapshot_id": str, "symbol": str, "timeframes": dict, "completeness": str},
        "quality.gap.detected": {"affected_stream_id": str, "expected_sequence": int, "observed_sequence": int, "reason": str},
        "quality.reconciliation.recorded": {"snapshot_id": str, "replay_boundary": dict, "disposition": str, "discrepancies": list},
    }
    for field, expected in schemas[event_type].items():
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, expected):
            raise ContractViolation(f"payload.{field}: invalid type")
        if isinstance(value, float) and not math.isfinite(value):
            raise ContractViolation(f"payload.{field}: finite number required")
        if isinstance(value, str) and not value:
            raise ContractViolation(f"payload.{field}: non-empty string required")
        if expected == (int, float, str) and isinstance(value, str):
            try:
                numeric = Decimal(value)
            except InvalidOperation as exc:
                raise ContractViolation(f"payload.{field}: decimal required") from exc
            if not numeric.is_finite():
                raise ContractViolation(f"payload.{field}: finite decimal required")


def validate_event(event: dict[str, Any]) -> None:
    required = {
        "event_id",
        "stream_id",
        "sequence",
        "event_type",
        "observed_at_utc",
        "ingested_at_utc",
        "source",
        "schema_version",
        "event_registry_version",
        "payload_schema_version",
        "payload",
        "payload_sha256",
        "provenance",
    }
    missing = sorted(required - event.keys())
    if missing:
        raise ContractViolation(f"missing required fields: {', '.join(missing)}")
    unknown = sorted(set(event) - TOP_LEVEL_FIELDS)
    if unknown:
        raise ContractViolation(f"unknown top-level fields: {', '.join(unknown)}")
    if not isinstance(event["event_id"], str) or not EVENT_ID_RE.fullmatch(
        event["event_id"]
    ):
        raise ContractViolation("event_id: invalid canonical ULID form")
    if not isinstance(event["stream_id"], str) or not 1 <= len(event["stream_id"]) <= 160:
        raise ContractViolation("stream_id: non-empty string required")
    if (
        not isinstance(event["sequence"], int)
        or isinstance(event["sequence"], bool)
        or event["sequence"] < 0
    ):
        raise ContractViolation("sequence: non-negative integer required")
    registry = load_json(ROOT / "config/event_type_registry.v0.1.json")
    if event["event_type"] not in registry.get("active_event_types", {}):
        raise ContractViolation("event_type: unknown, reserved or forbidden event type")
    if event["source"] not in SOURCES:
        raise ContractViolation("source: unknown source")
    if event["schema_version"] != "0.1.0":
        raise ContractViolation("schema_version: unsupported")
    if event["event_registry_version"] != "0.1.0":
        raise ContractViolation("event_registry_version: unsupported")
    if event["payload_schema_version"] != "0.1.0":
        raise ContractViolation("payload_schema_version: unsupported")
    observed = _datetime_utc(event["observed_at_utc"], "observed_at_utc")
    if event.get("source_time_utc") is not None:
        _datetime_utc(event["source_time_utc"], "source_time_utc")
    source_instance_id = event.get("source_instance_id")
    if source_instance_id is not None and (
        not isinstance(source_instance_id, str) or len(source_instance_id) > 128
    ):
        raise ContractViolation("source_instance_id: invalid")
    previous = event.get("previous_event_sha256")
    if previous is not None and (
        not isinstance(previous, str) or not SHA256_RE.fullmatch(previous)
    ):
        raise ContractViolation("previous_event_sha256: invalid")
    ingested = _datetime_utc(event["ingested_at_utc"], "ingested_at_utc")
    if ingested < observed:
        raise ContractViolation("clock regression: ingestion precedes observation")
    if not isinstance(event["payload"], dict):
        raise ContractViolation("payload: object required")
    _validate_payload(event["event_type"], event["payload"])
    if not isinstance(event["payload_sha256"], str) or not SHA256_RE.fullmatch(
        event["payload_sha256"]
    ):
        raise ContractViolation("payload_sha256: invalid")
    if sha256_json(event["payload"]) != event["payload_sha256"]:
        raise ContractViolation("payload_sha256: mismatch")
    provenance = event["provenance"]
    if (
        not isinstance(provenance, dict)
        or provenance.get("capture_mode") != "READ_ONLY"
    ):
        raise ContractViolation("provenance.capture_mode: READ_ONLY required")
    unknown_provenance = sorted(set(provenance) - PROVENANCE_FIELDS)
    if unknown_provenance:
        raise ContractViolation("provenance: unknown fields")
    if not provenance.get("collector") or not provenance.get("collector_version"):
        raise ContractViolation("provenance: collector identity required")
    terminal_build = provenance.get("terminal_build")
    if terminal_build is not None and (
        not isinstance(terminal_build, int) or isinstance(terminal_build, bool) or terminal_build < 0
    ):
        raise ContractViolation("provenance.terminal_build: invalid")


def validate_event_type_registry(registry: dict[str, Any]) -> None:
    if registry.get("default_decision") != "DENY":
        raise ContractViolation("event registry must be default-deny")
    active = registry.get("active_event_types")
    if not isinstance(active, dict) or set(active) != set(EVENT_TYPES):
        raise ContractViolation("event registry active set differs from validator")
    reserved = set(registry.get("reserved_event_types", []))
    forbidden = set(registry.get("forbidden_event_types", []))
    if set(active) & reserved or set(active) & forbidden or reserved & forbidden:
        raise ContractViolation("event registry classes must be disjoint")
    for event_type, definition in active.items():
        if definition.get("epistemic_class") not in EPISTEMIC_CLASSES:
            raise ContractViolation(
                f"event registry: invalid epistemic class for {event_type}"
            )
        fields = definition.get("required_payload_fields")
        if (
            not isinstance(fields, list)
            or not fields
            or set(fields) != set(PAYLOAD_REQUIRED_FIELDS[event_type])
        ):
            raise ContractViolation(
                f"event registry: required payload fields differ for {event_type}"
            )


def validate_read_only_policy(policy: dict[str, Any]) -> None:
    if policy.get("mode") != "READ_ONLY" or policy.get("default_decision") != "DENY":
        raise ContractViolation("policy must be READ_ONLY and default-deny")
    allowed = set(policy.get("allowed_capabilities", []))
    if allowed != set(ALLOWED_CAPABILITIES):
        raise ContractViolation("allowed capabilities differ from exact authority")
    forbidden = set(policy.get("forbidden_capabilities", []))
    if allowed & forbidden:
        raise ContractViolation("capability appears in both allow and deny sets")
    mutation_terms = (
        "order_send",
        "order_modify",
        "order_cancel",
        "position_open",
        "position_close",
        "position_modify",
        "object_create",
        "object_modify",
        "object_delete",
        "setting_modify",
    )
    if any(
        any(term in capability for term in mutation_terms) for capability in allowed
    ):
        raise ContractViolation("mutation capability present in allow set")
    required = {
        "broker.order_send",
        "broker.order_modify",
        "broker.order_cancel",
        "broker.position_open",
        "broker.position_close",
        "broker.position_modify",
        "chart.object_create",
        "chart.object_modify",
        "chart.object_delete",
        "account.setting_modify",
    }
    if not required.issubset(forbidden):
        raise ContractViolation("required mutation denial missing")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
