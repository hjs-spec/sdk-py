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
