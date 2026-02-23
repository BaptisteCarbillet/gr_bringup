from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    rgbd_sync_node = Node(
        package='rtabmap_sync',
        executable='rgbd_sync',
        name='rgbd_sync',
        output='screen',
        parameters=[{
            'approx_sync': True,      # or False if perfectly synced
            'queue_size': 30,
            'approx_sync_max_interval': 0.05,
            'use_sim_time': True
        }],
        remappings=[
            ('rgb/image', '/camera/camera/color/image_raw'),
            ('depth/image', '/camera/camera/depth/image_rect_raw'),
            ('rgb/camera_info', '/camera/camera/color/camera_info')
            #('rgbd_image', '/camera/rgbd_image')  # output
        ]
    )

    return LaunchDescription([rgbd_sync_node])