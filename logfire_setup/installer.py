"""Handle installation of Logfire with selected extras using uv."""

import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


class InstallationError(Exception):
    """Raised when installation fails."""

    pass


def install_logfire(extras: list[str], project_dir: Path | None = None) -> bool:
    """
    Install logfire with the specified extras using uv.

    Args:
        extras: List of extra names to install (e.g., ['fastapi', 'sqlalchemy'])
        project_dir: Project directory to install in. Defaults to current directory.

    Returns:
        True if installation succeeded, False otherwise.

    Raises:
        InstallationError: If uv is not available or installation fails.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Check if uv is available
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise InstallationError("uv is not installed or not available in PATH")
    except FileNotFoundError:
        raise InstallationError(
            "uv is not installed. Please install it from https://docs.astral.sh/uv/"
        )

    # Build the package spec
    if extras:
        extras_str = ",".join(extras)
        package_spec = f"logfire[{extras_str}]"
    else:
        package_spec = "logfire"

    console.print(f"\n[bold cyan]Installing {package_spec}...[/bold cyan]\n")

    # Run uv add
    try:
        result = subprocess.run(
            ["uv", "add", package_spec],
            cwd=project_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            console.print(
                f"[bold green]✓[/bold green] Successfully installed {package_spec}"
            )
            if result.stdout:
                console.print(result.stdout)
            return True
        else:
            console.print(f"[bold red]✗[/bold red] Failed to install {package_spec}")
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]")
            if result.stdout:
                console.print(result.stdout)
            return False

    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Installation error: {e}")
        return False


def check_uv_available() -> bool:
    """Check if uv is available in the system."""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
