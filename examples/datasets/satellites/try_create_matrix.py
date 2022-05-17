import numpy as np
pose_path = "/home/lyl/git/BlenderProc/resources/satellites/poses_first.txt"
with open(pose_path, "r") as f:
    f.readline()
    for line in f.readlines():
        line = np.array(line.split(), dtype=float)
        matrix = np.eye(4)
        matrix[0, 0:3] = line[0:3]
        matrix[1, 0:3] = line[3:6]
        matrix[2, 0:3] = line[6:9]
        matrix[0:3, 3] = line[9:12] / 1000.0
        cam2world_matrix = np.linalg.inv(matrix)