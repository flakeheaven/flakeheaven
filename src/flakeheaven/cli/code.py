from __future__ import annotations

from typer import Exit

from rich import print
from rich.table import Table
from typer import Exit
# app
from .._constants import NAME, VERSION, ExitCode
from flakeheaven.logic._extractors import extract
# from .._patched import FlakeHeavenApplication
# from .._types import CommandResult


from flakeheaven.cli.base import Flake8Context
from flakeheaven.compat.base import FlakeHeavenApplicationInterface

def code_command(
    app: FlakeHeavenApplicationInterface,
    redir,
    code:str
):
    """Show plugin name and message for given code."""

    plugins = app.get_installed()
    if not plugins:
        print('[red]no plugins installed[/red]')
        raise Exit(code=ExitCode.NO_PLUGINS_INSTALLED)
    messages = []
    checked = set()
    for plugin in plugins:
        if plugin['name'] in checked:
            continue
        checked.add(plugin['name'])
        if not code.startswith(tuple(plugin['codes'])):
            continue
        try:
            codes = extract(plugin['name'])
        except ImportError:
            continue
        if code not in codes:
            continue
        messages.append(dict(
            plugin=plugin['name'],
            message=codes[code],
        ))

    if not messages:
        print('[red]no messages found[/red]')
        raise Exit(code=ExitCode.NO_CODES)

    table = Table(
        title=f"flake8 code: {code}",
        expand=False
    )


    for column in ["PLUGIN", "MESSAGE"]:
        table.add_column(
            f'[yellow]{column}[/yellow]',
            justify="left",
            no_wrap=True
        )


    for message in messages:
        table.add_row(
            message['plugin'],
            message['message'],
        )
    with redir:
        print(table)

def command(
    ctx: Flake8Context,
    code: str
):
    """Show plugin name and message for given code."""
    return code_command(ctx.flake8_app, ctx.output_redir, code)
