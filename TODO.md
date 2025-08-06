# To do
🔴🟡🟢

* 🟢 change cli
    * 🟢 rename `blender` command to `run`
    * 🟢 add args to `run` override args provided to blender exe
* 🔴 detect existing venv (or .venv)
    * 🔴 ask user during create if they want to use it or abort or ignore
    * 🔴 set `PTHONPATH` env var
        * ex: `PYTHONPATH=/path/to/.venv/lib/python3.11/site-packages`
* 🟢 remove typer dependency, rewrite w `argparse`
* 🟡 tests
    * 🟢 cli
    * 🔴 create / setup env
    * 🔴 run blender
* 🔴 version command that prints versions of python, blenv, .blenv.yaml file, blender exe, and blender's python version
    * 🔴 emit warning if python and blender python's version don't match