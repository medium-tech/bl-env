# Blender App Template Sample - Hello Donut

The famous blender animation tutorial turned into a hello world application for Blender App Templates!

Tested on Blender 3.6 with Python 3.10

# Use template 
You can use the app without downloading this repo and setting up a development environment.

Download zip file in `./dist` folder and install and run like a normal blender app template


# Dev usage
To setup a local dev environment and run from source:

```bash
git clone https://github.com/b-rad-c/bl-hello-donut.git
cd bl-hello-donut
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

An included shell script helps with setting up and running the code.

*Note that you may need to update variables in this script because this example app is setup for OSX with Blender3.6 and a python3.10 local venv*

```bash
# this links the code to your blender install's app template folder
./dev.sh link

# run the app template
./dev.sh start
```

You will need to quit and re-run the start command to load code changes.

To unlink the code from your blender install:
```bash
./dev.sh unlink
```

To package into a zip for distributing:
```bash
./dev.sh package
```

# Credit
I created the donut in this application by following Blender Guru's famous donut tutorial available at this link: https://www.youtube.com/playlist?list=PLjEaoINr3zgFX8ZsChQVQsuDSjEqdWMAD