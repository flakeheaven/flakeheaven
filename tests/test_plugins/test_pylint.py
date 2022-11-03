# built-in
import json
from collections import defaultdict

# external
import pytest


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
