from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
import xacro
import os
from ament_index_python.packages import get_package_share_directory

from launch.actions import TimerAction


def generate_launch_description():
    share_dir = get_package_share_directory('four_wheel_bot_description')

    xacro_file = os.path.join(share_dir, 'urdf', 'four_wheel_bot.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()

    rviz_config_file = os.path.join(share_dir, 'config', 'display.rviz')

    gui_arg = DeclareLaunchArgument(
        name='gui',
        default_value='True'
    )

    show_gui = LaunchConfiguration('gui')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_urdf}
        ]
    )

    joint_state_publisher_node = Node(
        condition=UnlessCondition(show_gui),
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    joint_state_publisher_gui_node = Node(
        condition=IfCondition(show_gui),
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        output='screen'
    )
# -------------------------
    controllers_file = os.path.join(
        share_dir,
        "config",
        "my_configs.yaml"
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_urdf},
            controllers_file,
        ],
        output="screen",
    )

    # -------------------------
    # Joint State Broadcaster
    # -------------------------
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager'
        ]
    )

    # -------------------------
    # Diff Drive Controller
    # -------------------------
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_cont',
            '--controller-manager',
            '/controller_manager'
        ]
    )

    # Delay diff controller so hardware is ready
    delayed_diff_drive = TimerAction(
        period=2.0,
        actions=[diff_drive_spawner]
    )

    return LaunchDescription([
        gui_arg,
        robot_state_publisher_node,
        controller_manager,

        joint_state_broadcaster_spawner,
        delayed_diff_drive,
        # joint_state_publisher_node,
        # joint_state_publisher_gui_node,
        rviz_node
    ])
