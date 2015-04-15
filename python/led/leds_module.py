#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < leds_module.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/04/15 >
#	> Last Changed: 
#	> Description:		基于Nao机器人LED的Python类模块
#################################################################
import argparse
from naoqi import ALProxy
import time
import threading        # 多线程类
import random

class LED(threading.Thread):
	'''
		创建线程类 - LED, 实现Nao机器人led灯变化
	'''
	def __init__(self, robot_ip, robot_port=9559):
		# 线程类初始化
		threading.Thread.__init__(self)
		self.setDaemon(True)
		# 类成员变量
		# ----------> Eye led blink <----------
		# Group Name: FaceLeds, RightFaceLeds, LeftFaceLeds; 
		# Group Name: FaceLedsBottom (3,4),FaceLedsTop (7,0),FaceLedsExternal (6,5),FaceLedsInternal (1,2) 
		# Group Name: FaceLed0 ~ FaceLed7
		# Short Name:  
		self.face_led_list = [	"FaceLed0", "FaceLed1", "FaceLed2", "FaceLed3", 
								"FaceLed4", "FaceLed5", "FaceLed6", "FaceLed7"]

		# ----------> ear led blink <----------
		# Group Name: EarLeds, RightEarLeds, LeftEarLeds...
		# Short Name: RightEarLed1 ~ RightEarLed10, LeftEarLed1 ~ LeftEarLed10.
		self.right_ear_led_list = [	"RightEarLed1", "RightEarLed2", "RightEarLed3", "RightEarLed4",
									"RightEarLed5", "RightEarLed6", "RightEarLed7", "RightEarLed8",
									"RightEarLed9", "RightEarLed10"]
		self.left_ear_led_list = [	"LeftEarLed1", "LeftEarLed2", "LeftEarLed3", "LeftEarLed4", 
				  					"LeftEarLed5", "LeftEarLed6", "LeftEarLed7", "LeftEarLed8",
				  					"LeftEarLed9", "LeftEarLed10"]
		# Flush最占用时间，需要在线程内执行，这里在线程类的run()中，根据标志位来开关；
		self.faceFlushFlag = False
		self.earFlushFlag = False
		# fadeRGB()的颜色预设值
		self.color_list = ['red', 'white', 'green', 'blue', 'yellow', 'magenta', 'cyan'] 
		
		# naoqi.ALProxy
		try:
			self.leds = ALProxy("ALLeds", robot_ip, robot_port)
		except Exception, e:
			print "Could not create proxy by ALProxy in Class MP3player"
			print "Error: ", e
	def setFaceFlush(self, bools):
		self.faceFlushFlag = bools
	def setEarFlush(self, bools):
		self.earFlushFlag = bools
	def run(self):
		'''
			根据标志位faceFlushFlag, earFlushFlag来执行响应功能;
		'''
		while True:	# 在新线程内不断循环检测;
			if self.earFlushFlag == True:
				self.earFlush(5)
			else:
				time.sleep(1)	
	def stop(self):
		self.setFaceFlush(False)
		self.setEarFlush(False)
		self.earON()
	# -----------------------------------> face led control
	def faceON(self):
		'''
			打开Face LED
		'''
		self.leds.on("FaceLeds");
	def faceOFF(self):
		'''
			关闭Face LED
		'''
		self.leds.off("FaceLeds");
	def faceFlush(self, number=1, duration=0.05):
		"""
			在duration时间间隔下, 按顺序依次打开/关闭LED，实现流水灯闪烁效果。
			duration, 闪烁速度
			number, 闪烁次数
		"""
		# set all eye leds off immediately.
		self.leds.fade("FaceLeds", 0, 0) 
		for num in range(number):
			# open face leds
			for index in range(len(self.face_led_list)):
				self.leds.fade(self.face_led_list[index], 1, duration)
			# close face leds
			for index in range(len(self.face_led_list)):
				self.leds.fade(self.face_led_list[index], 0, duration)
	def faceBlink(self, number=1, duration=0.2):
		'''
			机器人眨眼睛
			duration, 眨眼速度
			number, 眨眼次数
		'''
		LedValueList = [0, 0, 1, 0,
						0, 0, 1, 0]
		# blink face leds
		for num in range(number):
			# 关闭一些LED，实现眨眼效果;
			for i in range(len(self.face_led_list)):
				self.leds.post.fade(self.face_led_list[i], LedValueList[i], duration)
			# 延时，视觉停留效应
			time.sleep(0.1) 	
			# 重新打开所有LED
			self.leds.fade("FaceLeds", 1, duration) 
	def faceRandomColor(self, number=1):
		"""
			The color of the eyes changes randomly.
			number, 次数；
		"""
		for i in range(number):
			rRandTime = random.uniform(0.0, 2.0) #随机速度
			self.leds.fadeRGB("FaceLeds", 
				256 * random.randint(0,255) + 256*256 * random.randint(0,255) + random.randint(0,255),
				rRandTime)
			time.sleep(random.uniform(0.0,1.0))

	def faceColor(self, color='white', duration=0.1):
		"""
			change the color of the eyes to [color].
			color, 颜色；
			duration, 速度;
		"""
		for led in self.face_led_list:
			self.leds.post.fadeRGB(led, color, duration)
	# -----------------------------------> ear led control
	def earON(self):
		self.leds.on("EarLeds");
	def earOFF(self):
		self.leds.off("EarLeds");
	def earFlush(self, number=10, duration=0.05):
		"""
			在duration时间间隔下, 按顺序依次打开/关闭LED，实现流水灯闪烁效果。
			number, 闪烁次数
			duration, 间隔事件，用来控制闪烁速度
		"""
		# set all ear leds off immediately.
		self.leds.fade("EarLeds", 0, 0) 
		for num in range(number):
			for i in range(len(self.right_ear_led_list)):
				self.leds.fade(self.right_ear_led_list[i], 1, duration)
				self.leds.fade(self.right_ear_led_list[i], 1, duration)
			for i in range(len(self.right_ear_led_list)):
				self.leds.fade(self.left_ear_led_list[i], 0, duration)
				self.leds.fade(self.right_ear_led_list[i], 0, duration)

def main(robot_IP, robot_PORT=9559):
	# ----------> Connect to robot <----------
	led = LED(robot_IP, robot_PORT)
	# ----------> Led control <----------
	led.setEarFlush(True)
	led.start()
	led.faceON()
	time.sleep(1)
	led.faceOFF()
	time.sleep(1)
	led.faceON()
	time.sleep(1)
	led.faceBlink(5)
	time.sleep(1)
	led.faceColor('red')
	time.sleep(1)
	led.faceBlink(5)
	time.sleep(1)
	led.faceColor('blue')
	time.sleep(1)
#	led.earFlush(5)
#	time.sleep(1)
	led.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.2.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
	# ----------> 执行main函数 <----------
    main(args.ip, args.port)
