# app
from .._constants import NAME, VERSION, ExitCode
from .._logic._discover import NoPlugins, get_missing
from .._patched import FlakeHeavenApplication
from .._types import CommandResult


def missed_command(argv) -> CommandResult:
    """Show patterns from the config that has no matched plugin installed.
    """
    if argv and argv[0] == '--help':
        print(missed_command.__doc__)
        return ExitCode.OK, ''
    if argv:
        return ExitCode.TOO_MANY_ARGS, 'the command does not accept arguments'

    app = FlakeHeavenApplication(program=NAME, version=VERSION)
    try:
        missing = get_missing(app)
    except NoPlugins:
        return ExitCode.NO_PLUGINS_INSTALLED, 'no plugins installed'

    for pattern in missing:
        print(pattern)

    return ExitCode.PLUGINS_MISSING, ''
