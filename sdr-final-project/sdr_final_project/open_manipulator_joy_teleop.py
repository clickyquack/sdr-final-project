#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional

from control_msgs.action import GripperCommand
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import Joy
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


def _deadzone(value: float, dz: float) -> float:
    return 0.0 if abs(value) < dz else value


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class _JointLimit:
    lo: float
    hi: float


class OpenManipulatorJoyTeleop(Node):

    def __init__(self) -> None:
        super().__init__('open_manipulator_joy_teleop')

        self.declare_parameter('joy_topic', 'joy')
        self.declare_parameter('publish_rate_hz', 50.0)
        self.declare_parameter('joy_timeout_s', 0.5)
        self.declare_parameter('deadzone', 0.05)

        # Joy mapping:
        # - By default, axes [4] and [5] control joints 1 and 2.
        # - While holding button [2], axes [4] and [5] control joints 3 and 4 instead.
        self.declare_parameter('axis_joint1', 4)
        self.declare_parameter('axis_joint2', 5)
        self.declare_parameter('axis_joint3', 4)
        self.declare_parameter('axis_joint4', 5)
        self.declare_parameter('button_shift_to_joints_3_4', 2)

        # Buttons: hold to open/close gripper.
        self.declare_parameter('button_gripper_open', 0)
        self.declare_parameter('button_gripper_close', 1)

        # Step behavior (axis acts like a "button"):
        # - Hold axis past deadzone to keep nudging joint by joint_step_rad every step_interval_s.
        self.declare_parameter('joint_step_rad', 0.02)
        self.declare_parameter('step_interval_s', 0.02)
        self.declare_parameter('gripper_speed_pos_s', 0.1)
        self.declare_parameter('gripper_send_period_s', 0.10)

        joy_topic = str(self.get_parameter('joy_topic').value)
        self._publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self._joy_timeout_s = float(self.get_parameter('joy_timeout_s').value)
        self._deadzone = float(self.get_parameter('deadzone').value)
        self._axis_joint = [
            int(self.get_parameter('axis_joint1').value),
            int(self.get_parameter('axis_joint2').value),
            int(self.get_parameter('axis_joint3').value),
            int(self.get_parameter('axis_joint4').value),
        ]
        self._btn_shift = int(self.get_parameter('button_shift_to_joints_3_4').value)
        self._btn_open = int(self.get_parameter('button_gripper_open').value)
        self._btn_close = int(self.get_parameter('button_gripper_close').value)
        self._joint_step = abs(float(self.get_parameter('joint_step_rad').value))
        self._step_interval_s = abs(float(self.get_parameter('step_interval_s').value))
        self._gripper_speed = abs(float(self.get_parameter('gripper_speed_pos_s').value))
        self._gripper_send_period_s = abs(float(self.get_parameter('gripper_send_period_s').value))

        qos = QoSProfile(depth=10)

        # Arm joint control publisher and gripper action client (same interfaces as open_manipulator_x_teleop.py).
        self._arm_pub = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', qos
        )
        self._gripper_client = ActionClient(
            self, GripperCommand, '/gripper_controller/gripper_cmd'
        )

        self.create_subscription(JointState, '/joint_states', self._on_joint_state, qos)
        self.create_subscription(Joy, joy_topic, self._on_joy, qos)

        self._arm_joint_names = ['joint1', 'joint2', 'joint3', 'joint4']
        self._arm_limits = [
            _JointLimit(lo=-math.pi, hi=math.pi),
            _JointLimit(lo=-1.5, hi=1.5),
            _JointLimit(lo=-1.5, hi=1.5),
            _JointLimit(lo=-1.5, hi=1.5),
        ]

        self._gripper_min = -0.01
        self._gripper_max = 0.019

        self._arm_pos: List[float] = [0.0, 0.0, 0.0, 0.0]
        self._gripper_pos: float = 0.0
        self._joint_received = False

        self._last_joy_msg: Optional[Joy] = None
        self._last_joy_time_ns = self.get_clock().now().nanoseconds
        self._last_gripper_send_ns = 0
        self._last_joint_step_ns = [0, 0, 0, 0]

        if self._publish_rate_hz > 0.0:
            self._dt = 1.0 / self._publish_rate_hz
            self.create_timer(self._dt, self._tick)
        else:
            self._dt = 0.02
            self.get_logger().warn('publish_rate_hz <= 0; teleop timer disabled.')

        self.get_logger().info('Waiting for /joint_states and /joy...')

    def _on_joint_state(self, msg: JointState) -> None:
        if set(self._arm_joint_names).issubset(set(msg.name)):
            for i, joint in enumerate(self._arm_joint_names):
                idx = msg.name.index(joint)
                self._arm_pos[i] = float(msg.position[idx])

        # OpenManipulator-X uses rh_r1_joint for the gripper joint state.
        if 'rh_r1_joint' in msg.name:
            idx = msg.name.index('rh_r1_joint')
            self._gripper_pos = float(msg.position[idx])

        self._joint_received = True

    def _on_joy(self, msg: Joy) -> None:
        self._last_joy_msg = msg
        self._last_joy_time_ns = self.get_clock().now().nanoseconds

    def _tick(self) -> None:
        if not self._joint_received:
            return

        joy = self._last_joy_msg
        now_ns = self.get_clock().now().nanoseconds
        if joy is None:
            return

        if self._joy_timeout_s > 0.0:
            timeout_ns = int(self._joy_timeout_s * 1e9)
            if now_ns - self._last_joy_time_ns > timeout_ns:
                return

        axes = joy.axes or []
        buttons = joy.buttons or []

        shift_pressed = (0 <= self._btn_shift < len(buttons)) and (int(buttons[self._btn_shift]) == 1)

        # Update only the active joint pair (axis behaves like a button).
        joint_indices = (2, 3) if shift_pressed else (0, 1)
        step_interval_ns = int(self._step_interval_s * 1e9) if self._step_interval_s > 0.0 else 0
        for j in joint_indices:
            aidx = self._axis_joint[j]
            raw = float(axes[aidx]) if 0 <= aidx < len(axes) else 0.0
            val = _deadzone(raw, self._deadzone)
            if val == 0.0:
                continue

            if step_interval_ns > 0 and (now_ns - self._last_joint_step_ns[j]) < step_interval_ns:
                continue

            self._last_joint_step_ns[j] = now_ns
            self._arm_pos[j] += (1.0 if val > 0.0 else -1.0) * self._joint_step
            lim = self._arm_limits[j]
            self._arm_pos[j] = _clamp(self._arm_pos[j], lim.lo, lim.hi)

        # Always publish at the teleop rate; the controller ignores repeated identical points.
        self._publish_arm()

        # Gripper hold buttons.
        open_pressed = (0 <= self._btn_open < len(buttons)) and (int(buttons[self._btn_open]) == 1)
        close_pressed = (0 <= self._btn_close < len(buttons)) and (int(buttons[self._btn_close]) == 1)

        if open_pressed and not close_pressed:
            self._gripper_pos = _clamp(
                self._gripper_pos + self._gripper_speed * self._dt,
                self._gripper_min,
                self._gripper_max,
            )
            self._maybe_send_gripper(now_ns)
        elif close_pressed and not open_pressed:
            self._gripper_pos = _clamp(
                self._gripper_pos - self._gripper_speed * self._dt,
                self._gripper_min,
                self._gripper_max,
            )
            self._maybe_send_gripper(now_ns)

    def _publish_arm(self) -> None:
        msg = JointTrajectory()
        msg.joint_names = list(self._arm_joint_names)
        pt = JointTrajectoryPoint()
        pt.positions = list(self._arm_pos)
        pt.time_from_start.sec = 0
        msg.points.append(pt)
        self._arm_pub.publish(msg)

    def _maybe_send_gripper(self, now_ns: int) -> None:
        if self._gripper_send_period_s <= 0.0:
            self._send_gripper()
            return

        period_ns = int(self._gripper_send_period_s * 1e9)
        if now_ns - self._last_gripper_send_ns < period_ns:
            return

        self._last_gripper_send_ns = now_ns
        self._send_gripper()

    def _send_gripper(self) -> None:
        if not self._gripper_client.server_is_ready():
            self._gripper_client.wait_for_server(timeout_sec=0.0)
            if not self._gripper_client.server_is_ready():
                return

        goal = GripperCommand.Goal()
        goal.command.position = float(self._gripper_pos)
        goal.command.max_effort = 10.0
        self._gripper_client.send_goal_async(goal)


def main() -> None:
    rclpy.init()
    node = OpenManipulatorJoyTeleop()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

