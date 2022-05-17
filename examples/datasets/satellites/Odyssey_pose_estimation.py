import blenderproc as bproc
import argparse
import numpy as np
import os

import blenderproc.python.camera.CameraUtility as CameraUtility

parser = argparse.ArgumentParser()
args = parser.parse_args()
args.path = "resources/satellites/Odyssey/Odyssey.blend"
args.output_dir = "examples/datasets/satellites/output"
args.bop_dataset_name = "odyssey"
bproc.init()

objs = bproc.loader.load_blend(args.path)
target_obj = []
for obj in objs:
    if obj.get_name() == "_root":
        obj.blender_obj['category_id'] = 0
        target_obj.append(obj)

cam = {
    'im_size': (1024, 1024),
    'K': np.array([[300.0, 0.0, 512.0],
                   [0.0, 300.0, 512.0],
                   [0.0, 0.0, 1.0]])
}

CameraUtility.set_intrinsics_from_K_matrix(cam['K'], cam['im_size'][0], cam['im_size'][1])

light = bproc.types.Light()
light.set_type("POINT")
light.set_energy(1000)
poi = bproc.object.compute_poi(bproc.filter.all_with_type(objs, bproc.types.MeshObject))
light.set_location(bproc.sampler.sphere(poi, radius=10, mode="SURFACE"))

pose_path = "resources/satellites/poses_first.txt"
bproc.renderer.enable_depth_output(activate_antialiasing=False)
with open(pose_path, "r") as f:
    data = f.readline()
    for line in f.readlines():
        line = np.array(line.split(), dtype=float)
        matrix = np.eye(4)
        matrix[0, 0:3] = line[0:3]
        matrix[1, 0:3] = line[3:6]
        matrix[2, 0:3] = line[6:9]
        matrix[0:3, 3] = line[9:12]/10.
        cam2world_matrix = np.linalg.inv(matrix)
        coordinate_change_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                             [0.0, 1.0, 0.0, 0.0],
                                             [0.0, 0.0, -1.0, 0.0],
                                             [0.0, 0.0, 0.0, 1.0]])
        cam2world_matrix = cam2world_matrix @ coordinate_change_matrix
        bproc.camera.add_camera_pose(cam2world_matrix, frame=0)
        data = bproc.renderer.render()
        bproc.writer.write_bop(os.path.join(args.output_dir, 'bop_data_test', 'odyssey_pose_estimation'),
                               target_objects = target_obj,
                               depths=data["depth"],
                               colors=data["colors"],
                               color_file_format="JPEG")
