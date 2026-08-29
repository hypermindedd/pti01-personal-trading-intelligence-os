# PTI.01 Event Envelope v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Ordering
`stream_id + sequence` is the authoritative per-stream order. UTC timestamps describe time but do not replace sequence. Missing, repeated or regressed sequence values become visible data-quality events.

## Clocks
Clocks are separated into collector observation, optional source time and durable ingestion time. Clock regression fails closed. Source time remains null when unavailable and is never inferred.

## Independent versions
- `schema_version`: generic envelope structure.
- `event_registry_version`: active/reserved/forbidden event-type registry.
- `payload_schema_version`: semantic payload admission rules for the selected type.
- `collector_version`: producing collector implementation.

All required versions are checked independently. Compatibility in one layer never implies compatibility in another.

## Integrity and provenance
Payloads use canonical JSON and SHA-256. Provenance states collector identity, collector version and `READ_ONLY` capture mode. Consumers reject unsupported versions and never infer missing required data.

## Semantic admission
A valid payload hash is necessary but insufficient. The event type must be ACTIVE and the payload must satisfy its type-specific required fields before RAW admission. RESERVED, forbidden and unknown types fail closed.

## Authority
The envelope carries evidence and correlation only. No identifier, version, source value or provenance field is an authorization token or broker/chart mutation handle.
