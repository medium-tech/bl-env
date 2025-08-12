#!/usr/bin/env python3
import argparse
from pprint import pprint
from blenv import (
    BlenvConf, 
    create_bl_env, 
    setup_bl_env, 
    run_blender_from_env, 
    versions
)

def parser() -> argparse.ArgumentParser:
    """Create the argument parser for the blenv CLI."""
    parser = argparse.ArgumentParser()
    cmd_subparsers = parser.add_subparsers(help='subcommand help')

    version_command = cmd_subparsers.add_parser('version', help='Show version info')
    version_command.set_defaults(command='version')

    create_command = cmd_subparsers.add_parser('create', help='Create a new blender environment in current directory')
    create_command.set_defaults(command='create')
    create_command.add_argument('--venv', type=str, default=None, help='Path to the python venv to use (if not specified, a new venv will be created in .blenv/venv)')

    setup_command = cmd_subparsers.add_parser('setup', help='Setup blender environment in current directory')
    setup_command.set_defaults(command='setup')

    run_command = cmd_subparsers.add_parser('run', help='Run Blender with the specified environment')
    run_command.set_defaults(command='run')
    run_command.add_argument('env_name', type=str, default='default', help='Name of the environment to use', nargs='?')
    run_command.add_argument('--debug', action='store_true', help='Print debug info')
    run_command.add_argument('--', nargs='*', default=None, dest='args', help='Run the blender binary for this env with all args that follow')

    return parser

def parse_arguments(args: list[str]=None) -> argparse.Namespace:
    """
    parse arguments, if <args> is None, use sys.argv[1:]

    preprocess args because the argparse library will not allow arguments with hyphens following nargs='*' args, 
    but some of the blender args may have hyphens, so we split them off from sys.argv and set them directly on the cli namespace as a hack
    """

    if args is None:
        args_to_parse = sys.argv[1:]
    else:
        args_to_parse = args

    try:
        split_index = args_to_parse.index('--')
        args_for_parser = args_to_parse[:split_index]
        override_args = args_to_parse[split_index + 1:]
    except ValueError:
        args_for_parser = args_to_parse
        override_args = None

    parsed_args = parser().parse_args(args_for_parser)
    parsed_args.args = override_args
    return parsed_args

def run_parsed_args(args: argparse.Namespace):
    """Run the appropriate function based on parsed args returned from parser."""
    if hasattr(args, 'command'):
        if args.command == 'version':
            versions()

        elif args.command == 'create':
            create_bl_env()

        elif args.command == 'setup':
            setup_bl_env(BlenvConf.from_yaml_file())

        elif args.command == 'run':
            result = run_blender_from_env(env_name=args.env_name, debug=args.debug, args=args.args)
            if args.debug:
                pprint(result)

    else:
        parser.print_help()

if __name__ == "__main__":
    import sys

    args = parse_arguments()
    run_parsed_args(args)
