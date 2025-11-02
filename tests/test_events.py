"""Tests for webhook event models."""

from __future__ import annotations

from layercode_create_app.sdk.events import (
    LayercodeEventType,
    MessagePayload,
    SessionStartPayload,
    parse_webhook_payload,
)


def test_session_start_payload_parsing(session_start_payload: dict[str, str]) -> None:
    payload = SessionStartPayload.model_validate(session_start_payload)
    assert payload.type is LayercodeEventType.SESSION_START
    assert payload.session_id == "sess_123"


def test_message_payload_parsing(message_payload: dict[str, str]) -> None:
    payload = MessagePayload.model_validate(message_payload)
    assert payload.type is LayercodeEventType.MESSAGE
    assert payload.text == "Hello"


def test_union_parsing(session_start_payload: dict[str, str]) -> None:
    payload = parse_webhook_payload(session_start_payload)
    assert isinstance(payload, SessionStartPayload)
