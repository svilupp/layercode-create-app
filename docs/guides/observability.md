# Observability Guide

Monitor and debug your LayerCode agents with structured logging and observability tools.

## Logging

### Loguru Integration

The toolkit uses [Loguru](https://github.com/Delgan/loguru) for structured logging.

#### Basic Logging

```python
from loguru import logger

logger.info("Processing webhook")
logger.warning("Rate limit approaching")
logger.error("Failed to connect to API")
```

#### Structured Logging

```python
logger.info(
    "Agent response generated",
    extra={
        "call_id": "call_123",
        "agent": "starter",
        "response_length": 150,
        "latency_ms": 450,
    }
)
```

#### Log Levels

Configure log level with the `--verbose` flag:

```bash
# INFO level (default)
uv run layercode-create-app run --agent starter

# DEBUG level
uv run layercode-create-app run --agent starter --verbose
```

#### Log Files

Configure log file rotation:

```python
from loguru import logger

logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    serialize=True,  # JSON format
)
```

## Logfire

[Logfire](https://logfire.pydantic.dev) provides advanced observability for FastAPI and PydanticAI.

### Setup

1. Sign up at [logfire.pydantic.dev](https://logfire.pydantic.dev)
2. Get your API token
3. Add to `.env`:

```env
LOGFIRE_TOKEN=lf_live_...
```

### Features

Logfire automatically instruments:

- **FastAPI requests** - Request/response timing, status codes
- **PydanticAI agents** - Agent runs, tool calls, model usage
- **Database queries** - SQL queries and timing
- **External API calls** - HTTP request tracking

### Viewing Data

Access your Logfire dashboard to:

- View request traces
- Analyze agent performance
- Monitor error rates
- Track model token usage
- Set up alerts

### Custom Spans

Add custom instrumentation:

```python
import logfire

async def process_order(order_id: str):
    with logfire.span("process_order", order_id=order_id):
        # Your order processing logic
        order = await fetch_order(order_id)

        with logfire.span("validate_order"):
            validate(order)

        with logfire.span("charge_payment"):
            await charge_customer(order)

        return order
```

### Performance Monitoring

Track agent performance:

```python
import logfire
from time import time

async def process(self, event: LayercodeEvent) -> str:
    start = time()

    try:
        result = await self.agent.run(event.transcript)

        logfire.info(
            "Agent completed",
            duration_ms=(time() - start) * 1000,
            call_id=event.call_id,
            agent=self.__class__.__name__,
        )

        return result.data

    except Exception as e:
        logfire.error(
            "Agent failed",
            error=str(e),
            call_id=event.call_id,
        )
        raise
```

## Metrics

### Key Metrics to Track

1. **Request Metrics**
   - Requests per minute
   - Response time (p50, p95, p99)
   - Error rate

2. **Agent Metrics**
   - Agent response time
   - Tool call frequency
   - Token usage
   - Success rate

3. **System Metrics**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk usage

### Custom Metrics

Track custom metrics with Logfire:

```python
import logfire

class MetricsCollector:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0

    async def track_request(self):
        self.request_count += 1
        logfire.metric("requests_total", self.request_count)

    async def track_error(self):
        self.error_count += 1
        logfire.metric("errors_total", self.error_count)

metrics = MetricsCollector()
```

## Alerting

### Logfire Alerts

Configure alerts in your Logfire dashboard:

1. **High Error Rate**
   - Condition: Error rate > 5%
   - Action: Send email/Slack notification

2. **Slow Response Times**
   - Condition: p95 latency > 2s
   - Action: Page on-call engineer

3. **High Token Usage**
   - Condition: Token usage > 1M/hour
   - Action: Send warning

### Custom Alerts

Implement custom alerting logic:

```python
import httpx

async def check_and_alert(metrics: dict):
    if metrics["error_rate"] > 0.05:
        await send_alert(
            severity="critical",
            message=f"High error rate: {metrics['error_rate']:.1%}",
        )

async def send_alert(severity: str, message: str):
    # Send to Slack
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            json={"text": f"[{severity.upper()}] {message}"}
        )
```

## Error Tracking

### Sentry Integration

Add Sentry for error tracking:

1. Install: `uv add sentry-sdk`
2. Configure:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project",
    traces_sample_rate=1.0,
)
```

3. Errors are automatically reported to Sentry

### Error Context

Add context to error reports:

```python
import sentry_sdk

async def process(self, event: LayercodeEvent) -> str:
    with sentry_sdk.configure_scope() as scope:
        scope.set_context("event", {
            "call_id": event.call_id,
            "agent_id": event.agent_id,
            "type": event.type,
        })

        try:
            result = await self.agent.run(event.transcript)
            return result.data
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise
```

## Debugging

### Debug Mode

Enable debug logging:

```bash
uv run layercode-create-app run --agent starter --verbose
```

### Request Tracing

Log all incoming requests:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(
            "Incoming request",
            method=request.method,
            path=request.url.path,
            headers=dict(request.headers),
        )

        response = await call_next(request)

        logger.debug(
            "Response",
            status_code=response.status_code,
        )

        return response
```

### Agent Debugging

Log agent internals:

```python
async def process(self, event: LayercodeEvent) -> str:
    logger.debug(f"Event received: {event.type}")
    logger.debug(f"Transcript: {event.transcript}")

    result = await self.agent.run(event.transcript)

    logger.debug(f"Agent result: {result.data}")
    logger.debug(f"Tool calls: {result.all_messages()}")

    return result.data
```

## Performance Profiling

### cProfile

Profile your agent:

```python
import cProfile
import pstats

async def profile_agent():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run agent
    await agent.process(event)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### Memory Profiling

Track memory usage:

```python
import tracemalloc

tracemalloc.start()

# Run your code
await agent.process(event)

current, peak = tracemalloc.get_traced_memory()
logger.info(f"Memory usage: {current / 1024 / 1024:.2f} MB (peak: {peak / 1024 / 1024:.2f} MB)")

tracemalloc.stop()
```

## Best Practices

1. **Log at appropriate levels**
   - DEBUG: Detailed diagnostic info
   - INFO: General informational messages
   - WARNING: Warning messages
   - ERROR: Error messages

2. **Include context**
   - Always include `call_id` and `agent_id`
   - Add relevant business context

3. **Avoid logging sensitive data**
   - Don't log API keys or tokens
   - Sanitize user data

4. **Use structured logging**
   - Log as JSON for easier parsing
   - Include consistent fields

5. **Monitor in production**
   - Set up alerts for critical issues
   - Review dashboards regularly

## Next Steps

- [Deployment Guide](deployment.md) - Deploy to production
- [Troubleshooting](troubleshooting.md) - Common issues
