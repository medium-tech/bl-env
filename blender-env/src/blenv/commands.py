#!/usr/bin/env python3
from blenv import *

from pprint import pprint
from enum import Enum
from pathlib import Path

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
            default_blenv_conf = BlenvConf()
            
            project_name = input('Project name?')
            if project_name != '':
                default_blenv_conf.package.name = project_name

            try:
                default_blenv_conf.dump_yaml_file(overwrite=overwrite)
                print(f'wrote: {BLENV_DEFAULT_CONFIG_FILENAME}')
            except FileExistsError:
                if input(f'{BLENV_DEFAULT_CONFIG_FILENAME} already exists. Overwrite? [y/n] ') == 'y':
                    default_blenv_conf.dump_yaml_file(overwrite=True)
                    print(f'wrote: {BLENV_DEFAULT_CONFIG_FILENAME}')
                else:
                    print(f'not overwriting: {BLENV_DEFAULT_CONFIG_FILENAME}')

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
            BlenvConf.from_yaml_file()
            EnvVariables.from_env_file()

        case CLIConfCommand.show:
            print(BlenvConf.from_yaml_file().dump_yaml())
            print(EnvVariables.from_env_file().dump_env())
        
        case _:
            raise ValueError(f'Unknown command: {conf_command}')


def blender(env_name:str='default', blend_file:str='bl-env.conf', debug:bool=False):
    bl_conf = BlenvConf.from_yaml_file(blend_file)
    bl_env = bl_conf.get(env_name)

    popen_args = bl_env.get_bl_run_args()
    popen_kwargs = bl_env.get_bl_run_kwargs()

    if debug:
        pprint({'popen_args': popen_args, 'popen_kwargs': popen_kwargs})
    else:
        run_blender(popen_args, **popen_kwargs)

def package(blend_file:str):
    bl_conf = BlenvConf.from_yaml_file(blend_file)

    zip_path = Path(bl_conf.package.output) / f'{bl_conf.package.name}.zip'
    
    package_app(bl_conf.package.source, zip_path)
