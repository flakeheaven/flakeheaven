# external
import pytest

# project
from flakeheaven._logic import _config


def test_merge_config_merges_root_keys():
    merged_config = _config._merge_configs({'key_1': 'value_1'}, {'key_2': 'value_2'})

    assert merged_config == {'key_1': 'value_1', 'key_2': 'value_2'}


@pytest.mark.parametrize('subdict', ['plugins', 'exceptions'])
def test_merge_config_merges_subdicts(subdict):
    merged_config = _config._merge_configs({subdict: {'key_1': 'value_1'}}, {subdict: {'key_2': 'value_2'}})

    assert merged_config == {subdict: {'key_1': 'value_1', 'key_2': 'value_2'}}


def test_merge_config_empty_dicts():
    merged_config = _config._merge_configs({}, {})

    assert merged_config == {}
