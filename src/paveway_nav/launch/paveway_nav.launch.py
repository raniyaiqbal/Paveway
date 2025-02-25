import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_nav2 = get_package_share_directory('nav2_bringup')
    pkg_paveway_nav = get_package_share_directory('paveway_nav')

    rviz_config = os.path.join(pkg_nav2, 'rviz', 'nav2_default_view.rviz')

    TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']
    default_map_path = os.path.join(pkg_paveway_nav, 'maps', f'{TURTLEBOT3_MODEL}.yaml')
    real_map_path = os.path.join(pkg_paveway_nav, 'maps', 'real_map.pgm')
    param_path = os.path.join(pkg_paveway_nav, 'params', f'{TURTLEBOT3_MODEL}.yaml')

    physical_env = LaunchConfiguration('physical_env', default='false')

    return LaunchDescription([
        DeclareLaunchArgument(
            'physical_env',
            default_value='false',
            description='Set to true for physical environment'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
            ),
            launch_arguments={
                'map': real_map_path if physical_env == 'true' else default_map_path,
                'use_sim_time': 'false' if physical_env == 'true' else 'true',
                'params_file': param_path
            }.items()
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': 'false' if physical_env == 'true' else 'true'}],
            output='screen')
    ])
