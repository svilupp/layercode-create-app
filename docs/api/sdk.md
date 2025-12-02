# SDK Reference

The LayerCode SDK provides primitives for webhook handling, signature verification, and SSE streaming.

## Modules

### `layercode_create_app.sdk.events`

Typed event models for LayerCode webhooks. All models are Pydantic-based with full type hints.

#### Event Types

The SDK supports all LayerCode webhook events:

| Event | Payload Class | Has `turn_id` | Description |
|-------|---------------|---------------|-------------|
| `session.start` | `SessionStartPayload` | Yes | New session begins |
| `message` | `MessagePayload` | Yes | User speech transcribed |
| `data` | `DataPayload` | Yes | Client-sent structured JSON |
| `session.update` | `SessionUpdatePayload` | No | Recording completed/failed |
| `session.end` | `SessionEndPayload` | No | Session finished with transcript |

#### `SessionStartPayload`

Sent when a new voice session begins.

```python
from layercode_create_app.sdk import SessionStartPayload

class SessionStartPayload:
    type: Literal["session.start"]
    session_id: str
    conversation_id: str
    turn_id: str
    text: str | None = None
    metadata: dict | None = None
    from_phone_number: str | None = None
    to_phone_number: str | None = None
```

#### `MessagePayload`

Sent when user speech is transcribed.

```python
from layercode_create_app.sdk import MessagePayload

class MessagePayload:
    type: Literal["message"]
    session_id: str
    conversation_id: str
    turn_id: str
    text: str | None = None
    recording_url: str | None = None
    recording_status: str | None = None
    transcript: str | None = None
    usage: dict | None = None
    metadata: dict | None = None
    from_phone_number: str | None = None
    to_phone_number: str | None = None
```

#### `DataPayload`

Sent when the client emits structured JSON (e.g., button clicks, form data).

```python
from layercode_create_app.sdk import DataPayload

class DataPayload:
    type: Literal["data"]
    session_id: str
    conversation_id: str
    turn_id: str
    data: dict  # Arbitrary JSON payload from client
    metadata: dict | None = None
    from_phone_number: str | None = None
    to_phone_number: str | None = None
```

#### `SessionUpdatePayload`

Sent when asynchronous session data becomes available (e.g., recording completion).

```python
from layercode_create_app.sdk import SessionUpdatePayload

class SessionUpdatePayload:
    type: Literal["session.update"]
    session_id: str
    conversation_id: str
    recording_status: str | None = None  # "completed" | "failed"
    recording_url: str | None = None     # URL to download WAV
    recording_duration: float | None = None  # Duration in seconds
    error_message: str | None = None     # Details when failed
    metadata: dict | None = None
    from_phone_number: str | None = None
    to_phone_number: str | None = None
```

#### `SessionEndPayload`

Sent when the session finishes, includes full transcript and metrics.

```python
from layercode_create_app.sdk import SessionEndPayload, TranscriptItem

class TranscriptItem:
    role: str           # "user" | "assistant"
    text: str
    timestamp: str | None = None

class SessionEndPayload:
    type: Literal["session.end"]
    session_id: str
    conversation_id: str
    agent_id: str | None = None
    started_at: str | None = None        # ISO timestamp
    ended_at: str | None = None          # ISO timestamp
    duration: int | None = None          # Milliseconds
    transcription_duration_seconds: float | None = None
    tts_duration_seconds: float | None = None
    latency: float | None = None
    ip_address: str | None = None
    country_code: str | None = None
    recording_status: str | None = None  # "enabled" | "disabled"
    transcript: list[TranscriptItem] | None = None
    metadata: dict | None = None
    from_phone_number: str | None = None
    to_phone_number: str | None = None
```

#### `parse_webhook_payload`

Parse raw webhook JSON into the appropriate typed model.

```python
from layercode_create_app.sdk import parse_webhook_payload

payload = parse_webhook_payload({"type": "session.start", ...})
# Returns: SessionStartPayload | MessagePayload | DataPayload | SessionUpdatePayload | SessionEndPayload
```

