"""Detect existing dependencies in a project to pre-select relevant Logfire integrations."""

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from logfire_setup.categories import Integration, get_all_integrations


def parse_pyproject_toml(path: Path) -> set[str]:
    """Parse pyproject.toml and extract all dependency package names."""
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return set()

    packages = set()

    # Check [project.dependencies]
    if "project" in data and "dependencies" in data["project"]:
        for dep in data["project"]["dependencies"]:
            # Extract package name (before any version specifier)
            pkg_name = (
                dep.split("[")[0]
                .split(">=")[0]
                .split("==")[0]
                .split("<")[0]
                .split(">")[0]
                .strip()
            )
            packages.add(pkg_name.lower())

    # Check [project.optional-dependencies]
    if "project" in data and "optional-dependencies" in data["project"]:
        for group_deps in data["project"]["optional-dependencies"].values():
            for dep in group_deps:
                pkg_name = (
                    dep.split("[")[0]
                    .split(">=")[0]
                    .split("==")[0]
                    .split("<")[0]
                    .split(">")[0]
                    .strip()
                )
                packages.add(pkg_name.lower())

    # Check [dependency-groups] (PEP 735)
    if "dependency-groups" in data:
        for group_deps in data["dependency-groups"].values():
            for dep in group_deps:
                pkg_name = (
                    dep.split("[")[0]
                    .split(">=")[0]
                    .split("==")[0]
                    .split("<")[0]
                    .split(">")[0]
                    .strip()
                )
                packages.add(pkg_name.lower())

    # Check [tool.poetry.dependencies] for Poetry projects
    if (
        "tool" in data
        and "poetry" in data["tool"]
        and "dependencies" in data["tool"]["poetry"]
    ):
        for pkg_name in data["tool"]["poetry"]["dependencies"].keys():
            if pkg_name != "python":
                packages.add(pkg_name.lower())

    return packages


def parse_requirements_txt(path: Path) -> set[str]:
    """Parse requirements.txt and extract package names."""
    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return set()

    packages = set()
    for line in lines:
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue
        # Skip flags like -e or -r
        if line.startswith("-"):
            continue
        # Extract package name
        pkg_name = (
            line.split("[")[0]
            .split(">=")[0]
            .split("==")[0]
            .split("<")[0]
            .split(">")[0]
            .strip()
        )
        packages.add(pkg_name.lower())

    return packages


def detect_project_dependencies(project_dir: Path | None = None) -> set[str]:
    """Detect all dependencies in a project directory."""
    if project_dir is None:
        project_dir = Path.cwd()

    packages = set()

    # Try pyproject.toml first
    pyproject_path = project_dir / "pyproject.toml"
    if pyproject_path.exists():
        packages.update(parse_pyproject_toml(pyproject_path))

    # Fall back to requirements.txt
    requirements_path = project_dir / "requirements.txt"
    if requirements_path.exists():
        packages.update(parse_requirements_txt(requirements_path))

    return packages


def match_integrations_to_dependencies(dependencies: set[str]) -> list[Integration]:
    """Match detected dependencies to Logfire integrations."""
    matched_integrations = []

    for integration in get_all_integrations():
        # Check if any of the package patterns match the detected dependencies
        for pattern in integration.package_patterns:
            if pattern.lower() in dependencies:
                matched_integrations.append(integration)
                break

    return matched_integrations


def detect_integrations(project_dir: Path | None = None) -> list[Integration]:
    """
    Detect which Logfire integrations are relevant for a project.

    Args:
        project_dir: Project directory to scan. Defaults to current working directory.

    Returns:
        List of Integration objects that match detected dependencies.
    """
    dependencies = detect_project_dependencies(project_dir)
    return match_integrations_to_dependencies(dependencies)
