# SDK Reference

The LayerCode SDK provides primitives for webhook handling, signature verification, and SSE streaming.

## Modules

### `layercode_create_app.sdk.events`

Event types and models for LayerCode webhooks.

#### `LayercodeEvent`

Main event model representing incoming webhooks.

```python
from layercode_create_app.sdk.events import LayercodeEvent

class LayercodeEvent:
    type: str  # Event type (call_started, transcript, etc.)
    call_id: str  # Unique call identifier
    agent_id: str  # Agent identifier
    timestamp: datetime  # Event timestamp
    transcript: str | None  # User transcript (for transcript events)
    metadata: dict  # Additional event metadata
```

**Event Types:**

- `call_started` - Call has begun
- `transcript` - User speech transcribed
- `call_ended` - Call has ended
- `user_interrupted` - User interrupted the agent

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
