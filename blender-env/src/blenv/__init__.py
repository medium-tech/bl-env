#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import yaml
import venv
import glob
import tomllib

from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel, Field

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

class BlenvError(Exception):
    pass

#
# constants
#

BLENDER_SEARCH_PATHS = [
    '/Applications/Blender.app/Contents/MacOS/Blender',
    '/usr/bin/blender',
    '/usr/local/bin/blender',
    'C:\\Program Files\\Blender Foundation\\Blender\\blender.exe'
]

VENV_SEARCH_PATHS = [
    '.blenv/venv',
    '.venv',
    'venv'
]

BLENV_CONFIG_FILENAME = '.blenv.yaml'
BLENV_DEFAULT_ENV_FILENAME = '.env'

#
# conf models
#

class EnvVariables(BaseModel):

    BLENDER_USER_RESOURCES: str
    PYTHONPATH: str

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

    blender: str | None = None
    blender_file: str | None = None

    app_template: str | None = None
    addons: list[str] | None = Field(default=None)

    env_file: str | None = None
    env_inherit: bool = True
    env_override: bool = True

    args: list[str] | None = None

    @classmethod
    def default(cls) -> 'BlenderEnv':
        return cls(blender=find_blender(), env_file=BLENV_DEFAULT_ENV_FILENAME)

    def get_bl_run_args(self, override_args: Optional[list[str]] = None) -> list[str]:
        args = [self.blender]

        if override_args is not None:
            return [self.blender] + override_args

        if self.args is not None:
            return args + self.args

        if self.app_template:
            args.extend(['--app-template', self.app_template])

        if self.addons:
            # blender expects a comma separated list of addons
            args.extend(['--addons', ','.join(self.addons)])

        if self.blender_file:
            args.append(self.blender_file)

        return args
    
    def get_bl_run_kwargs(self) -> dict[str, str]:
        return {
            'env_file': self.env_file,
            'env_inherit': self.env_inherit,
            'env_override': self.env_override,
        }


class BlenvConfMeta(BaseModel):
    version: Literal['1.1'] = '1.1'


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
        try:
            if raw_data['blenv']['version'] != '1.1':
                raise BlenvError(f'Unsupported blenv version: {raw_data["blenv"]["version"]}')
        except KeyError:
            raise BlenvError('Invalid blenv config, missing blenv.version key')
        
        return cls(**raw_data)
    
    @classmethod
    def from_yaml_file(cls, path: Path | str = BLENV_CONFIG_FILENAME) -> 'BlenvConf':
        with open(Path(path), 'r') as f:
            return cls.from_yaml(f.read())
        
#
# funcs and operations
#

def versions():
    pyproject_path = Path(__file__).parent.parent.parent / 'pyproject.toml'
    with open(pyproject_path, 'rb') as f:
        pyproject_data = tomllib.load(f)

    print(f'Python version: {sys.version}')
    print(f'Blenv version: {pyproject_data["project"]["version"]}')

    run_blender_from_env(override_args=['--background', '--python-expr', "import sys; print(f'Blender python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"])

# venv #

def find_venv() -> tuple[str, str] | None:
    """
    find existing python venv in current directory
    return tuple of (venv_path, site_packages_path) or None if not found
    """
    for search_path in VENV_SEARCH_PATHS:
        venv_pattern = f'./{search_path}*'
        print(f'looking for venv: {venv_pattern}')
        matches = glob.glob(venv_pattern)
        if matches:
            venv_path = matches[0]
            site_packages_path = find_site_packages(venv_path)
            if site_packages_path:
                return (venv_path, site_packages_path)
            else:
                raise BlenvError(f'Found venv at {venv_path} but could not find site-packages directory')

    return None

def find_site_packages(venv_path: str) -> str | None:
    """
    given a venv path, find the site-packages directory
    return path to site-packages or None if not found
    """
    site_packages_pattern = os.path.join(venv_path, 'lib', f'python*/site-packages')
    print(f'looking for site-packages: {site_packages_pattern}')
    site_packages = glob.glob(site_packages_pattern)
    if site_packages:
        return site_packages[0]
    return None

