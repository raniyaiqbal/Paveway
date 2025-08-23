#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32
from visualization_msgs.msg import MarkerArray


class PotholeCounter(Node):
    def __init__(self):
        super().__init__('pothole_counter')

        # Publisher for pothole count
        self.publisher_ = self.create_publisher(Int32, '/pothole_count', 10)

        # Subscriber to the marker array topic
        self.subscription = self.create_subscription(
            MarkerArray,
            '/object_markers',
            self.marker_callback,
            10
        )

        self.get_logger().info('Pothole Counter Node has been started.')

    def marker_callback(self, msg: MarkerArray):
        pothole_count = len(msg.markers)

        count_msg = Int32()
        count_msg.data = pothole_count

        self.publisher_.publish(count_msg)
        self.get_logger().info(f'Published pothole count: {pothole_count}')


def main(args=None):
    rclpy.init(args=args)
    node = PotholeCounter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
