# built-in
import collections.abc
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

# external
import toml
from flake8 import _EXTRA_VERBOSE, LOG as FLAKE8_LOG
from flake8.utils import normalize_paths


LOG = FLAKE8_LOG.getChild(__name__)


def read_config(*paths) -> Dict[str, Any]:
    config = dict()  # type: Dict[str, Any]
    for path in paths:
        if isinstance(path, Path):
            new_config = _read_local(path)
        elif path.startswith(('https://', 'http://')):
            new_config = _read_remote(path)
        elif Path(path).expanduser().exists():
            new_config = _read_local(Path(path).expanduser())
        else:
            new_config = _read_remote(path)
        LOG.log(_EXTRA_VERBOSE, 'CONFIG: incoming from `%s`:```%s```', path, new_config)
        config = _merge_configs(config, new_config)
        LOG.log(
            _EXTRA_VERBOSE, 'CONFIG: after merging from `%s`:```%s```', path, config,
        )
    return config


def _read_local(path: Path) -> Dict[str, Any]:
    with path.open('r') as stream:
        return _parse_config(stream.read())


def _read_remote(url: str) -> Dict[str, Any]:
    import urllib3  # isort: skip
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    return _parse_config(response.data.decode())


def _deep_update(old_dict, new_dict) -> Dict[str, Any]:
    for key, value in new_dict.items():
        if isinstance(value, collections.abc.Mapping):
            old_dict[key] = _deep_update(old_dict.get(key, {}), value)
        else:
            old_dict[key] = value
    return old_dict


def _merge_configs(*configs) -> Dict[str, Any]:
    config: Dict[str, Any] = defaultdict(dict)
    for subconfig in configs:
        _deep_update(config, subconfig)

    return dict(config)


def _parse_config(content: str) -> Dict[str, Any]:
    config = toml.loads(content).get('tool', {}).get('flakeheaven', {})
    config = dict(config)

    for section in ('plugins', 'exceptions'):
        if section in config:
            config[section] = dict(config[section])

    if 'base' in config:
        paths = config['base']
        if not isinstance(paths, list):
            paths = [paths]
        config = _merge_configs(read_config(*paths), config)

    if 'exclude' in config:
        config['exclude'] = normalize_paths(config['exclude'])

    return config
