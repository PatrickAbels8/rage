import sys
from time import sleep
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS

from gui import stack, num_to_let


class ClientProtocol(WebSocketClientProtocol):

	player_id = '0'

	def makeShot(self, board):
		shot = ''
		while not shot in stack:
			let_shot = input('shot? ')
			shot = let_shot[0] + num_to_let[let_shot[1:]]
		return shot

	def onOpen(self):
		print('CONNECTED TO SERVER')

	def onMessage(self, payload, isBinary):
		if not isBinary:
			msg = payload.decode('utf8')
			if 'HELLO' in msg:
				self.player_id = msg.split()[1]
				print('Player ID: ' + self.player_id)
			else:
				if msg[0] == self.player_id:
					print(msg)
					board = msg.split(':')[1]
					shot = self.makeShot(board)
					self.sendMessage(shot.encode('utf8'))



factory = WebSocketClientFactory('ws://127.0.0.1:9000')
factory.protocol = ClientProtocol
connectWS(factory)
reactor.run()