import bpy

class BLENDUALIZER_OT_audio_to_vse(bpy.types.Operator):
    bl_idname = "sequencerextra.blz_audio_to_sequencer"
    bl_label = "Add Audio to VSE"
    bl_description = "Adds the audio file to the VSE"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.blz_audio_file == "":
            return False
        else:
            return True

    def execute(self, context):
        bpy.ops.sequencerextra.blz_audio_remove()

        scene = context.scene
        audiofile = bpy.path.abspath(scene.blz_audio_file)
        name = audiofile.split('\\')[-1]
        chan = scene.blz_audio_channel
        start = 1
        if not scene.sequence_editor:
            scene.sequence_editor_create()

        scene.sequence_editor.sequences.new_sound(
            "blz_" + name, audiofile, chan, start)

        frame_start = 300000
        frame_end = -300000
        for strip in scene.sequence_editor.sequences:
            try:
                if strip.frame_final_start < frame_start:
                    frame_start = strip.frame_final_start
                if strip.frame_final_end > frame_end:
                    frame_end = strip.frame_final_end - 1
            except AttributeError:
                pass

        if frame_start != 300000:
            scene.frame_start = frame_start
        if frame_end != -300000:
            scene.frame_end = frame_end

        return {"FINISHED"}
