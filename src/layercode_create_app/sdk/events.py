"""Typed LayerCode event models."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class LayercodeEventType(str, Enum):
    """Supported inbound LayerCode webhook events."""

    SESSION_START = "session.start"
    MESSAGE = "message"
    SESSION_END = "session.end"
    SESSION_UPDATE = "session.update"


class BaseWebhookPayload(BaseModel):
    """Shared attributes for all webhook events."""

    type: LayercodeEventType
    session_id: str = Field(..., alias="session_id")
    conversation_id: str = Field(..., alias="conversation_id")
    turn_id: str = Field(..., alias="turn_id")
    metadata: dict[str, Any] | None = None
    from_phone_number: str | None = Field(default=None, alias="from_phone_number")
    to_phone_number: str | None = Field(default=None, alias="to_phone_number")

    model_config = ConfigDict(populate_by_name=True)


class SessionStartPayload(BaseWebhookPayload):
    """Payload for `session.start` events."""

    type: Literal[LayercodeEventType.SESSION_START]
    text: str | None = None


class MessagePayload(BaseWebhookPayload):
    """Payload for `message` events."""

    type: Literal[LayercodeEventType.MESSAGE]
    text: str | None = None
    recording_url: str | None = Field(default=None, alias="recording_url")
    recording_status: str | None = Field(default=None, alias="recording_status")
    transcript: str | None = None
    usage: dict[str, Any] | None = None


class SessionEndPayload(BaseWebhookPayload):
    """Payload for `session.end` events."""

    type: Literal[LayercodeEventType.SESSION_END]
    reason: str | None = None


class SessionUpdatePayload(BaseWebhookPayload):
    """Payload for `session.update` events."""

    type: Literal[LayercodeEventType.SESSION_UPDATE]
    text: str | None = None


WebhookPayload = SessionStartPayload | MessagePayload | SessionEndPayload | SessionUpdatePayload


_WEBHOOK_PAYLOAD_ADAPTER: TypeAdapter[WebhookPayload] = TypeAdapter(WebhookPayload)


def parse_webhook_payload(data: dict[str, Any]) -> WebhookPayload:
    """Validate raw webhook payload into the appropriate typed model."""

    return _WEBHOOK_PAYLOAD_ADAPTER.validate_python(data)
