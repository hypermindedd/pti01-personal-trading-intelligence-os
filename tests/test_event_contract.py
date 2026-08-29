import copy
import unittest
from pathlib import Path

from pti01.contracts import (
    ContractViolation,
    load_json,
    sha256_json,
    validate_event,
    validate_event_type_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def valid_event():
    payload = {"symbol": "XAUUSD", "bid": "2500.10", "ask": "2500.20"}
    return {
        "event_id": "evt_01J00000000000000000000000",
        "stream_id": "market:XAUUSD:tick",
        "sequence": 42,
        "event_type": "market.tick.observed",
        "observed_at_utc": "2026-08-29T13:00:00Z",
        "ingested_at_utc": "2026-08-29T13:00:00.010000Z",
        "source": "MT5_TERMINAL",
        "schema_version": "0.1.0",
        "payload": payload,
        "payload_sha256": sha256_json(payload),
        "previous_event_sha256": None,
        "provenance": {
            "collector": "PTI01Observer",
            "collector_version": "0.1.0",
            "capture_mode": "READ_ONLY",
            "terminal_build": 5000,
        },
    }


class EventContractTests(unittest.TestCase):
    def test_valid_event_passes(self):
        validate_event(valid_event())

    def test_invalid_events_fail_closed(self):
        cases = [
            (lambda e: e.pop("provenance"), "missing required fields"),
            (
                lambda e: e.update(event_type="broker.order_send"),
                "unknown, reserved or forbidden",
            ),
            (
                lambda e: e["provenance"].update(capture_mode="EXECUTE"),
                "READ_ONLY required",
            ),
            (lambda e: e.update(payload_sha256="0" * 64), "mismatch"),
            (
                lambda e: e.update(
                    ingested_at_utc="2026-08-29T12:59:59Z"
                ),
                "clock regression",
            ),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                event = copy.deepcopy(valid_event())
                mutate(event)
                with self.assertRaisesRegex(ContractViolation, expected):
                    validate_event(event)

    def test_missing_type_specific_payload_field_fails_closed(self):
        event = valid_event()
        event["payload"].pop("bid")
        event["payload_sha256"] = sha256_json(event["payload"])
        with self.assertRaisesRegex(ContractViolation, "missing required fields.*bid"):
            validate_event(event)

    def test_reserved_event_type_is_not_admissible(self):
        event = valid_event()
        event["event_type"] = "market.microstructure.snapshot"
        with self.assertRaisesRegex(ContractViolation, "reserved"):
            validate_event(event)

    def test_boolean_sequence_is_rejected(self):
        event = valid_event()
        event["sequence"] = True
        with self.assertRaisesRegex(ContractViolation, "non-negative integer"):
            validate_event(event)

    def test_event_registry_matches_validator(self):
        registry = load_json(
            ROOT / "config" / "event_type_registry.v0.1.json"
        )
        validate_event_type_registry(registry)

    def test_event_registry_is_default_deny(self):
        registry = load_json(
            ROOT / "config" / "event_type_registry.v0.1.json"
        )
        registry["default_decision"] = "ALLOW"
        with self.assertRaisesRegex(ContractViolation, "default-deny"):
            validate_event_type_registry(registry)


if __name__ == "__main__":
    unittest.main()
