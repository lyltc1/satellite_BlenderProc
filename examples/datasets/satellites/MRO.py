import blenderproc as bproc
import argparse
import numpy as np
import os

import blenderproc.python.camera.CameraUtility as CameraUtility

# import debugpy
# debugpy.listen(5678)
# debugpy.wait_for_client()

parser = argparse.ArgumentParser()
# parser.add_argument('path', default="resources/satellites/MRO/MRO.blend")
# parser.add_argument('output_dir', default="examples/datasets/satellites/output")
args = parser.parse_args()
args.path = "resources/satellites/MRO/MRO.blend"
args.output_dir = "examples/datasets/satellites/output"
args.bop_dataset_name = "MRO"
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

bproc.renderer.enable_depth_output(activate_antialiasing=False)
for j in range(200):
    for i in range(5):
        # define a light and set its location and energy level
        light.set_location(bproc.sampler.sphere([0, 0, 0], radius=10, mode="SURFACE"))

        poi = bproc.object.compute_poi(bproc.filter.all_with_type(objs, bproc.types.MeshObject))
        poi = poi + bproc.sampler.sphere([0, 0, 0], radius=10, mode="INTERIOR")

        radius = np.random.uniform(low=8.0, high=30.0)
        location = bproc.sampler.sphere([0, 0, 0], radius=radius, mode="SURFACE")
        rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location,
                                                                 inplane_rot=np.random.uniform(-3.14159, 3.14159))
        cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
        bproc.camera.add_camera_pose(cam2world_matrix, frame=i)

    data = bproc.renderer.render()
    seg_data = bproc.renderer.render_segmap(map_by = ["instance", "class", "cp_bop_dataset_name"],
                                            default_values = {"class": 0, "cp_bop_dataset_name": None})

    bproc.writer.write_bop(os.path.join(args.output_dir, 'bop_data_test', 'MRO'),
                           target_objects = target_obj,
                           depths=data["depth"],
                           colors=data["colors"],
                           color_file_format="JPEG")
