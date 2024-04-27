#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import yaml

from pathlib import Path
from typing import Literal

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
    'find_blender',
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

#
# .env
#

class BlenvError(Exception):
    pass


class EnvVariables(BaseModel):

    BLENDER_USER_SCRIPTS: str = Field(default_factory=lambda: os.path.join(os.getcwd(), 'src'))

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
    
#
# blenv
#


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

    python: str | None = None 
    python_text: str | None = None
    python_expr: str | None = None
    python_console: bool = False

    python_exit_code: int = -1
    python_use_system_env: bool = False

    addons: list[str] | None = Field(default=None)

    @classmethod
    def default(cls) -> 'BlenderEnv':
        return cls(blender=find_blender(), env_file='.env')
    
    @model_validator(mode='after')
    def check_defaults(self) -> Self:
        inherit_set = self.inherit is not None
        if self.blender is None and not inherit_set:
            raise ValueError('"blender" must be set if "inherit" is not set')
        
        if self.env_file is None and not inherit_set:
            raise ValueError('"env_file" must be set if "inherit" is not set')
        
        return self

    def get_bl_run_args(self, blend_file:str|None = None) -> list[str]:
        args = [self.blender]

        if self.args is not None:
            return args + self.args

        if self.background:
            args.append('--background')

        if self.autoexec:
            args.append('--enable-autoexec')

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
            args.extend(['--addon', ','.join(self.addons)])

        if blend_file:
            args.append(blend_file)
            
        elif self.file:
            args.append(self.file)

        return args
    
    def get_bl_run_kwargs(self) -> dict[str, str]:
        return {
            'env_file': self.env_file,
            'env_inherit': self.env_inherit,
            'env_override': self.env_override,
        }

def _default_blender_env() -> BlenderEnv:
    return {'default': BlenderEnv.default()}


class BlenvConfMeta(BaseModel):
    version: Literal['1'] = '1'


class BlenvConf(BaseModel):
    blenv: BlenvConfMeta = Field(default_factory=BlenvConfMeta)
    environments: dict[str, BlenderEnv] = Field(default_factory=_default_blender_env)

    def get(self, key: str) -> BlenderEnv:
        try:
            return self.environments[key]
        except KeyError:
            raise BlenvError(f'No such environment: {key}')
        
    def get_default(self) -> BlenderEnv:
        return self.get('default')
    
    def get_names(self) -> list[str]:
        return list(self.environments.keys())
    
    def items(self) -> list[tuple[str, BlenderEnv]]:
        return list(self.environments.items())
    
    def dump_yaml(self, stream=None, full=False) -> str:
        enviros = {}
        for name, env in self.environments.items():
            BlenderEnv.model_validate(env)
            enviros[name] = env.model_dump(exclude_defaults=not full)

        data = {
            'blenv': self.blenv.model_dump(),
            'environments': enviros
        }
        return yaml.safe_dump(data, stream=stream)
    
    def dump_yaml_file(self, path: Path | str = BLENV_CONFIG_FILENAME, overwrite:bool = False) -> None:
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f'File already exists: {path}')
        
        with open(path, 'w') as f:
            self.dump_yaml(stream=f)
    
    @classmethod
    def from_yaml(cls, data: str) -> 'BlenderEnv':
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

        return cls(blenv=BlenvConfMeta(**raw_data['blenv']), environments=enviros)
    
    @classmethod
    def from_yaml_file(cls, path: Path | str = BLENV_CONFIG_FILENAME) -> 'BlenderEnv':
        with open(Path(path), 'r') as f:
            return cls.from_yaml(f.read())
        
#
# blender
#

def find_blender() -> str:
    for path in BLENDER_SEARCH_PATHS:
        if os.path.exists(path):
            return path
    return 'blender'


def run_blender(
        args: list[str], 
        # environment: None | dict[str, str] = None,
        env_file: str | None = None,
        env_inherit: bool = True,
        env_override: bool = True,
    ) -> None:

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
