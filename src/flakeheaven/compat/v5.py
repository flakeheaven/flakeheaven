from __future__ import annotations
from collections import defaultdict
from typing import Any, Iterator, Optional

from flake8.main.application import Application
from flake8.options import config as f8_opts_config

from flakeheaven.compat.base import FlakeHeavenApplicationInterface
from flakeheaven.compat.base import REX_CODE
from flakeheaven.compat.base import ALIASES
from flakeheaven.compat.base import TomlAndRawConfigParser
from flake8.options.manager import OptionManager
from flakeheaven.patched._checkers import FlakeHeavenCheckersManager

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

    @staticmethod
    def get_option_manager_keys(option_manager: OptionManager) -> set:
        return (vars(option_manager.parse_args([]))).keys()


    def get_exit_code(self):
        return self.exit_code()

    def make_file_checker_manager(self) -> None:
        self.file_checker_manager = FlakeHeavenCheckersManager(
            baseline=self.options.baseline,
            style_guide=self.guide,
            arguments=self.options.filenames,
            checker_plugins=self.plugins.checkers,
            relative=self.options.relative,
        )

__all__ = [
    "FlakeHeavenApplication",
]
