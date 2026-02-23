#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node
from launch.event_handlers import OnProcessStart


def generate_launch_description():
    bag_dir_default = os.path.join(
        os.path.expanduser("~"), "roskit_ws", "bags", "lidar_inspection"
    )

    bag_dir = LaunchConfiguration("bag_dir")

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gr_bringup"),
                "launch",
                "gazebo_launch.py",
            )
        )
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("slam_bringup"),
                "launch",
                "slam_sim_launch.py",
            )
        )
    )

    nav_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("nav2_sim_bringup"),
                "launch",
                "navigation_launch.py",
            )
        )
    )

    waypoint_node = Node(
        package="coverage_roi",
        executable="waypoint_explorer",
        name="waypoint_explorer",
        output="screen",
        parameters=[{"waypoints_file": "waypoint_lidar_only.yaml"}],
    )

    ### get first indice of bag_dir that does not exist
    idx = 0
    while os.path.exists(f"{bag_dir_default}_{idx}"):
        idx += 1
    bag_dir_default = f"{bag_dir_default}_{idx}"

    bag_record = ExecuteProcess(
        cmd=[
            "ros2",
            "bag",
            "record",
            "-o",
            bag_dir_default,
            "/livox/lidar",
            "/imu/data_raw",
            "/imu/mag",
            "/rgbd_image",
            "/tf",
            "/tf_static",
            "/clock",
            "/odom",
            "/camera/camera/color/image_raw",
            "/camera/camera/depth/image_rect_raw",
            "--use-sim-time",
        ],
       
        
    )

    delayed_launches = TimerAction(
        period=10.0,
        actions=[
            slam_launch,
            nav_launch,
            waypoint_node,
            #mkdir_bag_dir,
            bag_record,
        ],
    )

    configure_waypoint = ExecuteProcess(
        cmd=["ros2", "lifecycle", "set", "/waypoint_explorer", "configure"]
    )

    activate_waypoint = ExecuteProcess(
        cmd=["ros2", "lifecycle", "set", "/waypoint_explorer", "activate"]
    )

    lifecycle_on_start = RegisterEventHandler(
        OnProcessStart(
            target_action=waypoint_node,
            on_start=[
                TimerAction(period=2.0, actions=[configure_waypoint]),
                TimerAction(period=4.0, actions=[activate_waypoint]),
            ],
        )
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("bag_dir", default_value=bag_dir_default),
            gazebo_launch,
            delayed_launches,
            lifecycle_on_start,
        ]
    )
