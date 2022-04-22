from entity import Entity


class Monster(Entity):

    def __init__(self, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        super().__init__(x, y, shield_life, is_controlled, vx, vy)
        self.health = health
        self.near_base = near_base
        self.threat_for = threat_for

    def update(self, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        super().update_base(x, y, shield_life, is_controlled, vx, vy)
        self.health = health
        self.near_base = near_base
        self.threat_for = threat_for
