from __future__ import annotations
import argparse
from collections import defaultdict
import configparser
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple
from pathlib import Path

from flake8 import LOG
from flake8.main.application import Application
from flake8.options import config as f8_opts_config

# from flake8.options import aggregator

from flakeheaven.compat.base import FlakeHeavenApplicationInterface
from flakeheaven.compat.base import REX_CODE
from flakeheaven.compat.base import ALIASES
from flakeheaven.compat.base import TomlAndRawConfigParser

# from flakeheaven.compat.base import get_toml_config
# from flake8.options.manager import OptionManager
# from flakeheaven.logic._config import read_config


# def load_config(
#     config: Optional[str],
#     *a,
#     isolated: bool = False,
#     **kw,
# ):
#     breakpoint()
#     print()  # TODO remove this
#     cfg, cfg_dir = f8_opts_config._legacy_load_config(
#         config, *a, isolated=isolated, **kw
#     )
#     incoming = get_toml_config(
#         Path(config) if config is not None else config,
#     )
#     if "flake8" not in cfg:
#         cfg.add_section("flake8")
#     for k, v in incoming.items():
#         cfg.set("flake8", k, v)

#     return cfg, cfg_dir


# def parse_config(
#     option_manager: OptionManager,
#     cfg: configparser.RawConfigParser,
#     cfg_dir: str,
# ) -> Dict[str, Any]:
#     """Parse and normalize the typed configuration options."""
#     if "flake8" not in cfg:
#         return {}

#     config_dict = {}

#     for option_name in cfg["flake8"]:
#         option = option_manager.config_options_dict.get(option_name)
#         if option is None:
#             LOG.debug('Option "%s" is not registered. Ignoring.', option_name)
#             continue

#         # Use the appropriate method to parse the config value
#         value: Any
#         try:
#             if option.type is int or option.action == "count":
#                 value = cfg.getint("flake8", option_name)
#             elif option.action in {"store_true", "store_false"}:
#                 value = cfg.getboolean("flake8", option_name)
#             else:
#                 value = cfg.get("flake8", option_name)
#         except AttributeError:
#             value = cfg.get("flake8", option_name)
#         LOG.debug('Option "%s" returned value: %r', option_name, value)

#         final_value = option.normalize(value, cfg_dir)
#         assert option.config_name is not None
#         config_dict[option.config_name] = final_value

#     return config_dict


# def patch_config_module():
#     f8_opts_config._legacy_load_config = f8_opts_config.load_config
#     f8_opts_config.load_config = load_config

#     f8_opts_config._legacy_parse_config = f8_opts_config.parse_config
#     f8_opts_config.parse_config = parse_config
#     ...


# def parse_args(
#     self: OptionManager,
#     args: Optional[List[str]] = None,
#     values: Optional[argparse.Namespace] = None,
# ) -> Tuple[argparse.Namespace, List[str]]:
#     """Proxy to calling the OptionParser's parse_args method."""
#     self.generate_epilog()
#     self.update_version_string()
#     if values:
#         self.parser.set_defaults(**vars(values))
#     parsed_args = self.parser.parse_args(args)
#     # TODO: refactor callers to not need this
#     return parsed_args, parsed_args.filenames


def load_config(
    config: Optional[str],
    *a,
    **kw,
):
    config = "pyproject.toml" if config is None else config
    return f8_opts_config._legacy_load_config(config, *a, **kw)


def patch_config_module2():
    f8_opts_config.configparser.RawConfigParser = TomlAndRawConfigParser

    f8_opts_config._legacy_load_config = f8_opts_config.load_config
    f8_opts_config.load_config = load_config


class FlakeHeavenApplication(FlakeHeavenApplicationInterface, Application):
    def post_init(self) -> None:
        patch_config_module2()

    # def parse_preliminary_options(
    #     self, argv: Sequence[str]
    # ) -> Tuple[argparse.Namespace, List[str]]:
    #     ret = super().parse_preliminary_options(argv)
    #     return ret

    def before_initialize(self, args: list[str]) -> list[str]:
        return args

    def gen_installed(self) -> Iterator[dict[str, Any]]:
        plugins_codes = defaultdict(list)
        versions = dict()

        codes: list[str]

        for check_type in ("tree", "logical_line", "physical_line"):
            for plugin in getattr(self.plugins.checkers, check_type):
                name = plugin.plugin.package
                version = plugin.plugin.version
                key = (check_type, name)
                versions[key[-1]] = version

                # if codes for plugin specified explicitly in ALIASES, use it
                codes = ALIASES.get(name, [])
                if codes:
                    plugins_codes[key] = list(codes)
                    continue

                # otherwise get codes from plugin entrypoint
                code = plugin.plugin.entry_point.name
                if not REX_CODE.match(code):
                    raise ValueError("Invalid code format: {}".format(code))
                plugins_codes[key].append(code)

        if "flake8-docstrings" in versions:
            versions["flake8-docstrings"] = versions["flake8-docstrings"].split(",")[0]

        for (check_type, name), codes in plugins_codes.items():
            yield dict(
                type=check_type,
                name=name,
                codes=sorted(codes),
                version=versions[name],
            )

    def get_missing(self) -> list[str]:
        ...
