# PTI.01 Latent Rule and Edge Epistemics Contract v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Purpose
PTI discovers possible trading rules from behavior without requiring the trader to explain or label them.

## Mandatory classes
1. REPEATED_BEHAVIOR: a recurring measurable sequence supported by identified observations. It makes no rule or edge claim.
2. INFERRED_RULE: a falsifiable conditional hypothesis linking context, interaction and decision. It must include alternatives, confidence and counterexamples.
3. VALIDATED_EDGE: an inferred rule that passes predeclared out-of-sample statistical and operational gates.

No class may be silently promoted to another.

## Minimum evidence
Every output links to exact RAW and DERIVED inputs, feature and model versions, observation window, sample count, missingness, market regime, instrument/symbol mapping and uncertainty.

## Leakage controls
Features at decision time may use only information available at or before that boundary. Exit, MAE/MFE and post-exit outcomes are labels/evaluation inputs and cannot leak into pre-entry features.

## Validation discipline
Validated edge requires a frozen hypothesis before evaluation; separated discovery and evaluation windows; effective sample size; uncertainty interval; multiple-testing control; stability across time/regime; transaction-cost and execution-sensitivity analysis; and explicit abstention when evidence is insufficient.

The first 50–100 trades may support candidate discovery and instrumentation diagnostics. They do not automatically prove edge. Thresholds are declared before each validation study and may become stricter as hypothesis count grows.

## Confounding
PTI records correlated context and alternative explanations. Repeated behavior is not assumed causal. A model score is not evidence unless calibrated against held-out outcomes.

## Revocation
Every edge claim is versioned and monitored for drift. Failed stability or calibration creates a superseding revocation record; historical evidence is retained.
