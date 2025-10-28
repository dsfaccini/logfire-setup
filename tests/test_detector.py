"""Tests for dependency detection."""

from pathlib import Path
from tempfile import TemporaryDirectory

from logfire_setup.detector import (
    detect_integrations,
    parse_pyproject_toml,
)


def test_parse_pyproject_toml():
    """Test parsing pyproject.toml."""
    with TemporaryDirectory() as tmpdir:
        pyproject = Path(tmpdir) / "pyproject.toml"
        pyproject.write_text(
            """
[project]
dependencies = [
    "fastapi>=0.100.0",
    "sqlalchemy>=2.0.0",
]
"""
        )

        packages = parse_pyproject_toml(pyproject)
        assert "fastapi" in packages
        assert "sqlalchemy" in packages


def test_detect_integrations():
    """Test detecting integrations from dependencies."""
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        pyproject = tmpdir / "pyproject.toml"
        pyproject.write_text(
            """
[project]
dependencies = [
    "fastapi>=0.100.0",
    "httpx>=0.27.0",
    "redis>=5.0.0",
]
"""
        )

        integrations = detect_integrations(tmpdir)
        extras = [i.extra for i in integrations]

        assert "fastapi" in extras
        assert "httpx" in extras
        assert "redis" in extras


if __name__ == "__main__":
    test_parse_pyproject_toml()
    test_detect_integrations()
    print("All tests passed!")
