import bpy
import os
import shutil

from .operators import *

bl_info = {
    "name": "Bizualizer",
    "description": "Create a simple visualizer for audio",
    "author": "doakey3",
    "version": (1, 3, 4),
    "blender": (2, 93, 0),
    "wiki_url": "https://github.com/doakey3/Bizualizer",
    "tracker_url": "https://github.com/doakey3/Bizualizer/issues",
    "category": "Animation",
    "location": "Properties > Scene"}


class RENDER_PT_ui(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_label = "Bizualizer"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def is_shape_3d(self, shape):
        if shape == "CUBOID" or shape == "PYRAMID":
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        row = layout.label(text="Audio")

        row = layout.row()
        row.prop(scene, "bz_audiofile", icon="SOUND")
        row = layout.row()
        row.prop(scene, "bz_audio_channel")
        row = layout.row()
        row.operator("sequencerextra.bz_audio_to_sequencer",
                     icon="SEQ_SEQUENCER")
        row.operator("sequencerextra.bz_audio_remove", icon="CANCEL")

        row = layout.separator()
        row = layout.label(text="Bars")

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.label(text="Bar Name:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_custom_name")

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.label(text="Bar Shape:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_bar_shape")

        row = layout.row()
        row.prop(scene, "bz_bar_count")
        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "bz_bar_width")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_bar_depth")
        col_b.enabled = self.is_shape_3d(scene.bz_bar_shape)
        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "bz_amplitude")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_spacing")
        col_b.enabled = not scene.bz_use_radial
        row = layout.row()
        row.prop(scene, "bz_attack_time")
        row.prop(scene, "bz_release_time")

        row = layout.separator()

        row = layout.row()
        row.prop(scene, "bz_use_radial")

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "bz_radius")
        col_a.enabled = scene.bz_use_radial
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_flip_direction")
        col_b.enabled = scene.bz_use_radial

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "bz_arc_angle")
        col_a.enabled = scene.bz_use_radial
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_arc_center_offset")
        col_b.enabled = scene.bz_use_radial

        row = layout.separator()
        row = layout.label(text="Colors")

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.label(text="Visualizer Color Style:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_color_style")

        if scene.bz_color_style != "SINGLE_COLOR":
            row = layout.row()
            row.prop(scene, "bz_color_count")

        row = layout.row()
        row.prop(scene, "bz_color1")

        if scene.bz_color_style != "SINGLE_COLOR":
            for index in range(2, scene.bz_color_count + 1):
                row = layout.row()
                row.prop(scene, "bz_color" + ("{0:d}".format(index)))

            row = layout.row()
            row.prop(scene, "bz_color_pattern")

            if scene.bz_color_style == "GRADIENT":
                row = layout.row()
                row.prop(scene, "bz_gradient_interpolation")

        row = layout.row()
        row.prop(scene, "bz_emission_strength")

        row = layout.separator()
        row = layout.label(text="Generate")

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "bz_preview_mode")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_use_sym")

        row = layout.row()
        row.operator("object.bz_generate", icon="FILE_REFRESH")

        row = layout.separator()
        row = layout.label(text="Camera")

        row = layout.row()
        row.prop(scene, "bz_cam_alignment")
        row = layout.row()
        row.operator("object.bz_align_camera", icon="CAMERA_DATA")

        row = layout.separator()

        box = layout.box()
        row = box.row()
        row.prop(scene, 'bbz_config')
        row = box.row()
        row.operator('object.batch_bizualize', icon="ALIGN_LEFT")
        row.operator('object.make_bz_previews')

        '''
        #column = layout.column()
        #for i in range(scene.bz_bar_count):
        #layout.prop_search(scene, "bob",  scene, "objects")
        
        row = layout.row()
        row.template_list('UI_UL_list', 'bob', scene, "bar_collection", scene, "bar_collection_index")
        
        col = row.column(align=True)
        col.operator("collection.add_remove", icon="ZOOM_IN", text="").add = True
        col.operator("collection.add_remove", icon="ZOOM_OUT", text="").add = False
        
        if scene.bar_collection:
            entry = scene.bar_collection[scene.bar_collection_index]
            
            layout.prop_search(entry, "obj_name", scene, 'objects', text='Object Name')
            

class OBJECT_OT_add_remove_Collection_Items(bpy.types.Operator):
    bl_label = "Add or Remove"
    bl_idname = "collection.add_remove"
    
    add : bpy.props.BoolProperty(default = True)
    
    def invoke(self, context, event):
        add = self.add
        scene = context.scene
        collection = scene.bar_collection
        if add:
            collection.add()
            scene.bar_collection_index = 0
        else:
            index = scene.bar_collection_index
            scene.bar_collection_index -= 1
            collection.remove(index)
        
        #self.report({'INFO'}, str(scene.bar_collection_index))
        
        return {'FINISHED'}


class PropertyGroup(bpy.types.PropertyGroup):
    #name: bpy.props.IntProperty(name='Bar Number', default=0)
    obj_name: bpy.props.StringProperty(name='Object name to be affected')
'''

