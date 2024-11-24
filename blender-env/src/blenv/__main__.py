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
    except BlenvError as e:
        typer.echo(e)
        raise typer.Exit(code=1)


@app.command()
def blender(
        blend_file: Annotated[str, typer.Argument()] = BLENV_DEFAULT_CONFIG_FILENAME, 
        env_name: Annotated[str, typer.Argument()] = 'default', 
        debug: bool = False
    ):

    try:
        commands.blender(env_name, blend_file=blend_file, debug=debug)
    except BlenvError as e:
        typer.echo(e)
        raise typer.Exit(code=1)

@app.command()
def package(
        blend_file: Annotated[str, typer.Argument()] = BLENV_DEFAULT_CONFIG_FILENAME, 
    ):
    try:
        commands.package(blend_file)
    except BlenvError as e:
        typer.echo(e)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
