# To do
🔴🟡🟢

* 🟢 change cli
    * 🟢 rename `blender` command to `run`
    * 🟢 add args to `run` override args provided to blender exe
* 🟢 detect existing venv (or .venv)
    * 🟢 ask user during create if they want to use it or abort or ignore
    * 🟢 set `PTHONPATH` env var
* 🟢 remove typer dependency, rewrite w `argparse`
* 🟢 tests
    * 🟢 cli
    * 🟢 create / setup env
    * 🟢 run blender
* 🟢 version command that prints versions of python, blenv, .blenv.yaml file, blender exe, and blender's python version
* 🟢 pypi does not have the readme as the project description
    * likely because the pyproject.toml file is referencing the file with the wrong path, the build system is unable to access files in a parent directory, so the `blender-env` folder should be removed and the project moved up a level so it can reference the readme correctly
* 🔴 emit warning if python and blender python's version don't match
    * 🔴 also emit warning when setting up blenv if mismatch is detected, ask for user confirmation to continue/abort
* 🔴 remove pydantic dependency (convert to dataclasses)
