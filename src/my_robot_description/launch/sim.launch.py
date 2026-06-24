import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_my_robot_description = get_package_share_directory('my_robot_description')
    
    # Include the robot_state_publisher launch file, provided by our own package
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            pkg_my_robot_description, 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Include the Gazebo launch file
    # Ensure ros-humble-ros-ign or ros-humble-ros-gz is installed depending on your setup
    # Here we default to ros_gz_sim (modern name)
    try:
        pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
        gazebo = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': '-r empty.sdf'}.items()
        )
    except Exception:
        # Fallback for older ign names
        pkg_ros_ign_gazebo = get_package_share_directory('ros_ign_gazebo')
        gazebo = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py')
            ),
            launch_arguments={'ign_args': '-r empty.sdf'}.items()
        )

    # Run the spawner node from ros_gz_sim / ros_ign_gazebo
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-topic', 'robot_description',
                                   '-name', 'my_robot'],
                        output='screen')

    # Optionally add a bridge for the camera here
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/zed/zed_node/rgb/image_rect_color@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/zed/zed_node/imu/data@sensor_msgs/msg/Imu[ignition.msgs.IMU'
        ],
        output='screen'
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        bridge
    ])
