import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    slam_toolbox_demo_dir = get_package_share_directory('slam_toolbox_demo')
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

    localization_params = os.path.join(slam_toolbox_demo_dir, 'config', 'localization.yaml')
    posegraph_path = os.path.join(slam_toolbox_demo_dir, 'posegraph', 'turtlebot3_world_posegraph')

    # Launch turtlebot3_world simulation
    turtlebot3_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_gazebo_dir, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    # SLAM Toolbox in localization mode
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='localization_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            localization_params,
            {
                'use_sim_time': True,
                'map_file_name': posegraph_path,
            }
        ],
    )

    configure_event = TimerAction(
        period=8.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'configure'],
            output='screen'
        )]
    )

    activate_event = TimerAction(
        period=12.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'activate'],
            output='screen'
        )]
    )

    return LaunchDescription([
        turtlebot3_world,
        slam_toolbox_node,
        configure_event,
        activate_event,
    ])