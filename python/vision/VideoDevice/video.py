#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < video.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/04/01 >
#	> Last Changed: 
#	> Description:
#################################################################

import argparse
from naoqi import ALProxy

# First you have to choose a name for your Vision Module
nameId = "tutorial_VM";

# Then specify the resolution among : 
#	kQQVGA (160x120), kQVGA (320x240), kVGA (640x480) or k4VGA (1280x960, only with the HD camera).
# (Definitions are available in alvisiondefinitions.h)
resolution = 0; # 160x120

# Then specify the color space desired among : 
#	kYuvColorSpace, kYUVColorSpace, kYUV422ColorSpace, kRGBColorSpace, etc.
# (Definitions are available in alvisiondefinitions.h)
colorSpace = 13;

# Finally, select the minimal number of frames per second (fps) that your
# vision module requires up to 30fps.
fps = 24;

def main(robot_IP, robot_PORT=9559):
	# ----------> Connect to robot <----------
	tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
#	memory = ALProxy("ALMemory", robot_IP, robot_PORT)
#	autonomous = ALProxy("ALAutonomousLife", robot_IP, robot_PORT)
#	autonomous.setState("disabled") # turn ALAutonomousLife off
	video = ALProxy("ALVideoDevice", robot_IP, robot_PORT)

	# You only have to call the "subscribe" function with those parameters and
	# ALVideoDevice will be in charge of driver initialization and buffer's management.
	subscriberID = video.subscribeCamera(nameId, 0, resolution, colorSpace, fps)
	
	image = video.getImageRemote(subscriberID)
	# image : ALImage
	# image[0] : [int] with of the image
	# image[1] : [int] height of the image
	# image[2] : [int] number of layers of the image
	# image[3] : [int] colorspace of the image	
	# image[4] : [int] time stamp in second 
	# image[5] : [int] time stamp in microsecond (and under second)
	# image[6] : [int] data of the image
	# image[7] : [int] camera ID
	# image[8] : [float] camera FOV left angle (radian)
	# image[9] : [float] camera FOV top angle (radian)
	# image[10]: [float] camera FOV right angle (radian)
	# image[11]: [float] camera FOV bottom angle (radian)
	print "image.getWidth:", image[0]
	print "image.getHeight:", image[1]
	print "image.getNbLayers:", image[2]
	print "list.length:", len(image)

	for i in range(len(image)):
		print image[i]
		print ""
	outputfile = open('data.yuv', 'wb')
	outputfile.write(image[6])
	outputfile.close()

	video.releaseImage(subscriberID)
	video.unsubscribe(subscriberID)

	

	# ----------> <----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
	# ----------> 执行main函数 <----------
    main(args.ip, args.port)
