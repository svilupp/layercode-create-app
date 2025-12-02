# Configuration

## Environment Variables

The toolkit uses environment variables for configuration. All variables are loaded from `.env` by default.

### Required Variables

```env
# LayerCode credentials
LAYERCODE_API_KEY=lk_live_...
LAYERCODE_WEBHOOK_SECRET=whsec_...

# AI provider API key (choose one)
OPENAI_API_KEY=sk-...
# OR
GOOGLE_GENERATIVEAI_API_KEY=...
```

### Optional Variables

```env
# Default model for PydanticAI
DEFAULT_MODEL=openai:gpt-5-nano

# Logfire token for observability
LOGFIRE_TOKEN=lf_...

# LayerCode agent ID (for --unsafe-update-webhook)
LAYERCODE_AGENT_ID=agent_...
```

## CLI Configuration

### Global Flags

Available for all commands:

```bash
--env-file PATH    # Path to .env file (default: .env)
--verbose, -v      # Enable debug logging
```

### Run Command Flags

Configure the `run` command:

```bash
--agent NAME           # Agent to run (default: starter)
--model MODEL          # AI model identifier
--host HOST            # Server host (default: 0.0.0.0)
--port PORT            # Server port (default: 8000)
--agent-route PATH     # Webhook route (default: /api/agent)
--authorize-route PATH # Auth route (default: /api/authorize)
--tunnel               # Enable Cloudflare tunnel
--agent-id ID          # Agent ID for webhook auto-update
--unsafe-update-webhook # Auto-update webhook to tunnel URL
```

## Model Configuration

### Supported Models

PydanticAI supports multiple providers. Specify models using the format `provider:model-name`:

**OpenAI:**
```bash
--model openai:gpt-5-nano
--model openai:gpt-4
--model openai:gpt-4-turbo
```

**Google:**
```bash
--model google:gemini-1.5-pro
--model google:gemini-1.5-flash
```

### Setting a Default Model

In your `.env`:

```env
DEFAULT_MODEL=openai:gpt-5-nano
```

Or via CLI:

```bash
uv run layercode-create-app run --agent starter --model openai:gpt-4
```

## Server Configuration

### Host and Port

By default, the server binds to `0.0.0.0:8000`. Change this:

```bash
uv run layercode-create-app run --host 127.0.0.1 --port 3000
```

### Custom Routes

Customize webhook endpoints:

```bash
uv run layercode-create-app run \
  --agent-route /webhooks/agent \
  --authorize-route /webhooks/auth
```

## Tunnel Configuration

The Cloudflare tunnel provides a temporary public URL for local development.

### Enable Tunnel

```bash
uv run layercode-create-app run --tunnel
```

The tunnel URL will be printed to the console. Copy the full webhook URL to your LayerCode dashboard.

### Auto-Update Webhook

For quick testing, automatically update your LayerCode agent's webhook URL:

```bash
uv run layercode-create-app run --tunnel --unsafe-update-webhook
```

This requires `LAYERCODE_AGENT_ID` in your `.env` (or `--agent-id` flag). On shutdown, the previous webhook URL is automatically restored.

### Tunnel Logs

Enable verbose logging to see tunnel activity:

```bash
uv run layercode-create-app run --tunnel --verbose
```

## Logging Configuration

### Log Levels

- Default: `INFO`
- Verbose (`-v`): `DEBUG`

### Logfire Integration

If `LOGFIRE_TOKEN` is set in `.env`, Logfire instrumentation is automatically enabled for:

- FastAPI requests
- PydanticAI agent runs
- Custom application logs

Learn more at [logfire.pydantic.dev](https://logfire.pydantic.dev)

## Advanced Configuration

### Custom Environment Files

Use a different environment file:

```bash
uv run layercode-create-app run --env-file .env.production
```

### Multiple Agents

Run different agents on different ports:

```bash
# Terminal 1
uv run layercode-create-app run --agent starter --port 8000

# Terminal 2
uv run layercode-create-app run --agent bakery --port 8001
```

## Next Steps

- [Built-in Agents](../agents/built-in.md) - Explore included agents
- [Observability Guide](../guides/observability.md) - Set up monitoring
- [Troubleshooting](../guides/troubleshooting.md) - Common issues
