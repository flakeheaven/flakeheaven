# FlakeHeaven

[![License: MIT](https://img.shields.io/pypi/l/flakeheaven)](https://opensource.org/licenses/MIT)
[![python versions](https://img.shields.io/pypi/pyversions/flakeheaven)](https://pypi.org/project/flakeheaven/)

[![version](https://img.shields.io/pypi/v/flakeheaven)](https://pypi.org/project/flakeheaven/)
[![conda](https://anaconda.org/conda-forge/flakeheaven/badges/version.svg)](https://anaconda.org/conda-forge/flakeheaven)
[![Downloads](https://img.shields.io/pypi/dm/flakeheaven)](https://pypi.org/project/flakeheaven/)

[![CI](https://github.com/flakeheaven/flakeheaven/actions/workflows/ci.yaml/badge.svg)](https://github.com/flakeheaven/flakeheaven/actions/workflows/ci.yaml)
[![Docs](https://readthedocs.org/projects/flakeheaven/badge/?version=latest)](https://flakeheaven.readthedocs.io/en/latest/)


FlakeHeaven is a [Flake8](https://gitlab.com/pycqa/flake8) wrapper to make it cool.

This project is a fork of [FlakeHell](https://github.com/life4/flakehell). FlakeHell and other forks of it such as
flakehell/flakehell are [no longer maintained](https://github.com/flakehell/flakehell/issues/25) and do not work with Flake8 4.0.x.

FlakeHeaven works with Flake8 4.0.1 or greater. This fork will be [maintained by the community](https://github.com/flakeheaven/flakeheaven/discussions/1) that developed the existing forks.

+ [Lint md, rst, ipynb, and more](https://flakeheaven.readthedocs.io/en/latest/parsers.html).
+ [Shareable and remote configs](https://flakeheaven.readthedocs.io/en/latest/config.html#base).
+ [Legacy-friendly](https://flakeheaven.readthedocs.io/en/latest/commands/baseline.html): ability to get report only about new errors.
+ Caching for much better performance.
+ [Use only specified plugins](https://flakeheaven.readthedocs.io/en/latest/config.html#plugins), not everything installed.
+ [Make output beautiful](https://flakeheaven.readthedocs.io/en/latest//formatters.html).
+ [pyproject.toml](https://www.python.org/dev/peps/pep-0518/) support.
+ [Check that all required plugins are installed](https://flakeheaven.readthedocs.io/en/latest/commands/missed.html).
+ [Syntax highlighting in messages and code snippets](https://flakeheaven.readthedocs.io/en/latest/formatters.html#colored-with-source-code).
+ [PyLint](https://github.com/PyCQA/pylint) integration.
+ [Powerful GitLab support](https://flakeheaven.readthedocs.io/en/latest/formatters.html#gitlab).
+ Codes management:
    + Manage codes per plugin.
    + Enable and disable plugins and codes by wildcard.
    + [Show codes for installed plugins](https://flakeheaven.readthedocs.io/en/latest/commands/plugins.html).
    + [Show all messages and codes for a plugin](https://flakeheaven.readthedocs.io/en/latest/commands/codes.html).
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
base = "https://raw.githubusercontent.com/flakeheaven/flakeheaven/main/pyproject.toml"
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

Read [the documentation](https://flakeheaven.readthedocs.io/en/latest/) for more information.

## Contributing

Contributions are welcome! A few ideas what you can contribute:

+ Improve documentation.
+ Add more tests.
+ Improve performance.
+ Found a bug? Fix it!
+ Made an article about FlakeHeaven? Great! Let's add it into the `README.md`.
+ Don't have time to code? No worries! Just tell your friends and subscribers about the project. More users -> more contributors -> more cool features.

A convenient way to run tests is using [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer):

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry run pytest tests
```

Bug-tracker is disabled by-design to shift contributions from words to actions. Please, help us make the project better and don't stalk maintainers in social networks and on the street.

Thank you :heart:

![](./assets/flaky.png)

The FlakeHeaven mascot (Flaky) is created by [@illustrator.way](https://www.instagram.com/illustrator.way/) and licensed under the [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) license.
