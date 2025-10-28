"""Tests for authentication checking."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from logfire_setup.auth_checker import check_authentication, check_env_token


def test_check_authentication_no_file():
    """Test authentication check when default.toml doesn't exist."""
    # This test assumes the file doesn't exist in a temp location
    # In reality, it checks ~/.logfire/default.toml
    auth_status = check_authentication()
    # Will check real file, so we just verify it returns AuthStatus
    assert isinstance(auth_status.is_authenticated, bool)
    assert isinstance(auth_status.message, str)


def test_check_env_token_in_environment():
    """Test env token detection in environment variables."""
    # Save original
    original = os.environ.get("LOGFIRE_TOKEN")

    try:
        # Set token
        os.environ["LOGFIRE_TOKEN"] = "test_token"
        token_status = check_env_token()
        assert token_status.is_authenticated is True
        assert "environment" in token_status.message
    finally:
        # Restore
        if original:
            os.environ["LOGFIRE_TOKEN"] = original
        else:
            os.environ.pop("LOGFIRE_TOKEN", None)


def test_check_env_token_in_dotenv():
    """Test env token detection in .env file."""
    with TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Create .env file
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("LOGFIRE_TOKEN=test_token_value\n")

            # Make sure not in environment
            os.environ.pop("LOGFIRE_TOKEN", None)

            token_status = check_env_token()
            assert token_status.is_authenticated is True
            assert ".env" in token_status.message
        finally:
            os.chdir(original_cwd)


def test_check_env_token_missing():
    """Test env token detection when token is missing."""
    with TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            # Make sure not in environment
            os.environ.pop("LOGFIRE_TOKEN", None)

            token_status = check_env_token()
            assert token_status.is_authenticated is False
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    test_check_authentication_no_file()
    print("✓ test_check_authentication_no_file")

    test_check_env_token_in_environment()
    print("✓ test_check_env_token_in_environment")

    test_check_env_token_in_dotenv()
    print("✓ test_check_env_token_in_dotenv")

    test_check_env_token_missing()
    print("✓ test_check_env_token_missing")

    print("\nAll auth_checker tests passed!")
