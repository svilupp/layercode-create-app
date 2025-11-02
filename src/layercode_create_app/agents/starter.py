"""Starter conversational agent."""

from __future__ import annotations

from pathlib import Path

from pydantic_ai import Agent as PydanticAgent
from pydantic_ai.messages import ModelMessage
from textprompts import load_prompt

from ..sdk.events import MessagePayload, SessionEndPayload, SessionStartPayload
from ..sdk.stream import StreamHelper
from .base import BaseLayercodeAgent, agent

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


@agent("starter")
class StarterAgent(BaseLayercodeAgent):
    """Concise voice assistant tuned for audio interactions."""

    name = "starter"
    description = "Concise conversational agent"

    def __init__(self, model: str) -> None:
        super().__init__(model)
        prompt = load_prompt(PROMPTS_DIR / "starter.txt")
        system_prompt = str(prompt.prompt)
        self._welcome = "Hi there! How can I help today?"
        self._agent = PydanticAgent(
            model,
            system_prompt=system_prompt,
        )

    def pydantic_agent(self) -> object | None:
        return self._agent

    async def handle_session_start(
        self, payload: SessionStartPayload, stream: StreamHelper
    ) -> None:
        stream.tts(self._welcome)
        stream.end()

    async def handle_message(
        self,
        payload: MessagePayload,
        stream: StreamHelper,
        history: list[ModelMessage],
    ) -> list[ModelMessage]:
        user_text = payload.text or ""

        async with self._agent.run_stream(user_text, message_history=history) as run:
            streamed = False
            async for chunk in run.stream_text(delta=True):
                if chunk:
                    streamed = True
                    stream.tts(chunk)

            final_text = await run.get_output()
            if final_text and not streamed:
                stream.tts(final_text)

            new_messages = list(run.new_messages())

        stream.end()
        return new_messages

    async def handle_session_end(self, payload: SessionEndPayload) -> None:
        return None
