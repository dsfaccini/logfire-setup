"""Main CLI entry point for logfire-setup."""

import json
import subprocess
import sys
from pathlib import Path

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from logfire_setup.agents_md import add_instructions_to_project, find_agent_config_file
from logfire_setup.api_client import fetch_user_projects
from logfire_setup.auth_checker import check_authentication, check_env_token
from logfire_setup.categories import CATEGORIES, Integration
from logfire_setup.detector import detect_integrations
from logfire_setup.installer import (
    InstallationError,
    check_uv_available,
    install_logfire,
)
from logfire_setup.instructions import generate_instructions
from logfire_setup.mcp_checker import (
    find_mcp_config,
    get_mcp_config_example,
    get_read_token_url,
)

console = Console()

LOGFIRE_CHECKBOX_STYLE = Style([
    ('pointer', 'fg:#E620E9 bold'), # the pointer used to select
    ('selected', 'fg:#f9a4f7 bold'), # style for a selected item of a checkbox
    ('highlighted', 'fg:#E620E9 bold'), # the currently highlighted option
    ('separator', 'fg:#E620E9'),  # the highlight on selected options
    ('disabled', 'fg:#858585 italic'),
])

project_url: str | None = (
    None  # Global variable to hold project_url from logfire_credentials.json
)


def print_welcome():
    """Print welcome message."""
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]Logfire Setup[/bold cyan]\n\n"
            "Interactive CLI to set up Pydantic Logfire with optional dependencies",
            border_style="cyan",
        )
    )
    console.print()


def detect_and_display_dependencies(project_dir: Path) -> list[Integration]:
    """Detect existing dependencies and display them."""
    console.print("[bold]Detecting existing dependencies...[/bold]")

    detected_integrations = detect_integrations(project_dir)

    if detected_integrations:
        console.print(
            f"\n[green]✓[/green] Detected {len(detected_integrations)} matching integration(s):"
        )
        for integration in detected_integrations:
            console.print(f"  • {integration.display_name}")
        console.print()
    else:
        console.print("\n[dim]No matching integrations detected.[/dim]\n")

    return detected_integrations


def prompt_integration_selection(
    detected_integrations: list[Integration],
) -> list[Integration]:
    """Prompt user to select integrations from categories."""
    selected_integrations: list[Integration] = []
    detected_extras = {integration.extra for integration in detected_integrations}

    console.print("[bold]Select Logfire integrations to install:[/bold]\n")
    console.print(
        "[dim]Use arrow keys to navigate, space to select, enter to confirm[/dim]\n"
    )

    # First, show Recommended category
    recommended_category = CATEGORIES[0]  # Recommended is first
    console.print(
        f"[bold cyan]{recommended_category.name}[/bold cyan] - {recommended_category.description}\n"
    )

    choices: list[questionary.Choice] = []
    for integration in recommended_category.integrations:
        label = f"{integration.display_name} - {integration.description}"
        if integration.extra in detected_extras:
            label += " [DETECTED ✓]"
        choices.append(
            questionary.Choice(
                title=label,
                value=integration,
                checked=integration.extra in detected_extras,
            )
        )

    selected = questionary.checkbox(
        "Select integrations:",
        choices=choices,
        style=LOGFIRE_CHECKBOX_STYLE,
    ).ask()

    # Handle Ctrl+C
    if selected is None:
        raise KeyboardInterrupt()

    if selected:
        selected_integrations.extend(selected)
        console.print(
            f"\n[green]✓[/green] Selected {len(selected)} from {recommended_category.name}\n"
        )
    else:
        console.print(f"\n[dim]Skipped {recommended_category.name}[/dim]\n")

    # Second, show all other integrations in one flat alphabetically sorted list
    console.print(
        "[bold cyan]Other Integrations[/bold cyan] - Additional framework and library instrumentation\n"
    )

    other_integrations: list[Integration] = []
    for category in CATEGORIES[1:]:  # Skip Recommended
        other_integrations.extend(category.integrations)

    # Sort alphabetically by display_name
    other_integrations.sort(key=lambda i: i.display_name.lower())

    choices = []
    for integration in other_integrations:
        label = f"{integration.display_name} - {integration.description}"
        if integration.extra in detected_extras:
            label += " [DETECTED ✓]"
        choices.append(
            questionary.Choice(
                title=label,
                value=integration,
                checked=integration.extra in detected_extras,
            )
        )

    selected = questionary.checkbox(
        "Select integrations:",
        choices=choices,
        style=LOGFIRE_CHECKBOX_STYLE,
    ).ask()

    # Handle Ctrl+C
    if selected is None:
        raise KeyboardInterrupt()

    if selected:
        selected_integrations.extend(selected)
        console.print(
            f"\n[green]✓[/green] Selected {len(selected)} additional integration(s)\n"
        )
    else:
        console.print("\n[dim]Skipped other integrations[/dim]\n")

    return selected_integrations


