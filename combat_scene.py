# ============================================================
#  Turn-based combat scene manager
# ============================================================
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_HP, COLOR_MP, COLOR_UI, COLOR_ACCENT, COLOR_GOLD,
    COMBAT_MELEE, COMBAT_RANGED, COMBAT_MAGIC,
    MELEE_BASE_DMG, RANGED_BASE_DMG, MAGIC_BASE_DMG, MAGIC_COST,
)
from combat import calc_damage, check_crit
from inventory import ITEMS
from i18n import t, tf, get_item_name
from utils import draw_bar, draw_text, get_font, ui, FONT_UI_SM, FONT_UI_MD, FONT_UI_LG


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

    def _grant_rewards(self):
        self.player._on_enemy_kill(self.enemy, self.game)
        xp = self.enemy.xp_reward
        gold = self.enemy.gold_reward
        self.log.append((tf("xp_gold_reward", xp=xp, gold=gold), COLOR_GOLD))

    # ---- Draw ----

    def draw(self, screen):
        if not self.active:
            return

        font = get_font(FONT_UI_MD)
        font_sm = get_font(FONT_UI_SM)
        font_lg = get_font(FONT_UI_LG)

        screen.fill((15, 12, 20))

        panel_y = SCREEN_HEIGHT * 2 // 3

        self._draw_battle_area(screen, panel_y, font, font_sm, font_lg)

        pygame.draw.rect(screen, (25, 22, 32), (0, panel_y, SCREEN_WIDTH, SCREEN_HEIGHT - panel_y))
        pygame.draw.line(screen, (80, 80, 100), (0, panel_y), (SCREEN_WIDTH, panel_y), 2)

        if self.phase == PHASE_PLAYER_CHOOSE:
            self._draw_menu(screen, panel_y, font, font_sm)
        else:
            self._draw_log(screen, panel_y, font_sm)

        if self.phase == PHASE_WIN:
            draw_text(screen, t("victory_continue"),
                      SCREEN_WIDTH // 2, panel_y + ui(8), font, COLOR_GOLD, center=True)
        elif self.phase == PHASE_LOSE:
            draw_text(screen, t("defeated_continue"),
                      SCREEN_WIDTH // 2, panel_y + ui(8), font, COLOR_ACCENT, center=True)
        elif self.phase == PHASE_FLEE:
            draw_text(screen, t("escaped_continue"),
                      SCREEN_WIDTH // 2, panel_y + ui(8), font, (100, 255, 100), center=True)

    def _draw_battle_area(self, screen, panel_y, font, font_sm, font_lg):
        cx = SCREEN_WIDTH // 2
        area_h = panel_y

        draw_text(screen, tf("round_num", n=self.round_num),
                  SCREEN_WIDTH - ui(30), ui(3), font_sm, (150, 150, 180))

        # --- Enemy (upper) ---
        enemy_x = cx + ui(30)
        enemy_y = area_h // 4

        e_color = self.enemy.color
        if self.enemy_flash > 0 and self.enemy_flash % 4 < 2:
            e_color = (255, 255, 255)
        if not self.enemy.stats.alive:
            e_color = tuple(c // 3 for c in self.enemy.color)

        ew, eh = getattr(self.enemy, 'draw_size', (4, 3))
        scale = 5
        sw, sh = ew * scale, eh * scale
        points = [
            (enemy_x, enemy_y - sh * 2),
            (enemy_x + sw, enemy_y - sh),
            (enemy_x, enemy_y),
            (enemy_x - sw, enemy_y - sh),
        ]
        pygame.draw.polygon(screen, e_color, points)
        if getattr(self.enemy, 'is_boss', False):
            pygame.draw.polygon(screen, (255, 255, 100), points, 2)

        ename = self._enemy_name()
        if getattr(self.enemy, 'is_boss', False):
            ename = tf("boss_prefix", name=ename)
        draw_text(screen, ename, enemy_x, enemy_y + ui(4), font, COLOR_UI, center=True)

        bar_w = ui(60)
        bar_x = enemy_x - bar_w // 2
        bar_y = enemy_y + ui(12)
        hp_ratio = self.enemy.stats.hp / self.enemy.stats.max_hp
        draw_bar(screen, bar_x, bar_y, bar_w, ui(5), hp_ratio, COLOR_HP)
        draw_text(screen, f"HP {self.enemy.stats.hp}/{self.enemy.stats.max_hp}",
                  enemy_x, bar_y + ui(6), font_sm, COLOR_UI, center=True)

        # --- Player (lower) ---
        player_x = cx - ui(30)
        player_y = area_h * 3 // 4 - ui(10)

        p_color = (80, 180, 255)
        if self.player_flash > 0 and self.player_flash % 4 < 2:
            p_color = (255, 100, 100)
        if self.player_defending:
            p_color = (100, 200, 255)

        pw, ph = 6 * 4, 4 * 4
        p_points = [
            (player_x, player_y - ph * 2),
            (player_x + pw, player_y - ph),
            (player_x, player_y),
            (player_x - pw, player_y - ph),
        ]
        pygame.draw.polygon(screen, p_color, p_points)
        pygame.draw.circle(screen, (100, 200, 255),
                           (player_x, player_y - ph * 2 - 8), 8)

        if self.player_defending:
            shield_points = [
                (player_x - 12, player_y - ph - 20),
                (player_x + 12, player_y - ph - 20),
                (player_x + 10, player_y - ph - 5),
                (player_x, player_y - ph + 2),
                (player_x - 10, player_y - ph - 5),
            ]
            pygame.draw.polygon(screen, (100, 150, 255), shield_points, 2)

        stats = self.player.stats
        info_x = ui(8)
        info_y = area_h - ui(28)

        draw_text(screen, f"Lv{stats.level}", info_x, info_y - ui(8), font, COLOR_UI)

        hp_bar_w = ui(50)
        draw_bar(screen, info_x, info_y, hp_bar_w, ui(5),
                 stats.hp / stats.max_hp, COLOR_HP)
        draw_text(screen, f"HP {stats.hp}/{stats.max_hp}",
                  info_x + hp_bar_w + ui(3), info_y, font_sm, COLOR_UI)

        draw_bar(screen, info_x, info_y + ui(8), hp_bar_w, ui(5),
                 stats.mp / stats.max_mp, COLOR_MP)
        draw_text(screen, f"MP {stats.mp}/{stats.max_mp}",
                  info_x + hp_bar_w + ui(3), info_y + ui(8), font_sm, COLOR_UI)

    def _draw_menu(self, screen, panel_y, font, font_sm):
        menu_x = ui(20)
        menu_y = panel_y + ui(8)

        if self.menu_level == MENU_MAIN:
            draw_text(screen, t("actions_label"), menu_x, menu_y - ui(5), font_sm, (150, 150, 180))
            for i, key in enumerate(MAIN_OPT_KEYS):
                y = menu_y + i * ui(8)
                color = COLOR_GOLD if i == self.cursor else COLOR_UI
                prefix = "> " if i == self.cursor else "  "
                draw_text(screen, f"{prefix}{t(key)}", menu_x, y, font, color)

        elif self.menu_level == MENU_SKILL:
            draw_text(screen, t("skills_label"), menu_x, menu_y - ui(5),
                      font_sm, (150, 150, 180))
            for i, skill in enumerate(SKILL_DEFS):
                y = menu_y + i * ui(8)
                color = COLOR_GOLD if i == self.cursor else COLOR_UI
                prefix = "> " if i == self.cursor else "  "
                cost_str = tf("mp_cost_tag", cost=skill["cost"]) if skill["cost"] > 0 else t("free_tag")
                draw_text(screen, f"{prefix}{t(skill['name_key'])}{cost_str}",
                          menu_x, y, font, color)

        elif self.menu_level == MENU_ITEM:
            draw_text(screen, t("items_label"), menu_x, menu_y - ui(5),
                      font_sm, (150, 150, 180))
            if not self.item_list:
                draw_text(screen, t("no_items"), menu_x, menu_y, font, (120, 120, 120))
            else:
                for i, item in enumerate(self.item_list):
                    y = menu_y + i * ui(8)
                    color = COLOR_GOLD if i == self.item_cursor else COLOR_UI
                    prefix = "> " if i == self.item_cursor else "  "
                    draw_text(screen, f"{prefix}{item['name']} x{item['count']}",
                              menu_x, y, font, color)

        # Right side: recent log
        log_x = SCREEN_WIDTH // 2 + ui(10)
        log_y = panel_y + ui(3)
        draw_text(screen, t("battle_log"), log_x, log_y, font_sm, (150, 150, 180))
        visible = self.log[-5:]
        for i, (text, color) in enumerate(visible):
            draw_text(screen, text, log_x, log_y + ui(5) + i * ui(6), font_sm, color)

    def _draw_log(self, screen, panel_y, font_sm):
        log_x = ui(10)
        log_y = panel_y + ui(5)
        visible = self.log[-7:]
        for i, (text, color) in enumerate(visible):
            draw_text(screen, text, log_x, log_y + i * ui(6), font_sm, color)
