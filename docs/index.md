# LayerCode Create App

!!! warning "Early Alpha"
    This toolkit is an early alpha (v0.0.1) and may contain bugs or breaking changes. Please test thoroughly before using in production.

**layercode-create-app** is a lightweight toolkit for spinning up LayerCode-compliant FastAPI backends with a single command.

## Features

- **Typed LayerCode SDK primitives** for webhook payloads, signature verification, and SSE streaming
- **Ready-to-run agents** (echo, starter, bakery) powered by [PydanticAI](https://ai.pydantic.dev/)
- **Observability hooks** for Logfire + Loguru
- **An ergonomic CLI** for running the server locally and optionally tunnelling via Cloudflare

## Quick Example

```bash
# Install dependencies
uv sync --group dev

# Run the starter agent
uv run layercode-create-app run --agent starter

# Expose with Cloudflare tunnel
uv run layercode-create-app run --agent bakery --tunnel
```

## Why layercode-create-app?

This toolkit gives teams an opinionated but hackable starting point for LayerCode voice agents. It handles the boilerplate of webhook verification, SSE streaming, and agent orchestration so you can focus on building your conversational logic.

## Next Steps

- [Installation](getting-started/installation.md) - Set up your development environment
- [Quickstart](getting-started/quickstart.md) - Run your first agent in minutes
- [Built-in Agents](agents/built-in.md) - Explore the included agent examples
- [Creating Custom Agents](agents/custom.md) - Build your own voice agents
