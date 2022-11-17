
# future
from __future__ import annotations

# built-in
from contextlib import nullcontext
from contextlib import AbstractContextManager
from contextlib import redirect_stdout
import functools

from typer import Context
from typer import Typer
from flake8 import LOG
# app
from flakeheaven.compat.base import CompatModule
from flakeheaven.compat.base import select_provider
from flakeheaven.compat.base import FlakeHeavenApplicationInterface
# from flakeheaven.cli.version import version_or_initialize_flake8

def inject_flakeheaven_into_context(ctx):
    ctx.flake8 = select_provider()
    ctx.flake8_app = ctx.flake8.FlakeHeavenApplication()
    ctx.flake8_app.initialize(ctx.args)

def define_output_redir(ctx):
    app = ctx.flake8_app
    output_file = app.options.output_file
    if output_file:
        fp = open(output_file, "a+")
        redir = redirect_stdout(fp)
    else:
        redir = nullcontext()
    bkp = redir.__enter__

    def enter(self):
        [h.flush() for h in LOG.handlers]
        return bkp()

    redir.__enter__ = enter
    ctx.output_redir = redir

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
                inject_flakeheaven_into_context(ctx)
                define_output_redir(ctx)
                return f_orig(*a, **kw)
            return cmd_decorator(f)
        return inject_initialized_flakeheaven_to_context


class Flake8Context(Context):
    flake8: CompatModule
    output_redir: AbstractContextManager
    flake8_app: FlakeHeavenApplicationInterface
