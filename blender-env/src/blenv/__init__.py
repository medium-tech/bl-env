#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import yaml
import zipfile

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
    'create_bl_env',
    'find_blender',
    'run_blender_from_env',
    'run_blender',
    'package_app',
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

    @classmethod
    def default(cls) -> 'BlenderEnv':
        return cls(blender=find_blender(), env_file='.env')
    
    @model_validator(mode='after')
    def check_defaults(self) -> Self:
        inherit_set = self.inherit is not None
        if self.blender is None and not inherit_set:
            raise ValueError('Must set either "blender" or "inherit" option on environment')
        
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


class BlenvConfMeta(BaseModel):
    version: Literal['1'] = '1'


class BlenderProjectConf(BaseModel):
    name: str = 'my-project'
    source: str = './my-project'


class BlenderPackageConf(BaseModel):
    output: str = './dist'


class BlenvConf(BaseModel):
    blenv: BlenvConfMeta = Field(default_factory=BlenvConfMeta)
    project: BlenderProjectConf = Field(default_factory=BlenderProjectConf)
    package: BlenderPackageConf = Field(default_factory=BlenderPackageConf)
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
            'package': self.package.model_dump(),
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

        return cls(blenv=BlenvConfMeta(**raw_data['blenv']), environments=enviros)
    
    @classmethod
    def from_yaml_file(cls, path: Path | str = BLENV_CONFIG_FILENAME) -> 'BlenvConf':
        with open(Path(path), 'r') as f:
            return cls.from_yaml(f.read())
        
#
# ops / commands
#


def create_bl_env():
    """interactively create a new bl-env.yaml file and .env file"""

    # create bl-env.yaml file #

    blenv = BlenvConf()
    
    project_name = input('Project name? [my-project] ')
    if project_name != '':
        blenv.project.name = project_name
        blenv.project.source = Path(os.path.join(os.getcwd(), project_name)).absolute().as_posix()

    try:
        blenv.dump_yaml_file()
        print(f'wrote: {BLENV_CONFIG_FILENAME}')

    except FileExistsError:
        if input(f'{BLENV_CONFIG_FILENAME} already exists. Overwrite? [y/n] ').lower() == 'y':
            blenv.dump_yaml_file(overwrite=True)
            print(f'wrote: {BLENV_CONFIG_FILENAME}')
        else:
            print(f'not overwriting: {BLENV_CONFIG_FILENAME}')

    # create .env file #

    default_env_file = EnvVariables()
    if project_name != '':
        default_env_file.BLENDER_USER_SCRIPTS = blenv.project.source
    try:
        default_env_file.dump_env_file()
        print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')
    except FileExistsError:
        if input(f'{BLENV_DEFAULT_ENV_FILENAME} already exists. Overwrite? [y/n] ').lower() == 'y':
            default_env_file.dump_env_file(overwrite=True)
            print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')
        else:
            print(f'not overwriting: {BLENV_DEFAULT_ENV_FILENAME}')


def find_blender(search_paths:list[str] = BLENDER_SEARCH_PATHS) -> str:
    """find blender executable in search paths, return first found path or 'blender' if none are found"""
    for path in search_paths:
        if os.path.exists(path):
            return path
    return 'blender'


def run_blender_from_env(env_name:str='default', blend_file:str=BLENV_CONFIG_FILENAME, debug:bool=False):
    """run blender with specified environment, or default environment if not specified"""
    bl_conf = BlenvConf.from_yaml_file(blend_file)
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

def package_app(source_dir:str, output:str) -> None:
    """write source files from source_dir into a zip file at output path"""

    # collect source files

    sources = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            path = os.path.join(root, file)
            if '__pycache__' in path:
                continue
            if path.endswith('.DS_Store'):
                continue
            if path.endswith('blend1'):
                continue
            sources.append(path)

    output:Path = Path(output)
    os.makedirs(output.parent, exist_ok=True)

    # zip sources

    with zipfile.ZipFile(output, 'w') as zipf:
        for source in sources:
            zipf.write(source, source)
            print(f' -> zipping: {source}')

    print(f'wrote: {output}')
