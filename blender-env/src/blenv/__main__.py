#!/usr/bin/env python3
from blenv import *

from typer import Typer, Argument, Exit, echo
from typing import Annotated
from pathlib import Path
from enum import Enum


app = Typer(help='Blender Environment CLI')

class ConfCommands(str, Enum):
    create = 'create'
    test = 'test'
    show = 'show'

@app.command()
def conf(conf_command: Annotated[ConfCommands, Argument()] = ConfCommands.show):
    """
    Create, test or show the configuration of the current blender environment
    """
    try:
        if conf_command == ConfCommands.create:
            create_bl_env()

        elif conf_command == ConfCommands.test:
            BlenvConf.from_yaml_file()
            EnvVariables.from_env_file()

        elif conf_command == ConfCommands.show:
            print(BlenvConf.from_yaml_file().dump_yaml())
            print(EnvVariables.from_env_file().dump_env())
        
        else:
            raise ValueError(f'Unknown command: {conf_command}')
    except BlenvError as e:
        echo(e)
        raise Exit(code=1)

@app.command()
def blender(env_name: Annotated[str, Argument()] = 'default', debug: bool = False):
    """run blender with specified environment, or default environment if not specified"""

    try:
        run_blender_from_env(env_name, debug=debug)
    except BlenvError as e:
        echo(e)
        raise Exit(code=1)

if __name__ == "__main__":
    app()
