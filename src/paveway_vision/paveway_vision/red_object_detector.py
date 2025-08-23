#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, BoundingBox2D
from cv_bridge import CvBridge

class RedObjectDetector(Node):
    def __init__(self):
        super().__init__('red_object_detector')
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(Detection2DArray, '/red_objects', 10)
        self.bridge = CvBridge()
        
        # Red color thresholds (HSV space)
        self.lower_red1 = np.array([0, 120, 70])
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([170, 120, 70])
        self.upper_red2 = np.array([180, 255, 255])

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        # Threshold for red color
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = Detection2DArray()
        detections.header = msg.header
        detections.header.frame_id = 'camera_rgb_optical_frame'
        
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Minimum area threshold
                # Create bounding box
                x, y, w, h = cv2.boundingRect(contour)
                bbox = BoundingBox2D()
                bbox.center.position.x = float(x + w/2)
                bbox.center.position.y = float(y + h/2)
                bbox.size_x = float(w)
                bbox.size_y = float(h)
                
                detection = Detection2D()
                detection.bbox = bbox
                detections.detections.append(detection)
        
        self.publisher.publish(detections)

def main(args=None):
    rclpy.init(args=args)
    node = RedObjectDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()