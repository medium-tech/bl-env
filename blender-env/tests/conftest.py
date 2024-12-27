from blenv import BlenvConf, BlenvConfMeta

__all__ = [
    'common_blenv_test',
    'basic_test'
]


def common_blenv_test(conf: BlenvConf):
    assert isinstance(conf, BlenvConf)
    assert isinstance(conf.blenv, BlenvConfMeta)
    assert conf.blenv.version == '1'

def basic_test(conf:BlenvConf):
    common_blenv_test(conf)
    default_env = conf.get_default()

    assert len(conf.environments) == 1
    assert conf.get('default') == default_env
    assert default_env.inherit is None
