"""Tests for webhook event models."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from layercode_create_app.sdk.events import (
    DataPayload,
    LayercodeEventType,
    MessagePayload,
    SessionEndPayload,
    SessionStartPayload,
    SessionUpdatePayload,
    TranscriptItem,
    parse_webhook_payload,
)

# =============================================================================
# SessionStartPayload Tests
# =============================================================================


def test_session_start_payload_parsing(session_start_payload: dict[str, str]) -> None:
    payload = SessionStartPayload.model_validate(session_start_payload)
    assert payload.type is LayercodeEventType.SESSION_START
    assert payload.session_id == "sess_123"
    assert payload.turn_id == "turn_789"


def test_session_start_requires_turn_id() -> None:
    """session.start events must include turn_id."""
    with pytest.raises(ValidationError) as exc_info:
        SessionStartPayload.model_validate(
            {
                "type": "session.start",
                "session_id": "sess_123",
                "conversation_id": "conv_456",
                # Missing turn_id
            }
        )
    assert "turn_id" in str(exc_info.value)


# =============================================================================
# MessagePayload Tests
# =============================================================================


def test_message_payload_parsing(message_payload: dict[str, str]) -> None:
    payload = MessagePayload.model_validate(message_payload)
    assert payload.type is LayercodeEventType.MESSAGE
    assert payload.text == "Hello"
    assert payload.turn_id == "turn_790"


def test_message_payload_with_optional_fields() -> None:
    payload = MessagePayload.model_validate(
        {
            "type": "message",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
            "turn_id": "turn_790",
            "text": "Hello",
            "recording_url": "https://example.com/recording.wav",
            "recording_status": "completed",
            "transcript": "Hello there",
            "usage": {"tokens": 100},
        }
    )
    assert payload.recording_url == "https://example.com/recording.wav"
    assert payload.recording_status == "completed"
    assert payload.transcript == "Hello there"
    assert payload.usage == {"tokens": 100}


# =============================================================================
# DataPayload Tests
# =============================================================================


def test_data_payload_parsing(data_payload: dict[str, Any]) -> None:
    payload = DataPayload.model_validate(data_payload)
    assert payload.type is LayercodeEventType.DATA
    assert payload.session_id == "sess_123"
    assert payload.turn_id == "turn_791"
    assert payload.data == {"action": "button_click", "value": 42}


def test_data_payload_requires_turn_id() -> None:
    """data events must include turn_id."""
    with pytest.raises(ValidationError) as exc_info:
        DataPayload.model_validate(
            {
                "type": "data",
                "session_id": "sess_123",
                "conversation_id": "conv_456",
                "data": {"key": "value"},
                # Missing turn_id
            }
        )
    assert "turn_id" in str(exc_info.value)


def test_data_payload_empty_data() -> None:
    """data events can have empty data dict."""
    payload = DataPayload.model_validate(
        {
            "type": "data",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
            "turn_id": "turn_791",
            "data": {},
        }
    )
    assert payload.data == {}


def test_data_payload_defaults_to_empty_dict() -> None:
    """data field defaults to empty dict if not provided."""
    payload = DataPayload.model_validate(
        {
            "type": "data",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
            "turn_id": "turn_791",
        }
    )
    assert payload.data == {}


# =============================================================================
# SessionUpdatePayload Tests
# =============================================================================


def test_session_update_payload_parsing(session_update_payload: dict[str, Any]) -> None:
    """session.update parses correctly without turn_id."""
    payload = SessionUpdatePayload.model_validate(session_update_payload)
    assert payload.type is LayercodeEventType.SESSION_UPDATE
    assert payload.session_id == "fm4l7332owiu9ng5crslh75l"
    assert payload.conversation_id == "ho8n0aht86qrs6tpfocymyty"
    assert payload.recording_status == "completed"
    assert (
        payload.recording_url
        == "https://api.layercode.com/v1/agents/mxdi9mls/sessions/fm4l7332owiu9ng5crslh75l/recording"
    )
    assert payload.recording_duration == 27


def test_session_update_failed_payload(session_update_failed_payload: dict[str, Any]) -> None:
    """session.update with failed recording status."""
    payload = SessionUpdatePayload.model_validate(session_update_failed_payload)
    assert payload.recording_status == "failed"
    assert payload.error_message == "Recording quota exceeded"
    assert payload.recording_url is None
    assert payload.recording_duration is None


def test_session_update_no_turn_id_required() -> None:
    """session.update does NOT require turn_id (key fix for the 400 error)."""
    payload = SessionUpdatePayload.model_validate(
        {
            "type": "session.update",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
            "recording_status": "completed",
        }
    )
    assert payload.session_id == "sess_123"
    # Verify turn_id is not an attribute on this payload type
    assert not hasattr(payload, "turn_id")


def test_session_update_minimal_payload() -> None:
    """session.update with only required fields."""
    payload = SessionUpdatePayload.model_validate(
        {
            "type": "session.update",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
        }
    )
    assert payload.recording_status is None
    assert payload.recording_url is None
    assert payload.recording_duration is None
    assert payload.error_message is None


# =============================================================================
# SessionEndPayload Tests
# =============================================================================


def test_session_end_payload_parsing(session_end_payload: dict[str, Any]) -> None:
    """session.end parses correctly without turn_id."""
    payload = SessionEndPayload.model_validate(session_end_payload)
    assert payload.type is LayercodeEventType.SESSION_END
    assert payload.session_id == "sess_123"
    assert payload.agent_id == "agent_abc"
    assert payload.started_at == "2025-12-02T16:50:00.000Z"
    assert payload.ended_at == "2025-12-02T16:53:36.351Z"
    assert payload.duration == 216351
    assert payload.transcription_duration_seconds == 45.2
    assert payload.tts_duration_seconds == 30.1
    assert payload.latency == 0.85
    assert payload.ip_address == "192.168.1.1"
    assert payload.country_code == "US"
    assert payload.recording_status == "enabled"
    assert payload.transcript is not None
    assert len(payload.transcript) == 2


def test_session_end_transcript_items(session_end_payload: dict[str, Any]) -> None:
    """session.end transcript items are properly typed."""
    payload = SessionEndPayload.model_validate(session_end_payload)
    assert payload.transcript is not None

    first_item = payload.transcript[0]
    assert isinstance(first_item, TranscriptItem)
    assert first_item.role == "assistant"
    assert first_item.text == "Welcome!"
    assert first_item.timestamp == "2025-12-02T16:50:00.000Z"

    second_item = payload.transcript[1]
    assert second_item.role == "user"
    assert second_item.text == "Hello"


def test_session_end_no_turn_id_required() -> None:
    """session.end does NOT require turn_id (key fix for the 400 error)."""
    payload = SessionEndPayload.model_validate(
        {
            "type": "session.end",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
        }
    )
    assert payload.session_id == "sess_123"
    # Verify turn_id is not an attribute on this payload type
    assert not hasattr(payload, "turn_id")


def test_session_end_minimal_payload(session_end_minimal_payload: dict[str, Any]) -> None:
    """session.end with only required fields."""
    payload = SessionEndPayload.model_validate(session_end_minimal_payload)
    assert payload.session_id == "sess_min"
    assert payload.agent_id is None
    assert payload.duration is None
    assert payload.transcript is None


def test_session_end_transcript_with_extra_fields() -> None:
    """TranscriptItem allows extra fields for forward compatibility."""
    payload = SessionEndPayload.model_validate(
        {
            "type": "session.end",
            "session_id": "sess_123",
            "conversation_id": "conv_456",
            "transcript": [
                {
                    "role": "user",
                    "text": "Hello",
                    "timestamp": "2025-12-02T16:50:05.000Z",
                    "confidence": 0.95,  # Extra field
                    "language": "en",  # Extra field
                }
            ],
        }
    )
    assert payload.transcript is not None
    item = payload.transcript[0]
    assert item.role == "user"
    assert item.text == "Hello"


# =============================================================================
# Union Parsing Tests (parse_webhook_payload)
# =============================================================================


def test_union_parsing_session_start(session_start_payload: dict[str, str]) -> None:
    payload = parse_webhook_payload(session_start_payload)
    assert isinstance(payload, SessionStartPayload)


def test_union_parsing_message(message_payload: dict[str, str]) -> None:
    payload = parse_webhook_payload(message_payload)
    assert isinstance(payload, MessagePayload)


def test_union_parsing_data(data_payload: dict[str, Any]) -> None:
    payload = parse_webhook_payload(data_payload)
    assert isinstance(payload, DataPayload)


def test_union_parsing_session_update(session_update_payload: dict[str, Any]) -> None:
    payload = parse_webhook_payload(session_update_payload)
    assert isinstance(payload, SessionUpdatePayload)


def test_union_parsing_session_end(session_end_payload: dict[str, Any]) -> None:
    payload = parse_webhook_payload(session_end_payload)
    assert isinstance(payload, SessionEndPayload)


def test_union_parsing_unknown_type() -> None:
    """Unknown event types should raise ValidationError."""
    with pytest.raises(ValidationError):
        parse_webhook_payload(
            {
                "type": "unknown.event",
                "session_id": "sess_123",
                "conversation_id": "conv_456",
            }
        )


# =============================================================================
# Edge Cases and Regression Tests
# =============================================================================


def test_session_update_exact_failing_payload() -> None:
    """Test exact payload from the user's error log that was returning 400."""
    payload_dict = {
        "type": "session.update",
        "session_id": "fm4l7332owiu9ng5crslh75l",
        "conversation_id": "ho8n0aht86qrs6tpfocymyty",
        "recording_status": "completed",
        "recording_url": "https://api.layercode.com/v1/agents/mxdi9mls/sessions/fm4l7332owiu9ng5crslh75l/recording",
        "recording_duration": 27,
    }
    # This should NOT raise - it was the original bug
    payload = parse_webhook_payload(payload_dict)
    assert isinstance(payload, SessionUpdatePayload)
    assert payload.recording_status == "completed"
    assert payload.recording_duration == 27


