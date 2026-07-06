import xacro
import time
import os

import numpy as np
import matplotlib.pyplot as plt

import tempfile
import pybullet as p
import pybullet_data
## TODO: 
# make this script communicate via serial
# capture camera data -> for AI
# capture lidar data -> for SLAM
# move wheel
# make a gamefield
xacro_file = os.path.join("../four_wheel_bot_description/", 'urdf', 'four_wheel_bot.xacro')
robot_description_config = xacro.process_file(xacro_file)

urdf_path = os.path.join(tempfile.gettempdir(), "four_wheel_bot.urdf")

with open(urdf_path, "w") as f:
    f.write(robot_description_config.toprettyxml())

physics = p.connect(p.DIRECT)

p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

p.loadURDF("plane.urdf")

robot = p.loadURDF(
    urdf_path,
)
## WHEELS
FRONT_LEFT_JOINT = 0
BACK_LEFT_JOINT = 1
FRONT_RIGHT_JOINT = 2 
BACK_RIGHT_JOINT = 3 
CAMERA_SENSOR_JOINT = 4
LIDAR_SENSOR_JOINT = 5

num_joints = p.getNumJoints(robot)
for i in range(num_joints):
    info = p.getJointInfo(robot, i)
    print(i, info[1].decode())

def cont_left(velocity = 0):
    p.setJointMotorControl2(
            robot,
            FRONT_LEFT_JOINT,
            p.VELOCITY_CONTROL,
            targetVelocity = velocity,
            force = 20
            )
    p.setJointMotorControl2(
            robot,
            BACK_LEFT_JOINT,
            p.VELOCITY_CONTROL,
            targetVelocity = velocity,
            force = 20
            )

def cont_rigth(velocity = 0):
    p.setJointMotorControl2(
            robot,
            FRONT_RIGHT_JOINT,
            p.VELOCITY_CONTROL,
            targetVelocity = velocity,
            force = 20
            )
    p.setJointMotorControl2(
            robot,
            BACK_RIGHT_JOINT,
            p.VELOCITY_CONTROL,
            targetVelocity = velocity,
            force = 20
            )

while 1:
    p.stepSimulation()
    cont_left(10)
    cont_rigth()

    ## CAMERA

    state = p.getLinkState(
            robot,
            CAMERA_SENSOR_JOINT,
            computeForwardKinematics=True
            )
    cam_pos = state[4]
    cam_orn = state[5]

    rot = p.getMatrixFromQuaternion(cam_orn)
    forward = [rot[0], rot[3], rot[6]]
    up = [rot[2], rot[5], rot[8]]

    target = [
            cam_pos[0] + forward[0],
            cam_pos[1] + forward[1],
            cam_pos[2] + forward[2],
            ]

    view = p.computeViewMatrix(
            cam_pos,
            target,
            up
            )

    proj = p.computeProjectionMatrixFOV(
            fov = 60,
            aspect = 640/480,
            nearVal = 0.01,
            farVal = 20,
            )

    w, h, rgb, depth, seg = p.getCameraImage(
            640,
            480,
            view,
            proj,
            p.ER_BULLET_HARDWARE_OPENGL
            )

    rgb = np.reshape(rgb, (h, w, 4))
    rgb = rgb[:, :, :3]
    plt.imshow(rgb)
    plt.show()

    time.sleep(1.0/240.)
