import bpy
from .operators import *

bl_info = {
    "name": "Blendualizer",
    "description": "Audio Visualizer Creator",
    "author": "532stary4",
    "version": (0, 2, 0),
    "blender": (2, 93, 0),
    "wiki_url": "https://github.com/532stary4/Blendualizer",
    "tracker_url": "https://github.com/532stary4/Blendualizer/issues",
    "category": "Animation",
    "location": "Properties > Scene"}


class BLENDUALIZER_PT_properties_ui(bpy.types.Panel):
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
        row.prop(scene, "bz_audio_file", icon="SOUND")
        row = layout.row()
        split = row.split()
        col_a = split.column(align=True)
        col_a.prop(scene, "blz_start_freq")
        col_b = split.column(align=True)
        col_b.prop(scene, "blz_freq_step")

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
        col_a.label(text="Visualizer Shape:")
        col_b = split.column(align=True)
        col_b.prop(scene, "bz_vis_shape")
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
        col_b.enabled = self.is_shape_3d(scene.bz_vis_shape)
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


def init_prop():
    bpy.types.Scene.bz_audio_file = bpy.props.StringProperty(
        name="Audio Path",
        description="Define path of the audio file",
        subtype="FILE_PATH",
    )

    bpy.types.Scene.blz_start_freq = bpy.props.IntProperty(
        name="Starting frequency",
        description="The starting frequency",
        default=0,
        min=0,
        max=100000
    )

    bpy.types.Scene.blz_freq_step = bpy.props.IntProperty(
        name="Freq Step Size",
        description="The power of the root of 2",
        default=12,
        min=1,
        max=1000
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

    bpy.types.Scene.bz_vis_shape = bpy.props.EnumProperty(
        name="",
        description="The shape of the bars",
        default="RECTANGLE",
        items=[("RECTANGLE", "Rectangle", "", "", 1),
               ("TRIANGLE", "Triangle", "", "", 2),
               ("CUBOID", "Cuboid", "", "", 3),
               ("PYRAMID", "Pyramid", "", "", 4),
               ('CURVE', 'Curve', '', '', 5)]
    )

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

    bpy.types.Scene.bz_preview_mode = bpy.props.BoolProperty(
        name="Preview Mode",
        description="Generate bars without animation",
        default=False
    )


classes = [
    BLENDUALIZER_PT_properties_ui,
    BLENDUALIZER_OT_audio_to_vse,
    BLENDUALIZER_OT_generate_visualizer,
    BLENDUALIZER_OT_remove_audio_from_vse,
]


def register():
    init_prop()

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
