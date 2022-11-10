
# future
from __future__ import annotations

# built-in
from __future__ import annotations
import functools
import sys
from typing import List, NoReturn

from typer import secho
from typer import echo
from typer import Context
from typer import Option
from typer import Typer
from typer import Exit
from typer.core import TyperCommand

# app
from flakeheaven.compat.base import CompatModule
from flakeheaven.compat.base import select_provider
# from flakeheaven.cli.version import version_or_initialize_flake8


class Flake8Typer(Typer):
    def command(self, *a, **kw):
        kw.setdefault(
            "context_settings",
            {"allow_extra_args": True, "ignore_unknown_options": True}
        )

        cmd_decorator = super().command(*a, **kw)

        def inject_initialized_flakeheaven_to_context(f_orig):
            @functools.wraps(f_orig)
            def f(*a, **kw):
                ctx = kw['ctx']
                ctx.flake8 = select_provider()
                ctx.flake8_app = ctx.flake8.FlakeHeavenApplication()
                ctx.flake8_app.initialize(ctx.args)
                return f_orig(*a, **kw)
            return cmd_decorator(f)
        return inject_initialized_flakeheaven_to_context

    # def callback(self, *a, **kw):
    #     kw.setdefault(
    #         "context_settings",
    #         {"allow_extra_args": True, "ignore_unknown_options": True}
    #     )
    #     return super().callback(*a, **kw)
    # def __init__(self, *a, **kw):
    #     super().__init__(*a, **kw)
    #     self.callback(invoke_without_command=True)(self.__callback)

    # def __callback(
    #     self, 
    #     version: bool = Option(
    #         None,
    #         "--version",
    #         callback=version_or_initialize_flake8,
    #         is_eager=True,
    #         help="Show FlakeHeaven version and exit."
    #     ),
    #     ctx: Context = ...,
    # ):
    #     ...

class Flake8Context(Context):
    flake8: CompatModule
    # flake8_app: CompatModule


class Flake8ContextParent(Context):
    parent: Flake8Context
