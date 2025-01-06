# Blenv - Blender Environment Manager

🔴 warning - blenv is in beta - api or config may change 🔴

## Overview
Blenv is like `venv` for [Blender](https://docs.blender.org/api/current/index.html) python projects. It uses a `blenv.yaml` for configuring 1 or more blender/python environments for a given project. This project makes setting up a development environment for blender app templates and add ons simple.

The cli utility has a command to run blender using a selected environment. It will generate blender cli options and environment variables that point blender to your current project so it will load your addon or app template. You don't need to worry about making sure it's in the correct Blender folder. Plus, it adds hot-reloading to your development workflow. This speeds up your workflow and also keeps your blender installation clean of all your test applications. You can define multiple environments in one project test against different blender versions or run python commands.

## Example

The following `blenv.yaml` file defines 4 environments, 1 default which uses the system blender, 2 for running against specific blender versions, and another for running unittests.

    blenv:
        version: '1'
    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            env_file: .env

        v4.0:
            blender: /path/to/blender4.0
            env_file: .env

        v4.1:
            blender: /path/to/blender4.1
            env_file: .env

        test:
            inherit: default
            python: tests/test_file.py

## Getting started
Blenv can be installed in your system python or project's venv.

    pip install blenv

Create blenv for current project

    python -m blenv create 


## What is a blenv

A blenv is a `.blenv.yaml`, a `.env` file and also a `.blenv` directory that mimics blender's [directory layout](https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html). The `.blenv.yaml` file defines the project (addon vs. app template) and various environments or commands.  

The `.env` file only requires on variable, `BLENDER_USER_RESOURCES` which is used to override blender's directory layout so that the user and can test their plugin from their local project path instead of blender's default path. This enables more rapid development by skipping a build step, using custom scripts or manual file system linking. 

    BLENDER_USER_RESOURCES=/Users/john/bl-env-test-proj/.blenv/bl

## Documentation

See [DOCUMENTATION.md](./DOCUMENTATION.md) in the [repostiory](https://github.com/medium-tech/bl-env).