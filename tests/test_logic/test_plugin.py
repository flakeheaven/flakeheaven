# built-in
from pathlib import Path

# external
import pytest

# project
from flakeheaven._logic import get_exceptions


def test_get_exceptions(tmp_path: Path):
    exceptions = {
        'tests/': {'pyflakes': ['+*']},
        'test_*.py': {'pycodestyle': ['+*']},
    }

    # prefix match
    tests_path = tmp_path / 'tests'
    tests_path.mkdir()
    test_path = tests_path / 'test_example.py'
    test_path.touch()
    result = get_exceptions(path=test_path, exceptions=exceptions, root=tmp_path)
    assert result == {'pyflakes': ['+*']}

    # glob match
    base_test_path = tmp_path / 'test_example.py'
    base_test_path.touch()
    result = get_exceptions(path=base_test_path, exceptions=exceptions, root=tmp_path)
    assert result == {'pycodestyle': ['+*']}

    # no match
    source_path = tmp_path / 'example.py'
    source_path.touch()
    result = get_exceptions(path=source_path, exceptions=exceptions, root=tmp_path)
    assert result == {}


def test_get_exceptions_with_intersections(tmp_path: Path):
    exceptions = {
        'tests/': {'pyflakes': ['+*']},
        '**/test.py': {'pycodestyle': ['+*']},
    }

    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()

    test_file_path = tests_dir / 'test.py'
    test_file_path.touch()

    result = get_exceptions(path=test_file_path, exceptions=exceptions, root=tmp_path)
    assert result == {'pyflakes': ['+*'], 'pycodestyle': ['+*']}


@pytest.mark.parametrize(
    'first_match,better_match',
    (
        ('root/dir_1', 'root/dir_1/dir_1_1'),
        ('*/dir1/*', '*/dir_1/dir_1_1/*'),
        ('*/dir1/*', 'root/dir_1/dir_1_1'),
    ),
)
def test_exceptions_priority(tmp_path: Path, first_match, better_match):
    exceptions = {
        first_match: {'plugin_name': ['+FIRST_MATCH_RULE']},
        better_match: {'plugin_name': ['+BETTER_MATCH_RULE']},
    }

    test_file_path = _setup_filetree_for_priority_test(tmp_path)
    result = get_exceptions(path=test_file_path, exceptions=exceptions, root=tmp_path)

    assert result == {'plugin_name': ['+BETTER_MATCH_RULE']}


def _setup_filetree_for_priority_test(tmp_path: Path) -> Path:
    """
    root
    └─ dir_1
       └─ dir_1_1
          └─ file_1.py

    Returns: path for file_1.py
    """
    root_dir = tmp_path / 'root'
    root_dir.mkdir()

    dir_1 = root_dir / 'dir_1'
    dir_1.mkdir()

    dir_1_1 = dir_1 / 'dir_1_1'
    dir_1_1.mkdir()

    file_1_path = dir_1_1 / 'file_1.py'
    file_1_path.touch()

    return file_1_path
