# Agents API Reference

Complete API reference for agent development.

## Base Classes

### `BaseLayercodeAgent`

Abstract base class for all agents.

```python
from layercode_create_app.agents.base import BaseLayercodeAgent

class BaseLayercodeAgent(ABC):
    """Base class for LayerCode agents."""

    def __init__(self, model: Model):
        """Initialize agent.

        Args:
            model: PydanticAI model instance
        """
        self.model = model

    @abstractmethod
    async def process(self, event: LayercodeEvent) -> str:
        """Process an event and return response.

        Args:
            event: Incoming LayerCode event

        Returns:
            Agent response text
        """
        pass

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file.

        Args:
            filename: Prompt file name (in prompts/ directory)

        Returns:
            Prompt text
        """
        pass
```

## Agent Registration

### `@agent` Decorator

Register an agent for use with the CLI.

```python
from layercode_create_app.agents.base import agent

@agent("agent-name")
class MyAgent(BaseLayercodeAgent):
    """My custom agent."""
    pass
```

**Parameters:**

- `name` (str): Agent identifier used in CLI `--agent` flag

## PydanticAI Integration

### Creating an Agent

```python
from pydantic_ai import Agent

class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)

        self.agent = Agent(
            model=model,
            system_prompt="You are a helpful assistant.",
            retries=2,
        )
```

### Running the Agent

```python
async def process(self, event: LayercodeEvent) -> str:
    if event.type == "transcript":
        result = await self.agent.run(
            event.transcript,
            message_history=self._build_history(event),
        )
        return result.data
    return ""
```

## Tools

### Defining Tools

Use the `@tool` decorator to define agent tools:

```python
from pydantic_ai import tool, RunContext

class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.agent = Agent(model=model, system_prompt="...")

        # Register tools
        self.agent.tool(self.my_tool)

    @tool
    async def my_tool(
        self,
        ctx: RunContext,
        param: str
    ) -> str:
        """Tool description for the AI.

        Args:
            ctx: Run context with dependencies
            param: Parameter description

        Returns:
            Tool result
        """
        # Tool implementation
        return f"Result: {param}"
```

### Tool Context

Access dependencies via `RunContext`:

```python
@tool
async def lookup_user(self, ctx: RunContext, user_id: str) -> str:
    """Look up user information."""
    # Access dependencies
    db = ctx.deps["database"]
    user = await db.get_user(user_id)
    return user.name
```

## Event Handling

### Event Types

Handle different event types in your `process` method:

```python
async def process(self, event: LayercodeEvent) -> str:
    match event.type:
        case "call_started":
            return await self._handle_start(event)

        case "transcript":
            return await self._handle_transcript(event)

        case "call_ended":
            await self._handle_end(event)
            return ""

        case "user_interrupted":
            return "Let me stop there."

        case _:
            return ""
```

### Event Properties

```python
class LayercodeEvent:
    type: str              # Event type
    call_id: str           # Unique call ID
    agent_id: str          # Agent identifier
    timestamp: datetime    # Event timestamp
    transcript: str | None # User transcript
    metadata: dict         # Additional data
```

## Response Streaming

### Streaming Responses

For long-running agents, stream responses:

```python
async def process(self, event: LayercodeEvent) -> str:
    if event.type == "transcript":
        # Stream the response
        async for chunk in self.agent.stream(event.transcript):
            yield chunk
```

### Handling Interruptions

Handle user interruptions gracefully:

```python
async def process(self, event: LayercodeEvent) -> str:
    if event.type == "user_interrupted":
        # Stop current processing
        await self._cancel_current_task()
        return "Sorry about that. What did you need?"

    # ... rest of processing
```

## State Management

### Instance State

Store state on the agent instance:

```python
class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.conversations: dict[str, list] = {}

    async def process(self, event: LayercodeEvent) -> str:
        # Store conversation state
        if event.call_id not in self.conversations:
            self.conversations[event.call_id] = []

        self.conversations[event.call_id].append({
            "type": event.type,
            "transcript": event.transcript,
        })

        # Use state in processing
        history = self.conversations[event.call_id]
        # ...
```

### External State

Use databases or caches for persistent state:

```python
import redis

class MyAgent(BaseLayercodeAgent):
    def __init__(self, model: Model):
        super().__init__(model)
        self.redis = redis.Redis(host="localhost")

    async def process(self, event: LayercodeEvent) -> str:
        # Load state from Redis
        state = self.redis.get(f"call:{event.call_id}")

        # ... processing ...

        # Save state
        self.redis.set(f"call:{event.call_id}", new_state)
```

## Testing

### Mocking Events

Create test events for unit tests:

```python
import pytest
from layercode_create_app.sdk.events import LayercodeEvent

@pytest.mark.asyncio
async def test_agent():
    agent = MyAgent(model="openai:gpt-5-nano")

    event = LayercodeEvent(
        type="call_started",
        call_id="test-123",
        agent_id="my-agent",
        timestamp=datetime.now(),
        transcript=None,
        metadata={},
    )

    response = await agent.process(event)
    assert response == "Expected greeting"
```

### Testing Tools

Test tools independently:

```python
@pytest.mark.asyncio
async def test_tool():
    agent = MyAgent(model="openai:gpt-5-nano")

    result = await agent.my_tool(
        ctx=RunContext(deps={"key": "value"}),
        param="test",
    )

    assert "test" in result
```

## Best Practices

1. **Type Hints** - Use type hints for all methods and parameters
2. **Async/Await** - Make all I/O operations async
3. **Error Handling** - Catch and handle exceptions gracefully
4. **Logging** - Use structured logging for debugging
5. **Docstrings** - Document all tools and methods
6. **Testing** - Write tests for your agents and tools

## Example Agent

Complete example agent:

```python
from pydantic_ai import Agent, RunContext, tool
from pydantic_ai.models import Model

from layercode_create_app.agents.base import BaseLayercodeAgent, agent
from layercode_create_app.sdk.events import LayercodeEvent


@agent("example")
class ExampleAgent(BaseLayercodeAgent):
    """Example agent with tools."""

    def __init__(self, model: Model):
        super().__init__(model)

        prompt = self._load_prompt("example.txt")

        self.agent = Agent(
            model=model,
            system_prompt=prompt,
        )

        self.agent.tool(self.get_time)

    @tool
    async def get_time(self, ctx: RunContext) -> str:
        """Get the current time."""
        from datetime import datetime
        return datetime.now().strftime("%I:%M %p")

    async def process(self, event: LayercodeEvent) -> str:
        if event.type == "call_started":
            return "Hello! How can I help you?"

        elif event.type == "transcript":
            result = await self.agent.run(event.transcript)
            return result.data

        return ""
```

## Next Steps

- [Creating Custom Agents](../agents/custom.md) - Detailed guide
- [Built-in Agents](../agents/built-in.md) - Example implementations
