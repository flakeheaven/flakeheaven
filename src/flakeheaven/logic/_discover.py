# built-in
import re

# app
from ._plugin import get_plugin_rules


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


class NoPlugins(LookupError):
    """No plugins are installed and found."""


def get_missing(
    app,
):
    installed_plugins = app.get_installed()
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
