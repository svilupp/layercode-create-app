# Quickstart

This guide will walk you through running your first LayerCode agent in minutes.

## Prerequisites

Make sure you've completed the [Installation](installation.md) steps and have your `.env` file configured.

## Run Your First Agent

### 1. List Available Agents

See what agents are available:

```bash
uv run layercode-create-app list-agents
```

You should see:

- `echo` - Simple deterministic agent (no AI required)
- `starter` - General-purpose conversational assistant
- `bakery` - Example agent with tool calling for bakery operations

### 2. Run the Starter Agent

Start the starter agent locally:

```bash
uv run layercode-create-app run --agent starter --port 8000
```

The server will start at `http://0.0.0.0:8000`. You'll see logs indicating:

- Environment variables loaded
- FastAPI server initialized
- Webhook endpoints registered

### 3. Expose with Cloudflare Tunnel

To receive webhooks from LayerCode, you need a public URL. Use the built-in tunnel:

```bash
uv run layercode-create-app run --agent starter --tunnel
```

This will:

1. Start the FastAPI server
2. Launch a Cloudflare quick tunnel
3. Print the public webhook URL

Look for output like:

```
🌐 Tunnel URL: https://abc-def-ghi.trycloudflare.com
📍 Webhook endpoint: https://abc-def-ghi.trycloudflare.com/api/agent
```

### 4. Configure LayerCode Dashboard

1. Go to your LayerCode dashboard
2. Navigate to your agent's settings
3. Paste the webhook endpoint URL into the webhook field
4. Save the configuration

### 5. Test Your Agent

Make a test call to your LayerCode agent. The webhook should be received by your local server, and you'll see logs in your terminal.

## CLI Options

Common flags for the `run` command:

| Option | Default | Description |
|--------|---------|-------------|
| `--agent` | `starter` | Which agent to run |
| `--model` | from `.env` | AI model to use |
| `--host` | `0.0.0.0` | Server host |
| `--port` | `8000` | Server port |
| `--tunnel` | `False` | Enable Cloudflare tunnel |
| `--verbose`, `-v` | `False` | Enable debug logging |

## Example Commands

Run the bakery agent with a specific model:

```bash
uv run layercode-create-app run \
  --agent bakery \
  --model openai:gpt-4 \
  --tunnel
```

Run with verbose logging:

```bash
uv run layercode-create-app run --agent starter --tunnel --verbose
```

## Next Steps

- [Configuration Guide](configuration.md) - Learn about all configuration options
- [Built-in Agents](../agents/built-in.md) - Explore the included agents
- [Creating Custom Agents](../agents/custom.md) - Build your own agent
