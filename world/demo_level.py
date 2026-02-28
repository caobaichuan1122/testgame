# ============================================================
#  Demo level builder — 16 independent 30×30 zone scenes
#
#  Each zone function builds its own IsoMap(30,30) and
#  entity lists using LOCAL coordinates (0-29 for both axes).
#  Global systems (dialogue / quest / shop) are shared.
# ============================================================
from world.iso_map import (
    IsoMap, TILE_GRASS, TILE_GRASS2, TILE_DIRT, TILE_STONE, TILE_STONE2,
    TILE_HOUSE_WALL, TILE_ROOF,
    TILE_WATER, TILE_WATER2, TILE_SAND, TILE_BRIDGE,
    TILE_TREE, TILE_WALL, TILE_CAVE, TILE_CLIFF, TILE_FENCE,
)
from world.scene_manager import SceneManager
from entities.enemy import Enemy
from entities.npc import NPC
from systems.dialogue import DialogueManager
from systems.quest import QuestManager
from systems.shop import ShopManager
from systems.i18n import t, tf
import random

# ── Zone metadata (used for HUD banner & explore quests) ────
ZONES = [
    {"id": "shire",        "name_key": "zone_shire",        "diff_key": "diff_easy"},
    {"id": "rivendell",    "name_key": "zone_rivendell",    "diff_key": "diff_safe"},
    {"id": "lothlorien",   "name_key": "zone_lothlorien",   "diff_key": "diff_medium"},
    {"id": "weathertop",   "name_key": "zone_weathertop",   "diff_key": "diff_very_hard"},
    {"id": "fangorn",      "name_key": "zone_fangorn",      "diff_key": "diff_medium"},
    {"id": "hobbiton",     "name_key": "zone_hobbiton",     "diff_key": "diff_safe"},
    {"id": "misty_mts",    "name_key": "zone_misty_mts",    "diff_key": "diff_hard"},
    {"id": "moria",        "name_key": "zone_moria",        "diff_key": "diff_very_hard"},
    {"id": "rohan_west",   "name_key": "zone_rohan_west",   "diff_key": "diff_easy"},
    {"id": "rohan_center", "name_key": "zone_rohan_center", "diff_key": "diff_medium"},
    {"id": "rohan_east",   "name_key": "zone_rohan_east",   "diff_key": "diff_hard"},
    {"id": "dead_marshes", "name_key": "zone_dead_marshes", "diff_key": "diff_very_hard"},
    {"id": "anduin",       "name_key": "zone_anduin",       "diff_key": "diff_medium"},
    {"id": "osgiliath",    "name_key": "zone_osgiliath",    "diff_key": "diff_hard"},
    {"id": "mordor",       "name_key": "zone_mordor",       "diff_key": "diff_boss"},
    {"id": "mount_doom",   "name_key": "zone_mount_doom",   "diff_key": "diff_boss"},
]


# ============================================================
#  Walkability helper — snaps a position to the nearest walkable tile
# ============================================================
def _clamp_to_walkable(m, wx, wy):
    """Return (wx, wy) clamped to the nearest walkable tile center."""
    return m.nearest_walkable(wx, wy)


def _validate_scene(scene):
    """Snap all entity positions in a scene dict to walkable tiles."""
    m = scene["iso_map"]
    for e in scene["enemies"]:
        e.wx, e.wy = _clamp_to_walkable(m, e.wx, e.wy)
    for n in scene["npcs"]:
        n.wx, n.wy = _clamp_to_walkable(m, n.wx, n.wy)
        n.home_wx, n.home_wy = n.wx, n.wy   # keep home in sync
        n.patrol_points = [
            _clamp_to_walkable(m, px, py) for px, py in n.patrol_points
        ]
        n._move_target = None               # clear any stale target


# ============================================================
#  Main entry point
# ============================================================
def build_demo_level():
    """Build all 16 scenes + global subsystems. Returns the data dict."""
    scene_mgr = SceneManager()

    builders = {
        "shire":        _build_shire,
        "rivendell":    _build_rivendell,
        "lothlorien":   _build_lothlorien,
        "weathertop":   _build_weathertop,
        "fangorn":      _build_fangorn,
        "hobbiton":     _build_hobbiton,
        "misty_mts":    _build_misty_mts,
        "moria":        _build_moria,
        "rohan_west":   _build_rohan_west,
        "rohan_center": _build_rohan_center,
        "rohan_east":   _build_rohan_east,
        "dead_marshes": _build_dead_marshes,
        "anduin":       _build_anduin,
        "osgiliath":    _build_osgiliath,
        "mordor":       _build_mordor,
        "mount_doom":   _build_mount_doom,
    }
    for zone_id, fn in builders.items():
        scene = fn()
        _validate_scene(scene)          # snap all entities to walkable tiles
        scene_mgr.scenes[zone_id] = scene

    scene_mgr.active_id = "hobbiton"

    dialogue_mgr = _build_dialogues()
    quest_mgr    = _build_quests()
    shop_mgr     = _build_shops()

    return {
        "scene_mgr":    scene_mgr,
        "dialogue_mgr": dialogue_mgr,
        "quest_mgr":    quest_mgr,
        "shop_mgr":     shop_mgr,
        "player_start": (14, 14),   # center of Hobbiton
        "zones":        ZONES,
    }


# ============================================================
#  Zone builders — all coords LOCAL (0-29)
# ============================================================

