class Entity:

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        self.uid = uid
        self.x = x
        self.y = y
        self.shield_life = shield_life
        self.is_controlled = is_controlled
        self.vx = vx
        self.vy = vy

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def vector(self):
        return (self.vx, self.vy)

    def __repr__(self):
        return f"<{self.__class__.__name__}>({self.x}, {self.y})"

    def between(self, a, b):
        ax, ay = a.position
        bx, by = b.position
        x, y = self.position
        left = ax < x < bx and ay < y < by
        right = ax > x > bx and ay > y > by
        return left or right

    def update_base(self, x, y, shield_life, is_controlled, vx, vy):
        self.x = x
        self.y = y
        self.shield_life = shield_life
        self.is_controlled = is_controlled
        self.vx = vx
        self.vy = vy
