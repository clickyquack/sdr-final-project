from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    joy_topic = LaunchConfiguration('joy_topic', default='joy')
    publish_rate_hz = LaunchConfiguration('publish_rate_hz', default='50.0')
    joy_timeout_s = LaunchConfiguration('joy_timeout_s', default='0.5')
    deadzone = LaunchConfiguration('deadzone', default='0.05')

    axis_joint1 = LaunchConfiguration('axis_joint1', default='4')
    axis_joint2 = LaunchConfiguration('axis_joint2', default='5')
    axis_joint3 = LaunchConfiguration('axis_joint3', default='4')
    axis_joint4 = LaunchConfiguration('axis_joint4', default='5')
    button_shift_to_joints_3_4 = LaunchConfiguration('button_shift_to_joints_3_4', default='2')

    button_gripper_open = LaunchConfiguration('button_gripper_open', default='0')
    button_gripper_close = LaunchConfiguration('button_gripper_close', default='1')

    joint_step_rad = LaunchConfiguration('joint_step_rad', default='0.02')
    step_interval_s = LaunchConfiguration('step_interval_s', default='0.02')
    gripper_speed_pos_s = LaunchConfiguration('gripper_speed_pos_s', default='0.1')
    gripper_send_period_s = LaunchConfiguration('gripper_send_period_s', default='0.10')

    declare_args = [
        DeclareLaunchArgument('joy_topic', default_value='joy'),
        DeclareLaunchArgument('publish_rate_hz', default_value='50.0'),
        DeclareLaunchArgument('joy_timeout_s', default_value='0.5'),
        DeclareLaunchArgument('deadzone', default_value='0.05'),
        DeclareLaunchArgument('axis_joint1', default_value='4'),
        DeclareLaunchArgument('axis_joint2', default_value='5'),
        DeclareLaunchArgument('axis_joint3', default_value='4'),
        DeclareLaunchArgument('axis_joint4', default_value='5'),
        DeclareLaunchArgument('button_shift_to_joints_3_4', default_value='2'),
        DeclareLaunchArgument('button_gripper_open', default_value='0'),
        DeclareLaunchArgument('button_gripper_close', default_value='1'),
        DeclareLaunchArgument('joint_step_rad', default_value='0.02'),
        DeclareLaunchArgument('step_interval_s', default_value='0.02'),
        DeclareLaunchArgument('gripper_speed_pos_s', default_value='0.1'),
        DeclareLaunchArgument('gripper_send_period_s', default_value='0.10'),
    ]

    joy_node = Node(
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[{
            'autorepeat_rate': 50.0,
        }],
    )

    teleop_node = Node(
        package='sdr-final-project',
        executable='open_manipulator_joy_teleop',
        name='open_manipulator_joy_teleop',
        output='screen',
        parameters=[{
            'joy_topic': joy_topic,
            'publish_rate_hz': publish_rate_hz,
            'joy_timeout_s': joy_timeout_s,
            'deadzone': deadzone,
            'axis_joint1': axis_joint1,
            'axis_joint2': axis_joint2,
            'axis_joint3': axis_joint3,
            'axis_joint4': axis_joint4,
            'button_shift_to_joints_3_4': button_shift_to_joints_3_4,
            'button_gripper_open': button_gripper_open,
            'button_gripper_close': button_gripper_close,
            'joint_step_rad': joint_step_rad,
            'step_interval_s': step_interval_s,
            'gripper_speed_pos_s': gripper_speed_pos_s,
            'gripper_send_period_s': gripper_send_period_s,
        }],
    )

    return LaunchDescription([*declare_args, joy_node, teleop_node])

