"""Tests for AGENTS.md/CLAUDE.md handling."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from logfire_setup.agents_md import (
    add_instructions_to_project,
    check_if_logfire_instructions_exist,
    find_agent_config_file,
    resolve_real_file,
)


def test_find_agent_config_file_agents_md():
    """Test finding AGENTS.md file."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        agents_md = tmpdir / "AGENTS.md"
        agents_md.write_text("# Agents")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            found = find_agent_config_file()
            assert found is not None
            assert found.resolve() == agents_md.resolve()
        finally:
            os.chdir(original_cwd)


def test_find_agent_config_file_claude_md():
    """Test finding CLAUDE.md file."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        claude_md = tmpdir / "CLAUDE.md"
        claude_md.write_text("# Claude")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            found = find_agent_config_file()
            assert found is not None
            assert found.resolve() == claude_md.resolve()
        finally:
            os.chdir(original_cwd)


def test_find_agent_config_file_not_found():
    """Test when no config file exists."""
    with TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            found = find_agent_config_file()
            assert found is None
        finally:
            os.chdir(original_cwd)


def test_check_if_logfire_instructions_exist_true():
    """Test detecting existing Logfire instructions."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        agents_md = tmpdir / "AGENTS.md"
        agents_md.write_text("# Logfire Best Practices\n\nSome content...")

        exists = check_if_logfire_instructions_exist(agents_md)
        assert exists is True


def test_check_if_logfire_instructions_exist_false():
    """Test when Logfire instructions don't exist."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        agents_md = tmpdir / "AGENTS.md"
        agents_md.write_text("# Other content")

        exists = check_if_logfire_instructions_exist(agents_md)
        assert exists is False


def test_add_instructions_create_new():
    """Test creating new AGENTS.md file."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            instructions = "# Test Instructions\n\nTest content"
            success, file_path = add_instructions_to_project(instructions)

            assert success is True
            assert file_path is not None
            assert file_path.resolve() == (tmpdir / "AGENTS.md").resolve()
            assert file_path.exists()
            assert "Test Instructions" in file_path.read_text()
        finally:
            os.chdir(original_cwd)


def test_add_instructions_append_existing():
    """Test appending to existing file."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        agents_md = tmpdir / "AGENTS.md"
        agents_md.write_text("# Existing content")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            instructions = "# New Instructions"
            success, file_path = add_instructions_to_project(instructions)

            assert success is True
            assert file_path is not None
            assert file_path.resolve() == agents_md.resolve()
            content = file_path.read_text()
            assert "Existing content" in content
            assert "New Instructions" in content
            assert "---" in content  # Separator
        finally:
            os.chdir(original_cwd)


def test_add_instructions_skip_if_exists():
    """Test skipping when instructions already exist."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        agents_md = tmpdir / "AGENTS.md"
        agents_md.write_text("# Logfire Best Practices\n\nExisting logfire content")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            instructions = "# Logfire Best Practices\n\nNew content"
            success, file_path = add_instructions_to_project(instructions)

            # Should succeed but not modify
            assert success is True
            assert file_path is not None
            assert file_path.resolve() == agents_md.resolve()
            # Content should be unchanged
            assert (
                file_path.read_text()
                == "# Logfire Best Practices\n\nExisting logfire content"
            )
        finally:
            os.chdir(original_cwd)


def test_resolve_real_file():
    """Test symlink resolution."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create a real file
        real_file = tmpdir / "real.md"
        real_file.write_text("Real content")

        # Create a symlink
        symlink = tmpdir / "symlink.md"
        symlink.symlink_to(real_file)

        resolved = resolve_real_file(symlink)
        assert resolved == real_file.resolve()


if __name__ == "__main__":
    test_find_agent_config_file_agents_md()
    print("✓ test_find_agent_config_file_agents_md")

    test_find_agent_config_file_claude_md()
    print("✓ test_find_agent_config_file_claude_md")

    test_find_agent_config_file_not_found()
    print("✓ test_find_agent_config_file_not_found")

    test_check_if_logfire_instructions_exist_true()
    print("✓ test_check_if_logfire_instructions_exist_true")

    test_check_if_logfire_instructions_exist_false()
    print("✓ test_check_if_logfire_instructions_exist_false")

    test_add_instructions_create_new()
    print("✓ test_add_instructions_create_new")

    test_add_instructions_append_existing()
    print("✓ test_add_instructions_append_existing")

    test_add_instructions_skip_if_exists()
    print("✓ test_add_instructions_skip_if_exists")

    test_resolve_real_file()
    print("✓ test_resolve_real_file")

    print("\nAll agents_md tests passed!")
