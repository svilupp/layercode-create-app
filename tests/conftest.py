"""Test fixtures for LayerCode create app."""

from __future__ import annotations

import pytest


@pytest.fixture()
def session_start_payload() -> dict[str, str]:
    return {
        "type": "session.start",
        "session_id": "sess_123",
        "conversation_id": "conv_456",
        "turn_id": "turn_789",
    }


@pytest.fixture()
def message_payload() -> dict[str, str]:
    return {
        "type": "message",
        "session_id": "sess_123",
        "conversation_id": "conv_456",
        "turn_id": "turn_790",
        "text": "Hello",
    }
