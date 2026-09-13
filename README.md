# JEP Python SDK v0.6

Python client for the [JEP-Core-0.6](https://github.com/hjs-spec/jep-v06) API (wire version `"1"`). SDK release versions are separate from the protocol version. See the protocol repository for core semantics, profiles, and public drafts.

This SDK targets the current JEP API shape:

```text
POST /events/create
POST /events/verify
GET  /health
```

## Status

Experimental implementation seed.

This SDK does not define new JEP-Core semantics and does not determine legal liability, factual truth, regulatory compliance, or complete-log availability.

## Installation

```bash
pip install jep-sdk-py
```

For local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

Start the [local API](https://github.com/hjs-spec/jep-api#run-locally) before running this example. Verification uses that API's configured trusted keys.

```python
from jep import JEPClient, CreateEventRequest, Verb

client = JEPClient(base_url="http://127.0.0.1:8000")

created = client.create_event(CreateEventRequest(
    verb=Verb.JUDGMENT.value,
    who="did:example:agent-789",
    what={"claim": "approve"},
))

print(created.event_hash)

verified = client.verify_event({
    "event": created.event.to_dict(),
    "mode": "archival",
})

print(verified.valid)
```

## Core Types

- `Verb`
- `JEPEvent`
- `CreateEventRequest`
- `EventResponse`
- `VerifyEventRequest`
- `ValidationResult`
- `HealthResponse`

## API and helpers

The quickstart above demonstrates event creation and archival verification. The client also exposes helpers for the four verbs; see [client methods and types](jep/client.py) for signatures and options.

Claim fields and reference requirements are defined in the [Core-0.6 event schema](https://github.com/hjs-spec/jep-v06/blob/main/schemas/jep-event.schema.json). For an event reference, use the actual returned event hash.

### Health

```python
health = client.health()
```

## Validation results

Validation results preserve the API's `conformance_class` and diagnostic fields (`code`, `message`, `level`, `recoverable`). Older servers may omit the class; the SDK does not infer conformance.

## Testing

```bash
pytest -q
```

Tests use a local in-process HTTP server and do not require a live JEP API.

## Related Repositories

- JEP v0.6: https://github.com/hjs-spec/jep-v06
- JEP API v0.6: https://github.com/hjs-spec/jep-api
- HJS v0.5: https://github.com/hjs-spec/hjs-05
- JAC v0.5: https://github.com/hjs-spec/jac-agent-02

## License

MIT
