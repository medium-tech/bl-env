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

if __name__ == "__main__":

    #
    # define arg parser
    #

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

    #
    # parse and run args
    #

    args = parser.parse_args()

    if hasattr(args, 'command'):
        if args.command == 'version':
            versions()

        elif args.command == 'create':
            create_bl_env()

        elif args.command == 'setup':
            setup_bl_env(BlenvConf.from_yaml_file())

        elif args.command == 'run':
            result = run_blender_from_env(env_name=args.env_name, debug=args.debug)
            if args.debug:
                pprint(result)

    else:
        parser.print_help()