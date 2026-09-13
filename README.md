# JEP Python SDK v0.6

Python client for the JEP-Core-0.6 API (wire version `"1"`). SDK release versions are separate from the protocol version.

This SDK targets the current JEP API shape:

```text
POST /events/create
POST /events/verify
GET  /health
```

It is aligned with:

- `draft-wang-jep-judgment-event-protocol-06`
- `draft-wang-jep-profiles-00`
- `draft-wang-jep-conformance-00`
- `hjs-spec/jep-api`

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

- `JEPEvent`
- `CreateEventRequest`
- `EventResponse`
- `VerifyEventRequest`
- `ValidationResult`
- `HealthResponse`

Supported verbs:

```python
Verb.JUDGMENT
Verb.DELEGATION
Verb.TERMINATION
Verb.VERIFICATION
```

## API and helpers

The quickstart above demonstrates event creation and archival verification. The client also exposes helpers for the four verbs; see [client methods and types](jep/client.py) for signatures and options.

For object-form `what`, `D` requires a claim, delegatee, and scope; `T` requires a claim, target, and termination scope; `V` requires a verification scope and non-null reference. Digest-form claims are also supported. Use the actual returned event hash for an event reference. See the [event schema](https://github.com/hjs-spec/jep-v06/blob/main/schemas/jep-event.schema.json) for the full requirements.

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

## Public Drafts

- JEP-Core: https://datatracker.ietf.org/doc/draft-wang-jep-judgment-event-protocol/
- JEP-Profiles: https://datatracker.ietf.org/doc/draft-wang-jep-profiles/
- JEP-Conformance: https://datatracker.ietf.org/doc/draft-wang-jep-conformance/

## License

MIT