def test_phone_number_fields_on_all_payloads() -> None:
    """All payload types should support optional phone number fields."""
    base_fields = {
        "from_phone_number": "+1234567890",
        "to_phone_number": "+0987654321",
    }

    # session.start
    start_payload = SessionStartPayload.model_validate(
        {
            "type": "session.start",
            "session_id": "s1",
            "conversation_id": "c1",
            "turn_id": "t1",
            **base_fields,
        }
    )
    assert start_payload.from_phone_number == "+1234567890"
    assert start_payload.to_phone_number == "+0987654321"

    # session.update (no turn_id)
    update_payload = SessionUpdatePayload.model_validate(
        {
            "type": "session.update",
            "session_id": "s1",
            "conversation_id": "c1",
            **base_fields,
        }
    )
    assert update_payload.from_phone_number == "+1234567890"

    # session.end (no turn_id)
    end_payload = SessionEndPayload.model_validate(
        {
            "type": "session.end",
            "session_id": "s1",
            "conversation_id": "c1",
            **base_fields,
        }
    )
    assert end_payload.to_phone_number == "+0987654321"


def test_metadata_field_on_all_payloads() -> None:
    """All payload types should support optional metadata field."""
    metadata = {"user_id": "u123", "custom": True}

    # session.update
    update_payload = SessionUpdatePayload.model_validate(
        {
            "type": "session.update",
            "session_id": "s1",
            "conversation_id": "c1",
            "metadata": metadata,
        }
    )
    assert update_payload.metadata == metadata

    # session.end
    end_payload = SessionEndPayload.model_validate(
        {
            "type": "session.end",
            "session_id": "s1",
            "conversation_id": "c1",
            "metadata": metadata,
        }
    )
    assert end_payload.metadata == metadata
