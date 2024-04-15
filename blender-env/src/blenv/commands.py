#!/usr/bin/env python3
from typing import Optional
from enum import Enum
from blenv import *

__all__ = [
    'CLIConfCommand',
    'conf',
    'blender',
    'system',
]

class CLIConfCommand(str, Enum):
    create = 'create'
    test = 'test'
    show = 'show'


def conf(conf_command: CLIConfCommand = CLIConfCommand.show, overwrite: bool = False):
    match conf_command:

        case CLIConfCommand.create:
            default_bl_env = BlenderEnvironmentConf()
            try:
                default_bl_env.dump_yaml_file(overwrite=overwrite)
            except FileExistsError:
                if input('File already exists. Overwrite? [y/n] ') == 'y':
                    default_bl_env.dump_yaml_file(overwrite=True)
                else:
                    print('not overwriting')

        case CLIConfCommand.test:
            BlenderEnvironmentConf.from_yaml_file()

        case CLIConfCommand.show:
            _conf = BlenderEnvironmentConf.from_yaml_file()
            print(_conf.dump_yaml())
        
        case _:
            raise ValueError(f'Unknown command: {conf_command}')


def blender(env_name: str = 'default'):
    bl_conf = BlenderEnvironmentConf()
    bl_env = bl_conf.get(env_name)
    
    run_blender(bl_env.get_bl_run_args(), bl_env.get_bl_run_kwargs())


def system(
        args: Optional[list[str]] = None, 
        env_file:Optional[str] = None,
        env_inherit: bool = True,
        env_override: bool = True,
    ):

    sys_bl_args = [DEFAULT_BLENDER] + (args if args else [])

    run_blender(sys_bl_args, env_file=env_file, env_inherit=env_inherit, env_override=env_override)
