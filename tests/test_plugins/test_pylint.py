# built-in
from collections import defaultdict
import json

# external
import pytest

# app
from flakeheaven._constants import NAME, VERSION
from flakeheaven._patched import FlakeHeavenApplication


@pytest.fixture
def initialized_app(request, tmp_path):
    toml_config, py_code = request.param

    toml_config_file = tmp_path / 'test_config.toml'
    toml_config_file.write_text(toml_config)

    python_lintee = tmp_path / 'code.py'
    python_lintee.write_text(py_code)

    app = FlakeHeavenApplication(program=NAME, version=VERSION)
    app.initialize([f'--config={toml_config_file}', str(python_lintee)])

    yield app


MAX_LINE_LENGTH = 4

TOML_CONFIG = f"""
[tool.flakeheaven]
format = "json"
max-line-length = {MAX_LINE_LENGTH}

[tool.flakeheaven.plugins]
pylint = ["+C0301"]

"""


PY_CODE = """
a=0
'''e501'''

b=5
'''both errors here'''
"""

EXPECTED = json.dumps({
    3: {
        'C0301': f'Line too long (10/{MAX_LINE_LENGTH}) (line-too-long)',
    },
    6: {
        'C0301': f'Line too long (22/{MAX_LINE_LENGTH}) (line-too-long)',
    },
}, sort_keys=True)


@pytest.mark.parametrize(
    'initialized_app',
    [
        [TOML_CONFIG, PY_CODE],
    ],
    indirect=True,
)
def test_plugin_flags(initialized_app, capsys):

    assert initialized_app.options.max_line_length == MAX_LINE_LENGTH, '`max_line_length` incorrectly set from toml'

    initialized_app.run_checks()
    out0 = capsys.readouterr().out
    initialized_app.report()
    captured = capsys.readouterr().out.replace(out0, '')

    found = defaultdict(dict)
    for c in captured.splitlines():
        report = json.loads(c)
        found[report['line']][report['code']] = report['description']

    found_json = json.dumps(found, sort_keys=True)
    assert found_json == EXPECTED, f'found:`{found_json}` but expected:`{EXPECTED}`'
