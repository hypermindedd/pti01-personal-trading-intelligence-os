# PTI.01 Canonical Serialization v0.1

Status: DRAFT — W0 candidate; not canonical and not locked.

Before hashing, every string value and object key is normalized to Unicode NFC.
Objects are serialized as UTF-8 JSON with lexicographically sorted keys, compact
separators, and non-ASCII characters preserved. `NaN`, positive infinity and
negative infinity are forbidden. The algorithm identifier is `PTI01-CJSON-NFC-0.1`.
