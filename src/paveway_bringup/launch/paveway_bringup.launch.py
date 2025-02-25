import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    set_turtlebot_model = SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger')

    paveway_nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('paveway_nav'), 'launch', 'paveway_nav.launch.py')
        ),
        launch_arguments={'physical_env': 'true'}.items()
    )
    
    paveway_web_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('paveway_web'), 'launch', 'paveway_web.launch')
        )
    )
    
    paveway_vision_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('paveway_vision'), 'launch', 'paveway_vision.launch.py')
        )
    )
    
    return LaunchDescription([
        set_turtlebot_model,
        paveway_nav_launch,
        paveway_web_launch,
        paveway_vision_launch
    ])