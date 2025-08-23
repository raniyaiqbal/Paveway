from ultralytics import YOLO
import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Int32
from vision_msgs.msg import Detection2DArray, Detection2D, BoundingBox2D
from cv_bridge import CvBridge
import math

bridge = CvBridge()

class PotholeDetector(Node):
    def __init__(self):
        super().__init__('pothole_detector')
        
        # YOLOv8 Model
        self.model = YOLO(os.environ['HOME'] + '/paveway_ws/src/paveway_vision/models/v8.pt')
        
        # Subscribers
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',  # Remap in launch file if needed
            self.image_callback,
            10
        )
        
        # Publishers
        self.detection_pub = self.create_publisher(Detection2DArray, '/red_objects', 10)  # Same as red_object_detector
        self.visualization_pub = self.create_publisher(Image, '/inference_result', 1)
        # self.count_pub = self.create_publisher(Int32, '/pothole_count', 1)
        
        # Tracking
        self.detected_potholes = []
        self.detection_threshold = 50  # pixels
        self.marker_id = 0

    # def is_new_pothole(self, center):
    #     for existing in self.detected_potholes:
    #         if math.dist(center, existing) < self.detection_threshold:
    #             return False
    #     return True

    def image_callback(self, msg):
        try:
            # Convert and process image
            cv_image = bridge.imgmsg_to_cv2(msg, 'bgr8')
            results = self.model(cv_image, conf=0.5)
            
            # Prepare Detection2DArray (identical to red_object_detector.py)
            detections = Detection2DArray()
            detections.header = msg.header
            detections.header.frame_id = 'camera_rgb_optical_frame'  # Must match URDF!
            
            current_detections = []
            
            for result in results:
                for box in result.boxes:
                    b = box.xyxy[0].cpu().numpy()  # [x1,y1,x2,y2]
                    
                    # Calculate centroid (same as red detector)
                    center_x = (b[0] + b[2]) / 2
                    center_y = (b[1] + b[3]) / 2
                    
                    # if self.is_new_pothole((center_x, center_y)):
                    #     self.detected_potholes.append((center_x, center_y))
                    #     current_detections.append((center_x, center_y))
                    
                    # Create identical Detection2D message
                    detection = Detection2D()
                    bbox = BoundingBox2D()
                    bbox.center.position.x = float(center_x)
                    bbox.center.position.y = float(center_y)
                    bbox.size_x = float(b[2] - b[0])
                    bbox.size_y = float(b[3] - b[1])
                    detection.bbox = bbox
                    detections.detections.append(detection)
            
            # Publish (same topics as red_object_detector)
            self.detection_pub.publish(detections)
            # self.count_pub.publish(Int32(data=len(current_detections)))
            
            # Optional visualization
            annotated = results[0].plot()
            self.visualization_pub.publish(bridge.cv2_to_imgmsg(annotated, 'bgr8'))
            
        except Exception as e:
            self.get_logger().error(f'Detection error: {str(e)}')

def main():
    rclpy.init()
    node = PotholeDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()