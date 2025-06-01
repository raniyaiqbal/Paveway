import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from time import time

class InspectionTimer(Node):
    def __init__(self):
        super().__init__('inspection_timer')
        self.start_time = time()
        self.pub = self.create_publisher(Float32, '/inspection_time', 10)
        self.timer = self.create_timer(1.0, self.publish_elapsed_time)  # every 1 sec

    def publish_elapsed_time(self):
        elapsed = (time() - self.start_time) / 60.0  # minutes
        msg = Float32()
        msg.data = elapsed
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = InspectionTimer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()