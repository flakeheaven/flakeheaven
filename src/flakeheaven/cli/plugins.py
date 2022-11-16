"""Show all installed plugins, their codes prefix, and matched rules from config."""

from typing import Iterator, Tuple
from rich import print
from flakeheaven._constants import ExitCode
from flakeheaven.logic._plugin import get_plugin_rules

from rich.table import Table

from flakeheaven.cli.base import Flake8Context
from flakeheaven.compat.base import FlakeHeavenApplicationInterface

def yield_plugins(app, plugins) -> Iterator[Tuple[str, str, str, list[str]]]:
    visited = set()
    for plugin in plugins:
        # Plugins returned by get_installed are unique by name and type.
        # We are not showing type, so, let's show one name only once.
        name = plugin['name']
        if name in visited:
            continue
        visited.add(name)
        rules = get_plugin_rules(
            plugin_name=name,
            plugins=app.options.plugins,
        )
        yield name, plugin['version'], plugin['codes'], rules

def color_rules(rules:list[str]):
    return [
        f"[green]{rule}[/green]" if rule[0] == '+'
        else f"[red]{rule}[/red]" if rule[0] == '-'
        else f"{rule}"
        for rule in rules
    ]




def get_plugins(
    app: FlakeHeavenApplicationInterface,
    redir,
):
    """Show all installed plugins, their codes prefix, and matched rules from config."""

    plugins = app.get_installed()
    if not plugins:
        return ExitCode.NO_PLUGINS_INSTALLED, 'no plugins installed'

    table = Table(
        title="Flakeheaven plugins rules",
        expand=False
    )
    columns = ["NAME", "VERSION", "CODES", "RULES"]
    for column in columns:
        table.add_column(column, justify="left", style="yellow", no_wrap=True)

    for name, version, codes, rules in yield_plugins(app, plugins):
        colored_rules = color_rules(rules)
        color = 'green' if colored_rules else 'red'
        table.add_row(
            f"[{color}]{name}[/{color}]",
            f"{version}",
            ', '.join(codes),
            ', '.join(colored_rules),
        )
    with redir:
        print(table)

def command(
    ctx: Flake8Context,
):
    """Show all installed plugins, their codes prefix, and matched rules from config."""
    return get_plugins(ctx.flake8_app, ctx.output_redir)
