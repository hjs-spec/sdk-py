"""Basic usage for JEP Python SDK v0.6.

Run a local jep-api server first:

    uvicorn main:app --reload
"""

from jep import JEPClient, CreateEventRequest, Verb

client = JEPClient(base_url="http://127.0.0.1:8000")

created = client.create_event(CreateEventRequest(
    verb=Verb.JUDGMENT.value,
    who="did:example:agent-789",
    what={
        "claim": "approve",
        "subject": "demo",
    },
    aud="https://api.example.org",
))

print("event_hash:", created.event_hash)
print("valid:", created.validation.valid)

verified = client.verify_event({
    "event": created.event.to_dict(),
    "mode": "archival",
})

print("verification profile:", verified.profile)
