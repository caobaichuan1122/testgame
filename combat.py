# ============================================================
#  Combat system: damage formulas, crits, arc detection
# ============================================================
import math
import random
from settings import (
    COMBAT_MELEE, COMBAT_RANGED, COMBAT_MAGIC,
    MELEE_RANGE, MELEE_ARC, MELEE_COOLDOWN, MELEE_BASE_DMG,
    RANGED_RANGE, RANGED_COOLDOWN, RANGED_BASE_DMG,
    MAGIC_RANGE, MAGIC_COOLDOWN, MAGIC_BASE_DMG, MAGIC_COST,
)
from utils import distance, angle_between, angle_diff


COMBAT_NAMES = {
    COMBAT_MELEE: "Sword",
    COMBAT_RANGED: "Bow",
    COMBAT_MAGIC: "Magic",
}

COMBAT_COLORS = {
    COMBAT_MELEE: (200, 200, 200),
    COMBAT_RANGED: (200, 180, 100),
    COMBAT_MAGIC: (130, 80, 255),
}


def calc_damage(base_dmg, stat_bonus, weapon_bonus, target_def):
    """Damage formula: actual = max(1, base + stat_bonus + weapon_bonus - def*0.8)."""
    raw = base_dmg + stat_bonus + weapon_bonus
    reduced = max(1, raw - int(target_def * 0.8))
    return reduced


def check_crit(dex):
    """Crit check: base 5% + DEX*1%."""
    crit_chance = 0.05 + dex * 0.01
    return random.random() < crit_chance


def get_combat_params(mode):
    """Get base params for a combat mode."""
    if mode == COMBAT_MELEE:
        return {
            "range": MELEE_RANGE,
            "cooldown": MELEE_COOLDOWN,
            "base_dmg": MELEE_BASE_DMG,
            "stat": "str",
        }
    elif mode == COMBAT_RANGED:
        return {
            "range": RANGED_RANGE,
            "cooldown": RANGED_COOLDOWN,
            "base_dmg": RANGED_BASE_DMG,
            "stat": "dex",
        }
    else:
        return {
            "range": MAGIC_RANGE,
            "cooldown": MAGIC_COOLDOWN,
            "base_dmg": MAGIC_BASE_DMG,
            "stat": "int",
            "mp_cost": MAGIC_COST,
        }


def melee_arc_hit(attacker_wx, attacker_wy, facing_angle, target_wx, target_wy):
    """Check if target is within melee arc range."""
    dist = distance(attacker_wx, attacker_wy, target_wx, target_wy)
    if dist > MELEE_RANGE:
        return False
    target_angle = angle_between(attacker_wx, attacker_wy, target_wx, target_wy)
    diff = abs(angle_diff(facing_angle, target_angle))
    return diff <= MELEE_ARC / 2


def perform_melee_attack(player, entities):
    """Execute melee attack; return list of (enemy, dmg, is_crit)."""
    params = get_combat_params(COMBAT_MELEE)
    hit_enemies = []

    weapon_bonus = 0
    equipped = player.inventory.get_equipped_weapon()
    if equipped:
        weapon_bonus = equipped.get("bonus", 0)

    for enemy in entities.get_enemies_in_range(player.wx, player.wy, MELEE_RANGE):
        if melee_arc_hit(player.wx, player.wy, player.facing_angle,
                         enemy.wx, enemy.wy):
            stat_bonus = player.stats.str * 2
            dmg = calc_damage(params["base_dmg"], stat_bonus, weapon_bonus,
                              enemy.stats.def_)
            is_crit = check_crit(player.stats.dex)
            if is_crit:
                dmg = int(dmg * 1.5)
            enemy.stats.take_damage(dmg)
            hit_enemies.append((enemy, dmg, is_crit))
    return hit_enemies


def perform_ranged_attack(player, entities):
    """Execute ranged attack: spawn arrow projectile."""
    from projectile import Projectile
    from settings import ARROW_SPEED, COLOR_ARROW

    weapon_bonus = 0
    equipped = player.inventory.get_equipped_weapon()
    if equipped:
        weapon_bonus = equipped.get("bonus", 0)

    stat_bonus = player.stats.dex * 2
    base_dmg = RANGED_BASE_DMG + stat_bonus + weapon_bonus

    proj = Projectile(
        player.wx, player.wy,
        player.facing_angle,
        speed=ARROW_SPEED,
        damage=base_dmg,
        max_range=RANGED_RANGE,
        color=COLOR_ARROW,
        owner="player",
    )
    entities.add_projectile(proj)
    return proj


def perform_magic_attack(player, entities):
    """Execute magic attack: consume MP, spawn magic bolt."""
    if not player.stats.use_mp(MAGIC_COST):
        return None

    from projectile import Projectile
    from settings import MAGIC_SPEED, COLOR_MAGIC_BOLT

    weapon_bonus = 0
    equipped = player.inventory.get_equipped_weapon()
    if equipped:
        weapon_bonus = equipped.get("bonus", 0)

    stat_bonus = player.stats.int * 2
    base_dmg = MAGIC_BASE_DMG + stat_bonus + weapon_bonus

    proj = Projectile(
        player.wx, player.wy,
        player.facing_angle,
        speed=MAGIC_SPEED,
        damage=base_dmg,
        max_range=MAGIC_RANGE,
        color=COLOR_MAGIC_BOLT,
        owner="player",
    )
    entities.add_projectile(proj)
    return proj
