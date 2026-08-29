# ADR-0001 — Fail-closed read-only observer boundary

Status: PROPOSED

PTI.01 W0 defines a default-deny capability boundary. Only named observation, snapshot, append-only persistence, derivation and replay capabilities are allowed. All broker/account and chart-object mutation capabilities are explicitly denied. Unknown capabilities are denied, and no execution adapter, authorization token, order API wrapper or broker mutation interface exists in W0/W1 contracts.