def _build_shire():
    """The Shire — EASY ★  (safe starter zone, goblins)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS)
    # Rolling hills
    m.fill_rect(3, 3, 14, 14, TILE_GRASS2)
    m.fill_rect(16, 2, 28, 10, TILE_GRASS2)
    # Stream (west-center to south)
    for r in range(10, 28):
        m.set_tile(18, r, TILE_WATER)
        m.set_tile(19, r, TILE_WATER)
    m.set_tile(18, 28, TILE_BRIDGE)
    m.set_tile(19, 28, TILE_BRIDGE)
    # Trees
    for c, r in [(2,2),(6,7),(10,2),(22,4),(26,1),(27,14),(4,18),(8,24),(16,21)]:
        m.set_tile(c, r, TILE_TREE)
    # Hobbit houses
    _house(m, 6, 14, 10, 18, 8, 14)
    _house(m, 13, 14, 17, 18, 15, 14)
    # Road south (connects to Fangorn border)
    for c in range(1, 29):
        m.set_tile(c, 27, TILE_DIRT)
        m.set_tile(c, 28, TILE_DIRT)
    # Road east (connects to Rivendell border)
    for r in range(1, 29):
        m.set_tile(27, r, TILE_DIRT)
        m.set_tile(28, r, TILE_DIRT)

    enemies = [Enemy(*p, "goblin") for p in
               [(5,9),(8,15),(13,7),(17,4),(23,11),(9,21),(20,19)]]
    return {"iso_map": m, "enemies": enemies, "npcs": []}


def _build_rivendell():
    """Rivendell — SAFE ★  (shop hub, Bilbo)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS2)
    m.fill_rect(4, 4, 26, 26, TILE_STONE)
    # Central paths
    for c in range(4, 26): m.set_tile(c, 14, TILE_DIRT)
    for r in range(4, 26): m.set_tile(14, r, TILE_DIRT); m.set_tile(15, r, TILE_DIRT)
    # Elrond's Hall
    _house(m, 8, 6, 18, 12, 13, 6)
    # Garden trees
    for c, r in [(5,3),(6,3),(23,3),(24,3),(5,26),(24,26)]:
        m.set_tile(c, r, TILE_TREE)
    # Waterfall east border
    for r in range(1, 29): m.set_tile(29, r, TILE_WATER2)
    # Road west edge (connects to Shire)
    for r in range(12, 18): m.set_tile(0, r, TILE_DIRT); m.set_tile(1, r, TILE_DIRT)
    # Road south (connects to Hobbiton)
    for c in range(12, 18): m.set_tile(c, 28, TILE_DIRT); m.set_tile(c, 29, TILE_DIRT)

    bilbo = NPC(14, 10, name="Bilbo", npc_type="shop",
                shop_id="elrond_shop", dialogue_id="bilbo_default",
                color=(220, 200, 140), behavior="wander", wander_radius=2.0,
                idle_lines=[t("idle_bilbo_1"), t("idle_bilbo_2"), t("idle_bilbo_3")])
    return {"iso_map": m, "enemies": [], "npcs": [bilbo]}


def _build_lothlorien():
    """Lothlórien — MEDIUM ★★  (wolves + spiders, Legolas)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS2)
    # Border trees
    for c in range(30): m.set_tile(c, 0, TILE_TREE)
    for r in range(30): m.set_tile(0, r, TILE_TREE)
    # Interior tree clusters
    for c, r in [(3,3),(7,6),(12,2),(18,8),(24,4),(14,18),(22,12),(26,20),(5,24),(16,25)]:
        m.set_tile(c, r, TILE_TREE)
    # Golden clearing (center)
    m.fill_rect(8, 8, 22, 22, TILE_GRASS)
    # Roads
    for c in range(1, 29): m.set_tile(c, 27, TILE_DIRT); m.set_tile(c, 28, TILE_DIRT)
    for r in range(1, 29): m.set_tile(27, r, TILE_DIRT); m.set_tile(28, r, TILE_DIRT)

    enemies = (
        [Enemy(*p, "wolf")   for p in [(4,5),(8,12),(16,8),(22,4),(13,22),(26,16)]] +
        [Enemy(*p, "spider") for p in [(3,15),(10,20),(19,18),(26,25)]]
    )
    legolas = NPC(15, 15, name="Legolas", npc_type="quest",
                  quest_ids=["quest_wolf", "quest_spider"],
                  dialogue_id="legolas_default",
                  color=(180, 210, 160), behavior="patrol",
                  patrol_points=[(13,13),(17,13),(17,17),(13,17)],
                  idle_lines=[t("idle_legolas_1"), t("idle_legolas_2"), t("idle_legolas_3")])
    return {"iso_map": m, "enemies": enemies, "npcs": [legolas]}


def _build_weathertop():
    """Weathertop Ruins — VERY HARD ★★★★  (nazgul, Aragorn)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_STONE2)
    # Cliff borders (leave edges clear for transition)
    for c in range(1, 29): m.set_tile(c, 1, TILE_CLIFF)
    for r in range(1, 29): m.set_tile(28, r, TILE_CLIFF)
    # Ruined tower
    m.fill_rect(8, 7, 22, 21, TILE_STONE)
    for c in range(8, 22): m.set_tile(c, 7, TILE_WALL); m.set_tile(c, 20, TILE_WALL)
    for r in range(7, 21): m.set_tile(8, r, TILE_WALL); m.set_tile(21, r, TILE_WALL)
    m.fill_rect(10, 9, 20, 19, TILE_CAVE)
    # Passage through south wall
    m.set_tile(14, 20, TILE_STONE); m.set_tile(15, 20, TILE_STONE)
    # Approach path south
    for r in range(20, 30): m.set_tile(14, r, TILE_STONE); m.set_tile(15, r, TILE_STONE)
    # Crags
    for c, r in [(2,4),(5,11),(26,7),(27,18),(2,24)]:
        m.set_tile(c, r, TILE_CLIFF)
    # Entry from west
    for r in range(13, 17): m.set_tile(0, r, TILE_STONE); m.set_tile(1, r, TILE_STONE)

    enemies = [Enemy(*p, "nazgul") for p in [(12,14),(17,14),(14,18)]]
    aragorn = NPC(14, 25, name="Aragorn", npc_type="quest",
                  quest_ids=["quest_nazgul"], dialogue_id="aragorn_default",
                  color=(130, 150, 190), behavior="patrol",
                  patrol_points=[(12,24),(17,24),(17,27),(12,27)],
                  idle_lines=[t("idle_aragorn_1"), t("idle_aragorn_2"), t("idle_aragorn_3")])
    return {"iso_map": m, "enemies": enemies, "npcs": [aragorn]}


