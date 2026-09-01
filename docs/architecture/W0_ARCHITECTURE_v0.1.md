# PTI.01 W0 Architecture v0.1

Status: DRAFT — clean W0 candidate; not canonical and not locked.

## Authority and isolation
Explicit HUMAN decisions are highest authority. PTI.01 is hard-isolated from TS.01 and TS.02. No code, evidence, lock, parent, state or architectural assumption may cross into PTI.01 without explicit human admission and recorded provenance.

The existing agent agreement is sufficient: CHATGPT/CHIEF owns implementation and registry writes; CLAUDE/WARDEN may independently review, critique and propose through the governed queue. Claude cannot create or acknowledge a canonical lock.

## Components
Collectors observe MT5; the envelope builder adds identity, sequence, clocks, schema, integrity and provenance; RAW storage appends observations; the reconciler appends discrepancies; replay reconstructs deterministic state; DERIVED computes versioned features; MODEL records interpretations without modifying evidence.

## Non-observation boundary
No component may send, modify or cancel orders; open, close or modify positions; change account settings; or create, modify or delete chart objects. Unknown capabilities fail closed.

## Event families fixed for W1
- `trade.transaction.observed`
- `trade.state.snapshot`
- `chart.object.observed`
- `chart.state.snapshot`
- `market.tick.observed`
- `market.bar.observed`
- `market.state.snapshot`
- `quality.gap.detected`
- `quality.reconciliation.recorded`

## Replay invariants
Same ordered valid events and logic version produce equivalent canonical state. Future events cannot influence earlier boundaries. Gaps, duplicates, hash failures and clock regressions remain visible. Reconciliation never mutates RAW. Incomplete replay cannot support definitive rule claims.

## W0 exit gate
W0 may become `READY_FOR_GATE` only after schema, policy, storage, isolation and deterministic tests plus a sanitized evidence manifest pass. Human lock remains separate.
