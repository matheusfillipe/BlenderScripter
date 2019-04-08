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

_BPY_MAIN_OWN = True
from console_python import *

def add_scrollback(context, text, text_type):
    for l in text.split("\n"):
        bpy.ops.console.scrollback_append(context, text=l.replace("\t", "    "), type=text_type)


def execute(context, is_interactive):
    sc = context['space_data']
    try:
        line_object = sc.history[-1]
    except:
        return {'CANCELLED'}
    console, stdout, stderr = get_console(hash(context['region']))
    if _BPY_MAIN_OWN:
        main_mod_back = sys.modules["__main__"]
        sys.modules["__main__"] = console._bpy_main_mod
    from contextlib import (
        redirect_stdout,
        redirect_stderr,
    )
    class redirect_stdin(redirect_stdout.__base__):
        _stream = "stdin"
    with redirect_stdout(stdout), \
            redirect_stderr(stderr), \
            redirect_stdin(None):
        line = ""  # in case of encoding error
        is_multiline = False
        try:
            line = line_object.body
            line_exec = line if line.strip() else "\n"
            is_multiline = console.push(line_exec)
        except:
            import traceback
            stderr.write(traceback.format_exc())
    if _BPY_MAIN_OWN:
        sys.modules["__main__"] = main_mod_back
    stdout.seek(0)
    stderr.seek(0)
    output = stdout.read()
    output_err = stderr.read()
    sys.last_traceback = None
    stdout.truncate(0)
    stderr.truncate(0)
    if hash(sc) != hash(context['space_data']):
        return {'FINISHED'}

    #bpy.ops.console.scrollback_append(text=sc.prompt + line, type='INPUT')

    if is_multiline:
        sc.prompt = PROMPT_MULTI
        if is_interactive:
            indent = line[:len(line) - len(line.lstrip())]
            if line.rstrip().endswith(":"):
                indent += "    "
        else:
            indent = ""
    else:
        sc.prompt = PROMPT
        indent = ""

    # insert a new blank line
    #bpy.ops.console.history_append(context, text=indent, current_character=0, remove_duplicates=True)
    sc.history[-1].current_character = len(indent)

    if output:
        add_scrollback(context, output, 'OUTPUT')
    if output_err:
        add_scrollback(context, output_err, 'ERROR')

    return {'FINISHED'}

class BlenderController(bpy.types.Operator):
    """Runs the active script on the Text Editor on the Python Console"""
    bl_idname = "object.blendercontroller_operator"
    bl_label = "Run"
    bl_description = "Runs the active script on the Text Editor on the Python Console"


    def execute(self, context):
        current=None
        override=None
        context = bpy.context
        script_name = ''

        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                space = area.spaces.active
                current=repr(space.text)
                script_name = space.text.name
            if area.type == 'CONSOLE':
                override = bpy.context.copy()
                override['space_data'] = area.spaces.active
                override['region'] = area.regions[-1]
                override['area'] = area
                override['screen'] = context.screen

        if current is None or override is None:
            self.report(type='ERROR',message="Please make sure you have a Console and Text Editor visible")
            return {'CANCELLED'}

        bpy.ops.console.clear_line(override)
        bpy.ops.console.scrollback_append(override, text='Running Script: '+script_name, type='OUTPUT')
        bpy.ops.console.insert(override,text="exec("+current+".as_string())\n")
        execute(override, is_interactive=True)
        bpy.ops.console.clear_line(override)


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
    km = wm.keyconfigs.addon.keymaps.new(name='Window', region_type='WINDOW', space_type='EMPTY')

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
