import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_my_robot_description = get_package_share_directory('my_robot_description')

    # ── Launch Arguments ────────────────────────────────────────────────────────
    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyUSB0',
        description='USB serial port for ESP32 (e.g. /dev/ttyUSB0 or /dev/ttyACM0)'
    )

    # ── Read URDF ───────────────────────────────────────────────────────────────
    # robot.urdf uses xacro macros (ZED camera), so we must process it with xacro.
    # The result is raw XML — ParameterValue(value_type=str) prevents launch from
    # trying to parse it as YAML (which would fail on the angle brackets).
    urdf_file = os.path.join(pkg_my_robot_description, 'urdf', 'robot.urdf')
    from launch.substitutions import Command
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    # Allow overriding the serial port from CLI without editing the URDF
    serial_port = LaunchConfiguration('serial_port')

    # ── 1. Robot State Publisher ────────────────────────────────────────────────
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False,
        }],
    )

    # ── 2. ros2_control Controller Manager ─────────────────────────────────────
    controller_params_file = os.path.join(
        pkg_my_robot_description, 'config', 'controllers.yaml'
    )

    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            controller_params_file,
        ],
        output='both',
        # Override serial port from launch arg if needed (passed via env workaround)
        # The serial port is read from the URDF <param> tag by the hardware plugin.
        # To change it without editing the URDF, set the env var or edit the URDF param.
    )

    # ── 3. Spawn joint_state_broadcaster ───────────────────────────────────────
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager',
        ],
    )

    # ── 4. Spawn diff_drive_controller (after joint_state_broadcaster) ─────────
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_controller',
            '--controller-manager', '/controller_manager',
        ],
    )

    # Delay the diff_drive_controller spawner to avoid ros2_control race conditions
    delay_diff_drive = TimerAction(
        period=3.0,
        actions=[diff_drive_spawner],
    )

    return LaunchDescription([
        serial_port_arg,
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        delay_diff_drive,
    ])
