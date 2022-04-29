from constants import *

class Base:
    UPPER = (0, 0)
    LOWER = (17630, 9000)

    def __init__(self, base_x, base_y, allegiance):
        self.x = base_x
        self.y = base_y
        self.allegiance = allegiance

    @property
    def home(self):
        return self.UPPER if self.x == 0 else self.LOWER

    @property
    def opponent(self):
        return self.LOWER if self.x == 0 else self.UPPER

    @property
    def position(self):
        return self.x, self.y

    def distance_to(self, entity):
        return distance(self.x, self.y, *entity.position)

    def angle_to(self, entity):
        return angle(self.x, self.y, *entity.vector)
