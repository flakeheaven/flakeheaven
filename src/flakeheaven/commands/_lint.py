# app
from .._constants import NAME, VERSION
from .._patched import FlakeHeavenApplication
from .._types import CommandResult


def lint_command(argv) -> CommandResult:
    """Run patched flake8 against the code.
    """
    app = FlakeHeavenApplication(program=NAME, version=VERSION)
    try:
        app.run(argv)
        app.exit()
    except SystemExit as exc:
        return int(exc.code), ''
    raise RuntimeError('unreachable')
