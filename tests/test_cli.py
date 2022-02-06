# built-in
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from unittest.mock import Mock, patch

# external
import pytest
from flake8.utils import parse_unified_diff, stdin_get_value

# project
from flakeheaven._cli import main

# app
from .utils import chdir


def test_flake8heavened_file():
    """Baseline behavior, when an actual filename is passed."""
    cmd = [
        sys.executable,
        '-c',
        'import sys; from flakeheaven import flake8_entrypoint; sys.exit(flake8_entrypoint())',
        __file__,
    ]
    result = subprocess.run(cmd)
    assert result.returncode == 0


def test_flake8heavened_stdin():
    """Problematic behavior from issue #44, `-` is passed as filename, together with --stdin-display-name."""
    source_file = open(__file__, 'r')
    cmd = [
        sys.executable,
        '-c',
        'import sys; from flakeheaven import flake8_entrypoint; sys.exit(flake8_entrypoint())',
        '--stdin-display-name',
        __file__,
        # '-' is not an existing filename, so snapshot cannot create a hexdigest of its content
        # but otherwise it's fine for flake8 which knows to read stdin instead
        '-',
    ]
    result = subprocess.run(cmd, stdin=source_file)
    assert result.returncode == 0


@pytest.mark.parametrize('flag', [
    '--help',
    'help',
    'commands',
])
def test_help(flag, capsys):
    result = main([flag])
    assert result == (0, '')
    captured = capsys.readouterr()
    assert captured.err == ''

    for name in ('baseline', 'code', 'codes', 'lint', 'missed', 'plugins'):
        assert name in captured.out


