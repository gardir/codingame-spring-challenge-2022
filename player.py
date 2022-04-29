from constants import *
from base import *
from hero import *
from monster import *

class Player:

    def __init__(self, base_x, base_y):
        self._base = Base(base_x, base_y, ALLY)
        Hero.base = self._base
        Hero.opponent_base = Base(*self._base.opponent, OPPONENT)
        Hero.player = self
        self._monsters = {}
        self.mana = 0
        self.health = 0

    @property
    def heroes(self):
        for hero in Hero.heroes.values():
            yield hero

    @property
    def enough_mana(self):
        return self.mana > 10

    def add_entity(self, uid, entity_type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        debug_string = f"Adding entity: {uid}, {entity_type}, {x}, {y}, {shield_life}, {is_controlled}, {health}, {vx}, {vy}, {near_base}, {threat_for} to "
        if entity_type == ALLY:
            debug_string += "ALLY"
            Hero.update_hero(uid, x, y, shield_life, is_controlled, vx, vy)
        elif entity_type == MONSTER:
            debug_string += "MONSTER"
            self.update_monster(uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        debug_print(debug_string)

    def update(self, health, mana):
        self.health = health
        self.mana = mana

    def update_monster(self, uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        if uid in self._monsters:
            self._monsters[uid].update(x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        else:
            self._monsters[uid] = Monster(uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)

    def deal_with_threatening_bugs(self, threatening_bugs):
        for hero in self.heroes:
            hero.idle(threatening_bugs)

    def mana_distance_limit(self):
        mana_limits = {
            250: 12000,
            200: 10000,
            150: 8000,
            100: 6000,
            50: 5000,
            0: 0,
        }
        for mana, distance_limit in mana_limits.values():
            if self.mana > mana:
                return distance_limit

    def watch_perimeter(self):
        # Send the three heroes out to guard perimeter
        for hero in self.heroes:
            hero.idle(self._monsters.values())

    def evaluate_orders(self):
        # Main order loop, check for threatening bugs, and squash them!
        threatening_bugs = []
        for bug in self._monsters.values():
            if bug.is_threat_to(self._base):
                threatening_bugs.append(bug)
        debug_print(f"Threatening bugs: {threatening_bugs}")
        attacker = Hero.offense
        attacker.idle(self._monsters.values())
        defender = Hero.defender
        midfielder = Hero.midfielder
        if threatening_bugs:
            defender.idle(threatening_bugs)
            midfielder.idle(threatening_bugs)
        else:
            defender.idle(self._monsters.values())
            midfielder.idle(self._monsters.values())

    def reset(self):
        self._monsters = {}
