#!/usr/bin/env python3

import os

from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.clock import Clock
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import Joy


BURGER_MAX_LIN_VEL = 0.22
BURGER_MAX_ANG_VEL = 2.84

WAFFLE_MAX_LIN_VEL = 0.26
WAFFLE_MAX_ANG_VEL = 1.82


def _deadzone(value: float, dz: float) -> float:
    return 0.0 if abs(value) < dz else value


def _slew(current: float, target: float, step: float) -> float:
    if target > current:
        return min(target, current + step)
    if target < current:
        return max(target, current - step)
    return target


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


class JoyTeleop(Node):

    def __init__(self) -> None:
        super().__init__('joy_teleop')

        self._ros_distro = os.environ.get('ROS_DISTRO')
        self._model = os.environ.get('TURTLEBOT3_MODEL', 'burger')
        if self._model == 'burger':
            self._max_lin = BURGER_MAX_LIN_VEL
            self._max_ang = BURGER_MAX_ANG_VEL
        else:
            self._max_lin = WAFFLE_MAX_LIN_VEL
            self._max_ang = WAFFLE_MAX_ANG_VEL

        self.declare_parameter('axis_angular', 0)
        self.declare_parameter('axis_linear', 2)
        # Defaults chosen so full stick (1.0) maps to TurtleBot3 model max velocities.
        self.declare_parameter('angular_scale', self._max_ang)
        self.declare_parameter('linear_scale', self._max_lin)
        self.declare_parameter('deadzone', 0.05)
        self.declare_parameter('joy_topic', 'joy')
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')
        self.declare_parameter('print_rate_hz', 5.0)
        self.declare_parameter('publish_rate_hz', 20.0)
        self.declare_parameter('joy_timeout_s', 0.5)
        self.declare_parameter('linear_slew_rate', 10.0)    # max change per second
        self.declare_parameter('angular_slew_rate', 10.0)   # max change per second

        self._axis_angular = int(self.get_parameter('axis_angular').value)
        self._axis_linear = int(self.get_parameter('axis_linear').value)
        self._angular_scale = float(self.get_parameter('angular_scale').value)
        self._linear_scale = float(self.get_parameter('linear_scale').value)
        self._deadzone = float(self.get_parameter('deadzone').value)
        self._print_rate_hz = float(self.get_parameter('print_rate_hz').value)
        self._publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self._joy_timeout_s = float(self.get_parameter('joy_timeout_s').value)
        self._lin_slew = abs(float(self.get_parameter('linear_slew_rate').value))
        self._ang_slew = abs(float(self.get_parameter('angular_slew_rate').value))
        joy_topic = str(self.get_parameter('joy_topic').value)
        cmd_vel_topic = str(self.get_parameter('cmd_vel_topic').value)

        qos = QoSProfile(depth=10)

        # Mirror TurtleBot3 teleop behavior: Humble uses Twist, newer distros use TwistStamped.
        if self._ros_distro == 'humble':
            self._pub_twist = self.create_publisher(Twist, cmd_vel_topic, qos)
        else:
            self._pub_twist = self.create_publisher(TwistStamped, cmd_vel_topic, qos)

        self.create_subscription(Joy, joy_topic, self._on_joy, qos)
        now_ns = self.get_clock().now().nanoseconds
        self._next_log_time_ns = now_ns
        self._last_joy_time_ns = now_ns
        self._target_lin = 0.0
        self._target_ang = 0.0
        self._control_lin = 0.0
        self._control_ang = 0.0

        if self._publish_rate_hz > 0.0:
            self.create_timer(1.0 / self._publish_rate_hz, self._publish_last_cmd)

    def _on_joy(self, msg: Joy) -> None:
        axes = msg.axes or []
        if self._axis_angular >= len(axes) or self._axis_linear >= len(axes):
            return

        # Requirement mapping:
        # - Axis 0: + => rotate left (positive angular.z), - => rotate right
        # - Axis 2: + => forward (positive linear.x), - => backward
        raw_ang = _deadzone(float(axes[self._axis_angular]), self._deadzone) * self._angular_scale
        raw_lin = _deadzone(float(axes[self._axis_linear]), self._deadzone) * self._linear_scale

        self._target_lin = _clamp(raw_lin, self._max_lin)
        self._target_ang = _clamp(raw_ang, self._max_ang)
        self._last_joy_time_ns = self.get_clock().now().nanoseconds

        if self._publish_rate_hz <= 0.0:
            self._control_lin = self._target_lin
            self._control_ang = self._target_ang
            self._publish_cmd(lin=self._control_lin, ang=self._control_ang)

    def _publish_last_cmd(self) -> None:
        target_lin = self._target_lin
        target_ang = self._target_ang

        if self._joy_timeout_s > 0.0:
            now_ns = self.get_clock().now().nanoseconds
            timeout_ns = int(self._joy_timeout_s * 1e9)
            if now_ns - self._last_joy_time_ns > timeout_ns:
                target_lin = 0.0
                target_ang = 0.0

        dt = 1.0 / self._publish_rate_hz
        self._control_lin = _slew(self._control_lin, target_lin, self._lin_slew * dt)
        self._control_ang = _slew(self._control_ang, target_ang, self._ang_slew * dt)

        self._publish_cmd(lin=self._control_lin, ang=self._control_ang)

    def _publish_cmd(self, *, lin: float, ang: float) -> None:
        if self._ros_distro == 'humble':
            twist = Twist()
            twist.linear.x = lin
            twist.angular.z = ang
            msg = twist
        else:
            twist_stamped = TwistStamped()
            twist_stamped.header.stamp = Clock().now().to_msg()
            twist_stamped.twist.linear.x = lin
            twist_stamped.twist.angular.z = ang
            msg = twist_stamped

        if self._print_rate_hz > 0.0:
            now_ns = self.get_clock().now().nanoseconds
            period_ns = int(1e9 / self._print_rate_hz)
            if now_ns >= self._next_log_time_ns:
                self.get_logger().info(f'cmd_vel: linear.x={lin:.3f} angular.z={ang:.3f}')
                self._next_log_time_ns = now_ns + period_ns

        self._pub_twist.publish(msg)


def main() -> None:
    rclpy.init()
    node = JoyTeleop()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
