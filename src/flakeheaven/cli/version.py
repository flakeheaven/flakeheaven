

from typing import Optional

from typer import secho
from typer import Typer
from typer import Option
from typer import Exit
from typer import Context
from rich import print

from flakeheaven import __version__


def version_or_initialize_flake8(
    value: bool,
    ctx: Context
):
    from flakeheaven.compat import flake8
    ctx.flake8 = flake8
    if value:
        version_data = {
            'FlakeHeaven': __version__,
            'Flake8': flake8.__version__,
            'For plugins versions run': 'flakeheaven plugins',
        }
        largest_description = max(map(len,version_data.keys()))
        for info, data in version_data.items():
            print(f'{info: <{largest_description}} : [green]{data}[/green]')
        raise Exit()
    ctx.flake8_app = app = ctx.flake8.FlakeHeavenApplication()
    app.initialize(ctx.args)
