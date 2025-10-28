"""Handle AGENTS.md/CLAUDE.md file detection and modification."""

from pathlib import Path

from rich.console import Console

console = Console()


def resolve_real_file(path: Path) -> Path:
    """
    Resolve a path to its real file, following symlinks.

    Args:
        path: Path to resolve

    Returns:
        Real path after following all symlinks
    """
    return path.resolve()


def find_agent_config_file(project_dir: Path | None = None) -> Path | None:
    """
    Find AGENTS.md or CLAUDE.md file in the project directory.

    Follows symlinks to find the real file location.

    Args:
        project_dir: Project directory to search. Defaults to current directory.

    Returns:
        Path to the real file (after resolving symlinks), or None if not found.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Check for AGENTS.md
    agents_md = project_dir / "AGENTS.md"
    if agents_md.exists():
        return resolve_real_file(agents_md)

    # Check for CLAUDE.md
    claude_md = project_dir / "CLAUDE.md"
    if claude_md.exists():
        return resolve_real_file(claude_md)

    # Check in .claude directory (common location)
    claude_dir_agents = project_dir / ".claude" / "AGENTS.md"
    if claude_dir_agents.exists():
        return resolve_real_file(claude_dir_agents)

    claude_dir_claude = project_dir / ".claude" / "CLAUDE.md"
    if claude_dir_claude.exists():
        return resolve_real_file(claude_dir_claude)

    return None


def check_if_logfire_instructions_exist(file_path: Path) -> bool:
    """
    Check if a file already contains Logfire instructions.

    Args:
        file_path: Path to the file to check

    Returns:
        True if Logfire instructions already exist
    """
    try:
        content = file_path.read_text()
        # Look for key phrases that indicate Logfire instructions
        return (
            "# Logfire Best Practices" in content
            or "logfire.configure()" in content
            or "https://logfire.pydantic.dev" in content
        )
    except Exception:
        return False


def append_instructions_to_file(file_path: Path, instructions: str) -> bool:
    """
    Append Logfire instructions to a file.

    Args:
        file_path: Path to the file to modify
        instructions: Instructions text to append

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read existing content
        if file_path.exists():
            existing_content = file_path.read_text()
            # Add separator if file is not empty
            if existing_content and not existing_content.endswith("\n\n"):
                separator = "\n\n---\n\n"
            else:
                separator = (
                    "\n---\n\n" if existing_content.endswith("\n") else "---\n\n"
                )
        else:
            existing_content = ""
            separator = ""

        # Append instructions
        new_content = existing_content + separator + instructions + "\n"

        # Write back
        file_path.write_text(new_content)
        return True

    except Exception as e:
        console.print(f"[red]Error writing to {file_path}: {e}[/red]")
        return False


def create_new_agents_md(project_dir: Path, instructions: str) -> Path | None:
    """
    Create a new AGENTS.md file in the project directory.

    Args:
        project_dir: Project directory
        instructions: Instructions text to write

    Returns:
        Path to the created file, or None if failed
    """
    try:
        agents_md = project_dir / "AGENTS.md"
        agents_md.write_text(instructions + "\n")
        return agents_md
    except Exception as e:
        console.print(f"[red]Error creating AGENTS.md: {e}[/red]")
        return None


def add_instructions_to_project(
    instructions: str,
    project_dir: Path | None = None,
) -> tuple[bool, Path | None]:
    """
    Add Logfire instructions to the project's AGENTS.md or CLAUDE.md file.

    Args:
        instructions: Instructions text to add
        project_dir: Project directory. Defaults to current directory.

    Returns:
        Tuple of (success, file_path). file_path is the path to the modified/created file.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Find existing file
    existing_file = find_agent_config_file(project_dir)

    if existing_file:
        # Check if instructions already exist
        if check_if_logfire_instructions_exist(existing_file):
            console.print(
                f"\n[yellow]Note:[/yellow] {existing_file} already contains Logfire instructions."
            )
            console.print("Skipping to avoid duplication.")
            return True, existing_file

        # Append to existing file
        if append_instructions_to_file(existing_file, instructions):
            console.print(
                f"\n[bold green]✓[/bold green] Added Logfire instructions to {existing_file}"
            )
            return True, existing_file
        else:
            return False, existing_file
    else:
        # Create new AGENTS.md
        new_file = create_new_agents_md(project_dir, instructions)
        if new_file:
            console.print(
                f"\n[bold green]✓[/bold green] Created {new_file} with Logfire instructions"
            )
            return True, new_file
        else:
            return False, None
