# PTI.01 Threat Model v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Safety objective
PTI.01 observes and records. It must never mutate broker, account, order, position, terminal setting or chart-object state during read-only phases.

## Trust boundaries
1. MT5 terminal and broker feeds are external observation sources, not authorities over PTI state.
2. Collector input is untrusted until envelope, provenance, sequence, clock and hash validation succeeds.
3. RAW is an immutable evidence boundary.
4. DERIVED and MODEL are untrusted interpretations relative to RAW.
5. Git and documentation stores must never contain runtime account data, credentials, raw tick archives or broker identifiers.
6. TS.01 and TS.02 are foreign projects and untrusted as PTI.01 inputs unless the HUMAN explicitly admits a named artifact with provenance.

## Threats and required response
| Threat | Required response |
|---|---|
| Hidden broker/chart mutation capability | Deny startup and emit sanitized safety evidence |
| Unknown capability or event version | Fail closed; do not infer |
| Missing provenance or invalid payload hash | Reject before RAW admission |
| Duplicate, gap or out-of-order stream sequence | Preserve anomaly; block definitive replay claims |
| Collector crash, reconnect or partial write | Append restart/reconciliation records; never overwrite RAW |
| Clock regression or ambiguous timezone | Reject boundary-sensitive interpretation |
| DERIVED/MODEL contaminates RAW | Block write and record layer violation |
| Model hypothesis presented as fact | Require epistemic class and supporting evidence IDs |
| Cross-project state contamination | Fail closed and record blocking isolation defect |
| Excluded image enters any input | Reject ingestion and record policy violation |
| Credentials or account identifiers enter Git/evidence | Sanitize, fail the gate and rotate affected secret outside PTI |

## Abuse cases
Forbidden even if technically possible: order send/modify/cancel; position open/close/modify; account setting change; chart object create/modify/delete; simulated user input that causes such mutation; DLL, shell, network or adapter side-channel that crosses into mutation; importing an execution authority from another project.

## Claim discipline
Static checks prove only the named static surface. Runtime, Real-MT5, completeness, statistical edge, canonical state and lock require separate evidence and authority.
