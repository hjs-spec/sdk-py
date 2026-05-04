"""Tests for JEP Python SDK v0.6."""

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
            self._json(200, {"ok": True, "profile": "jep-core-0.6"})
        else:
            self._json(404, {"message": "not found"})

    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")

        if self.path == "/events/create":
            event = {
                "jep": "1",
                "verb": payload["verb"],
                "who": payload.get("who", "did:example:agent"),
                "when": 1234567890,
                "what": payload.get("what"),
                "nonce": "nonce-1",
                "aud": payload.get("aud"),
                "ref": payload.get("ref"),
                "ext": payload.get("ext"),
                "ext_crit": payload.get("ext_crit"),
                "sig": "header..sig",
            }
            self._json(200, {
                "event": event,
                "event_hash": "sha256:abc",
                "validation": {
                    "valid": True,
                    "level": 1,
                    "mode": "archival",
                    "profile": "jep-core-0.6",
                    "scopes": ["syntax", "cryptographic"],
                    "event_hash": "sha256:abc",
                    "warnings": [],
                    "errors": [],
                }
            })
            return

        if self.path == "/events/verify":
            self._json(200, {
                "valid": True,
                "level": 1,
                "mode": payload.get("mode", "archival"),
                "profile": "jep-core-0.6",
                "scopes": ["syntax"],
                "event_hash": "sha256:def",
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
    assert resp.event.verb == "J"
    assert resp.validation.valid is True


def test_verify_event(api_server):
    client = JEPClient(base_url=api_server)
    event = JEPEvent(
        jep="1",
        verb="J",
        who="did:example:agent",
        when=123,
        what="sha256:abc",
        nonce="nonce-1",
        sig="header..sig",
    )
    result = client.verify_event(VerifyEventRequest(event=event, mode="archival"))
    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.profile == "jep-core-0.6"


def test_health(api_server):
    client = JEPClient(base_url=api_server)
    health = client.health()
    assert health.ok is True
    assert health.profile == "jep-core-0.6"


def test_convenience_helpers(api_server):
    client = JEPClient(base_url=api_server)
    assert client.judgment("agent", "judge").event.verb == "J"
    assert client.delegation("agent", "delegate").event.verb == "D"
    assert client.termination("agent", "terminate", ref="sha256:parent").event.verb == "T"
    assert client.verification("agent", "verify", ref="sha256:parent").event.verb == "V"


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
