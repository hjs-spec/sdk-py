"""JEP Python SDK for JEP Core 0.7.

Default endpoints:
- POST /v0.7/events/create
- POST /v0.7/events/verify
- GET /health

Explicit legacy methods remain available for historical pre-0.7 artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from enum import Enum
from typing import Any, Dict, List, Optional
import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
JEP_WIRE_VERSION = "1"
JEP_CORE_PROFILE = "jep-core-0.7"
LEGACY_JEP_CORE_PROFILE = "jep-core-0.6"


class Verb(str, Enum):
    JUDGMENT = "J"
    DELEGATION = "D"
    TERMINATION = "T"
    VERIFICATION = "V"


@dataclass
class JEPEvent:
    jep: str
    id: str
    verb: str
    who: str
    when: int
    what: Any
    aud: Optional[str] = None
    ref: str | Dict[str, Any] | None = None
    ext: Optional[Dict[str, Any]] = None
    ext_crit: Optional[List[str]] = None
    sig: str | Dict[str, Any] | None = None
    _wire: Optional[Dict[str, Any]] = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JEPEvent":
        data = deepcopy(data)
        return cls(
            jep=data["jep"],
            id=data["id"],
            verb=data["verb"],
            who=data["who"],
            when=data["when"],
            what=data["what"],
            aud=data.get("aud"),
            ref=data.get("ref"),
            ext=data.get("ext"),
            ext_crit=data.get("ext_crit"),
            sig=data.get("sig"),
            _wire=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = deepcopy(self._wire) if self._wire is not None else {}
        for name in ("jep", "id", "verb", "who", "when", "what", "aud", "ref", "ext", "ext_crit", "sig"):
            value = getattr(self, name)
            if value is not None or name in data:
                data[name] = deepcopy(value)
        return data


@dataclass
class CreateEventRequest:
    verb: str
    what: Any
    id: Optional[str] = None
    who: Optional[str] = None
    aud: Optional[str] = None
    ref: str | Dict[str, Any] | None = None
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
        if self.id is not None:
            data["id"] = self.id
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
    expected_audience: Optional[str] = None
    max_age_seconds: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        event = self.event.to_dict() if isinstance(self.event, JEPEvent) else self.event
        data: Dict[str, Any] = {"event": event, "mode": self.mode}
        if self.expected_audience is not None:
            data["expected_audience"] = self.expected_audience
        if self.max_age_seconds is not None:
            data["max_age_seconds"] = self.max_age_seconds
        return data


@dataclass
class ValidationResult:
    status: str
    mode: str
    profile: str
    checks: Dict[str, str] = field(default_factory=dict)
    event_identity: Optional[Dict[str, str]] = None
    event_hash: Optional[str] = None
    acceptance: Optional[Dict[str, Any]] = None
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    conformance_class: str = ""

    @property
    def valid(self) -> bool:
        return self.status == "valid"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        return cls(
            status=data.get("status", "indeterminate"),
            mode=data.get("mode", ""),
            profile=data.get("profile", ""),
            checks=dict(data.get("checks") or {}),
            event_identity=data.get("event_identity"),
            event_hash=data.get("event_hash"),
            acceptance=data.get("acceptance"),
            warnings=list(data.get("warnings") or []),
            errors=list(data.get("errors") or []),
            conformance_class=data.get("conformance_class", ""),
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
        return cls(ok=data.get("ok") is True, profile=data.get("profile", ""))


class JEPAPIError(Exception):
    def __init__(self, status_code: int, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(f"JEP API error ({status_code}): {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload or {}


class JEPValidationError(ValueError):
    pass


class JEPClient:
    """Client for the JEP Core 0.7 reference API."""

    def __init__(self, api_key: str = "", base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "content-type": "application/json",
            "user-agent": "JEP-Python-SDK/0.7.1",
        })
        if api_key:
            self.session.headers.update({
                "authorization": f"Bearer {api_key}",
                "x-api-key": api_key,
            })

    def create_event(self, request: CreateEventRequest | Dict[str, Any]) -> EventResponse:
        payload = request.to_dict() if isinstance(request, CreateEventRequest) else request
        self._validate_create_payload(payload)
        data = self._request("POST", "/v0.7/events/create", payload)
        return EventResponse.from_dict(data)

    def verify_event(self, request: VerifyEventRequest | Dict[str, Any]) -> ValidationResult:
        payload = request.to_dict() if isinstance(request, VerifyEventRequest) else request
        if not payload.get("event"):
            raise JEPValidationError("event is required")
        data = self._request("POST", "/v0.7/events/verify", payload)
        return ValidationResult.from_dict(data)

    def create_event_legacy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit pre-0.7 compatibility path. No automatic fallback occurs."""
        return self._request("POST", "/events/create", payload)

    def verify_event_legacy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Explicit pre-0.7 compatibility path. No automatic fallback occurs."""
        if not payload.get("event"):
            raise JEPValidationError("event is required")
        return self._request("POST", "/events/verify-legacy", payload)

    def health(self) -> HealthResponse:
        data = self._request("GET", "/health", None)
        return HealthResponse.from_dict(data)

    def judgment(self, who: str, what: Any, **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.JUDGMENT.value, who=who, what=what, **kwargs))

    def delegation(self, who: str, what: Any, **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.DELEGATION.value, who=who, what=what, **kwargs))

    def termination(self, who: str, what: Any, ref: str | Dict[str, Any], **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.TERMINATION.value, who=who, what=what, ref=ref, **kwargs))

    def verification(self, who: str, what: Any, ref: str | Dict[str, Any], **kwargs: Any) -> EventResponse:
        return self.create_event(CreateEventRequest(verb=Verb.VERIFICATION.value, who=who, what=what, ref=ref, **kwargs))

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        response = self.session.request(method, self.base_url + path, json=payload, timeout=self.timeout)
        try:
            data = response.json()
        except ValueError:
            data = {"message": response.text}
        if not 200 <= response.status_code < 300:
            message = data.get("message") or data.get("detail") or data.get("error") or response.text
            raise JEPAPIError(response.status_code, message, data)
        return data

    def _validate_create_payload(self, payload: Dict[str, Any]) -> None:
        verb = payload.get("verb")
        if verb not in {"J", "D", "T", "V"}:
            raise JEPValidationError("verb must be J, D, T, or V")
        if "what" not in payload:
            raise JEPValidationError("what is required")
        what = payload["what"]
        if verb == "D":
            if not isinstance(what, dict) or "delegatee" not in what or "scope" not in what:
                raise JEPValidationError("D requires what.delegatee and what.scope")
        elif verb == "T":
            if "ref" not in payload or payload.get("ref") is None:
                raise JEPValidationError("T requires ref")
            if not isinstance(what, dict) or "termination_scope" not in what:
                raise JEPValidationError("T requires what.termination_scope")
        elif verb == "V":
            if "ref" not in payload or payload.get("ref") is None:
                raise JEPValidationError("V requires ref")
            if not isinstance(what, dict) or "verification_scope" not in what or "result" not in what:
                raise JEPValidationError("V requires what.verification_scope and what.result")
