"""Brix CLI - an exploration for Databricks."""

from typing import Annotated

import typer

from brix import __version__

app = typer.Typer(help="Brix CLI - an exploration for Databricks.")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"brix {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True, help="Show version and exit."),
    ] = False,
) -> None:
    """Brix CLI entry point."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
