# **lint**: run flake8

Run patched flake8 against the code.

```bash
flakeheaven lint
```

This command accepts all the same arguments as Flake8.

Run linter against a file:

```bash
flakeheaven lint example.py
```

Run linter against a few dirs:

```bash
flakeheaven lint ./flakeheaven/ ./tests/
```

Show available arguments:

```bash
flakeheaven lint --help
```

Read [flake8 documentation](http://flake8.pycqa.org/en/latest/user/options.html) for list of available options.
