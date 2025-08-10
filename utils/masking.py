# utils/masking.py
from __future__ import annotations

import re
from typing import Any, Dict, Iterable

"""
Reusable masking helpers for logs and responses.

Usage:
    from utils.masking import mask_sensitive_data

    masked_headers = mask_sensitive_data(dict(request.headers), parent_key="headers")
    masked_body = mask_sensitive_data(request_body)

Notes:
- Keys listed in SENSITIVE_KEYS are always masked when found in dicts.
- SAFE_HEADER_KEYS remain visible when masking headers (parent_key="headers").
- Free-text masking hides JWTs, OTPs, and common token/password forms.
"""

# Keys whose values must be masked when they appear in dicts
SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "pass",
        "access_token",
        "refresh_token",
        "auth_token",
        "authorization",
        "auth-key",
        "token",
        "jwt",
        "otp",
        "pin",
        "secret",
        "api_key",
        "api-key",
        "x-api-key",
    }
)

# Header keys that are safe to keep visible (when parent_key="headers")
SAFE_HEADER_KEYS: frozenset[str] = frozenset(
    {
        "host",
        "origin",
        "referer",
        "x-forwarded-for",
        "x-forwarded-proto",
        "x-forwarded-host",
        "x-correlation-id",
        "user-agent",
        "accept",
        "accept-encoding",
        "accept-language",
        "content-type",
        "content-length",
        "connection",
        "url",
        "path",
    }
)

# === Text patterns we proactively scrub inside strings ===

# Standard JWT (with or without Bearer prefix)
JWT_PATTERN = re.compile(
    r"(?:Bearer\s+)?[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",
    re.IGNORECASE,
)

# Common "eyJ..." JWT style finder (some services format like this)
JWT_EYJ_PATTERN = re.compile(r"eyJ[\w-]*\.[\w-]*\.[\w-]*", re.IGNORECASE)

# OTP/code strings in text
OTP_LABELED_PATTERN = re.compile(
    r"(?i)\b(otp(?:\s*code)?(?:\s*is|:)?\s*)([0-9]{3,8})\b"
)

# "password: xxx" / "pwd is xxx"
PASSWORD_LABELED_PATTERN = re.compile(
    r"(?i)\b(password|pwd)(?:\s*is|:)?\s*([^\s,;]{3,64})\b"
)

# API key in text
APIKEY_LABELED_PATTERN = re.compile(
    r"(?i)\b(api[-_ ]?key)(?:\s*is|:)?\s*([A-Za-z0-9_\-]{6,})\b"
)

# Generic token-like phrases
GENERIC_TOKEN_LABELED_PATTERN = re.compile(
    r"(?i)\b(token|auth[-_ ]?key|authorization)(?:\s*is|:)?\s*([A-Za-z0-9_\-]{6,})\b"
)

# PIN labeled digits (to catch things like "pin: 123456789012")
PIN_LABELED_PATTERN = re.compile(
    r"(?i)\b(pin)(?:\s*is|:)?\s*([0-9]{4,20})\b"
)

MASK = "******"


def _mask_string_value(value: str) -> str:
    """Mask secrets embedded inside free text."""
    masked = value

    # JWT / bearer tokens
    masked = JWT_PATTERN.sub(MASK, masked)
    masked = JWT_EYJ_PATTERN.sub(MASK, masked)

    # OTP / password / api key / generic tokens / pins
    masked = OTP_LABELED_PATTERN.sub(r"\1" + MASK, masked)
    masked = PASSWORD_LABELED_PATTERN.sub(r"\1 " + MASK, masked)
    masked = APIKEY_LABELED_PATTERN.sub(r"\1 " + MASK, masked)
    masked = GENERIC_TOKEN_LABELED_PATTERN.sub(r"\1 " + MASK, masked)
    masked = PIN_LABELED_PATTERN.sub(r"\1 " + MASK, masked)

    return masked


def _should_mask_key(key: str, *, parent_key: str = "") -> bool:
    """
    Decide whether a dict key's value should be fully masked.
    - If we're inside headers (parent_key == "headers"), don't mask safe header keys.
    - Otherwise, mask if the key is in (or clearly contains) a sensitive keyword.
    """
    k = key.lower()

    if parent_key.lower() == "headers" and k in SAFE_HEADER_KEYS:
        return False

    # Exact match or obvious containment (e.g., "user_password")
    if k in SENSITIVE_KEYS:
        return True
    return any(s in k for s in SENSITIVE_KEYS)


def _mask_mapping(d: Dict[str, Any], *, parent_key: str = "") -> Dict[str, Any]:
    """Mask values inside a dict; respects SAFE_HEADER_KEYS when parent_key='headers'."""
    masked: Dict[str, Any] = {}
    for k, v in d.items():
        if _should_mask_key(k, parent_key=parent_key):
            masked[k] = MASK
        else:
            masked[k] = mask_sensitive_data(v, parent_key=k)
    return masked


def _mask_iterable(it: Iterable[Any], *, parent_key: str = "") -> list[Any]:
    """Mask values inside any iterable (list/tuple/set) and return a list."""
    return [mask_sensitive_data(v, parent_key=parent_key) for v in it]


def mask_sensitive_data(data: Any, *, parent_key: str = "") -> Any:
    """
    Recursively mask sensitive data.

    - dict: mask sensitive keys entirely, recurse into others
    - list/tuple/set: recurse into items
    - str: scrub secrets embedded in text (JWT, OTP, tokens, etc.)
    - bytes: decode to utf-8 (ignore errors) then scrub
    - anything else: returned as-is
    """
    if isinstance(data, dict):
        return _mask_mapping(data, parent_key=parent_key)

    if isinstance(data, (list, tuple, set)):
        return _mask_iterable(data, parent_key=parent_key)

    if isinstance(data, str):
        return _mask_string_value(data)

    if isinstance(data, bytes):
        try:
            return _mask_string_value(data.decode("utf-8", errors="ignore"))
        except Exception:
            return MASK  # fallback if bytes are not safely decodable

    return data


__all__ = [
    "mask_sensitive_data",
    "SENSITIVE_KEYS",
    "SAFE_HEADER_KEYS",
    "JWT_PATTERN",
]
