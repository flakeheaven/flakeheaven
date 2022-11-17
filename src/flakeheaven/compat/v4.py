"""Flake8 compatibility layer for flake8 v4."""

from __future__ import annotations
from collections import defaultdict
from typing import Any, Iterator
from flake8.main.application import Application
from flake8.options import config as f8_opts_config

# from flake8.options import aggregator
from flake8.options.manager import OptionManager

from flakeheaven.compat.base import FlakeHeavenApplicationInterface
from flakeheaven.compat.base import TomlAndRawConfigParser
from flakeheaven.patched._checkers import FlakeHeavenCheckersManager

# app
from flakeheaven.logic._plugin import get_plugin_name, get_plugin_rules

from flakeheaven.compat.base import ALIASES
from flakeheaven.compat.base import REX_CODE

# from flakeheaven.logic._config import read_config


class ConfigFileFinder(f8_opts_config.ConfigFileFinder):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.project_filenames = (
            "pyproject.toml",
            *self.project_filenames,
        )


def patch_config_module():
    f8_opts_config.configparser.RawConfigParser = TomlAndRawConfigParser
    f8_opts_config.ConfigFileFinder = ConfigFileFinder


class FlakeHeavenApplication(FlakeHeavenApplicationInterface, Application):
    def post_init(self):
        patch_config_module()

    def gen_installed(self) -> Iterator[dict[str, Any]]:
        plugins_codes = defaultdict(list)
        versions = dict()

        codes: list[str]

        for check_type in (
            "ast_plugins",
            "logical_line_plugins",
            "physical_line_plugins",
        ):
            for plugin in getattr(self.check_plugins, check_type):
                key = (check_type, get_plugin_name(plugin.to_dictionary()))
                versions[key[-1]] = plugin.version

                # if codes for plugin specified explicitly in ALIASES, use it
                codes = ALIASES.get(plugin.plugin_name, [])
                if codes:
                    plugins_codes[key] = list(codes)
                    continue

                # otherwise get codes from plugin entrypoint
                code = plugin.name
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

    def get_missing(self):
        installed_plugins = self.get_installed()
        if not installed_plugins:
            raise NoPlugins("No plugins installed")

        patterns = []
        for pattern in self.options.plugins:
            for plugin in installed_plugins:
                rules = get_plugin_rules(
                    plugin_name=plugin["name"],
                    plugins={pattern: ["+*"]},
                )
                if rules:
                    break
            else:
                patterns.append(pattern)
        return patterns

    def before_initialize(self, args: list[str]) -> list[str]:
        return args

    @staticmethod
    def get_option_manager_keys(option_manager: OptionManager) -> set:
        return vars(option_manager.parse_args([])[0]).keys()

    def get_exit_code(self):
        try:
            self.exit()
        except SystemExit as exc:
            return exc.code

    def make_file_checker_manager(self) -> None:
        self.file_checker_manager = FlakeHeavenCheckersManager(
            baseline=self.options.baseline,
            style_guide=self.guide,
            arguments=self.args,
            checker_plugins=self.check_plugins,
            relative=self.options.relative,
        )

__all__ = [
    "FlakeHeavenApplication",
]
