import os

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='paveway_vision', 
            executable='video_publisher',
            name='video_publisher',
            output='screen'
        ),
        Node(
            package='paveway_vision', 
            executable='yolov8',
            name='pothole_detector',
            output='screen'
        ),
        # Node(
        #     package='paveway_vision',
        #     executable='potholes_map',
        #     name='pothole_visualizer',
        #     output='screen'
        # )
    ])
