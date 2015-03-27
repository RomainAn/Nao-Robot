#-*- coding: utf-8 -*-
from naoqi import ALProxy
import time		# blink()
import random 	# random_eyes()

# ----------> Connect to robot <----------
robot_ip = "192.168.1.100"
robot_port = 9559			# default port : 9559

ledsProxy = ALProxy("ALLeds", robot_ip, robot_port)


# ----------> ear led blink <----------
# Group Name: EarLeds, RightEarLeds, LeftEarLeds...
# Short Name: RightEarLed1 ~ RightEarLed10, LeftEarLed1 ~ LeftEarLed10.

def Ear_Flush_Led():
	duration = 0.05
	RightEarLedList = ["RightEarLed1", "RightEarLed2", "RightEarLed3", "RightEarLed4", 
					   "RightEarLed5", "RightEarLed6", "RightEarLed7", "RightEarLed8",
					   "RightEarLed9", "RightEarLed10"]
	LeftEarLedList = ["LeftEarLed1", "LeftEarLed2", "LeftEarLed3", "LeftEarLed4", 
					  "LeftEarLed5", "LeftEarLed6", "LeftEarLed7", "LeftEarLed8",
					  "LeftEarLed9", "LeftEarLed10"]
	proxy = ALProxy("ALLeds", robot_ip, robot_port)
	proxy.fade("EarLeds", 0, 0) # set all ear leds off immediately.
	# fluse led...
	for i in range(len(RightEarLedList)):
		proxy.fade(LeftEarLedList[i], 1, duration)
		proxy.fade(RightEarLedList[i], 1, duration)
	for i in range(len(RightEarLedList)):
		proxy.fade(LeftEarLedList[i], 0, duration)
		proxy.fade(RightEarLedList[i], 0, duration)

# ----------> eye led blink <----------
# Group Name: FaceLeds, RightFaceLeds, LeftFaceLeds; 
# Group Name: FaceLedsBottom (3,4),FaceLedsTop (7,0),FaceLedsExternal (6,5),FaceLedsInternal (1,2) 
# Group Name: FaceLed0 ~ FaceLed7
# Short Name:  

def Face_Flush_Led():
	duration = 0.05
	FaceLedList = ["FaceLed0", "FaceLed1", "FaceLed2", "FaceLed3", 
				   "FaceLed4", "FaceLed5", "FaceLed6", "FaceLed7"]
	proxy = ALProxy("ALLeds", robot_ip, robot_port)
	proxy.fade("FaceLeds", 0, 0) # set all eye leds off immediately.
	# fluse led...
	for i in range(len(FaceLedList)):
		proxy.fade(FaceLedList[i], 1, duration)
	for i in range(len(FaceLedList)):
		proxy.fade(FaceLedList[i], 0, duration)

def blink():
	duration = 0.2
	FaceLedList = ["FaceLed0", "FaceLed1", "FaceLed2", "FaceLed3", 
				   "FaceLed4", "FaceLed5", "FaceLed6", "FaceLed7"]
	LedValueList = [0, 0, 1, 0,
					0, 0, 1, 0]
	proxy = ALProxy("ALLeds", robot_ip, robot_port)
	# blink face leds
	for i in range(len(FaceLedList)):
		proxy.post.fade(FaceLedList[i], LedValueList[i], duration)
	time.sleep(0.1)
	proxy.fade("FaceLeds", 1, duration) # set all eye leds off immediately.
	
def random_eyes():
	"""The color of the eyes changes randomly."""
	proxy = ALProxy("ALLeds", robot_ip, robot_port)
	while True:
		rRandTime = random.uniform(0.0, 2.0)
		proxy.fadeRGB("FaceLeds", 
			256 * random.randint(0,255) + 256 * 256 * random.randint(0,255) + random.randint(0,255),
			rRandTime)
		time.sleep(random.uniform(0.0,3.0))

while True:
#	Ear_Flush_Led()
#	Face_Flush_Led()
	blink()
#	random_eyes()
