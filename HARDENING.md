# Implementation hardening — September 2026

Preserve signed event member presence through API response/request round trips.

## Changes

Explicit nulls, empty extension containers, structured references and unknown members are retained. Values are not coerced during decoding. A returned dictionary is a copy; deliberate field edits remain visible. Acceptance requests can send expected_audience. J judgments may use explicit null what.

## Validation

```sh
PYTHONPATH=. python -m pytest -q
```

## Compatibility and remaining limits

Existing `jep` imports remain. Agent SDK 2.0 uses `jep_agent` and can coexist with this package. Agent SDK 1.x still conflicts; upgrade it and follow its migration instructions to restore any files overwritten by an older shared installation.

## Follow-up hardening

Validation and health results only treat literal JSON true as success; strings such as "false" are not coerced to True. Serialization may preserve historical null values without claiming that they satisfy the current creation schema.
