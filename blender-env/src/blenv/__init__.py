#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import yaml
import venv

from pathlib import Path
from typing import Literal
from pprint import pprint

from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


#
# init
#

__all__ = [
    'BLENDER_SEARCH_PATHS',
    'BLENV_CONFIG_FILENAME',
    'BLENV_DEFAULT_ENV_FILENAME',
    'BlenvError',
    'EnvVariables',
    'BlenderEnv',
    'BlenvConf',
    'setup_bl_env',
    'create_bl_env',
    'find_blender',
    'run_blender_from_env',
    'run_blender'
]

BLENDER_SEARCH_PATHS = [
    '/Applications/Blender.app/Contents/MacOS/Blender',
    '/usr/bin/blender',
    '/usr/local/bin/blender',
    'C:\\Program Files\\Blender Foundation\\Blender\\blender.exe'
]

BLENV_CONFIG_FILENAME = '.blenv.yaml'
BLENV_DEFAULT_ENV_FILENAME = '.env'

class BlenvError(Exception):
    pass

#
# conf models
#

class EnvVariables(BaseModel):

    BLENDER_USER_RESOURCES: str

    def dump_env(self) -> str:
        _env = ''
        for key, value in self.__dict__.items():
            _env += f'{key}={value}\n'
        return _env

    def dump_env_file(self, path: Path | str = BLENV_DEFAULT_ENV_FILENAME, overwrite:bool = False):
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f'File already exists: {path}')
        
        with open(path, 'w') as f:
            f.write(self.dump_env())

    @classmethod
    def from_env_file(cls, path: Path | str = BLENV_DEFAULT_ENV_FILENAME) -> 'EnvVariables':
        env = dotenv_values(dotenv_path=path)
        return cls(**env)


class BlenderEnv(BaseModel):
    inherit: str | None = None

    blender: str | None = None
    env_file: str | None = None

    env_inherit: bool = True
    env_override: bool = True

    file: str | None = None

    args: list[str] | None = None
    
    background: bool = False
    autoexec: bool = False

    app_template: str | None = None

    python: str | None = None 
    python_text: str | None = None
    python_expr: str | None = None
    python_console: bool = False

    python_exit_code: int = -1
    python_use_system_env: bool = False

    addons: list[str] | None = Field(default=None)

    blender_file: str | None = None

    @classmethod
    def default(cls) -> 'BlenderEnv':
        return cls(blender=find_blender(), env_file=BLENV_DEFAULT_ENV_FILENAME)
    
    @model_validator(mode='after')
    def check_defaults(self) -> Self:
        inherit_set = self.inherit is not None
        if self.blender is None and not inherit_set:
            raise ValueError('Must set either "blender" or "inherit" option on environment')
        
        return self

    def get_bl_run_args(self) -> list[str]:
        args = [self.blender]

        if self.args is not None:
            return args + self.args

        if self.background:
            args.append('--background')

        if self.autoexec:
            args.append('--enable-autoexec')

        if self.app_template:
            args.extend(['--app-template', self.app_template])

        if self.python:
            args.extend(['--python', self.python])

        if self.python_text:
            args.extend(['--python-text', self.python_text])

        if self.python_expr:
            args.extend(['--python-expr', self.python_expr])

        if self.python_console:
            args.append('--python-console')

        if self.python_exit_code >= 0:
            args.extend(['--python-exit-code', str(self.python_exit_code)])

        if self.python_use_system_env:
            args.append('--python-use-system-env')

        if self.addons:
            # blender is expecting a comma separated list of addons
            args.extend(['--addons', ','.join(self.addons)])

        if self.blender_file:
            args.append(self.blender_file)
            
        elif self.file:
            args.append(self.file)

        return args
    
    def get_bl_run_kwargs(self) -> dict[str, str]:
        return {
            'env_file': self.env_file,
            'env_inherit': self.env_inherit,
            'env_override': self.env_override,
        }


class BlenvConfMeta(BaseModel):
    version: Literal['1'] = '1'

class BlenderExtension(BaseModel):
    source: str

class BlenderProjectConf(BaseModel):
    app_templates: dict[str, BlenderExtension] = Field(default_factory=dict)
    addons: dict[str, BlenderExtension] = Field(default_factory=dict)

class BlenvConf(BaseModel):
    blenv: BlenvConfMeta = Field(default_factory=BlenvConfMeta)
    project: BlenderProjectConf = Field(default_factory=BlenderProjectConf)
    environments: dict[str, BlenderEnv] = Field(default_factory=lambda: {'default': BlenderEnv.default()})

    def get(self, env_name: str) -> BlenderEnv:
        try:
            return self.environments[env_name]
        except KeyError:
            raise BlenvError(f'No such environment: {env_name}')
        
    def get_default(self) -> BlenderEnv:
        return self.get('default')
    
    def dump_yaml(self, stream=None, full=False) -> str:
        enviros = {}
        for name, env in self.environments.items():
            BlenderEnv.model_validate(env)
            enviros[name] = env.model_dump(exclude_defaults=not full)

        data = {
            'blenv': self.blenv.model_dump(),
            'project': self.project.model_dump(),
            'environments': enviros
        }

        return yaml.safe_dump(data, stream=stream)
    
    def dump_yaml_file(self, path: Path|str = BLENV_CONFIG_FILENAME, overwrite:bool=False, full:bool=False) -> None:
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f'File already exists: {path}')
        
        with open(path, 'w') as f:
            self.dump_yaml(stream=f, full=full)
    
    @classmethod
    def from_yaml(cls, data: str) -> 'BlenvConf':
        raw_data = yaml.safe_load(data)

        child_enviros = {}
        enviros = {}

        # init base enviros
        for name, raw_env in raw_data['environments'].items():
            if raw_env.get('inherit') is not None:
                child_enviros[name] = raw_env   # will be loaded after all enviros are loaded so it can find parent
                continue

            enviros[name] = BlenderEnv(**raw_env)

        # init child enviros that inherit from bases
        for name, child_env in child_enviros.items():
            try:
                parent_env = enviros[child_env['inherit']]
            except KeyError as e:
                raise ValueError(f"'{name}' environment attempts inherit from undefined environment: {e}")
            
            enviros[name] = parent_env.model_copy(update=child_env, deep=True)
            BlenderEnv.model_validate(enviros[name])

        return cls(
            blenv=BlenvConfMeta(**raw_data['blenv']), 
            project=BlenderProjectConf(**raw_data['project']), 
            environments=enviros
        )
    
    @classmethod
    def from_yaml_file(cls, path: Path | str = BLENV_CONFIG_FILENAME) -> 'BlenvConf':
        with open(Path(path), 'r') as f:
            return cls.from_yaml(f.read())
        
