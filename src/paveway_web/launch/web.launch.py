from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    

    return LaunchDescription([
        Node(
            package='paveway_web', 
            executable='battery_publisher',
            name='battery_publisher',
            output='screen'
        ),
        Node(
            package='paveway_web', 
            executable='distance_publisher',
            name='distance_publisher',
            output='screen'
        ),
        Node(
            package='paveway_web', 
            executable='time_publisher',
            name='time_publisher',
            output='screen'
        ),
         Node(
            package='paveway_web', 
            executable='count_publisher',
            name='count_publisher',
            output='screen'
        ),
        
        ExecuteProcess(
            cmd=['ros2', 'launch', 'rosbridge_server', 'rosbridge_websocket_launch.xml'],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'run', 'web_video_server', 'web_video_server'],
            output='screen'
        )
    ])
