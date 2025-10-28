# logfire-setup

Interactive CLI to set up [Pydantic Logfire](https://logfire.pydantic.dev/) with optional dependencies.

https://github.com/user-attachments/assets/f41ff97f-6e84-4425-a752-7d0623954414

## What is this?

`logfire-setup` is a CLI tool that helps you quickly add Logfire to your Python project with an interactive setup process similar to `create-next-app`. It:

- **Interactive selection** with arrow keys and checkboxes for an intuitive user experience
- **Checks authentication** - Validates your Logfire credentials automatically
- **Project selection** - Fetches your projects and runs `logfire projects use` to configure your project
- **Auto-detects** your existing dependencies (FastAPI, Django, SQLAlchemy, etc.)
- **Pre-selects** matching Logfire integrations
- **Installs** Logfire with your chosen extras using `uv`
- **Validates environment** - Checks for LOGFIRE_TOKEN and MCP configuration
- **Generates** best practices documentation for your `AGENTS.md` or `CLAUDE.md`

## Installation & Usage

Run directly with `uvx` (no installation needed):

```bash
uvx logfire-setup
```

Or install globally:

```bash
uv tool install logfire-setup
logfire-setup
```

## Features

### 1. Authentication & Project Setup

Validates authentication by checking `~/.logfire/default.toml` for non-expired tokens. If not found, falls back to checking for `LOGFIRE_TOKEN` in environment variables or `.env` file.

If authenticated and no existing project configuration is found, fetches your projects, lets you select one, and runs `logfire projects use` to create `.logfire/logfire_credentials.json` in your project. If valid credentials already exist, skips project selection.

### 2. Automatic Dependency Detection

The CLI scans your `pyproject.toml` or `requirements.txt` to detect existing packages and pre-selects relevant Logfire integrations.

### 3. Interactive Integration Selection

Choose from two organized sections using arrow keys and spacebar:

**Recommended Integrations:**
- HTTPX, FastAPI, Pydantic AI, SQLAlchemy

**Other Integrations** (alphabetically sorted):
- Web Frameworks: Django, Flask, Starlette, ASGI, WSGI
- HTTP Clients: Requests, aiohttp
- Databases: PostgreSQL (asyncpg/psycopg/psycopg2), MySQL, SQLite3, Redis, MongoDB
- Task Queues: Celery
- Cloud: AWS Lambda
- LLM & AI: Google GenAI, LiteLLM
- Monitoring: System Metrics

Detected integrations are pre-selected with checkmarks.

### 4. One-Command Installation

Automatically runs:

```bash
uv add logfire[fastapi,sqlalchemy,redis]
```

### 5. MCP Configuration Check

After installation, checks for MCP (Model Context Protocol) configuration in common IDE locations (Cursor, Claude Desktop, Cline, VS Code, Zed, etc.).

Provides example configurations and links to create read tokens if MCP is not configured or missing `LOGFIRE_READ_TOKEN`.

### 6. AI Assistant Instructions

Generates custom Logfire best practices for `AGENTS.md` or `CLAUDE.md`:

- Core patterns (spans, structured logging, exception handling)
- Integration-specific setup based on your selections
- MCP usage instructions (if configured)
- Security and performance tips
- Direct links to documentation

The instructions are tailored to your selected integrations and displayed inline for review before adding.

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager

## Development

Clone the repository:

```bash
git clone https://github.com/pydantic/logfire-setup.git
cd logfire-setup
```

Install dependencies:

```bash
uv sync
```

Run locally:

```bash
uv run logfire-setup
```

Test with uvx:

```bash
uvx --from . logfire-setup
```

## License

MIT - see [LICENSE](LICENSE) for details.

## Links

- [Pydantic Logfire Documentation](https://logfire.pydantic.dev/)
- [Logfire GitHub Repository](https://github.com/pydantic/logfire)
- [uv Documentation](https://docs.astral.sh/uv/)
