"""Brix CLI - an exploration for Databricks."""

import typer

app = typer.Typer(help="Brix CLI - an exploration for Databricks.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Brix CLI entry point."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
