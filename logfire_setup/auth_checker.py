"""Check Logfire authentication status and environment variables."""

from dataclasses import dataclass
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class AuthStatus:
    is_authenticated: bool
    message: str
    base_url: str | None = None


def check_authentication() -> AuthStatus:
    """
    Check if user is authenticated with Logfire.

    Returns:
        Tuple of (is_authenticated, message)
    """
    default_file = Path.home() / ".logfire" / "default.toml"

    if not default_file.exists():
        return AuthStatus(
            False, "Not authenticated. Run `logfire auth` to authenticate."
        )

    try:
        with open(default_file, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        return AuthStatus(False, f"Error reading authentication file: {e}")

    # Check if we have any valid (non-expired) tokens
    tokens = data.get("tokens", {})
    if not tokens:
        return AuthStatus(
            False, "No authentication tokens found. Run `logfire auth` to authenticate."
        )

    # Check for at least one non-expired token
    for base_url, token_data in tokens.items():
        expiration = token_data.get("expiration", "")
        try:
            expiration_dt = datetime.fromisoformat(expiration.rstrip("Z")).replace(
                tzinfo=timezone.utc
            )
            if datetime.now(tz=timezone.utc) < expiration_dt:
                return AuthStatus(
                    True, f"Authenticated (credentials in {default_file})", base_url
                )
        except (ValueError, AttributeError):
            continue

    return AuthStatus(
        False,
        "All authentication tokens have expired. Run `logfire auth` to re-authenticate.",
    )


def check_env_token() -> AuthStatus:
    """
    Check if LOGFIRE_TOKEN environment variable is set.

    Returns:
        Tuple of (has_token, location) where location is "environment", ".env", or None
    """
    import os

    # Check environment variables
    if "LOGFIRE_TOKEN" in os.environ:
        return AuthStatus(True, "Token found in environment")

    # Check .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        try:
            content = env_file.read_text()
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("LOGFIRE_TOKEN="):
                    return AuthStatus(True, "Token found in .env file")
        except Exception:
            pass

    return AuthStatus(
        False,
        "No LOGFIRE_TOKEN found in the environment. Run `logfire auth` to authenticate.",
    )
