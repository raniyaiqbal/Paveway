import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.actions import TimerAction, DeclareLaunchArgument
from launch.conditions import IfCondition

def generate_launch_description():
    launch_file_dir = os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    TURTLEBOT3_MODEL = os.environ.get('TURTLEBOT3_MODEL', 'waffle')
    world_path = os.path.join(
        get_package_share_directory('paveway_sim'),
        'worlds',
        f'{TURTLEBOT3_MODEL}.world'
    )

    rviz_config = os.path.join(
        get_package_share_directory('paveway_sim'),
        'rviz',
        'model.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-0.6')
    y_pose = LaunchConfiguration('y_pose', default='0.5')

    if TURTLEBOT3_MODEL == "waffle":
        x_pose = '-1.5'
        y_pose = '-1.5'

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    spawn_turtlebot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose
        }.items()
    )

    joint_state_publisher_cmd = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    rviz2_cmd = TimerAction(
        period=5.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        )]
    )

    # Mapping mode only. For navigation, paveway_nav starts AMCL against a saved
    # map; running slam_toolbox at the same time would publish a second,
    # conflicting map -> odom transform.
    slam = LaunchConfiguration('slam')
    slam_node = Node(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(slam)
    )

    return LaunchDescription([
        DeclareLaunchArgument('slam', default_value='false',
                              description='Run slam_toolbox to build a new map'),
        gzserver_cmd, 
        gzclient_cmd, 
        robot_state_publisher_cmd, 
        spawn_turtlebot_cmd,
        joint_state_publisher_cmd,
        rviz2_cmd,
        slam_node
    ])
