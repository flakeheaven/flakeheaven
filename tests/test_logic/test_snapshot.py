# built-in
import importlib
import os
import subprocess as sp
import time
from pathlib import Path
from typing import Generator

# external
import pytest

# project
import flakeheaven._logic._snapshot
from flakeheaven._logic._snapshot import CACHE_PATH, prepare_cache


@pytest.mark.parametrize(
    'value, threshold',
    [
        ('3600', 3600),
        ('864000', 864000),
        (None, 3600 * 24),
    ],
)
def test_prepare_cache_timeout_default(value, threshold, tmp_path, monkeypatch):
    """
    Test default and configured via environment variable cache timeout.

    A special value 'None' tests the (documented) default cache timeout.

    Invokes prepare_cache and checks that files, that files are removed
    according to their access time.

    Parameters
    ----------
    value : Optional[str]
        Environment variable value or None to remove the variable.
    threshold : int
        Cache timeout threshold.
    tmp_path : Path
        Temporary directory created for test invocation. Unique to the test.
    monkeypatch: Monkeypatch
        Monkeypatch fixture.
    """
    if value is not None:
        monkeypatch.setenv('FLAKEHEAVEN_CACHE_TIMEOUT', value)
    else:
        monkeypatch.delenv('FLAKEHEAVEN_CACHE_TIMEOUT', raising=False)

    importlib.reload(flakeheaven._logic._snapshot)

    before_names = ['f1.before', 'f2.before']
    after_names = ['f1.after', 'f2.after']

    for fname in before_names:
        fpath = tmp_path / fname
        fpath.touch()
        atime = time.time() - threshold - 10
        os.utime(fpath, times=(atime, atime))

    for fname in after_names:
        fpath = tmp_path / fname
        fpath.touch()
        atime = time.time() - threshold + 10
        os.utime(fpath, times=(atime, atime))

    flakeheaven._logic._snapshot.prepare_cache(path=tmp_path)

    for fname in before_names:
        assert not (tmp_path / fname).exists()

    for fname in after_names:
        assert (tmp_path / fname).exists()


PYPROJECT_TOML = """
[tool.flakeheaven]
format = "json"
max-line-length = 3

[tool.flakeheaven.plugins]
pycodestyle = ["+E501"]
"""

PY_CODE = """
a=0
'''e501'''

b=5
'''both errors here'''
"""


PathClass = type(CACHE_PATH)


class LiarPath(PathClass):
    def exists(self) -> bool:
        return False


class RemoverPath(PathClass):
    def iterdir(self) -> Generator[Path, None, None]:
        for path in super().iterdir():
            path.unlink()
            yield path


def test_prepare_cache(monkeypatch, tmp_path: Path):
    """
    Test to fix #123 by concurrently keeping/removing cache directories.
    """

    monkeypatch.chdir(tmp_path)

    # enforce toml config, code and preexisting cache
    cache_path = tmp_path / 'cache'
    (tmp_path / 'pyproject.toml').write_text(PYPROJECT_TOML)
    (tmp_path / 'testcode.py').write_text(PY_CODE)
    monkeypatch.setenv('FLAKEHEAVEN_CACHE_TIMEOUT', '0')
    monkeypatch.setenv('FLAKEHEAVEN_CACHE', str(cache_path))

    sp.run(['flakeheaven', 'lint', 'testcode.py'])

    importlib.reload(flakeheaven._logic._snapshot)

    prepare_cache(path=LiarPath(cache_path))
    prepare_cache(path=RemoverPath(cache_path))


def test_default_cache_dir(monkeypatch, tmp_path: Path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('FLAKEHEAVEN_CACHE_TIMEOUT', '0')

    expected_cache_path = tmp_path / '.flakeheaven_cache'

    (tmp_path / 'pyproject.toml').write_text(PYPROJECT_TOML)
    (tmp_path / 'testcode.py').write_text(PY_CODE)

    sp.run(['flakeheaven', 'lint', 'testcode.py'])

    p = Path(expected_cache_path).resolve()
    assert p.exists()
    assert len(list(p.glob('*.json'))) == 1
