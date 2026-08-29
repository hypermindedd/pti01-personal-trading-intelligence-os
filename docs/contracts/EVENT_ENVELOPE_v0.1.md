# PTI.01 Event Envelope v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

`stream_id + sequence` is the authoritative per-stream order. UTC timestamps describe time but do not replace sequence. Missing or repeated sequence values become visible data-quality events.

Clocks are separated into collector observation, optional source time and durable ingestion time. Clock regression fails closed. Payloads use canonical JSON and SHA-256. Provenance must state collector identity, version and `READ_ONLY` capture mode. Consumers reject unsupported versions and never infer missing required data.