def _build_fangorn():
    """Fangorn Forest — MEDIUM ★★  (wights, wolves)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS2)
    # Border trees (leave transition edges open)
    for c in range(30): m.set_tile(c, 0, TILE_TREE)
    for r in range(30): m.set_tile(0, r, TILE_TREE)
    # Interior trees
    for c, r in [(3,4),(7,7),(12,2),(5,10),(15,5),(2,16),(8,14),(16,10),(4,20),(14,18),(25,14),(22,8),(28,20)]:
        m.set_tile(c, r, TILE_TREE)
    # Ancient path south → north
    for r in range(1, 28):
        m.set_tile(13, r, TILE_DIRT)
        m.set_tile(14, r, TILE_DIRT)
    # Road east (to Hobbiton)
    for r in range(12, 17): m.set_tile(28, r, TILE_DIRT); m.set_tile(29, r, TILE_DIRT)

    enemies = (
        [Enemy(*p, "wight") for p in [(5,5),(8,10),(14,6),(6,18),(16,14),(22,8),(25,22)]] +
        [Enemy(*p, "wolf")  for p in [(3,14),(20,20),(26,15)]]
    )
    return {"iso_map": m, "enemies": enemies, "npcs": []}


def _build_hobbiton():
    """Hobbiton Hub — SAFE (main village, all main NPCs)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_DIRT)
    # Crossroads
    for c in range(30): m.set_tile(c, 14, TILE_STONE); m.set_tile(c, 15, TILE_STONE)
    for r in range(30): m.set_tile(14, r, TILE_STONE); m.set_tile(15, r, TILE_STONE)
    # NW quad houses
    _house(m, 2, 2, 6, 6, 4, 2);  m.set_tile(4, 7, TILE_DIRT)
    _house(m, 8, 2, 12, 6, 10, 2); m.set_tile(10, 7, TILE_DIRT)
    # NE quad houses
    _house(m, 17, 2, 21, 6, 19, 2); m.set_tile(19, 7, TILE_DIRT)
    _house(m, 23, 2, 27, 6, 25, 2); m.set_tile(25, 7, TILE_DIRT)
    # SW quad houses
    _house(m, 2, 17, 6, 21, 4, 17);  m.set_tile(4, 16, TILE_DIRT)
    _house(m, 8, 17, 12, 21, 10, 17); m.set_tile(10, 16, TILE_DIRT)
    # SE quad houses
    _house(m, 17, 17, 21, 21, 19, 17); m.set_tile(19, 16, TILE_DIRT)
    _house(m, 23, 17, 27, 21, 25, 17); m.set_tile(25, 16, TILE_DIRT)
    # Inn / large building (center north)
    _house(m, 9, 2, 19, 10, 14, 2)
    # Perimeter fence with 4 gate openings
    for c in range(30):
        if not (13 <= c <= 16): m.set_tile(c, 0, TILE_FENCE); m.set_tile(c, 29, TILE_FENCE)
    for r in range(1, 29):
        if not (13 <= r <= 16): m.set_tile(0, r, TILE_FENCE); m.set_tile(29, r, TILE_FENCE)

    # ── NPCs ────────────────────────────────────────────────
    gandalf = NPC(14, 8, name="Gandalf", npc_type="quest",
                  quest_ids=["quest_orc", "quest_boss"],
                  dialogue_id="gandalf_default", color=(200, 160, 60),
                  behavior="wander", wander_radius=2.0,
                  idle_lines=[t("idle_gandalf_1"), t("idle_gandalf_2"),
                               t("idle_gandalf_3"), t("idle_gandalf_4")])

    barliman = NPC(4, 8, name="Barliman", npc_type="shop",
                   shop_id="general_shop", dialogue_id="barliman_default",
                   color=(100, 200, 100), behavior="idle",
                   idle_lines=[t("idle_barliman_1"), t("idle_barliman_2"), t("idle_barliman_3")])

    gimli = NPC(24, 8, name="Gimli", npc_type="shop",
                shop_id="weapon_shop", dialogue_id="gimli_default",
                color=(200, 120, 80), behavior="wander", wander_radius=1.0,
                idle_lines=[t("idle_gimli_1"), t("idle_gimli_2"), t("idle_gimli_3")])

    arwen = NPC(14, 25, name="Arwen", npc_type="quest",
                quest_ids=["quest_collect"], dialogue_id="arwen_default",
                color=(200, 100, 200), behavior="patrol",
                patrol_points=[(12,24),(16,24),(16,27),(12,27)],
                idle_lines=[t("idle_arwen_1"), t("idle_arwen_2"),
                             t("idle_arwen_3"), t("idle_arwen_4")])

    boromir = NPC(14, 1, name="Boromir", npc_type="quest",
                  quest_ids=["quest_explore"], dialogue_id="boromir_default",
                  color=(120, 140, 200), behavior="patrol",
                  patrol_points=[(12,1),(16,1),(16,4),(12,4)],
                  idle_lines=[t("idle_boromir_1"), t("idle_boromir_2"),
                               t("idle_boromir_3"), t("idle_boromir_4")])

    frodo = NPC(20, 14, name="Frodo", npc_type="quest",
                quest_ids=["quest_escort"], dialogue_id="frodo_default",
                color=(180, 160, 120), behavior="wander", wander_radius=3.0,
                idle_lines=[t("idle_frodo_1"), t("idle_frodo_2"),
                             t("idle_frodo_3"), t("idle_frodo_4")])

    return {"iso_map": m, "enemies": [],
            "npcs": [gandalf, barliman, gimli, arwen, boromir, frodo]}


def _build_misty_mts():
    """Misty Mountains — HARD ★★★  (spiders + cave trolls)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_STONE2)
    # Cliff borders
    for c in range(1, 29): m.set_tile(c, 0, TILE_CLIFF)
    for r in range(1, 29): m.set_tile(28, r, TILE_CLIFF)
    # Cliffs interior
    for c, r in [(3,3),(8,8),(12,2),(20,6),(25,12),(5,18),(17,22),(27,25)]:
        m.set_tile(c, r, TILE_CLIFF)
    # Mountain pass (N-S)
    for r in range(1, 28): m.set_tile(13, r, TILE_STONE); m.set_tile(14, r, TILE_STONE)
    # Cave entrance (center-left)
    m.fill_rect(2, 8, 11, 18, TILE_CAVE)
    # Entry from west (Fangorn side)
    for r in range(12, 17): m.set_tile(0, r, TILE_STONE); m.set_tile(1, r, TILE_STONE)
    # Entry south (Rohan East)
    for c in range(12, 17): m.set_tile(c, 28, TILE_STONE); m.set_tile(c, 29, TILE_STONE)

    enemies = (
        [Enemy(*p, "spider")     for p in [(2,7),(5,14),(10,10),(20,4),(25,18),(18,25)]] +
        [Enemy(*p, "cave_troll") for p in [(6,22),(23,8)]]
    )
    return {"iso_map": m, "enemies": enemies, "npcs": []}


def _build_moria():
    """Mines of Moria — VERY HARD ★★★★  (cave troll boss + wights)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_STONE)
    # Outer walls (leave south entry open)
    for c in range(30): m.set_tile(c, 0, TILE_WALL)
    for r in range(30): m.set_tile(0, r, TILE_WALL); m.set_tile(29, r, TILE_WALL)
    m.set_tile(29, 0, TILE_WALL)
    # South entry gap
    m.set_tile(14, 0, TILE_STONE); m.set_tile(15, 0, TILE_STONE)
    # Interior cave
    m.fill_rect(2, 2, 28, 28, TILE_CAVE)
    # Pillars
    for c, r in [(5,5),(10,5),(20,5),(24,5),(5,14),(24,14),(5,23),(10,23),(20,23),(24,23)]:
        m.set_tile(c, r, TILE_WALL)
    # Main hall path
    for c in range(2, 28): m.set_tile(c, 14, TILE_STONE); m.set_tile(c, 15, TILE_STONE)
    for r in range(2, 28): m.set_tile(14, r, TILE_STONE); m.set_tile(15, r, TILE_STONE)

    boss = Enemy(14, 14, "cave_troll")
    enemies = [boss] + [Enemy(*p, "wight") for p in [(5,6),(22,6),(6,22),(23,22)]]
    return {"iso_map": m, "enemies": enemies, "npcs": []}


