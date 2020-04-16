import sys
import os
from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS

import random
import json

# tba
from logic import create_deck



# from gui import game_tick, init, stack
# from twisted.internet.task import LoopingCall

# from random import shuffle
# from tkinter import *

# tk = Tk()
# tk.withdraw()


class ServerProtocol(WebSocketServerProtocol):

	# cards_per_client = IntVar(value=0) # not working yet


	# def read_board(self):
	# 	top_card = self.factory.shots[-1]
	# 	statistics = self.factory.statistics
	# 	return top_card + ', ' + statistics

	def init_game(self):
		print('--- START GAME (', str(len(self.factory.clients)), ') ---')

		ids = [self.factory.clients[c]['id'] for c in self.factory.clients]
		client_id = 0
		while client_id not in ids:
			client_id += 1 
		for c in self.factory.clients:
			if self.factory.clients[c]['id'] == client_id:
				self.factory.send(c, 'MODE', '')

		self.factory.deck = create_deck()

		start_id = random.randint(0, len(self.factory.clients)-1)
		for i, c in enumerate(self.factory.clients):
			if i == start_id:
				self.factory.start_id_id = i

		
	def start_game(self):
		# set order of rounds
		cards_list = list(range(1, 11)) if self.factory.mode == '++' else list(range(10, 0, -1))

		# init statistics and cards
		self.factory.stats = dict.fromkeys([self.factory.clients[c]['name'] for c in self.factory.clients], dict.fromkeys(cards_list, dict.fromkeys(['pre', 'post', 'bonus', 'points'], -1)))
		stack = self.factory.deck

		# set player who starts first round
		# for i, c in enumerate(self.factory.clients):
		# 	if self.factory.start_client == c:
		# 		round_start_id = i

		self.game_loop()

	def game_loop(self):
		num_cards = self.factory.round
		print('>>> ROUND', str(num_cards), '<<<')

		# get clients dict with start player being first
		# tmp_clients = {}
		# for i, c in enumerate(self.factory.clients):
		# 	if i >= round_start_id:
		# 		tmp_clients[c] = self.factory.clients[c]
		# for c in self.factory.clients:
		# 	if c not in tmp_clients:
		# 		tmp_clients[c] = self.factory.clients[c]
		# self.factory.clients = tmp_clients

		# shuffle cards
		shuffle(stack)

		# deal cards
		for c in self.factory.clients:
			self.factory.clients[c]['cards'] = ' '.join(stack[:num_cards])
			stack = stack[num_cards:]
		self.factory.board = stack.pop()

		# start player 
		for i, c in enumerate(self.factory.clients):
			if i == self.factory.start_id_id:
				start_client = c

		# bcast board
		for c in self.factory.clients:
			cur_board = {'board':self.factory.board, 'turn': self.factory.clients[start_client]['id'], 'cards': self.factory.clients[c]['cards'], 'stats': self.factory.stats}
			self.factory.send(c, 'BOARD', json.dumps(cur_board))

		
	# broadcast final stats
	def end_game(self):
		for c in self.factory.clients:
			self.factory.send(c, 'END', json.dumps(self.factory.stats))


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
					self.init_game()

			if 'MODE' in msg:
				mode = msg.split()[1]
				if mode in ['1-10', 'up', '++']:
					self.factory.mode = '++'
					self.factory.round = 1
				else:
					self.factory.mode = '--'
					self.factory.round = 10
				self.start_game()

			if 'MOVE' in msg:
				c_id, move = msg.split()[1:]

				for i, c in enumerate(self.factory.clients):
					if self.factory.clients[c]['id'] == int(c_id):
						c_id_id = i

				next_id_id = (c_id_id+1)%len(self.factory.clients)
				for i, c in enumerate(self.factory.clients):
					if i == c_id_id:
						next_c = c
						next_id = self.factory.clients[c]['id']

				if self.factory.stats[self.factory.clients[c]['name']][self.factory.round]['pre'] < 0:
					# called number of points to make
					self.factory.stats[self.factory.clients[c]['name']][self.factory.round]['pre'] = int(move)
					for c in self.factory.clients:
						cur_board = {'board':self.factory.board, 'turn': next_id, 'cards': self.factory.clients[c]['cards'], 'stats': self.factory.stats}
						self.factory.send(c, 'BOARD', json.dumps(cur_board))
				else:
					# played a card
					self.factory.board = ' '.join([self.factory.board, move])
					
					self.change_stats()

					for c in self.factory.clients:
						if self.factory.clients[c]['id'] == c_id:
							cards = self.factory.clients[c]['cards'].split()
							cards.remove(move)
							self.factory.clients[c]['cards'] = ' '.join(cards)
					if len(self.factory.clients[next_c]['cards'].split()) > 0:
						# round goes on
						# todo if board length == num clients, clear board and call render_stats for next player
						# todo else 
						for c in self.factory.clients:
							cur_board = {'board':self.factory.board, 'turn': next_id, 'cards': self.factory.clients[c]['cards'], 'stats': self.factory.stats}
							self.factory.send(c, 'BOARD', json.dumps(cur_board))
					else:
						# next round
						next_start_id_id = (next_id_id+1)%len(self.factory.clients)
						self.factory.start_id_id = next_start_id_id

						next_round = self.factory.round+1 if self.factory.mode=='++' else self.factory.round-1
						if next_round > 10 or next_round < 1:
							self.end_game()
						else:
							self.factory.round = next_round

						self.game_loop()

	# if board length == num clients: 
		# evaluate (consider startidid)
		# render +5 nd -5
	# if no cards left:
		# render -10 and -5
	def change_stats(self):
		pass


	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url):
		WebSocketServerFactory.__init__(self, url)
		self.clients = {}
		self.mode = None
		self.deck = None
		self.start_id_id = None
		self.board = ''
		self.round = None
		# self.turn = '0'
		# self.shots = []
		self.stats = None
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


server_factory = ServerFactory
factory = server_factory('ws://127.0.0.1:9000')
factory.protocol = ServerProtocol
listenWS(factory)
reactor.listenTCP(8000, Site(File(".")))

reactor.run()