import random

bonus_plus = 'j+'
bonus_minus = 'j-'
trump_now = 'j!'
trump_later = 'jX'


def create_deck():
	return '''
		g0 g1 g2 g3 g4 g5 g6 g7 g8 g9 gA gB gC gD gE gF 
		r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 rA rB rC rD rE rF 
		o0 o1 o2 o3 o4 o5 o6 o7 o8 o9 oA oB oC oD oE oF 
		y0 y1 y2 y3 y4 y5 y6 y7 y8 y9 yA yB yC yD yE yF 
		b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 bA bB bC bD bE bF 
		p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 pA pB pC pD pE pF 
		j! j! j! j! jX jX jX jX j- j- j- j+ j+ j+ jJ jJ'''.split()

'''
:param board: 'o1 a3 g7'
:param c_id_id: index of player who drew the last card
:return: player_id_id who wins the pot
'''
def get_winner(board, trump, c_id_id):
	return random.randint(0, len(board.split())-1)