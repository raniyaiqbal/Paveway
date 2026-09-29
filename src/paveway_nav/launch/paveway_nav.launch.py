"""Nav2 (AMCL + planners) on a saved map, plus RViz.

  ros2 launch paveway_nav paveway_nav.launch.py                               # simulation
  ros2 launch paveway_nav paveway_nav.launch.py use_sim_time:=false \\
      map:=$(ros2 pkg prefix paveway_nav)/share/paveway_nav/maps/real_map.yaml  # real robot
"""
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

    model = os.environ.get('TURTLEBOT3_MODEL', 'burger')
    default_map = os.path.join(pkg_paveway_nav, 'maps', f'{model}.yaml')
    default_params = os.path.join(pkg_paveway_nav, 'params', f'{model}.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=default_map,
                              description='Map YAML (maps/real_map.yaml for the real robot)'),
        DeclareLaunchArgument('params_file', default_value=default_params),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_nav2, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': map_yaml,
                'use_sim_time': use_sim_time,
                'params_file': params_file,
            }.items()
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),
    ])
