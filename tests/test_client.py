"""Tests for the JEP Python SDK against JEP Core 0.7."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from jep import (
    CreateEventRequest,
    JEPAPIError,
    JEPClient,
    JEPEvent,
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
                "what": payload["what"],
                "sig": "header..sig",
            }
            for key in ("aud", "ref", "ext", "ext_crit"):
                if payload.get(key) is not None:
                    event[key] = payload[key]
            self._json(200, {
                "event": event,
                "event_hash": "sha256:abc",
                "validation": {
                    "status": "valid",
                    "mode": "archival",
                    "profile": "jep-core-0.7",
                    "conformance_class": "JEP-Baseline-Ed25519-JWS-JCS-0.7",
                    "event_identity": {"who": event["who"], "id": event["id"]},
                    "checks": {"syntax": "pass", "cryptographic": "pass", "event_identity": "pass"},
                    "event_hash": "sha256:abc",
                    "warnings": [],
                    "errors": [],
                },
            })
            return
        if self.path == "/v0.7/events/verify":
            self._json(200, {
                "status": "valid",
                "mode": payload.get("mode", "archival"),
                "profile": "jep-core-0.7",
                "event_identity": {
                    "who": payload["event"]["who"],
                    "id": payload["event"]["id"],
                },
                "checks": {"syntax": "pass", "cryptographic": "pass", "event_identity": "pass"},
                "event_hash": "sha256:def",
                "acceptance": (
                    {"outcome": "accepted", "effect_applied": True}
                    if payload.get("mode") == "acceptance" else None
                ),
                "warnings": [],
                "errors": [],
            })
            return
        if self.path == "/events/verify-legacy":
            self._json(200, {"valid": True, "level": 1, "profile": "jep-core-0.6"})
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


def test_create_event_uses_v07(api_server):
    client = JEPClient(base_url=api_server)
    resp = client.create_event(CreateEventRequest(
        verb=Verb.JUDGMENT.value,
        who="did:example:agent",
        what={"claim": "approve"},
    ))
    assert resp.event_hash == "sha256:abc"
    assert resp.event.id
    assert resp.validation.status == "valid"
    assert resp.validation.valid is True


def test_verify_event_uses_v07_result(api_server):
    client = JEPClient(base_url=api_server)
    event = JEPEvent(
        jep="1",
        id="urn:uuid:00000000-0000-7000-8000-000000000002",
        verb="J",
        who="did:example:agent",
        when=123,
        what={"claim": "approve"},
        sig="header..sig",
    )
    result = client.verify_event(VerifyEventRequest(event=event, mode="acceptance"))
    assert isinstance(result, ValidationResult)
    assert result.status == "valid"
    assert result.profile == "jep-core-0.7"
    assert result.acceptance["outcome"] == "accepted"


def test_health(api_server):
    client = JEPClient(base_url=api_server)
    assert client.health().profile == "jep-core-0.7"


def test_verb_minimums():
    client = JEPClient()
    with pytest.raises(JEPValidationError):
        client.create_event({"verb": "D", "what": {"delegatee": "b"}})
    with pytest.raises(JEPValidationError):
        client.create_event({"verb": "T", "what": {"termination_scope": "x"}})
    with pytest.raises(JEPValidationError):
        client.create_event({"verb": "V", "ref": "x", "what": {"verification_scope": "syntax"}})


def test_explicit_legacy_path(api_server):
    client = JEPClient(base_url=api_server)
    result = client.verify_event_legacy({"event": {"jep": "1", "nonce": "legacy"}})
    assert result["profile"] == "jep-core-0.6"


def test_api_error(api_server):
    client = JEPClient(base_url=api_server)
    with pytest.raises(JEPAPIError):
        client._request("GET", "/missing", None)
