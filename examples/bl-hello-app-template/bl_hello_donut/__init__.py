# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.app.handlers import persistent
from pathlib import Path


#
# app startup
#


@persistent
def init_app(_):
    print('init_app()')
    context = bpy.context
    context.preferences.use_preferences_save = False

    # load background image
    image_path = Path(__file__).parent / 'donut.exr'
    image = bpy.data.images.load(image_path.as_posix(), check_existing=True)

    # find and configure image editor
    for area in context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            area.spaces.active.image = image

            for region in area.regions:

                if region.type == 'WINDOW':
                    img_context = {
                        'area': area,
                        'region': region,
                        'screen': area.id_data
                    }

                    with bpy.context.temp_override(**img_context):
                        bpy.ops.image.view_all(fit_view=True)
                        bpy.ops.image.view_zoom_ratio(ratio=1.0)
                        bpy.ops.screen.header_toggle_menus()
                        bpy.ops.screen.screen_full_area(use_hide_panels=True)


#
# register
#


load_post_handlers = [init_app]


def register():
    print('Template Register', __file__)

    for handler in load_post_handlers:
        bpy.app.handlers.load_post.append(handler)
 


def unregister():
    print('Template Unregister', __file__)

    for handler in reversed(load_post_handlers):
        bpy.app.handlers.load_post.remove(handler)
