"""Simple API client for fetching Logfire projects."""

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import httpx


def get_user_token() -> tuple[str | None, str | None]:
    """
    Get user token from ~/.logfire/default.toml.

    Returns:
        Tuple of (token, base_url) or (None, None) if not found
    """
    default_file = Path.home() / ".logfire" / "default.toml"

    if not default_file.exists():
        return None, None

    try:
        with open(default_file, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return None, None

    tokens = data.get("tokens", {})
    if not tokens:
        return None, None

    # Get first available token
    for base_url, token_data in tokens.items():
        token = token_data.get("token")
        if token:
            return token, base_url

    return None, None


def fetch_user_projects() -> list[dict[str, str]] | None:
    """
    Fetch user's Logfire projects from API.

    Returns:
        List of projects with {organization_name, project_name} or None on error
    """
    token, base_url = get_user_token()

    if not token or not base_url:
        return None

    try:
        response = httpx.get(
            f"{base_url}/v1/writable-projects/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

        if response.status_code == 200:
            projects = response.json()
            return projects
        else:
            return None

    except Exception:
        return None
