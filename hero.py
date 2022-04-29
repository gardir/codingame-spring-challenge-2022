from entity import Entity
from constants import *
import random
import queue

class Hero(Entity):
    heroes = {}
    base = None
    opponent_base = None
    player = None
    offense = None
    defender = None
    midfielder = None

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
        self._command = None

    @staticmethod
    def update_hero(uid, x, y, shield_life, is_controlled, vx, vy):
        if uid in Hero.heroes:
            Hero.heroes[uid].update(x, y, shield_life, is_controlled, vx, vy)
        else:
            hero_type = uid % 3
            if hero_type == DEFENDER:
                Hero.heroes[uid] = Defender(uid, x, y, shield_life, is_controlled, vx, vy)
                Hero.defender = Hero.heroes[uid]
            elif hero_type == MIDFIELDER:
                Hero.heroes[uid] = Midfielder(uid, x, y, shield_life, is_controlled, vx, vy)
                Hero.midfielder = Hero.heroes[uid]
            elif hero_type == OFFENSE:
                Hero.heroes[uid] = Attacker(uid, x, y, shield_life, is_controlled, vx, vy)
                Hero.offense = Hero.heroes[uid]

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        if self._command is None or self._command == WAIT:
            self._command = value
        else:
            debug_print(f"Tried to give command '{value}' to {self.uid} (already have {self._command})")

    def cast_spell(self, spell_command):
        if not self.player.enough_mana:
            return False
        self.player.mana -= 10
        self.command = f"SPELL {spell_command}"
        return True

    def move_to_base(self):
        self.command = f"MOVE {self.base.x} {self.base.y}"

    def move_to_bug_direction(self, bug):
        x = bug.x + bug.vx
        y = bug.y + bug.vy
        self.move_to(x, y)

    def update(self, x, y, shield_life, is_controlled, vx, vy):
        super().update_base(x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
        self._command = None

    def act(self):
        # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
        command = self._command
        self._command = None
        return command

    def idle(self, monsters):
        self.random_move()

    def random_move(self):
        # 17630, Y=9000
        x_boundaries = [0, 17630]
        y_boundaries = [0,  9000]
        x = random.randint(*x_boundaries)
        y = random.randint(*y_boundaries)
        self.move_to(x, y)

    def move_to(self, x, y):
        self._command = f"{MOVE} {x} {y}"

    def move_towards_base_and(self, target):
        speed = 650
        x0, y0 = target.position
        x, y = self.base.position
        d = self.base.distance_to(target)
        vx = speed / d * (x - x0)
        vy = speed / d * (y - y0)
        nx = int(x0 + vx)
        ny = int(y0 + vy)
        self.move_to(nx, ny)

    def move_towards_base_behind(self, target):
        speed = 350
        x0, y0 = target.position
        x, y = self.base.position
        d = self.base.distance_to(target)
        vx = speed / d * (x - x0)
        vy = speed / d * (y - y0)
        nx = int(x0 - vx)
        ny = int(y0 - vy)
        self.move_to(nx, ny)



class Defender(Hero):

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled

    def deal_with_threats(self, prio_threats):
        distance, closest = prio_threats.get()
        midfielder = Hero.midfielder
        between_midfielder = closest.between(self, midfielder)
        pushing_away_from_base = self.between(closest, self.base)
        within_distance = distance < 1200
        base_distance = self.base.distance_to(self)
        too_close_to_base = base_distance < 800
        close_enough_to_base = base_distance < 5000
        allowed_to_push = within_distance and pushing_away_from_base and ((close_enough_to_base and between_midfielder) or too_close_to_base)
        if not (allowed_to_push and self.cast_spell(f"WIND {midfielder.x} {midfielder.y}")):
            self.move_towards_base_and(closest)

    def idle(self, monsters):
        near_base = False
        prioQ = queue.PriorityQueue()
        for bug in monsters:
            if bug.near_base:
                if not near_base:
                    prioQ = queue.PriorityQueue()
                    near_base = True
            distance_to_base = self.base.distance_to(bug)
            prioQ.put((distance_to_base, bug))
        if prioQ.empty():
            self.watch_perimeter()
        else:
            self.deal_with_threats(prioQ)

    def watch_perimeter(self):
        # Move outside perimeter
        distance_to_base = self.base.distance_to(self)
        if distance_to_base < 5000:
            if self.base.x == 0:
                self.move_to(5000, 2200)
            else:
                self.move_to(12630, 7000)
        elif 7500 < distance_to_base:
            self.move_to_base()
        else:
            self.random_move()


class Midfielder(Hero):

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled

    def idle(self, monsters):
        near_base = False
        prioQ = queue.PriorityQueue()
        for bug in monsters:
            prioQ.put((distance(*self.position, *bug.position), bug))
        # Move outside perimeter
        if prioQ.empty():
            self.watch_perimeter()
        else:
            d, target = prioQ.get()
            self.move_towards_base_behind(target)

    def watch_perimeter(self):
        # Move outside perimeter
        distance_to_base = self.base.distance_to(self)
        if distance_to_base < 7500:
            self.move_to(8815, 4500)
        elif 11500 < distance_to_base:
            self.command = f"MOVE {self.base.x} {self.base.y}"
        else:
            self.random_move()


class Attacker(Hero):

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
        self.mind_controlled_target = None

    def deal_with_targets(self, targets):
        closest_distance, closest = targets.get()
        biggest_close_to_opponent_base = None
        while not targets.empty():
            d, target = targets.get()
            distance_to_base = self.opponent_base.distance_to(target)
            if d < 2200 and distance_to_base < 5000 and self.player.enough_mana and target.health > 10:
                if biggest_close_to_opponent_base is None:
                    biggest_close_to_opponent_base = target
                else:
                    biggest_close_to_opponent_base = [biggest_close_to_opponent_base, target]
            if closest.is_threat_to(self.opponent_base):
                closest = target
        if biggest_close_to_opponent_base:
            x, y = self.opponent_base.position
            if isinstance(biggest_close_to_opponent_base, list):
                counter = 0
                for target in biggest_close_to_opponent_base:
                    if target.between(self, self.opponent_base):
                        counter += 1
                if counter > 1:
                    self.cast_spell(f"WIND {x} {y}")
                elif biggest_close_to_opponent_base[0].is_controllable:
                    self.mind_controlled_target = biggest_close_to_opponent_base[0]
                    self.cast_spell(f"CONTROL {self.mind_controlled_target.uid} {x} {y}")
            elif biggest_close_to_opponent_base.is_controllable:
                self.mind_controlled_target = biggest_close_to_opponent_base
                self.cast_spell(f"CONTROL {self.mind_controlled_target.uid} {x} {y}")
        if not self.command:
            self.move_towards_base_and(closest)

    def idle(self, monsters):
        if self.mind_controlled_target and self.shield_mind_controlled_target():
            return
        prioQ = queue.PriorityQueue()
        for bug in monsters:
            d = distance(*self.position, *bug.position)
            distance_to_base = self.opponent_base.distance_to(bug)
            if distance_to_base < 8500:
                prioQ.put((d, bug))
        # Move outside perimeter
        if prioQ.empty():
            self.watch_perimeter()
        else:
            self.deal_with_targets(prioQ)

    def shield_mind_controlled_target(self):
        if self.cast_spell(f"SHIELD {self.mind_controlled_target.uid}"):
            self.mind_controlled_target = None
            return True
        return False

    def watch_perimeter(self):
        # Move outside perimeter
        distance_to_base = self.opponent_base.distance_to(self)
        if distance_to_base < 5000:
            if self.opponent_base.x == 0:
                self.move_to(5000, 2200)
            else:
                self.move_to(12630, 7000)
        elif 7500 < distance_to_base:
            self.move_to(*self.opponent_base.position)
        else:
            self.random_move()
