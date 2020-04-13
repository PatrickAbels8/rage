import pygame
from twisted.internet import reactor
pygame.font.init()

win = None
HEIGHT = 600
WIDTH = 1200
FONT = pygame.font.SysFont("arial", 50, bold=True)

cols = {'r': (255, 0, 0), 'g': (0, 255, 0), 'o': (255, 140, 0), 'y': (255, 255, 0), 'b': (0, 0, 255), 'p': (255, 0, 255), 'j': (105, 105, 105)}
tk_cols = {'r': 'red', 'g': 'green3', 'o': 'dark orange', 'y': 'yellow', 'b': 'blue', 'p': 'purple', 'j': 'gray50'}
let_to_num = {' ': ' ', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', 'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15'}
num_to_let = {' ': ' ', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': 'A', '11': 'B', '12': 'C', '13': 'D', '14': 'E', '15': 'F'}
stack = 'g0 g1 g2 g3 g4 g5 g6 g7 g8 g9 gA gB gC gD gE gF r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 rA rB rC rD rE rF o0 o1 o2 o3 o4 o5 o6 o7 o8 o9 oA oB oC oD oE oF y0 y1 y2 y3 y4 y5 y6 y7 y8 y9 yA yB yC yD yE yF b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 bA bB bC bD bE p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 pA pB pC pD pE pF'.split()
cur_stack = []


def init():
	global win, cols

	pygame.display.set_caption('Rage')
	win = pygame.display.set_mode((WIDTH, HEIGHT))
	win.fill((255, 255, 255))
	draw('j ')


def draw(card):
	global win, cols, let_to_num, FONT

	pygame.draw.rect(win, cols[card[0]], pygame.Rect(10, 10, 60, 120))
	win.blit(FONT.render(let_to_num[card[1]], 5, (255, 255, 255)), (15, 15))

	pygame.display.update()


def game_tick(shots):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			reactor.stop()

	global cur_stack
	if len(shots) > len(cur_stack):
		cur_stack.append(shots[-1])
		draw(cur_stack[-1])

	return True
