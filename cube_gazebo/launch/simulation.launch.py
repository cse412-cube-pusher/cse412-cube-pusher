from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    gazebo_dir = Path(get_package_share_directory("cube_gazebo"))
    description_dir = Path(get_package_share_directory("cube_description"))
    ros_gz_dir = Path(get_package_share_directory("ros_gz_sim"))

    robot_file = description_dir / "urdf" / "cube_robot.urdf.xacro"
    robot_xml = xacro.process_file(str(robot_file)).toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(ros_gz_dir / "launch" / "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": f"-r {gazebo_dir / 'worlds' / 'arena.sdf'}",
            "on_exit_shutdown": "true",
        }.items(),
    )

    state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "use_sim_time": True,
            "robot_description": ParameterValue(robot_xml, value_type=str),
        }],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            "config_file": str(gazebo_dir / "config" / "bridge.yaml"),
            "use_sim_time": True,
        }],
        output="screen",
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "cube_robot",
            "-string", robot_xml,
            "-x", "-2.4",
            "-y", "-1.4",
            "-z", "0.01",
        ],
        output="screen",
    )

    return LaunchDescription([
        gazebo, state_publisher, bridge, spawn_robot
    ])
