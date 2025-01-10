# Documentation

🔴 warning - blenv is in beta - api or config may change 🔴

[getting started](#getting-started)

[command line](#command-line-arguments)

[blenv.yaml](#blenvyaml)

## Getting started
Blenv can be installed in your system python or project's venv.

    pip install blenv

Create blenv for current project

    python -m blenv create 

This creates a blenv environment which is a `.blenv.yaml`, an `.env` file and also a `.blenv` directory that mimics blender's [directory layout](https://docs.blender.org/manual/en/latest/advanced/blender_directory_layout.html). The `.blenv.yaml` file defines the project (addons & app templates) and various environments or commands. The `create` command emits a placeholder `.blenv.yaml` config file that the developer will need to fill out to match their project's directory layout.

empty blenv.yaml file:

    blenv:
        version: '1'
    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            env_file: .env
    project:
        addons: {}
        app_templates: {}

In the following example we define our addon under `project.addons` and then attach it to our default environment under `environments.default.addons`

    blenv:
        version: '1'

    environments:
        default:
            blender: /Applications/Blender.app/Contents/MacOS/Blender
            env_file: .env
            addons:
            - object_cursor_array

    project:
        addons:
            object_cursor_array:
                source: 'src/object_cursor_array'

After configuring the project, run the following to set it up:

    python -m blenv setup

The `setup` command links the addon to the blender virtual environment. Now, the developer can run:

    python -m blenv blender

The `blender` command runs blender and loads the user's addon. This enables a quick and easy dev environment setup that would otherwise require custom scripts or using blender's directory structure which can get cluttered with all of the developer's other projects.

More technically, the `blender` command calls the binary listed in `blender` under the `default` environment, it will use the `.env` file which overrides the blender's directory structure to use the `.blenv` folder. The `setup` command created a link under `.blenv` where blender expects addons to be. The addon is passed to the cli's `addons` option so that it loads. An environment can define addons, app templates, python scripts, or configure many other blender cli options. A developer can setup multiple environments that use different blender versions, run tests, open a specific blend file and more to speed up development.

## command line arguments

**create**  - create a new blender environment in current directory

    python -m blenv create                                                                                                  

**setup** - setup blender environment in current directory, this is run during create, but can be run separately if a new app temnplate or addon is added to the environment and needs to be linked to the env. 
    
    python -m blenv setup     

**blender** - run blender with specified environment, or default environment if not specified. Blender's stdout is redirected to your terminal. If you `Ctl+C` in the terminal one time it will terminate the blender process and restart it, effectively reloading your application. If you use `Ctl+C` twice quickly it will terminate blender and then exit.

    python -m blenv blender [env_name] [--debug]

**env_name** - optional, `default` if not provided

**--debug** - optional, if provided, print the details of arguments that would be passed to the underlying `subprocess.Popen` constructor and exit.


## blenv.yaml

The `blenv.yaml` file contains the following fields:

| field name | type | description |
| -- | -- | -- |
| blenv | [blenv object](#blenv-config-object) | defines the version of the blenv file |
| project | [project object](#project-config-object) | defines the addons and/or app templates for this project |
| environments | object of [environment objects](#environment-config-object) | defines the environments and commands for this project, keys are environment names and values are [environment objects](#environment-config-object) |

### blenv config object
| field name | type | description |
| -- | -- | -- |
| version | str | `1` is the only version available |

### project config object
| field name | type | description |
| -- | -- | -- |
| addons | list of [extension config objects](#extension-config-object) | addons available to the project |
| app_templates | list of [extension config objects](#extension-config-object) | app templates availble to the project |

### extension config object
| field name | type | description |
| -- | -- | -- |
| source | `str` | the path for an addon or app template so it can be linked in the environment |

### environment config object
blenv environment objects can be found in the [blenv.yaml](#blenvyaml) files under `environments` key.


| environment field | blender cli arg | type | description | default |
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
