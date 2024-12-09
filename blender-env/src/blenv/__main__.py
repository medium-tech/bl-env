#!/usr/bin/env python3
from blenv import create_bl_env, setup_bl_env, run_blender_from_env, BlenvConf, BlenvError

from typer import Typer, Argument, Exit, echo
from typing import Annotated


app = Typer(help='Blender Environment CLI')

@app.command()
def create():
    """
    Create a new blender environment in current directory
    """
    create_bl_env()

@app.command()
def setup():
    """
    Setup blender environment in current directory, this is run during create, but can be run separately.
    This is useful is a new app temnplate or addon is added to the environment and needs to be linked to the env.
    """
    setup_bl_env(BlenvConf.from_yaml_file())

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
