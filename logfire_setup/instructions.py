"""Generate Logfire usage instructions for AGENTS.md/CLAUDE.md files."""

from logfire_setup.categories import Integration


def generate_core_instructions() -> str:
    """Generate core Logfire instructions that are always included."""
    return """# Logfire

## Setup

```python
import logfire

logfire.configure(send_to_logfire='if-token-present')
```

For production, use the `LOGFIRE_TOKEN` environment variable with write tokens.

## Logging Patterns

### Spans

Spans create parent-child relationships and measure duration:

```python
with logfire.span('processing_order', order_id=order_id):
    # Your code here
    pass
```

### F-Strings (Python 3.11+)

Logfire automatically extracts variable names from f-strings:

```python
logfire.info(f'Hello {name}')  # Automatically sets name attribute
```

Disable with `logfire.configure(inspect_arguments=False)` if needed.

### Structured Attributes

Pass structured data as keyword arguments:

```python
logfire.info('Operation complete', status='success', duration_ms=123)
```

### Exception Handling

Unhandled exceptions are automatically recorded. For caught exceptions:

```python
try:
    risky_operation()
except Exception as e:
    logfire.exception('Operation failed', error_type=type(e).__name__)
```

### Function Tracing

```python
@logfire.instrument()  # Must be first/outermost decorator
def my_function(x, y):
    return x + y
```

## Log Levels

Available: trace, debug, info, notice, warn, error, fatal

```python
with logfire.span('debug_operation', _level='debug'):
    pass
```

## Data Privacy

Logfire automatically scrubs passwords, secrets, API keys, cookies, session tokens, credit cards, SSNs, and JWT tokens.

Use message templates for structured data rather than string concatenation to ensure proper scrubbing.

## Resources

- Docs: https://logfire.pydantic.dev/docs/
- API Reference: https://logfire.pydantic.dev/docs/reference/api/logfire/
"""


def generate_integration_instructions(integrations: list[Integration]) -> str:
    """Generate integration-specific instructions based on selected integrations."""
    if not integrations:
        return ""

    instructions = "\n## Instrumentation\n\n```python\n"
    instructions += (
        "import logfire\n\nlogfire.configure(send_to_logfire='if-token-present')\n"
    )

    # Group by common patterns
    web_frameworks: list[Integration] = []
    http_clients: list[Integration] = []
    databases: list[Integration] = []
    llm_ai: list[Integration] = []
    other: list[Integration] = []

    for integration in integrations:
        if integration.extra in ["fastapi", "django", "flask", "starlette"]:
            web_frameworks.append(integration)
        elif integration.extra in ["httpx", "requests", "aiohttp-client"]:
            http_clients.append(integration)
        elif integration.extra in [
            "sqlalchemy",
            "asyncpg",
            "psycopg",
            "psycopg2",
            "pymongo",
            "redis",
            "mysql",
        ]:
            databases.append(integration)
        elif integration.extra in ["google-genai", "litellm"]:
            llm_ai.append(integration)
        else:
            other.append(integration)

    # Add web framework instrumentation
    if web_frameworks:
        instructions += "\n# Web framework\n"
        for integration in web_frameworks:
            if integration.extra == "fastapi":
                instructions += "logfire.instrument_fastapi(app)\n"
            elif integration.extra == "django":
                instructions += "logfire.instrument_django()\n"
            elif integration.extra == "flask":
                instructions += "logfire.instrument_flask(app)\n"
            elif integration.extra == "starlette":
                instructions += "logfire.instrument_starlette(app)\n"

    # Add HTTP client instrumentation
    if http_clients:
        instructions += "\n# HTTP clients\n"
        for integration in http_clients:
            if integration.extra == "httpx":
                instructions += "# Global instrumentation (all clients)\n"
                instructions += "logfire.instrument_httpx()\n\n"
                instructions += "# Per-client instrumentation\n"
                instructions += "async with httpx.AsyncClient() as client:\n"
                instructions += "    logfire.instrument_httpx(client)\n\n"
                instructions += "# Capture all request/response data\n"
                instructions += "async with httpx.AsyncClient() as client:\n"
                instructions += "    logfire.instrument_httpx(client, capture_request_json_body=True, capture_response_json_body=True)\n"
            elif integration.extra == "requests":
                instructions += "logfire.instrument_requests()\n"
            elif integration.extra == "aiohttp-client":
                instructions += "logfire.instrument_aiohttp_client()\n"

    # Add database instrumentation
    if databases:
        instructions += "\n# Databases\n"
        for integration in databases:
            if integration.extra == "sqlalchemy":
                instructions += "logfire.instrument_sqlalchemy(engine=engine)\n"
            elif integration.extra in ["asyncpg", "psycopg", "psycopg2"]:
                instructions += f"# {integration.display_name} is auto-instrumented\n"
            elif integration.extra == "pymongo":
                instructions += "logfire.instrument_pymongo()\n"
            elif integration.extra == "redis":
                instructions += "logfire.instrument_redis()\n"

    # Add LLM/AI instrumentation
    if llm_ai:
        instructions += "\n# LLM & AI\n"
        instructions += "# Pydantic AI (built-in instrumentation)\n"
        instructions += "logfire.instrument_pydantic_ai()\n\n"
        for integration in llm_ai:
            if integration.extra == "google-genai":
                instructions += (
                    "# Google GenAI auto-instrumentation via opentelemetry\n"
                )
            elif integration.extra == "litellm":
                instructions += "# LiteLLM auto-instrumentation via openinference\n"

    # Add other instrumentation
    if other:
        instructions += "\n# Other\n"
        for integration in other:
            if integration.extra == "celery":
                instructions += "logfire.instrument_celery()\n"
            elif integration.extra == "system-metrics":
                instructions += "logfire.instrument_system_metrics()\n"

    instructions += "```\n\n"
    instructions += "For detailed integration docs, see: https://logfire.pydantic.dev/docs/integrations/\n"

    return instructions


def generate_mcp_instructions() -> str:
    """Generate instructions for using Logfire MCP."""
    return """
## Using Logfire MCP

The Logfire MCP (Model Context Protocol) server is configured for this project. Use it to:

- **Query your Logfire data** during development
- **Debug issues** by inspecting traces, spans, and logs

"""


def generate_instructions(
    selected_integrations: list[Integration], mcp_configured: bool = False
) -> str:
    """
    Generate complete Logfire instructions based on selected integrations.

    Args:
        selected_integrations: List of Integration objects that were selected.
        mcp_configured: Whether the Logfire MCP server is configured.

    Returns:
        Complete instructions text ready to be added to AGENTS.md/CLAUDE.md.
    """
    instructions = generate_core_instructions()

    if mcp_configured:
        instructions += generate_mcp_instructions()

    if selected_integrations:
        instructions += generate_integration_instructions(selected_integrations)

    return instructions
