from entity import Entity
from constants import *


class Monster(Entity):

    def __init__(self, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        super().__init__(x, y, shield_life, is_controlled, vx, vy)
        self.health = health
        self.near_base = near_base
        self.threat_for = threat_for

    def is_threat_to(self, base):
        return self.threat_for == ALLY and self.health > 0

    def update(self, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        super().update_base(x, y, shield_life, is_controlled, vx, vy)
        self.health = health
        self.near_base = near_base
        self.threat_for = threat_for
