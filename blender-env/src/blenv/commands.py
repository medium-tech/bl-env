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

            # create bl-env.yaml file #

            default_blenv_conf = BlenderEnvironmentConf()
            try:
                default_blenv_conf.dump_yaml_file(overwrite=overwrite)
                print(f'wrote: {BLENV_CONFIG_FILENAME}')
            except FileExistsError:
                if input(f'{BLENV_CONFIG_FILENAME} already exists. Overwrite? [y/n] ') == 'y':
                    default_blenv_conf.dump_yaml_file(overwrite=True)
                    print(f'wrote: {BLENV_CONFIG_FILENAME}')
                else:
                    print(f'not overwriting: {BLENV_CONFIG_FILENAME}')

            # create .env file #

            default_env_file = EnvVariables()
            try:
                default_env_file.dump_env_file(overwrite=overwrite)
                print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')
            except FileExistsError:
                if input(f'{BLENV_DEFAULT_ENV_FILENAME} already exists. Overwrite? [y/n] ') == 'y':
                    default_env_file.dump_env_file(overwrite=True)
                    print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')
                else:
                    print(f'not overwriting: {BLENV_DEFAULT_ENV_FILENAME}')

        case CLIConfCommand.test:
            BlenderEnvironmentConf.from_yaml_file()
            EnvVariables.from_env_file()

        case CLIConfCommand.show:
            print(BlenderEnvironmentConf.from_yaml_file().dump_yaml())
            print(EnvVariables.from_env_file().dump_env())
        
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

    sys_bl_args = [find_blender()] + (args if args else [])

    run_blender(sys_bl_args, env_file=env_file, env_inherit=env_inherit, env_override=env_override)
