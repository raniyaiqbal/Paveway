import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from visualization_msgs.msg import Marker

class PotholeVisualizer(Node):
    def __init__(self):
        super().__init__('pothole_visualizer')

        # Subscribe to pothole coordinates
        self.subscription = self.create_subscription(
            PointStamped, '/pothole_coords', self.pothole_callback, 10)

        # Publisher for visualization markers
        self.marker_publisher = self.create_publisher(Marker, '/pothole_marker', 10)

        self.get_logger().info("Pothole Visualizer Node Initialized.")

    def pothole_callback(self, msg):
        marker = Marker()
        marker.header.frame_id = "base_link"  # Change to appropriate frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "potholes"
        marker.id = int(msg.point.x + msg.point.y)  # Unique ID based on coordinates
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD

        # Set position from received PointStamped
        marker.pose.position.x = msg.point.x
        marker.pose.position.y = msg.point.y
        marker.pose.position.z = 0.0

        # Set marker properties
        marker.scale.x = 0.2
        marker.scale.y = 0.2
        marker.scale.z = 0.2
        marker.color.a = 1.0
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0

        self.marker_publisher.publish(marker)
        self.get_logger().info(f"Visualized Pothole at ({msg.point.x}, {msg.point.y})")

def main(args=None):
    rclpy.init(args=args)
    node = PotholeVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
