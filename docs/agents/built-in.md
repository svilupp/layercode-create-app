# Built-in Agents

The toolkit includes three reference agents demonstrating different patterns and capabilities.

## Echo Agent

A deterministic agent that doesn't use AI models. Perfect for testing webhook delivery and SSE streaming.

### Usage

```bash
uv run layercode-create-app run --agent echo
```

### Behavior

- Sends a welcome message when the call starts
- Echoes back whatever the user says
- Doesn't require API keys for AI providers

### Use Cases

- Testing webhook configuration
- Verifying tunnel connectivity
- Understanding the basic agent flow
- Development without AI costs

### Implementation

Location: `src/layercode_create_app/agents/echo.py`

```python
@agent("echo")
class EchoAgent(BaseLayercodeAgent):
    async def process(self, event):
        if event.type == "call_started":
            return "Welcome! I'll echo everything you say."
        elif event.type == "transcript":
            return f"You said: {event.transcript}"
```

## Starter Agent

A general-purpose conversational assistant with progressive disclosure and automatic transcription cleanup.

### Usage

```bash
uv run layercode-create-app run --agent starter
```

### Features

- Clean, natural responses
- Context-aware conversations
- Automatic transcription cleanup
- Handles interruptions gracefully

### Configuration

Requires an AI provider API key:

```env
OPENAI_API_KEY=sk-...
# OR
GOOGLE_GENERATIVEAI_API_KEY=...
```

### Model Selection

```bash
# Use default model from .env
uv run layercode-create-app run --agent starter

# Override with specific model
uv run layercode-create-app run --agent starter --model openai:gpt-4
```

### Use Cases

- Customer support
- General Q&A
- Information lookup
- Friendly conversation

### Prompt

Location: `src/src/layercode_create_app/agents/prompts/starter.txt`

The prompt emphasizes:
- Concise responses
- Progressive disclosure
- Natural conversation flow
- Handling of speech artifacts

## Bakery Agent

A persona-driven agent demonstrating custom tools for business operations.

### Usage

```bash
uv run layercode-create-app run --agent bakery --tunnel
```

### Features

- Bakery persona with character
- Custom tools for business logic:
  - Menu lookup
  - Order placement
  - Reservation booking
- Demonstrates PydanticAI tool calling

### Tools

The bakery agent has three tools:

**1. Get Menu**
```python
@tool
async def get_menu(ctx: RunContext) -> str:
    """Retrieve the bakery menu"""
    return menu_items
```

**2. Place Order**
```python
@tool
async def place_order(
    ctx: RunContext,
    items: list[str],
    quantity: list[int]
) -> str:
    """Place an order for bakery items"""
    # Order processing logic
```

**3. Make Reservation**
```python
@tool
async def make_reservation(
    ctx: RunContext,
    date: str,
    time: str,
    party_size: int
) -> str:
    """Book a table reservation"""
    # Reservation logic
```

### Use Cases

- Restaurant ordering
- Business automation examples
- Learning tool implementation
- Custom persona development

### Prompt

Location: `src/src/layercode_create_app/agents/prompts/bakery.txt`

Features a friendly bakery owner persona with knowledge of the menu and operations.

## Comparing Agents

| Feature | Echo | Starter | Bakery |
|---------|------|---------|--------|
| AI Required | No | Yes | Yes |
| Custom Tools | No | No | Yes |
| Persona | None | Generic | Bakery Owner |
| Use Case | Testing | General | Business Logic |
| Complexity | Simple | Medium | Advanced |

## Running Multiple Agents

You can run multiple agents simultaneously on different ports:

```bash
# Terminal 1
uv run layercode-create-app run --agent echo --port 8000

# Terminal 2
uv run layercode-create-app run --agent starter --port 8001

# Terminal 3
uv run layercode-create-app run --agent bakery --port 8002
```

## Next Steps

- [Creating Custom Agents](custom.md) - Build your own agent
- [API Reference](../api/agents.md) - Agent API documentation
- [Observability](../guides/observability.md) - Monitor agent performance
