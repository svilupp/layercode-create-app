"""Test fixtures for LayerCode create app."""

from __future__ import annotations

from typing import Any

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


@pytest.fixture()
def data_payload() -> dict[str, Any]:
    return {
        "type": "data",
        "session_id": "sess_123",
        "conversation_id": "conv_456",
        "turn_id": "turn_791",
        "data": {"action": "button_click", "value": 42},
    }


@pytest.fixture()
def session_update_payload() -> dict[str, Any]:
    """Realistic session.update payload (no turn_id)."""
    return {
        "type": "session.update",
        "session_id": "fm4l7332owiu9ng5crslh75l",
        "conversation_id": "ho8n0aht86qrs6tpfocymyty",
        "recording_status": "completed",
        "recording_url": "https://api.layercode.com/v1/agents/mxdi9mls/sessions/fm4l7332owiu9ng5crslh75l/recording",
        "recording_duration": 27,
    }


@pytest.fixture()
def session_update_failed_payload() -> dict[str, Any]:
    """session.update payload for failed recording."""
    return {
        "type": "session.update",
        "session_id": "sess_456",
        "conversation_id": "conv_789",
        "recording_status": "failed",
        "error_message": "Recording quota exceeded",
    }


@pytest.fixture()
def session_end_payload() -> dict[str, Any]:
    """Realistic session.end payload (no turn_id)."""
    return {
        "type": "session.end",
        "session_id": "sess_123",
        "conversation_id": "conv_456",
        "agent_id": "agent_abc",
        "started_at": "2025-12-02T16:50:00.000Z",
        "ended_at": "2025-12-02T16:53:36.351Z",
        "duration": 216351,
        "transcription_duration_seconds": 45.2,
        "tts_duration_seconds": 30.1,
        "latency": 0.85,
        "ip_address": "192.168.1.1",
        "country_code": "US",
        "recording_status": "enabled",
        "transcript": [
            {"role": "assistant", "text": "Welcome!", "timestamp": "2025-12-02T16:50:00.000Z"},
            {"role": "user", "text": "Hello", "timestamp": "2025-12-02T16:50:05.000Z"},
        ],
    }


@pytest.fixture()
def session_end_minimal_payload() -> dict[str, Any]:
    """Minimal session.end payload with only required fields."""
    return {
        "type": "session.end",
        "session_id": "sess_min",
        "conversation_id": "conv_min",
    }
