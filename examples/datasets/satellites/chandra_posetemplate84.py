import blenderproc as bproc
import argparse
import numpy as np
import os

import blenderproc.python.camera.CameraUtility as CameraUtility

parser = argparse.ArgumentParser()
args = parser.parse_args()
args.output_dir = "examples/datasets/satellites/output"
args.bop_dataset_name = "chandra"
bproc.init()

'''setup camera'''
cam = {
    'im_size': (1024, 1024),
    'K': np.array([[300.0, 0.0, 512.0],
                   [0.0, 300.0, 512.0],
                   [0.0, 0.0, 1.0]])
}
CameraUtility.set_intrinsics_from_K_matrix(cam['K'], cam['im_size'][0], cam['im_size'][1])

'''setup light'''
light = bproc.types.Light()
light.set_type("POINT")
light.set_energy(1000)
light.set_location([0.0, 0.0, 0.0])

'''import object_1'''
objs_1 = bproc.loader.load_blend("resources/satellites/Chandra/chandra.blend")
target_obj = []
for obj in objs_1:
    if obj.get_name() == "_root":
        obj.blender_obj['category_id'] = 0
        target_obj.append(obj)
poi = bproc.object.compute_poi(bproc.filter.all_with_type(objs_1, bproc.types.MeshObject))
print(poi)

'''read pose_1 from file'''
pose_path_1 = "resources/satellites/pose_template84.txt"
cam2model_1 = []
with open(pose_path_1, "r") as f:
    data = f.readline()
    for line in f.readlines():
        line = np.array(line.split(), dtype=float)
        matrix = np.eye(4)
        matrix[0, 0:3] = line[0:3]
        matrix[1, 0:3] = line[3:6]
        matrix[2, 0:3] = line[6:9]
        matrix[0:3, 3] = line[9:12]
        matrix[1, 3] = matrix[1, 3] + 0.0
        matrix[2, 3] = matrix[2, 3] + 0.0
        matrix[2, 3] = matrix[2, 3] + 15.0
        cam2model_matrix = np.linalg.inv(matrix)
        coordinate_change_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                             [0.0, 1.0, 0.0, 0.0],
                                             [0.0, 0.0, -1.0, 0.0],
                                             [0.0, 0.0, 0.0, 1.0]])
        cam2model_matrix = cam2model_matrix @ coordinate_change_matrix
        cam2model_1.append(cam2model_matrix)

''' enable depth output '''
bproc.renderer.enable_depth_output(activate_antialiasing=False)
''' loop to generate dataset '''
for i in range(len(cam2model_1)):
    for obj in objs_1:
        if obj.get_name() == "_root":
            obj.set_local2world_mat(np.linalg.inv(cam2model_1[i]))
    ''' start rendering '''
    bproc.camera.add_camera_pose(np.eye(4), frame=0)
    data = bproc.renderer.render()
    bproc.writer.write_bop(os.path.join(args.output_dir, 'bop_data_test', 'chandra_posetemplate84'),
                           target_objects=target_obj,
                           depths=data["depth"],
                           colors=data["colors"],
                           color_file_format="JPEG")


