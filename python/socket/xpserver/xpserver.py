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
#################################################################

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

# <------------------------------------------------------------->
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
# 语音
COMMAND_SAY = 'SAY'
# 姿势
COMMAND_POSTURE_STAND = 'POSTURE_STADN'					# 站立
COMMAND_POSTURE_MOVEINIT = 'POSTURE_STADNINIT' 			# 行走预备
COMMAND_POSTURE_STANDZERO = 'POSTURE_STADNZERO'			# 站立零位 
COMMAND_POSTURE_CROUCH = 'POSTURE_CROUCH'				# 蹲
COMMAND_POSTURE_SIT = 'POSTURE_SIT'						# 坐下	
COMMAND_POSTURE_SITRELAX = 'POSTURE_SITRELAX'			# 坐下休息	
COMMAND_POSTURE_LYINGBELLY = 'POSTURE_LYINGBELLY'		# 趴下
COMMAND_POSTURE_LYINGBACK = 'POSTURE_LYINGBACK'			# 躺下

# <------------------------------------------------------------->
# flag
CONNECT_FLAG = False         # 客户端连接Flag    
SENSOR_FLAG  = False         # 传感器监控Flag, 为True则有线程定时发送数据；
# <------------------------------------------------------------->
# 全局变量，供其他函数使用
ROBOT_IP = '192.168.1.100'
ROBOT_PORT = 9559
connection = None				# socket连接
tts = motion = memory = battery = autonomous = posture = leds = None

# <------------------------------------------------------------->
# 设定Head/Touch/Front=1,Head/Touch/Middle=2,Head/Touch/Rear=3
HEAD_FRONT = 1
HEAD_MIDDLE = 2
HEAD_REAR = 3

# 密码序列，只有按照下面序列依次触摸机器人，才会通过验证；
PASSWORD = [1,3,2,3,1,2]
PASSWD = []

VERIFY_FLAG = False			# 密码验证标志，成功验证时改为True

# Global variable to store the FrontTouch module instance
FrontTouch = None			# 密码序列：1
MiddleTouch = None			# 密码序列：2
RearTouch = None			# 密码序列：3
LeftFootTouch = None		# 确定密码
RightFootTouch = None		# 清空密码
# <------------------------------------------------------------->

# ----------> Face LED List <----------
FaceLedList = ["FaceLed0", "FaceLed1", "FaceLed2", "FaceLed3",
               "FaceLed4", "FaceLed5", "FaceLed6", "FaceLed7"]
ColorList = ['red', 'white', 'green', 'blue', 'yellow', 'magenta', 'cyan'] # fadeRGB()的预设值