# blenv #

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

def create_bl_env(use_venv:str|None=None, yes:bool=False):
    """
    interactively create a new bl-env.yaml file and .env file
    :param use_venv: if provided, path to existing venv to use, otherwise will search for existing venv or create a new one
    :param yes: if True, skip all prompts and assume 'yes' to all questions
    """

    #
    # python venv
    #

    if use_venv:

        # use user specified venv #
        
        venv_path = use_venv

        if not os.path.exists(venv_path):
            raise BlenvError(f'Specified venv does not exist: {venv_path}')
        
        site_packages_path = find_site_packages(venv_path)
        if site_packages_path is None:
            raise BlenvError(f'Could not find site-packages in specified venv: {venv_path}')
        
    else:

        discovered_venv = find_venv()
        if discovered_venv is not None:

            # use discovered venv #

            venv_path, site_packages_path = discovered_venv
            print(f'found existing venv: {venv_path}')
            print(f'found site-packages: {site_packages_path}')
            
            if yes or input(f'Use this venv? [y/n] ').lower() == 'y':
                pass
        else:

            # no venv discovered, ask to create one #

            venv_path = f'.blenv/venv{sys.version_info.major}.{sys.version_info.minor}'
            
            if yes or input(f'Create virtual environment {venv_path}? [y/n] ').lower() == 'y':
                venv.create(venv_path, with_pip=True, upgrade_deps=True)
                site_packages_path = find_site_packages(venv_path)
                if site_packages_path is None:
                    raise BlenvError(f'Could not find site-packages in created venv: {venv_path}')
                
            else:
                print('Cannot continue without a venv. Aborting.')
                raise SystemExit(1)

    # create bl-env.yaml file #

    blenv = BlenvConf()

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

    env_file = EnvVariables(
        BLENDER_USER_RESOURCES=str(Path('.blenv/bl').absolute()),
        PYTHONPATH=str(Path(site_packages_path).absolute())
    )

    try:
        env_file.dump_env_file()
        print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')

    except FileExistsError:
        if input(f'{BLENV_DEFAULT_ENV_FILENAME} already exists. Overwrite? [y/n] ').lower() == 'y':
            env_file.dump_env_file(overwrite=True)
            print(f'wrote: {BLENV_DEFAULT_ENV_FILENAME}')
        else:
            print(f'not overwriting: {BLENV_DEFAULT_ENV_FILENAME}')

# blender #

def find_blender(search_paths:list[str] = BLENDER_SEARCH_PATHS) -> str:
    """find blender executable in search paths, return first found path or 'blender' if none are found"""
    for path in search_paths:
        if os.path.exists(path):
            return path
    return 'blender'

def run_blender_from_env(env_name:str='default', blenv_file:str=BLENV_CONFIG_FILENAME, debug:bool=False, override_args:Optional[list[str]] = None) -> dict | int:
    """
    run blender with specified environment, or default environment if not specified
    :param env_name: name of the environment to use, defaults to 'default'
    :param blenv_file: path to the blenv config file, defaults to '.blenv.yaml'
    :param debug: if True, print the args and kwargs that would be used to run blender instead of running it
    :param args: if provided, overrides the args provided to the blender executable (rest of env is the same)

    :return: if debug is True, returns a dict with 'popen_args' and 'popen_kwargs' that would be used to run blender
             if debug is False, returns the exit code of the blender process
    """
    bl_conf = BlenvConf.from_yaml_file(blenv_file)
    bl_env = bl_conf.get(env_name)

    popen_args = bl_env.get_bl_run_args(override_args)
    popen_kwargs = bl_env.get_bl_run_kwargs()

    if debug:
        return {'popen_args': popen_args, 'popen_kwargs': popen_kwargs}
    else:
        return run_blender(popen_args, **popen_kwargs)

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