### `layercode_create_app.sdk.auth`

Webhook signature verification.

#### `verify_signature`

Verify LayerCode webhook signatures.

```python
from layercode_create_app.sdk.auth import verify_signature

def verify_signature(
    payload: bytes,
    signature: str,
    secret: str,
    tolerance: int = 300
) -> bool:
    """Verify webhook signature.

    Args:
        payload: Raw webhook payload
        signature: Signature from header
        secret: Webhook secret
        tolerance: Timestamp tolerance in seconds

    Returns:
        True if signature is valid

    Raises:
        ValueError: If signature is invalid
    """
```

**Example:**

```python
from fastapi import Request, HTTPException

@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("layercode-signature")

    if not verify_signature(payload, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401)

    # Process webhook
```

### `layercode_create_app.sdk.stream`

Server-Sent Events (SSE) streaming utilities.

#### `create_sse_response`

Create an SSE response for streaming agent output.

```python
from layercode_create_app.sdk.stream import create_sse_response

def create_sse_response(
    generator: AsyncGenerator[str, None]
) -> StreamingResponse:
    """Create SSE streaming response.

    Args:
        generator: Async generator yielding response chunks

    Returns:
        FastAPI StreamingResponse configured for SSE
    """
```

**Example:**

```python
from fastapi import FastAPI
from layercode_create_app.sdk.stream import create_sse_response

@app.post("/agent")
async def agent_endpoint(event: LayercodeEvent):
    async def generate():
        # Stream agent responses
        async for chunk in agent.stream(event):
            yield chunk

    return create_sse_response(generate())
```

#### `format_sse_message`

Format a message for SSE transmission.

```python
def format_sse_message(
    data: str,
    event: str | None = None,
    id: str | None = None
) -> str:
    """Format SSE message.

    Args:
        data: Message data
        event: Event type (optional)
        id: Message ID (optional)

    Returns:
        Formatted SSE message
    """
```

**Example:**

```python
message = format_sse_message(
    data="Hello, world!",
    event="message",
    id="msg-123"
)
# Output:
# event: message
# id: msg-123
# data: Hello, world!
#
```

## Configuration

### `layercode_create_app.config`

Application settings and configuration.

#### `Settings`

Pydantic settings model loaded from environment.

```python
from layercode_create_app.config import Settings

class Settings:
    layercode_api_key: str
    layercode_webhook_secret: str
    openai_api_key: str | None = None
    google_generativeai_api_key: str | None = None
    default_model: str = "openai:gpt-5-nano"
    logfire_token: str | None = None
```

**Usage:**

```python
from layercode_create_app.config import Settings

settings = Settings()
print(settings.layercode_api_key)
```

## Logging

### `layercode_create_app.logging`

Structured logging setup.

#### `setup_logging`

Configure Loguru and Logfire.

```python
from layercode_create_app.logging import setup_logging

def setup_logging(
    verbose: bool = False,
    logfire_token: str | None = None
) -> None:
    """Setup application logging.

    Args:
        verbose: Enable debug logging
        logfire_token: Logfire API token (optional)
    """
```

## Error Handling

### Common Exceptions

**`SignatureVerificationError`**

Raised when webhook signature verification fails.

```python
from layercode_create_app.sdk.auth import SignatureVerificationError

try:
    verify_signature(payload, signature, secret)
except SignatureVerificationError as e:
    logger.error(f"Invalid signature: {e}")
```

**`AgentNotFoundError`**

Raised when requested agent doesn't exist.

```python
from layercode_create_app.agents import AgentNotFoundError

try:
    agent = get_agent("unknown")
except AgentNotFoundError:
    logger.error("Agent not found")
```

## Type Hints

The SDK uses type hints throughout. Enable type checking with mypy:

```bash
uv run mypy layercode_create_app
```

## Next Steps

- [Agents API](agents.md) - Agent interface documentation
- [Server API](server.md) - FastAPI server components
