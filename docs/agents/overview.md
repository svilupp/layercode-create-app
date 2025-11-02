# Agents Overview

Agents in layercode-create-app are conversational AI assistants that handle voice interactions through the LayerCode platform. They process webhooks, manage conversation state, and stream responses back to users.

## Architecture

All agents inherit from the `BaseLayercodeAgent` interface and are powered by [PydanticAI](https://ai.pydantic.dev/). The architecture consists of:

- **Agent Class**: Implements conversation logic and tool definitions
- **Prompt Files**: Define system prompts and instructions
- **SDK Integration**: Handles webhook verification and SSE streaming
- **Server Layer**: FastAPI endpoints for webhook handling

## Agent Lifecycle

```
┌─────────────────┐
│ LayerCode Call  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Webhook Verify  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Agent Process   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SSE Stream Back │
└─────────────────┘
```

1. **Webhook Reception**: LayerCode sends conversation events to your endpoint
2. **Verification**: Webhook signature is verified using your secret
3. **Agent Processing**: Agent receives event and generates response
4. **Streaming**: Response is streamed back via Server-Sent Events (SSE)

## Built-in Agents

The toolkit includes three reference agents:

- **echo**: Deterministic responses without AI
- **starter**: General-purpose conversational assistant
- **bakery**: Example with custom tools and business logic

See [Built-in Agents](built-in.md) for detailed documentation.

## Agent Registration

Agents are registered using the `@agent` decorator:

```python
from layercode_create_app.agents.base import BaseLayercodeAgent, agent

@agent("my-agent")
class MyAgent(BaseLayercodeAgent):
    async def process(self, event):
        # Your logic here
        pass
```

## Agent Prompts

Prompts are stored in `src/src/layercode_create_app/agents/prompts/` as text files. They support variable interpolation and are loaded at runtime.

Example prompt structure:

```
You are a helpful assistant for {company_name}.

Current conversation context:
{context}

User message: {message}

Respond naturally and helpfully.
```

## Next Steps

- [Built-in Agents](built-in.md) - Explore included examples
- [Creating Custom Agents](custom.md) - Build your own agent
- [API Reference](../api/agents.md) - Detailed API documentation
