import bpy
import math

from .tools.update_progress import update_progress


def get_context_area(context, context_dict, area_type='GRAPH_EDITOR',
                     context_screen=False):
    """
    context : the current context
    context_dict : a context dictionary. Will update area, screen, scene,
                   area, region
    area_type: the type of area to search for
    context_screen: Boolean. If true only search in the context screen.
    """
    if not context_screen:  # default
        screens = bpy.data.screens
    else:
        screens = [context.screen]
    for screen in screens:
        for area_index, area in screen.areas.items():
            if area.type == area_type:
                for region in area.regions:
                    if region.type == 'WINDOW':
                        context_dict["area"] = area
                        context_dict["screen"] = screen
                        context_dict["scene"] = context.scene
                        context_dict["window"] = context.window
                        context_dict["region"] = region
                        return area
    return None


class GenerateVisualizer(bpy.types.Operator):
    bl_idname = "object.bz_generate"
    bl_label = "(re)Generate Visualizer"
    bl_description = "Generates visualizer bars and animation"

    base_size = 2

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.bz_audio_file == "":
            return False
        else:
            return True

    def getVertices(self, shape):
        if shape == "RECTANGLE":
            return [(-1, 2, 0), (1, 2, 0), (1, 0, 0), (-1, 0, 0)]
        if shape == "TRIANGLE":
            return [(0, 2, 0), (1, 0, 0), (-1, 0, 0)]
        if shape == "CUBOID":
            return [(-1, 2, -1), (1, 2, -1), (1, 0, -1), (-1, 0, -1), (-1, 2, 1), (1, 2, 1), (1, 0, 1), (-1, 0, 1)]
        if shape == "PYRAMID":
            return [(0, 2, 0), (-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)]

    def getFaces(self, shape):
        if shape == "RECTANGLE":
            return [(0, 1, 2, 3)]
        if shape == "TRIANGLE":
            return [(0, 1, 2)]
        if shape == "CUBOID":
            return [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)]
        if shape == "PYRAMID":
            return [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3, 4)]

    def lerp_color(self, start_color, end_color, ratio):
        result = [0, 0, 0]

        for index in [0, 1, 2]:
            result[index] = start_color[index] + ratio * (end_color[index] - start_color[index])

        return result

    def execute(self, context):
        scene = context.scene
        scene.frame_current = 1
        attack_time = scene.bz_attack_time
        release_time = scene.bz_release_time

        if not scene.bz_use_custom_mesh:
            bar_shape = scene.bz_bar_shape
            vertices = self.getVertices(bar_shape)
            faces = self.getFaces(bar_shape)

        bar_count = scene.bz_bar_count

        bar_width = scene.bz_bar_width / self.base_size
        bar_depth = scene.bz_bar_depth / self.base_size
        amplitude = scene.bz_amplitude / self.base_size
        spacing = scene.bz_spacing + scene.bz_bar_width

        radius = scene.bz_radius
        arc_angle_deg = scene.bz_arc_angle
        arc_center_deg = scene.bz_arc_center_offset
        if scene.bz_use_sym and scene.bz_flip_direction:
            arc_center_deg += 180

        flip_direction = scene.bz_flip_direction
        preview_mode = scene.bz_preview_mode
        audiofile = bpy.path.abspath(scene.bz_audio_file)

        digits = str(len(str(bar_count)))
        number_format = "%0" + digits + "d"
        line_start = -(bar_count * spacing) / 2 + spacing / 2
        preview_coef = 8 * math.pi / bar_count

        arc_direction = -1
        if flip_direction:
            arc_direction = 1

        arc_angle = arc_angle_deg / 360 * 2 * math.pi
        arc_center = -arc_center_deg / 360 * 2 * math.pi
        arc_start = arc_center - arc_direction * arc_angle / 2

        note_step = 120.0 / bar_count
        a = 2 ** (1.0 / 12.0)
        low = 0.0
        high = 16.0

        bpy.ops.object.select_all(action="DESELECT")
        collection_name = "Bizualizer Collection"
        collection_present = bpy.data.collections.get(collection_name)

        if collection_present:
            empty_present = collection_present.objects.get(scene.bz_custom_name)
            if empty_present:
                for i in empty_present.children:
                    i.select_set(True)
                bpy.ops.object.delete()
        else:
            scene.collection.children.link(bpy.data.collections.new(collection_name))

        wm = context.window_manager
        wm.progress_begin(0, 100.0)

        centre_empty = scene.collection.children[collection_name].objects.get(scene.bz_custom_name)
        if not centre_empty:
            centre_empty = bpy.data.objects.new(scene.bz_custom_name, None)
            scene.collection.children[collection_name].objects.link(centre_empty)

        for i in range(0, bar_count):
            formatted_number = number_format % i
            name = 'Bar ' + formatted_number

            if not scene.bz_use_custom_mesh:
                mesh = bpy.data.meshes.new(name)
                mesh.from_pydata(vertices, [], faces)
                mesh.update()
                bar = bpy.data.objects.new(name, mesh)
            else:
                bar = bpy.data.objects.new(name, scene.bz_custom_mesh.copy())

            scene.collection.children[collection_name].objects.link(bar)

            bar.select_set(True)
            bpy.context.view_layer.objects.active = bar

            loc = [0.0, 0.0, 0.0]

            if scene.bz_use_radial:

                if scene.bz_use_sym:
                    angle = arc_start + (arc_direction * ((i + 0.5) / bar_count) * (arc_angle / 2))
                else:
                    angle = arc_start + (arc_direction * ((i + 0.5) / bar_count) * arc_angle)

                bar.rotation_euler[2] = angle
                loc[0] = -math.sin(angle) * radius
                loc[1] = math.cos(angle) * radius

            else:
                loc[0] = (i * spacing) + line_start

            bar.location = (loc[0], loc[1], loc[2])

            bar.scale.x = bar_width
            bar.scale.y = amplitude
            bar.scale.z = bar_depth

            c = bpy.context.copy()
            get_context_area(bpy.context, c)

            if preview_mode:
                bar.scale.y = amplitude * (math.cos(i * preview_coef) + 1.2) / 2.2
            else:
                bpy.ops.object.transform_apply(
                    location=False, rotation=False, scale=True)

                bpy.ops.anim.keyframe_insert_menu(c, type="Scaling")
                bar.animation_data.action.fcurves[0].lock = True
                bar.animation_data.action.fcurves[2].lock = True

                low = high
                high = low * (a ** note_step)

                area = bpy.context.area.type
                bpy.context.area.type = 'GRAPH_EDITOR'

                bpy.ops.graph.sound_bake(filepath=audiofile, low=low, high=high,
                                         attack=attack_time, release=release_time)

                bpy.context.area.type = area

                active = bpy.context.active_object
                active.animation_data.action.fcurves[1].lock = True

            bar.active_material = scene.bz_material

            if scene.bz_use_sym:
                mirror_modifier = bar.modifiers.new(name="Mirror", type="MIRROR")
                mirror_modifier.mirror_object = centre_empty
                if not scene.bz_use_radial:
                    mirror_modifier.use_axis = (False, True, False)

            bar.select_set(False)
            progress = 100 * (i / bar_count)
            wm.progress_update(progress)
            update_progress("Generating Visualizer", progress / 100.0)

        original_location = centre_empty.location[:]
        original_rotation = centre_empty.rotation_euler[:]
        original_scale = centre_empty.scale[:]
        centre_empty.location = (0.0, 0.0, 0.0)
        centre_empty.rotation_euler = (0.0, 0.0, 0.0)
        centre_empty.scale = (1.0, 1.0, 1.0)

        for i in scene.collection.children[collection_name].objects:
            if not i.parent and len(i.children) == 0:
                i.select_set(True)

        centre_empty.select_set(True)
        context.view_layer.objects.active = centre_empty
        bpy.ops.object.parent_set()

        bpy.ops.object.select_all(action="DESELECT")
        centre_empty.select_set(True)

        centre_empty.location = original_location
        centre_empty.rotation_euler = original_rotation
        centre_empty.scale = original_scale

        wm.progress_end()
        update_progress("Generating Visualizer", 1)
        bpy.context.view_layer.objects.active = None
        return {"FINISHED"}
