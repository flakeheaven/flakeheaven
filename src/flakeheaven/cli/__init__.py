"""command-line application for flakeheaven"""

# future
from __future__ import annotations

# built-in
from __future__ import annotations
import sys
from typing import List, NoReturn

from typer import secho
from typer import echo
from typer import Context
from typer import Typer

# app
from flakeheaven.compat.base import CompatModule
from flakeheaven.cli.base import Flake8Typer

# from flakeheaven.cli.base import register_initialize_flake8
from flakeheaven.cli.version import version_callback
from flakeheaven.cli.plugins import get_plugins

# from flakeheaven._constants import ExitCode
# from flakeheaven._logic import colored
# from flakeheaven._types import CommandResult
# from flakeheaven.commands import COMMANDS


entrypoint = Flake8Typer(
    name="flakeheaven",
    rich_markup_mode="rich",
    add_completion=False,
    no_args_is_help=True,
    # callback=version_callback,
)
"""Default entrypoint for CLI (flakeheaven): typer app."""

entrypoint.callback(
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)(version_callback)
entrypoint.command(
    name="plugins",
)(get_plugins)


def flake8_entrypoint(argv: List[str] = None) -> NoReturn:
    """Entrypoint with the same behavior as flake8 (flake8heavened)"""
    if argv is None:
        argv = sys.argv[1:]
    exit_code, msg = main(["lint"] + argv)
    if msg:
        print(colored(msg, "red"))
    if isinstance(exit_code, ExitCode):
        exit_code = exit_code.value
    sys.exit(exit_code)
