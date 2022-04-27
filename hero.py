from entity import Entity
from constants import *
import random

class Hero(Entity):


    def __init__(self, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
        self.command = None

    def update(self, x, y, shield_life, is_controlled, vx, vy):
        super().update_base(x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
        self.command = None

    def act(self):
        # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
        return self.command

    def random_move(self):
        # 17630, Y=9000
        x_boundaries = [0, 17630]
        y_boundaries = [0,  9000]
        x = random.randint(*x_boundaries)
        y = random.randint(*y_boundaries)
        self.move_to(x, y)

    def move_to(self, x, y):
        self.command = f"{MOVE} {x} {y}"
