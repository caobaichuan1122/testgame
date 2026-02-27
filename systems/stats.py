# ============================================================
#  RPG stat system: level, XP, and attribute points
# ============================================================
import math


class Stats:
    """RPG stats: STR/DEX/INT/DEF + level/XP."""

    def __init__(self, hp=50, mp=30, str_=3, dex=3, int_=3, def_=2, level=1):
        self.max_hp = hp
        self.hp = hp
        self.max_mp = mp
        self.mp = mp

        self.str = str_      # Strength -> melee bonus
        self.dex = dex       # Dexterity -> ranged bonus
        self.int = int_      # Intelligence -> magic bonus
        self.def_ = def_     # Defense -> damage reduction

        self.level = level
        self.xp = 0
        self.free_points = 0

    def xp_needed(self):
        """XP required to reach the next level."""
        return int(100 * (1.5 ** (self.level - 1)))

    def add_xp(self, amount):
        """Add XP and auto-level up as needed."""
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_needed():
            self.xp -= self.xp_needed()
            self.level += 1
            self.free_points += 3
            self.max_hp += 10
            self.max_mp += 5
            self.hp = self.max_hp
            self.mp = self.max_mp
            leveled = True
        return leveled

    def assign_point(self, stat_name):
        """Assign a free stat point."""
        if self.free_points <= 0:
            return False
        if stat_name == "str":
            self.str += 1
        elif stat_name == "dex":
            self.dex += 1
        elif stat_name == "int":
            self.int += 1
        elif stat_name == "def":
            self.def_ += 1
        else:
            return False
        self.free_points -= 1
        return True

    def take_damage(self, raw_damage):
        """Take damage; return actual damage dealt."""
        actual = max(1, raw_damage - int(self.def_ * 0.8))
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def restore_mp(self, amount):
        self.mp = min(self.max_mp, self.mp + amount)

    def use_mp(self, cost):
        if self.mp >= cost:
            self.mp -= cost
            return True
        return False

    @property
    def alive(self):
        return self.hp > 0
