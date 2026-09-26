# JEP Python SDK — JEP Core 0.7

Python client for the current [JEP Core 0.7](https://github.com/hjs-spec/jep-core) reference API.

The default client uses:

```text
POST /v0.7/events/create
POST /v0.7/events/verify
GET  /health
```

Historical pre-0.7 compatibility is explicit through `create_event_legacy()` and
`verify_event_legacy()`. The SDK never retries a failed 0.7 event as 0.6.

## Status

Experimental reference SDK. It does not define new JEP Core semantics and
does not determine legal liability, factual truth, authorization validity,
regulatory compliance, causality, or policy outcome.

## Installation

```bash
pip install jep-sdk-py
```

For local development:

```bash
pip install -e ".[dev]"
```

## Quick start

```python
from jep import JEPClient, CreateEventRequest, Verb

client = JEPClient(base_url="http://127.0.0.1:8000")

created = client.create_event(CreateEventRequest(
    verb=Verb.JUDGMENT.value,
    who="did:example:agent-789",
    what={"claim": "approve"},
))

verified = client.verify_event({
    "event": created.event.to_dict(),
    "mode": "archival",
})

print(created.event.id)
print(created.event_hash)
print(verified.status, verified.checks)
```

## JEP Core 0.7 model

- Event Identity is `(who,id)`.
- `id` is required; Core does not require a top-level nonce.
- Event Hash identifies one exact signed artifact and is not Event Identity.
- Validation uses independent checks rather than cumulative Validation Levels.
- Acceptance mode can return `accepted` or `already_accepted`.
- D requires `what.delegatee` and `what.scope`.
- T requires `ref` and `what.termination_scope`.
- V requires `ref`, `what.verification_scope`, and `what.result`.

The normative schema lives in [jep-core](https://github.com/hjs-spec/jep-core/blob/main/schemas/jep-event.schema.json).

## Legacy 0.6

Legacy handling is deliberately explicit:

```python
client.verify_event_legacy({
    "event": legacy_event,
    "mode": "archival",
})
```

Do not use a failed 0.7 validation as a signal to reinterpret an artifact as 0.6.

## Validation results

Current results expose:

- `status`: `valid | invalid | indeterminate`
- `checks`: independent check results
- `event_identity`
- `event_hash`
- optional `acceptance`
- `warnings` / `errors`

`ValidationResult.valid` is a convenience property equivalent to
`status == "valid"`.

## Testing

```bash
pytest -q
```

## Related repositories

- JEP Core 0.7: https://github.com/hjs-spec/jep-core
- JEP API: https://github.com/hjs-spec/jep-api
- JavaScript SDK: https://github.com/hjs-spec/sdk-js
- Go SDK: https://github.com/hjs-spec/sdk-go

## License

MIT
