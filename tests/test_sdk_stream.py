"""Tests for the streaming helper."""

from __future__ import annotations

from layercode_create_app.sdk.stream import StreamHelper


class Recorder:
    def __init__(self) -> None:
        self.events: list[bytes] = []
        self.closed = False

    def enqueue(self, data: bytes) -> None:
        self.events.append(data)

    def close(self) -> None:
        self.closed = True


class UTF8Encoder:
    def encode(self, text: str) -> bytes:
        return text.encode("utf-8")


def test_stream_helper_emits_expected_events() -> None:
    controller = Recorder()
    helper = StreamHelper("turn123", UTF8Encoder(), controller)

    helper.tts("Hello")
    helper.data({"foo": "bar"})
    helper.end()

    payloads = [event.decode("utf-8") for event in controller.events]
    assert "response.tts" in payloads[0]
    assert "response.data" in payloads[1]
    assert "response.end" in payloads[-1]
    assert controller.closed is True
