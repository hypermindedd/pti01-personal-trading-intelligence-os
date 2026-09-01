# PTI.01 Failure and Reconciliation Contract v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Failure states
Every stream tracks HEALTHY, DEGRADED, GAP_DETECTED, RECONCILING, INCOMPLETE and QUARANTINED. Silence is never interpreted as completeness.

## Detection
A failure is observable when sequence is missing/repeated/regressed, payload or chain hash fails, schema/provenance is invalid, source or collector clock regresses, a restart boundary appears, a full-state snapshot disagrees with replay, or a partial durable write is detected.

## Reconciliation
1. Freeze definitive downstream claims for affected boundaries.
2. Append a quality.gap.detected event containing affected stream, expected/observed sequence, detection time and reason.
3. Obtain a read-only full-state snapshot when available.
4. Append quality.reconciliation.recorded with comparison method, snapshot ID, replay boundary, discrepancies and disposition.
5. Never edit, delete or reorder RAW.
6. Resume HEALTHY only from a new explicit completeness boundary.

## Dispositions
- MATCH: replay and snapshot agree.
- EXPLAINED_DELTA: discrepancy is attributable to a recorded observation boundary.
- UNEXPLAINED_DELTA: evidence remains incomplete.
- SOURCE_UNAVAILABLE: reconciliation cannot run.
- HASH_OR_SCHEMA_FAILURE: affected records remain quarantined.

No disposition may manufacture missing observations. UNEXPLAINED_DELTA, SOURCE_UNAVAILABLE and HASH_OR_SCHEMA_FAILURE prohibit definitive latent-rule or edge claims for affected samples.

## Crash and partial-write rule
Durability acknowledgement occurs only after the complete envelope is atomically committed. A crash before acknowledgement permits retry using the same event identity; duplicate detection must be idempotent. A crash after acknowledgement must not create a second logical event.

## Restart rule
Collector restart creates a new source_instance_id and an explicit restart boundary. Sequence policy must be declared per stream; it may continue monotonically or begin a new stream identity, but it may never silently reset.
