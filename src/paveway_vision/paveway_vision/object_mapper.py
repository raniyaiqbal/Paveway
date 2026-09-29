#!/usr/bin/env python3
import math

import numpy as np
import rclpy
import tf2_ros
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo
from std_msgs.msg import ColorRGBA
from vision_msgs.msg import Detection2DArray
from visualization_msgs.msg import Marker, MarkerArray

from paveway_vision.geometry import project_to_ground, quat_to_rot


def to_rt(tf):
    q, t = tf.transform.rotation, tf.transform.translation
    return quat_to_rot(q.x, q.y, q.z, q.w), np.array([t.x, t.y, t.z])


class ObjectMapper(Node):
    def __init__(self):
        super().__init__('object_mapper')
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.subscription = self.create_subscription(
            Detection2DArray, '/pothole_detections', self.detection_callback, 10)
        self.create_subscription(CameraInfo, '/camera/camera_info', self.camera_info_callback, 1)
        self.marker_pub = self.create_publisher(MarkerArray, '/object_markers', 10)

        # Default intrinsics (RealSense, 69° FOV, 640x480); replaced by CameraInfo when available
        self.fx = self.fy = 530.0
        self.cx, self.cy = 320.0, 240.0

        # Ground-plane frame (z = 0 at the floor)
        self.base_frame = 'base_footprint'

        # Persistent storage
        self.known_objects = []
        self.marker_id = 0

    def camera_info_callback(self, msg):
        if msg.k[0] > 0.0 and msg.k[4] > 0.0:
            self.fx, self.fy, self.cx, self.cy = msg.k[0], msg.k[4], msg.k[2], msg.k[5]

    def lookup(self, target, source, stamp):
        try:
            return self.tf_buffer.lookup_transform(target, source, stamp,
                                                   timeout=Duration(seconds=0.1))
        except tf2_ros.ExtrapolationException:
            # Detection is slightly older/newer than TF; use the latest transform
            return self.tf_buffer.lookup_transform(target, source, Time())

    def detection_callback(self, msg):
        if not msg.detections:
            return
        stamp = Time.from_msg(msg.header.stamp)
        try:
            # 1. Camera -> base and base -> map transforms
            r_bc, t_bc = to_rt(self.lookup(self.base_frame, msg.header.frame_id, stamp))
            r_mb, t_mb = to_rt(self.lookup('map', self.base_frame, stamp))
        except tf2_ros.TransformException as e:
            self.get_logger().warning(f'Transform failed: {e}', throttle_duration_sec=1.0)
            return

        for detection in msg.detections:
            centroid = detection.bbox.center.position

            # 2. Intersect the camera ray through the detection with the ground
            point = project_to_ground(centroid.x, centroid.y, self.fx, self.fy,
                                      self.cx, self.cy, r_bc, t_bc)
            if point is None:  # at or above the horizon
                continue

            distance = point[0]  # Pure forward distance
            self.get_logger().info(
                f'Pothole detected at: ({point[0]:.2f}, {point[1]:.2f}) | Distance: {distance:.2f}m',
                throttle_duration_sec=1.0)

            # 3. Only trust close detections, then convert to map frame
            if 0.15 <= distance <= 0.5:
                map_point = r_mb @ point + t_mb
                self.add_object_marker(map_point)

    def add_object_marker(self, position):
        x, y, z = (float(v) for v in position)
        # Check if object already exists nearby
        for obj in self.known_objects:
            if math.hypot(x - obj['x'], y - obj['y']) < 0.1:
                return

        # Add new object
        self.known_objects.append({'x': x, 'y': y, 'z': z, 'id': self.marker_id})

        # Publish all markers
        marker_array = MarkerArray()
        for obj in self.known_objects:
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.id = obj['id']
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = obj['x']
            marker.pose.position.y = obj['y']
            marker.pose.position.z = obj['z']
            marker.pose.orientation.w = 1.0
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
