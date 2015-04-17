#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < send_YUV422.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/04/13 >
#	> Last Changed: 
#	> Description:		send YUV422 image file to socket client.
#################################################################

import sys
import time

import Image		# Python Image Library
import socket
import random
import struct

from naoqi import ALProxy

LISTEN_PORT = 8003 		# 服务器监听端�?
CONNECT = False         # 客户端连接Flag
connection = None
Data = None
Adress =None

def main(IP, PORT):
	camProxy = ALProxy("ALVideoDevice", IP, PORT)
#	resolution = 2    # VGA 640x480
	resolution = 0    # kQQVGA, 160x120
#	colorSpace = 11   # RGB
#	colorSpace = 10   # YUV
	colorSpace = 9    # YUV422

	# 程序测试经常挂掉，导致subscriberID未被取消订阅，需要更换订阅号；这里加入随�?
	subscriberID = 'send_YUV422_' + str(random.randint(0,100))

	videoClient = camProxy.subscribe(subscriberID, resolution, colorSpace, 30)

	# ----------> 开启socket服务器监听端�?<----------
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((IP, LISTEN_PORT))
#	sock.listen(10)

	naoImage = camProxy.getImageRemote(videoClient)
	array = naoImage[6]
#	print 'VIDEO#' + array + '\r'
	print 'image data length:', len(array) 
	print 'print test over.'
	print '---------------------------------------------'

	global address
	global Data
	try:
		while True:
			print 'Waiting for a connection'
			#connection,address = sock.accept()
			Data,address=sock.recvfrom(1024)
			print 'socket client connected.'
			print 'data:',Data
			print 'address', address
			CONNECT = True
			while CONNECT == True:
				naoImage = camProxy.getImageRemote(videoClient)
				array = naoImage[6]	
#				connection.send('VIDEO#' + array + '#OVER\r')
#				connection.send(array)
#				sock.sendto(array,address)
				sock.sendto('hello',address)
				sock.sendto('hello',address)
				sock.sendto('hello',address)
				sock.sendto('hello',address)
				sock.sendto('hello',address)
				print 'send image date successful.'
				#time.sleep(2)
				CONNECT = False
			print 'socket client disconnect.'
	except KeyboardInterrupt: # CTRL+C, 关闭服务器端程序;
		print ""
		print "Interrupted by user, shutting down"
		camProxy.unsubscribe(videoClient)
		sock.close()
		print 'unsubscribe nao video device'
		if connection != None:
			connection.close()	
			print 'socket connection closed.'
		sys.exit(0)


#		imageWidth = naoImage[0]
#  		imageHeight = naoImage[1]
#  		array = naoImage[6]

		#im = Image.fromstring("YUV", (imageWidth, imageHeight), array)
		#im.save("camImage.png", "PNG")
		#im.show()

if __name__ == '__main__':
	IP = "192.168.2.100"  # Replace here with your NaoQi's IP address.
	PORT = 9559

  	# Read IP address from first argument if any.
  	if len(sys.argv) > 1:
		IP = sys.argv[1]

	main(IP, PORT)
