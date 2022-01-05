# project
from flakeheaven._constants import DEFAULTS
from flakeheaven.parsers import PARSERS


def test_default_filename():
    assert {name[1:] for name in DEFAULTS['filename']} == set(PARSERS)
