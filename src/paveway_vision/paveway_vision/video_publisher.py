#!/usr/bin/env python3
"""Replays a recorded video as a camera topic, for testing the detector without a robot."""
import os

import cv2
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')
        default_video = os.path.join(get_package_share_directory('paveway_vision'),
                                     'angle-2.avi')
        video_path = os.path.expanduser(self.declare_parameter('video_path', default_video).value)
        topic = self.declare_parameter('topic', '/image_raw').value
        self.frame_id = self.declare_parameter('frame_id', 'camera_rgb_optical_frame').value

        if not os.path.exists(video_path):
            raise FileNotFoundError(video_path)
        self.cap = cv2.VideoCapture(video_path)
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.bridge = CvBridge()
        self.publisher_ = self.create_publisher(Image, topic, 10)
        self.create_timer(1.0 / fps, self.timer_callback)
        self.get_logger().info(f'Publishing {video_path} on {topic} at {fps:.0f} fps')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:  # loop the clip
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = VideoPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
