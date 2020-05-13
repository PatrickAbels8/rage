import sys
from time import sleep
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS
import json

from gui import onEnd, onBoard
 



class ClientProtocol(WebSocketClientProtocol):

	player_id = 0
	player_name = ''

	def onOpen(self):
		print('CONNECTED TO SERVER')

	def onMessage(self, payload, isBinary):
		if not isBinary:
			msg = payload.decode('utf8')
			print(msg)
			if 'HELLO' in msg:
				self.player_id = int(msg.split(':')[1])
				self.player_name = input('Name: ')
				self.send('HELLO', ' '.join([str(self.player_id), self.player_name]))

			elif 'MODE' in msg:
				mode = input('mode (10-1 / 1-10): ')
				self.send('MODE', mode)

			elif 'GO' in msg:
				go = input('go (y / n): ')
				self.send('GO', go)

			elif 'END' in msg:
				msg = msg.split(':')[1]
				onEnd(msg)

			elif 'BOARD' in msg:
				board, trump, turn, cards, stats = msg.split(':')[1].split('#')
				turn = int(turn)

				moves = self.possible_moves(board, trump, turn, cards)
				if self.player_id==int(turn):

					# preproc stats
					cs = stats.split('&')[:-1]
					for i in range(len(cs)):
						cs[i] = cs[i].split('_')
					for c in cs:
						if self.player_name in c:
							my_stats = c[1:]
					round_mode = msg.split(':')[0].split('D')[1]
					index = int(round_mode[:-2])-1 if round_mode[-2:]=='++' else 10-int(round_mode[:-2])
					call = len(board)==0 and int(my_stats[index].split('/')[0])<0

					# wait for goal
					if call:	
						move = -1
						# while not move in range(0, int(round_mode[:-2])+1):
						# 	# move_t = input('goal: ')
						# 	move_t = onBoard('call', board, trump, cards, stats, moves)
						# 	try:
						# 		move = int(move_t)
						# 	except:
						# 		continue
						while move not in range(len(cards.split())+1):
							move = onBoard('call', board, trump, cards, stats, moves, self.player_name)

						move_msg = ' '.join([str(self.player_id), str(move)])
						self.send('MOVE', move_msg)	

					# wait for move
					else:
						move = ''
						while not move in moves:
							# move = input('move: ')
							move = onBoard('move', board, trump, cards, stats, moves, self.player_name)
						move_msg = ' '.join([str(self.player_id), move])
						self.send('MOVE', move_msg)			

	
	def possible_moves(self, board, trump, turn, cards):
		if self.player_id!=turn:
			return []
		else:
			return cards.split()


	def send(self, key, value):
		self.sendMessage(' '.join([key, value]).encode('utf8'))


factory = WebSocketClientFactory('ws://127.0.0.1:9000')
factory.protocol = ClientProtocol
connectWS(factory)
reactor.run()


