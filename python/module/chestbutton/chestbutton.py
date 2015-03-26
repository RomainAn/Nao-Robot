#-*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:        < chestbutton.py >
#	> Author:           < Sean Guo >		
#	> Mail:             < iseanxp+code@gmail.com >		
#	> Created Time:     < 2015/03/26 >
#	> Last Changed: 
#	> Description:		编写一个python模块，响应机器人ChestButton事件，
#						并配置nao内部~/naoqi/preferences/autoload.ini实现开机自启;
#################################################################

#! /usr/bin/env python

""" Say 'Hello' each time pressed (TripleClick) Nao ChestButton

"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

#NAO_IP = "nao.local"
NAO_IP = "192.168.1.100"


# Global variable to store the TripleClick module instance
TripleClick = None # TripleClickModule是定义的一个类，而TripleClick是一个类实体。
memory = None

class TripleClickModule(ALModule):
	""" A simple module able to react
	to Event: "ALChestButton/TripleClickOccurred"

	"""
	def __init__(self, name):
		ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
		self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to the TripleClickOccurred event:
		global memory
		memory = ALProxy("ALMemory")
		memory.subscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick",
			"onTripleClickOccurred")

	def onTripleClickOccurred(self, *_args): # 对应事件的callback函数
		""" This will be called each time TripleClickOccurred.

		"""
        # Unsubscribe to the event when talking,
        # to avoid repetitions, 暂时取消订阅，预防冲突;
		memory.unsubscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick")

		self.tts.say("Oh!You're Breaking My Heart~")

        # Subscribe again to the event
		memory.subscribeToEvent("ALChestButton/TripleClickOccurred",
			"TripleClick",
			"onTripleClickOccurred")

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


    # Warning: TripleClick must be a global variable
    # The name given to the constructor must be the name of the
    # variable
	global TripleClick
	TripleClick = TripleClickModule("TripleClick")

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
