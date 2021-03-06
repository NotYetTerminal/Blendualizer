import bpy
import math

class BLENDUALIZER_OT_generate_visualizer(bpy.types.Operator):
    bl_idname = "object.blz_generate"
    bl_label = "(re)Generate Visualizer"
    bl_description = "Generates visualizer bars and animation"

    base_size = 2

    # first list is vertices
    # second is the faces
    data_dict = {'RECTANGLE': ([(-1, 2, 0), (1, 2, 0), (1, 0, 0), (-1, 0, 0)],
                               [(0, 1, 2, 3)]),
                 'TRIANGLE': ([(0, 2, 0), (1, 0, 0), (-1, 0, 0)],
                             [(0, 1, 2)]),
                 'CUBOID': ([(-1, 2, -1), (1, 2, -1), (1, 0, -1), (-1, 0, -1), (-1, 2, 1), (1, 2, 1), (1, 0, 1), (-1, 0, 1)],
                            [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)]),
                 'PYRAMID': ([(0, 2, 0), (-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)],
                             [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 2, 3, 4)])}

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.blz_audio_file != "" or scene.blz_preview_mode:
            return True
        else:
            return False

    def execute(self, context):
        scene = context.scene
        scene.frame_current = 1
        self.audio_file = bpy.path.abspath(scene.blz_audio_file)
        
        self.attack_time = scene.blz_attack_time
        self.release_time = scene.blz_release_time
        vis_object_count = scene.blz_vis_object_count
        self.use_radial = scene.blz_use_radial

        if not scene.blz_use_custom_mesh and scene.blz_vis_shape not in self.data_dict.keys():
            self.use_curve = True
        else:
            self.use_curve = False

        bar_width = scene.blz_bar_width / self.base_size
        bar_depth = scene.blz_bar_depth / self.base_size
        self.amplitude = scene.blz_amplitude / self.base_size
        self.spacing = scene.blz_spacing + scene.blz_bar_width


        if not self.use_curve:
            curve_buffer_front = 0
            curve_buffer_end = 0
            curve_buffer_between = 0
        else:
            curve_buffer_front = scene.blz_curve_buffer_front
            curve_buffer_front_strength = scene.blz_curve_buffer_front_strength
            curve_buffer_end = scene.blz_curve_buffer_end
            curve_buffer_end_strength = scene.blz_curve_buffer_end_strength
            curve_buffer_between = scene.blz_curve_buffer_between
        
        if scene.blz_flip_direction:
            self.flip_direction = 1
        else:
            self.flip_direction = -1

        vis_object_with_buffer_between = vis_object_count * (curve_buffer_between + 1) - curve_buffer_between
        self.total_object_count = vis_object_with_buffer_between + curve_buffer_end + curve_buffer_front
        self.line_start = self.flip_direction * (((self.total_object_count * self.spacing) / 2) - (self.spacing / 2))
        ''' + (self.spacing / 2))'''
        print(self.line_start)
        print(self.flip_direction)
        print(self.total_object_count * self.spacing)

        preview_coef = 8 * math.pi / vis_object_count
        preview_mode = scene.blz_preview_mode


        if self.use_radial:
            self.radius = scene.blz_radius
            arc_angle_deg = scene.blz_arc_angle
            arc_center_deg = scene.blz_arc_center_offset + 180 + (90 * self.flip_direction)
            self.arc_direction = self.flip_direction

            self.arc_angle = arc_angle_deg / 360 * 2 * math.pi
            self.arc_center = -arc_center_deg / 360 * 2 * math.pi
            self.arc_start = self.arc_center - (self.arc_direction * self.arc_angle / 2)

        note_step = 120.0 / vis_object_count
        a = 2 ** (1.0 / scene.blz_freq_step)
        low = 0.0
        high = scene.blz_start_freq

        bpy.ops.object.select_all(action="DESELECT")
        self.collection_name = "Bizualizer Collection"
        collection_present = bpy.data.collections.get(self.collection_name)

        if collection_present:
            empty_present = collection_present.objects.get(scene.blz_custom_name)
            if empty_present:
                for vis_object in empty_present.children:
                    vis_object.select_set(True)
                    for vis_object_child in vis_object.children:
                        vis_object_child.select_set(True)

                bpy.ops.object.delete()
        else:
            scene.collection.children.link(bpy.data.collections.new(self.collection_name))

        bar_set_empty = scene.collection.children[self.collection_name].objects.get(scene.blz_custom_name)
        if not bar_set_empty:
            bar_set_empty = bpy.data.objects.new(scene.blz_custom_name, None)
            scene.collection.children[self.collection_name].objects.link(bar_set_empty)


        if self.use_curve:
            curve_data = bpy.data.curves.new(scene.blz_custom_name, 'CURVE')
            curve_data.dimensions= '3D'
            spline = curve_data.splines.new(type='NURBS')

            total_points = self.total_object_count - 1
            spline.points.add(total_points)

            curve_data.bevel_depth = 0.1
            curve_object = bpy.data.objects.new('Curve', curve_data)
            curve_object.active_material = scene.blz_material

            scene.collection.children[self.collection_name].objects.link(curve_object)
            curve_object.select_set(False)

            if self.use_radial and not scene.blz_use_sym:
                spline.use_cyclic_u = True
                spline.use_cyclic_v = True

            else:
                spline.use_endpoint_u = True
                spline.use_endpoint_v = True

            if preview_mode:
                vis_object_list = []
            
            
            self.makeBuffers(context, "Buffer Front ", 0, curve_buffer_front, spline, curve_object, curve_buffer_front_strength, True)
            up_till_now = curve_buffer_front + vis_object_with_buffer_between
            self.makeBuffers(context, "Buffer End ", up_till_now, curve_buffer_end + up_till_now, spline, curve_object, curve_buffer_end_strength, False)


        area = bpy.context.area.type
        bpy.context.area.type = 'GRAPH_EDITOR'

        wm = context.window_manager
        wm.progress_begin(0, 100.0)

        for count in range(0, vis_object_with_buffer_between):
            
            name = str(round(low, 1)) + ' | ' + str(round(high, 1))
            location, angle = self.getVisObjectLocationAndRotation(scene, count + curve_buffer_front)
            
            if self.use_curve and curve_buffer_between != 0 and (count + curve_buffer_between + 1) % (curve_buffer_between + 1) != 0:
                spline.points[count + curve_buffer_front].co = [*location, scene.blz_curve_buffer_between_strength]
                continue

            if not self.use_curve:
                vis_object = self.makeVisObject(scene, name)

                vis_object.rotation_euler[2] = angle
                vis_object.scale.x = bar_width
                vis_object.scale.y = self.amplitude
                vis_object.scale.z = bar_depth
                vis_object.location = location

            else:
                vis_object = self.makeVisObject(scene, name, context)
                
                vis_object.parent.rotation_euler[2] = angle
                spline.points[count + curve_buffer_front].co = [*location, 1]

                hook_modifier = curve_object.modifiers.new(name=name, type="HOOK")
                hook_modifier.object = vis_object
                hook_modifier.vertex_indices_set([count + curve_buffer_front])
            
            
            if preview_mode:
                if not self.use_curve:
                    vis_object.scale.y = self.amplitude * (math.cos(count * preview_coef) + 1.2) / 2.2
                else:
                    vis_object_list.append(vis_object)
                    vis_object.location.y = (math.cos(count * preview_coef) + 1.2) / 2.2
            else:
                self.bakeSound(vis_object, low, high)
            
            if not self.use_curve:
                vis_object.active_material = scene.blz_material

            if scene.blz_use_sym and not self.use_curve:
                mirror_modifier = vis_object.modifiers.new(name="Mirror", type="MIRROR")
                mirror_modifier.mirror_object = bar_set_empty
                mirror_modifier.use_axis = (False, True, False)

            low = high
            high = low * (a ** note_step)

            if low >= 100000:
                break

            progress = 100 * (count / vis_object_with_buffer_between)
            wm.progress_update(progress)
        

        if scene.blz_use_sym and self.use_curve:
            mirror_modifier = curve_object.modifiers.new(name="Mirror", type="MIRROR")
            mirror_modifier.mirror_object = bar_set_empty
            if not scene.blz_use_radial:
                mirror_modifier.use_axis = (False, True, False)
        
        if self.use_curve:
            if preview_mode:
                location_list = []
                for vis_object in vis_object_list:
                    location_list.append([*vis_object.location])
                    vis_object.location = (0, 0, 0)

            curve_object.select_set(True)
            curve_object.active_material = scene.blz_material
            bpy.context.view_layer.objects.active = curve_object
            bpy.ops.object.mode_set(mode='EDIT')

            for hook in curve_object.modifiers:
                if hook.type == 'HOOK':
                    bpy.ops.object.hook_reset(modifier=hook.name)
                
            bpy.ops.object.mode_set(mode='OBJECT')
            curve_object.select_set(False)

            if preview_mode:
                index = 0
                for vis_object in vis_object_list:
                    vis_object.location = location_list[index]
                    index += 1

            
        bpy.context.area.type = area

        original_location = bar_set_empty.location[:]
        original_rotation = bar_set_empty.rotation_euler[:]
        original_scale = bar_set_empty.scale[:]
        bar_set_empty.location = (0, 0, 0)
        bar_set_empty.rotation_euler = (0, 0, 0)
        bar_set_empty.scale = (1, 1, 1)

        for vis_object in scene.collection.children[self.collection_name].objects:
            if not vis_object.parent and (len(vis_object.children) == 0 or vis_object.name[0:13] == "Scaling Empty") and vis_object != bar_set_empty:
                vis_object.select_set(True)

        bar_set_empty.select_set(True)
        context.view_layer.objects.active = bar_set_empty
        bpy.ops.object.parent_set()

        bpy.ops.object.select_all(action="DESELECT")
        bar_set_empty.select_set(True)

        bar_set_empty.location = original_location
        bar_set_empty.rotation_euler = original_rotation
        bar_set_empty.scale = original_scale

        wm.progress_end()
        return {"FINISHED"}


    def makeBuffers(self, context, buffer_name, start, end, spline, curve_object, buffer_strength, is_front):        
        for count in range(start, end):
            
            name = buffer_name + str(count - start)

            vis_object = self.makeVisObject(context.scene, name, context)
            location, angle = self.getVisObjectLocationAndRotation(context.scene, count)
            
            vis_object.parent.rotation_euler[2] = angle
            if is_front:
                spline.points[count].co = [*location, 1 - ((count - start) / (end - start - 1)) * (1 - buffer_strength)] # start is 0
            else:
                spline.points[count].co = [*location, buffer_strength + ((count - start) / (end - start - 1)) * (1 - buffer_strength)]

            hook_modifier = curve_object.modifiers.new(name=name, type="HOOK")
            hook_modifier.object = vis_object
            hook_modifier.vertex_indices_set([count])


    def makeVisObject(self, scene, name, context = None):
        if not scene.blz_use_custom_mesh:
            if not self.use_curve:
                vertices, faces = self.data_dict[scene.blz_vis_shape]

                mesh = bpy.data.meshes.new(name)
                mesh.from_pydata(vertices, [], faces)
                mesh.update()
                vis_object = bpy.data.objects.new(name, mesh)
                scene.collection.children[self.collection_name].objects.link(vis_object)

            else:
                vis_object_empty = bpy.data.objects.new("Scaling Empty " + name, None)
                vis_object_empty.scale = (1, 1.0 / self.amplitude, 1)
                scene.collection.children[self.collection_name].objects.link(vis_object_empty)
                
                vis_object = bpy.data.objects.new(name, None)
                vis_object.scale = (1, 1.0 / self.amplitude, 1)
                scene.collection.children[self.collection_name].objects.link(vis_object)

                vis_object.select_set(True)
                vis_object_empty.select_set(True)
                context.view_layer.objects.active = vis_object_empty
                bpy.ops.object.parent_set()

                vis_object_empty.scale = (1, 1, 1)
                vis_object.select_set(False)
                vis_object_empty.select_set(False)
        else:
            vis_object = bpy.data.objects.new(name, scene.blz_custom_mesh.copy())
            scene.collection.children[self.collection_name].objects.link(vis_object)

        return vis_object


    def getVisObjectLocationAndRotation(self, scene, count):
        location = [0.0, 0.0, 0.0]
        angle = 0

        if scene.blz_use_radial:
            angle = self.arc_direction * ((count + 0.5) / self.total_object_count) * self.arc_angle
            if scene.blz_use_sym:
                angle /= 2
            
            angle += self.arc_start

            location[0] = -math.sin(angle) * self.radius
            location[1] = math.cos(angle) * self.radius

        else:
            location[0] = -(count * self.spacing * self.flip_direction) + self.line_start
        
        return location, angle
    

    def bakeSound(self, vis_object, low, high):
        vis_object.select_set(True)
        bpy.context.view_layer.objects.active = vis_object

        if not self.use_curve:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.anim.keyframe_insert_menu(type="Scaling")
        else:
            bpy.ops.anim.keyframe_insert_menu(type="Location")

        vis_object.animation_data.action.fcurves[0].lock = True
        vis_object.animation_data.action.fcurves[2].lock = True

        bpy.ops.graph.sound_bake(filepath=self.audio_file, low=low, high=high,
                                 attack=self.attack_time, release=self.release_time)

        vis_object.select_set(False)
