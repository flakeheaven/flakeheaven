# **config**: show configuration

Show (pathched) flake8 application configuration after parsing and processing all options from cli and all configuration sources.

+ Use `--plugins-only` flag to show only the `app.options.config` namespace.
+ Use `-vvv` (vanilla flake8 verbose flag three times) to increase verbosity and show intermediate merges in the logger.
+ Use `--output-file` (vanilla flake8 config) to send logs and results to the specified file.
+ Use `--flake8-logs` to include vanilla flake8 logs while logging.


```console
$ flakeheaven config --plugins-only

{'pycodestyle': ['+*'], 'pyflakes': ['+*'], 'flake8-commas': ['+*'], 'flake8-quotes': ['+*'], 'pylint': ['+F*', '+E*', '-E0611', '-E1101', '-E0401', '-E1102', '-E1123']}
```
