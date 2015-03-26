#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < hello.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/26 >
#	> Last Changed: 
#	> Description:		一个简单的hello模块，用于Nao Robot自启动测试。
#################################################################

""" Say 'Hello' 

"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

#NAO_IP = "nao.local"
NAO_IP = "192.168.1.100"


# Global variable to store the Hello module instance
Hello = None # HelloModule是定义的一个类，而Hello是一个类实体。

class HelloModule(ALModule):
	""" A simple module just say 'hello' 

	"""
	def __init__(self, name):
		ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
		self.tts = ALProxy("ALTextToSpeech")
		self.tts.say("happy birthday to you,happy birthday to you,happy birthday to you,happy birthday to you!")

def main():
	""" Main entry point

	"""
	parser = OptionParser()
	parser.add_option("--pip",
		help="Parent broker port. The IP address or your robot",
		dest="pip")
	parser.add_option("--pport",
		help="Parent broker port. The port NAOqi is listening to",
		dest="pport",
		type="int")
	parser.set_defaults(
		pip=NAO_IP,
		pport=9559)

	(opts, args_) = parser.parse_args()
	pip   = opts.pip
	pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
	myBroker = ALBroker("myBroker",
		"0.0.0.0",   # listen to anyone
		0,           # find a free port and use it
		pip,         # parent broker IP
		pport)       # parent broker port


    # Warning: Hello must be a global variable
    # The name given to the constructor must be the name of the
    # variable
	global Hello
	Hello = HelloModule("Hello")

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print
		print "Interrupted by user, shutting down"
		myBroker.shutdown()
		sys.exit(0)



if __name__ == "__main__":
	main()
