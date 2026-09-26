"""Tests for JEP Python SDK current 0.7 and explicit legacy compatibility."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from jep import (
    CreateEventRequest,
    JEPAPIError,
    JEPClient,
    JEPEvent,
    LegacyJEPEvent,
    LegacyVerifyEventRequest,
    JEPValidationError,
    ValidationResult,
    VerifyEventRequest,
    Verb,
)


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True, "profile": "jep-core-0.7"})
        else:
            self._json(404, {"message": "not found"})

    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/v0.7/events/create":
            event = {
                "jep": "1",
                "id": payload.get("id", "urn:uuid:00000000-0000-7000-8000-000000000001"),
                "verb": payload["verb"],
                "who": payload.get("who", "did:example:agent"),
                "when": 1234567890,
                "what": payload.get("what"),
                "sig": "header..sig",
            }
            for name in ("aud", "ref", "ext", "ext_crit"):
                if payload.get(name) is not None:
                    event[name] = payload[name]
            self._json(200, {
                "event": event,
                "event_hash": "sha256:abc",
                "validation": {
                    "status": "valid",
                    "mode": "archival",
                    "profile": "jep-core-0.7",
                    "checks": {"syntax": "pass", "cryptographic": "pass", "event_identity": "pass"},
                    "event_hash": "sha256:abc",
                    "warnings": [],
                    "errors": [],
                }
            })
            return

        if self.path == "/v0.7/events/verify":
            self._json(200, {
                "status": "valid",
                "mode": payload.get("mode", "archival"),
                "profile": "jep-core-0.7",
                "checks": {"syntax": "pass", "cryptographic": "pass", "event_identity": "pass"},
                "event_hash": "sha256:def",
                "warnings": [],
                "errors": [],
            })
            return

        if self.path == "/events/verify":
            self._json(200, {
                "valid": True,
                "level": 1,
                "mode": payload.get("mode", "archival"),
                "profile": "jep-core-0.6",
                "scopes": ["syntax"],
                "event_hash": "sha256:legacy",
                "warnings": [],
                "errors": [],
            })
            return

        self._json(404, {"message": "not found"})

    def log_message(self, *args):
        pass


@pytest.fixture()
def api_server():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()


def test_create_event(api_server):
    client = JEPClient(base_url=api_server)
    resp = client.create_event(CreateEventRequest(
        verb=Verb.JUDGMENT.value,
        who="did:example:agent",
        what={"claim": "approve"},
    ))
    assert resp.event_hash == "sha256:abc"
    assert resp.event.id.startswith("urn:uuid:")
    assert resp.validation.status == "valid"


def test_verify_event(api_server):
    client = JEPClient(base_url=api_server)
    event = JEPEvent(
        jep="1",
        id="urn:uuid:00000000-0000-7000-8000-000000000001",
        verb="J",
        who="did:example:agent",
        when=123,
        what={"claim": "approve"},
        sig="header..sig",
    )
    result = client.verify_event(VerifyEventRequest(event=event, mode="archival"))
    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.status == "valid"
    assert result.profile == "jep-core-0.7"


def test_health(api_server):
    client = JEPClient(base_url=api_server)
    health = client.health()
    assert health.ok is True
    assert health.profile == "jep-core-0.7"


def test_convenience_helpers(api_server):
    client = JEPClient(base_url=api_server)
    assert client.judgment("agent", "judge").event.verb == "J"
    assert client.delegation("agent", {"delegatee": "b", "scope": {"task": "x"}}).event.verb == "D"
    ref = {"type": "jep:event", "value": {"who": "agent", "id": "urn:uuid:x"}}
    assert client.termination("agent", {"termination_scope": "future"}, ref=ref).event.verb == "T"
    assert client.verification("agent", {"verification_scope": ["cryptographic"], "result": "pass"}, ref=ref).event.verb == "V"


def test_explicit_legacy_verify(api_server):
    client = JEPClient(base_url=api_server)
    event = LegacyJEPEvent(jep="1", verb="J", who="a", when=1, nonce="n", what={"claim": "x"}, sig="h..s")
    result = client.verify_legacy_event(LegacyVerifyEventRequest(event))
    assert result.valid
    assert result.profile == "jep-core-0.6"


def test_validation_errors():
    client = JEPClient()
    with pytest.raises(JEPValidationError):
        client.create_event({"verb": "X", "what": "x"})
    with pytest.raises(JEPValidationError):
        client.create_event({"verb": "J"})


def test_api_error(api_server):
    client = JEPClient(base_url=api_server)
    with pytest.raises(JEPAPIError):
        client._request("GET", "/missing", None)
