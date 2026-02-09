from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # -------------------------
    # Launch arguments
    # -------------------------
    use_camera_arg = DeclareLaunchArgument(
        'use_camera',
        default_value='true',
        description='Whether to launch camera-related nodes (RealSense, RGB-D sync)'
    )

    use_camera = LaunchConfiguration('use_camera')

    # -------------------------
    # IMU filter (ros2 run ...)
    # -------------------------
    imu_filter = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter',
        output='screen',
        parameters=[{
            'publish_tf': False,
            'use_sim_time': False,
            'use_mag': False
        }]
    )

    # -------------------------
    # RealSense pointcloud
    # -------------------------
    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('realsense2_camera'),
                'examples',
                'pointcloud',
                'rs_pointcloud_launch.py'
            )
        ),
        launch_arguments={
            'clip_distance': '6.5'
        }.items()#,
        #condition=IfCondition(use_camera)
    )

    # -------------------------
    # RGB-D sync ### Use to produce rgbd_image topic for RTAB-Map
    # -------------------------
    rgbd_sync_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gr_bringup'),
                'launch',
                'rgbd_sync.launch.py'
            )
        ),
        condition=IfCondition(use_camera)
    )

    # -------------------------
    # PointCloud → LaserScan ###Use for nav2 in Obstacle layer
    # -------------------------
    pcl_to_scan_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('pointcloud_to_laserscan'),
                'launch',
                'sample_pointcloud_to_laserscan_launch.py'
            )
        )
    )

    # -------------------------
    # RTAB-Map lidar + RGB-D if use_camera
    print("Use camera:", IfCondition(use_camera))
    # -------------------------
   
    rtabmap_launch_with_camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rtabmap_examples'),
                'launch',
                'lidar3d.launch.py'
            )
        ),
        launch_arguments={
            'lidar_topic': '/livox/lidar',
            'imu_topic': '/imu/data',
            'frame_id': 'base_link',
            'rgbd_image_topic': 'rgbd_image',
            'deskewing': 'true'
        }.items(),
        condition=IfCondition(use_camera)
    )

    rtabmap_launch_without_camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rtabmap_examples'),
                'launch',
                'lidar3d.launch.py'
            )
        ),
        launch_arguments={
            'lidar_topic': '/livox/lidar',
            'imu_topic': '/imu/data',
            'frame_id': 'base_link',
            #'deskewing': 'false'
            
        }.items(),
        condition=UnlessCondition(use_camera)

    )

            

    # -------------------------
    # Return everything
    # -------------------------
    return LaunchDescription([
        use_camera_arg,
        imu_filter,
        realsense_launch,
        rgbd_sync_launch,
        pcl_to_scan_launch,
        rtabmap_launch_with_camera,
        rtabmap_launch_without_camera
    ])
