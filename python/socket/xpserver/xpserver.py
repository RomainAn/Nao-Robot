#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < xpserver.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/26 >
#	> Last Changed:		< 2015/03/31 >
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
import os		# os.walk
import urllib	# urllib.urlretrieve

LISTEN_PORT = 8001 # 服务器监听端口
# <-------------------------------------------------------------> Command 定义
# 基本操作
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
# 头部动作
COMMAND_HEADYAW = 'HEADYAW'     # 头左右
COMMAND_HEADPITCH = 'HEADPITCH' # 头上下
# 传感器
COMMAND_SENSOR = 'SENSOR'
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
# 避障
COMMAND_OBSTACLE = 'OBSTACLE'							# 超声波避障
# 音乐播放器
COMMAND_MUSIC_ON 	= 'MUSIC_ON'						# 打开音乐播放器
COMMAND_MUSIC_OFF 	= 'MUSIC_OFF'						# 关闭音乐播放器
COMMAND_MUSIC_NEXT 	= 'MUSIC_NEXT'						# 下一首歌曲
COMMAND_MUSIC_PREVIOUS = 'MUSIC_PREVIOUS'				# 上一首歌曲
COMMAND_MUSIC_PLAY	=	'MUSIC_PLAY'					# 开始
COMMAND_MUSIC_PAUSE =	'MUSIC_PAUSE'					# 暂停
COMMAND_MUSIC_UP	=	'MUSIC_UP'						# Volume Up
COMMAND_MUSIC_DOWN	=	'MUSIC_DOWN'					# Volume Down
COMMAND_MUSIC_FORWARD = 'MUSIC_FORWARD'					# 快进
COMMAND_MUSIC_REWIND=	'MUSIC_REWIND'					# 快退
COMMAND_MUSIC_URL	=	'MUSIC_URL'						# 下载音乐并播放
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
sonar = None
aup = None

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
TripleClick = None			# 退出登录，设置为胸前按钮三连击，是为了防止误操作;
# <------------------------------------------------------------->

# ----------> Face LED List <----------
FaceLedList = ["FaceLed0", "FaceLed1", "FaceLed2", "FaceLed3",
               "FaceLed4", "FaceLed5", "FaceLed6", "FaceLed7"]
ColorList = ['red', 'white', 'green', 'blue', 'yellow', 'magenta', 'cyan'] # fadeRGB()的预设值


# <------------------------------------------------------------->
# 障碍物标志
OBSTACLE_L = False 	# True则左侧有障碍
OBSTACLE_R = False  # True则右侧有障碍
OBSTACLE_ON = False	# 避障标志位，为False时退出避障循环

OBSTACLE_DISTANCE = 0.5	# 设置检测的安全距离
OBSTACLE_DELAY = 0.3	# 设置延时事件, 单位：秒
MOVE_SPEED = 0.4		# 移动速度, 单位: m/s
TURN_ANGLE = 20			# 旋转角度，单位: 度
# <------------------------------------------------------------->
# 音乐播放器
MUSIC_FLAG = False					# 音乐播放器Flag, 为True表示正在运行相应播放器功能
MusicPath = '/home/nao/music/'		# 歌曲文件夹
MusicList = []      # 歌曲列表；程序启动后会扫描一遍音乐文件夹；为绝对路径地址
MusicPoint = 0      # 指向当前播放音乐的索引, 范围 range(len(MusicList))
PlayFlag = False    # 播放标志位, 播放音乐时标识为True
PlayFileID = None   # 正在播放文件的fileID
MyVolume = 0.50     # 音量, [0.0 ~ 1.0]

# 与密码系统重合，注意在事件回调函数中利用标志位区分
#FrontTouch = None           # 下一首
#MiddleTouch = None          # 开始/暂停
#RearTouch = None            # 上一首
#LeftFootTouch = None        # Volume +
#RightFootTouch = None       # Volume -