def main():
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


	# ----------> 创建Robot ALProxy Module<----------
	global tts, motion, memory, battery, autonomous, posture, leds
	tts = ALProxy("ALTextToSpeech")
	motion = ALProxy("ALMotion")
	posture = ALProxy("ALRobotPosture")
	memory = ALProxy("ALMemory")
	leds = ALProxy("ALLeds")
	battery = ALProxy("ALBattery")
	autonomous = ALProxy("ALAutonomousLife")
	autonomous.setState("disabled") 			# turn ALAutonomousLife off
		
	# ----------> 触摸登录模块 <----------
	global FrontTouch, MiddleTouch, RearTouch
	global LeftFootTouch, RightFootTouch
	FrontTouch = FrontTouch("FrontTouch")
	MiddleTouch = MiddleTouch("MiddleTouch")
	RearTouch = RearTouch("RearTouch")
	LeftFootTouch = LeftFootTouch("LeftFootTouch")
	RightFootTouch = RightFootTouch("RightFootTouch")


	# 未通过验证前，main()睡觉
	while VERIFY_FLAG == False:
		time.sleep(1)

	print "Successfully verified, open socket server..."
	# ----------> 开启socket服务器监听端口 <----------
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((ROBOT_IP, LISTEN_PORT))
	sock.listen(10)

	global connection
	global CONNECT
	try:
		while True:		# 死循环	
			if VERIFY_FLAG == True: 		# 等待客户端连接，单线程监听单一客户端; 
				connection,address = sock.accept()
				tts.say("OK, socket connected")
				print "socket connected, waitting for command"
				CONNECT_FLAG = True
				while (CONNECT_FLAG == True) and (VERIFY_FLAG == True): # 与客户端进行通信
					# 服务器接受指令
					buf = connection.recv(1024)
					print "command:[", buf, "]"
					# 根据接受的命令执行不同操作
					Operation(connection, buf)			
				connection.close()  # 关闭当前socket连接，进入下一轮循环
				tts.say("socket connection is closed.")
				CONNECT_FLAG = False
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
		CONNECT_FLAG = False
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
		global SENSOR_FLAG
		if SENSOR_FLAG == False:
			# 开启新线程，定时发送传感器数据
			SENSOR_FLAG = True
			thread.start_new_thread(sensor, (1,)) # 2nd arg must be a tuple
		else:
			# 第二次发送COMMAND_SENSOR, 则关闭线程
			SENSOR_FLAG = False  # 设置标识位，线程检测后自己退出。
	elif command == COMMAND_ARMREST:						# arm rest
		LArmMoveInit()
		RArmMoveInit()
	elif command == COMMAND_LARMOPEN:						# left hand open
		motion.post.openHand("LHand")
	elif command == COMMAND_LARMCLOSE:						# left hand close
		motion.post.closeHand("LHand")
	elif command == COMMAND_RARMOPEN:						# Right hand open
		motion.post.openHand("RHand")
	elif command == COMMAND_RARMCLOSE:						# Right hand close
		motion.post.closeHand("RHand")
	elif command == COMMAND_LARMUP:							# left arm up
		LArmUp()
	elif command == COMMAND_LARMDOWN:						# left arm down
		LArmMoveInit()
	elif command == COMMAND_RARMUP:							# right arm up
		RArmUp()
	elif command == COMMAND_RARMDOWN:						# right arm down
		RArmMoveInit()
	elif command == COMMAND_SAY:							# say
		messages = connection.recv(1024)
		tts.post.say(messages)
	elif command == COMMAND_POSTURE_STAND:					# posture - stand
		posture.post.goToPosture("Stand", 1.0)
		# goToPosture()切换姿态是智能的，计算出到达目的姿势所需要的移动路径，进行改变。
		# 阻塞调用,这里加post实现后台调用。
	elif command == COMMAND_POSTURE_STANDZERO:				# posture - stand zero
		posture.post.goToPosture("StandZero", 1.0)
	elif command == COMMAND_POSTURE_MOVEINIT:				# posture - move init / stand init
		posture.post.goToPosture("StandInit", 1.0)
	elif command == COMMAND_POSTURE_CROUCH:					# posture - Crouch
		posture.post.goToPosture("Crouch", 1.0)
	elif command == COMMAND_POSTURE_SIT:					# posture - sit
		posture.post.goToPosture("Sit", 1.0)
	elif command == COMMAND_POSTURE_SITRELAX:				# posture - sit relax
		posture.post.goToPosture("SitRelax", 1.0)
	elif command == COMMAND_POSTURE_LYINGBELLY:				# posture - lying belly
		posture.post.goToPosture("LyingBelly", 1.0)
	elif command == COMMAND_POSTURE_LYINGBACK:				# posture - lying back
		posture.post.goToPosture("LyingBack", 1.0)
	else:													# error
		pass

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
	while SENSOR_FLAG == True:
		connection.send("BATTERY" + "#" + str(battery.getBatteryCharge()) + "\r")
		connection.send("SONAR1" + "#" + str(memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")) + "\r")
		connection.send("SONAR2" + "#" + str(memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")) + "\r")
		time.sleep(interval)
	# SENSOR_FLAG == False
	thread.exit_thread()

def LArmInit():	# 配置Left Arm 的所有关节为初始位置0.
	motion.setAngles('LShoulderPitch', 0, 0.2)
	motion.setAngles('LShoulderRoll', 0, 0.2)
	motion.setAngles('LElbowYaw', 0, 0.2)
	motion.setAngles('LElbowRoll', 0, 0.2)
	motion.setAngles('LWristYaw', 0, 0.2)
	motion.setAngles('LHand', 0, 0.2)
def RArmInit(): # 配置Right Arm 的所有关节为初始位置0.
	motion.setAngles('RShoulderPitch', 0, 0.2)
	motion.setAngles('RShoulderRoll', 0, 0.2)
	motion.setAngles('RElbowYaw', 0, 0.2)
	motion.setAngles('RElbowRoll', 0, 0.2)
	motion.setAngles('RWristYaw', 0, 0.2)
	motion.setAngles('RHand', 0, 0.2)
def LArmUp(): # Left Arm 抬起
	motion.setAngles('LShoulderPitch', 0.7, 0.2)
	motion.setAngles('LShoulderRoll', 0.3, 0.2)
	motion.setAngles('LElbowYaw', -1.5, 0.2)
	motion.setAngles('LElbowRoll', -0.5, 0.2)
	motion.setAngles('LWristYaw', -1.7, 0.2)
def RArmUp(): # Right Arm 抬起
	motion.setAngles('RShoulderPitch', 0.7, 0.2)
	motion.setAngles('RShoulderRoll', -0.3, 0.2)
	motion.setAngles('RElbowYaw', 1.5, 0.2)
	motion.setAngles('RElbowRoll', 0.5, 0.2)
	motion.setAngles('RWristYaw', 1.7, 0.2)
def ArmUp2():
	# 简易版本，依赖rest()/wakeUp()后的姿势。
	motion.rest()
	motion.wakeUp()
	motion.setAngles('RShoulderPitch', 0.7, 0.2)
	motion.setAngles('RWristYaw', 1.5, 0.2)
	motion.setAngles('LShoulderPitch', 0.7, 0.2)
	motion.setAngles('LWristYaw', -1.5, 0.2)
def LArmMoveInit(): # 配置Left Arm 为行走初始化的姿态。
	motion.setAngles('LShoulderPitch', 1, 0.2)
	motion.setAngles('LShoulderRoll', 0.3, 0.2)
	motion.setAngles('LElbowYaw', -1.3, 0.2)
	motion.setAngles('LElbowRoll', -0.5, 0.2)
	motion.setAngles('LWristYaw', 0, 0.2)
	motion.setAngles('LHand', 0, 0.2)
def RArmMoveInit(): # 配置Right Arm 为行走初始化的姿态。
	motion.setAngles('RShoulderPitch', 1, 0.2)
	motion.setAngles('RShoulderRoll', -0.3, 0.2)
	motion.setAngles('RElbowYaw', 1.3, 0.2)
	motion.setAngles('RElbowRoll', 0.5, 0.2)
	motion.setAngles('RWristYaw', 0, 0.2)
	motion.setAngles('RHand', 0, 0.2)

class FrontTouch(ALModule):
	def __init__(self, name):
		ALModule.__init__(self, name)
        # Subscribe to FrontTactilTouched event:
		memory.subscribeToEvent("FrontTactilTouched",
			"FrontTouch",
			"onTouched")

	def onTouched(self, strVarName, value):
		# Unsubscribe to the event when talking,
		# to avoid repetitions

		# value == 1.0, 即触摸响应；不考虑value == 0, 即离开触摸响应；
		# VERIFY_FLAG == False, 即未通过验证，此时才需要输入密码。验证后触摸无效；
		if value == 0 or VERIFY_FLAG == True: # 不符合条件，直接返回；这样可以有效防止事件未订阅异常
			return

		memory.unsubscribeToEvent("FrontTactilTouched",
			"FrontTouch")

		#if value == 1.0 and VERIFY_FLAG == False:
		PASSWD.append(HEAD_FRONT)
		tts.post.say("1")

			
        # Subscribe again to the event
		memory.subscribeToEvent("FrontTactilTouched",
			"FrontTouch",
			"onTouched")


class MiddleTouch(ALModule):
	def __init__(self, name):
		ALModule.__init__(self, name)
		memory.subscribeToEvent("MiddleTactilTouched",
			"MiddleTouch",
			"onTouched")

	def onTouched(self, strVarName, value):
		if value == 0 or VERIFY_FLAG == True:
			return
		memory.unsubscribeToEvent("MiddleTactilTouched",
			"MiddleTouch")

		PASSWD.append(HEAD_MIDDLE)
		tts.post.say("2")
			
		memory.subscribeToEvent("MiddleTactilTouched",
			"MiddleTouch",
			"onTouched")

class RearTouch(ALModule):
	def __init__(self, name):
		ALModule.__init__(self, name)
		memory.subscribeToEvent("RearTactilTouched",
			"RearTouch",
			"onTouched")

	def onTouched(self, strVarName, value):
		if value == 0 or VERIFY_FLAG == True:
			return
		memory.unsubscribeToEvent("RearTactilTouched",
			"RearTouch")

		PASSWD.append(HEAD_REAR)
		tts.post.say("3")
			
		memory.subscribeToEvent("RearTactilTouched",
			"RearTouch",
			"onTouched")

class LeftFootTouch(ALModule):
	def __init__(self, name):
		ALModule.__init__(self, name)
		memory.subscribeToEvent("LeftBumperPressed",
			"LeftFootTouch",
			"onTouched")

	def onTouched(self, strVarName, value):
		if value == 0 or VERIFY_FLAG == True:
			return
		memory.unsubscribeToEvent("LeftBumperPressed",
			"LeftFootTouch")
		
		global PASSWD
		tts.post.say("Confirm")
		verify(PASSWD)
		if VERIFY_FLAG == True: 	# 验证成功	
			tts.post.say("OK! Welcome to Sword Art Online!")
			thread.start_new_thread(FaceLed_Color, ('green',))
		else:
			tts.post.say("No! Wrong password.")
			# 开新线程，变化Face LED
			thread.start_new_thread(FaceLed_Color, ('red',)) # 2nd arg must be a tuple
		PASSWD = []	# 无论验证与否，都清空密码；
			
		memory.subscribeToEvent("LeftBumperPressed",
			"LeftFootTouch",
			"onTouched")

class RightFootTouch(ALModule):
	def __init__(self, name):
		ALModule.__init__(self, name)
		memory.subscribeToEvent("RightBumperPressed",
			"RightFootTouch",
			"onTouched")

	def onTouched(self, strVarName, value):
		'''	按右脚触摸，为清空密码；
   			在VERIFY_FLAG = False时，为清空密码；
		'''
		global VERIFY_FLAG
		if value == 0:
			return
		memory.unsubscribeToEvent("RightBumperPressed",
			"RightFootTouch")

		if VERIFY_FLAG == False:
			tts.post.say("Empty password.")
			PASSWD = []
		memory.subscribeToEvent("RightBumperPressed",
			"RightFootTouch",
			"onTouched")

def	verify(passwd):
	'''	将用户输入的passwd与密码库PASSWORD对比
		验证成功则配置标志位VERIFY_FLAG=True;
		验证失败则VERIFY_FLAG=False
	'''
	global VERIFY_FLAG
	if len(PASSWORD) != len(passwd):
		VERIFY_FLAG = False	
	else:
		# 先设为True, 一旦有不相同的，立刻改为False
		VERIFY_FLAG = True
		for i in range(len(passwd)):
			if PASSWORD[i] != passwd[i]:	
				VERIFY_FLAG = False

def FaceLed_Color(color='white',duration=0.1):
	"""
		change the color of the eyes to [color].
        color, 颜色；
		duration, 速度;
	"""
	time.sleep(1)
	# 变色
	for led in FaceLedList:
		leds.post.fadeRGB(led, color, duration)
	# 延时
	time.sleep(3)
	# 变回白色
	for led in FaceLedList:
		leds.post.fadeRGB(led, 'white', duration)
	thread.exit_thread() # 退出线程

if __name__ == "__main__":
	main()
