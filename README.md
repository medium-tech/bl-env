# Blenv - Blender Environment Manager

🔴 warning - blenv is in beta - api or config may change 🔴

## Overview
Blenv is like `venv` for [Blender](https://www.blender.org) python projects. It uses a `blenv.yaml` for configuring 1 or more blender/python environments for a given project. This project makes setting up a development environment for blender app templates and add ons simple.

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
...

## Documentation

### cli
...

When using the blenv cli to run blender, blender stdout is redirected to your terminal. If you `Ctl+C` in the terminal one time it will terminate the blender process and restart it, effectively reloading your application. If you use `Ctl+C` twice quickly it will terminate blender and then exit

...


### blenv.yaml

The `blenv.yaml` file contains 1 or more blender environments. Each environment is a top level attribute which is the name of the environment when using the cli. Each environment contains the following options:


| blenv.yaml | blender cli arg | type | description | default |
| -- | -- | -- | -- | -- |
| `inherit` | N/A | `str` / `null` | if not `null`, a `str` of the name of another blenv in this file, this blenv will be a duplicate of the parent with the remaining options overriding parent or default values | `null` |
| `blender` | N/A | `str` / `null` | path to blender binary, if `null` then `inherit` must define a parent that defines this value | The default value is system dependent, blenv will attempt to detect your installed blender by looking for common paths, if none are found a fallback of `blender` is used, if not defined your environment you will need to update this value manually to reference your blender executable |
| `env_file` | N/A | `str` / `null` | which env file to use, if `null` then `inherit` must define a parent that defines this value  | `.env` |
| `env_inherit` | N/A | `bool` | If `true` the blender process will have access to the system environment | `true` |
| `env_override` | N/A | `bool` | if `env_inherit` is `true` and this is `true` then the values from the `env_file` file will override system values | `true` |
| `args` | N/A | `list[str]` / `null` | launch blender with `blender` prepended to these arguments, ignores all other options that set a blender cli argument | `null` |
| `background` | `--background` | `bool` | If `true`, supply the blender arg to run blender in the background (headless / no ui) | `false` |
| `autoexec` | `--enable-autoexec` | `bool` | if `true`, supply the blender arg to enable automatic Python script execution | `false` |
| `app_template` | `--app-template` | `str` | if given supply app template cli option to blender | `null`
| `python` | `--python` | `str` | Run the given Python script file | `null` |
| `python_text` | `--python-text` | `str` | Run the given Python script text block | `null` |
| `python_expr` | `--python-expr` | `str` | Run the given expression as a Python script | `null` |
| `python_console` | `--python-console` | `bool` | Run Blender with an interactive console. | `false` |
| `python_exit_code` | `--python-exit-code` | `int` | If non-negative supply this vallue to the `--python-exit-code` arg, which sets the exit-code in [0..255] to exit if a Python exception is raised (only for scripts executed from the command line), zero disables. | `-1` |
| `python_use_system_env`  | `--python-use-system-env`| `bool` | Allow Python to use system environment variables such as PYTHONPATH and the user site-packages directory. | `false` |
| `addons` | `--addons` | `list[str]` / `null` | Supply addons to enable in addition to default addons, the blender cli accepts a csv delimited string, but `blenv.yaml` takes a list of strings. | `null` |
| `blender_file` | N/A | `str` | path to a `.blend` file to open | `null` |

## Roadmap
🔴 = not started

🟡 = started

🟢 = finished

* 🔴 unittests
* 🔴 finish README documentation
