#!/usr/bin/env python3

import cv2
from cv_bridge import CvBridge
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import Image


class CameraViewer(Node):
    def __init__(self) -> None:
        super().__init__('camera_viewer')

        # Match the common rqt_image_view pattern:
        # - base topic: /image_raw
        # - transport selection via parameter: _image_transport:=compressed
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('image_transport', 'compressed')
        self.declare_parameter('window_name', 'camera_viewer')

        self._image_topic = str(self.get_parameter('image_topic').value)
        self._image_transport = str(self.get_parameter('image_transport').value)
        self._window_name = str(self.get_parameter('window_name').value)

        self._bridge = CvBridge()

        qos = QoSProfile(depth=10)
        if self._image_transport == 'compressed':
            transport_topic = f'{self._image_topic}/compressed'
            self.create_subscription(
                CompressedImage, transport_topic, self._on_compressed_image, qos
            )
            self.get_logger().info(
                f"Subscribing to base '{self._image_topic}' with image_transport='compressed' "
                f"({transport_topic})"
            )
        else:
            # Fallback to raw transport (sensor_msgs/Image).
            self.create_subscription(Image, self._image_topic, self._on_raw_image, qos)
            self.get_logger().info(
                f"Subscribing to base '{self._image_topic}' with image_transport='{self._image_transport}' "
                f"({self._image_topic})"
            )

        self.get_logger().info('OpenCV window will appear on first frame')

    def _on_raw_image(self, msg: Image) -> None:
        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:  # cv_bridge throws generic exceptions
            self.get_logger().warn(f'Failed to convert image: {exc}')
            return

        try:
            cv2.imshow(self._window_name, frame)
            cv2.waitKey(1)
        except Exception as exc:
            self.get_logger().error(f'OpenCV imshow failed: {exc}')

    def _on_compressed_image(self, msg: CompressedImage) -> None:
        try:
            frame = self._bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:  # cv_bridge throws generic exceptions
            self.get_logger().warn(f'Failed to convert image: {exc}')
            return

        try:
            cv2.imshow(self._window_name, frame)
            cv2.waitKey(1)
        except Exception as exc:
            # Common when running headless (no DISPLAY) or with missing GUI backend.
            self.get_logger().error(f'OpenCV imshow failed: {exc}')


def main() -> None:
    rclpy.init()
    node = CameraViewer()
    try:
        rclpy.spin(node)
    finally:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

