# external
from flake8 import __version__ as flake8_version

# app
from .._constants import ExitCode
from .._logic import colored
from .._types import CommandResult
from .._version import __version__ as flakeheaven_version


def version_command(argv) -> CommandResult:
    """Show FlakeHeaven version.
    """
    print('FlakeHeaven', colored(flakeheaven_version, 'green'))
    print('Flake8   ', colored(flake8_version, 'green'))
    print('For plugins versions use', colored('flakeheaven plugins', 'green'))
    return ExitCode.OK, ''
