import bpy
import os
import shutil

from .operators import *

bl_info = {
    "name": "Blendualizer",
    "description": "Audio Visualizer Creator",
    "author": "532stary4",
    "version": (0, 1, 0),
    "blender": (2, 93, 0),
    "wiki_url": "https://github.com/532stary4/Blendualizer",
    "tracker_url": "https://github.com/532stary4/Blendualizer/issues",
    "category": "Animation",
    "location": "Properties > Scene"}


class PropertiesUi(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_label = "Blendualizer"
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
        col_a.label(text="Bar Set Name:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_custom_name")

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.label(text="Bar Shape:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_bar_shape")
        col_b.enabled = not scene.bz_use_custom_mesh
        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "bz_use_custom_mesh")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_custom_mesh")
        col_b.enabled = scene.bz_use_custom_mesh

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

        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.label(text="Visualizer Material:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_material")

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

    bpy.types.Scene.bz_use_custom_mesh = bpy.props.BoolProperty(
        name="Custom Mesh",
        description="Select mesh",
        default=False
    )

    bpy.types.Scene.bz_custom_mesh = bpy.props.PointerProperty(
        name="",
        description="Mesh to use",
        type=bpy.types.Mesh
    )

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

    bpy.types.Scene.bz_material = bpy.props.PointerProperty(
        name="",
        description="Material to be applied to bars",
        type=bpy.types.Material
    )

    # color_input_description = "Color applied to bars after visualizer is generated"

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


classes = [
    PropertiesUi,
    RENDER_OT_align_camera,
    RENDER_OT_audio_to_vse,
    GenerateVisualizer,
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
