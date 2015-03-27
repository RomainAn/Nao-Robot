Nao Robot Joint Control
----

可以单独的控制一个关节的位置(指定关节的名称)，也可以并行控制(指定一组关节的组名称, 例如"Body")。

##两种控制方法

1. animation methods (time fixed, blocking function)
	* ALMotionProxy::angleInterpolation()
	* ALMotionProxy::angleInterpolationWithSpeed()
2. reactive methods (could be changed every ALMotion cycle, non blocking function)
	* ALMotionProxy::setAngles()
	* ALMotionProxy::changeAngles()

关节控制的工作原理是基于Naoqi的DCM模块.

----

##Naoqi API
####获得Body的所有关节名称
	motion.getBodyNames(“Body”)
	
	
	motion.getBodyNames("Body")
	
['HeadYaw', 'HeadPitch', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw', 'LHand', 'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll', 'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll', 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw', 'RHand']

----





	
	