def display_selected_integrations(selected_integrations: list[Integration]):
    """Display summary of selected integrations."""
    if not selected_integrations:
        console.print("[yellow]No integrations selected.[/yellow]")
        return

    console.print(
        f"\n[bold]Selected {len(selected_integrations)} integration(s):[/bold]"
    )
    for integration in selected_integrations:
        console.print(f"  • {integration.display_name} ({integration.extra})")
    console.print()


def prompt_agents_md_addition(
    selected_integrations: list[Integration],
    project_dir: Path,
    mcp_configured: bool = False,
) -> bool:
    """Prompt user to add instructions to AGENTS.md/CLAUDE.md."""
    console.print("\n[bold]Logfire Usage Instructions[/bold]")

    # Check for existing file
    existing_file = find_agent_config_file(project_dir)

    if existing_file:
        # Show absolute path if it's outside the project
        display_path = existing_file
        if not str(existing_file).startswith(str(project_dir)):
            console.print(f"\n[dim]Found: {display_path} (outside project)[/dim]")
        else:
            console.print(f"\n[dim]Found: {display_path.name}[/dim]")
    else:
        console.print(
            "\n[dim]No AGENTS.md or CLAUDE.md found. A new AGENTS.md will be created.[/dim]"
        )

    # Generate instructions to show preview
    instructions = generate_instructions(selected_integrations, mcp_configured)

    # Show preview
    console.print("\n[bold]Preview of instructions to be added:[/bold]\n")

    # Show first 30 lines
    lines = instructions.split("\n")
    preview_lines = lines[:30]
    preview_text = "\n".join(preview_lines)

    if len(lines) > 30:
        preview_text += f"\n\n... ({len(lines) - 30} more lines)"

    console.print(Panel(preview_text, border_style="dim", expand=False))

    # Prompt user
    console.print()
    if existing_file:
        question = f"Add these instructions to {existing_file}?"
    else:
        question = "Create AGENTS.md with these instructions?"

    return Confirm.ask(question, default=False)


def check_and_display_auth() -> bool:
    """Check authentication status and display result."""
    console.print("[bold]Checking authentication...[/bold]")
    auth_status = check_authentication()

    if auth_status.is_authenticated:
        console.print(f"[green]✓[/green] {auth_status.message}\n")
        return True
    else:
        console.print(
            f"[yellow]⚠[/yellow] {auth_status.message}. Checking for token...\n"
        )
        token_status = check_env_token()
        if token_status.is_authenticated:
            console.print(f"[green]✓[/green] {token_status.message}\n")
            return True
        else:
            console.print(f"[yellow]⚠[/yellow] {token_status.message}\n")
        return False


def check_existing_credentials() -> str | None:
    """
    Check for existing logfire credentials and return project_url if valid.

    Returns:
        project_url if valid credentials exist, None otherwise.
    """
    credentials_file = Path.cwd() / ".logfire" / "logfire_credentials.json"

    if not credentials_file.exists():
        return None

    try:
        with open(credentials_file) as f:
            data = json.load(f)
            project_url = data.get("project_url")
            if project_url:
                return project_url
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        pass

    return None


