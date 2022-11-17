from __future__ import annotations

from typer import Exit

from rich import print
from typer import Exit

# app
# from .._constants import NAME, VERSION
# from .._patched import FlakeHeavenApplication
# from .._types import CommandResult
from flakeheaven.cli.base import Flake8Context
from flakeheaven.compat.base import FlakeHeavenApplicationInterface

def lint_command(
    app: FlakeHeavenApplicationInterface,
    redir,
    argv: list[str],
):
    """Run patched flake8 against the code."""
    app.run(argv)
    code = app.get_exit_code()
    raise Exit(code)


def command(
    ctx: Flake8Context,
):
    """Run patched flake8 against the code."""
    return lint_command(ctx.flake8_app, ctx.output_redir, ctx.args)
