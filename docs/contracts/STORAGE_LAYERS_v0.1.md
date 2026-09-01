# PTI.01 Storage Layer Contract v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## RAW
Immutable, append-only observations exactly as captured. Corrections are new reconciliation records; historical bytes are never overwritten. Each record carries schema version, provenance, sequence, timestamps, payload hash, and optional previous-record hash.

## DERIVED
Versioned features reproducible from identified RAW inputs. Every row carries derivation version, input IDs, input content hash, code commit, parameters, and produced-at time. A feature cannot overwrite RAW data.

## MODEL
Versioned interpretations, clusters, hypotheses, scores, calibrations and abstentions. Every output links to exact DERIVED inputs, model version, training window, evaluation window and uncertainty. Model output is never promoted to observation.

## Enforcement invariants
1. RAW is append-only and immutable.
2. DERIVED and MODEL use separate namespaces.
3. Every transformation is reproducible and provenance-complete.
4. Hash mismatch, missing lineage, schema failure or layer violation fails closed.
5. Reconciliation appends evidence of disagreement; it never rewrites history.
6. Git never stores raw ticks, account history, broker identifiers or runtime databases.