def prompt_project_selection() -> str | None:
    """Fetch and prompt user to select a Logfire project."""
    console.print("[bold]Fetching your Logfire projects...[/bold]")

    projects = fetch_user_projects()

    if projects is None:
        console.print(
            "[yellow]⚠[/yellow] Could not fetch projects. Skipping project selection.\n"
        )
        return None

    if not projects:
        default_us_projects_url = (
            "https://logfire-us.pydantic.dev/?to=:account/-/projects"
        )
        default_eu_projects_url = (
            "https://logfire-eu.pydantic.dev/?to=:account/-/projects"
        )
        console.print("[dim]No projects found.[/dim]\nYou can create a new project at:")
        console.print(f"[dim]  • US: {default_us_projects_url}[/dim]")
        console.print(f"[dim]  • EU: {default_eu_projects_url}[/dim]\n")
        return None

    console.print(f"\n[green]✓[/green] Found {len(projects)} project(s)\n")

    # Build project choices for questionary
    choices: list[questionary.Choice] = []
    for project in projects:
        org_name = project.get("organization_name", "")
        project_name = project.get("project_name", "")
        choices.append(
            questionary.Choice(title=f"{org_name}/{project_name}", value=project)
        )

    # Add skip option
    choices.append(questionary.Choice(title="Skip project selection", value=None))

    selected_project = questionary.select(
        "Select a project:",
        choices=choices,
        style=LOGFIRE_CHECKBOX_STYLE,
    ).ask()

    # Handle Ctrl+C
    if selected_project is None and len([c for c in choices if c.value is None]) == 0:
        raise KeyboardInterrupt()

    if selected_project is None:
        console.print("\n[dim]Skipped project selection[/dim]\n")
        return None

    org_name = selected_project.get("organization_name", "")
    project_name = selected_project.get("project_name", "")
    project_path = f"{org_name}/{project_name}"
    console.print(f"\n[green]✓[/green] Selected: {project_path}\n")

    # Run logfire projects use to create .logfire directory
    console.print(f"[dim]Setting project to {project_name}...[/dim]")
    try:
        subprocess.run(
            ["logfire", "projects", "use", project_name],
            check=True,
            capture_output=True,
            text=True,
        )

        # Read project_url from logfire_credentials.json
        global project_url
        project_url = check_existing_credentials()
        if project_url:
            console.print("[green]✓[/green] Project configured\n")
        else:
            console.print("[yellow]⚠[/yellow] Could not find credentials file\n")
    except subprocess.CalledProcessError as e:
        console.print(f"[yellow]⚠[/yellow] Failed to set project: {e.stderr}\n")
    except FileNotFoundError as e:
        console.print(f"[yellow]⚠[/yellow] Error reading credentials: {e}\n")
    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Unknown error happened: {type(e)}{e}\n")

    return project_path


def check_and_display_mcp() -> bool:
    """
    Check for MCP configuration and display status.

    Returns:
        True if MCP is configured with read token, False otherwise.
    """
    global project_url
    console.print("\n[bold]Checking MCP configuration...[/bold]")

    mcp_config_check = find_mcp_config()

    if mcp_config_check.is_configured and mcp_config_check.has_read_token:
        console.print(
            f"[green]✓[/green] MCP configured in {mcp_config_check.config_file_path}"
        )
        return True
    elif mcp_config_check.is_configured and not mcp_config_check.has_read_token:
        console.print(
            f"[yellow]⚠[/yellow] MCP configured in {mcp_config_check.config_file_path} but missing LOGFIRE_READ_TOKEN"
        )
        if project_url:
            read_url = get_read_token_url(project_url)
            if read_url:
                console.print(f"[dim]Create a read token at: {read_url}[/dim]")
        return False
    else:
        console.print("[yellow]⚠[/yellow] MCP not configured")
        console.print(
            "[dim]To set up Logfire MCP server, add this to your .mcp.json (or wherever you keep your MCPs):[/dim]\n"
        )

        # Try to detect IDE from config file locations
        cursor_config = Path.cwd() / ".cursor" / "mcp.json"
        if cursor_config.exists() or cursor_config.parent.exists():
            example = get_mcp_config_example("cursor")
            console.print(Panel(example, title=".cursor/mcp.json", border_style="dim"))
        else:
            example = get_mcp_config_example("cursor")
            console.print(Panel(example, title="Example config", border_style="dim"))

        if project_url:
            read_token_url = get_read_token_url(project_url)
            if read_token_url:
                console.print(f"\n[dim]Create a read token at: {read_token_url}[/dim]")

        return False


