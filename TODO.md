# To do
🔴🟡🟢

* 🔴 change cli
    * 🔴 rename `blender` command to `run`
    * 🔴 new command `blender` = dynamically create env and blender exe but allow user to pass all following args
* 🔴 detect existing venv (or .venv)
    * 🔴 ask user during create if they want to use it or abort or ignore
    * 🔴 set `PTHONPATH` env var
        * ex: `PYTHONPATH=/path/to/.venv/lib/python3.11/site-packages`
