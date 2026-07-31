import time
import numpy as np
import pybullet as p
import pybullet_data

####CUSTOM_LIBS
import wheel_logic

physics = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

p.loadURDF("plane.urdf")

robot = p.loadURDF("wheel_bot.urdf")

num_joints = p.getNumJoints(robot)
joint_name_idx = dict()

for i in range(num_joints):
    joint_info = p.getJointInfo(robot, i)
    joint_name = joint_info[1].decode("utf-8")
    joint_type = joint_info[2]

    if joint_type != p.JOINT_FIXED:
        joint_name_idx[joint_name] = i
print(joint_name_idx)


movement_logic = wheel_logic.WheelLogic(robot, joint_name_idx)
movement_logic.set_debug_params()


while 1:

    base_pos, base_orn = p.getBasePositionAndOrientation(robot)
    euler_orn = p.getEulerFromQuaternion(base_orn)
    base_z_rotation = euler_orn[2]
    rot_matrix = np.array(p.getMatrixFromQuaternion(base_orn)).reshape(3, 3)

    movement_logic.forward_movement()




    p.stepSimulation()

    time.sleep(1.0/240.)


