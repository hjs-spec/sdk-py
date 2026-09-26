# JEP Python SDK

Python client for **JEP Core 0.7**.

Current methods use the versioned 0.7 API contract:

```text
create_event() -> POST /v0.7/events/create
verify_event() -> POST /v0.7/events/verify
```

Explicit pre-0.7 compatibility is separate:

```text
create_legacy_event() -> POST /events/create
verify_legacy_event() -> POST /events/verify
```

No current-method failure triggers legacy fallback.

## Core 0.7 event model

`JEPEvent` contains stable `id` and does not contain a mandatory Core
nonce. Event Identity is `(who,id)`.

`LegacyJEPEvent` preserves the pre-0.7 nonce-bearing shape for explicit
compatibility work.

## Validation model

Current `ValidationResult` exposes:

- `status`: `valid | invalid | indeterminate`;
- independent `checks`;
- optional `event_identity`;
- optional `acceptance` with `accepted / already_accepted / rejected /
  indeterminate`.

The convenience `valid` property is true only when `status == "valid"`.

Legacy `valid + level` results use `LegacyValidationResult`.

## Example

```python
from jep import JEPClient, CreateEventRequest, VerifyEventRequest, Verb

client = JEPClient(base_url="http://127.0.0.1:8000")

created = client.create_event(CreateEventRequest(
    verb=Verb.JUDGMENT.value,
    who="did:example:agent",
    what={"claim": "approve-result"},
))

print(created.event.id)

result = client.verify_event(VerifyEventRequest(
    event=created.event,
    mode="acceptance",
))

print(result.status, result.acceptance)
```

Normative Core: https://github.com/hjs-spec/jep-core
