"""Show all installed plugins, their codes prefix, and matched rules from config."""

from typing import Iterator, Tuple
from rich import print
from flakeheaven._constants import ExitCode
from flakeheaven.logic._plugin import get_plugin_rules
# from flakeheaven._patched import FlakeHeavenApplication
# from flakeheaven._types import CommandResult

from rich.table import Table

table = Table(title="Star Wars Movies")

table.add_column("Released", justify="right", style="cyan", no_wrap=True)
table.add_column("Title", style="magenta")
table.add_column("Box Office", justify="right", style="green")

table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")

from flakeheaven.cli.base import Flake8ContextParent

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


        # colored_rules = []
        # for rule in rules:
        #     if rule[0] == '+':
        #         rule = colored(rule, 'green')
        #     elif rule[0] == '-':
        #         rule = colored(rule, 'red')
        #     colored_rules.append(rule)
        # color = 'green' if rules else 'red'
        # print(template.format(
        #     name=colored(name.ljust(name_width), color),
        #     version=plugin['version'].ljust(version_width),
        #     codes=', '.join(plugin['codes']).ljust(codes_width),
        #     rules=', '.join(colored_rules),
        # ))

def color_rules(rules:list[str]):
    return [
        f"[green]{rule}[/green]" if rule[0] == '+'
        else f"[red]{rule}[/red]" if rule[0] == '-'
        else f"{rule}"
        for rule in rules
    ]

def get_plugins(ctx: Flake8ContextParent):
    """Show all installed plugins, their codes prefix, and matched rules from config."""
    app = ctx.parent.flake8_app

    plugins = sorted(app.get_installed(), key=lambda p: p['name'])
    if not plugins:
        return ExitCode.NO_PLUGINS_INSTALLED, 'no plugins installed'

    table = Table(title="Flakeheaven plugins rules")
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
    print(table)
    # showed = set()
    # for plugin in plugins:
    #     # Plugins returned by get_installed are unique by name and type.
    #     # We are not showing type, so, let's show one name only once.
    #     if plugin['name'] in showed:
    #         continue
    #     showed.add(plugin['name'])

    #     rules = get_plugin_rules(
    #         plugin_name=plugin['name'],
    #         plugins=app.options.plugins,
    #     )
    #     colored_rules = []
    #     for rule in rules:
    #         if rule[0] == '+':
    #             rule = colored(rule, 'green')
    #         elif rule[0] == '-':
    #             rule = colored(rule, 'red')
    #         colored_rules.append(rule)
    #     color = 'green' if rules else 'red'
    #     print(template.format(
    #         name=colored(plugin['name'].ljust(name_width), color),
    #         version=plugin['version'].ljust(version_width),
    #         codes=', '.join(plugin['codes']).ljust(codes_width),
    #         rules=', '.join(colored_rules),
    #     ))
    return ExitCode.OK, ''
