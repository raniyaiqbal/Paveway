from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    paveway_web_launch = os.path.join(
        get_package_share_directory('paveway_web'),
        'launch',
        'web.launch.py'
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(paveway_web_launch)
        ),
        ExecuteProcess(
            cmd=['ros2', 'run', 'turtlebot3_teleop', 'teleop_keyboard'],
            output='screen'
        )
    ])
