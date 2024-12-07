#!/bin/bash

#
# init
#

APP_NAME='bl_music_player'
APP_VERSION='0.0.0'

BL_BIN='/Applications/Blender.app/Contents/MacOS/Blender'
BL_APP_TEMPLATE_FOLDER='/Users/brad/Library/Application Support/Blender/4.3/scripts/startup/bl_app_templates_user'

CURRENT_DIRECTORY=`pwd`
APP_SOURCE="${CURRENT_DIRECTORY}/${APP_NAME}"
SITE_PACKAGES="${CURRENT_DIRECTORY}/.venv/lib/python3.11/site-packages"
ADDON_PATH="${APP_SOURCE}/addons"
DIST_PATH="dist/${APP_NAME}-${APP_VERSION}.zip"


#
# run command
#

# ln -s /Users/brad/Code/BlenderProjects/bl-music-player/bl_music_player /Users/brad/Code/BlenderProjects/bl-music-player/.scripts/startup/bl_app_templates_user 
# ln -s /Users/brad/Code/BlenderProjects/bl-music-player/bl_music_player /Users/brad/Code/BlenderProjects/bl-music-player/.scripts/startup/bl_app_templates_system

clear; 
# BLENDER_USER_SCRIPTS="/Users/brad/Code/BlenderProjects/bl-env/examples/bl-hello-extension/.blenv/bl/scripts" "$BL_BIN" --addons "object_cursor_array";
BLENDER_USER_RESOURCES="/Users/brad/Code/BlenderProjects/bl-env/examples/bl-hello-extension/.blenv/bl" "$BL_BIN" --addons "object_cursor_array";