def _build_rohan_west():
    """West Rohan — EASY ★  (goblins + orcs, Éowyn)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS)
    m.fill_rect(4, 5, 26, 15, TILE_GRASS2)
    # West border trees
    for r in range(30): m.set_tile(0, r, TILE_TREE)
    for c, r in [(3,3),(8,10),(15,2),(22,8),(26,15)]:
        m.set_tile(c, r, TILE_TREE)
    # Farm buildings
    _house(m, 9, 6, 13, 10, 11, 6)
    _house(m, 15, 6, 19, 10, 17, 6)
    # Road south / east
    for c in range(1, 29): m.set_tile(c, 27, TILE_DIRT); m.set_tile(c, 28, TILE_DIRT)
    for r in range(1, 29): m.set_tile(27, r, TILE_DIRT); m.set_tile(28, r, TILE_DIRT)

    enemies = (
        [Enemy(*p, "goblin") for p in [(5,5),(12,12),(20,8),(8,20),(25,16)]] +
        [Enemy(*p, "orc")    for p in [(15,3),(22,18)]]
    )
    eowyn = NPC(12, 5, name="Éowyn", npc_type="quest",
                quest_ids=["quest_goblin"], dialogue_id="eowyn_default",
                color=(230, 200, 150), behavior="patrol",
                patrol_points=[(10,3),(14,3),(14,7),(10,7)],
                idle_lines=[t("idle_eowyn_1"), t("idle_eowyn_2"), t("idle_eowyn_3")])
    return {"iso_map": m, "enemies": enemies, "npcs": [eowyn]}


def _build_rohan_center():
    """Rohan Plains — MEDIUM ★★  (orcs, Théoden + smith)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS)
    # Edoras (fortified hilltop, center)
    m.fill_rect(8, 8, 22, 22, TILE_STONE)
    for c in range(8, 22): m.set_tile(c, 8, TILE_WALL); m.set_tile(c, 21, TILE_WALL)
    for r in range(8, 22): m.set_tile(8, r, TILE_WALL); m.set_tile(21, r, TILE_WALL)
    # Gate south
    m.set_tile(14, 21, TILE_STONE); m.set_tile(15, 21, TILE_STONE)
    # Golden Hall
    _house(m, 11, 11, 18, 17, 14, 11)
    # Roads
    for r in range(30): m.set_tile(13, r, TILE_DIRT); m.set_tile(14, r, TILE_DIRT)
    for c in range(30): m.set_tile(c, 27, TILE_DIRT); m.set_tile(c, 28, TILE_DIRT)

    enemies = [Enemy(random.randint(1,27), random.randint(1,27), "orc") for _ in range(8)]
    theoden = NPC(14, 15, name="Théoden", npc_type="quest",
                  quest_ids=["quest_berserker"], dialogue_id="theoden_default",
                  color=(200, 170, 100), behavior="patrol",
                  patrol_points=[(12,13),(16,13),(16,18),(12,18)],
                  idle_lines=[t("idle_theoden_1"), t("idle_theoden_2"), t("idle_theoden_3")])
    smith = NPC(5, 5, name="Éothain", npc_type="shop",
                shop_id="rohan_shop", dialogue_id="barliman_default",
                color=(160, 140, 100), behavior="idle",
                idle_lines=[t("idle_barliman_1"), t("idle_barliman_2"), t("idle_barliman_3")])
    return {"iso_map": m, "enemies": enemies, "npcs": [theoden, smith]}


def _build_rohan_east():
    """East Rohan — HARD ★★★  (uruk archers + berserkers)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS)
    m.fill_rect(0, 0, 30, 4, TILE_GRASS2)
    # Helm's Deep ruins
    m.fill_rect(8, 6, 22, 18, TILE_STONE)
    for c in range(8, 22): m.set_tile(c, 6, TILE_WALL); m.set_tile(c, 17, TILE_WALL)
    for r in range(6, 18): m.set_tile(8, r, TILE_WALL); m.set_tile(21, r, TILE_WALL)
    m.fill_rect(10, 8, 20, 16, TILE_CAVE)
    # East border trees
    for r in range(30): m.set_tile(29, r, TILE_TREE)
    # Road south
    for c in range(1, 28): m.set_tile(c, 27, TILE_DIRT); m.set_tile(c, 28, TILE_DIRT)

    enemies = (
        [Enemy(*p, "uruk_archer")    for p in [(2,4),(5,12),(12,4),(18,12),(25,4),(27,18)]] +
        [Enemy(*p, "uruk_berserker") for p in [(5,20),(16,8),(22,16),(27,2)]]
    )
    return {"iso_map": m, "enemies": enemies, "npcs": []}


def _build_dead_marshes():
    """Dead Marshes — VERY HARD ★★★★  (undead + wights, Gollum)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_WATER)
    # Muddy islands
    for x1, y1, x2, y2 in [(2,2,10,10),(13,5,23,13),(5,15,16,23),(18,17,27,27)]:
        m.fill_rect(x1, y1, x2, y2, TILE_DIRT)
    # Deep water channels
    m.fill_rect(10, 2, 14, 30, TILE_WATER2)
    # Twisted trees on islands
    for c, r in [(3,3),(7,7),(14,6),(21,10),(6,17),(13,21),(20,18),(25,24)]:
        m.set_tile(c, r, TILE_TREE)
    # Bridges between islands
    m.set_tile(10, 6, TILE_BRIDGE); m.set_tile(10, 7, TILE_BRIDGE)
    m.set_tile(10, 19, TILE_BRIDGE); m.set_tile(10, 20, TILE_BRIDGE)
    # Entry west
    for r in range(12, 17): m.set_tile(0, r, TILE_DIRT); m.set_tile(1, r, TILE_DIRT)

    enemies = (
        [Enemy(*p, "undead") for p in [(3,4),(7,8),(16,7),(21,12),(6,17),(13,22),(24,20),(27,25)]] +
        [Enemy(*p, "wight")  for p in [(4,12),(18,4),(25,16)]]
    )
    gollum = NPC(4, 5, name="Gollum", npc_type="quest",
                 quest_ids=[], dialogue_id="gollum_default",
                 color=(140, 150, 130), behavior="wander", wander_radius=3.0,
                 idle_lines=[t("idle_gollum_1"), t("idle_gollum_2"), t("idle_gollum_3")])
    return {"iso_map": m, "enemies": enemies, "npcs": [gollum]}


