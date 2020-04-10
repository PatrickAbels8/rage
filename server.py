import sys
import os
from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS

from gui import game_tick, init
from twisted.internet.task import LoopingCall

'''
TODO
- 
'''

def new_game():
	print('--- NEW GAME ---')
	factory.shots = []
	init()


class ServerProtocol(WebSocketServerProtocol):

	def read_balls(self): # todo save top card of stack and state of game somewhere and load it here
		# if os.path.exists('board.txt'):
		# 	with open('board.txt', 'r') as f:
		# 		return f.read()
		# else:
		# 	return ''
		return 'r1, 0:3/1:0/2:0'

	def read_cards(self): # todo save cards in dict and load the right ones here
		# self.factory.turn
		return 'r3 g2 b9'

	def render(self, shot):
		self.factory.shots.append(shot)
		game_tick(self.factory.shots)

	def broadcastBoard(self):
		self.factory.broadcast(self.factory.turn + "'s Turn:\n" + 'Board: ' + self.read_balls() + '\nCards: ' + self.read_cards())

	def onOpen(self):
		self.factory.register(self)
		if len(self.factory.clients) == max_clients:
			new_game()
			self.broadcastBoard()
			

	def onMessage(self, payload, isBinary):
		if not isBinary:
			shot = payload.decode('utf8')
			print(self.factory.turn + ': ' + shot)
			self.render(shot)
			self.factory.turn = str((int(self.factory.turn)+1)%len(self.factory.clients)) # not always the same one to start
			self.broadcastBoard()

	def connectionLost(self, reason): # todo deconnect clients if server crashes
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url):
		WebSocketServerFactory.__init__(self, url)
		self.clients = [] # todo dict with id, cards, ...
		self.turn = '0'
		self.shots = []

	def register(self, client): # todo reconnection not depending on clients length bc duplicate client_ids
		if client not in self.clients:
			client_id = str(len(self.clients))
			hello_msg = 'HELLO '+client_id
			client.sendMessage(hello_msg.encode('utf8'))
			self.clients.append(client)
			print('CONNECT')

	def unregister(self, client):
		if client in self.clients:
			self.clients.remove(client)
			print('DECONNECT')

	def broadcast(self, msg):
		for c in self.clients:
			c.sendMessage(msg.encode('utf8'))

max_clients = 3



server_factory = ServerFactory
factory = server_factory('ws://127.0.0.1:9000')
factory.protocol = ServerProtocol
listenWS(factory)
reactor.listenTCP(8000, Site(File(".")))

reactor.run()