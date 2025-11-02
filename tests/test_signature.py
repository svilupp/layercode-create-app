"""Tests for signature verification."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from layercode_create_app.sdk.auth import InvalidSignatureError, verify_signature


def _make_signature(payload: str, secret: str, timestamp: int) -> str:
    signed_payload = f"{timestamp}.{payload}".encode()
    digest = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_verify_signature_accepts_valid_signature() -> None:
    secret = "topsecret"
    body = json.dumps({"hello": "world"})
    timestamp = int(time.time())
    signature = _make_signature(body, secret, timestamp)

    verify_signature(body, signature, secret)


def test_verify_signature_rejects_invalid_signature() -> None:
    secret = "topsecret"
    body = json.dumps({"hello": "world"})
    timestamp = int(time.time())
    signature = _make_signature(body, secret, timestamp)

    with pytest.raises(InvalidSignatureError):
        verify_signature(body, signature + "broken", secret)


def test_verify_signature_rejects_outdated_timestamp() -> None:
    secret = "topsecret"
    body = json.dumps({"hello": "world"})
    timestamp = int(time.time()) - 1000
    signature = _make_signature(body, secret, timestamp)

    with pytest.raises(InvalidSignatureError):
        verify_signature(body, signature, secret, tolerance_seconds=10)
