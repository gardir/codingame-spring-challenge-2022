from constants import *
from base import *
from hero import *
from monster import *

class Player:

    def __init__(self, base_x, base_y):
        self._base = Base(base_x, base_y, ALLY)
        Hero.base = self._base
        Hero.opponent_base = Base(*self._base.opponent, VILLAIN)
        Hero.player = self
        self._monsters = {}
        self.mana = 0
        self.health = 0
        self.rounds = 0

    @property
    def heroes(self):
        for hero in Hero.heroes.values():
            yield hero

    @property
    def enough_mana(self):
        return self.mana > 10

    @property
    def mana_distance_limit(self):
        mana_limits = {
            400: 25000,
            350: 20000,
            300: 18000,
            250: 16000,
            200: 13500,
            150: 9500,
            100: 7500,
            50: 5000,
            0: 0,
        }
        for mana, distance_limit in mana_limits.items():
            if self.mana >= mana:
                return distance_limit

    def add_entity(self, uid, entity_type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        debug_string = f"Adding entity: {uid}, {entity_type}, {x}, {y}, {shield_life}, {is_controlled}, {health}, {vx}, {vy}, {near_base}, {threat_for} to "
        if entity_type == ALLY:
            debug_string += "ALLY"
            Hero.update_hero(uid, x, y, shield_life, is_controlled, vx, vy)
        elif entity_type == MONSTER:
            debug_string += "MONSTER"
            self.update_monster(uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        elif entity_type == VILLAIN:
            debug_string += "VILLAIN"
            Hero.update_villain(uid, x, y, shield_life, is_controlled, vx, vy)
        # debug_print(debug_string)

    def update(self, health, mana):
        self.health = health
        self.mana = mana

    def update_monster(self, uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        if uid in self._monsters:
            self._monsters[uid].update(x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        else:
            self._monsters[uid] = Monster(uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)

    def evaluate_orders(self):
        defender = Hero.defender
        midfielder = Hero.midfielder
        attacker = Hero.offense
        if self.rounds == 110:  # Switch tactic
            attacker.switch_tactic(Mentality.Attack)
            midfielder.switch_tactic(Mentality.Defend)
            defender.switch_tactic(Mentality.SaveBase)
        # Main order loop, check for threatening bugs, and squash them!
        threatening_bugs = []
        for bug in self._monsters.values():
            if bug.is_threat_to(self._base):
                threatening_bugs.append(bug)
        debug_print(f"Threatening bugs: {threatening_bugs}")
        if threatening_bugs:
            defender.evaluate_command(threatening_bugs)
            midfielder.evaluate_command(self._monsters.values() if not Hero.villains_in_base and self.rounds < 150 else threatening_bugs)
        else:
            defender.evaluate_command(self._monsters.values())
            midfielder.evaluate_command(self._monsters.values())
        attacker.evaluate_command(self._monsters.values())

    def reset(self):
        self._monsters = {}
        self.rounds += 1
