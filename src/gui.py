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
	Label(win, text='Your Cards').grid(column=0, row=0)
	for i, c in enumerate(cards.split()):
		Button(win, text=c[1], bg=get_color(c[0]), fg='white', command=partial(clicked, c)).grid(column=i+1, row=0)

	if action == 'call':
		Label(win, text='Your Prediction').grid(column=0, row=1)
		for i in range(len(cards.split())+1):
			Button(win, text=i, command=partial(clicked, i)).grid(column=i+1, row=1)

	# show trump
	Label(win, text='Current Trump').grid(column=0, row=2)
	if len(trump) > 1:
		Button(win, text=trump[1], bg=get_color(trump[0]), fg='white').grid(column=1, row=2)


	# show boards
	Label(win, text='Current Board').grid(column=0, row=3)
	if len(board) > 1:
		for i, bc in enumerate(board.split()):
			Button(win, text=bc[1], bg=get_color(bc[0]), fg='white').grid(column=i+1, row=3)

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

def onMode():
	from tkinter import Tk, Button, Entry, Label
	from functools import partial

	win = Tk()
	win.title('Rage')
	win.geometry('600x400+20+20')

	def clicked(c):
		global ret 
		ret = c
		win.destroy()

	Button(win, text='10 => 1', bg='red', fg='white', command=partial(clicked, '--')).grid(column=0, row=0)
	Button(win, text='1 => 10', bg='green', fg='white', command=partial(clicked, '++')).grid(column=1, row=0)


	win.mainloop()

	return ret

def onGo(cur_players):
	from tkinter import Tk, Button, Entry, Label
	from functools import partial

	win = Tk()
	win.title('Rage')
	win.geometry('600x400+20+20')

	def clicked(c):
		global ret 
		ret = c
		win.destroy()

	Label(win, text=str(cur_players)+' Player(s) joined! Ready to start the game?').grid(column=0, row=0)
	Button(win, text='GO', bg='red', fg='white', command=partial(clicked, 'y')).grid(column=0, row=1)
	Button(win, text='WAIT', bg='green', fg='white', command=partial(clicked, 'n')).grid(column=1, row=1)


	win.mainloop()

	return ret

def onName():
	from tkinter import Tk, Button, Entry, Label
	from functools import partial

	win = Tk()
	win.title('Rage')
	win.geometry('600x400+20+20')

	def returnbtnstring():
		global ret 
		ret = e.get()
		win.destroy()

	Label(win, text='Name', bg='white', fg='black').grid(column=0, row=0)
	e = Entry(win)
	e.grid(column=1, row=0)
	Button(win, text='JOIN', bg='black', fg='white', command=returnbtnstring).grid(column=0, row=1)


	win.mainloop()

	return ret
