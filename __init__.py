import sys
import os
import bpy


from bpy.types import Operator 

bl_info = {
            "name": "Scripter",
            "author": "Matheus Fillipe",
            "version": (1, 0, 0),
            "blender": (2, 80, 0),
            "location": "TextEditor",
            "description": "Easilly run scripts directly on the Plender Python Console",
            "category": "Development",
}
location=bpy.types.CONSOLE_HT_header
locationTextEditor=bpy.types.TEXT_MT_text

class BlenderController(bpy.types.Operator):
    """"Runs the active script on the Text Editor on the Python Console"""

    bl_idname = "object.blendercontroller_operator"
    bl_label = "Run"

    def execute(self, context):
        current=None
        override=None
        context = bpy.context

        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                space = area.spaces.active
                current=repr(space.text)
            if area.type == 'CONSOLE':
                override = bpy.context.copy()
                override['space_data'] = area.spaces.active
                override['region'] = area.regions[-1]
                override['area'] = area

              #  print(context.area, override['area'])
              #  print(context.screen, override['screen'])
              #  print(context.window, override['window'])
                override['screen'] = context.screen
               


        if current is None or override is None:
            self.report(type='ERROR',message="Please make sure you have a Console and Text Editor visible")

        bpy.ops.console.insert(override,text="exec("+current+".as_string())\n")
        bpy.ops.console.execute(override, interactive=True)

        return {'FINISHED'} 
        

def add_object_button(self, context):  
        self.layout.operator(  
        BlenderController.bl_idname,  
            text=BlenderController.bl_label,  
            icon='PLAY') 

addon_keymaps = []

def register():
    bpy.utils.register_class(BlenderController) 
    location.append(add_object_button)
    locationTextEditor.append(add_object_button)
    
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    kmi = km.keymap_items.new(BlenderController.bl_idname, 'F9', 'PRESS', ctrl=False, shift=False)

    addon_keymaps.append((km, kmi))
 
def unregister():
    bpy.utils.unregister_class(BlenderController) 
    location.remove(add_object_button)
    locationTextEditor.remove(add_object_button)


    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        addon_keymaps.clear()

if __name__ == "__main__":  
    register() 
