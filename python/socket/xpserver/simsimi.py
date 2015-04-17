#! /usr/bin/env python
#-*- coding: utf-8 -*-
#################################################################
#	Copyright (C) 2015 Sean Guo. All rights reserved.
#														  
#	> File Name:		< simsimi.py >
#	> Author:			< Sean Guo >		
#	> Mail:				< iseanxp+code@gmail.com >		
#	> Created Time:		< 2015/04/17 >
#	> Last Changed: 
#	> Description:
#################################################################
# 从simsimi读数据
import requests			# python HTTP客户端库
import cookielib
import socket
import random
import sys
sys.path.append('..')
reload(sys)
sys.setdefaultencoding('utf-8')
 
# 如果申请SIMSIMI_KEY的话，则配置;
# 没有申请则伪造User-Agent和Referer获取到json串
try:
	from settings import SIMSIMI_KEY
except:
	# 申请的SIMSIMI Trial KEY, 只有7天, 1天100次;
	SIMSIMI_KEY = 'd62736f7-1a0e-40ff-a3ed-5c567da53cb6'
 
class SimSimi:
	def __init__(self):
		self.session = requests.Session()
		# 官方免费聊天页面
		self.chat_url = 'http://www.simsimi.com/func/req?lc=ch&msg=%s'
		# API Request URL, 配置好SIMSIMI_KEY, 发送text
		self.api_url = 'http://sandbox.api.simsimi.com/request.p?key=%s&lc=%s&ft=1.0&text=%s'
		# key, SIMSIMI KEY
		# lc, Language code, ch:Chinese - Simplified / en - English
		# text, Query message
		# ft, Double(0.0 ~ 1.0)

		# 没有申请SIMSIMI_KEY, 则伪造浏览器获取;
		if not SIMSIMI_KEY:
			print 'initSimSimiCookie'
			self.initSimSimiCookie()
 
	def initSimSimiCookie(self):
		'''
			构造头信息，准备将Cookies添加在HTTP头部信息中;
		'''
		self.session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0'})
		self.session.get('http://www.simsimi.com/talk.htm')
		self.session.headers.update({'Referer': 'http://www.simsimi.com/talk.htm'})
		self.session.get('http://www.simsimi.com/talk.htm?lc=ch')
		self.session.headers.update({'Referer': 'http://www.simsimi.com/talk.htm?lc=ch'})
 
	def getSimSimiResult(self, message, method='normal', language='ch'):
		'''
			向SimSimi发送请求, 返回页面返回响应;
		'''
		if method == 'normal':		# 使用simsimi的talk页面模拟浏览器聊天;
			response = self.session.get(self.chat_url % message)
		else:						# 使用SIMSIMI_KEY发送请求
			url = self.api_url % (SIMSIMI_KEY, language, message)
			response = requests.get(url)
		return response
 
	def chat(self, message='', language='ch'):
		'''
			接受用户输入的信息, 返回SimSimi的反馈结果;
		'''
		if message:
			if SIMSIMI_KEY == '':
				r = self.getSimSimiResult(message, 'normal')
			else:
				r = self.getSimSimiResult(message, 'api', language)
			# 获得返回结果, 查看其反馈信息;
			try:
				answer = r.json()['response']
				return answer.encode('utf-8')
			except:
				return random.choice(['呵呵', '。。。', '= =', '=。='])
		else:
			return '叫我干嘛'
 
#simsimi = SimSimi()

def handle(data, bot):
	return simsimi.chat(data['message'])


def main():
#	print handle({'message': '最后一个问题'}, None)
#	print handle({'message': '还有一个问题'}, None)
#	print handle({'message': '其实我有三个问题'}, None)
	simsimi = SimSimi()
	while True:
		text = raw_input('输入:')
		print simsimi.chat(text,'ch')

if __name__ == '__main__':
	main()