def main():
    """Main CLI entry point."""
    try:
        # Welcome
        print_welcome()

        # Check for uv
        if not check_uv_available():
            console.print(
                "[bold red]Error:[/bold red] uv is not installed or not available in PATH"
            )
            console.print("\nPlease install uv from: https://docs.astral.sh/uv/")
            sys.exit(1)

        # Get project directory
        project_dir = Path.cwd()
        console.print(f"[dim]Project directory: {project_dir}[/dim]\n")

        # Check authentication
        is_authenticated = check_and_display_auth()
        if not is_authenticated:
            console.print(
                "[bold]To authenticate, run:[/bold]uv add logfire && logfire auth\n"
            )
            if not Confirm.ask("Continue without authentication?", default=True):
                sys.exit(0)

        # Project selection (if authenticated)
        if is_authenticated:
            # Check for existing credentials first
            existing_project_url = check_existing_credentials()
            if existing_project_url:
                global project_url
                project_url = existing_project_url
                console.print(
                    "[green]✓[/green] Found existing project configuration\n"
                )
                console.print(f"[dim]Project URL: {project_url}[/dim]\n")
                project_path = project_url  # Use URL as path identifier
            else:
                project_path = prompt_project_selection()
        else:
            project_path = None

        # Detect existing dependencies
        detected_integrations = detect_and_display_dependencies(project_dir)

        # Prompt for integration selection
        selected_integrations = prompt_integration_selection(detected_integrations)

        # Display summary
        display_selected_integrations(selected_integrations)

        # If nothing selected, ask if user wants to install base logfire anyway
        if not selected_integrations:
            install_base = Confirm.ask(
                "\nNo integrations selected. Install base logfire package anyway?",
                default=True,
            )
            if not install_base:
                console.print("\n[yellow]Setup cancelled.[/yellow]")
                sys.exit(0)

        # Confirm installation
        if selected_integrations:
            extras_list = ", ".join(
                integration.extra for integration in selected_integrations
            )
            console.print(f"\n[bold]Ready to install:[/bold] logfire[{extras_list}]")
        else:
            console.print("\n[bold]Ready to install:[/bold] logfire")

        proceed = Confirm.ask("\nProceed with installation?", default=True)
        if not proceed:
            console.print("\n[yellow]Installation cancelled.[/yellow]")
            sys.exit(0)

        # Install logfire
        extras = [integration.extra for integration in selected_integrations]
        success = install_logfire(extras, project_dir)

        if not success:
            console.print("\n[bold red]Installation failed.[/bold red]")
            sys.exit(1)

        # Check MCP configuration
        mcp_configured = check_and_display_mcp()

        questionary.press_any_key_to_continue().ask()

        # Prompt for AGENTS.md/CLAUDE.md
        if selected_integrations or Confirm.ask(
            "\nWould you like to add Logfire usage instructions for AI assistants?",
            default=True,
        ):
            add_instructions = prompt_agents_md_addition(
                selected_integrations, project_dir, mcp_configured
            )

            if add_instructions:
                instructions = generate_instructions(
                    selected_integrations, mcp_configured
                )
                success, file_path = add_instructions_to_project(
                    instructions, project_dir
                )

                if not success:
                    console.print(
                        "\n[yellow]Warning:[/yellow] Failed to add instructions to file",
                        file_path,
                    )

        console.print("\n")  # Add visual separation

        # Success message
        console.print("\n[bold green]✓ Setup complete![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")

        step_num = 1
        if not is_authenticated:
            console.print(f"{step_num}. Run [cyan]logfire auth[/cyan] to authenticate")
            step_num += 1

        if is_authenticated and not project_path:
            console.print(
                f"{step_num}. Run [cyan]logfire projects use <org>/<project>[/cyan] to select a project"
            )
            step_num += 1

        console.print(
            f"{step_num}. Add [cyan]logfire.configure()[/cyan] to your application startup"
        )
        console.print(
            f"{step_num + 1}. Visit https://logfire.pydantic.dev/docs/ for detailed documentation"
        )
        console.print()

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup cancelled by user.[/yellow]")
        sys.exit(130)
    except InstallationError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