def _build_anduin():
    """River Anduin — MEDIUM ★★  (orcs + undead, Sam)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_WATER)
    # Banks
    m.fill_rect(0, 0, 30, 6, TILE_GRASS2)
    m.fill_rect(0, 23, 30, 30, TILE_GRASS2)
    m.fill_rect(3, 7, 27, 23, TILE_WATER2)
    # Shallow edges
    for c in range(30): m.set_tile(c, 7, TILE_WATER); m.set_tile(c, 22, TILE_WATER)
    # Fishing pier (north bank)
    for c in range(11, 17): m.set_tile(c, 6, TILE_BRIDGE)
    # Trees on banks
    for c, r in [(2,1),(5,4),(8,2),(21,2),(26,4),(3,24),(12,25),(25,23)]:
        m.set_tile(c, r, TILE_TREE)
    # Road north/south (connects Rohan West above, Osgiliath below)
    for c in range(1, 29): m.set_tile(c, 0, TILE_DIRT); m.set_tile(c, 1, TILE_DIRT)
    for c in range(1, 29): m.set_tile(c, 28, TILE_DIRT); m.set_tile(c, 29, TILE_DIRT)

    enemies = (
        [Enemy(*p, "orc")    for p in [(3,5),(8,3),(15,4),(21,3),(25,4),(5,25),(18,24)]] +
        [Enemy(*p, "undead") for p in [(10,5),(20,24)]]
    )
    sam = NPC(15, 4, name="Sam", npc_type="quest",
              quest_ids=["quest_timed"], dialogue_id="sam_default",
              color=(100, 160, 180), behavior="idle",
              idle_lines=[t("idle_sam_1"), t("idle_sam_2"),
                           t("idle_sam_3"), t("idle_sam_4")])
    return {"iso_map": m, "enemies": enemies, "npcs": [sam]}


def _build_osgiliath():
    """Osgiliath Ruins — HARD ★★★  (undead + uruk archers, Faramir)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_GRASS)
    # River through center
    m.fill_rect(0, 10, 30, 20, TILE_WATER)
    m.fill_rect(12, 10, 18, 20, TILE_BRIDGE)
    # Ruined north bank
    m.fill_rect(2, 1, 28, 9, TILE_STONE)
    for c, r in [(3,2),(9,2),(18,2),(25,2),(5,6),(14,6),(23,6)]:
        m.set_tile(c, r, TILE_WALL)
    # Ruined south bank
    m.fill_rect(2, 21, 28, 28, TILE_STONE)
    for c, r in [(4,22),(11,22),(20,22),(26,22),(7,25),(17,25)]:
        m.set_tile(c, r, TILE_WALL)
    # Road through ruins
    for r in range(30): m.set_tile(14, r, TILE_DIRT); m.set_tile(15, r, TILE_DIRT)

    enemies = (
        [Enemy(*p, "undead")      for p in [(3,3),(9,5),(21,4),(26,6),(5,24),(17,26),(23,23)]] +
        [Enemy(*p, "uruk_archer") for p in [(8,22),(24,22)]] +
        [Enemy(14, 14, "cave_troll")]
    )
    faramir = NPC(14, 4, name="Faramir", npc_type="quest",
                  quest_ids=["quest_undead"], dialogue_id="faramir_default",
                  color=(120, 140, 200), behavior="patrol",
                  patrol_points=[(12,3),(17,3),(17,7),(12,7)],
                  idle_lines=[t("idle_faramir_1"), t("idle_faramir_2"), t("idle_faramir_3")])
    return {"iso_map": m, "enemies": enemies, "npcs": [faramir]}


