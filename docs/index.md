# FlakeHeaven

It's a [Flake8](https://gitlab.com/pycqa/flake8) wrapper to make it cool.

+ [Lint md, rst, ipynb, and more](https://github.com/flakeheaven/flakeheaven/blob/main/docs/parsers.md).
+ [Shareable and remote configs](https://github.com/flakeheaven/flakeheaven/blob/main/docs/config.md#base).
+ [Legacy-friendly](https://github.com/flakeheaven/flakeheaven/blob/main/docs/commands/baseline.md): ability to get report only about new errors.
+ Caching for much better performance.
+ [Use only specified plugins](https://github.com/flakeheaven/flakeheaven/blob/main/docs/config.md#plugins), not everything installed.
+ [Make output beautiful](https://github.com/flakeheaven/flakeheaven/blob/main/docs/formatters.md).
+ [pyproject.toml](https://www.python.org/dev/peps/pep-0518/) support.
+ [Check that all required plugins are installed](https://github.com/flakeheaven/flakeheaven/blob/main/docs/commands/missed.md).
+ [Syntax highlighting in messages and code snippets](https://github.com/flakeheaven/flakeheaven/blob/masmainter/docs/formatters.md#colored-with-source-code).
+ [PyLint](https://github.com/PyCQA/pylint) integration.
+ [Powerful GitLab support](https://github.com/flakeheaven/flakeheaven/blob/main/docs/formatters.md#gitlab).
+ Codes management:
    + Manage codes per plugin.
    + Enable and disable plugins and codes by wildcard.
    + [Show codes for installed plugins](https://github.com/flakeheaven/flakeheaven/blob/main/docs/commands/plugins.md).
    + [Show all messages and codes for a plugin](https://github.com/flakeheaven/flakeheaven/blob/main/docs/commands/codes.md).
    + Allow codes intersection for different plugins.

![output example](../assets/grouped.png)

## Compatibility

FlakeHeaven supports all flake8 plugins, formatters, and configs. However, FlakeHeaven has it's own beautiful way to configure enabled plugins and codes. So, options like `--ignore` and `--select` unsupported. You can have flake8 and FlakeHeaven in one project if you want but enabled plugins should be explicitly specified.

```eval_rst
.. toctree::
    :maxdepth: 1
    :caption: Main Info

    config
    formatters
    plugins
    parsers
    ide
    troubleshooting

.. toctree::
    :maxdepth: 1
    :caption: Commands

    commands/lint
    commands/baseline
    commands/plugins
    commands/codes
    commands/code
    commands/missed
```
