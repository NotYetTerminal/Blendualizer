import bpy
import math

class RENDER_OT_align_camera(bpy.types.Operator):

    bl_idname = "object.bz_align_camera"
    bl_label = "Align Camera"
    bl_description = "Aligns camera to bizualizer bars"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.camera:
            return True
        return False


    def execute(self, context):
        scene = context.scene

        camera_type = scene.bz_cam_alignment.split("_")[0]
        alignment = scene.bz_cam_alignment.split("_", 1)[1]
        
        if camera_type == "2D":
            self.set2DCamera(scene, alignment)
        elif camera_type == "3D":
            self.set3DCamera(scene, alignment)
        
        return {"FINISHED"}


    def set2DCamera(self, scene, alignment):
        camera = scene.camera

        bpy.data.cameras[camera.data.name].type = 'ORTHO'

        rotated = False
        inverted = False

        if alignment == "top":
            inverted = True
        elif alignment == "left":
            rotated = True
            inverted = True
        elif alignment == "right":
            rotated = True

        rectangle_size = self.getRectangleSize(scene, rotated)
        rectangle_width = rectangle_size["width"]
        rectangle_height = rectangle_size["height"]

        bpy.data.cameras[camera.data.name].ortho_scale = rectangle_width

        loc = camera.location
        rot = [0.0, 0.0, 0.0]
        loc[2] = 5.0

        if inverted:
            loc[2] = -5.0
            rot[0] = math.pi


        if alignment == "bottom":
            loc[0] = 0.0
            loc[1] = rectangle_height / 2

        elif alignment == "center":
            loc[0] = 0.0
            loc[1] = 0.0

        elif alignment == "top":
            loc[0] = 0.0
            loc[1] = rectangle_height / 2

        elif alignment == "left":
            loc[0] = 0.0
            loc[1] = rectangle_width / 2
            rot[2] = math.pi * 0.5

        elif alignment == "right":
            loc[0] = 0.0
            loc[1] = rectangle_width / 2
            rot[2] = math.pi * 1.5

        camera.location = loc
        camera.rotation_mode = 'XYZ'
        camera.rotation_euler = rot


    def set3DCamera(self, scene, alignment):
        camera = scene.camera

        bpy.data.cameras[camera.data.name].type = 'PERSP'

        bars_total_size = self.getBarsTotalSize(scene)
        
        res_x = scene.render.resolution_x
        res_y = scene.render.resolution_y

        loc = camera.location
        loc[2] = bars_total_size / 2

        if alignment == "bottom":
            rectangle_height = (bars_total_size / (res_x / res_y))
            loc[0] = 0.0
            loc[1] = rectangle_height / 2

        elif alignment == "center":
            loc[0] = 0.0
            loc[1] = 0.0

        camera.location = loc
        camera.rotation_mode = 'XYZ'
        camera.rotation_euler = [0.0, 0.0, 0.0]


    def getBarsTotalSize(self, scene):
        bar_count = scene.bz_bar_count
        spacing = scene.bz_spacing + scene.bz_bar_width
        
        extra_cushion = scene.bz_spacing
        bars_total_size = (bar_count * spacing) + extra_cushion

        return bars_total_size


    def getRectangleSize(self, scene, rotated):
        res_x = scene.render.resolution_x
        res_y = scene.render.resolution_y

        bars_total_size = self.getBarsTotalSize(scene)

        if rotated:
            width = (bars_total_size / (res_y / res_x))
            height = bars_total_size
        else:
            width = bars_total_size
            height = (bars_total_size / (res_x / res_y))

        return {"width": width, "height": height}
