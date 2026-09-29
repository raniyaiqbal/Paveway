"""Projects an image pixel onto the ground plane (no ROS imports).

Camera optical frame: +z forward, +x right, +y down.
Target frame (e.g. base_footprint): ground at z = 0.
"""
import numpy as np


def quat_to_rot(x, y, z, w):
    """Unit quaternion (x, y, z, w) -> 3x3 rotation matrix."""
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ])


def project_to_ground(u, v, fx, fy, cx, cy, rotation, translation):
    """Intersect the ray through pixel (u, v) with the ground plane z = 0.

    rotation/translation: pose of the camera optical frame in the target frame.
    Returns the point in the target frame, or None if the ray does not hit the
    ground in front of the camera (at or above the horizon).
    """
    origin = np.asarray(translation, dtype=float)
    direction = rotation @ np.array([(u - cx) / fx, (v - cy) / fy, 1.0])
    if direction[2] >= -1e-9:
        return None
    s = -origin[2] / direction[2]
    return origin + s * direction
