from base import Base
from hero import Hero
from monster import Monster
from constants import *

class Player:

    def __init__(self, base_x, base_y):
        self._base = Base(base_x, base_y)
        self._heroes = {}
        self._monsters = {}

    @property
    def heroes(self):
        for hero in self._heroes.values():
            yield hero

    def add_entity(self, uid, entity_type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        debug_string = f"Adding entity: {uid}, {entity_type}, {x}, {y}, {shield_life}, {is_controlled}, {health}, {vx}, {vy}, {near_base}, {threat_for} to "
        if entity_type == ALLY:
            debug_string += "ALLY"
            self.update_hero(uid, x, y, shield_life, is_controlled, vx, vy)
        elif entity_type == MONSTER:
            debug_string += "MONSTER"
            self.update_monster(uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        debug_print(debug_string)

    def update_hero(self, uid, x, y, shield_life, is_controlled, vx, vy):
        if uid in self._heroes:
            self._heroes[uid].update(x, y, shield_life, is_controlled, vx, vy)
        else:
            self._heroes[uid] = Hero(x, y, shield_life, is_controlled, vx, vy)

    def update_monster(self, uid, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for):
        if uid in self._monsters:
            self._monsters[uid].update(x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)
        else:
            self._monsters[uid] = Monster(x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for)

    def give_all_heroes(self, command):
        for hero in self._heroes.values():
            hero.command = command

    def deal_with_two_threatening_bugs(self, threatening_bugs):
        debug_print(f"deal_with_two_threatening_bugs")
        # send the two closest to the closest bug
        closest_distance = None
        closest = None
        for bug in threatening_bugs:
            bug_distance = self._base.distance_to(bug)
            if closest is None or bug_distance < closest_distance:
                closest_distance = bug_distance
                closest = bug

        furthest = None
        furthest_distance = None
        for hero in self._heroes.values():
            hero_distance = distance(*hero.position, *bug.position)
            if furthest is None or furthest_distance > hero_distance:
                furthest = hero
                furthest_distance = hero_distance
        for hero in self._heroes.values():
            if hero is not furthest:
                hero.move_to(*closest.position)
            else:
                for bug in threatening_bugs:
                    if bug is not closest:
                        hero.move_to(*bug.position)

    def deal_with_three_plus_threatening_bugs(self, threatening_bugs):
        debug_print(f"deal_with_three_plus_threatening_bugs: {len(threatening_bugs)} : {threatening_bugs}")
        # send each to their closest bug
        closest_to_base = None
        closest_distance_to_base = None
        for bug in threatening_bugs:
            distance_to_base = self._base.distance_to(bug)
            if closest_to_base is None or distance_to_base < closest_distance_to_base:
                closest_to_base = bug
                closest_distance_to_base = distance_to_base
        x,y = closest_to_base.position
        self.give_all_heroes(f"MOVE {x} {y}")
            # for hero in self.heroes:
            #     hero_distance = distance(*hero.position, *bug.position)
            #     debug_print(f"hero({hero.position}) has distance '{hero_distance}' to bug({bug.position})")
            #     if closest is None or closest_distance < hero_distance:
            #         closest = hero
            #         closest_distance = hero_distance
            # closest.move_to(*bug.position)

    def deal_with_threatening_bugs(self, threatening_bugs):
        if len(threatening_bugs) == 1:
            # Send all to one bug
            x, y = threatening_bugs[0].position
            command = f"{MOVE} {x} {y}"
            self.give_all_heroes(command)
        elif len(threatening_bugs) == 2:
            self.deal_with_two_threatening_bugs(threatening_bugs)
        else:
            self.deal_with_three_plus_threatening_bugs(threatening_bugs)

    def watch_perimeter(self):
        # Send the three heroes out to guard perimeter
        for hero in self._heroes.values():
            hero.random_move()

    def evaluate_orders(self):
        # FALLBACK IN CASE SOME EDGE CASES HAPPEN
        self.give_all_heroes(WAIT)
        # Main order loop, check for threatening bugs, and squash them!
        threatening_bugs = []
        for bug in self._monsters.values():
            if bug.is_threat_to(self._base):
                threatening_bugs.append(bug)
        debug_print(f"Threatening bugs: {threatening_bugs}")
        if threatening_bugs:
            self.deal_with_threatening_bugs(threatening_bugs)
        else:
            self.watch_perimeter()

    def reset(self):
        self._monsters = {}
