import json
import pytest
from jep import JEPEvent, VerifyEventRequest


@pytest.mark.parametrize("ref", [None, {"type": "event", "value": "sha256:" + "a" * 64}])
def test_signed_wire_members_survive_roundtrip(ref):
    wire = {"jep": "1", "verb": "J", "who": "agent", "when": 123,
            "nonce": "n", "what": None, "ref": ref, "ext": {},
            "ext_crit": [], "sig": "header..signature", "future": {"x": 1}}
    event = JEPEvent.from_dict(wire)
    assert VerifyEventRequest(event).to_dict()["event"] == wire
    wire["future"]["x"] = 2
    assert event.to_dict()["future"]["x"] == 1
    event.who = "changed"
    assert event.to_dict()["who"] == "changed"


def test_roundtrip_does_not_coerce_signed_values():
    wire = {"jep": "1", "verb": "J", "who": "agent", "when": "123", "nonce": "n", "sig": "s"}
    assert JEPEvent.from_dict(wire).to_dict() == wire


def test_invalid_result_type_cannot_become_success():
    from jep.client import ValidationResult, HealthResponse
    assert not ValidationResult.from_dict({"valid": "false"}).valid
    assert not HealthResponse.from_dict({"ok": "false"}).ok


def test_result_retains_conformance_and_diagnostics_with_old_server_compatibility():
    from jep import ValidationResult
    diagnostic = {"code": "ACCEPTANCE_NOT_CHECKED", "message": "archival", "level": 1, "recoverable": False}
    result = ValidationResult.from_dict({"valid": True, "level": 1, "mode": "archival",
        "profile": "jep-core-0.6", "conformance_class": "JEP-Baseline-Ed25519-JWS-JCS-0.6",
        "warnings": [diagnostic]})
    assert result.conformance_class == "JEP-Baseline-Ed25519-JWS-JCS-0.6"
    assert result.warnings == [diagnostic]
    assert ValidationResult.from_dict({"valid": True}).conformance_class == ""
    # Existing positional construction still assigns the fifth argument to scopes.
    assert ValidationResult(True, 1, "archival", "jep-core-0.6", ["syntax"]).scopes == ["syntax"]
