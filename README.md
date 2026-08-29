# PTI.01 | Personal Trading Intelligence OS

Read-only, evidence-driven personal trading intelligence for MetaTrader 5.

## Current status

`W0 — IN PROGRESS`

Repository bootstrap is complete. Architecture, safety, and data contracts are under construction. No runtime, collection, analysis, trading, or broker-mutation capability is claimed.

## Hard boundary

PTI.01 is independent from TS.01 and TS.02. No evidence, lock, canonical parent, state, code, or architectural assumption may silently cross into this repository.

Initial phases are strictly read-only. PTI.01 must never open, close, modify, or cancel orders or positions, and must never mutate broker/account state.

## Mission

Observe and reconstruct the trader's real decision process across trade lifecycle events, chart objects and manual line movement, multi-timeframe state, XAUUSD M1 ticks and microstructure, gaps, FVGs, liquidity voids, execution conditions, management, MAE/MFE, exit quality, and post-trade outcomes.

Latent rules are discovered from observed behavior without requiring the trader to pre-label or explain them.

## Epistemic separation

- Repeated behavior is not automatically an inferred rule.
- An inferred rule is not automatically a profitable edge.
- A profitable edge requires evidence, statistical validation, regime robustness, temporal separation, and out-of-sample support.

## Source-of-truth boundaries

- GitHub: code, schemas-as-code, tests, immutable version history.
- Notion: governance, requirements, roadmap, decisions, management views.
- Runtime evidence store: raw observations, replay evidence, and gates.
- Raw trading and tick datasets are forbidden in Git.

## Active wave

`W0 — Architecture, Safety & Data Contracts`
