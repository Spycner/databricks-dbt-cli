"""SQLFluff pre-commit hook that discovers and runs sqlfluff per-project.

This script solves the SQLFluff templater limitation where the `templater` setting
cannot be overridden in subdirectory `.sqlfluff` files. It discovers all directories
containing `.sqlfluff` files and runs sqlfluff from within each directory.

Usage:
    sqlfluff-project-lint [--require-dbt]
    sqlfluff-project-fix [--require-dbt]

Flags:
    --require-dbt    Only process directories with both .sqlfluff AND dbt_project.yml
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Directories to skip when discovering .sqlfluff files
SKIP_DIRS = frozenset(
    {
        ".venv",
        "venv",
        ".git",
        "node_modules",
        "__pycache__",
        ".tox",
        ".nox",
        ".eggs",
        "dist",
        "build",
    }
)


def discover_sqlfluff_projects(root: Path, require_dbt: bool) -> list[Path]:
    """Find all directories containing .sqlfluff files.

    Args:
        root: Root directory to search from.
        require_dbt: If True, also require dbt_project.yml to be present.

    Returns:
        List of project directories containing .sqlfluff (and optionally dbt_project.yml).
    """
    projects: list[Path] = []

    for sqlfluff_file in root.rglob(".sqlfluff"):
        project_dir = sqlfluff_file.parent

        # Skip if inside excluded directories
        if any(part in SKIP_DIRS for part in project_dir.parts):
            continue

        # Skip hidden directories (except for the .sqlfluff file itself)
        if any(part.startswith(".") and part != ".sqlfluff" for part in project_dir.parts):
            continue

        if require_dbt and not (project_dir / "dbt_project.yml").exists():
            continue

        projects.append(project_dir)

    return projects


def run_sqlfluff(mode: str, require_dbt: bool) -> int:
    """Discover and lint/fix all sqlfluff projects.

    Args:
        mode: Either "lint" or "fix".
        require_dbt: If True, only process directories with both .sqlfluff and dbt_project.yml.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    root = Path.cwd()
    projects = discover_sqlfluff_projects(root, require_dbt)

    if not projects:
        config_type = ".sqlfluff + dbt_project.yml" if require_dbt else ".sqlfluff"
        print(f"No {config_type} projects found", flush=True)
        return 0

    print(f"Found {len(projects)} project(s) with .sqlfluff config", flush=True)

    exit_code = 0

    for project_dir in sorted(projects):
        print(f"\n=== Running sqlfluff {mode} in {project_dir} ===", flush=True)

        # Build sqlfluff command - no file args, let sqlfluff use its config
        cmd = ["sqlfluff", mode, "--processes", "0", "--disable-progress-bar"]
        if mode == "fix":
            cmd.append("--show-lint-violations")

        result = subprocess.run(cmd, cwd=project_dir)
        exit_code = max(exit_code, result.returncode)

    return exit_code


def parse_args(args: list[str]) -> bool:
    """Parse command line arguments.

    Args:
        args: Command line arguments (excluding program name).

    Returns:
        require_dbt flag value.
    """
    require_dbt = False

    for arg in args:
        if arg == "--require-dbt":
            require_dbt = True
        elif arg.startswith("-"):
            print(f"Warning: Unknown flag '{arg}', ignoring", flush=True)
        # Ignore any file arguments - we use discovery instead

    return require_dbt


def lint() -> None:
    """Entry point for sqlfluff-project-lint command."""
    require_dbt = parse_args(sys.argv[1:])
    sys.exit(run_sqlfluff("lint", require_dbt))


def fix() -> None:
    """Entry point for sqlfluff-project-fix command."""
    require_dbt = parse_args(sys.argv[1:])
    sys.exit(run_sqlfluff("fix", require_dbt))


if __name__ == "__main__":
    # Default to lint mode when run directly
    lint()
