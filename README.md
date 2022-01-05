#FlakeHeaven

[![PyPI version](https://badge.fury.io/py/flakeheaven.svg)](https://badge.fury.io/py/flakeheaven)
[![Build Status](https://cloud.drone.io/api/badges/life4/flakeheaven/status.svg)](https://cloud.drone.io/life4/flakeheaven)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://readthedocs.org/projects/flakeheaven/badge/?version=latest)](https://github.com/mcarans/flakeheaven/blob/master/docs/)

It's a [Flake8](https://gitlab.com/pycqa/flake8) wrapper to make it cool.

+ [Lint md, rst, ipynb, and more](https://github.com/mcarans/flakeheaven/blob/master/docs/parsers.html).
+ [Shareable and remote configs](https://github.com/mcarans/flakeheaven/blob/master/docs/config.html#base).
+ [Legacy-friendly](https://github.com/mcarans/flakeheaven/blob/master/docs/commands/baseline.html): ability to get report only about new errors.
+ Caching for much better performance.
+ [Use only specified plugins](https://github.com/mcarans/flakeheaven/blob/master/docs/config.html#plugins), not everything installed.
+ [Make output beautiful](https://github.com/mcarans/flakeheaven/blob/master/docs/formatters.html).
+ [pyproject.toml](https://www.python.org/dev/peps/pep-0518/) support.
+ [Check that all required plugins are installed](https://github.com/mcarans/flakeheaven/blob/master/docs/commands/missed.html).
+ [Syntax highlighting in messages and code snippets](https://github.com/mcarans/flakeheaven/blob/master/docs/formatters.html#colored-with-source-code).
+ [PyLint](https://github.com/PyCQA/pylint) integration.
+ [Powerful GitLab support](https://github.com/mcarans/flakeheaven/blob/master/docs/formatters.html#gitlab).
+ Codes management:
    + Manage codes per plugin.
    + Enable and disable plugins and codes by wildcard.
    + [Show codes for installed plugins](https://github.com/mcarans/flakeheaven/blob/master/docs/commands/plugins.html).
    + [Show all messages and codes for a plugin](https://github.com/mcarans/flakeheaven/blob/master/docs/commands/codes.html).
    + Allow codes intersection for different plugins.

![output example](./assets/grouped.png)

## Compatibility

FlakeHeaven supports all flake8 plugins, formatters, and configs. However, FlakeHeaven has it's own beautiful way to configure enabled plugins and codes. So, options like `--ignore` and `--select` unsupported. You can have flake8 and FlakeHeaven in one project if you want but enabled plugins should be explicitly specified.

## Installation

```bash
python3 -m pip install --user flakeheaven
```

## Usage

First of all, let's create `pyproject.toml` config:

```toml
[tool.flakeheaven]
# optionally inherit from remote config (or local if you want)
base = "https://raw.githubusercontent.com/life4/flakeheaven/master/pyproject.toml"
# specify any flake8 options. For example, exclude "example.py":
exclude = ["example.py"]
# make output nice
format = "grouped"
# 80 chars aren't enough in 21 century
max_line_length = 90
# show line of source code in output
show_source = true

# list of plugins and rules for them
[tool.flakeheaven.plugins]
# include everything in pyflakes except F401
pyflakes = ["+*", "-F401"]
# enable only codes from S100 to S199
flake8-bandit = ["-*", "+S1??"]
# enable everything that starts from `flake8-`
"flake8-*" = ["+*"]
# explicitly disable plugin
flake8-docstrings = ["-*"]
```

Show plugins that aren't installed yet:

```bash
flakeheaven missed
```

Show installed plugins, used plugins, specified rules, codes prefixes:

```bash
flakeheaven plugins
```

![plugins command output](./assets/plugins.png)

Show codes and messages for a specific plugin:

```bash
flakeheaven codes pyflakes
```

![codes command output](./assets/codes.png)

Run flake8 against the code:

```bash
flakeheaven lint
```

This command accepts all the same arguments as Flake8.

Read [github.com/mcarans/flakeheaven/blob/master/docs](https://github.com/mcarans/flakeheaven/blob/master/docs/) for more information.

## Contributing

Contributions are welcome! A few ideas what you can contribute:

+ Improve documentation.
+ Add more tests.
+ Improve performance.
+ Found a bug? Fix it!
+ Made an article about FlakeHeaven? Great! Let's add it into the `README.md`.
+ Don't have time to code? No worries! Just tell your friends and subscribers about the project. More users -> more contributors -> more cool features.

A convenient way to run tests is using [DepHell](https://github.com/dephell/dephell):

```bash
curl -L dephell.org/install | python3
dephell venv create --env=pytest
dephell deps install --env=pytest
dephell venv run --env=pytest
```

Bug-tracker is disabled by-design to shift contributions from words to actions. Please, help us make the project better and don't stalk maintainers in social networks and on the street.

Thank you :heart:

![](./assets/flaky.png)

The FlakeHeaven mascot (Flaky) is created by [@illustrator.way](https://www.instagram.com/illustrator.way/) and licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) license.
