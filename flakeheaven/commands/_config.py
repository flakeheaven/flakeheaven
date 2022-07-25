# built-in
import atexit
import sys
import tempfile
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional, Tuple

# app
from .._constants import NAME, VERSION, ExitCode
from .._patched import FlakeHeavenApplication
from .._types import CommandResult


FLAKE8_DEFAULTS = {
    'verbose': 0,
    'output_file': None,
}

EXCLUDED = {
    'jobs',
}


def _inject_flake8_defaults(parser: ArgumentParser) -> None:
    """Inject some flake8 defaults.

    Defaults taken from
    `flake8.main.options:register_preliminary_options`.

    Args:
        parser: The parser to inject defaults into.

    Returns:
        Mapping of option names to actions.
    """

    parser.add_argument(
        '-v',
        '--verbose',
        default=FLAKE8_DEFAULTS['verbose'],
        action='count',
        help='Print more information about what is happening in flake8.'
        ' This option is repeatable and will increase verbosity each '
        'time it is repeated.',
    )
    parser.add_argument(
        '--output-file',
        default=FLAKE8_DEFAULTS['output_file'],
        help='Redirect report to a file.',
    )


def _maybe_backup_old_log(local_args: Namespace) -> Tuple[Optional[str], Path]:
    bkp: Optional[str] = local_args.output_file

    temp_dir = tempfile.TemporaryDirectory(prefix='flakeheaven-')
    logfile = Path(temp_dir.name) / 'config.log'
    local_args.output_file = str(logfile)
    atexit.register(lambda: temp_dir.cleanup())
    return bkp, logfile


def _parse(sys_argv) -> Tuple[Namespace, List[str], Optional[str], Path]:
    parser = ArgumentParser(
        description=config_command.__doc__,
    )
    parser.add_argument(
        '--plugins-only',
        action='store_true',
        help='If set, show only the plugins section of the config',
    )
    parser.add_argument(
        '--flake8-logs',
        action='store_true',
        default=False,
        help='If set, also include flake8 logs',
    )

    # l1, argv = parser.parse_known_args(sys_argv)
    _inject_flake8_defaults(parser)
    local_args, argv = parser.parse_known_args(sys_argv)

    bkp, logfile = _maybe_backup_old_log(local_args)

    # fix default verbose offfset
    verbose = FLAKE8_DEFAULTS['verbose']
    if local_args.verbose != verbose:
        local_args.verbose -= verbose

    av = [
        '--output-file',
        local_args.output_file,
    ]
    if local_args.verbose:
        av.append(f'-{"v" * local_args.verbose}')
    argv.extend(av)

    return local_args, argv, bkp, logfile


def get_config(argv) -> Tuple[dict, Namespace, Path, Optional[str]]:
    local_args, argv, bkp, logfile = _parse(argv)
    app = FlakeHeavenApplication(program=NAME, version=VERSION)
    app.initialize(argv)

    app.options.output_file = bkp
    config = {
        k: v for k, v in vars(app.options).items()
        if k not in EXCLUDED
    }
    if local_args.plugins_only:
        config = config['plugins']
    return config, local_args, logfile, bkp


def config_command(argv) -> CommandResult:
    """Show flake8 configuration after flakeheaven consolidation."""

    config, local_args, logfile, bkp = get_config(argv)

    try:
        logs = (
            '\n'.join(
                line
                for line in logfile.read_text().splitlines()
                if local_args.flake8_logs or line.startswith('flake8.flakeheaven')
            ) + '\n'
        )
    except FileNotFoundError:
        logs = ''

    stdout = f'{config}\n'

    if bkp and bkp not in ('stdout', 'stderr'):
        fileobj = open(bkp, 'a+')
        atexit.register(lambda: fileobj.close())
        fileobj_logs = fileobj_app = fileobj
    else:
        fileobj_logs = getattr(sys, bkp or 'stderr')
        fileobj_app = getattr(sys, bkp or 'stdout')

    print(logs, file=fileobj_logs)
    print(stdout, file=fileobj_app)

    return ExitCode.OK, ''
