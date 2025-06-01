import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import os

class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')
        self.publisher_ = self.create_publisher(Image, '/image_raw_simulated', 10)
        self.bridge = CvBridge()

        # Path to your video file (change this if needed)
        video_path = os.environ['HOME'] + '/paveway_ws/src/paveway_vision/angle-2.avi'

        if not os.path.exists(video_path):
            self.get_logger().error(f"Video file not found: {video_path}")
            raise FileNotFoundError(video_path)

        self.cap = cv2.VideoCapture(video_path)
        self.timer_period = 1.0 / self.cap.get(cv2.CAP_PROP_FPS)
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.get_logger().info('VideoPublisher started.')

    def timer_callback(self):
        ret, frame = self.cap.read()

        if not ret:
            # Restart video if it ends
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VideoPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