def _build_mordor():
    """Mordor Wastes — DANGER ★★★★★  (berserkers + nazgul)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_SAND)
    # Cliff borders (leave west entry open)
    for c in range(1, 29): m.set_tile(c, 29, TILE_CLIFF)
    for r in range(1, 29): m.set_tile(0, r, TILE_CLIFF)
    # Volcanic rocks
    for c, r in [(3,5),(8,10),(16,4),(22,12),(27,5),(5,18),(13,22),(26,18)]:
        m.set_tile(c, r, TILE_CLIFF)
    # Ash plain interior
    m.fill_rect(2, 2, 28, 28, TILE_STONE2)
    # Mordor Gate (north)
    for c in range(11, 19): m.set_tile(c, 2, TILE_WALL)
    m.set_tile(14, 2, TILE_STONE2); m.set_tile(15, 2, TILE_STONE2)
    # Road to Mount Doom (east)
    for r in range(13, 17): m.set_tile(27, r, TILE_STONE); m.set_tile(28, r, TILE_STONE)
    for c in range(2, 29): m.set_tile(c, 14, TILE_STONE); m.set_tile(c, 15, TILE_STONE)

    enemies = (
        [Enemy(*p, "uruk_berserker") for p in [(3,5),(10,10),(18,4),(23,12),(5,20),(13,25),(22,18),(27,26)]] +
        [Enemy(*p, "nazgul")         for p in [(6,7),(20,8),(15,22)]] +
        [Enemy(*p, "uruk_archer")    for p in [(2,14),(27,14)]]
    )
    return {"iso_map": m, "enemies": enemies, "npcs": []}


def _build_mount_doom():
    """Mount Doom — BOSS ★★★★★  (Balrog final boss)"""
    m = IsoMap(30, 30)
    m.fill_rect(0, 0, 30, 30, TILE_SAND)
    # Cliff walls (leave west entry open)
    for c in range(1, 29): m.set_tile(c, 0, TILE_CLIFF); m.set_tile(c, 29, TILE_CLIFF)
    for r in range(1, 29): m.set_tile(29, r, TILE_CLIFF)
    # Mountain
    m.fill_rect(7, 5, 23, 24, TILE_STONE2)
    for c in range(7, 23): m.set_tile(c, 5, TILE_CLIFF); m.set_tile(c, 23, TILE_CLIFF)
    for r in range(5, 24): m.set_tile(7, r, TILE_CLIFF); m.set_tile(22, r, TILE_CLIFF)
    # Lava (WATER2 repurposed)
    m.fill_rect(9, 7, 21, 22, TILE_WATER2)
    # Sammath Naur — bridge of stone across lava
    for r in range(7, 22): m.set_tile(14, r, TILE_STONE); m.set_tile(15, r, TILE_STONE)
    # Approach west → east
    for r in range(13, 17): m.set_tile(0, r, TILE_STONE); m.set_tile(1, r, TILE_STONE)
    for c in range(1, 8): m.set_tile(c, 14, TILE_STONE); m.set_tile(c, 15, TILE_STONE)

    balrog = Enemy(14, 14, "balrog")
    guards  = [Enemy(*p, "nazgul") for p in [(6,10),(23,10),(6,21),(23,21)]]
    pippin = NPC(13, 4, name="Pippin", npc_type="quest",
                 quest_ids=["quest_balrog"], dialogue_id="mount_doom_guide",
                 color=(170, 145, 110), behavior="idle",
                 idle_lines=[t("idle_frodo_1"), t("idle_sam_1"), t("idle_frodo_3")])
    return {"iso_map": m, "enemies": [balrog] + guards, "npcs": [pippin]}


# ============================================================
#  Global: Dialogue / Quest / Shop
# ============================================================
def _build_dialogues() -> DialogueManager:
    d = DialogueManager()

    # Gandalf
    d.register("gandalf_default", {"start": {
        "text": t("dlg_gandalf_default"),
        "options": [{"label": t("opt_ok"), "next": None}],
    }})
    for qid, ak, pk, ck, opt in [
        ("quest_orc",  "dlg_quest_orc_accept",  "dlg_quest_orc_progress",  "dlg_quest_orc_complete",  "opt_for_the_shire"),
        ("quest_boss", "dlg_quest_boss_accept",  "dlg_quest_boss_progress", "dlg_quest_boss_complete", "opt_you_shall_not_pass"),
    ]:
        d.register(f"{qid}_accept",   {"start": {"text": t(ak), "options": [{"label": t(opt), "next": None}]}})
        d.register(f"{qid}_progress", {"start": {"text": t(pk), "options": [{"label": t("opt_ok"),    "next": None}]}})
        d.register(f"{qid}_complete", {"start": {"text": t(ck), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Barliman (shop trigger)
    d.register("barliman_default", {"start": {
        "text": t("dlg_barliman_default"),
        "options": [
            {"label": t("opt_open_shop"), "next": None, "callback": lambda g: g.ui.open_shop("general_shop")},
            {"label": t("opt_farewell"),  "next": None},
        ],
    }})

    # Gimli (weapon shop, branching)
    d.register("gimli_default", {
        "start": {
            "text": t("dlg_gimli_default"),
            "options": [
                {"label": t("opt_open_shop"),   "next": None, "callback": lambda g: g.ui.open_shop("weapon_shop")},
                {"label": t("opt_tell_weapons"), "next": "weapons_info"},
                {"label": t("opt_farewell"),     "next": None},
            ],
        },
        "weapons_info": {
            "text": t("dlg_gimli_weapons_info"),
            "options": [
                {"label": t("opt_which_best"), "next": "best_weapon"},
                {"label": t("opt_open_shop"),  "next": None, "callback": lambda g: g.ui.open_shop("weapon_shop")},
                {"label": t("opt_thanks"),     "next": None},
            ],
        },
        "best_weapon": {
            "text": t("dlg_gimli_best_weapon"),
            "options": [{"label": t("opt_got_it"), "next": None}],
        },
    })

    # Arwen (heal + collect quest)
    def _heal(game):
        p = game.entities.player
        if p and p.inventory.gold >= 20:
            p.inventory.gold -= 20
            p.stats.hp = p.stats.max_hp
            p.stats.mp = p.stats.max_mp
            p.add_message(t("fully_healed"))
            game.chat_log.add(t("healed_by_arwen"), "system")
        elif p:
            p.add_message(t("not_enough_gold_short"))

    d.register("arwen_default", {
        "start": {
            "text": t("dlg_arwen_default"),
            "options": [
                {"label": t("opt_heal_me"),  "next": "healed", "callback": _heal},
                {"label": t("opt_no_thanks"), "next": None},
            ],
        },
        "healed": {"text": t("dlg_arwen_healed"), "options": [{"label": t("opt_thanks"), "next": None}]},
    })
    for k_a, k_p, k_c, opt in [
        ("dlg_quest_collect_accept", "dlg_quest_collect_progress", "dlg_quest_collect_complete", "opt_ill_gather"),
    ]:
        d.register("quest_collect_accept",   {"start": {"text": t(k_a), "options": [{"label": t(opt), "next": None}]}})
        d.register("quest_collect_progress", {"start": {"text": t(k_p), "options": [{"label": t("opt_on_it"), "next": None}]}})
        d.register("quest_collect_complete", {"start": {"text": t(k_c), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Boromir (explore quest)
    d.register("boromir_default", {
        "start": {
            "text": t("dlg_boromir_default"),
            "options": [
                {"label": t("opt_what_lies_beyond"), "next": "area_info"},
                {"label": t("opt_just_passing"),      "next": None},
            ],
        },
        "area_info": {"text": t("dlg_boromir_area_info"), "options": [{"label": t("opt_got_it"), "next": None}]},
    })
    d.register("quest_explore_accept",   {"start": {"text": t("dlg_quest_explore_accept"),   "options": [{"label": t("opt_for_gondor"), "next": None}]}})
    d.register("quest_explore_progress", {"start": {"text": t("dlg_quest_explore_progress"), "options": [{"label": t("opt_not_yet"), "next": None}]}})
    d.register("quest_explore_complete", {"start": {"text": t("dlg_quest_explore_complete"), "options": [{"label": t("opt_thank_you"), "next": None}]}})

    # Frodo (escort)
    d.register("frodo_default", {
        "start": {
            "text": t("dlg_frodo_default"),
            "options": [
                {"label": t("opt_any_tips"),    "next": "tips"},
                {"label": t("opt_safe_travels"), "next": None},
            ],
        },
        "tips": {"text": t("dlg_frodo_tips"), "options": [{"label": t("opt_thanks"), "next": None}]},
    })
    d.register("quest_escort_accept",   {"start": {"text": t("dlg_quest_escort_accept"),   "options": [{"label": t("opt_follow_me"), "next": None}]}})
    d.register("quest_escort_progress", {"start": {"text": t("dlg_quest_escort_progress"), "options": [{"label": t("opt_almost_there"), "next": None}]}})
    d.register("quest_escort_complete", {"start": {"text": t("dlg_quest_escort_complete"), "options": [{"label": t("opt_glad_to_help"), "next": None}]}})

    # Sam (timed)
    d.register("sam_default", {
        "start": {
            "text": t("dlg_sam_default"),
            "options": [
                {"label": t("opt_tell_more"),     "next": "mordor_info"},
                {"label": t("opt_good_luck_sam"), "next": None},
            ],
        },
        "mordor_info": {"text": t("dlg_sam_mordor_info"), "options": [{"label": t("opt_i_see"), "next": None}]},
    })
    d.register("quest_timed_accept",   {"start": {"text": t("dlg_quest_timed_accept"),   "options": [{"label": t("opt_im_on_it"), "next": None}]}})
    d.register("quest_timed_progress", {"start": {"text": t("dlg_quest_timed_progress"), "options": [{"label": t("opt_im_going"), "next": None}]}})
    d.register("quest_timed_complete", {"start": {"text": t("dlg_quest_timed_complete"), "options": [{"label": t("opt_thanks"),  "next": None}]}})

    # Bilbo
    d.register("bilbo_default", {
        "start": {
            "text": t("dlg_bilbo_default"),
            "options": [
                {"label": t("opt_open_shop"),   "next": None, "callback": lambda g: g.ui.open_shop("elrond_shop")},
                {"label": t("opt_tell_story"),  "next": "story"},
                {"label": t("opt_farewell"),    "next": None},
            ],
        },
        "story": {"text": t("dlg_bilbo_story"), "options": [{"label": t("opt_thanks"), "next": None}]},
    })

    # Legolas (wolf + spider)
    d.register("legolas_default", {
        "start": {
            "text": t("dlg_legolas_default"),
            "options": [
                {"label": t("opt_hunt_wolves"),  "next": None},
                {"label": t("opt_clear_spiders"), "next": None},
                {"label": t("opt_farewell"),      "next": None},
            ],
        },
    })
    for q, ak, pk, ck, opt in [
        ("quest_wolf",   "quest_wolf_accept",   "quest_wolf_progress",   "quest_wolf_complete",   "opt_hunt_wolves"),
        ("quest_spider", "quest_spider_accept",  "quest_spider_progress", "quest_spider_complete", "opt_clear_spiders"),
    ]:
        d.register(f"{q}_accept",   {"start": {"text": t(ak), "options": [{"label": t(opt), "next": None}]}})
        d.register(f"{q}_progress", {"start": {"text": t(pk), "options": [{"label": t("opt_ok"), "next": None}]}})
        d.register(f"{q}_complete", {"start": {"text": t(ck), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Éowyn (goblin)
    d.register("eowyn_default", {
        "start": {
            "text": t("dlg_eowyn_default"),
            "options": [
                {"label": t("opt_for_gondor"),   "next": None},
                {"label": t("opt_just_passing"), "next": None},
            ],
        },
    })
    d.register("quest_goblin_accept",   {"start": {"text": t("quest_goblin_accept"),   "options": [{"label": t("opt_for_gondor"), "next": None}]}})
    d.register("quest_goblin_progress", {"start": {"text": t("quest_goblin_progress"), "options": [{"label": t("opt_ok"), "next": None}]}})
    d.register("quest_goblin_complete", {"start": {"text": t("quest_goblin_complete"), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Théoden (berserker)
    d.register("theoden_default", {
        "start": {
            "text": t("dlg_theoden_default"),
            "options": [
                {"label": t("opt_slay_berserkers"), "next": None},
                {"label": t("opt_careful_now"),     "next": None},
            ],
        },
    })
    d.register("quest_berserker_accept",   {"start": {"text": t("quest_berserker_accept"),   "options": [{"label": t("opt_slay_berserkers"), "next": None}]}})
    d.register("quest_berserker_progress", {"start": {"text": t("quest_berserker_progress"), "options": [{"label": t("opt_ok"), "next": None}]}})
    d.register("quest_berserker_complete", {"start": {"text": t("quest_berserker_complete"), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Aragorn (nazgul)
    d.register("aragorn_default", {
        "start": {
            "text": t("dlg_aragorn_default"),
            "options": [
                {"label": t("opt_face_nazgul"),  "next": None},
                {"label": t("opt_careful_now"),  "next": None},
            ],
        },
    })
    d.register("quest_nazgul_accept",   {"start": {"text": t("quest_nazgul_accept"),   "options": [{"label": t("opt_face_nazgul"), "next": None}]}})
    d.register("quest_nazgul_progress", {"start": {"text": t("quest_nazgul_progress"), "options": [{"label": t("opt_ok"), "next": None}]}})
    d.register("quest_nazgul_complete", {"start": {"text": t("quest_nazgul_complete"), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Faramir (undead)
    d.register("faramir_default", {
        "start": {
            "text": t("dlg_faramir_default"),
            "options": [
                {"label": t("opt_cleanse_ruins"), "next": None},
                {"label": t("opt_careful_now"),   "next": None},
            ],
        },
    })
    d.register("quest_undead_accept",   {"start": {"text": t("quest_undead_accept"),   "options": [{"label": t("opt_cleanse_ruins"), "next": None}]}})
    d.register("quest_undead_progress", {"start": {"text": t("quest_undead_progress"), "options": [{"label": t("opt_ok"), "next": None}]}})
    d.register("quest_undead_complete", {"start": {"text": t("quest_undead_complete"), "options": [{"label": t("opt_thanks"), "next": None}]}})

    # Gollum (flavor only)
    d.register("gollum_default", {
        "start": {
            "text": t("dlg_gollum_default"),
            "options": [{"label": t("opt_careful_now"), "next": None}],
        },
    })

    # Mount Doom guide
    d.register("mount_doom_guide", {
        "start": {
            "text": t("dlg_mount_doom_npc"),
            "options": [
                {"label": t("opt_destroy_ring"), "next": None},
                {"label": t("opt_careful_now"),  "next": None},
            ],
        },
    })
    d.register("quest_balrog_accept",   {"start": {"text": t("quest_balrog_accept"),   "options": [{"label": t("opt_destroy_ring"), "next": None}]}})
    d.register("quest_balrog_progress", {"start": {"text": t("quest_balrog_progress"), "options": [{"label": t("opt_ok"), "next": None}]}})
    d.register("quest_balrog_complete", {"start": {"text": t("quest_balrog_complete"), "options": [{"label": t("opt_thanks"), "next": None}]}})

    return d


def _build_quests() -> QuestManager:
    q = QuestManager()
    q.register("quest_goblin",     {"name": t("quest_name_goblin"),     "desc": t("quest_desc_goblin"),     "type": "kill",   "target": "goblin",         "required": 8,  "rewards": {"xp": 60,   "gold": 30,  "items": ["miruvor","wolf_pelt"]}, "status": "available"})
    q.register("quest_orc",        {"name": t("quest_name_orc"),        "desc": t("quest_desc_orc"),        "type": "kill",   "target": "orc",            "required": 5,  "rewards": {"xp": 100,  "gold": 50,  "items": ["bow_galadhrim"]},        "status": "available"})
    q.register("quest_wolf",       {"name": t("quest_name_wolf"),       "desc": t("quest_desc_wolf"),       "type": "kill",   "target": "wolf",           "required": 5,  "rewards": {"xp": 80,   "gold": 40,  "items": ["elven_longbow"]},        "status": "available"})
    q.register("quest_collect",    {"name": t("quest_name_collect"),    "desc": t("quest_desc_collect"),    "type": "collect","target": "orc_blood",      "required": 3,  "rewards": {"xp": 80,   "gold": 40,  "items": ["miruvor","ent_draught"]}, "status": "available"})
    q.register("quest_explore",    {"name": t("quest_name_explore"),    "desc": t("quest_desc_explore"),    "type": "explore","target": "area",           "required": 3,
        "zones": [
            {"name": t("zone_fangorn"),  "scene": "fangorn",  "x1": 3, "y1": 3, "x2": 26, "y2": 26},
            {"name": t("zone_moria"),    "scene": "moria",    "x1": 3, "y1": 3, "x2": 26, "y2": 26},
            {"name": t("zone_mordor"),   "scene": "mordor",   "x1": 3, "y1": 3, "x2": 26, "y2": 26},
        ],
        "rewards": {"xp": 120, "gold": 60, "items": ["elven_brooch"]}, "status": "available"})
    q.register("quest_spider",     {"name": t("quest_name_spider"),     "desc": t("quest_desc_spider"),     "type": "kill",   "target": "spider",         "required": 6,  "rewards": {"xp": 100,  "gold": 55,  "items": ["mithril_helm"]},         "status": "available"})
    q.register("quest_boss",       {"name": t("quest_name_boss"),       "desc": t("quest_desc_boss"),       "type": "kill",   "target": "cave_troll",     "required": 1,  "rewards": {"xp": 300,  "gold": 150, "items": ["mithril_coat"]},         "status": "available"})
    q.register("quest_undead",     {"name": t("quest_name_undead"),     "desc": t("quest_desc_undead"),     "type": "kill",   "target": "undead",         "required": 5,  "rewards": {"xp": 200,  "gold": 100, "items": ["athelas","lembas_bread"]}, "status": "available"})
    q.register("quest_berserker",  {"name": t("quest_name_berserker"),  "desc": t("quest_desc_berserker"),  "type": "kill",   "target": "uruk_berserker", "required": 4,  "rewards": {"xp": 250,  "gold": 120, "items": ["anduril"]},              "status": "available"})
    q.register("quest_nazgul",     {"name": t("quest_name_nazgul"),     "desc": t("quest_desc_nazgul"),     "type": "kill",   "target": "nazgul",         "required": 1,  "rewards": {"xp": 400,  "gold": 200, "items": ["morgul_blade","ring_barahir"]}, "status": "available"})
    q.register("quest_escort",     {"name": t("quest_name_escort"),     "desc": t("quest_desc_escort"),     "type": "escort", "target": "frodo",          "required": 1,
        "escort_dest": (14, 14), "escort_radius": 3.0,
        "rewards": {"xp": 150,  "gold": 80,  "items": ["miruvor","lembas_bread"]}, "status": "available"})
    q.register("quest_timed",      {"name": t("quest_name_timed"),      "desc": t("quest_desc_timed"),      "type": "timed_kill","target": "uruk_archer", "required": 3,  "time_limit": 60,
        "rewards": {"xp": 150,  "gold": 100, "items": ["wizards_staff"]}, "status": "available"})
    q.register("quest_balrog",     {"name": t("quest_name_balrog"),     "desc": t("quest_desc_balrog"),     "type": "kill",   "target": "balrog",         "required": 1,  "rewards": {"xp": 1000, "gold": 500, "items": ["one_ring","phial_galadriel"]}, "status": "available"})
    return q


def _build_shops() -> ShopManager:
    s = ShopManager()
    s.register("general_shop",  ["miruvor","ent_draught","athelas","lembas_bread","ranger_cloak","elven_brooch"])
    s.register("weapon_shop",   ["sting","anduril","bow_galadhrim","wizards_staff","dark_blade","morgul_blade"])
    s.register("elrond_shop",   ["miruvor","lembas_bread","phial_galadriel","mithril_coat","mithril_helm","elven_longbow","ring_barahir","elven_brooch"])
    s.register("rohan_shop",    ["athelas","wolf_pelt","uruk_shield","sting","bow_galadhrim"])
    return s


# ── Helper ─────────────────────────────────────────────────
def _house(m, c1, r1, c2, r2, door_c, door_r):
    for c in range(c1, c2 + 1):
        m.set_tile(c, r1, TILE_HOUSE_WALL)
        m.set_tile(c, r2, TILE_HOUSE_WALL)
    for r in range(r1 + 1, r2):
        m.set_tile(c1, r, TILE_HOUSE_WALL)
        m.set_tile(c2, r, TILE_HOUSE_WALL)
    for r in range(r1 + 1, r2):
        for c in range(c1 + 1, c2):
            m.set_tile(c, r, TILE_ROOF)
    m.set_tile(door_c, door_r, TILE_DIRT)
