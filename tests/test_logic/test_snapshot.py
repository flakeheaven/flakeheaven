# built-in
import importlib
import os
import time

# external
import pytest

# project
import flakeheaven._logic._snapshot


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
