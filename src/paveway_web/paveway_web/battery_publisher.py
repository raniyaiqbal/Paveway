import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Float32
from collections import deque

class BatteryPercentagePublisher(Node):
    def __init__(self):
        super().__init__('battery_percentage_publisher')
        self.sub = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )
        self.pub = self.create_publisher(Float32, '/battery_percentage', 10)
        self.window = deque(maxlen=40)

    def battery_callback(self, msg: BatteryState):
        self.window.append(msg.percentage)
        smoothed = sum(self.window) / len(self.window)

        percentage_msg = Float32()
        percentage_msg.data = smoothed
        self.pub.publish(percentage_msg)

def main(args=None):
    rclpy.init(args=args)
    node = BatteryPercentagePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
