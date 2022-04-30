import math
import sys
import enum

MONSTER = 0
ALLY = 1
VILLAIN = 2

MIDFIELDER = 0
DEFENDER = 1
OFFENSE = 2
GATHER_WILD_MANA = "Wildman"

WIND_CAST_RANGE = 1280

WAIT = 'WAIT'
MOVE = 'MOVE'


def angle(vx1, vy1, vx2, vy2):
	return


def distance(x1, y1, x2, y2):
	return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))


def debug_print(*args, **kwargs):
	print(*args, file=sys.stderr, flush=True, **kwargs)


def calculate_vector_between(speed, base, target):
	x0, y0 = target.position
	x, y = base.position
	d = base.distance_to(target)
	vx = speed / d * (x - x0)
	vy = speed / d * (y - y0)
	return vx, vy, x0, y0


class Mentality(enum.Enum):
	ClassDefault = -1
	Midfield = 0
	Defend = 1
	Attack = 2
	SaveBase = 3
	Wildman = 4
