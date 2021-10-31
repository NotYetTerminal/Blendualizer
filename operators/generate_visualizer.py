import bpy
import math

class BLENDUALIZER_OT_generate_visualizer(bpy.types.Operator):
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
        audio_file = bpy.path.abspath(scene.bz_audio_file)

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
                for bar in empty_present.children:
                    bar.select_set(True)
                bpy.ops.object.delete()
        else:
            scene.collection.children.link(bpy.data.collections.new(collection_name))

        wm = context.window_manager
        wm.progress_begin(0, 100.0)

        bar_set_empty = scene.collection.children[collection_name].objects.get(scene.bz_custom_name)
        if not bar_set_empty:
            bar_set_empty = bpy.data.objects.new(scene.bz_custom_name, None)
            scene.collection.children[collection_name].objects.link(bar_set_empty)

        area = bpy.context.area.type
        bpy.context.area.type = 'GRAPH_EDITOR'

        for count in range(0, bar_count):

            name = str(round(low, 1)) + ' | ' + str(round(high, 1))

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
                    angle = arc_start + (arc_direction * ((count + 0.5) / bar_count) * (arc_angle / 2))
                else:
                    angle = arc_start + (arc_direction * ((count + 0.5) / bar_count) * arc_angle)

                bar.rotation_euler[2] = angle
                loc[0] = -math.sin(angle) * radius
                loc[1] = math.cos(angle) * radius

            else:
                loc[0] = (count * spacing) + line_start

            bar.location = (loc[0], loc[1], loc[2])

            bar.scale.x = bar_width
            bar.scale.y = amplitude
            bar.scale.z = bar_depth

            if preview_mode:
                bar.scale.y = amplitude * (math.cos(count * preview_coef) + 1.2) / 2.2
            else:
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                bpy.ops.anim.keyframe_insert_menu(type="Scaling")
                bar.animation_data.action.fcurves[0].lock = True
                bar.animation_data.action.fcurves[2].lock = True

                bpy.ops.graph.sound_bake(filepath=audio_file, low=low, high=high,
                                         attack=attack_time, release=release_time)

                bar.animation_data.action.fcurves[1].lock = True

                low = high
                high = low * (a ** note_step)


            bar.active_material = scene.bz_material

            if scene.bz_use_sym:
                mirror_modifier = bar.modifiers.new(name="Mirror", type="MIRROR")
                mirror_modifier.mirror_object = bar_set_empty
                if not scene.bz_use_radial:
                    mirror_modifier.use_axis = (False, True, False)

            bar.select_set(False)

            progress = 100 * (count / bar_count)
            wm.progress_update(progress)
            
        bpy.context.area.type = area

        original_location = bar_set_empty.location[:]
        original_rotation = bar_set_empty.rotation_euler[:]
        original_scale = bar_set_empty.scale[:]
        bar_set_empty.location = (0.0, 0.0, 0.0)
        bar_set_empty.rotation_euler = (0.0, 0.0, 0.0)
        bar_set_empty.scale = (1.0, 1.0, 1.0)

        for thing in scene.collection.children[collection_name].objects:
            if not thing.parent and len(thing.children) == 0:
                thing.select_set(True)

        bar_set_empty.select_set(True)
        context.view_layer.objects.active = bar_set_empty
        bpy.ops.object.parent_set()

        bpy.ops.object.select_all(action="DESELECT")
        bar_set_empty.select_set(True)
        # bpy.context.view_layer.objects.active = bar_set_empty

        bar_set_empty.location = original_location
        bar_set_empty.rotation_euler = original_rotation
        bar_set_empty.scale = original_scale

        wm.progress_end()
        return {"FINISHED"}
