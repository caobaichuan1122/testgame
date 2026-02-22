# ============================================================
#  演示关卡构建器：60×60地图 + 全部实体 — 中土世界版
# ============================================================
from iso_map import (
    IsoMap, TILE_GRASS, TILE_GRASS2, TILE_DIRT, TILE_STONE, TILE_STONE2,
    TILE_WATER, TILE_WATER2, TILE_SAND, TILE_BRIDGE,
    TILE_TREE, TILE_WALL, TILE_CAVE, TILE_CLIFF,
)
from enemy import Enemy
from npc import NPC
from dialogue import DialogueManager
from quest import QuestManager
from shop import ShopManager
from i18n import t, tf
import random


def build_demo_level():
    """构建60×60演示关卡，返回 (iso_map, entities_data, dialogue_mgr, quest_mgr, shop_mgr)"""
    iso_map = IsoMap(60, 60)

    # ============================================================
    #  地形绘制
    # ============================================================

    # --- 基底：全部草地 ---
    iso_map.fill_rect(0, 0, 60, 60, TILE_GRASS)

    # --- 法贡森林 Fangorn Forest (左上 0-19, 0-19) ---
    iso_map.fill_rect(0, 0, 20, 20, TILE_GRASS2)
    for c in range(0, 20):
        iso_map.set_tile(c, 0, TILE_TREE)
    for r in range(0, 20):
        iso_map.set_tile(0, r, TILE_TREE)
    tree_positions = [
        (3, 3), (7, 2), (12, 5), (5, 8), (15, 3),
        (2, 14), (8, 12), (16, 8), (4, 17), (14, 16),
        (10, 10), (18, 12), (6, 15),
    ]
    for c, r in tree_positions:
        iso_map.set_tile(c, r, TILE_TREE)
    for r in range(2, 19):
        iso_map.set_tile(10, r, TILE_DIRT)
        iso_map.set_tile(11, r, TILE_DIRT)

    # --- 摩瑞亚矿洞 Mines of Moria (中上 20-39, 0-19) ---
    iso_map.fill_rect(20, 0, 40, 20, TILE_STONE)
    for c in range(20, 40):
        iso_map.set_tile(c, 0, TILE_WALL)
        iso_map.set_tile(c, 19, TILE_WALL)
    for r in range(0, 20):
        iso_map.set_tile(20, r, TILE_WALL)
        iso_map.set_tile(39, r, TILE_WALL)
    iso_map.set_tile(30, 19, TILE_STONE)
    iso_map.set_tile(29, 19, TILE_STONE)
    iso_map.fill_rect(22, 2, 38, 18, TILE_CAVE)
    for pos in [(25, 5), (35, 5), (25, 14), (35, 14), (30, 10)]:
        iso_map.set_tile(pos[0], pos[1], TILE_WALL)

    # --- 迷雾山脉 Misty Mountains (右上 40-59, 0-19) ---
    iso_map.fill_rect(40, 0, 60, 20, TILE_STONE2)
    for c in range(40, 60):
        iso_map.set_tile(c, 0, TILE_CLIFF)
    for r in range(0, 20):
        iso_map.set_tile(59, r, TILE_CLIFF)
    for pos in [(45, 5), (50, 3), (55, 8), (48, 12), (53, 15), (42, 10)]:
        iso_map.set_tile(pos[0], pos[1], TILE_CLIFF)

    # --- 洛汗平原西 Fields of Rohan West (左中 0-19, 20-39) ---
    iso_map.fill_rect(0, 20, 20, 40, TILE_GRASS)
    for r in range(20, 40):
        iso_map.set_tile(0, r, TILE_TREE)

    # --- 霍比屯 Hobbiton (中间 20-39, 20-39) ---
    iso_map.fill_rect(20, 20, 40, 40, TILE_DIRT)
    for c in range(20, 40):
        iso_map.set_tile(c, 30, TILE_STONE)
    for r in range(20, 40):
        iso_map.set_tile(30, r, TILE_STONE)
    iso_map.fill_rect(23, 23, 28, 27, TILE_WALL)
    iso_map.set_tile(25, 27, TILE_DIRT)
    iso_map.fill_rect(33, 23, 38, 27, TILE_WALL)
    iso_map.set_tile(35, 27, TILE_DIRT)
    iso_map.fill_rect(23, 33, 28, 37, TILE_WALL)
    iso_map.set_tile(25, 33, TILE_DIRT)

    # --- 洛汗平原东 Fields of Rohan East (右中 40-59, 20-39) ---
    iso_map.fill_rect(40, 20, 60, 40, TILE_GRASS)
    iso_map.fill_rect(40, 20, 60, 22, TILE_GRASS2)
    for r in range(20, 40):
        iso_map.set_tile(59, r, TILE_TREE)

    # --- 安都因河 Anduin River (左下 0-19, 40-59) ---
    iso_map.fill_rect(0, 40, 20, 60, TILE_WATER)
    iso_map.fill_rect(0, 40, 20, 42, TILE_GRASS2)
    iso_map.fill_rect(0, 58, 20, 60, TILE_GRASS2)
    iso_map.fill_rect(3, 45, 17, 55, TILE_WATER2)

    # --- 奥斯吉利亚斯桥 Osgiliath Bridge (中下 20-39, 40-59) ---
    iso_map.fill_rect(20, 40, 40, 60, TILE_GRASS)
    iso_map.fill_rect(20, 46, 40, 52, TILE_WATER)
    iso_map.fill_rect(28, 46, 32, 52, TILE_BRIDGE)

    # --- 魔多荒原 Mordor Wastes (右下 40-59, 40-59) ---
    iso_map.fill_rect(40, 40, 60, 60, TILE_SAND)
    for c in range(40, 60):
        iso_map.set_tile(c, 59, TILE_CLIFF)
    for r in range(40, 60):
        iso_map.set_tile(59, r, TILE_CLIFF)
    for pos in [(45, 45), (52, 48), (48, 55), (55, 52), (50, 43)]:
        iso_map.set_tile(pos[0], pos[1], TILE_CLIFF)

    # ============================================================
    #  实体
    # ============================================================
    enemies = []
    npcs = []

    # --- 古墓尸妖 Barrow-wights（法贡森林区）×5 ---
    wight_positions = [(5, 5), (8, 8), (14, 4), (6, 13), (16, 15)]
    for c, r in wight_positions:
        enemies.append(Enemy(c, r, "wight"))

    # --- BOSS 洞穴巨魔 Cave Troll（摩瑞亚矿洞）---
    boss = Enemy(30, 10, "cave_troll")
    enemies.append(boss)

    # --- 兽人 Orcs（洛汗平原东）×8 ---
    for i in range(8):
        c = random.randint(42, 57)
        r = random.randint(22, 37)
        e = Enemy(c, r, "orc")
        enemies.append(e)

    # --- 乌鲁克弓手 Uruk-hai Archers（魔多荒原）×6 ---
    uruk_positions = [
        (44, 44), (50, 46), (54, 50), (46, 54), (52, 56), (48, 48)
    ]
    for c, r in uruk_positions:
        enemies.append(Enemy(c, r, "uruk_archer"))

    # --- NPC ---
    gandalf = NPC(25, 28, name="Gandalf", npc_type="quest",
                  quest_ids=["quest_orc", "quest_boss"],
                  dialogue_id="gandalf_default",
                  color=(200, 160, 60),
                  behavior="wander", wander_radius=1.5,
                  idle_lines=[
                      t("idle_gandalf_1"),
                      t("idle_gandalf_2"),
                      t("idle_gandalf_3"),
                      t("idle_gandalf_4"),
                  ])
    npcs.append(gandalf)

    barliman = NPC(35, 28, name="Barliman", npc_type="shop",
                   shop_id="general_shop",
                   dialogue_id="barliman_default",
                   color=(100, 200, 100),
                   behavior="idle",
                   idle_lines=[
                       t("idle_barliman_1"),
                       t("idle_barliman_2"),
                       t("idle_barliman_3"),
                   ])
    npcs.append(barliman)

    gimli = NPC(25, 32, name="Gimli", npc_type="shop",
                shop_id="weapon_shop",
                dialogue_id="gimli_default",
                color=(200, 120, 80),
                behavior="wander", wander_radius=1.0,
                idle_lines=[
                    t("idle_gimli_1"),
                    t("idle_gimli_2"),
                    t("idle_gimli_3"),
                ])
    npcs.append(gimli)

    arwen = NPC(30, 28, name="Arwen", npc_type="quest",
                quest_ids=["quest_collect"],
                dialogue_id="arwen_default",
                color=(200, 100, 200),
                behavior="patrol",
                patrol_points=[(30, 28), (30, 32), (32, 30), (28, 30)],
                idle_lines=[
                    t("idle_arwen_1"),
                    t("idle_arwen_2"),
                    t("idle_arwen_3"),
                    t("idle_arwen_4"),
                ])
    npcs.append(arwen)

    boromir = NPC(30, 20, name="Boromir", npc_type="quest",
                  quest_ids=["quest_explore"],
                  dialogue_id="boromir_default",
                  color=(120, 140, 200),
                  behavior="patrol",
                  patrol_points=[(28, 20), (32, 20), (32, 22), (28, 22)],
                  idle_lines=[
                      t("idle_boromir_1"),
                      t("idle_boromir_2"),
                      t("idle_boromir_3"),
                      t("idle_boromir_4"),
                  ])
    npcs.append(boromir)

    frodo = NPC(45, 30, name="Frodo", npc_type="quest",
                quest_ids=["quest_escort"],
                dialogue_id="frodo_default",
                color=(180, 160, 120),
                behavior="wander", wander_radius=5.0,
                idle_lines=[
                    t("idle_frodo_1"),
                    t("idle_frodo_2"),
                    t("idle_frodo_3"),
                    t("idle_frodo_4"),
                ])
    npcs.append(frodo)

    sam = NPC(27, 46, name="Sam", npc_type="quest",
              quest_ids=["quest_timed"],
              dialogue_id="sam_default",
              color=(100, 160, 180),
              behavior="idle",
              idle_lines=[
                  t("idle_sam_1"),
                  t("idle_sam_2"),
                  t("idle_sam_3"),
                  t("idle_sam_4"),
              ])
    npcs.append(sam)

    # ============================================================
    #  对话系统
    # ============================================================
    dialogue_mgr = DialogueManager()

    # 甘道夫对话
    dialogue_mgr.register("gandalf_default", {
        "start": {
            "text": t("dlg_gandalf_default"),
            "options": [{"label": t("opt_ok"), "next": None}],
        }
    })

    dialogue_mgr.register("quest_orc_accept", {
        "start": {
            "text": t("dlg_quest_orc_accept"),
            "options": [{"label": t("opt_for_the_shire"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_orc_progress", {
        "start": {
            "text": t("dlg_quest_orc_progress"),
            "options": [{"label": t("opt_ok"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_orc_complete", {
        "start": {
            "text": t("dlg_quest_orc_complete"),
            "options": [{"label": t("opt_thanks"), "next": None}],
        }
    })

    dialogue_mgr.register("quest_boss_accept", {
        "start": {
            "text": t("dlg_quest_boss_accept"),
            "options": [{"label": t("opt_you_shall_not_pass"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_boss_progress", {
        "start": {
            "text": t("dlg_quest_boss_progress"),
            "options": [{"label": t("opt_ok"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_boss_complete", {
        "start": {
            "text": t("dlg_quest_boss_complete"),
            "options": [{"label": t("opt_thank_you"), "next": None}],
        }
    })

    # 酒馆老板对话
    dialogue_mgr.register("barliman_default", {
        "start": {
            "text": t("dlg_barliman_default"),
            "options": [
                {"label": t("opt_open_shop"), "next": None,
                 "callback": lambda g: g.ui.open_shop("general_shop")},
                {"label": t("opt_farewell"), "next": None},
            ],
        }
    })

    # 吉姆利对话（分支）
    dialogue_mgr.register("gimli_default", {
        "start": {
            "text": t("dlg_gimli_default"),
            "options": [
                {"label": t("opt_open_shop"), "next": None,
                 "callback": lambda g: g.ui.open_shop("weapon_shop")},
                {"label": t("opt_tell_weapons"), "next": "weapons_info"},
                {"label": t("opt_farewell"), "next": None},
            ],
        },
        "weapons_info": {
            "text": t("dlg_gimli_weapons_info"),
            "options": [
                {"label": t("opt_which_best"), "next": "best_weapon"},
                {"label": t("opt_open_shop"), "next": None,
                 "callback": lambda g: g.ui.open_shop("weapon_shop")},
                {"label": t("opt_thanks"), "next": None},
            ],
        },
        "best_weapon": {
            "text": t("dlg_gimli_best_weapon"),
            "options": [{"label": t("opt_got_it"), "next": None}],
        },
    })

    # 阿尔温对话
    def heal_player(game):
        p = game.entities.player
        if p:
            cost = 20
            if p.inventory.gold >= cost:
                p.inventory.gold -= cost
                p.stats.hp = p.stats.max_hp
                p.stats.mp = p.stats.max_mp
                p.add_message(t("fully_healed"))
                game.chat_log.add(t("healed_by_arwen"), "system")
            else:
                p.add_message(t("not_enough_gold_short"))

    dialogue_mgr.register("arwen_default", {
        "start": {
            "text": t("dlg_arwen_default"),
            "options": [
                {"label": t("opt_heal_me"), "next": "healed",
                 "callback": heal_player},
                {"label": t("opt_no_thanks"), "next": None},
            ],
        },
        "healed": {
            "text": t("dlg_arwen_healed"),
            "options": [{"label": t("opt_thanks"), "next": None}],
        },
    })

    # 收集任务对话
    dialogue_mgr.register("quest_collect_accept", {
        "start": {
            "text": t("dlg_quest_collect_accept"),
            "options": [{"label": t("opt_ill_gather"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_collect_progress", {
        "start": {
            "text": t("dlg_quest_collect_progress"),
            "options": [{"label": t("opt_on_it"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_collect_complete", {
        "start": {
            "text": t("dlg_quest_collect_complete"),
            "options": [{"label": t("opt_thanks"), "next": None}],
        }
    })

    # 博罗米尔对话
    dialogue_mgr.register("boromir_default", {
        "start": {
            "text": t("dlg_boromir_default"),
            "options": [
                {"label": t("opt_what_lies_beyond"), "next": "area_info"},
                {"label": t("opt_just_passing"), "next": None},
            ],
        },
        "area_info": {
            "text": t("dlg_boromir_area_info"),
            "options": [
                {"label": t("opt_got_it"), "next": None},
            ],
        },
    })

    # 探索任务对话
    dialogue_mgr.register("quest_explore_accept", {
        "start": {
            "text": t("dlg_quest_explore_accept"),
            "options": [{"label": t("opt_for_gondor"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_explore_progress", {
        "start": {
            "text": t("dlg_quest_explore_progress"),
            "options": [{"label": t("opt_not_yet"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_explore_complete", {
        "start": {
            "text": t("dlg_quest_explore_complete"),
            "options": [{"label": t("opt_thank_you"), "next": None}],
        }
    })

    # 弗罗多对话
    dialogue_mgr.register("frodo_default", {
        "start": {
            "text": t("dlg_frodo_default"),
            "options": [
                {"label": t("opt_any_tips"), "next": "tips"},
                {"label": t("opt_safe_travels"), "next": None},
            ],
        },
        "tips": {
            "text": t("dlg_frodo_tips"),
            "options": [{"label": t("opt_thanks"), "next": None}],
        },
    })

    # 护送任务对话
    dialogue_mgr.register("quest_escort_accept", {
        "start": {
            "text": t("dlg_quest_escort_accept"),
            "options": [{"label": t("opt_follow_me"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_escort_progress", {
        "start": {
            "text": t("dlg_quest_escort_progress"),
            "options": [{"label": t("opt_almost_there"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_escort_complete", {
        "start": {
            "text": t("dlg_quest_escort_complete"),
            "options": [{"label": t("opt_glad_to_help"), "next": None}],
        }
    })

    # 山姆对话
    dialogue_mgr.register("sam_default", {
        "start": {
            "text": t("dlg_sam_default"),
            "options": [
                {"label": t("opt_tell_more"), "next": "mordor_info"},
                {"label": t("opt_good_luck_sam"), "next": None},
            ],
        },
        "mordor_info": {
            "text": t("dlg_sam_mordor_info"),
            "options": [{"label": t("opt_i_see"), "next": None}],
        },
    })

    # 限时任务对话
    dialogue_mgr.register("quest_timed_accept", {
        "start": {
            "text": t("dlg_quest_timed_accept"),
            "options": [{"label": t("opt_im_on_it"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_timed_progress", {
        "start": {
            "text": t("dlg_quest_timed_progress"),
            "options": [{"label": t("opt_im_going"), "next": None}],
        }
    })
    dialogue_mgr.register("quest_timed_complete", {
        "start": {
            "text": t("dlg_quest_timed_complete"),
            "options": [{"label": t("opt_thanks"), "next": None}],
        }
    })

    # ============================================================
    #  任务系统
    # ============================================================
    quest_mgr = QuestManager()

    quest_mgr.register("quest_orc", {
        "name": t("quest_name_orc"),
        "desc": t("quest_desc_orc"),
        "type": "kill",
        "target": "orc",
        "required": 5,
        "rewards": {"xp": 100, "gold": 50, "items": ["bow_galadhrim"]},
        "status": "available",
    })

    quest_mgr.register("quest_boss", {
        "name": t("quest_name_boss"),
        "desc": t("quest_desc_boss"),
        "type": "kill",
        "target": "cave_troll",
        "required": 1,
        "rewards": {"xp": 300, "gold": 150, "items": ["mithril_coat"]},
        "status": "available",
    })

    quest_mgr.register("quest_collect", {
        "name": t("quest_name_collect"),
        "desc": t("quest_desc_collect"),
        "type": "collect",
        "target": "orc_blood",
        "required": 3,
        "rewards": {"xp": 80, "gold": 40, "items": ["miruvor", "ent_draught"]},
        "status": "available",
    })

    quest_mgr.register("quest_explore", {
        "name": t("quest_name_explore"),
        "desc": t("quest_desc_explore"),
        "type": "explore",
        "target": "area",
        "required": 3,
        "zones": [
            {"name": t("zone_fangorn"), "x1": 2, "y1": 2, "x2": 18, "y2": 18},
            {"name": t("zone_moria"), "x1": 22, "y1": 2, "x2": 38, "y2": 18},
            {"name": t("zone_mordor"), "x1": 42, "y1": 42, "x2": 58, "y2": 58},
        ],
        "rewards": {"xp": 120, "gold": 60, "items": ["elven_brooch"]},
        "status": "available",
    })

    quest_mgr.register("quest_escort", {
        "name": t("quest_name_escort"),
        "desc": t("quest_desc_escort"),
        "type": "escort",
        "target": "frodo",
        "required": 1,
        "escort_dest": (30, 30),
        "escort_radius": 3.0,
        "rewards": {"xp": 100, "gold": 80, "items": ["miruvor"]},
        "status": "available",
    })

    quest_mgr.register("quest_timed", {
        "name": t("quest_name_timed"),
        "desc": t("quest_desc_timed"),
        "type": "timed_kill",
        "target": "uruk_archer",
        "required": 3,
        "time_limit": 60,
        "rewards": {"xp": 150, "gold": 100, "items": ["wizards_staff"]},
        "status": "available",
    })

    # ============================================================
    #  商店系统
    # ============================================================
    shop_mgr = ShopManager()

    shop_mgr.register("general_shop", [
        "miruvor", "ent_draught", "ranger_cloak",
        "ring_barahir", "elven_brooch",
    ])

    shop_mgr.register("weapon_shop", [
        "sting", "anduril", "bow_galadhrim", "wizards_staff",
    ])

    # ============================================================
    #  返回
    # ============================================================
    return {
        "iso_map": iso_map,
        "enemies": enemies,
        "npcs": npcs,
        "dialogue_mgr": dialogue_mgr,
        "quest_mgr": quest_mgr,
        "shop_mgr": shop_mgr,
        "player_start": (30, 30),
    }
