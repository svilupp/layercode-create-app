# Creating Custom Agents

Build your own conversational agents with custom logic, tools, and personas.

## Agent Structure

A custom agent consists of:

1. **Agent Class** - Python class implementing `BaseLayercodeAgent`
2. **Prompt File** - System instructions for the AI
3. **Tools** (optional) - Custom functions the agent can call
4. **Registration** - `@agent` decorator to register your agent

## Step-by-Step Guide

### 1. Create a Prompt File

Create `src/src/layercode_create_app/agents/prompts/my_agent.txt`:

```text
You are a helpful customer service agent for AcmeCorp.

Your role is to:
- Answer questions about our products
- Help customers track orders
- Resolve common issues

Guidelines:
- Be friendly and professional
- Keep responses concise
- Ask clarifying questions when needed
- Use the available tools to help customers

Current conversation context:
{context}
```

### 2. Create the Agent Class

Create `src/layercode_create_app/agents/my_agent.py`:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from layercode_create_app.agents.base import BaseLayercodeAgent, agent
from layercode_create_app.sdk.events import LayercodeEvent

@agent("my-agent")
class MyAgent(BaseLayercodeAgent):
    """Custom agent for AcmeCorp customer service."""

    def __init__(self, model: Model):
        super().__init__(model)

        # Load your prompt
        prompt = self._load_prompt("my_agent.txt")

        # Initialize PydanticAI agent
        self.agent = Agent(
            model=model,
            system_prompt=prompt,
        )

    async def process(self, event: LayercodeEvent) -> str:
        """Process incoming events and return responses."""

        if event.type == "call_started":
            return "Hello! I'm here to help with your AcmeCorp needs."

        elif event.type == "transcript":
            # Run the agent with the user's message
            result = await self.agent.run(
                event.transcript,
                message_history=self._build_history(event),
            )
            return result.data

        return ""

    def _build_history(self, event: LayercodeEvent) -> list:
        """Build conversation history from event."""
        # Implement history building logic
        return []
```

### 3. Add Custom Tools

Enhance your agent with custom tools:

```python
from pydantic_ai import Agent, RunContext, tool

@agent("my-agent")
class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)
        prompt = self._load_prompt("my_agent.txt")

        self.agent = Agent(
            model=model,
            system_prompt=prompt,
        )

        # Register tools
        self.agent.tool(self.lookup_order)
        self.agent.tool(self.track_shipment)

    @tool
    async def lookup_order(self, ctx: RunContext, order_id: str) -> str:
        """Look up order details by order ID.

        Args:
            order_id: The customer's order identifier

        Returns:
            Order status and details
        """
        # Your order lookup logic
        order = await fetch_order(order_id)
        return f"Order {order_id}: {order.status}"

    @tool
    async def track_shipment(self, ctx: RunContext, tracking_number: str) -> str:
        """Track a shipment by tracking number.

        Args:
            tracking_number: The shipment tracking number

        Returns:
            Current shipment status and location
        """
        # Your tracking logic
        status = await get_tracking_status(tracking_number)
        return f"Shipment status: {status}"

    async def process(self, event: LayercodeEvent) -> str:
        if event.type == "call_started":
            return "Hello! I can help you track orders and shipments."

        elif event.type == "transcript":
            result = await self.agent.run(event.transcript)
            return result.data

        return ""
```

### 4. Register and Test

Your agent is automatically registered via the `@agent` decorator. Test it:

```bash
# List agents (should show your new agent)
uv run layercode-create-app list-agents

# Run your agent
uv run layercode-create-app run --agent my-agent --tunnel
```

## Advanced Patterns

### Context Management

Maintain conversation context across turns:

```python
from typing import Any

class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.context: dict[str, Any] = {}

    async def process(self, event: LayercodeEvent) -> str:
        # Store context
        self.context[event.call_id] = {
            "user_id": event.user_id,
            "history": event.conversation_history,
        }

        # Use context in agent run
        result = await self.agent.run(
            event.transcript,
            deps=self.context[event.call_id],
        )
        return result.data
```

### External API Integration

Call external services in your tools:

```python
import httpx

@tool
async def get_weather(self, ctx: RunContext, city: str) -> str:
    """Get current weather for a city."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/v1/current",
            params={"city": city, "api_key": ctx.deps["weather_api_key"]},
        )
        data = response.json()
        return f"Weather in {city}: {data['temp']}°F, {data['conditions']}"
```

### Custom Event Handling

Handle different event types:

```python
async def process(self, event: LayercodeEvent) -> str:
    match event.type:
        case "call_started":
            return await self.handle_start(event)

        case "transcript":
            return await self.handle_transcript(event)

        case "call_ended":
            await self.cleanup(event)
            return ""

        case "user_interrupted":
            return "Sorry, let me stop there. What did you need?"

        case _:
            return ""

async def handle_start(self, event: LayercodeEvent) -> str:
    # Custom start logic
    user_name = await self.lookup_user(event.user_id)
    return f"Hello {user_name}! How can I help you today?"
```

### Stateful Agents

Persist state between calls:

```python
import json
from pathlib import Path

class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.state_dir = Path("agent_state")
        self.state_dir.mkdir(exist_ok=True)

    async def save_state(self, call_id: str, state: dict) -> None:
        """Persist agent state."""
        state_file = self.state_dir / f"{call_id}.json"
        with state_file.open("w") as f:
            json.dump(state, f)

    async def load_state(self, call_id: str) -> dict:
        """Load persisted state."""
        state_file = self.state_dir / f"{call_id}.json"
        if state_file.exists():
            with state_file.open() as f:
                return json.load(f)
        return {}
```

## Testing Your Agent

### Unit Tests

Create `tests/test_my_agent.py`:

```python
import pytest
from layercode_create_app.agents.my_agent import MyAgent
from layercode_create_app.sdk.events import LayercodeEvent

@pytest.mark.asyncio
async def test_call_started():
    agent = MyAgent(model="openai:gpt-5-nano")
    event = LayercodeEvent(type="call_started", call_id="test-123")

    response = await agent.process(event)
    assert response == "Hello! I'm here to help with your AcmeCorp needs."

@pytest.mark.asyncio
async def test_lookup_order():
    agent = MyAgent(model="openai:gpt-5-nano")
    result = await agent.lookup_order(ctx=None, order_id="ORD-123")

    assert "ORD-123" in result
```

### Manual Testing

Test with the echo server locally:

```bash
# Start your agent with verbose logging
uv run layercode-create-app run --agent my-agent --verbose

# In another terminal, send a test webhook
curl -X POST http://localhost:8000/api/agent \
  -H "Content-Type: application/json" \
  -d '{"type": "call_started", "call_id": "test-123"}'
```

## Best Practices

1. **Keep prompts focused** - Clear, specific instructions work best
2. **Document your tools** - Good docstrings help the AI use tools correctly
3. **Handle errors gracefully** - Catch exceptions and return helpful messages
4. **Test incrementally** - Start simple and add complexity gradually
5. **Use type hints** - Helps with IDE support and PydanticAI validation
6. **Log important events** - Use Loguru for debugging
7. **Version your prompts** - Track changes to system instructions

## Next Steps

- [API Reference](../api/agents.md) - Detailed API documentation
- [Observability](../guides/observability.md) - Monitor your agent
- [Deployment](../guides/deployment.md) - Deploy to production
