# external
import pytest

# project
from flakeheaven._constants import NAME, VERSION
from flakeheaven._patched import FlakeHeavenApplication


@pytest.fixture
def initialized_app(request, tmp_path, monkeypatch):
    toml_config, py_code, *init_args = request.param

    config_name = 'test_config.toml'
    code_name = 'testcode.py'
    with monkeypatch.context() as m:
        m.chdir(tmp_path)
        toml_config_file = tmp_path / config_name
        toml_config_file.write_text(toml_config)

        python_lintee = tmp_path / code_name
        python_lintee.write_text(py_code)

        app = FlakeHeavenApplication(program=NAME, version=VERSION)
        app.initialize([f'--config={config_name}', code_name, *init_args])
        yield app
