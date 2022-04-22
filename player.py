from base import Base
from hero import Hero
from monster import Monster
from constants import *

class Player:

    def __init__(self, base_x, base_y):
        self._base = Base(base_x, base_y)
        self._heroes = {}
        self._monsters = {}

    def add_entity(self, uid, entity_type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        if entity_type == ALLY:
            self.update_hero(uid, x, y, shield_life, is_controlled, vx, vy)
        elif entity_type == MONSTER:
            self.update_monster(uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)

    def update_hero(self, uid, x, y, shield_life, is_controlled, vx, vy):
        if uid in self._heroes:
            self._heroes.update(x, y, shield_life, is_controlled, vx, vy)
        else:
            self._heroes = Hero(x, y, shield_life, is_controlled, vx, vy)

    def update_monster(self, uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        if uid in self._monsters:
            self._monsters.update(x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        else:
            self._monsters = Monster(x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)

