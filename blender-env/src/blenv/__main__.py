#!/usr/bin/env python3
import typer
from typing import Annotated, Optional
from blenv import *
from blenv import commands


app = typer.Typer(help='Blender Environment CLI')

@app.command()
def conf(
        conf_command: Annotated[commands.CLIConfCommand, typer.Argument()] = commands.CLIConfCommand.show,
        overwrite: bool = False
    ):
    try:
        commands.conf(conf_command, overwrite=overwrite)
    except BlenderEnvError as e:
        typer.echo(e)
        raise typer.Exit(code=1)

@app.command()
def blender(env_name: Annotated[str, typer.Argument()] = 'default'):
    try:
        commands.blender(env_name)
    except BlenderEnvError as e:
        typer.echo(e)
        raise typer.Exit(code=1)

@app.command()
def system(
        args: Annotated[Optional[list[str]], typer.Argument()] = None, 
        env_file:Optional[str] = None,
        env_inherit: bool = True,
        env_override: bool = True,
    ):

    try:
        commands.blender(args, env_file=env_file, env_inherit=env_inherit, env_override=env_override)
    except BlenderEnvError as e:
        typer.echo(e)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
