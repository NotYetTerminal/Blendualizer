import bpy

class BLENDUALIZER_OT_remove_audio_from_vse(bpy.types.Operator):
    bl_idname = "sequencerextra.bz_audio_remove"
    bl_label = "Remove Audio"
    bl_description = "Adds the audio file to the VSE"

    @classmethod
    def poll(self, context):
        scene = context.scene
        if scene.bz_audio_file == "":
            return False
        else:
            return True

    def execute(self, context):

        scene = context.scene

        if not scene.sequence_editor:
            return {"FINISHED"}

        audiofile_name = bpy.path.abspath(scene.bz_audio_file).split('\\')[-1].split('.')[0]

        for seqs in scene.sequence_editor.sequences:
            if seqs.type == "SOUND" and seqs.sound.name.split('.')[0] == audiofile_name:
                seqs.select = True
                bpy.ops.sequencer.delete()

                self.report({"INFO"}, "Sound deleted.")

                return {"FINISHED"}

        if len(scene.sequence_editor.sequences) != 0:
            self.report({"WARNING"}, "Sound not found. (Name could contain foreign characters)")

        return {"FINISHED"}
