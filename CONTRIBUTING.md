# Contributing

## Authority

Human approval is required for canonical locks, authority changes, scope changes, and any future broker-mutation boundary.

## Workflow

- Use `wXX/<scope>` branches.
- Commit format: `PTI01 W<n>: <imperative change>`.
- Derive clean candidates from the latest accepted parent.
- Do not promote failed candidates or use patch-on-patch ancestry after a failed gate.
- Merge only after the active wave's required tests and evidence pass.
- Never claim PASS without evidence.
