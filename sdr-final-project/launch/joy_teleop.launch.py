from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    axis_angular = LaunchConfiguration('axis_angular', default='0')
    axis_linear = LaunchConfiguration('axis_linear', default='2')
    angular_scale = LaunchConfiguration('angular_scale', default='2.84')
    linear_scale = LaunchConfiguration('linear_scale', default='0.22')
    deadzone = LaunchConfiguration('deadzone', default='0.05')
    joy_topic = LaunchConfiguration('joy_topic', default='joy')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic', default='cmd_vel')
    print_rate_hz = LaunchConfiguration('print_rate_hz', default='5.0')
    publish_rate_hz = LaunchConfiguration('publish_rate_hz', default='20.0')
    joy_timeout_s = LaunchConfiguration('joy_timeout_s', default='0.5')
    linear_slew_rate = LaunchConfiguration('linear_slew_rate', default='10.0')
    angular_slew_rate = LaunchConfiguration('angular_slew_rate', default='10.0')

    declare_args = [
        DeclareLaunchArgument('axis_angular', default_value='0'),
        DeclareLaunchArgument('axis_linear', default_value='2'),
        DeclareLaunchArgument('angular_scale', default_value='2.84'),
        DeclareLaunchArgument('linear_scale', default_value='0.22'),
        DeclareLaunchArgument('deadzone', default_value='0.05'),
        DeclareLaunchArgument('joy_topic', default_value='joy'),
        DeclareLaunchArgument('cmd_vel_topic', default_value='cmd_vel'),
        DeclareLaunchArgument('print_rate_hz', default_value='5.0'),
        DeclareLaunchArgument('publish_rate_hz', default_value='20.0'),
        DeclareLaunchArgument('joy_timeout_s', default_value='0.5'),
        DeclareLaunchArgument('linear_slew_rate', default_value='10.0'),
        DeclareLaunchArgument('angular_slew_rate', default_value='10.0'),
    ]

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[{
            'autorepeat_rate': 20.0,
        }],
    )

    teleop_node = Node(
        package='sdr-final-project',
        executable='joy_teleop',
        name='joy_teleop',
        output='screen',
        parameters=[{
            'axis_angular': axis_angular,
            'axis_linear': axis_linear,
            'angular_scale': angular_scale,
            'linear_scale': linear_scale,
            'deadzone': deadzone,
            'joy_topic': joy_topic,
            'cmd_vel_topic': cmd_vel_topic,
            'print_rate_hz': print_rate_hz,
            'publish_rate_hz': publish_rate_hz,
            'joy_timeout_s': joy_timeout_s,
            'linear_slew_rate': linear_slew_rate,
            'angular_slew_rate': angular_slew_rate,
        }],
    )

    return LaunchDescription([*declare_args, joy_node, teleop_node])