# <------------------------------------------------------------->
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
	global sonar, aup
	tts = ALProxy("ALTextToSpeech")
	motion = ALProxy("ALMotion")
	posture = ALProxy("ALRobotPosture")
	memory = ALProxy("ALMemory")
	leds = ALProxy("ALLeds")
	battery = ALProxy("ALBattery")
	sonar = ALProxy("ALSonar")
	aup = ALProxy("ALAudioPlayer")
	autonomous = ALProxy("ALAutonomousLife")
	autonomous.setState("disabled") 			# turn ALAutonomousLife off
		
	# ----------> 触摸登录模块 <----------
	global FrontTouch, MiddleTouch, RearTouch
	global LeftFootTouch, RightFootTouch, TripleClick
	FrontTouch = FrontTouch("FrontTouch")
	MiddleTouch = MiddleTouch("MiddleTouch")
	RearTouch = RearTouch("RearTouch")
	LeftFootTouch = LeftFootTouch("LeftFootTouch")
	RightFootTouch = RightFootTouch("RightFootTouch")
	TripleClick = TripleClick("TripleClick")

	# ----------> 音乐播放器模块 <----------
	# 启动后需要提前加载第一个音乐文件
	global PlayFileID
	scan_mp3()          # 先扫描文件夹
	filename = MusicList[MusicPoint]
	PlayFileID = aup.loadFile(filename)

	# 未通过验证前，main()睡觉
	while VERIFY_FLAG == False:
		time.sleep(1)

	print "Successfully verified, open socket server..."
	# ----------> 开启socket服务器监听端口 <----------
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((ROBOT_IP, LISTEN_PORT))
	sock.listen(10)

	global connection
	global CONNECT_FLAG
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
		aup.stopAll()	# 关闭所有音乐
		myBroker.shutdown()
		sys.exit(0)

