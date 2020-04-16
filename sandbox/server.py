import sys
import os
from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS

# from gui import game_tick, init, stack
# from twisted.internet.task import LoopingCall

# from random import shuffle
# from tkinter import *

# tk = Tk()
# tk.withdraw()




# def new_game():
# 	print('--- NEW GAME ---')
# 	factory.shots = []
# 	init()


class ServerProtocol(WebSocketServerProtocol):

	# cards_per_client = IntVar(value=0) # not working yet

	# def deal_cards(self, num_cards):
	# 	print('>>> DEAL:', num_cards)
	# 	s = stack
	# 	shuffle(s)
	# 	for c in self.factory.clients:
	# 		self.factory.clients[c]['cards'] = ' '.join(s[:num_cards])
	# 		s = s[num_cards:]
	# 	self.factory.shots = [s.pop()]

		# self.cards_per_client.set(num_cards)

	# def read_board(self):
	# 	top_card = self.factory.shots[-1]
	# 	statistics = self.factory.statistics
	# 	return top_card + ', ' + statistics

	# def read_cards(self): 
	# 	for c in self.factory.clients:
	# 		if self.factory.turn == self.factory.clients[c]['id']:
	# 			return self.factory.clients[c]['cards']
	# 	return 'r1 r2 r3'

	# def round_over(self):
	# 	for c in self.factory.clients:
	# 		if len(self.factory.clients[c]['cards'].split()) > 0:
	# 			return False
	# 	return True


	# def render(self, shot):
	# 	self.factory.shots.append(shot)
	# 	for c in self.factory.clients:
	# 		if self.factory.turn == self.factory.clients[c]['id']:
	# 			cards = self.factory.clients[c]['cards'].split()
	# 			cards.remove(shot)
	# 			self.factory.clients[c]['cards'] = ' '.join(cards)				
	# 	game_tick(self.factory.shots)

	# def broadcastBoard(self):
	# 	self.factory.broadcast(self.factory.turn + "'s Turn:\n" + 'Board: ' + self.read_board() + '\nCards: ' + self.read_cards())

	# def var_changed(self):
	# 	if self.cards_per_client == 0:
	# 		self.deal_cards(i)
	# 		self.broadcastBoard()

	def start_game(self):
		print('--- START GAME (', str(len(self.factory.clients)), ') ---')

		# choose game mode
		ids = [self.factory.clients[c]['id'] for c in self.factory.clients]
		client_id = 0
		while client_id not in ids:
			client_id += 1 
		for c in self.factory.clients:
			if self.factory.clients[c]['id'] == client_id:
				self.factory.send(c, 'MODE', '')

		# create deck

		# choose start player

		# start round 10
		# start round 9
		# ...
		# start round 1

		# broadcast stats


	def onOpen(self):
		self.factory.register(self)
		ids = [self.factory.clients[c]['id'] for c in self.factory.clients]
		client_id = 0
		while client_id not in ids:
			client_id += 1 
		for c in self.factory.clients:
			if self.factory.clients[c]['id'] == client_id:
				self.factory.send(c, 'GO', '')

		# if len(self.factory.clients) == max_clients:
		# 	new_game()
		# 	# todo interactive mode
		# 	# for i in [1,2,3,4,5,6,7,8,9,10]:
		# 	# 	self.cards_per_client.trace(mode="w", callback=lambda: self.var_changed(i))
		# 	self.deal_cards(5)
		# 	self.broadcastBoard()
			

	def onMessage(self, payload, isBinary):
		if not isBinary:
			msg = payload.decode('utf8')
			print(msg)
			if 'HELLO' in msg:
				c_id, c_name = msg.split()[1:]
				for c in self.factory.clients:
					if self.factory.clients[c]['id'] == int(c_id):
						self.factory.clients[c]['name'] = c_name

			if 'GO' in msg:
				go = msg.split()[1]
				if go in ['y', 'yes', 'Y', 'Yes', '1']:
					self.start_game()

			if 'MODE' in msg:
				mode = msg.split()[1]
				if mode in ['1-10', 'up', '++']:
					self.factory.mode = '++'
				else:
					self.factory.mode = '--'


			# print(self.factory.turn + ': ' + shot)
			# self.render(shot)
			# if self.round_over():
			# 	self.cards_per_client.set(0)
			# self.factory.turn = str((int(self.factory.turn)+1)%len(self.factory.clients)) # todo not always the same one to start
			# self.broadcastBoard()

	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url):
		WebSocketServerFactory.__init__(self, url)
		self.clients = {}
		self.mode = ''
		# self.turn = '0'
		# self.shots = []
		# self.statistics = '0:3/1:0/2:0' # todo
		print('waiting ...')

	def register(self, client): # todo reconnection not depending on clients length bc duplicate client_ids
		if client not in self.clients:
			ids = [self.clients[c]['id'] for c in self.clients]
			client_id = 0
			while client_id in ids:
				client_id += 1
			self.send(client, 'HELLO', str(client_id))
			self.clients[client] = {'id': client_id, 'name': '', 'cards': ''}
			print('CLIENT CONNECTED', client_id)

	def unregister(self, client):
		if client in self.clients:
			print('DECONNECT', self.clients[client]['name'])
			del self.clients[client]

	def send(self, client, key, value):
		client.sendMessage(' '.join([key, value]).encode('utf8'))

	def broadcast(self, msg):
		pass
		# for c in self.clients:
		# 	c.sendMessage(msg.encode('utf8'))

# max_clients = 3



server_factory = ServerFactory
factory = server_factory('ws://127.0.0.1:9000')
factory.protocol = ServerProtocol
listenWS(factory)
reactor.listenTCP(8000, Site(File(".")))

reactor.run()