# -*- coding: utf-8 -*-
import time


class MessageBox(object):

	def __init__(self):
		self.listMsg = []

	def AddMessageQueue(msg):
		self.listMsg.Append(time.strftime("%d-%m-%y-%H-%M-%S")+msg)

	def SendMessageQueue(keep=False):
		return "$$".join(self.listMsg)

