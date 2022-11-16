

from rich import print
from typer import Exit
# app

from flakeheaven.logic._discover import get_missing, NoPlugins
from flakeheaven._constants import ExitCode

from flakeheaven.cli.base import Flake8Context
from flakeheaven.compat.base import FlakeHeavenApplicationInterface

def missed_command(
    app: FlakeHeavenApplicationInterface,
    redir,
):
    """Show patterns from the config that has no matched plugin installed."""

    try:
        missing = get_missing(app)
    except NoPlugins:
        print('no plugins installed')
        raise Exit(code=ExitCode.NO_PLUGINS_INSTALLED)

    with redir:
        for pattern in missing:
            print(pattern)

    return ExitCode.PLUGINS_MISSING, ''


def command(
    ctx: Flake8Context,
):
    """Show patterns from the config that has no matched plugin installed."""
    return missed_command(ctx.flake8_app, ctx.output_redir)
