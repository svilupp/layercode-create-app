# Server API Reference

FastAPI server components and utilities.

## Application Factory

### `create_app`

Create and configure the FastAPI application.

```python
from layercode_create_app.server.app import create_app

def create_app(
    settings: Settings,
    agent: BaseLayercodeAgent,
    agent_route: str = "/api/agent",
    authorize_route: str = "/api/authorize",
) -> FastAPI:
    """Create FastAPI application.

    Args:
        settings: Application settings
        agent: Agent instance to handle webhooks
        agent_route: Webhook endpoint path
        authorize_route: Authorization endpoint path

    Returns:
        Configured FastAPI application
    """
```

**Example:**

```python
from layercode_create_app.server.app import create_app
from layercode_create_app.config import Settings
from layercode_create_app.agents import get_agent

settings = Settings()
agent = get_agent("starter")
app = create_app(settings, agent)
```

## Endpoints

### Webhook Endpoint

Handles LayerCode webhook events.

**Path:** `/api/agent` (configurable)

**Method:** `POST`

**Request:**
```json
{
  "type": "transcript",
  "call_id": "call_123",
  "agent_id": "agent_456",
  "timestamp": "2025-01-15T10:30:00Z",
  "transcript": "Hello, how are you?",
  "metadata": {}
}
```

**Response:**
```
Content-Type: text/event-stream

event: message
data: I'm doing well, thank you!

event: done
data: [DONE]
```

**Headers:**
- `layercode-signature`: Webhook signature for verification

### Authorization Endpoint

Handles authorization callbacks.

**Path:** `/api/authorize` (configurable)

**Method:** `POST`

## Middleware

### Signature Verification

Automatically verifies webhook signatures.

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SignatureVerificationMiddleware(BaseHTTPMiddleware):
    """Verify LayerCode webhook signatures."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            # Verify signature
            signature = request.headers.get("layercode-signature")
            payload = await request.body()

            if not verify_signature(payload, signature, secret):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid signature"}
                )

        return await call_next(request)
```

### Logging Middleware

Logs all requests and responses.

```python
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")

        response = await call_next(request)

        logger.info(f"Response: {response.status_code}")
        return response
```

## Conversation Management

### `ConversationManager`

Manages conversation state across multiple calls.

```python
from layercode_create_app.server.conversation import ConversationManager

class ConversationManager:
    """Manage conversation state."""

    def __init__(self):
        self.conversations: dict[str, list] = {}

    def add_message(self, call_id: str, message: dict) -> None:
        """Add message to conversation history."""
        if call_id not in self.conversations:
            self.conversations[call_id] = []
        self.conversations[call_id].append(message)

    def get_history(self, call_id: str) -> list:
        """Get conversation history."""
        return self.conversations.get(call_id, [])

    def clear(self, call_id: str) -> None:
        """Clear conversation history."""
        if call_id in self.conversations:
            del self.conversations[call_id]
```

## Health Checks

### Health Endpoint

Check server health.

**Path:** `/health`

**Method:** `GET`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "0.0.1"
}
```

### Readiness Endpoint

Check if server is ready to accept requests.

**Path:** `/ready`

**Method:** `GET`

**Response:**
```json
{
  "ready": true,
  "agent": "starter",
  "model": "openai:gpt-5-nano"
}
```

## Error Handling

### Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Running the Server

### With Uvicorn

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
```

### Configuration Options

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="info",
    reload=False,
    workers=1,
    access_log=True,
)
```

## Testing

### Test Client

```python
from fastapi.testclient import TestClient

def test_webhook_endpoint():
    client = TestClient(app)

    response = client.post(
        "/api/agent",
        json={
            "type": "call_started",
            "call_id": "test-123",
        },
        headers={
            "layercode-signature": "test-signature",
        },
    )

    assert response.status_code == 200
```

## Next Steps

- [CLI Reference](cli.md) - Command-line interface
- [Deployment Guide](../guides/deployment.md) - Production deployment
