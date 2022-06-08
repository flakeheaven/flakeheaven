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
MAX_DOC_LENGTH = 10

TOML_CONFIG_1 = f"""
[tool.flakeheaven]
format = "json"
# https://pycodestyle.pycqa.org/en/latest/intro.html#configuration
max-line-length ={MAX_LINE_LENGTH}
max_doc_length = {MAX_DOC_LENGTH}

[tool.flakeheaven.plugins]
pycodestyle = ["+E501", "+W505"]

"""

TOML_CONFIG_2 = f"""
[tool.flakeheaven]
format = "json"
# https://pycodestyle.pycqa.org/en/latest/intro.html#configuration
max_line_length ={MAX_LINE_LENGTH}
max-doc-length = {MAX_DOC_LENGTH}

[tool.flakeheaven.plugins]
pycodestyle = ["+E501", "+W505"]

"""

PY_CODE = """
a=0
'''e501'''

b=5
'''both errors here'''
"""

EXPECTED = json.dumps({
    3: {
        'E501': f'line too long (10 > {MAX_LINE_LENGTH} characters)',
    },
    6: {
        'E501': f'line too long (22 > {MAX_LINE_LENGTH} characters)',
        'W505': f'doc line too long (22 > {MAX_DOC_LENGTH} characters)',
    },
}, sort_keys=True)


@pytest.mark.parametrize(
    'initialized_app',
    [
        [TOML_CONFIG_1, PY_CODE],
        [TOML_CONFIG_2, PY_CODE],
    ],
    indirect=True,
)
def test_plugin_flags(initialized_app, capsys):

    assert initialized_app.options.max_line_length == MAX_LINE_LENGTH, '`max_line_length` incorrectly set from toml'
    assert initialized_app.options.max_doc_length == MAX_DOC_LENGTH, '`max_doc_length` incorrectly set from toml'

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
