from naoqi import ALProxy
#-*- coding: utf-8 -*-

# ----------> Connect to robot <----------
robot_ip = "192.168.1.100"
robot_port = 9559			# default port : 9559
memProxy = ALProxy("ALMemory", robot_ip, robot_port)

# ----------> Get data <----------

# 机器人上配备了一个两轴陀螺仪，位于身体中心部位。它包括3个子器件以及一个参考值。
# 这些传感器提供围绕机器人X轴和Y轴的旋转速度。
print memProxy.getData("Device/SubDeviceList/LShoulderPitch/Position/Sensor/Value")
print memProxy.getData("Device/SubDeviceList/InertialSensor/GyrX/Sensor/Value")
print memProxy.getData("Device/SubDeviceList/InertialSensor/GyrY/Sensor/Value")
#print memProxy.getData("Device/SubDeviceList/InertialSensor/GyrRef/Sensor/Value")
