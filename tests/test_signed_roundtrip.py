import pytest
from jep import JEPEvent, VerifyEventRequest, ValidationResult


@pytest.mark.parametrize("ref", [
    None,
    {
        "type": "jep:event",
        "value": {"who": "did:example:b", "id": "urn:uuid:00000000-0000-7000-8000-000000000002"},
        "hash": "sha256:" + "a" * 64,
    },
])
def test_v07_signed_wire_members_survive_roundtrip(ref):
    wire = {
        "jep": "1",
        "id": "urn:uuid:00000000-0000-7000-8000-000000000001",
        "verb": "J",
        "who": "did:example:a",
        "when": 123,
        "what": {"claim": "approve"},
        "sig": "header..signature",
    }
    if ref is not None:
        wire["ref"] = ref
    event = JEPEvent.from_dict(wire)
    assert VerifyEventRequest(event).to_dict()["event"] == wire
    event.who = "did:example:changed"
    assert event.to_dict()["who"] == "did:example:changed"


def test_v07_result_retains_checks_and_diagnostics():
    diagnostic = {
        "code": "ERR_SIGNATURE_INVALID",
        "message": "bad signature",
        "check": "cryptographic",
        "recoverable": False,
    }
    result = ValidationResult.from_dict({
        "status": "invalid",
        "mode": "archival",
        "profile": "jep-core-0.7",
        "conformance_class": "JEP-Baseline-Ed25519-JWS-JCS-0.7",
        "event_identity": {"who": "did:example:a", "id": "urn:uuid:1"},
        "checks": {"syntax": "pass", "cryptographic": "fail"},
        "warnings": [],
        "errors": [diagnostic],
    })
    assert result.valid is False
    assert result.checks["cryptographic"] == "fail"
    assert result.errors == [diagnostic]
    assert result.conformance_class == "JEP-Baseline-Ed25519-JWS-JCS-0.7"


def test_legacy_payload_is_not_silently_decoded_as_v07():
    wire = {
        "jep": "1",
        "verb": "J",
        "who": "agent",
        "when": 123,
        "nonce": "legacy-nonce",
        "what": {"claim": "legacy"},
        "sig": "header..signature",
    }
    with pytest.raises(KeyError):
        JEPEvent.from_dict(wire)
