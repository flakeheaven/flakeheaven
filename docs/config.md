# Config

FlakeHeaven can be configured in [pyproject.toml](https://www.python.org/dev/peps/pep-0518/). You can specify any Flake8 options and FlakeHeaven-specific parameters. Also,

Config resolving order (every next step overwrites previous one):

1. Flake8 legacy configs: `setup.cfg`, `tox.ini`, `.flake8`. Everything you've specified for Flake8 will work for FlakeHeaven. The only exception is list of checks, it must be explicitly specified in FlakeHeaven's config via `plugins`. By default, FlakeHeaven runs only [pyflakes](https://github.com/PyCQA/pyflakes) and [pycodestyle](https://pypi.org/project/pycodestyle/).
1. Modern and beautiful FlakeHeaven's config in [pyproject.toml](https://www.python.org/dev/peps/pep-0518/). Here you can configure everything for FlakeHeaven. Use it.
1. CLI options.

## Plugins

In `pyproject.toml` you can specify `[tool.flakeheaven.plugins]` table. It's a list of flake8 [plugins](plugins) and associated to them rules.

Key can be exact plugin name or wildcard template. For example `"flake8-commas"` or `"flake8-*"`. FlakeHeaven will choose the longest match for every plugin if possible. In the previous example, `flake8-commas` will match to the first pattern, `flake8-bandit` and `flake8-bugbear` to the second, and `pycodestyle` will not match to any pattern.

Value is a list of templates for error codes for this plugin. First symbol in every template must be `+` (include) or `-` (exclude). The latest matched pattern wins. For example, `["+*", "-F*", "-E30?", "-E401"]` means "Include everything except all checks that starts with `F`, check from `E301` to `E310`, and `E401`".

## Exceptions

Use `exceptions` section to specify special rules for particular paths:

```toml
[tool.flakeheaven.plugins]
pycodestyle = ["+*"]
pyflakes = ["+*"]

# match by prefix
[tool.flakeheaven.exceptions."tests/"]
pycodestyle = ["-F401"]     # disable a check
pyflakes = ["-*"]           # disable a plugin

[tool.flakeheaven.exceptions."tests/test_example.py"]
pyflakes = ["+*"]           # enable a plugin

# match by glob
[tool.flakeheaven.exceptions."**/test_*.py"]
pyflakes = ["-*"]
```

path can be either a path prefix (from the project root) or a [glob pattern](https://docs.python.org/3/library/fnmatch.html).

## Base

Option `base` allows to specify base config from which you want to inherit this one. It can be path to local config or remote URL. You can specify one path or list of paths as well. For example:

```toml
base = ["https://raw.githubusercontent.com/flakeheaven/flakeheaven/master/pyproject.toml", ".flakeheaven.toml"]
max_line_length = 90
```

In this example, FlakeHeaven will read remote config, local config (`.flakeheaven.toml`), and then current config. So, even if `max_line_length` is specified in some of base configs, it will be overwritten by `max_line_length = 90` from current config.

## Defaults

Most of default parameters are the same as in Flake8. However, some of them are different to make FlakeHeaven cool:

```toml
# make output beautiful
format='colored'
# 80 chars limit isn't enough in 21 century
max_line_length=90
```

## Additional settings

FlakeHeaven provides a few additional options that aren't supported by the original flake8. They can be specified as everything else, in config or as CLI flags.

+ `--baseline` -- path to [baseline](commands/baseline) file.
+ `--safe` -- suppress exceptions from plugins. In that case, the exception will be converted into `E902` error.

## Ignored options

FlakeHeaven doesn't support some flake8 option by design. Flake8 has a long history and over-complicated logic to enable and disable some checks. We make it simple.

+ `--extend-exclude` - use just `exclude`, modify it right in the config if you need.
+ `--per-file-ignores` - use `exceptions`.
+ `--statistics` - use `--format=stat` instead.
+ `--ignore` - use `plugins`.
+ `--extend-ignore` - use `plugins`.
+ `--select` - use `plugins`.
+ `--enable-extensions` - use `plugins`.

## Example

```toml
[tool.flakeheaven]
# optionally inherit from remote config (or local if you want)
base = "https://raw.githubusercontent.com/flakeheaven/flakeheaven/master/pyproject.toml"
# specify any flake8 options. For example, exclude "example.py":
exclude = ["example.py"]
# make output nice
format = "grouped"
# don't limit yourself
max_line_length = 120
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

# disable some checks for tests
[tool.flakeheaven.exceptions."tests/"]
pycodestyle = ["-F401"]     # disable a check
pyflakes = ["-*"]           # disable a plugin

# do not disable `pyflakes` for one file in tests
[tool.flakeheaven.exceptions."tests/test_example.py"]
pyflakes = ["+*"]           # enable a plugin
```

See [Flake8 documentation](http://flake8.pycqa.org/en/latest/user/configuration.html) to read more about Flake8-specific configuration.
