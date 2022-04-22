from entity import Entity


class Hero(Entity):

    def __init__(self, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled

    def update(self, x, y, shield_life, is_controlled, vx, vy):
        super().update_base(x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
