from contextlib import nullcontext
from contextlib import redirect_stdout
import json
from rich.json import JSON
from flake8 import LOG

from flakeheaven.cli.base import Flake8Context

from rich import print_json


from flakeheaven.compat.base import FlakeHeavenApplicationInterface
import typer

EXCLUDED = {
    "jobs",
}


class ConfigEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except Exception:
            return repr(o)


def show_config(
    app: FlakeHeavenApplicationInterface,
    excluded: set,
    *,
    plugins_only: bool,
):
    config = {k: v for k, v in vars(app.options).items() if k not in excluded}
    if plugins_only:
        config = config["plugins"]

    output_file = app.options.output_file
    if output_file:
        fp = open(output_file, "a+")
        redir = redirect_stdout(fp)
    else:
        redir = nullcontext()

    [h.flush() for h in LOG.handlers]
    with redir:
        print_json(json.dumps(config, cls=ConfigEncoder))


def command(
    ctx: Flake8Context,
    plugins_only: bool = typer.Option(
        False, help="If set, show only the plugins section of the config"
    ),
):
    """Show flake8 configuration after flakeheaven consolidation."""
    return show_config(
        ctx.flake8_app,
        excluded=EXCLUDED,
        plugins_only=plugins_only,
    )
