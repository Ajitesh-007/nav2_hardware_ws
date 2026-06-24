import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_my_robot_navigation = get_package_share_directory('my_robot_navigation')
    
    use_sim_time = 'true'
    nav2_params_file = os.path.join(pkg_my_robot_navigation, 'config', 'nav2_params.yaml')

    # Launch Nav2
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file
        }.items()
    )

    # Launch RTAB-Map
    rtabmap = Node(
        package='rtabmap_slam', executable='rtabmap', output='screen',
        parameters=[{
            'frame_id': 'base_link',
            'subscribe_depth': True,
            'subscribe_odom_info': False,
            'approx_sync': True,
            'wait_for_transform': 0.2,
            'use_sim_time': True,
        }],
        remappings=[
            ('odom', '/zed/zed_node/odom'),
            ('rgb/image', '/zed/zed_node/rgb/image_rect_color'),
            ('rgb/camera_info', '/zed/zed_node/rgb/camera_info'),
            ('depth/image', '/zed/zed_node/depth/depth_registered')
        ]
    )

    return LaunchDescription([
        nav2,
        rtabmap
    ])
