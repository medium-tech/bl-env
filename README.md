# Blender Environment Manager

## Overview
Blenv aims to be a combination of `venv` and `pyenv` for [Blender](https://www.blender.org) python projects. It uses a `blenv.yaml` for configuring blender and python optionas and `.env` files to override the blender environment to reference your project. Install this into your global python and use its cli utility to create a new project that autogenerates both of these files.

The cli utility has a command to run blender using the env configuration, blender stdout is redirected to your terminal. If you `Ctl+C` in the terminal one time it will terminate the blender process and restart it, effectively reloading your application. If you use `Ctl+C` twice quickly it will terminate blender and then exit.

## Getting started
...

## Documentation

### cli
...


### blenv.yaml

The `blenv.yaml` file contains 1 or more blender environments. Each environment is a top level attribute which is the name of the environment when using the cli. Each environment contains the following options:




| blenv.yaml | blender cli arg | type | description | default |
| -- | -- | -- | -- | -- |
| blender | N/A | str | path to blender binary | /Applications/Blender.app/Contents/MacOS/Blender |
| env_file | N/A | str | which env file to use  | `.env` |
| env_inherit | N/A | bool | If `true` the blender process will have access to the system environment | `true` |
| env_override | N/A | bool | if `env_inherit` is `true` and this is `true` then the `.env` value will override system values | `true` |
| args | N/A | list[str] | `null` | launch blender with `blender` prepended to these arguments, ignores all other options that set a blender cli argument | `null` |
| background | `--background` | bool | If `true`, supply the blender arg to run blender in the background (headless / no ui) | `false` |
| autoexec | `--enable-autoexec` | bool | if `true`, supply the blender arg to enable automatic Python script execution | `false` |
| python | `--python` | str | Run the given Python script file | `null` |
| python_text | `--python-text` | str | Run the given Python script text block | `null` |
| python_expr | `--python-expr` | str | Run the given expression as a Python script | `null` |
| python_console | `--python-console` | bool | Run Blender with an interactive console. | `false` |
| python_exit_code | `--python-exit-code` | int | If non-negative supply this vallue to the `--python-exit-code` arg, which sets the exit-code in [0..255] to exit if a Python exception is raised (only for scripts executed from the command line), zero disables. | `-1` |
| python_use_system_env  | `--python-use-system-env`| bool | Allow Python to use system environment variables such as PYTHONPATH and the user site-packages directory. | `false` |
| addons | `--addons` | list[str] | Supply addons to enable in addition to default addons, the blender cli accepts a csv delimited string, but `blenv.yaml` takes a list of strings. | `[]` |

## Examples
...

## Roadmap
🔴 = not started

🟡 = started

🟢 = finished

* 🟢 detect blender path
    * 🟢 have list of common paths to search for
    * 🟢 start with defined paths for windows/osx and then fallback to `blender`

* 🟢 auto generate a `.env` file

* 🔴 create example app
    * 🔴 create unittests

* 🔴 add licence, make repo public, add to pypi

* 🔴 link / unlink / list links for app templates and addons

* 🔴 add conf option to open specific .blend file
* 🔴 add ability to override env's configured .blend file when using cli `run` command

* 🔴 create project template for addon
    * 🔴 emit build script
* 🔴 create project template for "app template"
    * 🔴 emit build script

* 🔴 add user global preferences with a defined default blender path
    * 🔴 when creating blenv.yaml reference user default blender
    * 🔴 enabling downloading arbitrary versions https://download.blender.org/release/
        * 🔴 store them in user folder (yaml files can reference by version instead of path)
    
    
    
## app template project layout
```
my_project/
    bl-env.conf
    .env
    app_templates/
        my_template/
            __init__.py
            startup.blend
            splash.png
            addons/
                my_addon/
                    __init__.py
                    ui.py
                    core.py
```

Build step will package the app template w/ addons and a standalone addon zip

## addon only project layout
```
my_project/
    bl-env.conf
    my_addon/
        __init__.py
        ui.py
        core.py
```
Build step will output a standalone addon zip

## combo layout
```
my_project/
    bl-env.conf
    dist/
        ...
    addons/
        my_addon/
            __init__.py
            ui.py
            core.py
            
    app_templates/
        my_template/
            startup.blend
            splash.png
            __init__.py
```

Add on can easily be packaged into standalone .zip but for app template the add on needs to be available to the template to install, by copying either sources or addon.zip into it