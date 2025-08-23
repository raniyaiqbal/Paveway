#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import PoseStamped, Point
from vision_msgs.msg import Detection2DArray
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA
import math

class ObjectMapper(Node):
    def __init__(self):
        super().__init__('object_mapper')
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        self.subscription = self.create_subscription(
            Detection2DArray, '/red_objects', self.detection_callback, 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/object_markers', 10)
        
        # Camera parameters (RealSense, 69° FOV, 640x480)
        self.focal_length = 530.0  # pixels
        self.principal_point = (320.0, 240.0)  # Center of 640x480 image
        self.camera_height = 0.13  # meters, from URDF
        
        # Persistent storage
        self.known_objects = []
        self.marker_id = 0

    def detection_callback(self, msg):
        try:
            # 1. Get camera to base_link transform
            camera_to_base = self.tf_buffer.lookup_transform(
                'base_link', 
                'camera_link',  # Changed from msg.header.frame_id
                msg.header.stamp,
                timeout=rclpy.duration.Duration(seconds=0.1))
            
            for detection in msg.detections:
                centroid = detection.bbox.center.position
                
                # 2. Calculate real-world coordinates
                x_img = centroid.x - self.principal_point[0]
                y_img = centroid.y - self.principal_point[1]
                Z = (self.focal_length * self.camera_height) / y_img
                X = (x_img * Z) / self.focal_length
                
                # 3. Create pose in camera optical frame
                object_pose = PoseStamped()
                object_pose.header.frame_id = msg.header.frame_id
                object_pose.header.stamp = msg.header.stamp
                object_pose.pose.position.x = X
                object_pose.pose.position.y = 0.0  # Ground plane assumption
                object_pose.pose.position.z = Z
                object_pose.pose.orientation.w = 1.0  # Neutral orientation
                
                try:
                    # 4. Transform to base_link
                    base_pose = self.tf_buffer.transform(
                        object_pose, 
                        'base_link',
                        timeout=rclpy.duration.Duration(seconds=0.1))
                    
                    distance = base_pose.pose.position.x  # Pure forward distance

                    self.get_logger().info(
                        f"Pothole detected at: ({base_pose.pose.position.x:.2f}, " 
                        f"{base_pose.pose.position.y:.2f}, {base_pose.pose.position.z:.2f}) | "
                        f"Distance: {distance:.2f}m",
                        throttle_duration_sec=1.0
                    )

                    # 5. Simple forward distance check
                    if 0.15 <= distance <= 0.5:  # 20cm ±2cm tolerance
                        map_pose = self.tf_buffer.transform(
                            base_pose,
                            'map',
                            timeout=rclpy.duration.Duration(seconds=0.1))
                        self.add_object_marker(map_pose.pose.position)
                        
                except tf2_ros.TransformException as e:
                    self.get_logger().warning(f'Base transform failed: {e}')
                    
        except tf2_ros.TransformException as e:
            self.get_logger().warning(f'Camera transform failed: {e}')

    def add_object_marker(self, position):
        # Check if object already exists nearby
        for obj in self.known_objects:
            if math.sqrt((position.x - obj['x'])**2 + (position.y - obj['y'])**2) < 0.1:
                return
        
        # Add new object
        self.known_objects.append({
            'x': position.x,
            'y': position.y,
            'z': position.z,
            'id': self.marker_id
        })
        
        # Publish all markers
        marker_array = MarkerArray()
        for obj in self.known_objects:
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.id = obj['id']
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = obj['x']
            marker.pose.position.y = obj['y']
            marker.pose.position.z = obj['z']
            marker.scale.x = 0.05
            marker.scale.y = 0.05
            marker.scale.z = 0.05
            marker.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0)
            marker.lifetime.sec = 0  # Persistent
            marker_array.markers.append(marker)
        
        self.marker_pub.publish(marker_array)
        self.marker_id += 1

def main(args=None):
    rclpy.init(args=args)
    node = ObjectMapper()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()