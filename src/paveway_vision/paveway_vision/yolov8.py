#!/usr/bin/env python3
"""YOLOv8 pothole detector: sensor_msgs/Image -> vision_msgs/Detection2DArray."""
import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from vision_msgs.msg import BoundingBox2D, Detection2D, Detection2DArray, ObjectHypothesisWithPose
from ultralytics import YOLO


class PotholeDetector(Node):
    def __init__(self):
        super().__init__('pothole_detector')
        default_model = os.path.join(get_package_share_directory('paveway_vision'), 'models', 'v8.pt')
        p = self.declare_parameter
        model_path = os.path.expanduser(p('model_path', default_model).value)
        self.conf = p('confidence', 0.5).value
        self.frame_id = p('frame_id', '').value  # '' = keep the image's frame_id
        self.default_frame = p('default_frame', 'camera_rgb_optical_frame').value
        self.publish_annotated = p('publish_annotated', True).value
        image_topic = p('image_topic', '/image_raw').value

        self.model = YOLO(model_path)
        self.bridge = CvBridge()
        self.create_subscription(Image, image_topic, self.image_callback, qos_profile_sensor_data)
        self.detection_pub = self.create_publisher(Detection2DArray, '/pothole_detections', 10)
        self.visualization_pub = self.create_publisher(Image, '/inference_result', 1)
        self.get_logger().info(f'Loaded {model_path}; listening on {image_topic}')

    def image_callback(self, msg: Image):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            result = self.model(frame, conf=self.conf, verbose=False)[0]
        except Exception as e:  # keep the node alive on a bad frame
            self.get_logger().error(f'Detection error: {e}', throttle_duration_sec=2.0)
            return

        out = Detection2DArray()
        out.header = msg.header
        out.header.frame_id = self.frame_id or msg.header.frame_id or self.default_frame

        for box in result.boxes:
            x1, y1, x2, y2 = (float(v) for v in box.xyxy[0].cpu().numpy())
            det = Detection2D()
            det.header = out.header
            det.bbox = BoundingBox2D()
            det.bbox.center.position.x = (x1 + x2) / 2.0
            det.bbox.center.position.y = (y1 + y2) / 2.0
            det.bbox.size_x = x2 - x1
            det.bbox.size_y = y2 - y1
            hyp = ObjectHypothesisWithPose()
            hyp.hypothesis.class_id = result.names[int(box.cls[0])]
            hyp.hypothesis.score = float(box.conf[0])
            det.results.append(hyp)
            out.detections.append(det)

        self.detection_pub.publish(out)
        if self.publish_annotated and self.visualization_pub.get_subscription_count() > 0:
            annotated = self.bridge.cv2_to_imgmsg(result.plot(), 'bgr8')
            annotated.header = msg.header
            self.visualization_pub.publish(annotated)


def main(args=None):
    rclpy.init(args=args)
    node = PotholeDetector()
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
