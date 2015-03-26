#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < server.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/23 >
#	> Last Changed:  	< 2015/03/25 >
#	> Description:		远程控制-服务器端
#						接受客户端发来的指令，执行相应功能。
#################################################################

#! /usr/bin/env python

import argparse
from naoqi import ALProxy
import socket
import sys		# sys.exit() 退出main函数
import almath 	# 角度转弧度(almath.TO_RAD)

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

COMMAND_BATTERY = 'BATTERY'

COMMAND_HEADYAW = 'HEADYAW' 	# 头左右
COMMAND_HEADPITCH = 'HEADPITCH' # 头上下

# flag
CONNECT = False  		# 客户端连接Flag	

def main(robot_IP, robot_PORT=9559):
	# ----------> Connect to robot <----------
	tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
	motion = ALProxy("ALMotion", robot_IP, robot_PORT)
	posture = ALProxy("ALRobotPosture", robot_IP, robot_PORT)
	memory = ALProxy("ALMemory", robot_IP, robot_PORT)
	leds = ALProxy("ALLeds", robot_IP, robot_PORT)
	battery = ALProxy("ALBattery", robot_IP, robot_PORT)
	autonomous = ALProxy("ALAutonomousLife", robot_IP, robot_PORT)
	autonomous.setState("disabled") # turn ALAutonomousLife off

	# ----------> 开启socket服务器监听端口 <----------
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind((robot_IP, LISTEN_PORT))
	sock.listen(10)

	try:
		while True:	# 等待客户端连接，单线程监听单一客户端
			connection,address = sock.accept()
			CONNECT = True
			while CONNECT == True:
				try:
					#connection.settimeout(10)
					# 服务器接受指令
					buf = connection.recv(1024)
					print "get:[", buf, "]"
					# 根据接受的命令执行不同操作
					if buf == COMMAND_WAKEUP:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
						connection.send("Robot Motion: [ Wakeup ]")
					elif buf == COMMAND_REST:
						if motion.robotIsWakeUp() == True: 
							motion.post.rest()
						connection.send("Robot Motion: [ Rest ]")
					elif buf == COMMAND_FORWARD:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
							connection.send("Robot Motion: [ Wakeup ]")
							motion.post.moveInit()
							connection.send("Robot Motion: [ MoveInit ]")
						#motion.post.moveTo(0.3, 0, 0)
						motion.move(0.1,0,0) # 固定速率持续行走
						connection.send("Robot Motion: [ Forward ]")
					elif buf == COMMAND_BACK:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
							connection.send("Robot Motion: [ Wakeup ]")
							motion.post.moveInit()
							connection.send("Robot Motion: [ MoveInit ]")
						#motion.post.moveTo(-0.1, 0, 0)
						motion.move(-0.1,0,0)
						connection.send("Robot Motion: [ Back ]")
					elif buf == COMMAND_LEFT:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
							connection.send("Robot Motion: [ Wakeup ]")
							motion.post.moveInit()
							connection.send("Robot Motion: [ MoveInit ]")
						#motion.post.moveTo(0, 0.1, 0)
						motion.move(0,0.1,0)
						connection.send("Robot Motion: [ Left ]")
					elif buf == COMMAND_RIGHT:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
							connection.send("Robot Motion: [ Wakeup ]")
							motion.post.moveInit()
							connection.send("Robot Motion: [ MoveInit ]")
						#motion.post.moveTo(0, -0.1, 0)
						motion.move(0,-0.1,0)
						connection.send("Robot Motion: [ Right ]")
					elif buf == COMMAND_STOP:
						motion.stopMove()
						connection.send("Robot Motion: [ stop move ]")
					elif buf == COMMAND_TURNRIGHT:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
							connection.send("Robot Motion: [ Wakeup ]")
							motion.post.moveInit()
							connection.send("Robot Motion: [ MoveInit ]")
						motion.move(0, 0, -0.3)
						connection.send("Robot Motion: [ turn right ]")
					elif buf == COMMAND_TURNLEFT:
						if motion.robotIsWakeUp() == False: 
							motion.post.wakeUp()
							connection.send("Robot Motion: [ Wakeup ]")
							motion.post.moveInit()
							connection.send("Robot Motion: [ MoveInit ]")
						motion.move(0, 0, 0.3)
						connection.send("Robot Motion: [ turn left ]")
					elif buf == COMMAND_DISCONNECT:
						CONNECT = False
						connection.send("disconnect from robot server.")
					elif buf == COMMAND_BATTERY:	# 返回机器人电量(单位: %)
						connection.send(str(battery.getBatteryCharge()) + "%")	
					elif buf == COMMAND_HEADYAW:
						# 头部左右转动(Yaw轴)
						buf2 = connection.recv(1024)	# 读取Yaw值	
						print "yaw:", buf2
						angles = (int(buf2) - 50)  
						motion.setStiffnesses("Head", 1.0)
						motion.setAngles("HeadYaw", angles * almath.TO_RAD, 0.2) # 以10%的速度转换angles角度
						connection.send("Robot Motion: [ head raw ]")
					elif buf == COMMAND_HEADPITCH:
						# 头部上下转动(Pitch轴)
						buf2 = connection.recv(1024)	# 读取Pitch值	
						print "pitch:", buf2
						angles = (int(buf2) - 50) * 2
						motion.setStiffnesses("Head", 1.0)
						motion.setAngles("HeadPitch", angles * almath.TO_RAD, 0.2) # 以10%的速度转换angles角度
						connection.send("Robot Motion: [ head pitch ]")
					else:
						connection.send(buf + ": command not found")
				except socket.timeout:
					print 'time out'
			connection.close()	# 关闭当前socket连接，进入下一轮循环
	except KeyboardInterrupt: # CTRL+C, 关闭服务器端程序;
		print ""
		print "Interrupted by user, shutting down"
		sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
	# ----------> 执行main函数 <----------
    main(args.ip, args.port)
