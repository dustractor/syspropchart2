import bpy
sysprop = bpy.context.window_manager.sysprop

sysprop.value = 'data.extrude,modifiers["Solidify"].thickness'
