import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import PointStamped
import tf2_ros
import tf2_geometry_msgs
from std_msgs.msg import Header

class PotholeDetector(Node):
    def __init__(self):
        super().__init__('pothole_detector')

        # ROS 2 Subscribers and Publishers
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(PointStamped, '/pothole_coords', 10)

        # TF2 Buffer and Listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.bridge = CvBridge()
        self.detected_potholes = set()  # Store detected potholes
        self.get_logger().info("Pothole Detector Node Initialized.")

    def is_new_pothole(self, x, y, threshold=0.2):  # Adjust threshold for real-world scale
        for px, py in self.detected_potholes:
            if abs(px - x) < threshold and abs(py - y) < threshold:
                return False  # Pothole is already detected
        return True

    def image_callback(self, msg):
        try:
            # Convert ROS Image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Convert BGR to HSV
            hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

            # Define HSV range for red color detection
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])

            # Create masks for red color
            mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
            mask = mask1 + mask2

            # Find contours of detected potholes
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Filter out small noise
                    # Compute centroid of the pothole
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        # Convert Image Coordinates (cx, cy) to 3D in Camera Frame
                        pothole_3D_camera = self.image_to_camera_coords(cx, cy)

                        # Transform to Base Link Frame
                        pothole_3D_robot = self.transform_to_robot_frame(pothole_3D_camera)

                        if pothole_3D_robot and self.is_new_pothole(pothole_3D_robot.x, pothole_3D_robot.y):
                            # Add to detected potholes list
                            self.detected_potholes.add((pothole_3D_robot.x, pothole_3D_robot.y))

                            # Publish the pothole coordinates
                            pothole_msg = PointStamped()
                            pothole_msg.header.stamp = self.get_clock().now().to_msg()
                            pothole_msg.header.frame_id = "base_link"
                            pothole_msg.point = pothole_3D_robot

                            self.publisher.publish(pothole_msg)
                            self.get_logger().info(f"Published New Pothole: x={pothole_3D_robot.x}, y={pothole_3D_robot.y}")

        except Exception as e:
            self.get_logger().error(f"Error processing image: {str(e)}")

    def image_to_camera_coords(self, cx, cy):
        Z = 1.5 
        fx, fy = 600.0, 600.0  # TODO: Camera focal lengths (change based on your camera)
        cx_offset, cy_offset = 320.0, 240.0  # TODO: Image center (change based on camera)

        X = (cx - cx_offset) * Z / fx
        Y = (cy - cy_offset) * Z / fy

        pothole_msg = PointStamped()
        pothole_msg.header = Header()
        pothole_msg.header.stamp = self.get_clock().now().to_msg()
        pothole_msg.header.frame_id = "camera_depth_frame"
        pothole_msg.point.x = X
        pothole_msg.point.y = Y
        pothole_msg.point.z = Z

        return pothole_msg

    def transform_to_robot_frame(self, pothole_camera):
        try:
            transform = self.tf_buffer.lookup_transform("base_link", "camera_depth_frame", rclpy.time.Time())
            pothole_robot = tf2_geometry_msgs.do_transform_point(pothole_camera, transform)
            return pothole_robot.point
        except Exception as e:
            self.get_logger().warn(f"TF2 transform failed: {e}")
            return None


def main(args=None):
    rclpy.init(args=args)
    node = PotholeDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
