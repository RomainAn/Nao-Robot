Nao Robot Touch Test
---

###传感器： 电容式传感器 capacitive sensors

 ALMemory:
 
Device/SubDeviceList/Head/Touch/Front/Sensor/Value
Device/SubDeviceList/Head/Touch/Middle/Sensor/Value
Device/SubDeviceList/Head/Touch/Rear/Sensor/Value

###Sensor List:
	std::vector<std::string> ALTouchProxy::getSensorList()

* 'Head/Touch/Front', 
* 'Head/Touch/Middle', 
* 'Head/Touch/Rear',

* 'LHand/Touch/Back',
* 'LHand/Touch/Left',
* 'LHand/Touch/Right',


* 'RHand/Touch/Back', 
* 'RHand/Touch/Left', 
* 'RHand/Touch/Right',

* 'LFoot/Bumper/Left', 
* 'LFoot/Bumper/Right',

* 'RFoot/Bumper/Left',
* 'RFoot/Bumper/Right'


----
	ALValue ALTouchProxy::getStatus()
时效性不及基于事件的响应callback函数；

###头部触摸：
将手放在Nao robot头部；
Nao robot 头部有三块触摸区域，分别对应Head/Touch/Front、Head/Touch/Middle、Head/Touch/Rear，触摸成功后，相应区域会有LED灯点亮；    
（可以根据头部三块触摸区域，当作启动某些功能的密码识别。）

输出示例：

触摸头部：（立刻触发TouchChanged事件）    
	
[['Head', True, [1]], ['Head/Touch/Front', True, [1]], ['Head/Touch/Middle', True, [1]], ['Head/Touch/Rear', True, [1]]]

离开头部：（需等待一段事件，触发TouchChanged事件）    
[['Head', False], ['Head/Touch/Front', False], ['Head/Touch/Middle', False], ['Head/Touch/Rear', False]]

不触摸机器人头部，而改变机器人的头部位置（较为剧烈），会触发：   
['Head', True, [3]]    
静止头部后一段时间，再次触发事件并返回[['Head', False]]；

响应速度：快速连续触摸时略有延时。可用于常用的简单功能。可以设置响应反馈（例如机器人检测到一次触摸，响铃一声），从而实现密码功能。

#### 基于事件的触摸测试：「Event: "TouchChanged"」

触摸前后，callback函数中都有触摸状态的改变；

[['Head', True, [1]], ['Head/Touch/Front', True, [1]]]

手离开头部一段事件后，才返回触摸后状态；
猜想可能是由于电容式传感器的电容特性引起的。    
[['Head', False], ['Head/Touch/Front', False]]

###手部触摸：
Nao Robot 手部左右也各有三个电容传感器。
分别对应：Left, Back, Right;
大致测试与头部触摸传感器类似。精度可以，触摸后立刻触发TouchChanged，离开触摸后一段事件才再次触发TouchChanged。

### 脚步触摸

响应同头部触摸，每支脚分别对应两个触摸传感器（Left/Right），不过由于脚部零件问题，经常是Left/Right一起触发。

