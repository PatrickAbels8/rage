import sys
from time import sleep
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS

from gui import stack, num_to_let, cols, let_to_num, tk_cols
from tkinter import *
from tkinter import font as tkFont
 



class ClientProtocol(WebSocketClientProtocol):

	player_id = '0'
	played_card = None

	def clicked(self, card, window):
		# print(card)
		self.played_card.set(card)
		window.destroy()
		

	def game_tick(self, cards):
		window = Tk()
		window.title("Rage")
		window.geometry('1200x200')

		self.played_card = StringVar()

		for i, card in enumerate(cards.split()): # todo always returns last card
			helv36 = tkFont.Font(family='Helvetica', size=36, weight=tkFont.BOLD) 
			btn = Button(window, activebackground='white', fg='black', text=let_to_num[card[1]], bg=tk_cols[card[0]], font=helv36, command=lambda: self.clicked(card, window))
			btn.grid(column=i, row=0)

		window.mainloop()

	def shot_made(self):
		shot = self.played_card.get()
		# print(shot)
		self.sendMessage(shot.encode('utf8'))

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
					turn, board, cards = msg.split('\n')
					board = board.split(',')[0].split(':')[1].strip()
					cards = cards.split(':')[1].strip()

					self.game_tick(cards)
					print(self.played_card.get())
					self.sendMessage(self.played_card.get().encode('utf8'))					



factory = WebSocketClientFactory('ws://127.0.0.1:9000')
factory.protocol = ClientProtocol
connectWS(factory)
reactor.run()