def test_version(capsys):
    result = main(['--version'])
    assert result == (0, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    assert 'FlakeHeaven' in captured.out
    assert 'Flake8' in captured.out


def test_plugins(capsys):
    result = main(['plugins'])
    assert result == (0, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    assert 'NAME' in captured.out
    assert 'RULES' in captured.out


@patch('sys.argv', ['flakeheaven'])
def test_lint_help(capsys):
    result = main(['lint', '--help'])
    assert result == (0, '')
    captured = capsys.readouterr()
    assert captured.err == ''

    # flake8 options
    assert '-h, --help' in captured.out
    assert '--builtins' in captured.out
    assert '--isort-show-traceback' in captured.out

    # ignored flake8 options
    assert '--per-file-ignores' not in captured.out
    assert '--enable-extensions' not in captured.out

    # flakeheaven options
    assert '--baseline' in captured.out


@patch('sys.argv', ['flakeheaven'])
def test_exceptions(capsys, tmp_path: Path):
    text = """
    [tool.flakeheaven.plugins]
    pyflakes = ["+*"]

    [tool.flakeheaven.exceptions."tests/"]
    pyflakes = ["-F401"]
    """
    (tmp_path / 'pyproject.toml').write_text(dedent(text))
    (tmp_path / 'example.py').write_text('import sys\na')
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'tests' / 'test_example.py').write_text('import sys\na')
    with chdir(tmp_path):
        result = main(['lint', '--format', 'default'])
    assert result == (1, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    exp = """
    ./example.py:1:1: F401 'sys' imported but unused
    ./example.py:2:1: F821 undefined name 'a'
    ./tests/test_example.py:2:1: F821 undefined name 'a'
    """
    assert captured.out.strip() == dedent(exp).strip()


@patch('sys.argv', ['flakeheaven'])
@patch('sys.stdin', Mock())
def test_diff(capsys, tmp_path: Path):
    text = """
    [tool.flakeheaven.plugins]
    pyflakes = ["+*"]

    [tool.flakeheaven.exceptions."tests/"]
    pyflakes = ["-F401"]
    """
    (tmp_path / 'pyproject.toml').write_text(dedent(text))
    (tmp_path / 'example.py').write_text('import sys\na')
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'tests' / 'test_example.py').write_text('import sys\na')

    diff = """
        --- a/tests/test_example.py
        +++ b/tests/test_example.py
        @@ -1,1 +1,2 @@ class FlakeHeavenCheckersManager(Manager):
        - .
        + import sys
        + a

        --- a/example.py
        +++ b/example.py
        @@ -1,1 +1,2 @@ class FlakeHeavenCheckersManager(Manager):
        - .
        + import sys
        + a
    """
    diff = dedent(diff)
    exp = {'tests/test_example.py': {1, 2}, 'example.py': {1, 2}}
    assert dict(parse_unified_diff(diff)) == exp

    stdin_get_value.cache_clear()
    stream = BytesIO(diff.encode())
    with patch('sys.stdin.buffer', stream):
        with chdir(tmp_path):
            result = main(['lint', '--format', 'default', '--diff', 'example.py'])
    assert result == (1, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    exp = """
    example.py:1:1: F401 'sys' imported but unused
    example.py:2:1: F821 undefined name 'a'
    """
    assert captured.out.strip() == dedent(exp).strip()


@patch('sys.argv', ['flakeheaven'])
@patch('sys.stdin.buffer', BytesIO(b'import sys\na\n'))
@patch('sys.stdin', Mock())
def test_exceptions_stdin(capsys, tmp_path: Path):
    # write config
    text = """
    [tool.flakeheaven.plugins]
    pyflakes = ["+*"]

    [tool.flakeheaven.exceptions."example.py"]
    pyflakes = ["-F401"]
    """
    (tmp_path / 'pyproject.toml').write_text(dedent(text))

    # make fake `stdin` with source file content
    # code_path = tmp_path / 'example.py'
    # code_path.write_text('import sys\na')

    stdin_get_value.cache_clear()
    # call the command with passing matching `--stdin-display-name`
    cmd = ['lint', '--format', 'default', '--stdin-display-name', 'example.py', '--', '-']
    with chdir(tmp_path):
        # with code_path.open('r') as stream:
        result = main(cmd)

    assert result == (1, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out.strip() == "example.py:2:1: F821 undefined name 'a'"


@pytest.mark.parametrize('relative', [True, False])
@patch('sys.argv', ['flakeheaven'])
def test_baseline(capsys, tmp_path: Path, relative: bool):
    code_path = tmp_path / 'example.py'
    code_path.write_text('a\nb\n')
    with chdir(tmp_path):
        result = main([
            'baseline',
            str(code_path.relative_to(tmp_path)) if relative else str(code_path),
        ])
    assert result == (0, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    hashes = captured.out.strip().split()
    assert len(hashes) == 2

    line_path = tmp_path / 'baseline.txt'
    line_path.write_text(hashes[0])
    with chdir(tmp_path):
        args = [
            'lint',
            '--baseline', str(line_path),
            '--format', 'default',
            str(code_path),
        ]
        if relative:
            args.insert(-1, '--relative')
        result = main(args)
    assert result == (1, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out.strip() == "{}:2:1: F821 undefined name 'b'".format(str(code_path))


@patch('sys.argv', ['flakeheaven'])
def test_ignore_file_by_top_level_noqa(capsys, tmp_path: Path):
    (tmp_path / 'example1.py').write_text('import sys\n')
    (tmp_path / 'example2.py').write_text('# flake8: noqa\nimport sys\n')
    with chdir(tmp_path):
        result = main(['lint', '--format', 'default'])
    assert result == (1, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    exp = "./example1.py:1:1: F401 'sys' imported but unused"
    assert captured.out.strip() == exp


@patch('sys.argv', ['flakeheaven'])
def test_exclude_file(capsys, tmp_path: Path):
    (tmp_path / 'checked.py').write_text('import sys\n')
    (tmp_path / 'ignored').mkdir()
    (tmp_path / 'ignored' / 'first.py').write_text('import sys\n')
    (tmp_path / 'ignored' / 'second.py').write_text('invalid syntax!')
    with chdir(tmp_path):
        result = main(['lint', '--format', 'default', '--exclude', 'ignored'])
    assert result == (1, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    exp = """
    ./checked.py:1:1: F401 'sys' imported but unused
    """
    assert captured.out.strip() == dedent(exp).strip()


ISSUE_48_CHECKS = [
    """
    [[array]]
    name = "value"

""",  # pandas-vet 0.2.3
    """
    [[array]]
    name = "value"

    [[array]]
    name = "value"
    """,
]


@patch('sys.argv', ['flakeheaven'])
@pytest.mark.parametrize(
    'text',
    ISSUE_48_CHECKS,
)
def test_config_cli_arg_toml(capsys, tmp_path: Path, text):
    """Verify that the application handles the --config argv correctly.

    See https://github.com/flakeheaven/flakeheaven/issues/48
    """
    # write valid toml array but invalid configparser
    pyproject = tmp_path / 'pyproject.toml'
    pyproject.write_text(dedent(text))

    # make source file content
    dummy = tmp_path / 'dummy.py'
    dummy.write_text('# not empty\n')

    with chdir(tmp_path):
        # call the command with passing matching `--config`
        result = main(['lint', f'--config={pyproject.resolve()}', str(dummy.resolve())])

    assert result == (0, '')
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''
