import bpy
import math
import re
import colorsys

from .tools.update_progress import update_progress


def make_color(name, rgb, emission_strength):
    if name in bpy.data.materials:
        material = bpy.data.materials[name]
    else:
        material = bpy.data.materials.new(name=name)
    material.use_nodes = True

    nodes = material.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

    node_lightpath = nodes.new(type='ShaderNodeLightPath')
    node_lightpath.location = [-200, 100]

    node_emission = nodes.new(type='ShaderNodeEmission')
    node_emission.inputs[0].default_value = (rgb[0], rgb[1], rgb[2], 1)
    node_emission.inputs[1].default_value = emission_strength
    node_emission.location = [0, -50]

    node_mix = nodes.new(type='ShaderNodeMixShader')
    node_mix.location = [200, 0]

    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = [400, 0]

    links = material.node_tree.links
    links.new(node_lightpath.outputs[0], node_mix.inputs[0])
    links.new(node_emission.outputs[0], node_mix.inputs[2])
    links.new(node_mix.outputs[0], node_output.inputs[0])

    return material


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


class RENDER_OT_generate_visualizer(bpy.types.Operator):
    bl_idname = "object.bz_generate"
    bl_label = "(re)Generate Visualizer"
    bl_description = "Generates visualizer bars and animation"

    base_size = 2

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.bz_audiofile == "":
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
        bar_shape = scene.bz_bar_shape
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
        audiofile = bpy.path.abspath(scene.bz_audiofile)

        digits = str(len(str(bar_count)))
        number_format = "%0" + digits + "d"
        line_start = -(bar_count * spacing) / 2 + spacing / 2
        preview_coef = 8 * math.pi / bar_count

        vertices = self.getVertices(bar_shape)
        faces = self.getFaces(bar_shape)

        arc_direction = -1
        if flip_direction:
            arc_direction = 1

        arc_angle = arc_angle_deg / 360 * 2 * math.pi
        arc_center = -arc_center_deg / 360 * 2 * math.pi
        arc_start = arc_center - arc_direction * arc_angle / 2

        color_style = scene.bz_color_style
        emission_strength = scene.bz_emission_strength

        if color_style == "SINGLE_COLOR":
            material = make_color('bz_color', scene.bz_color1, emission_strength)
        else:
            color_dict = self.create_color_dictionary(scene)
            color_pattern = self.parse_color_pattern_input(scene)
            color_pattern_length = len(color_pattern)
            gradient_interpolation = scene.bz_gradient_interpolation

            if color_pattern_length == 0:
                self.report({"ERROR"}, "Color Pattern is invalid!")
                return {"FINISHED"}

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

            mesh = bpy.data.meshes.new(name)
            bar = bpy.data.objects.new(name, mesh)
            scene.collection.children[collection_name].objects.link(bar)

            bar.select_set(True)
            bpy.context.view_layer.objects.active = bar
            mesh.from_pydata(vertices, [], faces)
            mesh.update()

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

            if color_style == "PATTERN":
                color_index = color_pattern[i % color_pattern_length]
                color = color_dict[color_index]["rgb"]
                material = make_color('bz_color' + formatted_number, color, emission_strength)

            if color_style == "GRADIENT":
                progress = (i + 0.5) / bar_count
                color = self.compute_gradient_color(progress, color_pattern_length, color_pattern, color_dict,
                                                    gradient_interpolation)
                material = make_color('bz_color' + formatted_number, color, emission_strength)

            bar.active_material = material

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

    def parse_color_pattern_input(self, scene):
        color_count = scene.bz_color_count
        color_pattern_user_input = scene.bz_color_pattern
        scene.bz_color_pattern = re.sub("[^1-9]", "", scene.bz_color_pattern)
        color_pattern = re.sub("[^1-{0:d}]".format(color_count), "", scene.bz_color_pattern)

        if color_pattern != scene.bz_color_pattern:
            self.report({"WARNING"}, "Color Pattern: Extra colors are ignored!")

        if color_pattern_user_input != scene.bz_color_pattern:
            self.report({"WARNING"}, "Color Pattern: Invalid characters were removed!")

        return color_pattern

    def create_color_dictionary(self, scene):
        color_dict = {
            "1": {"rgb": scene.bz_color1},
            "2": {"rgb": scene.bz_color2},
            "3": {"rgb": scene.bz_color3},
            "4": {"rgb": scene.bz_color4},
            "5": {"rgb": scene.bz_color5},
            "6": {"rgb": scene.bz_color6},
            "7": {"rgb": scene.bz_color7},
            "8": {"rgb": scene.bz_color8},
            "9": {"rgb": scene.bz_color9},
        }

        for key in color_dict:
            color_item = color_dict[key]
            rgb = color_item["rgb"]
            h, s, v = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            color_item["hsv"] = [h, s, v]
            h, l, s = colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])
            color_item["hsl"] = [h, l, s]

        return color_dict

    def compute_gradient_color(self, progress, color_pattern_length, color_pattern, color_dict, gradient_interpolation):
        pattern_position = progress * (color_pattern_length - 1)
        start_color_index = color_pattern[math.floor(pattern_position) % color_pattern_length]
        end_color_index = color_pattern[math.ceil(pattern_position) % color_pattern_length]
        start_color_dict = color_dict[start_color_index]
        end_color_dict = color_dict[end_color_index]

        start_color = start_color_dict[gradient_interpolation.lower()]
        end_color = end_color_dict[gradient_interpolation.lower()]
        lerped_color = self.lerp_color(start_color, end_color, pattern_position % 1)

        if gradient_interpolation == "RGB":
            final_color = lerped_color
        elif gradient_interpolation == "HSV":
            r, g, b = colorsys.hsv_to_rgb(lerped_color[0], lerped_color[1], lerped_color[2])
            final_color = [r, g, b]
        elif gradient_interpolation == "HSL":
            r, g, b = colorsys.hls_to_rgb(lerped_color[0], lerped_color[1], lerped_color[2])
            final_color = [r, g, b]

        return final_color