def initprop():
    '''bpy.types.Scene.bob = bpy.props.StringProperty()

    bpy.utils.register_class(PropertyGroup)
    bpy.types.Scene.bar_collection = bpy.props.CollectionProperty(type=PropertyGroup)
    bpy.types.Scene.bar_collection_index = bpy.props.IntProperty(min = -1, default = -1)'''


    bpy.types.Scene.bz_audiofile = bpy.props.StringProperty(
        name="Audio Path",
        description="Define path of the audio file",
        subtype="FILE_PATH",
    )

    bpy.types.Scene.bz_audio_channel = bpy.props.IntProperty(
        name="Audio Channel",
        description="Channel where audio will be added",
        default=1,
        min=1
    )

    bpy.types.Scene.bz_attack_time = bpy.props.FloatProperty(
        name="Attack Time",
        description="How long it takes for the hull curve to rise (the lower the value the steeper it can rise)",
        default=0.005,
        min=0,
        max=2
    )

    bpy.types.Scene.bz_release_time = bpy.props.FloatProperty(
        name="Release Time",
        description="How long it takes for the hull curve to fall (the lower the value the steeper it can fall)",
        default=0.2,
        min=0,
        max=5
    )

    bpy.types.Scene.bz_custom_name = bpy.props.StringProperty(
        name="",
        description="Define the name",
        default="bz_bar",
        subtype="NONE"
    )

    bpy.types.Scene.bz_bar_shape = bpy.props.EnumProperty(
        name="",
        description="The shape of the bars",
        default="RECTANGLE",
        items=[("RECTANGLE", "Rectangle", "", "", 1),
               ("TRIANGLE", "Triangle", "", "", 2),
               ("CUBOID", "Cuboid", "", "", 3),
               ("PYRAMID", "Pyramid", "", "", 4)
               ])

    bpy.types.Scene.bz_bar_count = bpy.props.IntProperty(
        name="Bar Count",
        description="The number of bars to make",
        default=64,
        min=1
    )

    bpy.types.Scene.bz_bar_width = bpy.props.FloatProperty(
        name="Bar Width",
        description="The width of the bars",
        default=1.6,
        min=0
    )

    bpy.types.Scene.bz_bar_depth = bpy.props.FloatProperty(
        name="Bar Depth",
        description="The depth of the bars (3D only)",
        default=1.6,
        min=0
    )

    bpy.types.Scene.bz_amplitude = bpy.props.FloatProperty(
        name="Amplitude",
        description="Amplitude of visualizer bars",
        default=48.0,
        min=0
    )

    bpy.types.Scene.bz_spacing = bpy.props.FloatProperty(
        name="Spacing",
        description="Spacing between bars",
        default=0.65,
        min=0
    )

    bpy.types.Scene.bz_use_radial = bpy.props.BoolProperty(
        name="Use Radial",
        description="Use a circular visualizer",
        default=False
    )

    bpy.types.Scene.bz_radius = bpy.props.FloatProperty(
        name="Radius",
        description="Radius of the radial visualizer",
        default=20,
        min=0
    )

    bpy.types.Scene.bz_arc_angle = bpy.props.FloatProperty(
        name="Arc Angle",
        description="Angular size of the radial visualizer",
        default=360,
        min=1,
        max=360
    )

    bpy.types.Scene.bz_arc_center_offset = bpy.props.FloatProperty(
        name="Arc Rotation",
        description="Angle where radial visualizer is centered",
        default=0,
        min=-180,
        max=180
    )

    bpy.types.Scene.bz_flip_direction = bpy.props.BoolProperty(
        name="Flip Direction",
        description="Arrange the bars in reverse direction",
        default=False
    )

    bpy.types.Scene.bz_use_sym = bpy.props.BoolProperty(
        name="Use Symmetry",
        description="Visualizer is reflected over Y axis",
        default=False
    )

    color_input_description = "Color applied to bars after visualizer is generated"

    bpy.types.Scene.bz_color_style = bpy.props.EnumProperty(
        name="",
        description="How the color(s) should be applied to bars",
        default="SINGLE_COLOR",
        items=[("SINGLE_COLOR", "Single Color", "", "", 1),
               ("PATTERN", "Pattern", "", "", 2),
               ("GRADIENT", "Gradient", "", "", 3)
               ])

    bpy.types.Scene.bz_color_count = bpy.props.IntProperty(
        name="Color Count",
        description="Number of input colors",
        default=3,
        min=2,
        max=9
    )

    bpy.types.Scene.bz_color1 = bpy.props.FloatVectorProperty(
        name="Bar Color 1",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color2 = bpy.props.FloatVectorProperty(
        name="Bar Color 2",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(1.0, 0.0, 0.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color3 = bpy.props.FloatVectorProperty(
        name="Bar Color 3",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(0.0, 0.0, 1.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color4 = bpy.props.FloatVectorProperty(
        name="Bar Color 4",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(0.0, 1.0, 0.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color5 = bpy.props.FloatVectorProperty(
        name="Bar Color 5",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(0.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color6 = bpy.props.FloatVectorProperty(
        name="Bar Color 6",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(1.0, 1.0, 0.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color7 = bpy.props.FloatVectorProperty(
        name="Bar Color 7",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(1.0, 0.0, 1.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color8 = bpy.props.FloatVectorProperty(
        name="Bar Color 8",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(0.5, 0.5, 0.5),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color9 = bpy.props.FloatVectorProperty(
        name="Bar Color 9",
        subtype='COLOR_GAMMA',
        description=color_input_description,
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0
    )

    bpy.types.Scene.bz_color_pattern = bpy.props.StringProperty(
        name="Color Pattern",
        description="Pattern in which the colors will be applied to bars",
        default="12321"
    )

    bpy.types.Scene.bz_gradient_interpolation = bpy.props.EnumProperty(
        name="Interpolation",
        description="Color system used for computing the gradient",
        default="RGB",
        items=[("RGB", "RGB", "", "", 1),
               ("HSV", "HSV", "", "", 2),
               ("HSL", "HSL", "", "", 3)
               ])

    bpy.types.Scene.bz_emission_strength = bpy.props.FloatProperty(
        name="Glow Strength",
        description="Strength of the emission shader",
        default=1.0,
        min=0
    )

    bpy.types.Scene.bz_preview_mode = bpy.props.BoolProperty(
        name="Preview Mode",
        description="Generate bars without animation",
        default=False
    )

    bpy.types.Scene.bz_cam_alignment = bpy.props.EnumProperty(
        name="Alignment",
        description="Position, orientation and type of camera",
        default="2D_bottom",
        items=[("2D_bottom", "2D bottom", "", "", 1),
               ("2D_center", "2D center", "", "", 2),
               ("2D_top", "2D top", "", "", 3),
               ("2D_left", "2D left", "", "", 4),
               ("2D_right", "2D right", "", "", 5),
               ("3D_bottom", "3D bottom", "", "", 6),
               ("3D_center", "3D center", "", "", 7)
               ])

    bpy.types.Scene.bbz_config = bpy.props.StringProperty(
        name="Config File",
        description="Path to the Config File",
        subtype="FILE_PATH",
    )


classes = [
    RENDER_PT_ui,
    RENDER_OT_align_camera,
    RENDER_OT_audio_to_vse,
    RENDER_OT_batch_bizualize,
    RENDER_OT_generate_visualizer,
    RENDER_OT_make_previews,
    RENDER_OT_remove_bz_audio
]
# OBJECT_OT_add_remove_Collection_Items

def register():
    initprop()

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    # unregister_class(PropertyGroup)

    for cls in reversed(classes):
        unregister_class(cls)
