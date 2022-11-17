from __future__ import annotations

import argparse
import abc
import configparser
import re
from types import ModuleType
from typing import (
    Callable,
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
from flake8.options.manager import OptionManager

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

def toml2ini(data):
    if isinstance(data, dict):
        return {
            toml2ini(k): toml2ini(v)
            for k,v in data.items()
        }
    if isinstance(data, (str, int, float)):
        return str(data)
    if isinstance(data, list):
        return ",".join(toml2ini(k) for k in data)
    raise NotImplementedError

class TomlAndRawConfigParser(configparser.RawConfigParser):

    def _read(self, fp, fpname):
        path = Path(fpname)
        if path.suffix != ".toml":
            return super()._read(fp, fpname)

        # toml_config = {"flake8": toml2ini(_parse_config(fp.read()))}
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

    @staticmethod
    @abc.abstractmethod
    def get_option_manager_keys(option_manager) -> set:
        ...

    @abc.abstractmethod
    def make_file_checker_manager(self):
        ...

    @abc.abstractmethod
    def get_exit_code(self):
        ...

class CompatModule(ModuleType):
    FlakeHeavenApplication: Type[FlakeHeavenApplicationInterface]

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

PROVIDER = None

def select_provider() -> CompatModule:
    global PROVIDER
    if PROVIDER is not None:
        return PROVIDER
    errors = {}
    for candidate_module in get_candidates():
        try:
            PROVIDER = validate(candidate_module)
            return PROVIDER
        except Exception as exc:
            errors[candidate_module.__name__] = exc
    else:
        raise LookupError(
            "Unable to locate valid flake8 compatibility layer" f". Errors:\n{errors}"
        )
