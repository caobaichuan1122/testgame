# ============================================================
#  Turn-based combat scene manager
# ============================================================
import math
import random
import pygame
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_HP, COLOR_MP, COLOR_UI, COLOR_ACCENT, COLOR_GOLD,
    COMBAT_MELEE, COMBAT_RANGED, COMBAT_MAGIC,
    MELEE_BASE_DMG, RANGED_BASE_DMG, MAGIC_BASE_DMG, MAGIC_COST,
)
from systems.combat import calc_damage, check_crit
from systems.inventory import ITEMS
from systems.i18n import t, tf, get_item_name
from core.utils import draw_bar, draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD, FONT_UI_LG


# --- Combat phases ---
PHASE_INTRO = "intro"            # Combat start animation
PHASE_PLAYER_CHOOSE = "player_choose"  # Player chooses action
PHASE_PLAYER_ACT = "player_act"  # Player action animation
PHASE_ENEMY_ACT = "enemy_act"    # Enemy action animation
PHASE_CHECK_END = "check_end"    # Check win/loss
PHASE_WIN = "win"                # Victory
PHASE_LOSE = "lose"              # Defeat
PHASE_FLEE = "flee"              # Flee success

# --- Menu levels ---
MENU_MAIN = "main"
MENU_SKILL = "skill"
MENU_ITEM = "item"

# Internal option IDs (not translated)
MAIN_OPT_IDS = ["Attack", "Defend", "Skill", "Item", "Flee"]
MAIN_OPT_KEYS = ["opt_attack", "opt_defend", "opt_skill", "opt_item", "opt_flee"]

SKILL_DEFS = [
    {"id": "slash", "name_key": "skill_slash", "short_key": "skill_slash_short",
     "mode": COMBAT_MELEE, "cost": 0},
    {"id": "shot", "name_key": "skill_shot", "short_key": "skill_shot_short",
     "mode": COMBAT_RANGED, "cost": 0},
    {"id": "magic", "name_key": "skill_magic", "short_key": "skill_magic_short",
     "mode": COMBAT_MAGIC, "cost": MAGIC_COST},
]


