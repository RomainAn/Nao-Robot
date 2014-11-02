from naoqi import ALProxy
#-*- coding: utf-8 -*-

# ----------> Connect to robot <----------
robot_ip = "192.168.1.100"
robot_port = 9559	# default port : 9559
motion = ALProxy("ALMotion", robot_ip, robot_port)
tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)

# ----------> Set stiffness <----------
# The robot will not move unless you set the stiffness of the joints to something that is not 0.

# void ALMotionProxy::setStiffnesses(const AL::ALValue& names, const AL::ALValue& stiffnesses)
# Parameters:
#	names - Names of joints, chains, “Body”, “JointActuators”, “Joints” or “Actuator
#	stiffnesses - One or more stiffnesses between zero and one.
motion.setStiffnesses("Body", 1.0)
#motion.setStiffnesses("Body", 0.0)

# ----------> Make robot move <----------

# Wake up robot
motion.wakeUp()

# void ALMotionProxy::moveInit()
# Initializes the move process. Checks the robot pose and takes a right posture. This is blocking called.
motion.moveInit()

# void ALMotionProxy::moveTo(const float& x, const float& y, const float& theta)
# Makes the robot move to the given pose in the ground plane, relative to FRAME_ROBOT. This is a blocking call.
# Parameters:	
#	x - Distance along the X axis in meters.
#	y - Distance along the Y axis in meters.
#	theta - Rotation around the Z axis in radians [-3.1415 to 3.1415].
motion.moveTo(0.5, 0, 0)
# If moveTo() method does nothing on the robot, read the section about walk protection.
tts.setLanguage("English")
tts.say("I'm walking")


# robot rest
motion.rest()
