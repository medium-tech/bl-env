#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import yaml

from dotenv import load_dotenv, dotenv_values
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

#
# init
#

__all__ = [
    'BLENV_CONFIG_FILENAME',
    'BLENV_DEFAULT_ENV_FILENAME',
    'BlenderEnvError',
    'EnvVariables',
    'BlenderEnv',
    'BlenderEnvironmentConf',
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

class BlenderEnvError(BlenvError):
    pass

@dataclass
class EnvVariables:
    BLENDER_USER_SCRIPTS: str = field(default_factory=lambda: os.path.join(os.getcwd(), 'src'))

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

@dataclass
class BlenderEnv:
    blender: str = field(default_factory=lambda: find_blender())
    env_file: str = '.env'
    env_inherit: bool = True
    env_override: bool = True

    args: list[str] | None = field(default=None)
    
    background: bool = False
    autoexec: bool = False

    python: str | None = None 
    python_text: str | None = None
    python_expr: str | None = None
    python_console: bool = False

    python_exit_code: int = -1
    python_use_system_env: bool = False

    addons: list[str] = field(default_factory=list)

    def get_bl_run_args(self) -> list[str]:
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
            args.extend(['--addon', self.addons])

        args.extend(self.append_args)

        return args
    
    def get_bl_run_kwargs(self) -> dict[str, str]:
        return {
            'env_file': self.env_file,
            'env_inherit': self.env_inherit,
            'env_override': self.env_override,
        }

def _default_blender_env() -> BlenderEnv:
    return {'default': BlenderEnv()}

@dataclass
class BlenderEnvironmentConf:
    blenv: dict[str, str] = field(default_factory=lambda: {'version': '1'})
    environments: dict[str, BlenderEnv] = field(default_factory=_default_blender_env)

    def get(self, key: str) -> BlenderEnv:
        try:
            return self.environments[key]
        except KeyError:
            raise BlenderEnvError(f'No such environment: {key}')
        
    def get_default(self) -> BlenderEnv:
        return self.get('default')
    
    def get_names(self) -> list[str]:
        return list(self.environments.keys())
    
    def items(self) -> list[tuple[str, BlenderEnv]]:
        return list(self.environments.items())
    
    def dump_yaml(self, stream=None) -> str:
        data = {
            'blenv': self.blenv,
            'environments': {name: env.__dict__ for name, env in self.environments.items()}
        }
        return yaml.safe_dump(data, stream=stream, default_flow_style=False, sort_keys=False)
    
    def dump_yaml_file(self, path: Path | str = BLENV_CONFIG_FILENAME, overwrite:bool = False) -> None:
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f'File already exists: {path}')
        
        with open(path, 'w') as f:
            self.dump_yaml(stream=f)
    
    @classmethod
    def from_yaml(cls, data: str) -> 'BlenderEnv':
        envs = {name: BlenderEnv(**env) for name, env in yaml.safe_load(data).items()}
        return cls(environments=envs)
    
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
        env_file: Optional[str] = None,
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
