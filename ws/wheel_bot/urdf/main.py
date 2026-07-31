import time

import pybullet as p
import pybullet_data

physics = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)

p.loadURDF("plane.urdf")

robot = p.loadURDF("wheel_bot.urdf")

while 1:
    p.stepSimulation()

    time.sleep(1.0/240.)


