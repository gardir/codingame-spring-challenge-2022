class Entity:

    def __init__(self, x, y, shield_life, is_controlled, vx, vy):
        self.x = x
        self.y = y
        self.shield_life = shield_life
        self.is_controlled = is_controlled
        self.vx = vx
        self.vy = vy

    def update_base(self, x, y, shield_life, is_controlled, vx, vy):
        self.x = x
        self.y = y
        self.shield_life = shield_life
        self.is_controlled = is_controlled
        self.vx = vx
        self.vy = vy
