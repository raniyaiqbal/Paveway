import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_nav2 = get_package_share_directory('nav2_bringup')
    pkg_paveway_nav = get_package_share_directory('paveway_nav')

    rviz_config = os.path.join(pkg_nav2, 'rviz', 'nav2_default_view.rviz')

    TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']
    map_path = os.path.join(pkg_paveway_nav, 'maps', f'{TURTLEBOT3_MODEL}.yaml')
    param_path = os.path.join(pkg_paveway_nav, 'params', f'{TURTLEBOT3_MODEL}.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    return LaunchDescription([
       DeclareLaunchArgument(
            'map',
            default_value=map_path,
            description='Full path to map file'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=param_path,
            description='Full path to nav2 params file'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')
            ),
            launch_arguments={
                'map': map_path,
                'use_sim_time': use_sim_time,
                'params_file': param_path
            }.items()
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
            condition=IfCondition(LaunchConfiguration('use_rviz', default='true')))
    ])
