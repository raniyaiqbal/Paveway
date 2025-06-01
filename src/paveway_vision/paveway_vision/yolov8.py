from ultralytics import YOLO
import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
from cv_bridge import CvBridge
import math

from yolo_msgs.msg import InferenceResult
from yolo_msgs.msg import YoloInference

bridge = CvBridge()

class Camera_subscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')

        self.model = YOLO(os.environ['HOME'] + '/paveway_ws/src/paveway_vision/models/v8.pt')
        self.yolov8_inference = YoloInference()

        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.camera_callback,
            10
        )

        self.yolov8_pub = self.create_publisher(YoloInference, '/inference', 1)
        self.img_pub = self.create_publisher(Image, '/inference_result', 1)

         # Track unique potholes using center point tracking
        self.detected_potholes = []
        self.detection_threshold = 50  # pixels

        # Publisher for unique pothole count
        self.pothole_count_pub = self.create_publisher(Int32, '/pothole_count', 1)

    def is_new_detection(self, center):
        for existing in self.detected_potholes:
            dist = math.hypot(center[0] - existing[0], center[1] - existing[1])
            if dist < self.detection_threshold:
                return False
        return True

    def camera_callback(self, data):
        img = bridge.imgmsg_to_cv2(data, 'bgr8')
        results = self.model(img, conf = 0.5)

        self.yolov8_inference.header.frame_id = "inference"
        self.yolov8_inference.header.stamp = self.get_clock().now().to_msg()

        for r in results:
            boxes = r.boxes

            for box in boxes:
                self.inference_result = InferenceResult()
                b = box.xyxy[0].cpu().detach().numpy().copy()

                center_x = int((b[0] + b[2]) / 2)
                center_y = int((b[1] + b[3]) / 2)

                if self.is_new_detection((center_x, center_y)):
                    self.detected_potholes.append((center_x, center_y))

                self.inference_result.top = int(b[0])
                self.inference_result.left = int(b[1])
                self.inference_result.bottom = int(b[2])
                self.inference_result.right = int(b[3])

                self.yolov8_inference.yolov8_inference.append(self.inference_result)

        annotated_frame = results[0].plot()
        img_msg = bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')

        self.img_pub.publish(img_msg)
        self.yolov8_pub.publish(self.yolov8_inference)

        # Publish the count
        pothole_msg = Int32()
        pothole_msg.data = len(self.detected_potholes)
        self.pothole_count_pub.publish(pothole_msg)

        self.yolov8_inference.yolov8_inference.clear()

def main():
    rclpy.init(args=None)
    camera_subscriber = Camera_subscriber()
    rclpy.spin(camera_subscriber)
    camera_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

