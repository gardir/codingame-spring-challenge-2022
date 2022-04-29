import math
import sys
MONSTER = 0
ALLY = 1
OPPONENT = 2

MIDFIELDER = 0
DEFENDER = 1
OFFENSE = 2

WAIT = 'WAIT'
MOVE = 'MOVE'


def angle(vx1, vy1, vx2, vy2):
	return


def distance(x1, y1, x2, y2):
	return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def debug_print(*args, **kwargs):
	print(*args, file=sys.stderr, flush=True, **kwargs)
