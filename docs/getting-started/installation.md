# Installation

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Install Dependencies

Clone the repository and install dependencies using uv:

```bash
git clone https://github.com/svilupp/layercode-create-app.git
cd layercode-create-app
uv sync --group dev
```

This will install all required dependencies including:

- FastAPI and Uvicorn for the web server
- PydanticAI for agent orchestration
- Logfire and Loguru for observability
- Development tools (pytest, mypy, ruff)

## Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required - Get these from your LayerCode dashboard
LAYERCODE_API_KEY=lk_live_...
LAYERCODE_WEBHOOK_SECRET=whsec_...

# Required - Your AI provider API key
OPENAI_API_KEY=sk-...
# OR for Google models:
# GOOGLE_GENERATIVEAI_API_KEY=...

# Optional
LOGFIRE_TOKEN=lf_...
DEFAULT_MODEL=openai:gpt-5-nano
```

### Getting LayerCode Credentials

1. Sign up at [LayerCode](https://layercode.com)
2. Create a new agent in the dashboard
3. Copy your API key and webhook secret
4. Paste them into your `.env` file

### AI Provider Setup

You'll need an API key from one of the supported providers:

- **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com)
- **Google**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Verify Installation

Test that everything is working:

```bash
# List available agents
uv run layercode-create-app list-agents

# Run the echo agent (doesn't require AI credentials)
uv run layercode-create-app run --agent echo
```

You should see the server start on `http://0.0.0.0:8000`.

## Next Steps

- [Quickstart Guide](quickstart.md) - Run your first agent
- [Configuration](configuration.md) - Learn about all configuration options
