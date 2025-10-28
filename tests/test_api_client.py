"""Tests for API client."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from logfire_setup.api_client import fetch_user_projects, get_user_token


def test_get_user_token_no_file():
    """Test token extraction when file doesn't exist."""
    with TemporaryDirectory() as tmpdir:
        fake_home = Path(tmpdir)
        with mock.patch("pathlib.Path.home", return_value=fake_home):
            token, base_url = get_user_token()
            assert token is None
            assert base_url is None


def test_get_user_token_with_file():
    """Test token extraction from default.toml."""
    with TemporaryDirectory() as tmpdir:
        fake_home = Path(tmpdir)
        logfire_dir = fake_home / ".logfire"
        logfire_dir.mkdir()

        default_file = logfire_dir / "default.toml"
        default_file.write_text("""
[tokens."https://logfire-us.pydantic.dev"]
token = "test_token_123"
expiration = "2099-12-31T23:59:59Z"
""")

        with mock.patch("pathlib.Path.home", return_value=fake_home):
            token, base_url = get_user_token()
            assert token == "test_token_123"
            assert base_url == "https://logfire-us.pydantic.dev"


def test_fetch_user_projects_success():
    """Test fetching projects with mock API response."""
    mock_projects = [
        {"organization_name": "test-org", "project_name": "test-project-1"},
        {"organization_name": "test-org", "project_name": "test-project-2"},
    ]

    with mock.patch(
        "logfire_setup.api_client.get_user_token",
        return_value=("token", "https://logfire-us.pydantic.dev"),
    ):
        with mock.patch("logfire_setup.api_client.httpx.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_projects

            projects = fetch_user_projects()
            assert projects is not None
            assert projects == mock_projects
            assert len(projects) == 2


def test_fetch_user_projects_no_token():
    """Test fetching projects when no token available."""
    with mock.patch(
        "logfire_setup.api_client.get_user_token", return_value=(None, None)
    ):
        projects = fetch_user_projects()
        assert projects is None


def test_fetch_user_projects_api_error():
    """Test fetching projects when API returns error."""
    with mock.patch(
        "logfire_setup.api_client.get_user_token",
        return_value=("token", "https://logfire-us.pydantic.dev"),
    ):
        with mock.patch("logfire_setup.api_client.httpx.get") as mock_get:
            mock_get.return_value.status_code = 401

            projects = fetch_user_projects()
            assert projects is None


if __name__ == "__main__":
    test_get_user_token_no_file()
    print("✓ test_get_user_token_no_file")

    test_get_user_token_with_file()
    print("✓ test_get_user_token_with_file")

    test_fetch_user_projects_success()
    print("✓ test_fetch_user_projects_success")

    test_fetch_user_projects_no_token()
    print("✓ test_fetch_user_projects_no_token")

    test_fetch_user_projects_api_error()
    print("✓ test_fetch_user_projects_api_error")

    print("\nAll api_client tests passed!")
