# PTI.01 W0 to W1 Interface Freeze v0.1

Status: DRAFT — review candidate only.

W1 may implement read-only collectors only after W0 lock. Until then this document defines a provisional dependency surface.

## Allowed W1 outputs
Versioned event envelopes for trade lifecycle, chart interaction, market tick/bar, multi-timeframe snapshots, collector health and reconciliation. W1 may append to RAW and sanitized operational evidence.

## Forbidden W1 surfaces
Order/position/account mutation APIs; chart-object mutation APIs; execution adapters; authorization or permit tokens; credential persistence in Git; MODEL inference presented as observation.

## Required interfaces before W1 readiness
- capability check returns allow/deny with default DENY;
- envelope validation before RAW admission;
- atomic append acknowledgement;
- source instance and sequence tracking;
- health/gap/restart events;
- read-only full-state snapshot for reconciliation;
- sanitized evidence exporter;
- explicit excluded-input policy;
- no dependency on TS.01 or TS.02.

## Gate
This interface is not frozen until independent review findings are resolved, all static gates pass on the final candidate, Evidence hashes match, and the HUMAN locks W0.
