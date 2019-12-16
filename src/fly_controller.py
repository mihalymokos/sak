#!/usr/bin/env python

# author: Mokos Mihaly

# import libs
import cv2
import sys
import rospy
import time

# import msgs
from natnet_msgs.msg import MarkerList
from sensor_msgs.msg import Image
from std_msgs.msg import Empty, UInt8
from std_msgs.msg import String
from geometry_msgs.msg import Twist, PoseStamped
from tello_driver.msg import TelloStatus
from cv_bridge import CvBridge, CvBridgeError

class FlyController():
	def __init__(self):

		# name of node
		rospy.init_node('tello_fly_controller', anonymous=True)

		# class variables
		self.key = None
		self.status = None
		self.in_air = False
		self.in_command = False
		self.flip_allowed = False
		self.command_msg = '0'
		self.flip_msg = 0
		self.velocity_msg = Twist()
		self.drone_pose = PoseStamped()
		self.destination_pose = PoseStamped()
		self.bridge = CvBridge()

		self.command1_executed = False
		self.command2_executed = False
		self.command3_executed = False
		self.command4_executed = False

		self.forward = 0
		self.right = 0
		self.speed = 0.1
		self.rate = rospy.Rate(30)

		# subscribers declaration
		# VRPN CLIENT
		rospy.Subscriber('/vrpn_client_node/tello/pose', PoseStamped, self.tello_pose_callback)
		rospy.Subscriber('/vrpn_client_node/destination/pose', PoseStamped, self.destination_pose_callback)

		# NATNET CLIENT
		# rospy.Subscriber('/mocap/markers/leftovers', MarkerList, self.tello_pose_callback)
		# rospy.Subscriber('/mocap/rigid_bodies/destination/pose', PoseStamped, self.destination_callback)

		rospy.Subscriber('/tello/camera/image_raw', Image, self.image_callback)
		rospy.Subscriber('/tello/status', TelloStatus, self.status_callback)
		rospy.Subscriber('/barcode', String, self.barcode_callback)
		rospy.Subscriber('/command', String, self.command_callback)

		# publishers declaration
		self.velocity_pub = rospy.Publisher('/tello/cmd_vel', Twist, queue_size=1)
		self.takeoff_pub = rospy.Publisher('/tello/takeoff', Empty,  queue_size=1)
		self.land_pub = rospy.Publisher('/tello/land', Empty,  queue_size=1)
		self.flip_pub = rospy.Publisher('/tello/flip', UInt8,  queue_size=1)

		self.command_pub = rospy.Publisher('/command', String, queue_size=1)

	# callback functions
	def command_callback(self, data):
		#rospy.loginfo('command')
		self.rate.sleep()
		self.command_msg = data.data

		# autonomous control
		if ((self.in_command == True) and (self.status == 6)):
			if (self.command_msg == '1'):
				rospy.loginfo('command 1')
				self.go_up()
				time.sleep(1)
				self.stop()
				time.sleep(2)
				self.go_forward()
				time.sleep(1)
				self.stop()
				time.sleep(2)
				self.turn_right()
				time.sleep(2)
				self.stop()
				self.command1_executed = True
			elif (self.command_msg == '2'):
				rospy.loginfo('command 2')
				self.go_forward()
				time.sleep(2)
				self.stop()
				self.turn_left()
				time.sleep(2)
				self.go_forward()
				time.sleep(2)
				self.stop()
				self.command3_executed = True
			elif (self.command_msg == '3'):
				rospy.loginfo('command 3')
				self.turn_right()
				time.sleep(2)
				self.stop()
				self.go_forward()
				time.sleep(1)
				self.stop()
				self.turn_right()
				time.sleep(1)
				self.go_forward()
				time.sleep(6)
				self.stop()
				self.command3_executed =  True
			elif (self.command_msg == '4'):
				rospy.loginfo('command 4')
				self.send_land()
				self.stop()
				self.command4_executed = True

		self.command_msg = None
		self.in_command = False

	def barcode_callback(self, data):
		# rospy.loginfo('barcode')
		# self.rate.sleep()

		if ((self.status == 6) and (self.in_air == True) and (self.in_command == False)):
			self.command_pub.publish(data)
			self.in_command = True

	def image_callback(self, data):
		# rospy.loginfo('image')
		self.rate.sleep()

		try:
			cv_image = self.bridge.imgmsg_to_cv2(data, 'bgr8')
		except CvBridgeError as e:
			print(e)

		cv2.imshow('Image Window', cv_image)
		cv_key = cv2.waitKey(3)
		cv2.namedWindow('Image Window', 1)


		self.key = chr(cv_key) if cv_key != -1 else False

		if(self.key == 'b'):
			rospy.loginfo('flip allowed - (b) || press (n) to disallow')
			self.flip_allowed = True
		elif(self.key == 'n'):
			rospy.loginfo('flip disallowed - (n) || press (b) to allow')
			self.flip_allowed = False

		# manual control
		elif ((self.key == 'y') and (self.status == 6)):
			rospy.loginfo('take off - (y)')
			self.send_takeoff()
			self.go_up()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'x') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('land - (x)')
			self.send_land()
		elif ((self.key == 'w') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('go forward - (w)')
			self.go_forward()
			time.sleep(1)
			self.stop()
		elif ((self.key == 's') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('go backward - (s)')
			self.go_backward()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'a') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('go left - (a)')
			self.go_left()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'd') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('go right - (d)')
			self.go_right()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'q') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('turn left - (q)')
			self.turn_left()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'e') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('turn right - (e)')
			self.turn_right()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'r') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('go up - (r)')
			self.go_up()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'f') and (self.status == 6) and (self.in_air == True)):
			rospy.loginfo('go down - (f)')
			self.go_down()
			time.sleep(1)
			self.stop()
		elif ((self.key == 'z') and (self.status == 6) and (self.in_air == True)):
			if (self.flip_allowed == True):
				rospy.loginfo('flip forward - (z)')
				self.flip_forward()
				time.sleep(2)
				self.stop()
			elif (self.flip_allowed == False):
				rospy.loginfo('flip not allowed || press (b) to allow')
		elif ((self.key == 'h') and (self.status == 6) and (self.in_air == True)):
			if (self.flip_allowed == True):
				rospy.loginfo('flip backward - (h)')
				self.flip_backward()
				time.sleep(2)
				self.stop()
			elif (self.flip_allowed == False):
				rospy.loginfo('flip not allowed || press (b) to allow')

	def tello_pose_callback(self, data):
			# rospy.loginfo('tello pose')
			drone_pose = data

	def destination_pose_callback(self, data):
			#rospy.loginfo('destination pose')
			destination_pose = data

	def status_callback(self, data):
		# rospy.loginfo('status')
		self.status = data.fly_mode

	# command functions
	def send_takeoff(self):
		self.takeoff_pub.publish()
		self.in_air = True

	def send_land(self):
		self.land_pub.publish()
		self.in_air = False

	def go_forward(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = 1
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def go_backward(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = -1
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def go_left(self):
		self.velocity_msg.linear.x = -1
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def go_right(self):
		self.velocity_msg.linear.x = 1
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def turn_left(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = -1
		self.velocity_pub.publish(self.velocity_msg)

	def turn_right(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 1
		self.velocity_pub.publish(self.velocity_msg)

	def go_up(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = 1
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def go_down(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = -1
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def stop(self):
		self.velocity_msg.linear.x = 0
		self.velocity_msg.linear.y = 0
		self.velocity_msg.linear.z = 0
		self.velocity_msg.angular.x = 0
		self.velocity_msg.angular.y = 0
		self.velocity_msg.angular.z = 0
		self.velocity_pub.publish(self.velocity_msg)

	def flip_forward(self):
		self.flip_msg = 0
		self.flip_pub.publish(self.flip_msg)

	def flip_backward(self):
		self.flip_msg = 2
		self.flip_pub.publish(self.flip_msg)

def main(args):
		f = FlyController()
		try:
			rospy.spin()
		except KeyboardInterrupt:
			print("Shutting down")
		cv2.destroyAllWindows()

if __name__ == '__main__':
	main(sys.argv)
