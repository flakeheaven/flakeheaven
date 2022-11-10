from __future__ import annotations

import argparse
import abc
import configparser
import re
from types import ModuleType
from typing import (
    Dict,
    Iterator,
    Tuple,
    Type,
    Union,
    Protocol,
    Optional,
    List,
    Any,
    runtime_checkable,
)

from itertools import chain
from pathlib import Path
from importlib import import_module
import typing

from flake8 import __version_info__
from flake8.main.application import Application
from flake8.options.manager import Option

from flakeheaven.logic._config import _parse_config


COMPAT_PKG = Path(__file__).parent

REX_CODE = re.compile(r"^[A-Z]{1,9}[0-9]{0,5}$")

ALIASES = {
    "flake-mutable": ("M511",),
    "flake8-bandit": ("S",),
    "flake8-django": ("DJ",),  # they say `DJ0` prefix but codes have `DJ10`
    "flake8-future-import": ("FI",),
    "flake8-mock": ("M001",),
    "flake8-pytest": ("T003",),
    "flake8-annotations-complexity": ("TAE002", "TAE003"),
    "logging-format": ("G",),
    "pycodestyle": ("W", "E"),
    "pylint": ("C", "E", "F", "I", "R", "W"),
}


# def get_toml_config(
#     path: Optional[Path] = None,
#     *,
#     enforce_keys_from: Dict[str, Option] | None = None,
# ) -> Dict[str, Any]:
#     """Extract config from TOML.

#     Args:
#         path: toml filepath. If not set, searches in cwd parents.
#         enforce_keys_from: Mapping of configuration option names to
#          :class:`~flake8.options.manager.Option` instances. It is
#          used to convert ``dashed-names`` in `toml` to
#          :class:`~flake8.options.config.ConfigParser` namespace so
#          it can be updated via its ``__dict__``. Typically, it comes
#          from either
#          :attr:`~flake8.options.config.ConfigParser.config_options`,
#          or directly from
#          :attr:`~flake8.options.manager.OptionManager.config_options_dict`.
#     """
#     if path is not None:
#         toml_config = read_config(path)
#     else:
#         # lookup for config from current dir up to root
#         root = Path().resolve()
#         for dir_path in chain([root], root.parents):
#             path = dir_path / "pyproject.toml"
#             if path.exists():
#                 toml_config = read_config(path)
#                 break
#         else:
#             toml_config = {}

#     if not enforce_keys_from:
#         return toml_config

#     for name in list(toml_config.keys()):
#         try:
#             option = enforce_keys_from[name]
#             dst = option.config_name
#             if dst == name:
#                 continue
#             if dst is None:
#                 raise ValueError(
#                     f"Unable to parse `{path}`. "
#                     f"Reason: option {option}.config_name not set. "
#                     f"Maybe its not enabled as `parse_from_config`?"  # noqa: C812
#                 )
#         except KeyError:
#             continue

#         toml_config[dst] = toml_config.pop(name)
#     return toml_config


def extract_toml_config_path(argv: List[str]) -> Tuple[Optional[Path], List[str]]:
    if not argv:
        return None, argv

    # TODO: Why was this necessary?
    # <pwoolvett 2022-11-10T10:52:08 >
    # if "--help" in argv:
    #     argv = argv.copy()
    #     argv.remove("--help")
    #     if not argv:
    #         return None, ["--help"]

    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    known, unknown = parser.parse_known_args(argv)
    if known.config and known.config.endswith(".toml"):
        return Path(known.config).expanduser(), unknown
    return None, argv


class TomlAndRawConfigParser(configparser.RawConfigParser):
    def _read(self, fp, fpname):
        path = Path(fpname)
        if path.suffix != ".toml":
            return super()._read(fp, fpname)

        toml_config = {"flake8": _parse_config(fp.read())}

        self.read_dict(toml_config, fpname)


class FlakeHeavenApplicationInterface(abc.ABC, Application):
    initialized: bool = False

    def get_installed(self) -> Iterator[dict[str, Any]]:
        return sorted(self.gen_installed(), key=lambda p: p["name"])

    def initialize(self, args: list[str]):
        if not self.initialized:
            args = self.before_initialize(args)

            super().initialize(args)
            self.initialized = True

    # def parse_preliminary_options(
    #     self,
    #     argv: List[str],
    # ) -> Tuple[argparse.Namespace, List[str]]:
    #     # if passed `--config` with path to TOML-config, we should extract it
    #     # before passing into flake8 mechanisms
    #     self._toml_config_path, argv = extract_toml_config_path(argv=argv)
    #     breakpoint();print()  # TODO remove this
    #     return super().parse_preliminary_options(argv)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.post_init()

    @abc.abstractmethod
    def post_init(self) -> None:
        ...

    @abc.abstractmethod
    def before_initialize(self, args: list[str]) -> list[str]:
        ...

    @abc.abstractmethod
    def gen_installed(self) -> Iterator[dict[str, Any]]:
        ...

    @abc.abstractmethod
    def get_missing(self) -> list[str]:
        ...


class CompatModule(ModuleType):
    FlakeHeavenApplication: Type[
        FlakeHeavenApplicationInterface
    ]  # type(FlakeHeavenApplicationInterface)


_TYPE_CHECK_PAT = None


def get_type_check_pattern():
    global _TYPE_CHECK_PAT
    if _TYPE_CHECK_PAT is None:
        _TYPE_CHECK_PAT = re.compile(r"(?<=Type\[)(?:.*(?:\s*,)?)+(?=\])")
    return _TYPE_CHECK_PAT


def is_class_type_hint(annotation_type):
    found = get_type_check_pattern().findall(annotation_type)
    if len(found) != 1:
        return False
    inner = found[0].split(",")
    if len(inner) != 1:
        return False

    return inner[0]


def validate(module: ModuleType) -> CompatModule:
    for name, annotation_type in CompatModule.__annotations__.items():
        attr = getattr(module, name)
        inner = is_class_type_hint(annotation_type)
        if inner:
            against = type(globals()[inner])
        else:
            against = annotation_type
        check = isinstance(attr, against)
        if not check:  # type: ignore
            raise ValueError(
                f"Wrong value for '{module.__name__}.{name}'"
                f". It's {attr}, but should be {annotation_type}"
            )

    candidate = Path(module.__file__).stem[1:]
    if int(candidate) != __version_info__[0]:
        raise NotImplementedError(
            f"flake8 version mismatch: installed={__version_info__}, module={candidate}"
        )

    return module  # type: ignore


def get_candidates() -> Iterator[CompatModule]:
    for path in sorted(COMPAT_PKG.glob("*.py"), reverse=True):
        module = ".".join(path.relative_to(COMPAT_PKG.parents[1]).with_suffix("").parts)
        if any(
            module.endswith(exclude)
            for exclude in (
                "__init__",
                "base",
            )
        ):
            continue
        yield import_module(module)


def select_provider():

    errors = {}
    for candidate_module in get_candidates():
        try:
            return validate(candidate_module)
        except Exception as exc:
            errors[candidate_module.__name__] = exc
    else:
        raise LookupError(
            "Unable to locate valid flake8 compatibility layer" f". Errors:\n{errors}"
        )
