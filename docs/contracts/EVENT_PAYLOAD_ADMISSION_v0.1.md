# PTI.01 Event-Type and Payload Admission Contract v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

## Default deny
The generic envelope does not admit arbitrary payload semantics. An event enters RAW only when its event type is ACTIVE in the versioned registry and every required payload field is present. Unknown, RESERVED and forbidden event types fail closed.

## Epistemic class
Every active event type declares one class:
- OBSERVED: externally observed state or transition.
- QUALITY: evidence about capture, completeness or reconciliation.
- DERIVED: reproducible calculation from identified RAW parents.
- MODEL: interpretation or hypothesis; never an observation.

W0 v0.1 activates only OBSERVED and QUALITY envelope types. DERIVED and MODEL payload families require separate future contracts.

## Reserved types
RESERVED means the name is held for architecture continuity but is not admissible. Reservation is not implementation, evidence or runtime authority.

## Payload rules
1. Required fields are checked before RAW admission.
2. Missing fields are not inferred or defaulted.
3. Null does not satisfy a required field unless the future payload schema explicitly permits it.
4. Numeric market values may be represented losslessly as decimal strings; rounding is derived.
5. IDs are pseudonymous correlations and never broker mutation handles.
6. A payload hash proves bytes, not semantic validity; both checks are required.
7. Event registry version and envelope schema version are recorded independently when they diverge in the future.

## Change control
Activating a reserved type or changing required fields requires a new registry version, compatibility decision, tests, Evidence and W0/W1 authority appropriate to the phase.
