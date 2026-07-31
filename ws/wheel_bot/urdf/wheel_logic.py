import pybullet as p

class WheelLogic:
    def __init__(self, robot, joint_data, RIGHT_WHEEL_VEL = 5, LEFT_WHEEL_VEL = 5) -> None:
        self.joint_data = joint_data
        self.right_wheel_vel = RIGHT_WHEEL_VEL
        self.left_wheel_vel = LEFT_WHEEL_VEL
        self.robot = robot

        self.front_left_wheel = self.joint_data.get("front_left_joint")
        self.rear_left_wheel = self.joint_data.get("back_left_joint")
        self.front_right_wheel = self.joint_data.get("front_right_joint")
        self.rear_right_wheel = self.joint_data.get("back_right_joint")

    def set_debug_params(self):
        self.right_vel_slider = p.addUserDebugParameter("RIGHT_VEL_SILDER", -10, 10, self.right_wheel_vel)
        self.left_vel_slider = p.addUserDebugParameter("LEFT_VEL_SILDER", -10, 10, self.left_wheel_vel)

    def forward_movement(self):
        p.setJointMotorControl2(self.robot, self.front_left_wheel, p.VELOCITY_CONTROL, targetVelocity = self.left_wheel_vel, force = 100)
        p.setJointMotorControl2(self.robot, self.rear_left_wheel, p.VELOCITY_CONTROL, targetVelocity = self.left_wheel_vel, force = 100)

        p.setJointMotorControl2(self.robot, self.front_right_wheel, p.VELOCITY_CONTROL, targetVelocity = self.right_wheel_vel, force = 100)
        p.setJointMotorControl2(self.robot, self.rear_right_wheel, p.VELOCITY_CONTROL, targetVelocity = self.right_wheel_vel, force = 100)

