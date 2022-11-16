"""command-line application for flakeheaven"""

# future
from __future__ import annotations

# built-in
from __future__ import annotations
import sys
from types import ModuleType
from typing import Iterator, List, NoReturn

from typer import secho
from typer import echo
from typer import Context
from typer import Typer
from pathlib import Path
from importlib import import_module
# app
from flakeheaven.compat.base import CompatModule
from flakeheaven.cli.base import Flake8Typer

# from flakeheaven.cli.base import register_initialize_flake8
from flakeheaven.cli.version import version_callback
from flakeheaven.cli import plugins

# from flakeheaven._constants import ExitCode
# from flakeheaven._logic import colored
# from flakeheaven._types import CommandResult
# from flakeheaven.commands import COMMANDS

CLI_PKG = Path(__file__).parent

CLI_SUBMODULES_NOT_COMMANDS = (
    "__init__",
    "base",
    "version",
)

def get_commands() -> Iterator[tuple[str, callable]]:
    for path in sorted(CLI_PKG.glob("*.py"), reverse=True):
        module_dot_path = ".".join(path.relative_to(CLI_PKG.parents[1]).with_suffix("").parts)
        if any(
            module_dot_path.endswith(exclude)
            for exclude in CLI_SUBMODULES_NOT_COMMANDS
        ):
            continue
        module = import_module(module_dot_path)
        yield module.__name__.split(".")[-1] , module.command

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

for name, command in get_commands():
    entrypoint.command(
        name=name,
    )(command)


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
