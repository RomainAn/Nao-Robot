#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < video.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/04/01 >
#	> Last Changed:		< 2015/04/13 > 
#	> Description:
#################################################################

import argparse
from naoqi import ALProxy

import Image			# Python Image Library
import random


# -------------------------------------------------------------------------
# 订阅模块的订阅名称，取消订阅时要用; 
# 因为调试代码常挂掉程序，没有取消订阅，无法再次订阅相同名称，因此这里加入随机化.
nameId = "video_VM_" + str(random.randint(0,100))

# 分辨率:
#	kQQVGA (160x120), kQVGA (320x240), kVGA (640x480) or k4VGA (1280x960, only with the HD camera).
# (Definitions are available in alvisiondefinitions.h)
RESOLUTION_QQVGA_160 = 0		# 1/4 VGA
RESOLUTION_QVGA_320 = 1			# 1/2 VGA
RESOLUTION_VGA_640 = 2			# VGA, 640x480
resolution = RESOLUTION_QQVGA_160

# 文件格式(ColorSpace):
#	kYuvColorSpace, kYUVColorSpace, kYUV422ColorSpace (9), kRGBColorSpace(11), etc.
# (Definitions are available in alvisiondefinitions.h)
ColorSpace_YUV422 = 9	# 0xVVUUYY
ColorSpace_YUV = 10		# 0xY'Y'VVYY
ColorSpace_RGB = 11		# 0xBBGGRR
ColorSpace_BGR = 13		# 0xRRGGBB
colorSpace = ColorSpace_YUV422;

# 帧率(最高 30 fps):
fps = 24;
# -------------------------------------------------------------------------

def main(robot_IP, robot_PORT=9559):
	# ----------> Connect to robot <----------
	tts = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
	video = ALProxy("ALVideoDevice", robot_IP, robot_PORT)

	# You only have to call the "subscribe" function with those parameters and
	# ALVideoDevice will be in charge of driver initialization and buffer's management.
	subscriberID = video.subscribeCamera(nameId, 0, resolution, colorSpace, fps)

	getImage(video, subscriberID)
	
	# Release image buffer locked by getImageLocal(). 
	# If module had no locked image buffer, does nothing.
	video.releaseImage(subscriberID)
	video.unsubscribe(subscriberID)

def getImage(videoProxy, subscriberID):
	''' 
		获得一张图像
		参数: 	videoProxy, ALVideoDevice 代理;
				subscriberID, 订阅者;
	'''
	image = videoProxy.getImageRemote(subscriberID)
	# image : ALImage
	# image[0] : [int] with of the image
	# image[1] : [int] height of the image
	# image[2] : [int] number of layers of the image
	# image[3] : [int] colorspace of the image	
	# image[4] : [int] time stamp in second 
	# image[5] : [int] time stamp in microsecond (and under second)
	# image[6] : [int] data of the image		<<<<<<<<<<<<<<<<<<<<<<<<<<< YUV422
	# image[7] : [int] camera ID
	# image[8] : [float] camera FOV left angle (radian)
	# image[9] : [float] camera FOV top angle (radian)
	# image[10]: [float] camera FOV right angle (radian)
	# image[11]: [float] camera FOV bottom angle (radian)

	# image Info
	print "image.getWidth:", image[0]
	print "image.getHeight:", image[1]
	print "image.getNbLayers:", image[2]
	print "list.length:", len(image)

	filename = 'data.yuv422' 
	print 'save image to', filename
	outputfile = open(filename, 'wb')
	outputfile.write(image[6])
	outputfile.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.2.100", help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    args = parser.parse_args()
	# ----------> 执行main函数 <----------
    main(args.ip, args.port)
