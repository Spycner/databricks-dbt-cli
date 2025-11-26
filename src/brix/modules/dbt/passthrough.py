"""dbt module - business logic for dbt operations."""

import subprocess

from brix.utils.logging import get_logger


class DbtNotFoundError(Exception):
    """Raised when dbt executable cannot be found."""


def find_dbt_executable() -> str:
    """Find the dbt executable path.

    This function handles two scenarios:
    1. brix is installed in the same venv as dbt - dbt should be directly available
    2. brix is installed as a global tool - need to discover project venv with dbt

    Returns:
        Path to the dbt executable.

    Raises:
        DbtNotFoundError: If dbt cannot be found.
    """
    # TODO: Implement venv discovery logic for when brix is installed globally
    # but dbt is in a project-specific venv. This could involve:
    # - Looking for .venv/ in current directory or parent directories
    # - Checking for pyproject.toml/requirements.txt to identify project root
    # - Activating the discovered venv or returning path to its dbt executable

    # For now, assume dbt is available in PATH (same venv scenario)
    return "dbt"


def pre_dbt_hook() -> None:
    """Hook for setup before running dbt. Placeholder for future logic."""
    # TODO: Placeholder for other stuff that has to happen before running dbt.
    pass


def run_dbt(args: list[str]) -> int:
    """Run dbt with the given arguments and return exit code.

    Args:
        args: List of arguments to pass to dbt.

    Returns:
        Exit code from the dbt process (1 if dbt not found).
    """
    logger = get_logger()

    pre_dbt_hook()

    try:
        dbt_path = find_dbt_executable()
    except DbtNotFoundError as e:
        logger.error(str(e))
        return 1

    logger.debug("Executing dbt command: %s %s", dbt_path, " ".join(args))
    try:
        # "unsafe" passthrough is intended, we trust the user to pass valid arguments. Its their local machine.
        result = subprocess.run([dbt_path, *args])  # noqa: S603
    except FileNotFoundError:
        logger.error(
            "dbt not found in PATH. Ensure dbt is installed and available.\n"
            "If using a virtual environment, make sure it's activated or install brix in the same environment as dbt."
        )
        return 1
    except OSError as e:
        logger.error("Failed to execute dbt: %s", e)
        return 1

    logger.debug("dbt exited with code: %d", result.returncode)

    return result.returncode
