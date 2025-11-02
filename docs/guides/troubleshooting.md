# Troubleshooting

Common issues and solutions for LayerCode agent development.

## Installation Issues

### uv not found

**Problem:** `command not found: uv`

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
uv --version
```

### Python version mismatch

**Problem:** `Python 3.12 or higher required`

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.12
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12

# macOS
brew install python@3.12
```

### Dependency conflicts

**Problem:** Package dependency resolution fails

**Solution:**
```bash
# Clear cache and reinstall
uv clean
uv sync --group dev

# If still failing, try with verbose output
uv sync --group dev --verbose
```

## Configuration Issues

### Missing environment variables

**Problem:** `LAYERCODE_API_KEY not found`

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Copy from example if missing
cp .env.example .env

# Edit with your credentials
nano .env

# Verify environment is loaded
uv run layercode-create-app run --verbose
```

### Invalid API keys

**Problem:** `401 Unauthorized` or `Invalid API key`

**Solution:**
1. Verify keys in LayerCode dashboard
2. Check for extra spaces or quotes in `.env`
3. Ensure you're using the correct environment (test vs live)

```env
# Correct format (no quotes)
LAYERCODE_API_KEY=lk_live_abc123
OPENAI_API_KEY=sk-abc123

# Incorrect format
LAYERCODE_API_KEY="lk_live_abc123"  # Remove quotes
```

### Wrong model specified

**Problem:** `Model not found: openai:gpt-3.5`

**Solution:**
```bash
# Use correct model format
uv run layercode-create-app run --agent starter --model openai:gpt-5-nano

# Check supported models
# OpenAI: openai:gpt-4, openai:gpt-5-nano
# Google: google:gemini-1.5-pro
```

## Webhook Issues

### Webhooks not received

**Problem:** No webhooks arriving at your endpoint

**Solution:**

1. **Verify tunnel is running:**
```bash
# Start with verbose logging
uv run layercode-create-app run --agent starter --tunnel --verbose

# Look for tunnel URL in output
# 🌐 Tunnel URL: https://abc-def.trycloudflare.com
```

2. **Check webhook URL in dashboard:**
   - Copy full URL including `/api/agent`
   - Example: `https://abc-def.trycloudflare.com/api/agent`

3. **Test endpoint manually:**
```bash
curl -X POST https://your-tunnel.trycloudflare.com/api/agent \
  -H "Content-Type: application/json" \
  -d '{"type":"call_started","call_id":"test"}'
```

4. **Check firewall/network:**
   - Ensure port 8000 is not blocked
   - Verify no VPN interfering with tunnel

### Signature verification fails

**Problem:** `401 Unauthorized - Invalid signature`

**Solution:**

1. **Verify webhook secret:**
```env
# Check secret matches LayerCode dashboard
LAYERCODE_WEBHOOK_SECRET=whsec_abc123
```

2. **Check for middleware issues:**
```python
# Ensure signature middleware is properly configured
# Should happen automatically, but verify in logs
```

3. **Disable verification for testing:**
```python
# Only for local debugging!
# In server/app.py, temporarily disable signature check
```

### Tunnel disconnects

**Problem:** Cloudflare tunnel keeps disconnecting

**Solution:**

1. **Restart tunnel:**
```bash
# Kill existing process
pkill cloudflared

# Restart with tunnel
uv run layercode-create-app run --agent starter --tunnel
```

2. **Use ngrok as alternative:**
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from ngrok.com

# Start server without tunnel
uv run layercode-create-app run --agent starter

# In another terminal, start ngrok
ngrok http 8000
```

## Agent Issues

### Agent not responding

**Problem:** Agent receives webhook but doesn't respond

**Solution:**

1. **Check logs:**
```bash
uv run layercode-create-app run --agent starter --verbose
```

2. **Verify AI provider credentials:**
```env
# Check API key is valid
OPENAI_API_KEY=sk-...
```

3. **Test with echo agent:**
```bash
# Echo agent doesn't need AI provider
uv run layercode-create-app run --agent echo
```

### Slow responses

**Problem:** Agent takes too long to respond

**Solution:**

1. **Use faster model:**
```bash
# Switch to faster model
uv run layercode-create-app run --agent starter --model openai:gpt-5-nano
```

2. **Check network latency:**
```bash
# Ping OpenAI
ping api.openai.com
```

3. **Enable streaming:**
```python
# Ensure your agent uses streaming for long responses
async for chunk in self.agent.stream(event.transcript):
    yield chunk
