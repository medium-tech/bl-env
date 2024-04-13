# Blender Environment Manager


## To do list
    * add user global preferences with a defined system blender path
    * when creating bl-env.yaml reference user system blender
    * link / unlink / list links for app templates and addons
    * open download link in browser (or add this link to readme) https://download.blender.org/release/
    * create app templates
    * create readme doc
    * unittests
    
## app template project layout
```
my_project/
    bl-env.conf
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