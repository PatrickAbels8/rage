import sys
import os
from time import sleep
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory, listenWS

import random
import json
from random import shuffle

from logic import create_deck, get_winner, bonus_minus, bonus_plus, trump_now, trump_later


class ServerProtocol(WebSocketServerProtocol):

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
		self.factory.board = ''

		start_id = random.randint(0, len(self.factory.clients)-1)
		for i, c in enumerate(self.factory.clients):
			if i == start_id:
				self.factory.start_id_id = i

		
	def start_game(self):
		# set order of rounds
		cards_list = list(range(1, 11)) if self.factory.mode == '++' else list(range(10, 0, -1))

		# init statistics
		my_stats = {}
		for c in self.factory.clients:
			my_client = {}
			for nc in cards_list:
				my_cell = {'pre': -1, 'post': 0, 'bonus': 0, 'points': 0}
				my_client[nc] = my_cell
			my_stats[self.factory.clients[c]['name']] = my_client
		# self.factory.stats = dict.fromkeys([self.factory.clients[c]['name'] for c in self.factory.clients], dict.fromkeys(cards_list, dict.fromkeys(['pre', 'post', 'bonus', 'points'], -1)))
		self.factory.stats = my_stats

		self.game_loop()

	def game_loop(self):
		num_cards = self.factory.round
		print('>>> ROUND', str(num_cards), '<<<')

		# shuffle cards
		self.factory.cur_deck = self.factory.deck
		shuffle(self.factory.cur_deck)

		# deal cards
		for c in self.factory.clients:
			self.factory.clients[c]['cards'] = ' '.join(self.factory.cur_deck[:num_cards])
			self.factory.cur_deck = self.factory.cur_deck[num_cards:]
		self.factory.trump = self.factory.cur_deck.pop()
		while self.factory.trump[0] == 'j':
			self.factory.trump = self.factory.cur_deck.pop()

		# start player 
		for i, c in enumerate(self.factory.clients):
			if i == self.factory.start_id_id:
				start_client = c


		# bcast board
		for c in self.factory.clients:
			cur_board = {'board':self.factory.board, 'trump': self.factory.trump, 'turn': self.factory.clients[start_client]['id'], 'cards': self.factory.clients[c]['cards'], 'stats': self.factory.stats}
			self.factory.send(c, 'BOARD'+str(self.factory.round)+self.factory.mode, cur_board)

		
	# broadcast final stats
	def end_game(self):
		for c in self.factory.clients:
			self.factory.send(c, 'END', self.factory.stats)


	def onOpen(self):
		self.factory.register(self)
		ids = [self.factory.clients[c]['id'] for c in self.factory.clients]
		client_id = 0
		while client_id not in ids:
			client_id += 1 
		for c in self.factory.clients:
			if self.factory.clients[c]['id'] == client_id:
				self.factory.send(c, 'GO', str(len(self.factory.clients)))
			

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
				c_id = int(c_id)

				for i, c in enumerate(self.factory.clients):
					if self.factory.clients[c]['id'] == c_id:
						c_id_id = i
						cur_c = c

				next_id_id = (c_id_id+1)%len(self.factory.clients)

				for i, c in enumerate(self.factory.clients):
					if i == next_id_id:
						next_c = c
						next_id = self.factory.clients[c]['id']

				if self.factory.stats[self.factory.clients[cur_c]['name']][self.factory.round]['pre'] < 0:
					# called number of points to make
					self.factory.stats[self.factory.clients[cur_c]['name']][self.factory.round]['pre'] = int(move)

					for c in self.factory.clients:
						cur_board = {'board':self.factory.board, 'trump': self.factory.trump, 'turn': next_id, 'cards': self.factory.clients[c]['cards'], 'stats': self.factory.stats}
						self.factory.send(c, 'BOARD'+str(self.factory.round)+self.factory.mode, cur_board)
				else:
					# played a card
					for c in self.factory.clients:
						if self.factory.clients[c]['id'] == c_id:
							cards = self.factory.clients[c]['cards'].split()
							cards.remove(move)
							self.factory.clients[c]['cards'] = ' '.join(cards)

					self.factory.board = ' '.join([self.factory.board, move])
					if move == trump_now:
						if len(self.factory.trump)==2:
							cur_trump_col = self.factory.trump[0]
							while self.factory.trump[0] in [cur_trump_col, 'j']:
								self.factory.trump = self.factory.cur_deck.pop()
						else:
							cur_trump_col = self.factory.safed_trump_col
							self.factory.trump = self.factory.cur_deck.pop()
							while self.factory.trump[0] in [cur_trump_col, 'j']:
								self.factory.trump = self.factory.cur_deck.pop()
					elif move == trump_later:
						self.factory.safed_trump_col = self.factory.trump[0]
						self.factory.trump = ''

					
					if len(self.factory.board.split()) == len(self.factory.clients):
						next_id = self.save_board(c_id_id)
						self.factory.board = ''

					if len(self.factory.clients[next_c]['cards'].split()) > 0:
						# round goes on
						for c in self.factory.clients:
							cur_board = {'board':self.factory.board, 'trump': self.factory.trump, 'turn': next_id, 'cards': self.factory.clients[c]['cards'], 'stats': self.factory.stats}
							self.factory.send(c, 'BOARD'+str(self.factory.round)+self.factory.mode, cur_board)
					else:
						# next round
						next_start_id_id = (next_id_id+1)%len(self.factory.clients)
						self.factory.start_id_id = next_start_id_id

						next_round = self.factory.round+1 if self.factory.mode=='++' else self.factory.round-1
						if next_round > self.factory.num_rounds or next_round < 1:
							self.end_game()
						else:
							self.factory.round = next_round

						self.game_loop()


	def save_board(self, c_id_id):
		winner_id_id = get_winner(self.factory.board, self.factory.trump, c_id_id)

		for i, c in enumerate(self.factory.clients):
			if i == winner_id_id:
				winner_id = self.factory.clients[c]['id']
				winner_name = self.factory.clients[c]['name']

		for card in self.factory.board.split():
			if card == bonus_minus:
				self.factory.stats[winner_name][self.factory.round]['bonus'] = self.factory.stats[winner_name][self.factory.round]['bonus'] - 5
			elif card == bonus_plus:
				self.factory.stats[winner_name][self.factory.round]['bonus'] = self.factory.stats[winner_name][self.factory.round]['bonus'] + 5
		self.factory.stats[winner_name][self.factory.round]['post'] = self.factory.stats[winner_name][self.factory.round]['post'] + 1

		round_over = True
		for c in self.factory.clients:
			if len(self.factory.clients[c]['cards']) > 0:
				round_over = False
		if round_over:
			for c in self.factory.stats:
				if self.factory.stats[c][self.factory.round]['pre'] == self.factory.stats[c][self.factory.round]['post']:
					self.factory.stats[c][self.factory.round]['points'] = 10
				else:
					self.factory.stats[c][self.factory.round]['points'] = -5

				self.factory.stats[c][self.factory.round]['points'] = self.factory.stats[c][self.factory.round]['points'] + self.factory.stats[c][self.factory.round]['post']
				
				if self.factory.stats[c][self.factory.round]['post'] == self.factory.round and self.factory.round != 1:
					self.factory.stats[c][self.factory.round]['points'] = self.factory.stats[c][self.factory.round]['points'] + self.factory.stats[c][self.factory.round]['post']

				self.factory.stats[c][self.factory.round]['points'] = self.factory.stats[c][self.factory.round]['points'] + self.factory.stats[c][self.factory.round]['bonus']

		return winner_id



	def connectionLost(self, reason):
		WebSocketServerProtocol.connectionLost(self, reason)
		self.factory.unregister(self)

	def print_clients(self):
		for c in self.factory.clients:
			print(self.factory.clients[c]['id'], self.factory.clients[c]['name'])


