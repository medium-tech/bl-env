# Blenv - Blender Environment Manager

🔴 warning - blenv is in beta - api or config may change 🔴

## Overview
Blenv is like `venv` for [Blender](https://docs.blender.org/api/current/index.html) python projects. It uses a `blenv.yaml` for configuring 1 or more blender/python environments for a given project. This project makes setting up a development environment for blender app templates and add ons simple.

The cli utility has a command to run blender using a selected environment. It will generate blender cli options and environment variables that point blender to your current project so it will load your addon or app template. You don't need to worry about making sure it's in the correct Blender folder. Plus, it adds hot-reloading to your development workflow. This speeds up your workflow and also keeps your blender installation clean of all your test applications. You can define multiple environments in one project test against different blender versions or run python commands.

## Documentation

See [DOCUMENTATION.md](./DOCUMENTATION.md) in the [repository](https://github.com/medium-tech/bl-env).