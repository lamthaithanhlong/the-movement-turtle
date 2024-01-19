#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import threading

class RobotController:
    def __init__(self):
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    def move_robot(self, linear_speed, angular_speed, duration):
        rate = rospy.Rate(10)  # 10 Hz
        move_cmd = Twist()
        move_cmd.linear.x = linear_speed
        move_cmd.angular.z = angular_speed

        for _ in range(int(10 * duration)):
            self.pub.publish(move_cmd)
            rate.sleep()

        move_cmd.linear.x = 0
        move_cmd.angular.z = 0
        self.pub.publish(move_cmd)

class HandleCommands(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command = json.loads(post_data)

            action = command.get('action')
            duration = command.get('duration', 1)

            robot_controller = RobotController()

            if action == 'forward':
                robot_controller.move_robot(0.2, 0, duration)
            elif action == 'backward':
                robot_controller.move_robot(-0.2, 0, duration)
            elif action == 'left':
                robot_controller.move_robot(0, 0.5, duration)
            elif action == 'right':
                robot_controller.move_robot(0, -0.5, duration)
            else:
                rospy.logwarn("Invalid action received")

            self.send_response(200)
            self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.end_headers()

def run_server():
    server_address = ('', 7000)
    httpd = HTTPServer(server_address, HandleCommands)
    rospy.loginfo("Starting HTTP Server...")
    httpd.serve_forever()

if __name__ == '__main__':
    rospy.init_node('api_command_receiver')
    run_server()
