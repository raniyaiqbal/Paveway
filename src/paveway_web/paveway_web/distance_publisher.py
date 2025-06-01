import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Float32
import math

class DistanceTracker(Node):
    def __init__(self):
        super().__init__('distance_tracker')
        self.sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.pub = self.create_publisher(Float32, '/distance_covered', 10)

        self.last_x = None
        self.last_y = None
        self.total_distance = 0.0

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        if self.last_x is not None and self.last_y is not None:
            dx = x - self.last_x
            dy = y - self.last_y
            dist = math.sqrt(dx**2 + dy**2)
            self.total_distance += dist

        self.last_x = x
        self.last_y = y

        distance_msg = Float32()
        distance_msg.data = self.total_distance
        self.pub.publish(distance_msg)

def main(args=None):
    rclpy.init(args=args)
    node = DistanceTracker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
