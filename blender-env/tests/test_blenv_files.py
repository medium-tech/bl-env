import pytest
from pydantic import ValidationError
from blenv import BlenvConf, BlenvConfMeta
from pathlib import Path
from conftest import basic_test, common_blenv_test

test_dir = Path(__file__).parent


def test_basic():
    conf:BlenvConf = BlenvConf.from_yaml_file(test_dir / '.blenv.basic.yaml')
    basic_test(conf)

def test_advanced():
    conf:BlenvConf = BlenvConf.from_yaml_file(test_dir / '.blenv.advanced.yaml')
    common_blenv_test(conf)

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
