from entity import Entity
from constants import *
from monster import *
import random
import queue


class Hero(Entity):
    heroes = {}
    villains = {}
    base = None
    opponent_base = None
    player = None
    offense = None
    defender = None
    midfielder = None

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)
        self._mentality = Mentality.ClassDefault
        self._command = None
        self.command_target = None

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

    @staticmethod
    def update_villain(uid, x, y, shield_life, is_controlled, vx, vy):
        if uid in Hero.villains:
            Hero.villains[uid].update(x, y, shield_life, is_controlled, vx, vy)
        else:
            Hero.villains[uid] = Villain(uid, x, y, shield_life, is_controlled, vx, vy)

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        if self._command is None or self._command == WAIT:
            class_name = self.__class__.__name__
            mentality_name = self.mentality.name if self.mentality is not Mentality.ClassDefault else class_name
            self._command = f"{value} {class_name} ({mentality_name})"
        else:
            debug_print(f"Tried to give command '{value}' to {self.uid} (already have {self._command})")

    @property
    def command_target_is_bug(self):
        has_target = self.command_target is not None
        is_bug = isinstance(self.command_target, Monster)
        return has_target and is_bug

    @property
    def mentality(self):
        return self._mentality

    @mentality.setter
    def mentality(self, value):
        if not isinstance(value, Mentality):
            raise ValueError(f"Could not assign '{value}' as Hero Mentality")
        self._mentality = value

    def act(self):
        # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
        command = self._command
        self._command = None
        self.command_target = None
        return command

    def cast_spell(self, spell_command):
        if not self.player.enough_mana:
            return False
        self.player.mana -= 10
        self.command = f"SPELL {spell_command}"
        return True

    def cast_mindcontrol_on_towards(self, victim, target):
        uid = victim.uid
        x, y = target.position
        spell_cast = self.cast_spell(f"CONTROL {uid} {x} {y}")
        if spell_cast:
            self.command_target = victim
        return spell_cast

    def cast_shield_on(self, target):
        spell_cast = self.cast_spell(f"SHIELD {target.uid}")
        if spell_cast:
            self.command_target = target
        return spell_cast

    def cast_windspell_at(self, target):
        x, y = target.position
        spell_cast = self.cast_spell(f"WIND {x} {y}")
        if spell_cast:
            self.command_target = target
        return spell_cast

    def move_to_base(self):
        self.command = f"MOVE {self.base.x} {self.base.y}"

    def move_to_bug_direction(self, bug):
        x = bug.x + bug.vx
        y = bug.y + bug.vy
        self.move_to(x, y)

    def switch_tactic(self, to):
        self.mentality = to

    def update(self, x, y, shield_life, is_controlled, vx, vy):
        super().update_base(x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled
        self._command = None


    def evaluate_command(self, monsters):
        self.random_move()

    def random_move(self):
        # 17630, Y=9000
        x_boundaries = [0, 17630]
        y_boundaries = [0,  9000]
        x = random.randint(*x_boundaries)
        y = random.randint(*y_boundaries)
        self.move_to(x, y)

    def move_to(self, x, y):
        self.command = f"{MOVE} {x} {y}"

    def move_between_homebase_and(self, target, speed=650):
        vx, vy, x0, y0 = calculate_vector_between(speed, self.base, target)
        nx = int(x0 + vx)
        ny = int(y0 + vy)
        self.command_target = target
        self.move_to(nx, ny)

    def move_towards_homebase_behind(self, target):
        speed = 350
        vx, vy, x0, y0 = calculate_vector_between(speed, self.base, target)
        nx = int(x0 - vx)
        ny = int(y0 - vy)
        self.command_target = target
        self.move_to(nx, ny)

    def villains_in_base(self):
        for villain in Hero.villains.values():
            distance_to_home = self.base.distance_to(villain)
            if distance_to_home < 5000:
                return True
        return False



class Defender(Hero):

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)
        self.is_controlled = is_controlled

    @property
    def mentality(self):
        if self.villains_in_base():
            return Mentality.SaveBase
        return super().mentality

    @mentality.setter
    def mentality(self, value):
        if not isinstance(value, Mentality):
            raise ValueError(f"Could not assign '{value}' as Hero Mentality")
        self._mentality = value

    def deal_with_threats(self, prio_threats):
        bug_distance_to_base, closest = prio_threats.get()
        pushing_away_from_base = self.between(closest, self.base)
        distance_to_bug = self.distance_to(closest)
        midfielder = Hero.midfielder
        between_midfielder = closest.between(self, midfielder)
        midfielder_in_position = between_midfielder and self.distance_to(midfielder) < WIND_CAST_RANGE + 2200 - distance_to_bug - 600
        within_casting_distance = distance_to_bug < 1200
        base_distance = self.base.distance_to(self)
        too_close_to_base = bug_distance_to_base < 2500 if self.mentality == Mentality.SaveBase else bug_distance_to_base < 1500
        close_enough_to_base = bug_distance_to_base < 3500
        allowed_to_push = within_casting_distance and \
                          pushing_away_from_base and \
                          ((close_enough_to_base and midfielder_in_position) or too_close_to_base)
        spell_target = closest if too_close_to_base else midfielder
        if not (allowed_to_push and self.cast_windspell_at(spell_target)):
            self.move_between_homebase_and(closest)

    def evaluate_command(self, monsters):
        if self.mentality == Mentality.SaveBase and self.push_villains_away():
            return
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

    def push_villains_away(self):
        closest_distance = None
        closest = None
        for villain in self.villains.values():
            d = self.base.distance_to(villain)
            if closest is None or d < closest_distance:
                closest = villain
                closest_distance = d
        within_distance = self.distance_to(closest) <= WIND_CAST_RANGE
        casting_away_from_base = self.between(self.base, closest)
        return within_distance and casting_away_from_base and self.cast_windspell_at(closest)

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

    @property
    def mentality(self):
        if self.villains_in_base():
            return Mentality.SaveBase
        return super().mentality

    @mentality.setter
    def mentality(self, value):
        if not isinstance(value, Mentality):
            raise ValueError(f"Could not assign '{value}' as Hero Mentality")
        self._mentality = value

    def evaluate_command(self, monsters):
        if self.mentality == Mentality.Defend and self.defender.command_target_is_bug:
            self.move_towards_homebase_behind(self.defender.command_target)
        prioQ = queue.PriorityQueue()
        for bug in monsters:
            distance_origin = self.base if self.mentality is Defender else self
            prioQ.put((distance(*distance_origin.position, *bug.position), bug))
        # Move outside perimeter
        if prioQ.empty():
            self.watch_perimeter()
        else:
            d, target = prioQ.get()
            self.move_towards_homebase_behind(target)

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
        self.mind_controlled_target = None
        self._mentality = Mentality.Wildman

    @property
    def max_distance(self):
        if self._mentality is GATHER_WILD_MANA:
            return 12500
        if self._mentality is Attacker:
            return 7200
        return 8750

    def deal_with_targets(self, targets):
        closest_distance, closest = targets.get()
        big_close_to_opponent_base = None
        mana_limit_distance = self.player.mana_distance_limit
        while not targets.empty():
            d, target = targets.get()
            distance_to_opponent = self.opponent_base.distance_to(target)
            if d < 2200 and distance_to_opponent < mana_limit_distance and self.player.enough_mana and target.health > 8:
                if big_close_to_opponent_base is None:
                    big_close_to_opponent_base = target
                elif not isinstance(big_close_to_opponent_base, list):
                    big_close_to_opponent_base = [big_close_to_opponent_base, target]
                else:
                    big_close_to_opponent_base.append(target)
            if closest.is_threat_to(self.opponent_base):
                closest = target
        if big_close_to_opponent_base:
            if isinstance(big_close_to_opponent_base, list):
                counter = 0
                for target in big_close_to_opponent_base:
                    if target.between(self, self.opponent_base):
                        counter += 1
                if counter > 1:
                    self.cast_windspell_at(self.opponent_base)
                elif big_close_to_opponent_base[0].is_controllable:
                    self.mind_controlled_target = big_close_to_opponent_base[0]
                    self.cast_mindcontrol_on_towards(self.mind_controlled_target, self.opponent_base)
            elif big_close_to_opponent_base.is_controllable:
                self.mind_controlled_target = big_close_to_opponent_base
                self.cast_mindcontrol_on_towards(self.mind_controlled_target, self.opponent_base)
        if not self.command:
            distance_to_opponent = self.opponent_base.distance_to(self)
            self.move_between_homebase_and(closest, speed=2200 if distance_to_opponent < 5500 else 600)

    def evaluate_command(self, monsters):
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
        if self.cast_shield_on(self.mind_controlled_target):
            self.mind_controlled_target = None
            return True
        return False

    def watch_perimeter(self):
        # Move outside perimeter
        distance_to_base = self.opponent_base.distance_to(self)
        if distance_to_base < 5800:
            if self.opponent_base.x == 0:
                self.move_to(5000, 2200)
            else:
                self.move_to(12630, 7000)
        elif self.max_distance < distance_to_base:
            self.move_to(*self.opponent_base.position)
        else:
            self.random_move()


class Villain(Hero):

    def __init__(self, uid, x, y, shield_life, is_controlled, vx, vy):
        super().__init__(uid, x, y, shield_life, is_controlled, vx, vy)