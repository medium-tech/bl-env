import pytest
from pydantic import ValidationError
from blenv import BlenvConf
from conftest import basic_test


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
    basic_test(conf)


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
    

def test_blend_files():
    conf_str = """
    blenv:
        version: '1'
    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            file: my_project.blend
            env_file: .env
        test:
            inherit: default
            file: test.blend
    """
    conf:BlenvConf = BlenvConf.from_yaml(conf_str)

    default_env = conf.get('default')
    assert default_env.get_bl_run_args()[-1] == 'my_project.blend'
    assert default_env.get_bl_run_args(blender_file='different.blend')[-1] == 'different.blend'

    test_env = conf.get('test')
    assert test_env.get_bl_run_args()[-1] == 'test.blend'
    assert test_env.get_bl_run_args(blender_file='different.blend')[-1] == 'different.blend'