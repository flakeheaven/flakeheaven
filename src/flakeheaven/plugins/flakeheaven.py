# built-in
from ast import AST
from ast import literal_eval
from tokenize import TokenInfo
from typing import Sequence, TypeVar

from flakeheaven import __version__
from flakeheaven._constants import DEFAULTS
# from flakeheaven.compat.base import get_toml_config


def override_defaults(option_manager):
    for k, v in DEFAULTS.items():
        try:
            option_manager.config_options_dict[k].default = v
        except KeyError as exc:
            print(exc)


def add_flakeheaven_options(option_manager):

    common = {
        "parse_from_config": True,
    }

    def add_option(*a, **kw):
        option_manager.add_option(*a, **common, **kw)

    add_option("--baseline", nargs="*", help="path to baseline")
    add_option(
        "--relative",
        action="store_true",
        help="Treat file paths as relative to directory containing baseline file",
    )
    add_option("--safe", action="store_true", help="suppress exceptions from plugins")
    add_option(
        "--error-on-missing",
        action="store_true",
        help="Error before linting if there are missing plugins",
    )
    add_option(
        "--plugins",
        nargs="*",
        help="suppress exceptions from plugins",
    )
    add_option(
        "--exceptions",
        nargs="*",
        help="suppress exceptions from plugins",
    )
    add_option(
        "--base",
        nargs="*",
        help="suppress exceptions from plugins",
    )


# def enforce_defaults_from_toml():
#     ...


# class FlakeheavenToml:
#     def __init__(self):
#         self.config = None
#         self._data = None

#     @property
#     def data(self):
#         if not self._data:
#             self._data = get_toml_config(
#                 Path(self.config) if self.config is not None else self.config,
#             )
#         return self._data


class Flakeheaven:
    # name and version are required for flake8<5
    name = "flakeheaven"
    version = __version__

    @classmethod
    def add_options(cls, option_manager) -> None:
        add_flakeheaven_options(option_manager)
        override_defaults(option_manager)

        # cls.fh_toml = FlakeheavenToml()
        # bkp = option_manager.parser.set_defaults
        # def set_defaults(*args, **kwargs):
        #     breakpoint();print()  # TODO remove this
        #     bkp(**kwargs)
        # option_manager.parser.set_defaults = set_defaults

        # from flakeheaven.compat import flake8
        # Namespace(**vars(args1), **vars(args2))
        # option_manager.parser.set_defaults = bkp()
        # breakpoint()
        # print()  # TODO remove this

    @classmethod
    def parse_options(cls, option_manager, options, args) -> None:
        require_eval = (
            "baseline",
            "plugins",
            "exceptions",
            "base",
        )
        for opt in require_eval:
            stringified = getattr(options, opt)
            if stringified is None:
                continue
            if not isinstance(stringified, str):
                continue
            setattr(options, opt, literal_eval(stringified))
