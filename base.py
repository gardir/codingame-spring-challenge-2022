from constants import *

class Base:

    def __init__(self, base_x, base_y):
        self._x = base_x
        self._y = base_y

    def distance_to(self, entity):
        return distance(self._x, self._y, *entity.position)
