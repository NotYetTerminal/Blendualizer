import bpy
import sys
import time

if __name__ == '__main__':
    data_file = sys.argv[-1]

    id = data_file.split('\\')[-1].split('.')[0]
    path = data_file.split('\\' + id + '.txt')[0]

    with open(data_file, 'r') as f:
        data = f.read().split(';')

    cube = bpy.data.objects['Cube']

    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube

    while (True):
        time.sleep(0.1)
        try:
            bpy.context.area.type = 'GRAPH_EDITOR'
            break
        except Exception as e:
            print(e)

    #bpy.context.area.type = 'GRAPH_EDITOR'

    bpy.ops.anim.keyframe_insert_menu(type="Scaling")
    cube.animation_data.action.fcurves[0].lock = True
    cube.animation_data.action.fcurves[2].lock = True

    bpy.ops.graph.sound_bake(filepath=data[0], low=data[1], high=data[2], attack=data[3], release=data[4])

    point_list = []
    for points in bpy.data.actions[0].fcurves[1].sampled_points:
        point_list.append(points.co[1])

    with open(path + '_b' + '\\' + id + '.txt', 'w') as f:
        f.write(';'.join(point_list))