class CombatScene:
    def __init__(self):
        self.active = False
        self.player = None
        self.enemy = None
        self.game = None

        # Round
        self.round_num = 0
        self.phase = PHASE_INTRO
        self.phase_timer = 0

        # Menu
        self.menu_level = MENU_MAIN
        self.cursor = 0
        self.item_list = []   # Currently available consumable list
        self.item_cursor = 0

        # Combat log
        self.log = []  # [(text, color), ...]

        # Animation
        self.anim_timer = 0
        self.player_flash = 0
        self.enemy_flash = 0
        self.player_defending = False

        # Results
        self.combat_finished = False
        self.result = None  # "win", "lose", "flee"

        # Visual state
        self._tick = 0
        self._player_lunge = 0.0
        self._enemy_lunge = 0.0
        self._particles = []
        self._damage_floats = []
        self._shake = [0, 0]
        self._pending_floats = []   # [(text, target, color)]
        self._pending_hits = []     # [(target, effect_type)]

    def start(self, player, enemy, game):
        self.active = True
        self.player = player
        self.enemy = enemy
        self.game = game

        self.round_num = 1
        self.phase = PHASE_INTRO
        self.phase_timer = 60  # 1 second intro

        self.menu_level = MENU_MAIN
        self.cursor = 0
        self.item_cursor = 0

        self.log = []
        self.player_flash = 0
        self.enemy_flash = 0
        self.player_defending = False
        self.combat_finished = False
        self.result = None

        self._tick = 0
        self._player_lunge = 0.0
        self._enemy_lunge = 0.0
        self._particles = []
        self._damage_floats = []
        self._shake = [0, 0]
        self._pending_floats = []
        self._pending_hits = []

        name = getattr(self.enemy, 'enemy_type', 'enemy').replace('_', ' ').title()
        self.log.append((tf("wild_appears", name=name), COLOR_UI))

    def handle_key(self, key):
        if self.phase == PHASE_PLAYER_CHOOSE:
            self._handle_menu_key(key)
        elif self.phase == PHASE_WIN:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.combat_finished = True
                self.result = "win"
        elif self.phase == PHASE_LOSE:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.combat_finished = True
                self.result = "lose"
        elif self.phase == PHASE_FLEE:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.combat_finished = True
                self.result = "flee"

    def _handle_menu_key(self, key):
        if self.menu_level == MENU_MAIN:
            if key in (pygame.K_w, pygame.K_UP):
                self.cursor = (self.cursor - 1) % len(MAIN_OPT_IDS)
            elif key in (pygame.K_s, pygame.K_DOWN):
                self.cursor = (self.cursor + 1) % len(MAIN_OPT_IDS)
            elif key in (pygame.K_a, pygame.K_LEFT):
                if self.cursor >= 1:
                    self.cursor = max(0, self.cursor - 1)
            elif key in (pygame.K_d, pygame.K_RIGHT):
                if self.cursor < len(MAIN_OPT_IDS) - 1:
                    self.cursor = min(len(MAIN_OPT_IDS) - 1, self.cursor + 1)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_j):
                self._select_main_option()
            elif key == pygame.K_ESCAPE:
                pass

        elif self.menu_level == MENU_SKILL:
            if key in (pygame.K_w, pygame.K_UP):
                self.cursor = (self.cursor - 1) % len(SKILL_DEFS)
            elif key in (pygame.K_s, pygame.K_DOWN):
                self.cursor = (self.cursor + 1) % len(SKILL_DEFS)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_j):
                self._select_skill()
            elif key == pygame.K_ESCAPE:
                self.menu_level = MENU_MAIN
                self.cursor = 2

        elif self.menu_level == MENU_ITEM:
            if len(self.item_list) > 0:
                if key in (pygame.K_w, pygame.K_UP):
                    self.item_cursor = (self.item_cursor - 1) % len(self.item_list)
                elif key in (pygame.K_s, pygame.K_DOWN):
                    self.item_cursor = (self.item_cursor + 1) % len(self.item_list)
                elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_j):
                    self._select_item()
            if key == pygame.K_ESCAPE:
                self.menu_level = MENU_MAIN
                self.cursor = 3

    def _select_main_option(self):
        opt = MAIN_OPT_IDS[self.cursor]
        if opt == "Attack":
            self._do_player_attack()
        elif opt == "Defend":
            self._do_player_defend()
        elif opt == "Skill":
            self.menu_level = MENU_SKILL
            self.cursor = 0
        elif opt == "Item":
            self._build_item_list()
            if len(self.item_list) == 0:
                self.log.append((t("no_usable_items"), COLOR_ACCENT))
            else:
                self.menu_level = MENU_ITEM
                self.item_cursor = 0
        elif opt == "Flee":
            self._do_flee()

    def _build_item_list(self):
        self.item_list = []
        for slot in self.player.inventory.items:
            item_data = ITEMS.get(slot["id"])
            if item_data and item_data["type"] == "consumable":
                self.item_list.append({
                    "id": slot["id"],
                    "name": get_item_name(slot["id"]),
                    "count": slot["count"],
                    "data": item_data,
                })

    # ---- Player actions ----

    def _do_player_attack(self):
        dmg, is_crit = self._calc_player_damage(COMBAT_MELEE)
        self.enemy.stats.take_damage(dmg)
        self.enemy_flash = 15
        self.enemy.take_hit()
        self._pending_floats.append((str(dmg), "enemy", (255, 80, 80) if is_crit else (255, 230, 80)))
        self._pending_hits.append(("enemy", "magic" if False else "melee"))
        self._shake = [5, 3]

        if is_crit:
            msg = tf("crit_attack_for_dmg", dmg=dmg)
        else:
            msg = tf("attack_for_dmg", dmg=dmg)
        self.log.append((msg, (255, 255, 200)))

        self.phase = PHASE_PLAYER_ACT
        self.anim_timer = 30

    def _do_player_defend(self):
        self.player_defending = True
        self.log.append((t("defend_stance"), (100, 200, 255)))
        self.phase = PHASE_PLAYER_ACT
        self.anim_timer = 20

    def _select_skill(self):
        skill = SKILL_DEFS[self.cursor]
        mode = skill["mode"]
        cost = skill["cost"]

        if cost > 0 and self.player.stats.mp < cost:
            self.log.append((t("not_enough_mp"), COLOR_ACCENT))
            return

        if cost > 0:
            self.player.stats.use_mp(cost)

        dmg, is_crit = self._calc_player_damage(mode)
        self.enemy.stats.take_damage(dmg)
        self.enemy_flash = 15
        self.enemy.take_hit()
        effect = "magic" if mode == COMBAT_MAGIC else ("ranged" if mode == COMBAT_RANGED else "melee")
        self._pending_floats.append((str(dmg), "enemy", (180, 100, 255) if mode == COMBAT_MAGIC else (255, 230, 80)))
        self._pending_hits.append(("enemy", effect))
        self._shake = [5, 3]

        skill_name = t(skill["short_key"])
        if is_crit:
            msg = tf("crit_skill_deals_dmg", skill=skill_name, dmg=dmg)
        else:
            msg = tf("skill_deals_dmg", skill=skill_name, dmg=dmg)
        if cost > 0:
            msg += tf("mp_cost_suffix", cost=cost)
        self.log.append((msg, (255, 255, 200)))

        self.menu_level = MENU_MAIN
        self.cursor = 0
        self.phase = PHASE_PLAYER_ACT
        self.anim_timer = 30

    def _select_item(self):
        if not self.item_list:
            return
        item = self.item_list[self.item_cursor]
        used = self.player.inventory.use_item(item["id"], self.player.stats)
        if used:
            desc_parts = []
            if "heal" in item["data"]:
                desc_parts.append(f"+{item['data']['heal']} HP")
            if "restore_mp" in item["data"]:
                desc_parts.append(f"+{item['data']['restore_mp']} MP")
            desc = ", ".join(desc_parts) if desc_parts else t("used_fallback")
            self.log.append((tf("used_item_desc", name=item['name'], desc=desc), (100, 255, 100)))

            self.menu_level = MENU_MAIN
            self.cursor = 0
            self.phase = PHASE_PLAYER_ACT
            self.anim_timer = 20
        else:
            self.log.append((t("cannot_use_item"), COLOR_ACCENT))

    def _do_flee(self):
        if getattr(self.enemy, 'is_boss', False):
            self.log.append((t("cannot_flee_boss"), COLOR_ACCENT))
            return

        if random.random() < 0.5:
            self.log.append((t("fled_success"), (100, 255, 100)))
            self.phase = PHASE_FLEE
            self.anim_timer = 40
        else:
            self.log.append((t("fled_fail"), COLOR_ACCENT))
            self.phase = PHASE_PLAYER_ACT
            self.anim_timer = 20

    def _calc_player_damage(self, mode):
        p = self.player
        weapon_bonus = 0
        equipped = p.inventory.get_equipped_weapon()
        if equipped:
            weapon_bonus = equipped.get("bonus", 0)

        if mode == COMBAT_MELEE:
            base = MELEE_BASE_DMG
            stat_bonus = p.stats.str * 2
        elif mode == COMBAT_RANGED:
            base = RANGED_BASE_DMG
            stat_bonus = p.stats.dex * 2
        else:
            base = MAGIC_BASE_DMG
            stat_bonus = p.stats.int * 2

        # Equipment stat bonus
        stat_bonus += p.inventory.get_stat_bonus("str" if mode == COMBAT_MELEE
                                                  else "dex" if mode == COMBAT_RANGED
                                                  else "int") * 2

        dmg = calc_damage(base, stat_bonus, weapon_bonus, self.enemy.stats.def_)
        is_crit = check_crit(p.stats.dex)
        if is_crit:
            dmg = int(dmg * 1.5)
        return dmg, is_crit

    # ---- Enemy AI ----

    def _enemy_act(self):
        e = self.enemy
        if not e.stats.alive:
            return

        hp_ratio = e.stats.hp / e.stats.max_hp
        if hp_ratio < 0.3 and random.random() < 0.5:
            self.log.append((tf("enemy_defend", name=self._enemy_name()), (200, 200, 255)))
        else:
            raw_dmg = e.atk_damage
            if self.player_defending:
                raw_dmg = max(1, raw_dmg // 2)
            equip_def = self.player.inventory.get_total_defense()
            total_def = self.player.stats.def_ + equip_def
            actual = max(1, raw_dmg - int(total_def * 0.8))
            self.player.stats.hp = max(0, self.player.stats.hp - actual)
            self.player_flash = 15
            self._pending_floats.append((str(actual), "player", (255, 120, 120)))
            self._pending_hits.append(("player", "melee"))
            self._shake = [7, 5]

            self.log.append((tf("enemy_attacks", name=self._enemy_name(), dmg=actual),
                             (255, 150, 150)))

    def _enemy_name(self):
        return getattr(self.enemy, 'enemy_type', 'enemy').replace('_', ' ').title()

    # ---- Update ----

    def update(self):
        if not self.active:
            return

        if self.player_flash > 0:
            self.player_flash -= 1
        if self.enemy_flash > 0:
            self.enemy_flash -= 1

        if self.phase == PHASE_INTRO:
            self.phase_timer -= 1
            if self.phase_timer <= 0:
                self.phase = PHASE_PLAYER_CHOOSE
                self.menu_level = MENU_MAIN
                self.cursor = 0

        elif self.phase == PHASE_PLAYER_ACT:
            self.anim_timer -= 1
            if self.anim_timer <= 0:
                self.phase = PHASE_CHECK_END

        elif self.phase == PHASE_CHECK_END:
            if not self.enemy.stats.alive:
                self.log.append((t("victory"), (255, 215, 0)))
                self._grant_rewards()
                self.phase = PHASE_WIN
                self.anim_timer = 0
            elif not self.player.stats.alive:
                self.log.append((t("defeated"), COLOR_ACCENT))
                self.phase = PHASE_LOSE
                self.anim_timer = 0
            else:
                self.phase = PHASE_ENEMY_ACT
                self.anim_timer = 30
                self._enemy_act()

        elif self.phase == PHASE_ENEMY_ACT:
            self.anim_timer -= 1
            if self.anim_timer <= 0:
                if not self.player.stats.alive:
                    self.log.append((t("defeated"), COLOR_ACCENT))
                    self.phase = PHASE_LOSE
                else:
                    self.round_num += 1
                    self.player_defending = False
                    self.phase = PHASE_PLAYER_CHOOSE
                    self.menu_level = MENU_MAIN
                    self.cursor = 0

        elif self.phase == PHASE_FLEE:
            self.anim_timer -= 1
            if self.anim_timer <= 0:
                self.combat_finished = True
                self.result = "flee"

        self._tick += 1
        # Lunge animation fractions
        if self.phase == PHASE_PLAYER_ACT and self.anim_timer > 0:
            r = self.anim_timer / 30.0
            self._player_lunge = 1.0 - abs(r * 2 - 1.0)
        else:
            self._player_lunge = 0.0
        if self.phase == PHASE_ENEMY_ACT and self.anim_timer > 0:
            r = self.anim_timer / 30.0
            self._enemy_lunge = 1.0 - abs(r * 2 - 1.0)
        else:
            self._enemy_lunge = 0.0
        # Particles
        for p in self._particles:
            p["x"] += p["vx"];  p["y"] += p["vy"]
            p["vy"] += 0.35;    p["life"] -= 1
        self._particles = [p for p in self._particles if p["life"] > 0]
        # Damage floats
        for df in self._damage_floats:
            df["y"] += df["vy"];  df["timer"] -= 1
        self._damage_floats = [df for df in self._damage_floats if df["timer"] > 0]
        # Screen shake decay
        self._shake[0] = int(self._shake[0] * 0.60)
        self._shake[1] = int(self._shake[1] * 0.60)

    def _grant_rewards(self):
        self.player._on_enemy_kill(self.enemy, self.game)
        xp = self.enemy.xp_reward
        gold = self.enemy.gold_reward
        self.log.append((tf("xp_gold_reward", xp=xp, gold=gold), COLOR_GOLD))

    # ---- Draw ---------------------------------------------------------------

    def draw(self, screen):
        if not self.active:
            return

        sw, sh = screen.get_size()
        panel_y = sh * 2 // 3
        s = max(10, sh // 45)   # base sprite scale unit

        # Character anchor positions
        enemy_cx = int(sw * 0.64)
        enemy_cy = int(panel_y * 0.54)
        player_cx = int(sw * 0.27)
        player_cy = int(panel_y - s * 0.5)

        # Apply lunge offsets
        p_lunge_dx = int(self._player_lunge * s * 10)
        e_lunge_dx = int(self._enemy_lunge * s * 8)
        p_draw_cx = player_cx + p_lunge_dx
        e_draw_cx = enemy_cx - e_lunge_dx

        # Consume pending effects (now we know screen positions)
        for text, target, color in self._pending_floats:
            x = e_draw_cx if target == "enemy" else p_draw_cx
            y = (enemy_cy - s * 8) if target == "enemy" else (player_cy - s * 8)
            self._damage_floats.append({
                "text": text, "x": float(x), "y": float(y),
                "vy": -2.8, "timer": 55, "color": color,
            })
        self._pending_floats.clear()

        for target, etype in self._pending_hits:
            x = e_draw_cx if target == "enemy" else p_draw_cx
            y = (enemy_cy - s * 5) if target == "enemy" else (player_cy - s * 5)
            self._spawn_particles(x, y, etype)
        self._pending_hits.clear()

        # Apply screen shake offset
        ox, oy = self._shake[0], self._shake[1]

        # Draw everything
        self._draw_background(screen, sw, sh, panel_y, ox, oy)
        self._draw_entities(screen, sw, sh, panel_y, s,
                            enemy_cx, enemy_cy, e_draw_cx,
                            player_cx, player_cy, p_draw_cx,
                            ox, oy)
        self._draw_particles_layer(screen, ox, oy)
        self._draw_damage_floats_layer(screen)
        self._draw_bottom_panel(screen, sw, sh, panel_y)
        self._draw_phase_overlay(screen, sw, sh, panel_y)
    # ---- Background ---------------------------------------------------------

    def _draw_background(self, surf, sw, sh, panel_y, ox, oy):
        # Sky - 4 gradient bands
        bands = [
            (0.00, (8,  6, 16)),
            (0.25, (10, 8, 22)),
            (0.55, (14,11, 28)),
            (0.80, (18,14, 32)),
            (1.00, (22,18, 36)),
        ]
        for i in range(len(bands) - 1):
            ya = int((sh * 2 // 3) * bands[i][0])
            yb = int((sh * 2 // 3) * bands[i + 1][0])
            pygame.draw.rect(surf, bands[i + 1][1], (ox, oy + ya, sw, yb - ya + 1))

        floor_y = panel_y - 4 + oy

        # Distant mountain range (2 layers)
        import random as _r
        for layer in range(2, 0, -1):
            rng = _r.Random(layer * 17)
            n = 14
            dark = (10 + layer * 4, 8 + layer * 3, 18 + layer * 5)
            pts = [(ox + 0, floor_y + oy), (ox + sw, floor_y + oy)]
            ybase = int(panel_y * (0.55 + layer * 0.05))
            for i in range(n + 1):
                x = ox + int(sw * i / n)
                y = oy + ybase - rng.randint(0, int(panel_y * 0.28))
                pts.insert(-1, (x, y))
            pygame.draw.polygon(surf, dark, pts)

        # Torchlight glow spots on floor
        glow_surf = pygame.Surface((sw, 60), pygame.SRCALPHA)
        for gx in [int(sw * 0.27), int(sw * 0.64)]:
            for r2, a2 in [(80, 18), (50, 30), (25, 45)]:
                pygame.draw.ellipse(glow_surf, (200, 160, 80, a2),
                                    (gx - r2, 20, r2 * 2, 30))
        surf.blit(glow_surf, (ox, floor_y - 20 + oy))

        # Stone floor strip
        pygame.draw.rect(surf, (22, 19, 30),
                         (ox, floor_y, sw, 8))
        # Floor crack lines (perspective)
        for i in range(7):
            x = int(sw * i / 6)
            pygame.draw.line(surf, (30, 26, 40),
                             (ox + sw // 2, floor_y + oy),
                             (ox + x, floor_y + 8 + oy), 1)

        # Horizontal fog/mist near floor
        mist = pygame.Surface((sw, 30), pygame.SRCALPHA)
        mist.fill((60, 55, 80, 28))
        surf.blit(mist, (ox, floor_y - 12 + oy))
    # ---- Entities -----------------------------------------------------------

    def _draw_entities(self, surf, sw, sh, panel_y, s,
                       enemy_cx, enemy_cy, e_draw_cx,
                       player_cx, player_cy, p_draw_cx,
                       ox, oy):
        ex = e_draw_cx + ox
        ey = enemy_cy + oy
        px = p_draw_cx + ox
        py = player_cy + oy

        # Enemy sprite
        e_alive = self.enemy.stats.alive
        e_flash = self.enemy_flash > 0 and self.enemy_flash % 4 < 2
        self._draw_enemy_sprite(surf, ex, ey, s, e_flash, e_alive)

        # Enemy info (name + HP bar above sprite)
        self._draw_enemy_info(surf, enemy_cx + ox, enemy_cy + oy, s)

        # Player sprite
        p_flash = self.player_flash > 0 and self.player_flash % 4 < 2
        self._draw_player_sprite(surf, px, py, s, p_flash, self.player_defending)

        # Player info (bottom-left corner of battle area)
        self._draw_player_info(surf, sw, sh, panel_y, s, ox, oy)

        # Round indicator
        font_sm = get_font(FONT_UI_SM)
        draw_text(surf, tf("round_num", n=self.round_num),
                  sw - ui(30) + ox, ui(3) + oy, font_sm, (150, 150, 180))
    # ---- Player sprite ------------------------------------------------------

    def _draw_player_sprite(self, surf, cx, cy, s, flash, defending):
        # Shadow
        pygame.draw.ellipse(surf, (18, 15, 26),
                            (cx - s * 3, cy - s, s * 6, s * 2))

        body_c  = (255, 180, 160) if flash else (70, 110, 170)
        dark_c  = (255, 100, 80)  if flash else (40,  70, 120)
        skin_c  = (255, 200, 160)
        helm_c  = (60, 75, 110)
        sword_c = (200, 225, 255)
        eye_c   = (120, 200, 255)

        # Cape (triangle behind body)
        cape_pts = [
            (cx + s, cy - s * 3),
            (cx - s * 2, cy - s * 8),
            (cx - s * 4, cy - s * 2),
        ]
        pygame.draw.polygon(surf, (30, 40, 80), cape_pts)

        # Legs
        leg_top = cy - s * 3
        pygame.draw.polygon(surf, dark_c, [
            (cx - s * 2, leg_top), (cx - s, leg_top),
            (cx - s, cy), (cx - s * 2 - s // 2, cy),
        ])
        pygame.draw.polygon(surf, body_c, [
            (cx,      leg_top), (cx + s, leg_top),
            (cx + s + s // 3, cy), (cx, cy),
        ])

        # Torso
        pygame.draw.rect(surf, body_c,
                         (cx - s * 2, cy - s * 7, s * 4, s * 4))
        # Shoulder plates
        pygame.draw.polygon(surf, dark_c, [
            (cx - s * 2, cy - s * 7),
            (cx - s * 4, cy - s * 6),
            (cx - s * 3, cy - s * 5),
            (cx - s * 2, cy - s * 5),
        ])
        pygame.draw.polygon(surf, dark_c, [
            (cx + s * 2, cy - s * 7),
            (cx + s * 4, cy - s * 6),
            (cx + s * 3, cy - s * 5),
            (cx + s * 2, cy - s * 5),
        ])

        # Left arm
        if defending:
            shield_pts = [
                (cx - s * 3, cy - s * 6 + s // 2),
                (cx - s * 2, cy - s * 7),
                (cx - s,     cy - s * 6 + s // 2),
                (cx - s,     cy - s * 4),
                (cx - s * 2, cy - s * 3 + s // 2),
            ]
            pygame.draw.polygon(surf, (80, 120, 200), shield_pts)
            pygame.draw.polygon(surf, (160, 200, 255), shield_pts, max(1, s // 5))
        else:
            pygame.draw.line(surf, body_c,
                             (cx - s * 2, cy - s * 6),
                             (cx - s * 4, cy - s * 4), max(2, s // 4))

        # Right arm + sword
        arm_ex = cx + s * 5
        arm_ey = cy - s * 5 - s // 2
        pygame.draw.line(surf, body_c,
                         (cx + s * 2, cy - s * 6),
                         (arm_ex, arm_ey), max(2, s // 4))
        # Sword
        tip_x = arm_ex + s * 5
        tip_y = arm_ey - s * 5
        pygame.draw.polygon(surf, sword_c, [
            (arm_ex - s // 3, arm_ey + s // 3),
            (arm_ex + s // 3, arm_ey - s // 3),
            (tip_x + s // 3, tip_y - s // 3),
            (tip_x - s // 3, tip_y + s // 3),
        ])
        # Guard
        pygame.draw.line(surf, (150, 160, 190),
                         (arm_ex - s, arm_ey - s),
                         (arm_ex + s, arm_ey + s), max(2, s // 4))

        # Head
        head_cy = cy - s * 8
        pygame.draw.circle(surf, skin_c, (cx, head_cy), int(s * 1.3))
        # Helmet
        helm_pts = [
            (cx - s * 2, head_cy + s // 2),
            (cx - s,     head_cy - s * 2),
            (cx + s,     head_cy - s * 2),
            (cx + s + s // 2, head_cy - s),
            (cx + s * 2, head_cy + s // 2),
        ]
        pygame.draw.polygon(surf, helm_c, helm_pts)
        # Visor slit
        pygame.draw.line(surf, eye_c,
                         (cx - s + s // 3, head_cy - s // 4),
                         (cx + s - s // 3, head_cy - s // 4),
                         max(1, s // 5))
    # ---- Enemy sprite -------------------------------------------------------

    def _draw_enemy_sprite(self, surf, cx, cy, s, flash, alive):
        etype = getattr(self.enemy, "enemy_type", "orc").lower()
        base_color = self.enemy.color
        if flash:
            e_color = (255, 255, 255)
        elif not alive:
            e_color = tuple(max(0, c // 4) for c in base_color)
        else:
            e_color = base_color

        # Glow aura (pulsing)
        pulse = 0.5 + 0.5 * math.sin(self._tick * 0.08)
        glow_r = int(s * (4.5 + pulse * 1.5))
        glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
        for r2, a2 in [(glow_r, 18), (glow_r * 2 // 3, 28), (glow_r // 3, 35)]:
            gc = tuple(min(255, int(c * 1.3)) for c in base_color)
            pygame.draw.circle(glow_surf, gc + (a2,), (glow_r + 2, glow_r + 2), r2)
        surf.blit(glow_surf, (cx - glow_r - 2, cy - s * 6 - glow_r - 2))

        # Shadow
        pygame.draw.ellipse(surf, (16, 13, 22),
                            (cx - s * 4, cy - s, s * 8, s * 2))

        # Type-specific body
        bob = int(math.sin(self._tick * 0.07) * s * 0.5)

        if "troll" in etype:
            self._draw_troll(surf, cx, cy + bob, s, e_color, alive)
        elif "wight" in etype:
            self._draw_wight(surf, cx, cy + bob, s, e_color, alive)
        elif "uruk" in etype:
            self._draw_uruk(surf, cx, cy + bob, s, e_color, alive)
        else:
            # Default orc/generic enemy
            self._draw_orc(surf, cx, cy + bob, s, e_color, alive)

    def _draw_orc(self, surf, cx, cy, s, color, alive):
        dark = tuple(max(0, c - 40) for c in color)
        # Legs (stocky)
        pygame.draw.rect(surf, dark,
                         (cx - s * 3, cy - s * 4, s * 2 + s // 2, s * 4))
        pygame.draw.rect(surf, color,
                         (cx + s // 2, cy - s * 4, s * 2 + s // 2, s * 4))
        # Wide body
        pygame.draw.ellipse(surf, color,
                            (cx - s * 4, cy - s * 10, s * 8, s * 7))
        # Spiky shoulders
        for side in (-1, 1):
            pts = [
                (cx + side * s * 3, cy - s * 9),
                (cx + side * s * 6, cy - s * 11),
                (cx + side * s * 5, cy - s * 8),
            ]
            pygame.draw.polygon(surf, dark, pts)
        # Head
        pygame.draw.circle(surf, color, (cx, int(cy - s * 11)), int(s * 2))
        # Eyes (red)
        for dx in (-s // 2, s // 2):
            pygame.draw.circle(surf, (255, 50, 0), (cx + dx, cy - s * 11), max(2, s // 4))
        # Weapon arm
        pygame.draw.line(surf, dark,
                         (cx + s * 4, cy - s * 8),
                         (cx + s * 7, cy - s * 5), max(3, s // 3))
        pygame.draw.polygon(surf, (160, 150, 130), [
            (cx + s * 7, cy - s * 7),
            (cx + s * 9, cy - s * 2),
            (cx + s * 8, cy - s * 2),
            (cx + s * 6, cy - s * 6),
        ])

    def _draw_wight(self, surf, cx, cy, s, color, alive):
        # Ethereal flowing body
        alpha_surf = pygame.Surface((s * 14, s * 18), pygame.SRCALPHA)
        acx, acy = s * 7, s * 15
        a = 130 if not alive else 180
        pygame.draw.ellipse(alpha_surf, color + (a,),
                            (acx - s * 2, acy - s * 12, s * 4, s * 12))
        # Wisps
        for i in range(4):
            wx = acx + int(math.sin(self._tick * 0.05 + i) * s * 3)
            pygame.draw.ellipse(alpha_surf, color + (60,),
                                (wx - s, acy - i * s * 3, s * 2, s * 3))
        surf.blit(alpha_surf, (cx - s * 7, cy - s * 15))
        # Skull head
        pygame.draw.circle(surf, tuple(min(255, c + 60) for c in color),
                           (cx, cy - s * 14), int(s * 2))
        for dx in (-s // 2, s // 2):
            pygame.draw.circle(surf, (180, 220, 255), (cx + dx, cy - s * 14), max(2, s // 3))

    def _draw_troll(self, surf, cx, cy, s, color, alive):
        dark = tuple(max(0, c - 30) for c in color)
        # Huge rounded body
        pygame.draw.ellipse(surf, color,
                            (cx - s * 6, cy - s * 11, s * 12, s * 11))
        # Thick legs
        for dx in (-s * 2, s * 2 - s // 2):
            pygame.draw.rect(surf, dark, (cx + dx, cy - s * 4, s * 3, s * 4))
        # Large fists
        for dx in (-s * 7, s * 5):
            pygame.draw.circle(surf, dark, (cx + dx, cy - s * 4), s * 2)
        # Small head
        pygame.draw.circle(surf, color, (cx, cy - s * 12), int(s * 1.8))
        for dx in (-s // 2, s // 2):
            pygame.draw.circle(surf, (255, 80, 0), (cx + dx, cy - s * 12), max(2, s // 4))

    def _draw_uruk(self, surf, cx, cy, s, color, alive):
        dark = tuple(max(0, c - 50) for c in color)
        armor = (50, 50, 60)
        # Legs
        for dx in (-s * 2, s // 2):
            pygame.draw.rect(surf, armor, (cx + dx, cy - s * 5, s * 2, s * 5))
        # Armored body
        pygame.draw.rect(surf, color, (cx - s * 3, cy - s * 11, s * 6, s * 6))
        pygame.draw.rect(surf, armor, (cx - s * 3, cy - s * 11, s * 6, s * 6), max(2, s // 5))
        # Helmet
        pygame.draw.rect(surf, armor, (cx - s * 2, cy - s * 13, s * 4, s * 3))
        pygame.draw.line(surf, (200, 200, 220),
                         (cx - s * 2, cy - s * 12), (cx + s * 2, cy - s * 12), max(1, s // 5))
        # Eyes
        for dx in (-s // 2, s // 2):
            pygame.draw.circle(surf, (255, 40, 0), (cx + dx, cy - s * 12), max(2, s // 4))
        # Sword
        pygame.draw.polygon(surf, (180, 180, 200), [
            (cx + s * 3, cy - s * 9),
            (cx + s * 7, cy - s * 3),
            (cx + s * 6, cy - s * 3),
            (cx + s * 2, cy - s * 8),
        ])
    # ---- Entity info --------------------------------------------------------

    def _draw_enemy_info(self, surf, cx, cy, s):
        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)
        ename = self._enemy_name()
        if getattr(self.enemy, "is_boss", False):
            ename = tf("boss_prefix", name=ename)
            name_color = (255, 220, 60)
        else:
            name_color = (220, 210, 255)
        name_top = cy - s * 16
        draw_text(surf, ename, cx, name_top, font, name_color, center=True)
        bar_w = s * 14
        bar_x = cx - bar_w // 2
        bar_y = name_top + ui(7)
        hp_r = self.enemy.stats.hp / max(1, self.enemy.stats.max_hp)
        # HP bar background + fill
        pygame.draw.rect(surf, (40, 20, 20), (bar_x - 1, bar_y - 1, bar_w + 2, ui(5) + 2), border_radius=3)
        pygame.draw.rect(surf, (180, 40, 40), (bar_x, bar_y, int(bar_w * hp_r), ui(5)), border_radius=2)
        pygame.draw.rect(surf, (255, 80, 80), (bar_x, bar_y, int(bar_w * hp_r), ui(2)), border_radius=2)
        draw_text(surf, f"{self.enemy.stats.hp}/{self.enemy.stats.max_hp}",
                  cx, bar_y + ui(6), font_sm, (200, 180, 180), center=True)

    def _draw_player_info(self, surf, sw, sh, panel_y, s, ox, oy):
        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)
        stats = self.player.stats
        ix = ui(6) + ox
        iy = int(panel_y * 0.72) + oy
        draw_text(surf, f"Lv{stats.level}", ix, iy - ui(8), font, (200, 200, 255))
        bar_w = ui(55)
        hp_r = stats.hp / max(1, stats.max_hp)
        mp_r = stats.mp / max(1, stats.max_mp)
        # HP
        pygame.draw.rect(surf, (40, 15, 15), (ix - 1, iy - 1, bar_w + 2, ui(5) + 2), border_radius=3)
        pygame.draw.rect(surf, (180, 40, 40), (ix, iy, int(bar_w * hp_r), ui(5)), border_radius=2)
        pygame.draw.rect(surf, (255, 80, 80), (ix, iy, int(bar_w * hp_r), ui(2)), border_radius=2)
        draw_text(surf, f"HP {stats.hp}/{stats.max_hp}",
                  ix + bar_w + ui(3), iy, font_sm, (220, 180, 180))
        # MP
        iy2 = iy + ui(8)
        pygame.draw.rect(surf, (15, 15, 40), (ix - 1, iy2 - 1, bar_w + 2, ui(5) + 2), border_radius=3)
        pygame.draw.rect(surf, (40, 40, 180), (ix, iy2, int(bar_w * mp_r), ui(5)), border_radius=2)
        pygame.draw.rect(surf, (80, 80, 255), (ix, iy2, int(bar_w * mp_r), ui(2)), border_radius=2)
        draw_text(surf, f"MP {stats.mp}/{stats.max_mp}",
                  ix + bar_w + ui(3), iy2, font_sm, (180, 180, 220))
        if self.player_defending:
            draw_text(surf, t("defend_stance"),
                      ix, iy2 + ui(9), font_sm, (100, 180, 255))
    # ---- Particles ----------------------------------------------------------

    def _spawn_particles(self, cx, cy, etype):
        colors = {
            "melee":  [(255, 220, 100), (255, 160, 60), (200, 200, 200)],
            "ranged": [(180, 220, 255), (100, 180, 255), (220, 240, 255)],
            "magic":  [(200, 100, 255), (130, 60, 255), (255, 150, 255)],
        }
        cols = colors.get(etype, colors["melee"])
        count = 10 if etype == "magic" else 8
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.5, 7.0)
            color = random.choice(cols)
            self._particles.append({
                "x": float(cx), "y": float(cy),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 2.0,
                "life": random.randint(14, 28),
                "color": color,
                "r": random.randint(2, 5),
            })

    def _draw_particles_layer(self, surf, ox, oy):
        for p in self._particles:
            ratio = p["life"] / 28.0
            c = tuple(int(ch * ratio) for ch in p["color"])
            r = max(1, int(p["r"] * ratio))
            pygame.draw.circle(surf, c,
                               (int(p["x"] + ox), int(p["y"] + oy)), r)

    def _draw_damage_floats_layer(self, surf):
        font = get_font(FONT_UI_MD)
        for df in self._damage_floats:
            ratio = min(1.0, df["timer"] / 55.0)
            c = tuple(int(ch * ratio) for ch in df["color"])
            draw_text(surf, df["text"], int(df["x"]), int(df["y"]), font, c, center=True)
    # ---- Bottom panel -------------------------------------------------------

    def _draw_bottom_panel(self, surf, sw, sh, panel_y):
        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)

        # Panel background
        pygame.draw.rect(surf, (18, 15, 26),
                         (0, panel_y, sw, sh - panel_y))
        pygame.draw.line(surf, (70, 60, 100), (0, panel_y), (sw, panel_y), 2)

        divider_x = sw // 2
        pygame.draw.line(surf, (45, 40, 65),
                         (divider_x, panel_y + 6), (divider_x, sh - 6), 1)

        if self.phase == PHASE_PLAYER_CHOOSE:
            self._draw_action_menu(surf, sw, sh, panel_y, font, font_sm)
        else:
            self._draw_full_log(surf, sw, sh, panel_y, font_sm)

        # Always show recent log on right when in menu
        if self.phase == PHASE_PLAYER_CHOOSE:
            self._draw_side_log(surf, sw, sh, panel_y, font_sm)

    def _draw_action_menu(self, surf, sw, sh, panel_y, font, font_sm):
        mx = ui(10)
        my = panel_y + ui(4)

        # Section header
        draw_text(surf, t("actions_label"), mx, my, font_sm, (120, 110, 160))
        my += ui(6)

        if self.menu_level == MENU_MAIN:
            for i, key in enumerate(MAIN_OPT_KEYS):
                y = my + i * ui(7)
                selected = (i == self.cursor)
                if selected:
                    hl = pygame.Rect(mx - ui(2), y - ui(1), sw // 2 - ui(6), ui(6))
                    pygame.draw.rect(surf, (35, 30, 52), hl, border_radius=4)
                    pygame.draw.rect(surf, (80, 65, 120), hl, 1, border_radius=4)
                color = COLOR_GOLD if selected else (190, 185, 210)
                marker = "▶  " if selected else "   "
                draw_text(surf, marker + t(key), mx, y, font, color)

        elif self.menu_level == MENU_SKILL:
            draw_text(surf, t("skills_label"), mx, my - ui(3), font_sm, (120, 110, 160))
            for i, skill in enumerate(SKILL_DEFS):
                y = my + i * ui(7)
                selected = (i == self.cursor)
                if selected:
                    hl = pygame.Rect(mx - ui(2), y - ui(1), sw // 2 - ui(6), ui(6))
                    pygame.draw.rect(surf, (35, 30, 52), hl, border_radius=4)
                    pygame.draw.rect(surf, (80, 65, 120), hl, 1, border_radius=4)
                color = COLOR_GOLD if selected else (190, 185, 210)
                marker = "▶  " if selected else "   "
                cost_str = (tf("mp_cost_tag", cost=skill["cost"])
                            if skill["cost"] > 0 else t("free_tag"))
                draw_text(surf, marker + t(skill["name_key"]) + cost_str,
                          mx, y, font, color)

        elif self.menu_level == MENU_ITEM:
            draw_text(surf, t("items_label"), mx, my - ui(3), font_sm, (120, 110, 160))
            if not self.item_list:
                draw_text(surf, t("no_items"), mx, my, font, (100, 100, 120))
            else:
                for i, item in enumerate(self.item_list):
                    y = my + i * ui(7)
                    selected = (i == self.item_cursor)
                    if selected:
                        hl = pygame.Rect(mx - ui(2), y - ui(1), sw // 2 - ui(6), ui(6))
                        pygame.draw.rect(surf, (35, 30, 52), hl, border_radius=4)
                        pygame.draw.rect(surf, (80, 65, 120), hl, 1, border_radius=4)
                    color = COLOR_GOLD if selected else (190, 185, 210)
                    marker = "▶  " if selected else "   "
                    iname = item["name"]; icnt = item["count"]
                    draw_text(surf, f"{marker}{iname} x{icnt}",
                              mx, y, font, color)

    def _draw_side_log(self, surf, sw, sh, panel_y, font_sm):
        lx = sw // 2 + ui(8)
        ly = panel_y + ui(4)
        draw_text(surf, t("battle_log"), lx, ly, font_sm, (100, 95, 140))
        ly += ui(5)
        visible = self.log[-6:]
        for i, (text, color) in enumerate(visible):
            alpha_factor = (i + 1) / len(visible) if visible else 1
            faded = tuple(int(c * (0.45 + 0.55 * alpha_factor)) for c in color)
            draw_text(surf, text, lx, ly + i * ui(6), font_sm, faded)

    def _draw_full_log(self, surf, sw, sh, panel_y, font_sm):
        lx = ui(10)
        ly = panel_y + ui(4)
        visible = self.log[-8:]
        for i, (text, color) in enumerate(visible):
            alpha_factor = (i + 1) / len(visible) if visible else 1
            faded = tuple(int(c * (0.35 + 0.65 * alpha_factor)) for c in color)
            draw_text(surf, text, lx, ly + i * ui(6), font_sm, faded)    # ---- Phase overlays -----------------------------------------------------

    def _draw_phase_overlay(self, surf, sw, sh, panel_y):
        font_lg = get_font(FONT_UI_LG)
        font = get_font(FONT_UI_MD)
        cx = sw // 2

        if self.phase == PHASE_INTRO:
            overlay = pygame.Surface((sw, panel_y), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, max(0, 160 - self.phase_timer * 4)))
            surf.blit(overlay, (0, 0))
            name = self._enemy_name()
            if getattr(self.enemy, "is_boss", False):
                name = tf("boss_prefix", name=name)
            draw_text(surf, tf("wild_appears", name=name),
                      cx, panel_y // 2 - ui(8), font_lg,
                      (255, 220, 100), center=True)
            draw_text(surf, t("combat_start_hint"),
                      cx, panel_y // 2 + ui(6), font,
                      (180, 180, 220), center=True)

        elif self.phase == PHASE_WIN:
            overlay = pygame.Surface((sw, panel_y), pygame.SRCALPHA)
            overlay.fill((20, 15, 0, 180))
            surf.blit(overlay, (0, 0))
            draw_text(surf, t("victory"),
                      cx, panel_y // 2 - ui(12), font_lg,
                      (255, 215, 0), center=True)
            draw_text(surf, t("victory_continue"),
                      cx, panel_y // 2 + ui(2), font,
                      (220, 200, 120), center=True)

        elif self.phase == PHASE_LOSE:
            overlay = pygame.Surface((sw, panel_y), pygame.SRCALPHA)
            overlay.fill((30, 0, 0, 200))
            surf.blit(overlay, (0, 0))
            draw_text(surf, t("defeated"),
                      cx, panel_y // 2 - ui(12), font_lg,
                      COLOR_ACCENT, center=True)
            draw_text(surf, t("defeated_continue"),
                      cx, panel_y // 2 + ui(2), font,
                      (220, 160, 160), center=True)

        elif self.phase == PHASE_FLEE:
            overlay = pygame.Surface((sw, panel_y), pygame.SRCALPHA)
            overlay.fill((0, 20, 0, 160))
            surf.blit(overlay, (0, 0))
            draw_text(surf, t("escaped_continue"),
                      cx, panel_y // 2, font,
                      (100, 255, 100), center=True)