#
# ops / commands
#

def setup_bl_env(blenv:BlenvConf):
    """setup blender environment in current directory"""

    blenv_directories = [
        '.blenv/bl/scripts/startup/bl_app_templates_user',
        '.blenv/bl/scripts/addons/modules',
        '.blenv/bl/extensions',
    ]

    for dir in blenv_directories:
        os.makedirs(dir, exist_ok=True)

    try:
        for app_template in blenv.project.app_templates.values():
            app_template_path = Path(app_template.source)
            src = app_template_path.absolute()
            dest = Path(f'.blenv/bl/scripts/startup/bl_app_templates_user/{app_template_path.name}').absolute()
            try:
                os.symlink(src, dest, target_is_directory=True)
            except FileExistsError:
                pass
            print(f'linked: {src} -> {dest}')
    except TypeError:
        pass
    
    try:
        for addon in blenv.project.addons.values():
            addon_path = Path(addon.source)
            src = addon_path.absolute()
            dest = Path(f'.blenv/bl/scripts/addons/modules/{addon_path.name}').absolute()
            try:
                os.symlink(src, dest, target_is_directory=True)
            except FileExistsError:
                pass
            print(f'linked: {src} -> {dest}')

    except TypeError:
        pass

def create_bl_env():
    """interactively create a new bl-env.yaml file and .env file"""

    # create bl-env.yaml file #

    blenv = BlenvConf()

    venv_path = f'.blenv/venv{sys.version_info.major}.{sys.version_info.minor}'
    if not os.path.exists(venv_path):
        if input(f'Create virtual environment {venv_path}? [y/n] ').lower() == 'y':
            venv.create(venv_path, with_pip=True, upgrade_deps=True)

    try:
        blenv.dump_yaml_file()
        print(f'wrote: {BLENV_CONFIG_FILENAME}')

    except FileExistsError:
        if input(f'{BLENV_CONFIG_FILENAME} already exists. Overwrite? [y/n] ').lower() == 'y':
            blenv.dump_yaml_file(overwrite=True)
            print(f'wrote: {BLENV_CONFIG_FILENAME}')
        else:
            blenv = BlenvConf.from_yaml_file()
            print(f'not overwriting: {BLENV_CONFIG_FILENAME}')

    setup_bl_env(blenv)

    # create .env file #

    env_file = EnvVariables(BLENDER_USER_RESOURCES=str(Path('.blenv/bl').absolute()))

    try:
        env_file.dump_env_file()
        print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')

    except FileExistsError:
        if input(f'{BLENV_DEFAULT_ENV_FILENAME} already exists. Overwrite? [y/n] ').lower() == 'y':
            env_file.dump_env_file(overwrite=True)
            print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')
        else:
            print(f'not overwriting: {BLENV_DEFAULT_ENV_FILENAME}')

def find_blender(search_paths:list[str] = BLENDER_SEARCH_PATHS) -> str:
    """find blender executable in search paths, return first found path or 'blender' if none are found"""
    for path in search_paths:
        if os.path.exists(path):
            return path
    return 'blender'

def run_blender_from_env(env_name:str='default', blenv_file:str=BLENV_CONFIG_FILENAME, debug:bool=False):
    """run blender with specified environment, or default environment if not specified"""
    bl_conf = BlenvConf.from_yaml_file(blenv_file)
    bl_env = bl_conf.get(env_name)

    popen_args = bl_env.get_bl_run_args()
    popen_kwargs = bl_env.get_bl_run_kwargs()

    if debug:
        pprint({'popen_args': popen_args, 'popen_kwargs': popen_kwargs})
    else:
        run_blender(popen_args, **popen_kwargs)

def run_blender(
        args: list[str], 
        env_file: str | None = None,
        env_inherit: bool = True,
        env_override: bool = True,
    ) -> int:
    """run blender with specified args and environment variables as subprocess,
    passing stdout and stderr to the parent process, returning the exit code.
    Use Ctl-C to terminate the blender process and restart to load code changes.
    Use Ctl-C twice to terminate blender and exit the parent process.
    """

    # init #

    popen_kwargs = {
        'bufsize': 0,
        'text': True,
        'stdout': sys.stdout,
        'stderr': sys.stderr,
    }

    if env_file is not None:
        if env_inherit:
            load_dotenv(dotenv_path=env_file, override=env_override)
        else:
            popen_kwargs['env'] = dotenv_values(dotenv_path=env_file)

    # run blender #

    while True:
        try:
            proc = subprocess.Popen(args, **popen_kwargs)
            while proc.poll() is None:
                pass

            break   # if poll is not None then the program exited, so break the loop

        except KeyboardInterrupt:
            proc.terminate()

            try:
                time.sleep(.25)
            except KeyboardInterrupt:
                break
    
    return proc.returncode
