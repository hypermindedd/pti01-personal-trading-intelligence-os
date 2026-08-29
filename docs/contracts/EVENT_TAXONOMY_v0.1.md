# PTI.01 Event Taxonomy v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Event families
### Trade lifecycle
trade.transaction.observed, trade.state.snapshot, trade.intent_proxy.observed, trade.entry.observed, trade.management.observed, trade.exit.observed, trade.post_exit.observed.

An intent proxy is an observed action such as line placement/movement or chart interaction. It is not a claim about mental intent.

### Chart interaction
chart.object.observed, chart.object.created_observed, chart.object.moved_observed, chart.object.deleted_observed, chart.state.snapshot.

Names describe observed external state transitions. PTI never creates, moves or deletes the object.

### Market and multi-timeframe
market.tick.observed, market.bar.observed, market.state.snapshot, market.mtf.snapshot, market.microstructure.snapshot.

### Structure and discontinuity
market.gap.observed, market.fvg.derived, market.liquidity_void.derived.

Observed and derived concepts must not share an epistemic class. FVG and liquidity-void definitions require versioned derivation parameters.

### Quality and operations
quality.gap.detected, quality.reconciliation.recorded, collector.started, collector.stopped, collector.heartbeat, collector.degraded.

## Minimum lifecycle coverage
A reconstructable trade sample links pre-entry context, entry, every management change, exit, MAE/MFE calculation inputs, exit-quality window and post-exit outcome window. Missing segments are explicit completeness flags.

## Payload discipline
Each event type owns a versioned payload schema. The generic envelope does not authorize arbitrary semantic payloads. Unknown event types or unsupported payload versions fail closed.
