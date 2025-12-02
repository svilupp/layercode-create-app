# CLI Reference

Complete reference for the `layercode-create-app` command-line interface.

## Commands

### `run`

Start the FastAPI server with a specified agent.

```bash
uv run layercode-create-app run [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--agent` | string | `starter` | Agent to run (echo, starter, bakery, or custom) |
| `--model` | string | from env | AI model identifier (e.g., `openai:gpt-4`) |
| `--host` | string | `0.0.0.0` | Server host binding |
| `--port` | integer | `8000` | Server port |
| `--agent-route` | string | `/api/agent` | Webhook endpoint path |
| `--authorize-route` | string | `/api/authorize` | Authorization endpoint path |
| `--tunnel` | flag | `False` | Launch Cloudflare tunnel |
| `--agent-id` | string | from env | Agent ID for webhook auto-update |
| `--unsafe-update-webhook` | flag | `False` | Auto-update agent webhook to tunnel URL |
| `--env-file` | path | `.env` | Environment file to load |
| `--verbose`, `-v` | flag | `False` | Enable debug logging |

**Examples:**

Run the starter agent:
```bash
uv run layercode-create-app run --agent starter
```

Run with a Cloudflare tunnel:
```bash
uv run layercode-create-app run --agent bakery --tunnel
```

Run on a custom port with verbose logging:
```bash
uv run layercode-create-app run --port 3000 --verbose
```

Use a specific AI model:
```bash
uv run layercode-create-app run --agent starter --model openai:gpt-4
```

Auto-update webhook URL for quick testing:
```bash
uv run layercode-create-app run --tunnel --unsafe-update-webhook --agent-id agent_xxx
```

### `list-agents`

List all available agents (built-in and custom).

```bash
uv run layercode-create-app list-agents
```

**Output:**
```
Available agents:
  - echo
  - starter
  - bakery
```

## Global Options

Available for all commands:

```bash
--env-file PATH    # Load environment from file
--verbose, -v      # Enable debug logging
--help, -h         # Show help message
```

## Environment Variables

The CLI loads environment variables from `.env` by default. Override with `--env-file`.

### Required Variables

```env
LAYERCODE_API_KEY=lk_live_...
LAYERCODE_WEBHOOK_SECRET=whsec_...
OPENAI_API_KEY=sk-...  # or GOOGLE_GENERATIVEAI_API_KEY
```

### Optional Variables

```env
DEFAULT_MODEL=openai:gpt-5-nano
LOGFIRE_TOKEN=lf_...
LAYERCODE_AGENT_ID=agent_...  # For --unsafe-update-webhook
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Agent not found |

## Usage Examples

### Development Workflow

```bash
# Start with verbose logging
uv run layercode-create-app run --verbose

# In another terminal, check logs
tail -f logs/app.log
```

### Testing Multiple Agents

```bash
# Terminal 1
uv run layercode-create-app run --agent echo --port 8000

# Terminal 2
uv run layercode-create-app run --agent starter --port 8001

# Terminal 3
uv run layercode-create-app run --agent bakery --port 8002
```

### Production-like Setup

```bash
# Use production env file
uv run layercode-create-app run \
  --env-file .env.production \
  --agent starter \
  --host 0.0.0.0 \
  --port 8000
```

### Custom Agent

```bash
# Run your custom agent
uv run layercode-create-app run --agent my-custom-agent --tunnel
```

## Next Steps

- [SDK Reference](sdk.md) - SDK API documentation
- [Configuration Guide](../getting-started/configuration.md) - Detailed configuration
