# built-in
from pathlib import Path
from unittest import mock

# external
import pytest

# project
from flakeheaven._patched._checkers import FlakeHeavenFileChecker


def test_nonexistent_file():
    """Verify that checking non-existent file results in an error."""
    plugin = {
        'plugin_name': 'flake8-example',
        'name': 'something',
        'plugin': FlakeHeavenFileChecker,
    }
    checks = dict(ast_plugins=[plugin], logical_line_plugins=[], physical_line_plugins=[])
    c = FlakeHeavenFileChecker(
        filename='foobar.py',
        checks=checks,
        options=None,
    )

    assert c.processor is None
    assert not c.should_process
    assert len(c.results) == 1
    error = c.results[0]
    assert error.error_code == 'E902'


def test_catches_exception_on_invalid_syntax(tmp_path):
    code_path = tmp_path / 'example.py'
    code_path.write_text('I exist!')
    plugin = {
        'name': 'failure',
        'plugin_name': 'failure',
        'parameters': dict(),
        'plugin': mock.MagicMock(side_effect=ValueError),
    }
    options = mock.MagicMock()
    options.safe = False
    checks = dict(ast_plugins=[plugin], logical_line_plugins=[], physical_line_plugins=[])
    fchecker = FlakeHeavenFileChecker(
        filename=str(code_path),
        checks=checks,
        options=options,
    )
    assert fchecker.should_process is True
    assert fchecker.processor is not None
    fchecker.run_checks()
    assert len(fchecker.results) == 1
    assert fchecker.results[0].error_code == 'E999'
    assert fchecker.results[0].text.startswith('SyntaxError: invalid syntax')


TOML_EXCEPTION_OVERRIDE = """
[tool.flakeheaven.plugins]
pycodestyle = ["+*"]

[tool.flakeheaven.exceptions."testcode.py"]
pycodestyle = ["-*", "+E401"]
"""

TOML_GLOB_DISABLE = """
[tool.flakeheaven.plugins]
pycodestyle = ["+*"]

[tool.flakeheaven.exceptions."testcode.py"]
pycodestyle = ["-*"]
"""


@pytest.fixture
def change_test_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    yield tmp_path


@pytest.mark.parametrize(
    'initialized_app',
    [
        [TOML_EXCEPTION_OVERRIDE, 'asdf=', str(False)],
        [TOML_GLOB_DISABLE, 'asdf=', str(True)],
    ],
    indirect=True,
)
def test_exception_disable(initialized_app):
    """Adding '-*' to exception disables a check partially/completely ."""
    code_py = Path(initialized_app.args[0]).name

    # Define wether any check should be performed using pytest
    # parametrize last arg (as seen from
    # flake8.main.application.Application).
    should_skip = {
        str(True): True,
        str(False): False,
    }[initialized_app.args.pop()]

    manager = initialized_app.file_checker_manager
    manager.make_checkers()
    checkers = manager.checkers

    if should_skip:
        # there should be no checkers activated
        assert len(checkers) == 0
        return

    # only a single checker should be active
    assert len(checkers) == 1
    checker = checkers[0]

    # if we partially removed pycodestyle, it should not be checked!
    for group in checker.checks.values():
        for plugin in group:
            plugin_name = plugin['plugin_name']
            if plugin['plugin_name'] != 'pycodestyle':
                continue
            assert manager._get_rules(plugin_name, filename='non-existent-file.py') == ['+*']
            rules = manager._get_rules(plugin_name, filename=code_py)
            assert rules == ['-*', '+E401']
    path, results, _ = checker.run_checks()
    assert Path(path).name == code_py
    assert len(results) == 1
    result = results[0]
    # it should raise syntaxerror on `asdf=`
    assert result.error_code == 'E999'
