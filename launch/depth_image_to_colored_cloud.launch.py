from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    rgbd_sync_node = Node(
        package='depth_image_proc',
        executable='point_cloud_xyzrgb_node',
        name='depth_image_to_cloud',
        output='screen',
        parameters=[{
            
            'queue_size': 5
        }],
        remappings=[('rgb/camera_info', '/camera/camera/color/camera_info'),
                                ('rgb/image_rect_color', '/camera/camera/color/image_raw'),
                                ('depth_registered/image_rect',
                                 '/camera/camera/aligned_depth_to_color/image_raw'),
                                ('points', '/camera/camera/depth_registered/points')]
        
    )

    return LaunchDescription([rgbd_sync_node])