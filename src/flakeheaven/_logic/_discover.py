# built-in
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, Iterator, List, Optional

# app
from ._plugin import get_plugin_name, get_plugin_rules


REX_CODE = re.compile(r'^[A-Z]{1,9}[0-9]{0,5}$')

ALIASES = {
    'flake-mutable': ('M511', ),
    'flake8-bandit': ('S', ),
    'flake8-django': ('DJ', ),  # they say `DJ0` prefix but codes have `DJ10`
    'flake8-future-import': ('FI', ),
    'flake8-mock': ('M001', ),
    'flake8-pytest': ('T003', ),
    'flake8-annotations-complexity': ('TAE002', 'TAE003'),
    'logging-format': ('G', ),
    'pycodestyle': ('W', 'E'),
    'pylint': ('C', 'E', 'F', 'I', 'R', 'W'),
}


class NoPlugins(Exception):
    """No plugins are installed and found."""


def get_installed(
    app,
    *,
    initialize: bool = True,
    initialize_args: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    plugins_codes = defaultdict(list)
    versions = dict()

    if initialize:
        app.initialize(initialize_args or [])
    codes: Iterable[str]

    for check_type in ('ast_plugins', 'logical_line_plugins', 'physical_line_plugins'):
        for plugin in getattr(app.check_plugins, check_type):
            key = (check_type, get_plugin_name(plugin.to_dictionary()))
            versions[key[-1]] = plugin.version

            # if codes for plugin specified explicitly in ALIASES, use it
            codes = ALIASES.get(plugin.plugin_name, [])
            if codes:
                plugins_codes[key] = list(codes)
                continue

            # otherwise get codes from plugin entrypoint
            code = plugin.name
            if not REX_CODE.match(code):
                raise ValueError('Invalid code format: {}'.format(code))
            plugins_codes[key].append(code)

    if 'flake8-docstrings' in versions:
        versions['flake8-docstrings'] = versions['flake8-docstrings'].split(',')[0]

    for (check_type, name), codes in plugins_codes.items():
        yield dict(
            type=check_type,
            name=name,
            codes=sorted(codes),
            version=versions[name],
        )


def get_missing(
    app,
    *,
    initialize: bool = True,
    initialize_args: Optional[List[str]] = None,
):
    installed_plugins = sorted(
        get_installed(app=app, initialize=initialize, initialize_args=initialize_args),
        key=lambda p: p['name'],
    )
    if not installed_plugins:
        raise NoPlugins('No plugins installed')

    patterns = []
    for pattern in app.options.plugins:
        for plugin in installed_plugins:
            rules = get_plugin_rules(
                plugin_name=plugin['name'],
                plugins={pattern: ['+*']},
            )
            if rules:
                break
        else:
            patterns.append(pattern)
    return patterns
