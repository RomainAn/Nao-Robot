#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < xpserver.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/26 >
#	> Last Changed: 
#	> Description:		Nao Robot 远程控制-服务器端
#						接受客户端发来的指令，执行相应功能。
#						自动载入该模块，自动载入配置文件：/home/nao/naoqi/preferences/autoload.ini
# 						启动模块事件：连续三击机器人胸前按钮
#						关闭模块事件：同上；
#################################################################

""" Triple Click Nao ChestButton turn on / off python programe.

"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

import socket
import sys      # sys.exit() 退出main函数
import almath   # 角度转弧度(almath.TO_RAD)
import thread   # 多线程
import time     # 延时函数 time.sleep(1)

LISTEN_PORT = 8001 # 服务器监听端口

# Command 定义
COMMAND_WAKEUP = 'WAKEUP'
COMMAND_REST = 'REST'

COMMAND_FORWARD = 'FORWARD'
COMMAND_BACK = 'BACK'
COMMAND_LEFT = 'LEFT'
COMMAND_RIGHT = 'RIGHT'
COMMAND_STOP = 'STOP'

COMMAND_TURNLEFT = 'TURNLEFT'
COMMAND_TURNRIGHT = 'TURNRIGHT'

COMMAND_DISCONNECT = 'DISCONNECT'
COMMAND_SENSOR = 'SENSOR'

# 头部动作
COMMAND_HEADYAW = 'HEADYAW'     # 头左右
COMMAND_HEADPITCH = 'HEADPITCH' # 头上下
# 手臂动作
COMMAND_ARMREST = 'ARMREST' 
COMMAND_LARMOPEN = 'LARMOPEN'
COMMAND_LARMCLOSE = 'LARMCLOSE'
COMMAND_LARMUP = 'LARMUP'
COMMAND_LARMDOWN = 'LARMDOWN'
COMMAND_RARMOPEN = 'RARMOPEN'
COMMAND_RARMCLOSE = 'RARMCLOSE'
COMMAND_RARMUP = 'RARMUP'
COMMAND_RARMDOWN = 'RARMDOWN'

# flag
CONNECT = False         # 客户端连接Flag    
SENSOR  = False         # 传感器监控Flag, 为True则有线程定时发送数据；
CLICK = False			# 按钮Flag, 按三下CLICK变True, 再按三下变会False;

# 全局变量，供其他函数使用
ROBOT_IP = '192.168.1.100'
ROBOT_PORT = 9559
connection = None
tts = motion = memory = battery = autonomous = None

TripleClick = None 		# TripleClickModule是定义的一个类，而TripleClick是一个类实体。

class TripleClickModule(ALModule):
	""" A module able to react
	to Event: "ALChestButton/TripleClickOccurred"

	"""
	def __init__(self, name):
		ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
		global tts, motion, memory, battery, autonomous
		tts = ALProxy("ALTextToSpeech")
		motion = ALProxy("ALMotion")
#		posture = ALProxy("ALRobotPosture")
		memory = ALProxy("ALMemory")
#		leds = ALProxy("ALLeds")
		battery = ALProxy("ALBattery")
		autonomous = ALProxy("ALAutonomousLife")
		

        # Subscribe to the TripleClickOccurred event:
		memory.subscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick",
			"onTripleClickOccurred")

	def onTripleClickOccurred(self, *_args): # 对应事件的callback函数
		""" This will be called each time TripleClickOccurred.

		"""
        # Unsubscribe to the event when talking,
        # to avoid repetitions, 暂时取消订阅，预防冲突;
		memory.unsubscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick")

		# 由于双击ChestButton会开启ALAutonomousLife，这里需要再一次关闭
		# turn ALAutonomousLife off
		autonomous.setState("disabled") 

		# ------------------> Start <----------------------
		global CLICK
		if CLICK == False:	# 启动程序
			CLICK = True
			tts.say("Hello, I am nao robot.")
		else:				# 关闭程序	
			CLICK = False
			tts.say("B B E E U U")
		# ------------------> End <------------------------
        # Subscribe again to the event
		memory.subscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick",
			"onTripleClickOccurred")
	

def main():
	""" Main entry point

	"""
	# ----------> 命令行解析 <----------
	parser = OptionParser()
	parser.add_option("--pip",
		help="Parent broker port. The IP address or your robot",
		dest="pip")
	parser.add_option("--pport",
		help="Parent broker port. The port NAOqi is listening to",
		dest="pport",
		type="int")
	parser.set_defaults(
		pip=ROBOT_IP,
		pport=9559)

	(opts, args_) = parser.parse_args()
	pip   = opts.pip
	pport = opts.pport

	# ----------> 创建python broker <----------
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
	myBroker = ALBroker("myBroker",
		"0.0.0.0",   # listen to anyone
		0,           # find a free port and use it
		pip,         # parent broker IP
		pport)       # parent broker port


    # Warning: TripleClick must be a global variable
    # The name given to the constructor must be the name of the
    # variable
	global TripleClick
	TripleClick = TripleClickModule("TripleClick") # 在__init__中，订阅相应事件;

	while CLICK == False:
		time.sleep(1)

	# ----------> 开启socket服务器监听端口 <----------
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((ROBOT_IP, LISTEN_PORT))
	sock.listen(10)

	global connection
	global CONNECT
	try:
		while True:		# 死循环	
			if CLICK == True: 	# 等待客户端连接，单线程监听单一客户端; 
				connection,address = sock.accept()
				tts.say("socket connecting...")
				CONNECT = True
				while (CONNECT == True) and (CLICK == True): # 与客户端进行通信
					# 服务器接受指令
					buf = connection.recv(1024)
					print "get:[", buf, "]"
					# 根据接受的命令执行不同操作
					Operation(connection, buf)			
				connection.close()  # 关闭当前socket连接，进入下一轮循环
				tts.say("socket connection is closed.")
				CONNECT = False
			else:
				time.sleep(1)

	except KeyboardInterrupt:
		print
		print "Interrupted by user, shutting down"
		myBroker.shutdown()
		sys.exit(0)

def Operation(connection, command):	# 根据指令执行相应操作
	if command == COMMAND_WAKEUP:							# wakeup
		motion.post.wakeUp()
	elif command == COMMAND_REST:							# rest
		motion.post.rest()
	elif command == COMMAND_FORWARD:						# forward
		mymoveinit()
		motion.move(0.1, 0, 0) # 固定速率持续行走	
	elif command == COMMAND_BACK:							# back
		mymoveinit()
		motion.move(-0.1, 0, 0)
	elif command == COMMAND_LEFT:							# left
		mymoveinit()
		motion.move(0, 0.1, 0)
	elif command == COMMAND_RIGHT:							# right
		mymoveinit()
		motion.move(0, -0.1, 0)
	elif command == COMMAND_STOP:							# stop
		motion.stopMove()
	elif command == COMMAND_TURNLEFT:						# turn left
		mymoveinit()
		motion.move(0, 0, 0.3)
	elif command == COMMAND_TURNRIGHT:						# turn right
		mymoveinit()
		motion.move(0, 0, -0.3)
	elif command == COMMAND_DISCONNECT:						# disconnect
		global CONNECT
		CONNECT = False
	elif command == COMMAND_HEADYAW:						# head yaw
		# 头部左右转动(Yaw轴)
		command2 = connection.recv(1024)    # 读取Yaw值
		angles = (int(command2) - 50) * 2
		motion.setStiffnesses("Head", 1.0)
		motion.setAngles("HeadYaw", angles * almath.TO_RAD, 0.2)
	elif command == COMMAND_HEADPITCH:						# head pitch
		# 头部上下转动(Pitch轴)
		command2 = connection.recv(1024)    # 读取Yaw值
		angles = (int(command2) - 50)
		motion.setStiffnesses("Head", 1.0)
		motion.setAngles("HeadPitch", angles * almath.TO_RAD, 0.2)
	elif command == COMMAND_SENSOR:							# sensor
		global SENSOR
		if SENSOR == False:
			# 开启新线程，定时发送传感器数据
			SENSOR = True
			thread.start_new_thread(sensor, (1,)) # 2nd arg must be a tuple
		else:
			# 第二次发送COMMAND_SENSOR, 则关闭线程
			SENSOR = False  # 设置标识位，线程检测后自己退出。
	elif command == COMMAND_ARMREST:						# arm rest
		motion.setAngles('LShoulderPitch', 1, 0.2)
		motion.setAngles('LShoulderRoll', 0.3, 0.2)
		motion.setAngles('LElbowYaw', -1.3, 0.2)
		motion.setAngles('LElbowRoll', -0.5, 0.2)
		motion.setAngles('LWristYaw', 0, 0.2)
		motion.setAngles('LHand', 0, 0.2)	
		motion.setAngles('RShoulderPitch', 1, 0.2)
		motion.setAngles('RShoulderRoll', -0.3, 0.2)
		motion.setAngles('RElbowYaw', 1.3, 0.2)
		motion.setAngles('RElbowRoll', 0.5, 0.2)
		motion.setAngles('RWristYaw', 0, 0.2)
		motion.setAngles('RHand', 0, 0.2)
	elif command == COMMAND_LARMOPEN:						# left hand open
		motion.post.openHand("LHand")
	elif command == COMMAND_LARMCLOSE:						# left hand close
		motion.post.closeHand("LHand")
	elif command == COMMAND_RARMOPEN:						# Right hand open
		motion.post.openHand("RHand")
	elif command == COMMAND_RARMCLOSE:						# Right hand close
		motion.post.closeHand("RHand")
	elif command == COMMAND_LARMUP:							# left arm up
		motion.setAngles('LShoulderPitch', 0.7, 0.2)
		motion.setAngles('LShoulderRoll', 0.3, 0.2)
		motion.setAngles('LElbowYaw', -1.5, 0.2)
		motion.setAngles('LElbowRoll', -0.5, 0.2)
		motion.setAngles('LWristYaw', -1.7, 0.2)
	elif command == COMMAND_LARMDOWN:						# left arm down
		motion.setAngles('LShoulderPitch', 1, 0.2)
		motion.setAngles('LShoulderRoll', 0.3, 0.2)
		motion.setAngles('LElbowYaw', -1.3, 0.2)
		motion.setAngles('LElbowRoll', -0.5, 0.2)
		motion.setAngles('LWristYaw', 0, 0.2)
	elif command == COMMAND_RARMUP:							# right arm up
		motion.setAngles('RShoulderPitch', 0.7, 0.2)
		motion.setAngles('RShoulderRoll', -0.3, 0.2)
		motion.setAngles('RElbowYaw', 1.5, 0.2)
		motion.setAngles('RElbowRoll', 0.5, 0.2)
		motion.setAngles('RWristYaw', 1.7, 0.2)
	elif command == COMMAND_RARMDOWN:						# right arm down
		motion.setAngles('RShoulderPitch', 1, 0.2)
		motion.setAngles('RShoulderRoll', -0.3, 0.2)
		motion.setAngles('RElbowYaw', 1.3, 0.2)
		motion.setAngles('RElbowRoll', 0.5, 0.2)
		motion.setAngles('RWristYaw', 0, 0.2)
	else:													# error
		pass
#		connection.send(command + ": command not found\r")

def mymoveinit():
	"""判断机器人是否为站立状态，不是站立状态，则更改站立状态，并进行MoveInit.
	"""
	if motion.robotIsWakeUp() == False:
	   motion.post.wakeUp()
	   motion.post.moveInit()
	else:
		pass

def sensor(interval):
	''' 每interval秒，发送一次传感器数据
	'''
	while SENSOR == True:
		connection.send("BATTERY" + "#" + str(battery.getBatteryCharge()) + "\r")
		connection.send("SONAR1" + "#" + str(memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")) + "\r")
		connection.send("SONAR2" + "#" + str(memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")) + "\r")
	else:													# error
		pass
#		connection.send(command + ": command not found\r")

def mymoveinit():
	"""判断机器人是否为站立状态，不是站立状态，则更改站立状态，并进行MoveInit.
	"""
	if motion.robotIsWakeUp() == False:
	   motion.post.wakeUp()
	   motion.post.moveInit()
	else:
		pass

def sensor(interval):
	''' 每interval秒，发送一次传感器数据
	'''
	while SENSOR == True:
		connection.send("BATTERY" + "#" + str(battery.getBatteryCharge()) + "\r")
		connection.send("SONAR1" + "#" + str(memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")) + "\r")
		connection.send("SONAR2" + "#" + str(memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")) + "\r")
		time.sleep(interval)
	# SENSOR == False
	thread.exit_thread()

if __name__ == "__main__":
	main()
