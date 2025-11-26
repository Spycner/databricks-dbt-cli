# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

Use `uv` for all Python operations. Task runner commands via poethepoet:

```bash
uv run poe lint       # Run ruff linting
uv run poe format     # Run ruff formatting
uv run poe typecheck  # Run ty type checking
uv run poe test       # Run pytest
uv run poe check      # Run lint + typecheck together
```

Single test: `uv run pytest test/test_file.py::test_name -v`

Run the CLI: `uv run brix --help`

## Code Style

- Python 3.10+, strict type hints required (ANN rules enforced)
- Google-style docstrings
- Line length: 120 characters
- Ruff handles linting and formatting
- ty for type checking (src-layout aware via `tool.ty.environment.root`)

## Project Structure

- `src/brix/` - Main package (src-layout)
- `test/` - Tests (relaxed rules: no type hints, docstrings, or assert warnings required)

## Architecture

**CLI Entry Point** (`main.py`): Typer-based CLI with global callback pattern. Global options (--version, --log-level, --log-path, --log-json) are processed before subcommands. Add new commands via `@app.command()` decorators.

**Logging System** (`utils/logging.py`): Terraform-style logging with environment variables (`BRIX_LOG`, `BRIX_LOG_PATH`, `BRIX_LOG_JSON`) and CLI flag overrides. Uses thread-safe singleton pattern. Call `get_logger()` from any module to access the logger.

**Configuration Pattern**: Uses `pydantic-settings` for env var parsing with `BRIX_` prefix. CLI arguments override environment variables.

**Version Checking** (`version_check.py`): Non-blocking update checker using background threads. Caches results to `~/.cache/brix/` with 24-hour TTL.
