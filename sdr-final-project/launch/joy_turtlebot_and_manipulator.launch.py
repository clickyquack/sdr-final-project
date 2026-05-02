from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    # Shared joy topic across both teleops
    joy_topic = LaunchConfiguration('joy_topic', default='joy')
    joy_autorepeat_rate = LaunchConfiguration('joy_autorepeat_rate', default='50.0')

    # TurtleBot teleop args (mirrors joy_teleop.launch.py)
    axis_angular = LaunchConfiguration('axis_angular', default='0')
    axis_linear = LaunchConfiguration('axis_linear', default='2')
    angular_scale = LaunchConfiguration('angular_scale', default='2.84')
    linear_scale = LaunchConfiguration('linear_scale', default='0.22')
    deadzone = LaunchConfiguration('deadzone', default='0.05')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic', default='cmd_vel')
    print_rate_hz = LaunchConfiguration('print_rate_hz', default='5.0')
    publish_rate_hz = LaunchConfiguration('publish_rate_hz', default='20.0')
    joy_timeout_s = LaunchConfiguration('joy_timeout_s', default='0.5')
    linear_slew_rate = LaunchConfiguration('linear_slew_rate', default='10.0')
    angular_slew_rate = LaunchConfiguration('angular_slew_rate', default='10.0')

    # Manipulator teleop args (mirrors open_manipulator_joy_teleop.launch.py)
    manip_publish_rate_hz = LaunchConfiguration('manip_publish_rate_hz', default='50.0')
    manip_joy_timeout_s = LaunchConfiguration('manip_joy_timeout_s', default='0.5')
    manip_deadzone = LaunchConfiguration('manip_deadzone', default='0.05')

    axis_joint1 = LaunchConfiguration('axis_joint1', default='4')
    axis_joint2 = LaunchConfiguration('axis_joint2', default='5')
    axis_joint3 = LaunchConfiguration('axis_joint3', default='4')
    axis_joint4 = LaunchConfiguration('axis_joint4', default='5')
    button_shift_to_joints_3_4 = LaunchConfiguration('button_shift_to_joints_3_4', default='2')
    button_gripper_open = LaunchConfiguration('button_gripper_open', default='0')
    button_gripper_close = LaunchConfiguration('button_gripper_close', default='1')
    joint_speed_rad_s = LaunchConfiguration('joint_speed_rad_s', default='1.0')
    gripper_speed_pos_s = LaunchConfiguration('gripper_speed_pos_s', default='0.1')
    gripper_send_period_s = LaunchConfiguration('gripper_send_period_s', default='0.10')

    declare_args = [
        DeclareLaunchArgument('joy_topic', default_value='joy'),
        DeclareLaunchArgument('joy_autorepeat_rate', default_value='50.0'),

        # TurtleBot teleop
        DeclareLaunchArgument('axis_angular', default_value='0'),
        DeclareLaunchArgument('axis_linear', default_value='2'),
        DeclareLaunchArgument('angular_scale', default_value='2.84'),
        DeclareLaunchArgument('linear_scale', default_value='0.22'),
        DeclareLaunchArgument('deadzone', default_value='0.05'),
        DeclareLaunchArgument('cmd_vel_topic', default_value='cmd_vel'),
        DeclareLaunchArgument('print_rate_hz', default_value='5.0'),
        DeclareLaunchArgument('publish_rate_hz', default_value='20.0'),
        DeclareLaunchArgument('joy_timeout_s', default_value='0.5'),
        DeclareLaunchArgument('linear_slew_rate', default_value='10.0'),
        DeclareLaunchArgument('angular_slew_rate', default_value='10.0'),

        # Manipulator teleop (namespaced args so they don't clash)
        DeclareLaunchArgument('manip_publish_rate_hz', default_value='50.0'),
        DeclareLaunchArgument('manip_joy_timeout_s', default_value='0.5'),
        DeclareLaunchArgument('manip_deadzone', default_value='0.05'),
        DeclareLaunchArgument('axis_joint1', default_value='4'),
        DeclareLaunchArgument('axis_joint2', default_value='5'),
        DeclareLaunchArgument('axis_joint3', default_value='4'),
        DeclareLaunchArgument('axis_joint4', default_value='5'),
        DeclareLaunchArgument('button_shift_to_joints_3_4', default_value='2'),
        DeclareLaunchArgument('button_gripper_open', default_value='0'),
        DeclareLaunchArgument('button_gripper_close', default_value='1'),
        DeclareLaunchArgument('joint_speed_rad_s', default_value='1.0'),
        DeclareLaunchArgument('gripper_speed_pos_s', default_value='0.1'),
        DeclareLaunchArgument('gripper_send_period_s', default_value='0.10'),
    ]

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[{
            'autorepeat_rate': joy_autorepeat_rate,
        }],
    )

    turtlebot_teleop_node = Node(
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

    manipulator_teleop_node = Node(
        package='sdr-final-project',
        executable='open_manipulator_joy_teleop',
        name='open_manipulator_joy_teleop',
        output='screen',
        parameters=[{
            'joy_topic': joy_topic,
            'publish_rate_hz': manip_publish_rate_hz,
            'joy_timeout_s': manip_joy_timeout_s,
            'deadzone': manip_deadzone,
            'axis_joint1': axis_joint1,
            'axis_joint2': axis_joint2,
            'axis_joint3': axis_joint3,
            'axis_joint4': axis_joint4,
            'button_shift_to_joints_3_4': button_shift_to_joints_3_4,
            'button_gripper_open': button_gripper_open,
            'button_gripper_close': button_gripper_close,
            'joint_speed_rad_s': joint_speed_rad_s,
            'gripper_speed_pos_s': gripper_speed_pos_s,
            'gripper_send_period_s': gripper_send_period_s,
        }],
    )

    return LaunchDescription([
        *declare_args,
        joy_node,
        turtlebot_teleop_node,
        manipulator_teleop_node,
    ])

