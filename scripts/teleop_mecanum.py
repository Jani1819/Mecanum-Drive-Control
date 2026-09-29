#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import pygame
import threading
import time


class MecanumJoystickTeleop(Node):
    def __init__(self):
        super().__init__("mecanum_joystick_teleop")

        # Publisher for /cmd_vel
        self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # Initialize joystick
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.get_logger().error("No joystick detected!")
            raise RuntimeError("No joystick detected")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.get_logger().info(
            f"Joystick detected: {self.joystick.get_name()}"
        )

        # Deadzone to ignore small joystick drift
        self.deadzone = 0.05

        # Run joystick read loop in a separate thread
        self.running = True
        self.thread = threading.Thread(target=self.joy_loop, daemon=True)
        self.thread.start()

    def dz(self, value):
        """Apply a deadzone to a joystick axis value."""
        return value if abs(value) >= self.deadzone else 0.0

    def joy_loop(self):
        rate = 0.05  # 20 Hz

        while self.running:
            pygame.event.pump()

            # Axis mapping from the supplied joystick program
            forward = self.dz(-self.joystick.get_axis(1))
            rotate = self.dz(self.joystick.get_axis(4))
            strafe = self.dz(self.joystick.get_axis(3))

            # Initialize Twist with zeros
            twist = Twist()

            # CLOCKWISE / ANTICLOCKWISE
            if abs(rotate) > 0:
                twist.linear.x = 1.0 * rotate
                twist.linear.y = 1.0 * rotate

            # FORWARD / BACKWARD
            if abs(forward) > 0:
                twist.angular.y = -5.0 * forward
                twist.angular.z = -5.0 * forward

            # LEFT / RIGHT STRAFING
            if abs(strafe) > 0:
                twist.linear.x = 2.0 * strafe
                twist.linear.y = -2.0 * strafe

            # Publish the command
            self.cmd_vel_pub.publish(twist)
            time.sleep(rate)

    def destroy_node(self):
        self.running = False

        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

        pygame.quit()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MecanumJoystickTeleop()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
