#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < template.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/16 >
#	> Last Changed: 
#	> Description:		
#################################################################

#! /usr/bin/env python
#-*- coding: utf-8 -*-

from naoqi import ALProxy

# ----------> Connect to robot <----------
robot_ip = "192.168.1.100"
robot_port = 9559			# default port : 9559

tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
motionProxy = ALProxy("ALMotion", robot_ip, robot_port)
postureProxy = ALProxy("ALRobotPosture", robot_ip, robot_port)
memoryProxy = ALProxy("ALMemory", robot_ip, robot_port)
ledsProxy = ALProxy("ALLeds", robot_ip, robot_port)

# ----------> <----------
