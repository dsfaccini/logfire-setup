# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`logfire-setup` is an interactive CLI tool that helps users set up Pydantic Logfire in their Python projects. Similar to `create-next-app`, it guides users through selecting optional dependencies (web frameworks, databases, HTTP clients, etc.) and configures everything automatically.

The tool is designed to be run via `uvx logfire-setup` without installation.

## Development Commands

```bash
# Install dependencies
uv sync

# Run CLI locally
uv run logfire-setup

# Test with uvx (simulates production usage)
uvx --from . logfire-setup

# Run tests
uv run python tests/test_detector.py
```

## Architecture

### Core Flow (main.py)

The CLI follows this execution flow:

1. **Authentication Check** (`auth_checker.py`) - Validates `~/.logfire/default.toml` for valid tokens
2. **Project Selection** (`api_client.py`) - Fetches user's Logfire projects via API, prompts selection with arrow keys, runs `logfire projects use`, and reads `project_url` from `.logfire/logfire_credentials.json`
3. **Dependency Detection** (`detector.py`) - Scans `pyproject.toml`/`requirements.txt` to auto-detect frameworks
4. **Integration Selection** (`categories.py`) - Two interactive checkbox prompts: "Recommended" (HTTPX, FastAPI, Pydantic AI, SQLAlchemy), then "Other Integrations" (alphabetically sorted flat list)
5. **Installation** (`installer.py`) - Runs `uv add logfire[extras,...]`
6. **Environment Checks** (`mcp_checker.py`) - Validates MCP configuration and displays status with pause for user review
7. **Documentation Generation** (`instructions.py`, `agents_md.py`) - Creates tailored best practices for AGENTS.md/CLAUDE.md, including MCP usage if configured

### Key Modules

**categories.py**: Central registry of 23+ Logfire integrations. First category is "Recommended" (HTTPX, FastAPI, Pydantic AI, SQLAlchemy), followed by categorized integrations (Web Frameworks, Databases, etc.). Each `Integration` maps:
- `extra`: The pip extra name (e.g., "fastapi")
- `package_patterns`: Package names to detect in user's dependencies (e.g., ["fastapi"])
- `display_name` and `description`: For UI display

Note: UI shows 2 prompts total - "Recommended" first, then all others in one alphabetically sorted list.

**detector.py**: Dependency detection logic. Parses TOML (using `tomllib`/`tomli`) and plaintext requirements files. Matches detected packages against `Integration.package_patterns` to pre-select relevant integrations.

**instructions.py**: Generates markdown documentation. Core instructions are always included (spans, f-strings, structured logging). If MCP is configured, adds MCP usage section. Integration-specific sections are dynamically added based on user selections (e.g., HTTPX examples show global, per-client, and extended capture modes).

**auth_checker.py**: Authentication validation matching logfire's own logic:
- Reads `~/.logfire/default.toml`
- Checks token expiration: `datetime.now(tz=timezone.utc) < expiration_dt`
- Non-invasive (same as running `logfire auth`)

**api_client.py**: Minimal Logfire API client. Extracts token from `default.toml` and calls `/v1/writable-projects/` to fetch user's projects for selection.

**mcp_checker.py**: Detects MCP (Model Context Protocol) configuration in common IDE locations (`.cursor/mcp.json`, `~/claude_desktop_config.json`, etc.). Verifies if Logfire MCP server is configured with read token. Returns configuration status and generates read token URLs using `project_url` from logfire credentials.

## Integration Categories

When adding new integrations, update `CATEGORIES` in `categories.py` with:
- Correct `extra` name from your (forked) [logfire pyproject.toml](../logfire/pyproject.toml)
- Accurate `package_patterns` for detection (package names users actually install)
- Clear category placement

## Python Version Support

Supports Python 3.9+ with conditional imports:
```python
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
```

## Dependencies

- `rich`: CLI UI (panels, console output)
- `questionary`: Interactive prompts (arrow key navigation, checkboxes)
- `httpx`: Logfire API calls
- `tomli`: TOML parsing for Python <3.11

## Key Design Principles

1. **Graceful degradation**: All checks are optional, failures don't block the flow
2. **Minimal API calls**: Prefer local file checks over network requests
3. **Non-invasive**: Authentication check mirrors `logfire auth` behavior
4. **User control**: Always prompt before installing or modifying files
