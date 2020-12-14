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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
        "name": "System Property Chart 2",
        "description":"Rework of the built-in version which allows for "
        "indexed and keyed property access in addition to named "
        " attribute access.",
        "author":"dustractor@gmail.com",
        "version":(1,2),
        "blender":(2,80,0),
        "location":"3d Viewport -> UI -> Chart",
        "warning":"",
        "wiki_url":"",
        "tracker_url":"",
        "category": "System"
        }
from bpy.types import (
    Panel,Operator,bpy_prop_array,Object,Menu,PropertyGroup,WindowManager
)
from bpy.utils import (
    register_class,unregister_class,preset_paths,user_resource
)
from bpy.props import (
    StringProperty,PointerProperty
)
from pathlib import Path
from re import match
from bl_operators.presets import AddPresetBase
from bl_ui.utils import PresetPanel
from mathutils import Vector,Color,Euler
from shutil import copy2

def propexpr(obj,expr):
    if "." in expr:
        head,dot,rest = expr.partition(".")
        indexed = match(r"(\w*)\[(\d*)\]$",head)
        keyed = match(r"(\w*)\[[\"'](.*)[\"']\]$",head)
        if indexed:
            obj = getattr(obj,indexed.group(1)).__getitem__(int(indexed.group(2)))
        elif keyed:
            obj = getattr(obj,keyed.group(1)).get(keyed.group(2))
        else:
            obj = getattr(obj,head)
        return propexpr(obj,rest)
    return obj,expr

def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r


@_
class SYSPROP_OT_sysprop_interp(Operator):
    bl_idname = "sysprop.interp"
    bl_label = "Interpolate"
    bl_options = {"INTERNAL"}
    expr: StringProperty(default="")
    @classmethod
    def poll(self,context):
        return len(context.selected_objects) > 2
    def execute(self,context):
        expr = self.expr
        obs = list(context.selected_objects)
        tot = len(obs)-1
        inc = 1/tot
        first,last = obs[0],obs[-1]
        obj1,prop1 = propexpr(first,expr)
        obj2,prop2 = propexpr(last,expr)
        attr1 = getattr(obj1,prop1)
        attr2 = getattr(obj2,prop2)
        print("type(attr1):",type(attr1))
        if isinstance(attr1,Vector):
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = attr1.lerp(attr2,fac)
        elif isinstance(attr1,Euler):
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                qa = attr1.to_quaternion()
                qb = attr2.to_quaternion()
                attrx[:] = qa.slerp(qb,fac).to_euler()
        elif isinstance(attr1,Color):
            r1,g1,b1 = attr1
            r2,g2,b2 = attr2
            vec1 = Vector((r1,g1,b1))
            vec2 = Vector((r2,g2,b2))
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = vec1.lerp(vec2,fac)
        elif isinstance(attr1,bpy_prop_array) and len(attr1)==4:
            r1,g1,b1,a1 = attr1
            r2,g2,b2,a2 = attr2
            vec1 = Vector((r1,g1,b1))
            vec2 = Vector((r2,g2,b2))
            avec1 = Vector((a1,a1,a1))
            avec2 = Vector((a2,a2,a2))
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                t = (*vec1.lerp(vec2,fac),avec1.lerp(avec2,fac)[0])
                attrx[:] = t
        elif type(attr1) == float:
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                v1 = Vector((attr1,)*3)
                v2 = Vector((attr2,)*3)
                objx,propx = propexpr(ob,expr)
                setattr(objx,propx,v1.lerp(v2,fac)[0])
        elif type(attr1) == Object:
            for n,ob in enumerate(obs):
                objx,propx = propexpr(ob,expr)
                setattr(objx,propx,attr1)
            print("I OBJECT")
        return {"FINISHED"}


@_
class SysProp(PropertyGroup):
    value: StringProperty(default="name,location")


@_
class SYSPROP_MT_preset_menu(Menu):
    bl_label = "sysprop presets"
    preset_subdir = "sysprop_strings"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


@_
class SYSPROP_OT_sysprop_preset_add(AddPresetBase,Operator):
    bl_idname = "sysprop.add_preset"
    bl_label = "add sysprop preset"
    preset_menu = "SYSPROP_MT_preset_menu"
    preset_subdir = "sysprop_strings"
    preset_defines = ["sysprop = bpy.context.window_manager.sysprop"]
    preset_values = ["sysprop.value"]

@_
class SYSPROP_PT_presets(PresetPanel,Panel):
    bl_label = "SysPropChart2 Presets"
    preset_subdir = "sysprop_strings"
    preset_operator = "script.execute_preset"
    preset_add_operator = "sysprop.add_preset"

@_
class SYSPROP_PT_panel(Panel):
    bl_label = "SysPropChart2"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Chart"
    def draw_header_preset(self,context):
        SYSPROP_PT_presets.draw_panel_header(self.layout)
    # def draw_header(self,context):
    #     layout = self.layout
    #     layout.menu("SYSPROP_MT_preset_menu")
    #     row = self.layout.box().row(align=True)
    #     row.operator("sysprop.add_preset",text="",icon="PLUS")
    #     row.operator("sysprop.add_preset",text="",icon="TRASH").remove_active=True
    def draw(self,context):
        sysprop_string = context.window_manager.sysprop.value
        propstrings = sysprop_string.split(",")
        layout = self.layout
        box = layout.box()
        box.prop(context.window_manager.sysprop,"value",text="",icon="LIGHTPROBE_GRID")
        box.label(text=sysprop_string)
        cols = {expr:layout.column(align=True) for expr in propstrings}
        for expr in propstrings:
            op = cols[expr].row(align=True).operator("sysprop.interp",text=expr,icon="HANDLETYPE_AUTO_VEC")
            op.expr = expr
        for ob in context.selected_objects:
            for expr in propstrings:
                cols[expr].row(align=True).prop(*propexpr(ob,expr),text="")

def deploy_presets():
    if not len(preset_paths("sysprop_strings")):
        scriptsdir = Path(user_resource("SCRIPTS"))
        presetsdir = scriptsdir / "presets" / "sysprop_strings"
        presetsdir.mkdir(parents=True,exist_ok=True)
        presetsdir = str(presetsdir)
        print(f"[{__package__}]deploying presets to {presetsdir}",end="...")
        builtin_presets = Path(__file__).parent / "presets"
        for presetfile in map(str,builtin_presets.iterdir()):
            copy2(presetfile,presetsdir)
        print("OK")

def register():
    deploy_presets()
    list(map(register_class,_()))
    WindowManager.sysprop = PointerProperty(type=SysProp)

def unregister():
    del WindowManager.sysprop
    list(map(unregister_class,_()))

