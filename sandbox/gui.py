def onBoard(action, board, trump, cards, stats, moves, player):

	from tkinter import Tk, Button, Entry, Label
	from functools import partial

	def get_color(c):
		return {'o':'orange', 'r':'red', 'g':'green', 'y':'yellow', 'b':'blue', 'p':'purple', 'j':'grey'}[c]

	win = Tk()
	win.title('Rage'+' ('+player+')')
	win.geometry('600x400+20+20')

	def clicked(c):
		global ret 
		ret = c

		win.destroy()

	# show cards
	for i, c in enumerate(cards.split()):
		Button(win, text=c[1], bg=get_color(c[0]), fg='white', command=partial(clicked, c)).grid(column=i, row=0)

	if action == 'call':
		for i in range(len(cards.split())+1):
			Button(win, text=i, command=partial(clicked, i)).grid(column=i, row=1)

	# show trump
	if len(trump) > 1:
		Button(win, text=trump[1], bg=get_color(trump[0]), fg='white').grid(column=0, row=2)


	# show boards
	if len(board) > 1:
		for i, bc in enumerate(board.split()):
			Button(win, text=bc[1], bg=get_color(bc[0]), fg='white').grid(column=i, row=3)

	# show stats
	for i, p in enumerate(stats.split('&')):
		Label(win, text=p.split('_')[0]).grid(row=0, column=i+20) 
		for j, r in enumerate(p.split('_')[1:]):
			Label(win, text=r).grid(row=j+1, column=i+20)

	win.mainloop()

	return ret


def onEnd(stats):

	from tkinter import Tk, Button, Entry, Label
	from functools import partial

	win = Tk()
	win.title('Rage')
	win.geometry('600x400+20+20')

	# show stats
	for i, p in enumerate(stats.split('&')):
		result = 0

		Label(win, text=p.split('_')[0]).grid(row=0, column=i) 
		for j, r in enumerate(p.split('_')[1:]):
			Label(win, text=r).grid(row=j+1, column=i)
			result += int(r.split('/')[3])

		Label(win, text=str(result)).grid(row=len(p.split('_')[1:])+1, column=i)

	win.mainloop()

