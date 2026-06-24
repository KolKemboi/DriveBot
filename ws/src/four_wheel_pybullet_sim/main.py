import xacro
import time
import os

import tempfile
import pybullet as p
import pybullet_data

xacro_file = os.path.join("../four_wheel_bot_description/", 'urdf', 'four_wheel_bot.xacro')
robot_description_config = xacro.process_file(xacro_file)

urdf_path = os.path.join(tempfile.gettempdir(), "four_wheel_bot.urdf")

with open(urdf_path, "w") as f:
    f.write(robot_description_config.toprettyxml())

physics = p.connect(p.GUI)

p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

p.loadURDF("plane.urdf")

robot = p.loadURDF(
    urdf_path,
)

while 1:
    p.stepSimulation()
    time.sleep(1.0/240.)
