#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < avoidance.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/30 >
#	> Last Changed: 
#	> Description:		使用机器人的超声波实现避障
#################################################################

import argparse
import time
from naoqi import ALProxy
import sys
import almath			# almath.TO_RAD, 角度转弧度

# 障碍物标志
OBSTACLE_L = False 	# True则左侧有障碍
OBSTACLE_R = False  # True则右侧有障碍
OBSTACLE_ON = True	# 避障标志位，为False时退出避障循环

OBSTACLE_DISTANCE = 0.5	# 设置检测的安全距离
OBSTACLE_DELAY = 0.3	# 设置延时事件, 单位：秒
MOVE_SPEED = 0.4		# 移动速度, 单位: m/s
TURN_ANGLE = 20			# 旋转角度，单位: 度

tts = motion = memory = sonar = None

def main(robot_IP, robot_PORT=9559):
	# ----------> Connect to robot <----------
	try:
		global tts, motion, memory, sonar
		tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
		motion = ALProxy("ALMotion", robot_IP, robot_PORT)
		memory = ALProxy("ALMemory", robot_IP, robot_PORT)
		sonar = ALProxy("ALSonar", robot_IP, robot_PORT)
	except Exception, e:
		print "Could not create proxy by ALProxy"
		print "Error was: ", e
	# ----------> <----------
	motion.wakeUp()
	motion.moveInit()
	try:
		obstacle()
	except KeyboardInterrupt:
		# 中断程序
		OBSTACLE_ON = False
		motion.stopMove()
		motion.rest()
		print "Interrupted by user, shutting down"
		sys.exit(0)

def obstacle():
	''' 
		固定间隔循环检测是否存在障碍，根据障碍物标志决定机器人的行走方向
	'''
	global OBSTACLE_L, OBSTACLE_R, OBSTACLE_ON

	sonar.subscribe("my_obstacle")
	while OBSTACLE_ON == True:			# 避障标识为True，则持续循环检测
		# 1. 检测障碍物
		check()
		# 2. 根据障碍物标志决定行走方向
		operation(OBSTACLE_L, OBSTACLE_R)	
		# 3. 延时
		time.sleep(OBSTACLE_DELAY)
	sonar.unsubscribe("my_obstacle")
	

def check():
	'''
		检测超声波数值，设置标志位
	'''
	left = memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
	right = memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")

	global OBSTACLE_L, OBSTACLE_R
	if left > OBSTACLE_DISTANCE: 		# 超过安全距离，无障碍
		OBSTACLE_L = False
	else:								# 小于安全距离，有障碍
		OBSTACLE_L = True
	if right > OBSTACLE_DISTANCE: 		# 超过安全距离，无障碍
		OBSTACLE_R = False
	else:								# 小于安全距离，有障碍
		OBSTACLE_R = True

# 	FLAG_L		FLAG_R				operation
# 	False		False				无障碍物，直走
#	False		True				右侧障碍，左转
#	True		False				左侧障碍，右转
#	True		True				左右障碍，左转
def operation(flag_L, flag_R):
	if flag_L == False:
		if flag_R == False:
			motion_go()			
		else:
			motion_turn_left()
	else:
		if flag_R == False:
			motion_turn_right()
		else:
			motion_turn_left()

def motion_go():
	motion.move(MOVE_SPEED, 0, 0)
def motion_turn_left():
	motion.post.moveTo(0, 0, TURN_ANGLE * almath.TO_RAD)
def motion_turn_right():
	motion.post.moveTo(0, 0, -1.0 * TURN_ANGLE * almath.TO_RAD)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", type=str, default="192.168.1.100", help="Robot ip address")
	parser.add_argument("--port", type=int, default=9559, help="Robot port number")
	args = parser.parse_args()
	# ----------> 执行main函数 <----------
	main(args.ip, args.port)
