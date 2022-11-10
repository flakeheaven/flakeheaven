from typing import Optional

from flake8 import __version__ as flake8_version
from typer import secho
from typer import Typer
from typer import Option
from typer import Exit
from typer import Context
from rich import print
from rich.table import Table
from flakeheaven import __version__


def version_or_initialize_flake8(value: bool, ctx: Context):
    if value:
        version_data = {
            "FlakeHeaven": __version__,
            "Flake8": flake8_version,
        }

        table = Table(title="Flakeheaven Version", expand=False)
        columns = ["Name", "[green]Version/Description[/green]"]
        for column in columns:
            table.add_column(column, justify="left", no_wrap=True)
        # largest_description = max(map(len, version_data.keys()))
        for info, data in version_data.items():
            table.add_row(
            info,
            f"[green]{data}[/green]",
        )
        print(table)
        print(f"For plugins versions run: '[green]flakeheaven plugins[/green]'",)
        raise Exit()



def version_callback(
    version: bool = Option(
        None,
        "--version",
        callback=version_or_initialize_flake8,
        is_eager=True,
        help="Show FlakeHeaven version and exit.",
    ),
    ctx: Context = ...,
):
    ...