def Operation(connection, command):	# 根据指令执行相应操作
	global MUSIC_FLAG
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
		global CONNECT_FLAG
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
			thread.start_new_thread(sensor, (0.5,)) # 2nd arg must be a tuple
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
	elif command == COMMAND_OBSTACLE:						# avoid obstacle
		global OBSTACLE_ON
		if OBSTACLE_ON == False:
			OBSTACLE_ON = True
			thread.start_new_thread(obstacle, ())
		else:
			OBSTACLE_ON = False
	elif command == COMMAND_MUSIC_ON:						# 音乐播放器打开
		if MUSIC_FLAG == True:
			pass
		else:
			tts.post.say("Music!")
			MUSIC_FLAG = True		# 标志位设为True, 触摸功能开启
			thread.start_new_thread(timer_check, ())
	elif command == COMMAND_MUSIC_OFF:						# 音乐播放器关闭
		MUSIC_FLAG = False		# 标志位设为False, 触摸功能失效
		aup.stopAll()
		tts.post.say("Stop Music!")
	elif command == COMMAND_MUSIC_PLAY:						# music play
		memory.raiseEvent('MiddleTactilTouched', 1.0)
	elif command == COMMAND_MUSIC_PAUSE:					# music play
		memory.raiseEvent('MiddleTactilTouched', 1.0)
	elif command == COMMAND_MUSIC_NEXT:						# music next song
		memory.raiseEvent('FrontTactilTouched', 1.0)
	elif command == COMMAND_MUSIC_PREVIOUS:					# music previous song
		memory.raiseEvent('RearTactilTouched', 1.0)
	elif command == COMMAND_MUSIC_UP:						# music volume up
		global MyVolume
		volume = connection.recv(1024)
		volume = int(volume) / 100.0
		if volume >= 0 and volume <= 1.00:
			MyVolume = volume
			aup.setVolume(PlayFileID, MyVolume)
			print "Volume:", volume * 100, "%"
	elif command == COMMAND_MUSIC_URL:						# download mp3 file
		buf = connection.recv(1024)
		# 需要分隔歌名和URL
		index = buf.find('http')
		filename = buf[:index]
		url = buf[index:]
		print "Music Name:", filename
		print "Download URL:", url
		tts.post.say("Download music")
		thread.start_new_thread(download_mp3, (filename,url))	# 开一新线程下载音乐
	else:														# error
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
	sonar.subscribe("xpserver")
	while SENSOR_FLAG == True:
		connection.send("BATTERY" + "#" + str(battery.getBatteryCharge()) + "\r")
		connection.send("SONAR1" + "#" + str(memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")) + "\r")
		connection.send("SONAR2" + "#" + str(memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")) + "\r")
		time.sleep(interval)
	# SENSOR_FLAG == False
	sonar.unsubscribe("xpserver")
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
		if value == 0: # 不符合离开触摸区域的触发时间，直接返回；
			return

		if VERIFY_FLAG == True and MUSIC_FLAG == False:
			# 通过验证，而未打开音乐播放器，此时触摸无反应
			return
		memory.unsubscribeToEvent("FrontTactilTouched",
			"FrontTouch")

		if VERIFY_FLAG == False:		# 登录系统
			PASSWD.append(HEAD_FRONT)
			tts.post.say("1")
		elif MUSIC_FLAG == True:		# 播放器系统
			global MusicPoint, PlayFileID
			MusicPoint = (MusicPoint + 1) % len(MusicList)
			filename = MusicList[MusicPoint]
			print "Next Song:", MusicList[MusicPoint]
			if PlayFlag == True:        # 播放音乐时切歌
				# 停止播放
				aup.pause(PlayFileID)
				# 切歌播放
				PlayFileID = aup.post.playFileInLoop(filename, MyVolume, 0)
			else:                       # 暂停音乐时切歌
				# 载入下一首歌曲
				PlayFileID = aup.loadFile(filename)	
			
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
		if value == 0:
			return
		if VERIFY_FLAG == True and MUSIC_FLAG == False:
			return
		memory.unsubscribeToEvent("MiddleTactilTouched",
			"MiddleTouch")

		if VERIFY_FLAG == False:	
			PASSWD.append(HEAD_MIDDLE)
			tts.post.say("2")
		elif MUSIC_FLAG == True:
			global PlayFlag, PlayFileID
			if PlayFlag == False:           # 没有播放音乐，则开始播放音乐
				PlayFlag = True
				aup.post.playInLoop(PlayFileID, MyVolume, 0)
				print "Music Play"
			else:                           # 正在播放音乐，则暂停播放
				PlayFlag = False
				aup.pause(PlayFileID)
				print "Pause"	
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
		if value == 0:
			return
		if VERIFY_FLAG == True and MUSIC_FLAG == False:
			return
		memory.unsubscribeToEvent("RearTactilTouched",
			"RearTouch")
		if VERIFY_FLAG == False:
			PASSWD.append(HEAD_REAR)
			tts.post.say("3")
		elif MUSIC_FLAG == True:
			global MusicPoint, PlayFileID
			MusicPoint = (MusicPoint + len(MusicList) - 1) % len(MusicList)
			filename = MusicList[MusicPoint]
			print "Previous Song:", MusicList[MusicPoint]
			if PlayFlag == True:        # 播放音乐时切歌
				# 停止播放
				aup.pause(PlayFileID)
				# 切歌播放
				PlayFileID = aup.post.playFileInLoop(filename, MyVolume, 0)
			else:                       # 暂停音乐时切歌
				# 载入下一首歌曲
				PlayFileID = aup.loadFile(filename)
				
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

class TripleClick(ALModule):
	''' 胸前按钮三连接 - 退出登录。
		注意：由于机器人自带的绑定事件，双击按钮会触发机器人的autonomous life，这里需要再关闭。
		autonomous life会对编程控制产生干扰。
	'''
	def __init__(self, name):
		ALModule.__init__(self, name)
		memory.subscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick",
			"onClicked")

	def onClicked(self, eventName):
		'''
			在通过验证后(VERIFY_FLAG=True)，通过胸前三连击退出登录。
		'''
		autonomous.setState("disabled")
		global VERIFY_FLAG
		if VERIFY_FLAG == False:
			return
		memory.unsubscribeToEvent("MiddleTactilTouched",
			"MiddleTouch")

		global PASSWD
		PASSWD = []
		VERIFY_FLAG = False
		tts.post.say("Logout!")
		thread.start_new_thread(FaceLed_Color, ('yellow',))
			
		memory.subscribeToEvent("MiddleTactilTouched",
			"MiddleTouch",
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

# --------------------------------------------------------------------- 超声波避障
def obstacle():
	''' 
		固定间隔循环检测是否存在障碍，根据障碍物标志决定机器人的行走方向
	'''
	global OBSTACLE_L, OBSTACLE_R, OBSTACLE_ON

	motion.wakeUp()
	motion.moveInit()
	sonar.subscribe("my_obstacle")
	while OBSTACLE_ON == True:			# 避障标识为True，则持续循环检测
		# 1. 检测障碍物
		check()
		# 2. 根据障碍物标志决定行走方向
		avoid(OBSTACLE_L, OBSTACLE_R)	
		# 3. 延时
		time.sleep(OBSTACLE_DELAY)
	sonar.unsubscribe("my_obstacle")
	motion.stopMove()
	motion.rest()
	thread.exit_thread()
	
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
def avoid(flag_L, flag_R):
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
# ---------------------------------------------------------------------  音乐播放器
def scan_mp3():
	'''
	    从指定的文件夹中扫描出MP3格式的文件
	'''
	global MusicList
	MusicList = []
	for root, dirs, files in os.walk(MusicPath):
		# root   #当前遍历到的目录的根
		# dirs   #当前遍历到的目录的根下的所有目录
		# files  #当前遍历到的目录的根下的所有文件
		for filename in files:
			if filename.find('.mp3') != -1:         # 找不到后缀才返回-1
				filepath = os.path.join(root, filename)
				MusicList.append(filepath)          # 将找到的mp3文件的地址加入MusicList

def timer_check():
	'''
		检查当前音乐的播放进度，结束后切换下一首歌曲;
	'''
	while MUSIC_FLAG == True:
		if PlayFlag == True:
			postion = aup.getCurrentPosition(PlayFileID)
			length = aup.getFileLength(PlayFileID)
			if postion >= length - 2: # 正在播放，且进度即将结束
				memory.raiseEvent('FrontTactilTouched', 1.0) # 触发下一首对应的事件
		else:
			pass
		time.sleep(1)
	thread.exit_thread()	
def download_mp3(filename, url):
	'''
		开启一个新线程，用来下载MP3音乐；下载好音乐后自动切歌
	'''
	global MusicList, MusicPoint, PlayFileID
	try:
		print '>>> Start to download music [%s]' % filename
		urllib.urlretrieve(url, MusicPath+filename+'.mp3')
		print '>>> Download Completed'
		tts.post.say("Download complete!")
		# 将下载好的音乐添加在播放列表中
		MusicList.append(MusicPath+filename+'.mp3')

		# 切换歌曲
		if PlayFlag == False:	# 没有播放音乐, 则载入播放
			MusicPoint = len(MusicList) - 1
			filename = MusicList[MusicPoint]
			PlayFileID = aup.loadFile(filename)
			memory.raiseEvent('MiddleTactilTouched', 1.0)
		else:					# 正在播放音乐, 则调整MusicPoint, 实现下一首就是目标歌曲
			MusicPoint = len(MusicList) - 2
			memory.raiseEvent('FrontTactilTouched', 1.0)
		# 关闭线程
		thread.exit_thread()
	except Exception,e:
		print 'Exception:',e
		print "download_mp3()"

if __name__ == "__main__":
	main()
