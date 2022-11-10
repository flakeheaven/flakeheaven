# built-in
import json
from ast import literal_eval

from flake8.options.manager import OptionManager

from flakeheaven import __version__
from flakeheaven._constants import DEFAULTS
from flakeheaven.compat.base import select_provider

def set_flakeheaven_defaults(option_manager:OptionManager):
    option_manager.parser.set_defaults(**DEFAULTS)
    # TODO: are following lines actually necessary?
    
    # <pwoolvett 2022-11-10T18:05:28 >
    for k, v in DEFAULTS.items():
        option = option_manager.config_options_dict[k]
        option.default = v
        option.option_kwargs['default'] = v

def add_flakeheaven_options(option_manager:OptionManager):

    provider = select_provider()
    common = {
        "parse_from_config": True,
    }

    k0 = provider.FlakeHeavenApplication.get_option_manager_keys(option_manager)

    def add_option(*a, **kw):
        option_manager.add_option(*a, **common, **kw)

    add_option(
        "--baseline",
        nargs="*",
        help="path to baseline",
        default=None,
    )
    add_option(
        "--relative",
        action="store_true",
        help="Treat file paths as relative to directory containing baseline file",
    )
    add_option(
        "--safe",
        action="store_true",
        help="suppress exceptions from plugins",
        default=False,
    )
    add_option(
        "--error-on-missing",
        action="store_true",
        help="Error before linting if there are missing plugins",
    )
    add_option(
        "--plugins",
        help="flake8 plugin name to and associated rules dict.",
        default={
            'pyflakes': ['+*'],
            'pycodestyle': ['+*'],
        },
        type=literal_eval,
    )
    add_option(
        "--exceptions",
        nargs="*",
        help="per-file (or fnmatch glob) plugin rule exception",
        default={},
        type=literal_eval,
    )
    add_option(
        "--base",
        nargs="*",
        help="Upstream flakeheaven configuration. Can be local or remote.",
        default=None,
    )

    k1 = provider.FlakeHeavenApplication.get_option_manager_keys(option_manager)
    new_keys = k1-k0
    return new_keys

class Flakeheaven:
    # name and version are required for flake8<5
    name = "flakeheaven"
    version = __version__
    _f8_keys: set

    @classmethod
    def add_options(cls, option_manager: OptionManager) -> None:
        cls._f8_keys = add_flakeheaven_options(option_manager)
        set_flakeheaven_defaults(option_manager)


    @classmethod
    def parse_options(cls, option_manager, options, args) -> None:
        require_eval = (
            "baseline",
            "plugins",
            "exceptions",
            "base",
        )
        require_eval = cls._f8_keys
        for opt in require_eval:
            stringified = getattr(options, opt)
            if stringified is None:
                continue
            if not isinstance(stringified, str):
                continue
            setattr(options, opt, literal_eval(stringified))
