from ament_index_python.packages import get_package_share_directory
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    
    ld = LaunchDescription()

    pkg_share = FindPackageShare(package='gr_description').find('gr_description')
    gr_bringup_share = FindPackageShare(package='gr_bringup').find('gr_bringup')
    default_model_path = os.path.join(pkg_share, 'urdf/gr_p247_ign.urdf.xacro')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    ### Environment variables
    ld.add_action(SetEnvironmentVariable('LIDAR_TYPE', 'LIVOX_MID_360'))
    ld.add_action(SetEnvironmentVariable('ROBOT_TYPE', 'SCOUT_MINI'))
    ld.add_action(SetEnvironmentVariable('CAMERA_TYPE', 'D435'))


    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        emulate_tty=True,
        parameters=[{'robot_description': Command(['xacro ', default_model_path]),
                     'use_sim_time':True}]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[{'use_sim_time':True}]
    )
    default_rviz_config_path = os.path.join(gr_bringup_share, 'rviz/rviz_livox_realsense.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )

    ld.add_action(DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                            description='Absolute path to rviz config file'))
    ld.add_action(rviz_node)
    #ld.add_action(IncludeLaunchDescription(PythonLaunchDescriptionSource(PathJoinSubstitution([
    #    FindPackageShare("gr_description"), "launch", "component.launch.py"]
    #))))
    ld.add_action(joint_state_publisher_node)
    ld.add_action(robot_state_publisher_node)
    world = PathJoinSubstitution([
        FindPackageShare('aws_robomaker_small_warehouse_world'),
        'worlds',
        'no_roof_small_warehouse.sdf',
    ])
    
    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': world}.items(),
        #launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'scout_mini',
            '-topic', 'robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.3',
            '-v', '4',
        ],
        output='screen',
    )
    bridge_path = os.path.join(gr_bringup_share, 'config', 'gz_bridge.yaml')
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True},
                     {'config_file' : bridge_path}])
    
    ld.add_action(gazebo)
    ld.add_action(spawn)
    ld.add_action(bridge)

    ## TF republisher : change frame X into Y : used because the realsense gazebo plugin is for the old gazebo,
    # and natively the frame in ignition is $name/base_link/cameradepth, but in ROS2 we want it to be camera_depth_optical_frame, so we republish a static transform between these two frames 

    tf_republisher = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "0",
            "0",
            "0",
            "1.5708",
            "-1.5708",
            "0",
            "camera_depth_optical_frame",
            "scout_mini/base_link/cameradepth",
        ],
        output="screen",
    )
    #ld.add_action(tf_republisher)

    ### Invert IMU gravity, to match the real robot s IMU

    invert_imu_gravity_node = Node(
        package='slam_bringup',
        executable='invert_imu_gravity',
        name='invert_imu_gravity',
        output='screen',
    )
    ld.add_action(invert_imu_gravity_node)

    '''
    port_name_launch_arg = DeclareLaunchArgument(
        'port_name',
        default_value='can0'
    )
    simulated_robot_launch_arg = DeclareLaunchArgument(
        'simulated_robot',
        default_value='false'
    )
    odom_topic_name_launch_arg = DeclareLaunchArgument(
        'odom_topic_name',
        default_value='odom'
    )
    pub_tf_launch_arg = DeclareLaunchArgument(
        'pub_tf',
        default_value='true'
    )
    ld.add_action(port_name_launch_arg)
    ld.add_action(simulated_robot_launch_arg)
    ld.add_action(odom_topic_name_launch_arg)
    ld.add_action(pub_tf_launch_arg)

    ld.add_action(IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([FindPackageShare("scout_base"), "launch", "scout_mini_base.launch.py"])]
            ),
            launch_arguments={
                'port_name': LaunchConfiguration('port_name'),
                'simulated_robot': LaunchConfiguration('simulated_robot'),
                'odom_topic_name': LaunchConfiguration('odom_topic_name'),
                'publish_tf': LaunchConfiguration('pub_tf'),
            }.items()
        ))
    '''
    

    return ld