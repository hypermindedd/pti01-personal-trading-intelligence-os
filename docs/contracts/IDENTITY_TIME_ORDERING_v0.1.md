# PTI.01 Identity, Time and Ordering Contract v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Identifiers
- event_id: globally unique immutable ULID-shaped identifier.
- stream_id: stable logical stream identity with no credentials or raw account number.
- source_instance_id: collector-process identity regenerated at restart.
- observation_id: event_id for RAW observations.
- trade_lifecycle_id: PTI pseudonymous correlation identity; never a broker mutation handle.
- object_lifecycle_id: PTI pseudonymous identity for an observed chart object across movement events.
- snapshot_id: immutable identity for a full-state or multi-timeframe snapshot.

Identifiers are correlations, not authority tokens.

## Time fields
- source_time_utc: optional source-supplied time.
- observed_at_utc: collector observation time.
- ingested_at_utc: durable admission time.
- produced_at_utc: DERIVED/MODEL production time only.

All are timezone-aware UTC. Original broker timezone metadata may be preserved separately, but never replaces UTC. Missing source time remains null; it is not inferred.

## Ordering
stream_id plus sequence is authoritative within a stream. Time does not repair sequence. Cross-stream order is a partial order established only by explicit causal/correlation links and bounded clock evidence.

## Precision
Tick and chart-interaction timestamps preserve source precision and collector precision separately. Rounding is a derived operation with a version and must not change RAW.

## Late and duplicate events
Late events remain visible and cannot silently rewrite an already reported boundary. Exact duplicate identity plus identical bytes is idempotent. Same identity with different bytes is a collision and quarantines both claims.
