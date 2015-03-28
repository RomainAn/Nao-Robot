#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < leds.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/28 >
#	> Last Changed: 
#	> Description:		Nao robot led control
#################################################################

import argparse
from naoqi import ALProxy
import time
import random

leds = None

# ----------> Face Led List <----------
FaceLedList = ["FaceLed0", "FaceLed1", "FaceLed2", "FaceLed3", 
			   "FaceLed4", "FaceLed5", "FaceLed6", "FaceLed7"]

# ----------> Ear Led List <----------
RightEarLedList = ["RightEarLed1", "RightEarLed2", "RightEarLed3", "RightEarLed4", 
				   "RightEarLed5", "RightEarLed6", "RightEarLed7", "RightEarLed8",
				   "RightEarLed9", "RightEarLed10"]
LeftEarLedList = ["LeftEarLed1", "LeftEarLed2", "LeftEarLed3", "LeftEarLed4", 
				  "LeftEarLed5", "LeftEarLed6", "LeftEarLed7", "LeftEarLed8",
				  "LeftEarLed9", "LeftEarLed10"]

ColorList = ['red', 'white', 'green', 'blue', 'yellow', 'magenta', 'cyan'] # fadeRGB()的预设值

def main(robot_IP, robot_PORT=9559):
	# ----------> Connect to robot <----------
	global leds
	leds = ALProxy("ALLeds", robot_IP, robot_PORT)
	# ----------> Led control <----------
#	FaceLed_Flush()
#	FaceLed_Blink()
#	FaceLed_RandomColor()
#	FaceLed_Color('green')
#	FaceLed_Color_Test()
#	EarLed_Flush()
	FaceLed_OFF()
	time.sleep(1)
	FaceLed_ON()

# ----------> Eye led blink <----------
# Group Name: FaceLeds, RightFaceLeds, LeftFaceLeds; 
# Group Name: FaceLedsBottom (3,4),FaceLedsTop (7,0),FaceLedsExternal (6,5),FaceLedsInternal (1,2) 
# Group Name: FaceLed0 ~ FaceLed7
# Short Name:  

def FaceLed_ON():
	'''
		打开Face LED
	'''
	leds.on("FaceLeds");

def FaceLed_OFF():
	'''
		关闭Face LED
	'''
	leds.off("FaceLeds");

def FaceLed_Flush(duration=0.05, number=10):
	"""
		先关闭所有Face Led, 然后在duration时间间隔下打开/关闭LED，实现闪烁效果。
		duration, 闪烁速度
		number, 闪烁次数
	"""
	leds.fade("FaceLeds", 0, 0) # set all eye leds off immediately.
	# fluse led...
	for i in range(number):
		for i in range(len(FaceLedList)):
			leds.fade(FaceLedList[i], 1, duration)
		for i in range(len(FaceLedList)):
			leds.fade(FaceLedList[i], 0, duration)

def FaceLed_Blink(duration=0.2, number=10):
	'''
		机器人眨眼睛
		duration, 眨眼速度
		number, 眨眼次数
	'''
	LedValueList = [0, 0, 1, 0,
					0, 0, 1, 0]
	# blink face leds
	for i in range(number):
		for i in range(len(FaceLedList)):
			leds.post.fade(FaceLedList[i], LedValueList[i], duration)
		time.sleep(0.1) 	# 延时，视觉停留效应
		leds.fade("FaceLeds", 1, duration) # set all eye leds off immediately.
		
def FaceLed_RandomColor(number=5):
	"""
		The color of the eyes changes randomly.
		number, 次数；
	"""
	for i in range(number):
		rRandTime = random.uniform(0.0, 2.0) #随机速度
		leds.fadeRGB("FaceLeds", 
			256 * random.randint(0,255) + 256*256 * random.randint(0,255) + random.randint(0,255),
			rRandTime)
		time.sleep(random.uniform(0.0,3.0))

def FaceLed_Color(color='white',duration=0.1):
	"""
		change the color of the eyes to [color].
		color, 颜色；
		duration, 速度;
	"""
	for led in FaceLedList:
		leds.post.fadeRGB(led, color, duration)

def FaceLed_Color_Test():
	'''
		FaceLed_Color() test
	'''
	for color in ColorList:
		FaceLed_Color(color)
		time.sleep(1) 			# 由于FaceLed_Color()是使用post实现非阻塞的，这里需要延时等待，否则冲突。

# ----------> ear led blink <----------
# Group Name: EarLeds, RightEarLeds, LeftEarLeds...
# Short Name: RightEarLed1 ~ RightEarLed10, LeftEarLed1 ~ LeftEarLed10.

def EarLed_Flush(duration=0.05, number=10):
	"""
		先关闭所有Ear Led, 然后在duration时间间隔下打开/关闭LED，实现闪烁效果。
		duration, 闪烁速度
		number, 闪烁次数
	"""
	leds.fade("EarLeds", 0, 0) # set all ear leds off immediately.
	# fluse led...
	for i in range(number):
		for i in range(len(RightEarLedList)):
			leds.fade(LeftEarLedList[i], 1, duration)
			leds.fade(RightEarLedList[i], 1, duration)
		for i in range(len(RightEarLedList)):
			leds.fade(LeftEarLedList[i], 0, duration)
			leds.fade(RightEarLedList[i], 0, duration)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
	# ----------> 执行main函数 <----------
    main(args.ip, args.port)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
	# ----------> 执行main函数 <----------
    main(args.ip, args.port)
