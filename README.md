# JEP Python SDK — JEP Core 0.7

Python client for the current [JEP Core 0.7](https://github.com/hjs-spec/jep-core) reference API.

## Status

Experimental HTTP client. Event creation and verification run on the configured
API. Start the [local reference API](https://github.com/hjs-spec/jep-quickstart#start-a-local-api)
before running the examples below.

## Installation

```bash
pip install jep-sdk-py==0.7.0
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

## Legacy 0.6

Legacy handling is deliberately explicit:

```python
client.verify_event_legacy({
    "event": legacy_event,
    "mode": "archival",
})
```

Do not use a failed 0.7 validation as a signal to reinterpret an artifact as 0.6.

## Testing

From a source checkout:

```bash
pip install -e ".[dev]"
pytest -q
```

## Related repositories

- Core contract and implementation path: https://github.com/hjs-spec/jep-core#current-contract
- JEP API: https://github.com/hjs-spec/jep-api
- JavaScript SDK: https://github.com/hjs-spec/sdk-js
- Go SDK: https://github.com/hjs-spec/sdk-go

## License

MIT
