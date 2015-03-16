#-*- coding: utf-8 -*-
from naoqi import ALProxy

# ----------> Connect to robot <----------
robot_ip = "192.168.1.100"
robot_port = 9559			# default port : 9559

motionProxy = ALProxy("ALMotion", robot_ip, robot_port)
postureProxy = ALProxy("ALRobotPosture", robot_ip, robot_port)
navigationProxy = ALProxy("ALNavigation", robot_ip, robot_port)

# ----------> stand init <----------

# Wake up robot
motionProxy.wakeUp()

# Send robot to Stand Init
postureProxy.goToPosture("StandInit", 0.5)

# No specific move config.
motionProxy.moveTo(1.0, 0.0, 0.0)
motionProxy.moveTo(1.0, 0.0, 0.0, [])

# To do 6 cm steps instead of 4 cm.
motionProxy.moveTo(1.0, 0.0, 0.0, [["MaxStepX", "0.06"]])

# Will stop at 0.5m (FRAME_ROBOT) instead of 0.4m away from the obstacle.
# 设置安全距离为0.5m, 遇到障碍物在0.5m内则停止.
navigationProxy.setSecurityDistance(0.5)
