import pytest
from jep import JEPEvent, LegacyJEPEvent, VerifyEventRequest


@pytest.mark.parametrize("ref", [None, {"type": "jep:event", "value": {"who": "a", "id": "urn:uuid:b"}}])
def test_signed_wire_members_survive_roundtrip(ref):
    wire = {
        "jep": "1", "id": "urn:uuid:a", "verb": "J", "who": "agent",
        "when": 123, "what": {"claim": "x"}, "ref": ref, "ext": {},
        "ext_crit": [], "sig": "header..signature",
    }
    event = JEPEvent.from_dict(wire)
    assert VerifyEventRequest(event).to_dict()["event"] == wire
    wire["what"]["claim"] = "changed-outside"
    assert event.to_dict()["what"]["claim"] == "x"
    event.who = "changed"
    assert event.to_dict()["who"] == "changed"


def test_current_event_does_not_gain_nonce():
    event = JEPEvent(jep="1", id="urn:uuid:a", verb="J", who="a", when=1, what={"claim":"x"}, sig="s")
    assert "nonce" not in event.to_dict()


def test_legacy_event_preserves_nonce():
    wire = {"jep":"1","verb":"J","who":"a","when":1,"nonce":"n","what":{"claim":"x"},"sig":"s"}
    assert LegacyJEPEvent.from_dict(wire).to_dict() == wire


def test_invalid_status_cannot_become_success():
    from jep.client import ValidationResult, HealthResponse
    assert not ValidationResult.from_dict({"status": "invalid"}).valid
    assert not HealthResponse.from_dict({"ok": "false"}).ok


def test_result_retains_07_metadata_and_acceptance():
    from jep import ValidationResult
    result = ValidationResult.from_dict({
        "status":"valid","mode":"acceptance","profile":"jep-core-0.7",
        "conformance_class":"JEP-Baseline-Ed25519-JWS-JCS-0.7",
        "checks":{"syntax":"pass"},
        "acceptance":{"outcome":"already_accepted","effect_applied":False},
        "warnings":[],"errors":[]
    })
    assert result.valid
    assert result.checks["syntax"] == "pass"
    assert result.acceptance["outcome"] == "already_accepted"
