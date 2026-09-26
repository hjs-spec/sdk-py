"""JEP Python SDK for JEP Core 0.7.

Current methods target the versioned 0.7 JEP API routes. Explicit legacy
methods retain pre-0.7 compatibility; no current-method failure triggers a
legacy fallback.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
JEP_WIRE_VERSION = "1"
JEP_CORE_PROFILE = "jep-core-0.7"


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
            if value is not None or name in data or name in {"jep", "id", "verb", "who", "when", "what"}:
                data[name] = deepcopy(value)
        return data


@dataclass
class LegacyJEPEvent:
    jep: str
    verb: str
    who: str
    when: int
    nonce: str
    what: Any = None
    aud: Optional[str] = None
    ref: str | Dict[str, Any] | None = None
    ext: Optional[Dict[str, Any]] = None
    ext_crit: Optional[List[str]] = None
    sig: str | Dict[str, Any] | None = None
    _wire: Optional[Dict[str, Any]] = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LegacyJEPEvent":
        data = deepcopy(data)
        return cls(
            jep=data["jep"],
            verb=data["verb"],
            who=data["who"],
            when=data["when"],
            nonce=data["nonce"],
            what=data.get("what"),
            aud=data.get("aud"),
            ref=data.get("ref"),
            ext=data.get("ext"),
            ext_crit=data.get("ext_crit"),
            sig=data.get("sig"),
            _wire=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = deepcopy(self._wire) if self._wire is not None else {}
        for name in ("jep", "verb", "who", "when", "nonce", "what", "aud", "ref", "ext", "ext_crit", "sig"):
            value = getattr(self, name)
            if value is not None or name in data or name in {"jep", "verb", "who", "when", "nonce"}:
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
        data: Dict[str, Any] = {
            "verb": self.verb,
            "what": self.what,
            "digest_only_who": self.digest_only_who,
        }
        for name in ("id", "who", "aud", "ref", "ttl_minutes"):
            value = getattr(self, name)
            if value is not None:
                data[name] = value
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
class LegacyVerifyEventRequest:
    event: LegacyJEPEvent | Dict[str, Any]
    mode: str = "archival"
    consume_nonce: bool = False
    expected_audience: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        event = self.event.to_dict() if isinstance(self.event, LegacyJEPEvent) else self.event
        data: Dict[str, Any] = {
            "event": event,
            "mode": self.mode,
            "consume_nonce": self.consume_nonce,
        }
        if self.expected_audience is not None:
            data["expected_audience"] = self.expected_audience
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
            status=data.get("status", ""),
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
class LegacyValidationResult:
    valid: bool
    level: int
    mode: str
    profile: str
    scopes: List[str] = field(default_factory=list)
    event_hash: Optional[str] = None
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    conformance_class: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LegacyValidationResult":
        return cls(
            valid=data.get("valid") is True,
            level=int(data.get("level", 0)),
            mode=data.get("mode", ""),
            profile=data.get("profile", ""),
            scopes=list(data.get("scopes") or []),
            event_hash=data.get("event_hash"),
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
class LegacyEventResponse:
    event: LegacyJEPEvent
    event_hash: str
    validation: LegacyValidationResult

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LegacyEventResponse":
        return cls(
            event=LegacyJEPEvent.from_dict(data["event"]),
            event_hash=data["event_hash"],
            validation=LegacyValidationResult.from_dict(data["validation"]),
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
    """Client for JEP Core 0.7 API with explicit pre-0.7 compatibility."""

    def __init__(self, api_key: str = "", base_url: str = DEFAULT_BASE_URL, timeout: float = 30.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "content-type": "application/json",
            "user-agent": "JEP-Python-SDK/0.7.0",
        })
        if api_key:
            self.session.headers.update({
                "authorization": f"Bearer {api_key}",
                "x-api-key": api_key,
            })

    def create_event(self, request: CreateEventRequest | Dict[str, Any]) -> EventResponse:
        payload = request.to_dict() if isinstance(request, CreateEventRequest) else request
        self._validate_create_payload(payload)
        return EventResponse.from_dict(self._request("POST", "/v0.7/events/create", payload))

    def verify_event(self, request: VerifyEventRequest | Dict[str, Any]) -> ValidationResult:
        payload = request.to_dict() if isinstance(request, VerifyEventRequest) else request
        if not payload.get("event"):
            raise JEPValidationError("event is required")
        return ValidationResult.from_dict(self._request("POST", "/v0.7/events/verify", payload))

    def create_legacy_event(self, request: CreateEventRequest | Dict[str, Any]) -> LegacyEventResponse:
        payload = request.to_dict() if isinstance(request, CreateEventRequest) else request
        self._validate_create_payload(payload)
        return LegacyEventResponse.from_dict(self._request("POST", "/events/create", payload))

    def verify_legacy_event(self, request: LegacyVerifyEventRequest | Dict[str, Any]) -> LegacyValidationResult:
        payload = request.to_dict() if isinstance(request, LegacyVerifyEventRequest) else request
        if not payload.get("event"):
            raise JEPValidationError("event is required")
        return LegacyValidationResult.from_dict(self._request("POST", "/events/verify", payload))

    def health(self) -> HealthResponse:
        return HealthResponse.from_dict(self._request("GET", "/health", None))

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
            message = data.get("message") or data.get("error") or data.get("detail") or response.text
            raise JEPAPIError(response.status_code, str(message), data)
        return data

    @staticmethod
    def _validate_create_payload(payload: Dict[str, Any]) -> None:
        if payload.get("verb") not in {"J", "D", "T", "V"}:
            raise JEPValidationError("verb must be J, D, T, or V")
        if "what" not in payload:
            raise JEPValidationError("what is required")