```

### Tool calls failing

**Problem:** Agent's tools are not working correctly

**Solution:**

1. **Check tool signatures:**
```python
# Ensure tool parameters match what AI expects
@tool
async def my_tool(
    self,
    ctx: RunContext,
    param: str  # Type hints are important!
) -> str:
    """Clear docstring helps AI use tool correctly."""
    pass
```

2. **Test tool independently:**
```python
# Unit test your tools
result = await agent.my_tool(ctx=None, param="test")
assert result is not None
```

3. **Check tool permissions:**
```python
# Ensure tool has access to needed resources
@tool
async def fetch_data(self, ctx: RunContext) -> str:
    # Check ctx.deps has required dependencies
    if "api_key" not in ctx.deps:
        return "API key not configured"
```

## Server Issues

### Port already in use

**Problem:** `Address already in use: 0.0.0.0:8000`

**Solution:**

1. **Use different port:**
```bash
uv run layercode-create-app run --agent starter --port 8001
```

2. **Kill existing process:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)
```

### Server crashes on start

**Problem:** Server exits immediately after starting

**Solution:**

1. **Check for Python errors:**
```bash
# Run with verbose logging
uv run layercode-create-app run --agent starter --verbose
```

2. **Verify all files:**
```bash
# Ensure no syntax errors
uv run ruff check .
uv run mypy layercode_create_app
```

3. **Check dependencies:**
```bash
# Reinstall dependencies
uv sync --group dev
```

## Development Issues

### Type checking errors

**Problem:** `mypy` reports type errors

**Solution:**

1. **Add type hints:**
```python
# Add proper type hints
async def process(self, event: LayercodeEvent) -> str:
    pass
```

2. **Use type ignore sparingly:**
```python
# Only when absolutely necessary
result = some_untyped_library()  # type: ignore
```

### Linting errors

**Problem:** `ruff` reports formatting issues

**Solution:**
```bash
# Auto-fix most issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Tests failing

**Problem:** `pytest` tests fail

**Solution:**

1. **Run tests with verbose output:**
```bash
uv run pytest -v
```

2. **Run specific test:**
```bash
uv run pytest tests/test_my_feature.py::test_specific_case -v
```

3. **Check test isolation:**
```python
# Ensure tests clean up after themselves
@pytest.fixture
async def agent():
    agent = MyAgent(model="openai:gpt-5-nano")
    yield agent
    # Cleanup
    await agent.cleanup()
```

## Performance Issues

### High memory usage

**Problem:** Agent consuming too much memory

**Solution:**

1. **Clear conversation history:**
```python
# Limit history size
def _build_history(self, event: LayercodeEvent) -> list:
    history = event.conversation_history
    # Keep only last 10 messages
    return history[-10:]
```

2. **Use memory profiling:**
```python
import tracemalloc

tracemalloc.start()
# Run your code
current, peak = tracemalloc.get_traced_memory()
print(f"Memory: {current / 1024 / 1024:.2f} MB")
tracemalloc.stop()
```

### High latency

**Problem:** Response times are too slow

**Solution:**

1. **Profile your code:**
```bash
uv run python -m cProfile -s cumulative your_script.py
```

2. **Use async properly:**
```python
# Don't block the event loop
async def slow_operation():
    # Good: use async operations
    result = await httpx.get(url)

    # Bad: blocking call
    # result = requests.get(url)  # Don't do this!
```

3. **Cache expensive operations:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_computation(param: str) -> str:
    # This will be cached
    pass
```

## Getting Help

If you're still stuck:

1. **Check the logs:**
```bash
uv run layercode-create-app run --agent starter --verbose 2>&1 | tee debug.log
```

2. **Search GitHub issues:**
   - [LayerCode Create App Issues](https://github.com/svilupp/layercode-create-app/issues)

3. **Create a new issue:**
   - Include logs, error messages, and steps to reproduce
   - Mention your OS, Python version, and configuration

4. **Join the community:**
   - LayerCode Discord
   - Community forums

## Common Error Messages

### `Agent not found: my-agent`

Register your agent with `@agent` decorator.

### `Event type not supported: unknown_type`

Handle all event types in your `process` method.

### `Failed to load prompt: prompts/missing.txt`

Ensure prompt file exists in `src/src/layercode_create_app/agents/prompts/`.

### `Connection refused`

Server not running or firewall blocking connection.

### `Too many requests`

Hitting rate limits - implement backoff/retry logic.

## Next Steps

- [Deployment Guide](deployment.md) - Production deployment
- [Observability Guide](observability.md) - Monitoring and debugging