class ServerFactory(WebSocketServerFactory):

	def __init__(self, url):
		WebSocketServerFactory.__init__(self, url)
		self.clients = {}
		self.mode = None
		self.deck = []
		self.cur_deck = []
		self.start_id_id = None
		self.board = ''
		self.trump = ''
		self.round = None
		self.stats = None
		self.num_rounds = 10

		self.safed_trump_col = ''
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
		if 'BOARD' in key:
			stats_value = value['stats']
			stats_msg = ''
			for c in stats_value:
				stats_msg += c
				for r in stats_value[c]:
					stats_msg += '_'
					for q in stats_value[c][r]:
						stats_msg += str(stats_value[c][r][q])
						stats_msg += '/'
				stats_msg += '&'
			msg = '#'.join([value['board'], value['trump'], str(value['turn']), value['cards'], stats_msg])
			value = msg
		elif key == 'END':
			msg = ''
			for c in value:
				msg += c
				for r in value[c]:
					msg += '_'
					for q in value[c][r]:
						msg += str(value[c][r][q])
						msg += '/'
				msg += '&'
			value = msg
		client.sendMessage(':'.join([key, value]).encode('utf8'))


server_factory = ServerFactory
factory = server_factory('ws://127.0.0.1:9000')
factory.protocol = ServerProtocol
listenWS(factory)
reactor.listenTCP(8000, Site(File(".")))

reactor.run()