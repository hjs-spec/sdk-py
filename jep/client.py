"""JEP Python SDK v0.6.

This SDK targets the JEP API v0.6 seed:

- POST /events/create
- POST /events/verify
- GET /health

It is an implementation seed and does not define new JEP-Core semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
JEP_WIRE_VERSION = "1"
JEP_CORE_PROFILE = "jep-core-0.6"


class Verb(str, Enum):
    JUDGMENT = "J"
    DELEGATION = "D"
    TERMINATION = "T"
    VERIFICATION = "V"


@dataclass
class JEPEvent:
    jep: str
    verb: str
    who: str
    when: int
    nonce: str
    what: Any = None
    aud: Optional[str] = None
    ref: Optional[str] = None
    ext: Optional[Dict[str, Any]] = None
    ext_crit: Optional[List[str]] = None
    sig: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JEPEvent":
        return cls(
            jep=data.get("jep", JEP_WIRE_VERSION),
            verb=data["verb"],
            who=data["who"],
            when=int(data["when"]),
            nonce=data["nonce"],
            what=data.get("what"),
            aud=data.get("aud"),
            ref=data.get("ref"),
            ext=data.get("ext"),
            ext_crit=data.get("ext_crit"),
            sig=data.get("sig"),
        )

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "jep": self.jep,
            "verb": self.verb,
            "who": self.who,
            "when": self.when,
            "nonce": self.nonce,
        }
        if self.what is not None:
            data["what"] = self.what
        if self.aud is not None:
            data["aud"] = self.aud
        if self.ref is not None:
            data["ref"] = self.ref
        if self.ext is not None:
            data["ext"] = self.ext
        if self.ext_crit is not None:
            data["ext_crit"] = self.ext_crit
        if self.sig is not None:
            data["sig"] = self.sig
        return data


@dataclass
class CreateEventRequest:
    verb: str
    what: Any
    who: Optional[str] = None
    aud: Optional[str] = None
    ref: Optional[str] = None
    ttl_minutes: Optional[int] = None
    digest_only_who: bool = False
    ext: Dict[str, Any] = field(default_factory=dict)
    ext_crit: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "verb": self.verb,
            "what": self.what,
            "digest_only_who": self.digest_only_who,
        }
        if self.who is not None:
            data["who"] = self.who
        if self.aud is not None:
            data["aud"] = self.aud
        if self.ref is not None:
            data["ref"] = self.ref
        if self.ttl_minutes is not None:
            data["ttl_minutes"] = self.ttl_minutes
        if self.ext:
            data["ext"] = self.ext
        if self.ext_crit:
            data["ext_crit"] = self.ext_crit
        return data


@dataclass
class VerifyEventRequest:
    event: JEPEvent | Dict[str, Any]
    mode: str = "archival"
    consume_nonce: bool = False

    def to_dict(self) -> Dict[str, Any]:
        event = self.event.to_dict() if isinstance(self.event, JEPEvent) else self.event
        return {
            "event": event,
            "mode": self.mode,
            "consume_nonce": self.consume_nonce,
        }


@dataclass
class ValidationResult:
    valid: bool
    level: int
    mode: str
    profile: str
    scopes: List[str] = field(default_factory=list)
    event_hash: Optional[str] = None
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        return cls(
            valid=bool(data.get("valid", False)),
            level=int(data.get("level", 0)),
            mode=data.get("mode", ""),
            profile=data.get("profile", ""),
            scopes=list(data.get("scopes") or []),
            event_hash=data.get("event_hash"),
            warnings=list(data.get("warnings") or []),
            errors=list(data.get("errors") or []),
        )


@dataclass
class EventResponse:
    event: JEPEvent
    event_hash: str
    validation: ValidationResult

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventResponse":
        return cls(
            event=JEPEvent.from_dict(data["event"]),
            event_hash=data["event_hash"],
            validation=ValidationResult.from_dict(data["validation"]),
        )


@dataclass
class HealthResponse:
    ok: bool
    profile: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthResponse":
        return cls(ok=bool(data.get("ok", False)), profile=data.get("profile", ""))


class JEPAPIError(Exception):
    def __init__(self, status_code: int, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(f"JEP API error ({status_code}): {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload or {}


class JEPValidationError(ValueError):
    pass


class JEPClient:
    """Client for JEP API v0.6 seed."""

    def __init__(self, api_key: str = "", base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "content-type": "application/json",
            "user-agent": "JEP-Python-SDK/0.6.0",
        })
        if api_key:
            self.session.headers.update({
                "authorization": f"Bearer {api_key}",
                "x-api-key": api_key,
            })

    def create_event(self, request: CreateEventRequest | Dict[str, Any]) -> EventResponse:
        payload = request.to_dict() if isinstance(request, CreateEventRequest) else request
        self._validate_create_payload(payload)
        data = self._request("POST", "/events/create", payload)
        return EventResponse.from_dict(data)

    def verify_event(self, request: VerifyEventRequest | Dict[str, Any]) -> ValidationResult:
        payload = request.to_dict() if isinstance(request, VerifyEventRequest) else request
        if not payload.get("event"):
            raise JEPValidationError("event is required")
        data = self._request("POST", "/events/verify", payload)
        return ValidationResult.from_dict(data)

    def health(self) -> HealthResponse:
        data = self._request("GET", "/health", None)
        return HealthResponse.from_dict(data)

    # Convenience helpers

    def judgment(self, who: str, what: Any, **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.JUDGMENT.value, who=who, what=what, **kwargs))

    def delegation(self, who: str, what: Any, **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.DELEGATION.value, who=who, what=what, **kwargs))

    def termination(self, who: str, what: Any, ref: Optional[str] = None, **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.TERMINATION.value, who=who, what=what, ref=ref, **kwargs))

    def verification(self, who: str, what: Any, ref: str, **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.VERIFICATION.value, who=who, what=what, ref=ref, **kwargs))

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        response = self.session.request(
            method,
            self.base_url + path,
            json=payload,
            timeout=self.timeout,
        )
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text}

        if not 200 <= response.status_code < 300:
            message = data.get("message") or data.get("error") or response.text
            raise JEPAPIError(response.status_code, message, data)

        return data

    def _validate_create_payload(self, payload: Dict[str, Any]) -> None:
        if payload.get("verb") not in {"J", "D", "T", "V"}:
            raise JEPValidationError("verb must be J, D, T, or V")
        if "what" not in payload or payload.get("what") is None:
            raise JEPValidationError("what is required")
