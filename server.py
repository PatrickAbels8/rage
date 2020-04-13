import sys
import os
from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS

from gui import game_tick, init, stack
from twisted.internet.task import LoopingCall

from random import shuffle
from tkinter import *

tk = Tk()
tk.withdraw()




def new_game():
	print('--- NEW GAME ---')
	factory.shots = []
	init()


class ServerProtocol(WebSocketServerProtocol):

	cards_per_client = IntVar(value=0) # not working yet

	def deal_cards(self, num_cards):
		print('>>> DEAL:', num_cards)
		s = stack
		shuffle(s)
		for c in self.factory.clients:
			self.factory.clients[c]['cards'] = ' '.join(s[:num_cards])
			s = s[num_cards:]
		self.factory.shots = [s.pop()]

		self.cards_per_client.set(num_cards)

	def read_board(self):
		top_card = self.factory.shots[-1]
		statistics = self.factory.statistics
		return top_card + ', ' + statistics

	def read_cards(self): 
		for c in self.factory.clients:
			if self.factory.turn == self.factory.clients[c]['id']:
				return self.factory.clients[c]['cards']
		return 'r1 r2 r3'

	def round_over(self):
		for c in self.factory.clients:
			if len(self.factory.clients[c]['cards'].split()) > 0:
				return False
		return True


	def render(self, shot):
		self.factory.shots.append(shot)
		for c in self.factory.clients:
			if self.factory.turn == self.factory.clients[c]['id']:
				cards = self.factory.clients[c]['cards'].split()
				cards.remove(shot)
				self.factory.clients[c]['cards'] = ' '.join(cards)				
		game_tick(self.factory.shots)

	def broadcastBoard(self):
		self.factory.broadcast(self.factory.turn + "'s Turn:\n" + 'Board: ' + self.read_board() + '\nCards: ' + self.read_cards())

	def var_changed(self):
		if self.cards_per_client == 0:
			self.deal_cards(i)
			self.broadcastBoard()

	def onOpen(self):
		self.factory.register(self)
		if len(self.factory.clients) == max_clients:
			new_game()
			# todo interactive mode
			for i in [1,2,3,4,5,6,7,8,9,10]:
				self.cards_per_client.trace(mode="w", callback=lambda: self.var_changed(i))
			

	def onMessage(self, payload, isBinary):
		if not isBinary:
			shot = payload.decode('utf8')
			print(self.factory.turn + ': ' + shot)
			self.render(shot)
			if self.round_over():
				self.cards_per_client.set(0)
			self.factory.turn = str((int(self.factory.turn)+1)%len(self.factory.clients)) # todo not always the same one to start
			self.broadcastBoard()

	def connectionLost(self, reason): # todo deconnect clients if server crashes
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url):
		WebSocketServerFactory.__init__(self, url)
		self.clients = {}
		self.turn = '0'
		self.shots = []
		self.statistics = '0:3/1:0/2:0' # todo

	def register(self, client): # todo reconnection not depending on clients length bc duplicate client_ids
		if client not in self.clients:
			client_id = str(len(self.clients))
			hello_msg = 'HELLO '+client_id
			client.sendMessage(hello_msg.encode('utf8'))
			self.clients[client] = {'id': client_id, 'cards': ''}
			print('CONNECT')

	def unregister(self, client):
		if client in self.clients:
			del self.clients[client]
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