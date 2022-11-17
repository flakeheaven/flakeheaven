# built-in
import re

from rich import print
from rich.table import Table
from typer import Exit
from typer import Argument
# app
from flakeheaven._constants import ExitCode
from flakeheaven.logic._extractors import extract
# from .._types import CommandResult


from flakeheaven.cli.base import Flake8Context

REX_CODE = re.compile(r'([A-Z]+)([0-9]+)')
REX_PLACEHOLDER = re.compile(r'(\{[a-z0-9]+\}|\%[a-z])')
REX_QUOTES = re.compile(r'([\"\'\`][\w\s\:\_\-\.]+[\"\'\`])')


def codes_command(
    redir,
    plugin:str,
):
    """Show available codes and messages for given plugin."""

    try:
        codes = extract(plugin)
    except ImportError as e:
        print('cannot import module: {}'.format(e.args[0]))
        raise Exit(ExitCode.IMPORT_ERROR)
    if not codes:
        print('no codes found')
        raise Exit(ExitCode.NO_CODES)

    table = Table(
        title=f"flake8 codes for: '{plugin}'",
        expand=False
    )
    for column in ["CODE", "DESCRIPTION"]:
        table.add_column(
            f'[yellow]{column}[/yellow]',
            justify="left",
            no_wrap=True
        )
    for code, info in codes.items():
        table.add_row(
            code,
            info,
        )

    with redir:
        print(table)


def command(
    ctx: Flake8Context,
    plugin: str = Argument(..., help="Plugin name to show codes from (example: 'flake8-fixme')"),
):
    """Show available codes and messages for given plugin."""
    return codes_command(ctx.output_redir, plugin)
