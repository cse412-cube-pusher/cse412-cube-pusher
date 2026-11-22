#!/usr/bin/env python3
import curses
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__("keyboard_teleop")
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)
        self.declare_parameter("linear_speed", 0.15)
        self.declare_parameter("angular_speed", 0.5)
        self.declare_parameter("key_timeout", 0.8)

        self.speed = float(self.get_parameter("linear_speed").value)
        self.turn = float(self.get_parameter("angular_speed").value)
        self.timeout = float(self.get_parameter("key_timeout").value)

        if not 0 < self.speed <= 0.8:
            raise ValueError("linear_speed: 0 < hiz <= 0.8 olmali.")
        if not 0 < self.turn <= 1.5:
            raise ValueError("angular_speed: 0 < hiz <= 1.5 olmali.")
        if self.timeout <= 0:
            raise ValueError("key_timeout pozitif olmali.")

    def send(self, linear=0.0, angular=0.0):
        message = Twist()
        message.linear.x = linear
        message.angular.z = angular
        self.publisher.publish(message)

    def run(self, screen):
        screen.keypad(True)
        screen.nodelay(True)

        bindings = {}
        for keys, command in [
            ((curses.KEY_UP, ord("w"), ord("W")), (self.speed, 0.0)),
            ((curses.KEY_DOWN, ord("s"), ord("S")), (-self.speed, 0.0)),
            ((curses.KEY_LEFT, ord("a"), ord("A")), (0.0, self.turn)),
            ((curses.KEY_RIGHT, ord("d"), ord("D")), (0.0, -self.turn)),
        ]:
            for key in keys:
                bindings[key] = command

        linear = 0.0
        angular = 0.0
        last_key_time = time.monotonic()

        while rclpy.ok():
            key = screen.getch()

            while key != -1:
                if key in (ord("q"), ord("Q")):
                    return

                if key in bindings:
                    linear, angular = bindings[key]
                    last_key_time = time.monotonic()
                elif key != curses.KEY_RESIZE:
                    linear, angular = 0.0, 0.0

                key = screen.getch()

            if time.monotonic() - last_key_time > self.timeout:
                linear, angular = 0.0, 0.0

            self.send(linear, angular)
            rclpy.spin_once(self, timeout_sec=0.0)

            lines = [
                "ROBOT KONTROLU",
                "",
                "Oklar / WASD : Hareket",
                "Space        : Dur",
                "Q / Ctrl+C   : Cikis",
                "",
                f"Ileri hiz : {linear:.2f} m/s",
                f"Donus hizi: {angular:.2f} rad/s",
            ]

            try:
                screen.erase()
                rows, columns = screen.getmaxyx()

                for row, line in enumerate(lines):
                    if row < rows and columns > 1:
                        screen.addnstr(row, 0, line, columns - 1)

                screen.refresh()
            except curses.error:
                pass

            time.sleep(0.05)


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = None

    try:
        node = KeyboardTeleop()
        curses.wrapper(node.run)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            if rclpy.ok():
                for _ in range(5):
                    node.send()
                    time.sleep(0.03)

            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
