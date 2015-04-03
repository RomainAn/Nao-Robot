#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < vision_getandsaveimage.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/04/01 >
#	> Last Changed: 
#	> Description:
#################################################################
# Get an image from NAO. Display it and save it using PIL.

import sys
import time

# Python Image Library
import Image

from naoqi import ALProxy


def showNaoImage(IP, PORT):
	"""
	First get an image from Nao, then show it on the screen with PIL.
	"""
	
	camProxy = ALProxy("ALVideoDevice", IP, PORT)
#	resolution = 2    # VGA 640x480
	resolution = 0    # kQQVGA, 160x120
#	colorSpace = 11   # RGB
	colorSpace = 10   # YUV
#	colorSpace = 9    # YUV422

	videoClient = camProxy.subscribe("python_client2", resolution, colorSpace, 30)

	time_sum = 0
	number = 100
	for i in range(number):
		t0 = time.time()
		naoImage = camProxy.getImageRemote(videoClient)
		t1 = time.time()
		print "acquisition delay ", t1 - t0
		time_sum = time_sum + t1 - t0

		imageWidth = naoImage[0]
  		imageHeight = naoImage[1]
  		array = naoImage[6]
		#im = Image.fromstring("YUV", (imageWidth, imageHeight), array)
		#im.save("camImage.png", "PNG")
		#im.show()
	print "time cost:", time_sum
	print "average:", time_sum / number

if __name__ == '__main__':
	IP = "192.168.1.100"  # Replace here with your NaoQi's IP address.
	PORT = 9559

  	# Read IP address from first argument if any.
  	if len(sys.argv) > 1:
		IP = sys.argv[1]

	naoImage = showNaoImage(IP, PORT)
