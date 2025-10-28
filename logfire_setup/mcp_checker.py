"""Check for MCP (Model Context Protocol) configuration."""

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class McpConfigCheckResult:
    is_configured: bool
    config_file_path: Path | None
    has_read_token: bool


def get_read_token_url(project_url: str | None) -> str | None:
    """
    Generate the read token creation URL based on the project URL.

    Args:
        project_url: The project URL from logfire_credentials.json.

    Returns:
        The URL to create a new read token, or None if project_url is None.
    """
    if not project_url:
        return 'https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens'
    return f"{project_url}/settings/read-tokens/new"


def find_mcp_config() -> McpConfigCheckResult:
    """
    Check for MCP configuration files and Logfire setup.

    Returns:
        Tuple of (is_configured, config_file_path, has_read_token)
    """
    # Check common MCP config file locations
    config_locations = [
        Path.cwd() / ".mcp.json",
        Path.cwd() / ".cursor" / "mcp.json",
        Path.cwd() / "cline_mcp_settings.json",
        Path.cwd() / ".claude" / "mcp.json",
        Path.cwd() / ".vscode" / "mcp.json",
        Path.cwd() / ".zed" / "settings.json",
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
    ]

    for config_path in config_locations:
        if not config_path.exists():
            continue

        try:
            with open(config_path) as f:
                config = json.load(f)

            # Check different JSON structures based on IDE
            # Standard: mcpServers (Cursor, Cline, Claude Desktop, Claude Code)
            # VS Code: servers
            # Zed: context_servers
            logfire_config = None
            for key in ["mcpServers", "servers", "context_servers"]:
                servers = config.get(key, {})
                if "logfire" in servers:
                    logfire_config = servers["logfire"]
                    break

            if logfire_config:
                # Check if read token is present (in args or env)
                has_token = False

                # Check in args
                args = logfire_config.get("args", [])
                if any(
                    "--read-token" in str(arg) or "LOGFIRE_READ_TOKEN" in str(arg)
                    for arg in args
                ):
                    has_token = True

                # Check in env
                env = logfire_config.get("env", {})
                if "LOGFIRE_READ_TOKEN" in env:
                    has_token = True

                return McpConfigCheckResult(True, config_path, has_token)

        except (json.JSONDecodeError, Exception):
            continue

    return McpConfigCheckResult(False, None, False)


def get_mcp_config_example(ide_name: str = "cursor") -> str:
    """
    Get MCP configuration example for a specific IDE.

    Args:
        ide_name: IDE name (cursor, claude-desktop, cline, claude-code)

    Returns:
        JSON configuration example as string
    """
    examples = {
        "cursor": """{
  "mcpServers": {
    "logfire": {
      "command": "uvx",
      "args": ["logfire-mcp@latest", "--read-token=YOUR_TOKEN"]
    }
  }
}""",
        "claude-desktop": """{
  "mcpServers": {
    "logfire": {
      "command": ["uvx"],
      "args": ["logfire-mcp@latest"],
      "type": "stdio",
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      }
    }
  }
}""",
        "cline": """{
  "mcpServers": {
    "logfire": {
      "command": "uvx",
      "args": ["logfire-mcp@latest"],
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}""",
        "claude-code": """Run: claude mcp add logfire -e LOGFIRE_READ_TOKEN=YOUR_TOKEN -- uvx logfire-mcp@latest""",
        "vs-code": """{
  "servers": {
    "logfire": {
      "type": "stdio",
      "command": "uvx",
      "args": ["logfire-mcp@latest"],
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      }
    }
  }
}""",
        "zed": """{
  "context_servers": {
    "logfire": {
      "source": "custom",
      "command": "uvx",
      "args": ["logfire-mcp@latest"],
      "env": {
        "LOGFIRE_READ_TOKEN": "YOUR_TOKEN"
      },
      "enabled": true
    }
  }
}""",
    }

    return examples.get(ide_name, examples["cursor"])
