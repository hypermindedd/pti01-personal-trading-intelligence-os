# Security Policy

PTI.01 is fail-closed and read-only during observation and discovery phases.

## Never commit

- credentials, tokens, API keys, or `.env` files
- broker or account identifiers
- raw trading history with identifying metadata
- raw XAUUSD tick archives
- runtime SQLite, Parquet, or event-store databases
- unsanitized screenshots containing account details

Report any read-only boundary violation, secret exposure, raw-data commit, or broker mutation as a critical incident. Stop runtime work until evidence-backed containment and review are complete.
