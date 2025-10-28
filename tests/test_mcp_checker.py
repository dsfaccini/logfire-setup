"""Tests for MCP configuration checker."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from logfire_setup.mcp_checker import find_mcp_config, get_mcp_config_example


def test_find_mcp_config_cursor():
    """Test finding MCP config in .cursor/mcp.json."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        cursor_dir = tmpdir / ".cursor"
        cursor_dir.mkdir()

        mcp_config = cursor_dir / "mcp.json"
        config_data: dict[str, Any] = {
            "mcpServers": {
                "logfire": {
                    "command": "uvx",
                    "args": ["logfire-mcp"],
                    "env": {"LOGFIRE_READ_TOKEN": "test_token"},
                }
            }
        }
        mcp_config.write_text(json.dumps(config_data))

        # Mock cwd to temp directory
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            mcp_config_check = find_mcp_config()
            assert mcp_config_check.is_configured is True
            assert mcp_config_check.config_file_path is not None
            assert mcp_config_check.config_file_path.resolve() == mcp_config.resolve()
            assert mcp_config_check.has_read_token is True
        finally:
            os.chdir(original_cwd)


def test_find_mcp_config_no_token():
    """Test finding MCP config without read token."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        cursor_dir = tmpdir / ".cursor"
        cursor_dir.mkdir()

        mcp_config = cursor_dir / "mcp.json"
        config_data: dict[str, Any] = {
            "mcpServers": {
                "logfire": {
                    "command": "uvx",
                    "args": ["logfire-mcp"],
                }
            }
        }
        mcp_config.write_text(json.dumps(config_data))

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            mcp_config_check = find_mcp_config()
            assert mcp_config_check.is_configured is True
            assert mcp_config_check.config_file_path is not None
            assert mcp_config_check.config_file_path.resolve() == mcp_config.resolve()
            assert mcp_config_check.has_read_token is False
        finally:
            os.chdir(original_cwd)


def test_find_mcp_config_not_found():
    """Test when no MCP config exists."""
    with TemporaryDirectory() as tmpdir:
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            mcp_config_check = find_mcp_config()
            assert mcp_config_check.is_configured is False
            assert mcp_config_check.config_file_path is None
            assert mcp_config_check.has_read_token is False
        finally:
            os.chdir(original_cwd)


def test_get_mcp_config_example():
    """Test getting MCP config examples."""
    cursor_example = get_mcp_config_example("cursor")
    assert "mcpServers" in cursor_example
    assert "logfire" in cursor_example
    assert "LOGFIRE_READ_TOKEN" in cursor_example

    claude_example = get_mcp_config_example("claude-code")
    assert "claude mcp add" in claude_example
    assert "logfire" in claude_example


if __name__ == "__main__":
    test_find_mcp_config_cursor()
    print("✓ test_find_mcp_config_cursor")

    test_find_mcp_config_no_token()
    print("✓ test_find_mcp_config_no_token")

    test_find_mcp_config_not_found()
    print("✓ test_find_mcp_config_not_found")

    test_get_mcp_config_example()
    print("✓ test_get_mcp_config_example")

    print("\nAll mcp_checker tests passed!")
