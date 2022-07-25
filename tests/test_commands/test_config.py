# built-in
from pathlib import Path
from shlex import split
import subprocess as sp
from typing import Optional

# external
import pytest

# app
from flakeheaven.commands._config import get_config

HELP = """\
usage: flakeheaven [-h] [--plugins-only] [--flake8-logs] [-v]
                   [--output-file OUTPUT_FILE]

Show flake8 configuration after flakeheaven consolidation.

optional arguments:
  -h, --help            show this help message and exit
  --plugins-only        If set, show only the plugins section of the config
  --flake8-logs         If set, also include flake8 logs
  -v, --verbose         Print more information about what is happening in
                        flake8. This option is repeatable and will increase
                        verbosity each time it is repeated.
  --output-file OUTPUT_FILE
                        Redirect report to a file.
"""


def run_cmd(
    args: str,
    *,
    stdout: Optional[str],
    stderr: Optional[str],
    returncode: int = 0,
    **kw,
) -> sp.CompletedProcess:
    result = sp.run(split(args), stdout=sp.PIPE, stderr=sp.PIPE, text=True, **kw)
    assert result.returncode == returncode

    if stderr is not None:
        assert result.stderr.strip() == stderr.strip()

    if stdout is not None:
        assert result.stdout.strip() == stdout.strip()

    return result


def test_config_help() -> None:
    run_cmd('flakeheaven config --help', stdout=HELP, stderr='')


def check_plugins(args, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.chdir(tmp_path)
    config, *_ = get_config([args])
    return config


def test_plugins_only_no(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    config = check_plugins('', tmp_path, monkeypatch)
    assert 'plugins' in config
    assert 'pyflakes' not in config


def test_plugins_only_yes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = check_plugins('--plugins-only', tmp_path, monkeypatch)
    assert 'plugins' not in config
    assert 'pyflakes' in config


def output_file_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    args: str = '',
) -> str:
    monkeypatch.chdir(tmp_path)
    logfile = tmp_path / 'config.log'
    run_cmd(f'flakeheaven config --output-file={logfile} {args}', stdout='', stderr='')
    console_output = logfile.read_text()
    assert f"'output_file': '{logfile}'" in console_output
    return console_output


def test_output_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    return output_file_helper(tmp_path, monkeypatch)


def test_verbose(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    console_output = output_file_helper(tmp_path, monkeypatch, '-vvv')
    assert 'after flakeheaven defaults' in console_output
    assert 'flake8.plugins.manager' not in console_output


def test_verbose_and_flake8(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    console_output = output_file_helper(tmp_path, monkeypatch, '-vvv --flake8-logs')
    assert 'after flakeheaven defaults' in console_output
    assert 'flake8.plugins.manager' in console_output
