import pytest
from pydantic import ValidationError
from blenv import BlenvConf, BlenvConfMeta
from pathlib import Path

test_dir = Path(__file__).parent

def _common_blenv_test(conf: BlenvConf):
    assert isinstance(conf, BlenvConf)
    assert isinstance(conf.blenv, BlenvConfMeta)
    assert conf.blenv.version == '1'

def _test_basic(conf:BlenvConf):
    _common_blenv_test(conf)
    default_env = conf.get_default()

    assert len(conf.environments) == 1
    assert conf.get('default') == default_env
    assert default_env.inherit is None
    

def test_basic():
    conf:BlenvConf = BlenvConf.from_yaml_file(test_dir / '.blenv.basic.yaml')
    _test_basic(conf)

def test_basic_from_string():
    conf_str = """
    blenv:
        version: '1'
    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            env_file: .env
    """
    conf:BlenvConf = BlenvConf.from_yaml(conf_str)
    _test_basic(conf)

def test_missing_inerhit_property():
    conf_str = """
    blenv:
        version: '1'
    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            env_file: .env
        test:
            python: test.py
    """
    with pytest.raises(ValidationError, match='"blender" must be set if "inherit" is not set'):
        BlenvConf.from_yaml(conf_str)

def test_undefined_parent():
    conf_str = """
    blenv:
        version: '1'
    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            env_file: .env
        test:
            inherit: undefined-env
            python: test.py
    """
    with pytest.raises(ValueError, match="'test' environment attempts inherit from undefined environment: 'undefined-env'"):
        BlenvConf.from_yaml(conf_str)
    

def test_advanced():
    conf:BlenvConf = BlenvConf.from_yaml_file(test_dir / '.blenv.advanced.yaml')
    _common_blenv_test(conf)

    assert len(conf.environments) == 4

    default_env = conf.get_default()
    test_env = conf.get('test')
    
    assert conf.get('default') == default_env
    assert default_env.inherit is None
    assert test_env.inherit == 'default'

    # ensure each field is the same as parent except the 'python' field we overrode
    for name, child_value in test_env.model_dump().items():
        parent_value = getattr(default_env, name)
        if name in ['python', 'inherit']:
            assert child_value != parent_value, f'test_env.{name} ({child_value}) == default.{name} ({parent_value})'
        else:
            assert child_value == parent_value, f'test_env.{name} ({child_value}) != default.{name} ({parent_value})'
