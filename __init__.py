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
        "version":(1,0),
        "blender":(2,80,0),
        "location":"3d Viewport -> UI -> Chart",
        "warning":"",
        "wiki_url":"",
        "tracker_url":"",
        "category": "System"
        }

import bpy,re
from bl_operators.presets import AddPresetBase
from mathutils import Vector,Color
def propexpr(obj,expr):
    if "." in expr:
        head,dot,rest = expr.partition(".")
        indexed = re.match(r"(\w*)\[(\d*)\]$",head)
        keyed = re.match(r"(\w*)\[[\"'](.*)[\"']\]$",head)
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
class SYSPROP_OT_sysprop_interp(bpy.types.Operator):
    bl_idname = "sysprop.interp"
    bl_label = "Interpolate"
    bl_options = {"INTERNAL"}
    expr: bpy.props.StringProperty(default="")
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
        if isinstance(attr1,Vector):
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = attr1.lerp(attr2,fac)
        elif isinstance(attr1,Color):
            r1,g1,b1 = attr1
            r2,g2,b2 = attr2
            vec1 = Vector((r1,g1,b1))
            vec2 = Vector((r2,g2,b2))
            print("vec1,vec2:",vec1,vec2)
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                objx,propx = propexpr(ob,expr)
                attrx = getattr(objx,propx)
                attrx[:] = vec1.lerp(vec2,fac)
        elif isinstance(attr1,bpy.types.bpy_prop_array) and len(attr1)==4:
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
            print("attr1,attr2:",attr1,attr2)
            for n,ob in enumerate(obs[1:-1]):
                fac = inc * (n+1)
                v1 = Vector((attr1,)*3)
                v2 = Vector((attr2,)*3)
                print("v1,v2:",v1,v2)
                objx,propx = propexpr(ob,expr)
                setattr(objx,propx,v1.lerp(v2,fac)[0])
        return {"FINISHED"}


@_
class SysProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(default="name,data.name,location,data.materials[0].node_tree.nodes['Diffuse BSDF'].inputs[0].default_value")


@_
class SYSPROP_MT_preset_menu(bpy.types.Menu):
    bl_label = "sysprop presets"
    preset_subdir = "sysprop_strings"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


@_
class SYSPROP_OT_sysprop_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "sysprop.add_preset"
    bl_label = "add sysprop preset"
    preset_menu = "SYSPROP_MT_preset_menu"
    preset_subdir = "sysprop_strings"
    preset_defines = [ "sysprop = bpy.context.window_manager.sysprop" ]
    preset_values = ["sysprop.value"]


@_
class SYSPROP_PT_panel(bpy.types.Panel):
    bl_label = "sysprop"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Chart"
    def draw_header(self,context):
        layout = self.layout
        layout.menu("SYSPROP_MT_preset_menu")
        row = self.layout.box().row(align=True)
        row.operator("sysprop.add_preset",text="",icon="PLUS")
        row.operator("sysprop.add_preset",text="",icon="TRASH").remove_active=True
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


def register():
    preset_paths = bpy.utils.preset_paths("sysprop_strings")
    if not len(preset_paths):
        import pathlib
        scriptsdir = pathlib.Path(bpy.utils.user_resource("SCRIPTS"))
        presets = scriptsdir / "presets" / "sysprop_strings"
        print(presets)
        presets.mkdir(exist_ok=True)
        t = "import bpy\nsysprop = bpy.context.window_manager.sysprop\n\nsysprop.value='%s'".__mod__
        preset_sysprop_strings = {
                "mass":"particle_systems[0].settings.mass",
                "diffuse_color":"data.materials[0].node_tree.nodes[\"Diffuse BSDF\"].inputs[0].default_value",
                "location":"location"}
        for k,v in preset_sysprop_strings.items():
            with open(str(presets/(k+".py")),"w") as presetfile:
                presetfile.write(t(v))


    list(map(bpy.utils.register_class,_()))
    bpy.types.WindowManager.sysprop = bpy.props.PointerProperty(type=SysProp)

def unregister():
    del bpy.types.WindowManager.sysprop
    list(map(bpy.utils.unregister_class,_()))

