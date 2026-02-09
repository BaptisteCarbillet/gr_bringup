from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    rgbd_sync_node = Node(
        package='depth_image_proc',
        executable='point_cloud_xyz_node',
        name='depth_image_to_cloud',
        output='screen',
        parameters=[{
            
            'queue_size': 5
        }],
        remappings=[
           ('image_rect', '/camera/camera/depth/image_rect_raw'),
            ('camera_info', '/camera/camera/depth/camera_info'),
            ('points', '/camera/depth_cloud')  # output
        ]
    )

    return LaunchDescription([rgbd_sync_node])