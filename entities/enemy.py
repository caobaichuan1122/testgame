# ============================================================
#  Enemy: AI state machine (idle/wander/chase/attack)
# ============================================================
import math
import random
import pygame
from entities.entity import Entity
from systems.stats import Stats
from core.utils import distance, normalize
from assets.sprite_manager import load_entity_sprites


# AI states
AI_IDLE = "idle"
AI_WANDER = "wander"
AI_CHASE = "chase"
AI_ATTACK = "attack"


class Enemy(Entity):
    def __init__(self, wx, wy, enemy_type="orc", **kwargs):
        super().__init__(wx, wy)
        self.enemy_type = enemy_type
        self.spawn_wx = wx
        self.spawn_wy = wy

        # Default attributes, can be overridden via kwargs
        defaults = ENEMY_TEMPLATES.get(enemy_type, ENEMY_TEMPLATES["orc"])
        for k, v in defaults.items():
            setattr(self, k, v)
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.stats = Stats(
            hp=self.max_hp, mp=0,
            str_=self.str_val, dex=self.dex_val,
            int_=self.int_val, def_=self.def_val,
        )

        # AI
        self.ai_state = AI_IDLE
        self.ai_timer = random.randint(30, 120)
        self.wander_dx = 0.0
        self.wander_dy = 0.0
        self.attack_cooldown = 0
        self.hit_flash = 0
        self.combat_cooldown = 0  # Post-combat cooldown to prevent immediate re-trigger

        # Sprites
        self.sprites = load_entity_sprites(f"enemies/{self.enemy_type}")

    def update(self, game):
        if not self.stats.alive:
            if self.hit_flash > 0:
                self.hit_flash -= 1
            else:
                self.active = False
            return

        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.combat_cooldown > 0:
            self.combat_cooldown -= 1

        player = game.entities.player
        if not player or not player.stats.alive:
            return

        dist_to_player = distance(self.wx, self.wy, player.wx, player.wy)

        # Advance sprite animation
        if self.sprites:
            state = "walk" if self.ai_state in (AI_WANDER, AI_CHASE) else "idle"
            self.sprites.update(state)

        # AI state machine
        if self.ai_state == AI_IDLE:
            self._ai_idle(dist_to_player)
        elif self.ai_state == AI_WANDER:
            self._ai_wander(game, dist_to_player)
        elif self.ai_state == AI_CHASE:
            self._ai_chase(game, player, dist_to_player)
        elif self.ai_state == AI_ATTACK:
            self._ai_attack(game, player, dist_to_player)

    def _ai_idle(self, dist_to_player):
        self.ai_timer -= 1
        if dist_to_player < self.detect_range:
            self.ai_state = AI_CHASE
            return
        if self.ai_timer <= 0:
            self.ai_state = AI_WANDER
            angle = random.uniform(0, math.pi * 2)
            self.wander_dx = math.cos(angle)
            self.wander_dy = math.sin(angle)
            self.ai_timer = random.randint(60, 180)

    def _ai_wander(self, game, dist_to_player):
        if dist_to_player < self.detect_range:
            self.ai_state = AI_CHASE
            return

        self.ai_timer -= 1
        if self.ai_timer <= 0:
            self.ai_state = AI_IDLE
            self.ai_timer = random.randint(30, 120)
            return

        speed = self.move_speed / 60.0 * 0.5
        new_wx = self.wx + self.wander_dx * speed
        new_wy = self.wy + self.wander_dy * speed

        # Don't wander too far from spawn point
        if distance(new_wx, new_wy, self.spawn_wx, self.spawn_wy) > self.wander_range:
            self.ai_state = AI_IDLE
            self.ai_timer = random.randint(30, 60)
            return

        if game.iso_map.is_walkable(new_wx, new_wy):
            self.wx = new_wx
            self.wy = new_wy

    def _ai_chase(self, game, player, dist_to_player):
        if dist_to_player > self.detect_range * 1.5:
            self.ai_state = AI_IDLE
            self.ai_timer = random.randint(30, 60)
            return

        # Trigger turn-based combat when within attack range
        if dist_to_player < self.attack_range and self.combat_cooldown <= 0:
            from core.settings import STATE_COMBAT
            if game.state != STATE_COMBAT:
                game.start_combat(self)
            return

        # Move toward player
        dx = player.wx - self.wx
        dy = player.wy - self.wy
        dx, dy = normalize(dx, dy)
        speed = self.move_speed / 60.0

        new_wx = self.wx + dx * speed
        new_wy = self.wy + dy * speed

        if game.iso_map.is_walkable(new_wx, self.wy):
            self.wx = new_wx
        if game.iso_map.is_walkable(self.wx, new_wy):
            self.wy = new_wy

    def _ai_attack(self, game, player, dist_to_player):
        # In turn-based combat mode, attack state directly triggers combat
        if self.combat_cooldown <= 0:
            from core.settings import STATE_COMBAT
            if game.state != STATE_COMBAT:
                game.start_combat(self)
        else:
            self.ai_state = AI_IDLE
            self.ai_timer = random.randint(30, 60)

    def draw(self, surface, camera):
        if not self.active:
            return

        sx, sy = camera.world_to_cam(self.wx, self.wy)

        # White flash effect
        use_flash = self.hit_flash > 0
        color = (255, 255, 255) if use_flash else self.color

        if not self.stats.alive:
            color = tuple(c // 2 for c in self.color)

        drawn_with_sprite = False
        sprite_top_y = sy  # for HP bar placement

        if self.sprites:
            frame = self.sprites.get_frame()
            if frame:
                ax, ay = self.sprites.anchor
                dx = int(sx) - ax
                dy = int(sy) - ay
                sprite_top_y = dy

                if use_flash:
                    # Flash white: create tinted copy
                    flash_surf = frame.copy()
                    flash_surf.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGB_MAX)
                    surface.blit(flash_surf, (dx, dy))
                elif not self.stats.alive:
                    # Death: darken
                    dark_surf = frame.copy()
                    dark_surf.fill((128, 128, 128), special_flags=pygame.BLEND_RGB_MULT)
                    surface.blit(dark_surf, (dx, dy))
                else:
                    surface.blit(frame, (dx, dy))
                drawn_with_sprite = True

        if not drawn_with_sprite:
            # Body (diamond shape)
            w, h = self.draw_size
            points = [
                (sx, sy - h * 2),
                (sx + w, sy - h),
                (sx, sy),
                (sx - w, sy - h),
            ]
            pygame.draw.polygon(surface, color, points)
            sprite_top_y = sy - h * 2

            # Boss extra decoration
            if self.is_boss:
                pygame.draw.polygon(surface, (255, 255, 100), points, 1)

        # HP bar
        if self.stats.alive and self.stats.hp < self.stats.max_hp:
            bar_w = 16
            bar_h = 2
            bx = sx - bar_w // 2
            by = sprite_top_y - 3
            ratio = self.stats.hp / self.stats.max_hp
            pygame.draw.rect(surface, (60, 0, 0), (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, (220, 30, 30),
                             (bx, by, int(bar_w * ratio), bar_h))

    def take_hit(self):
        self.hit_flash = 6


# --- Enemy templates ---
ENEMY_TEMPLATES = {
    # ★ Easy
    "goblin": {
        "max_hp": 12, "str_val": 1, "dex_val": 1, "int_val": 0, "def_val": 0,
        "atk_damage": 3, "attack_range": 1.1, "attack_cd": 55,
        "detect_range": 4.0, "move_speed": 1.2, "wander_range": 3.5,
        "xp_reward": 10, "gold_reward": 5, "drops": ["goblin_ear"],
        "color": (70, 90, 50), "draw_size": (3, 2),
        "ranged": False, "is_boss": False,
    },
    "wolf": {
        "max_hp": 20, "str_val": 3, "dex_val": 2, "int_val": 0, "def_val": 1,
        "atk_damage": 5, "attack_range": 1.2, "attack_cd": 45,
        "detect_range": 5.0, "move_speed": 1.5, "wander_range": 5.0,
        "xp_reward": 15, "gold_reward": 8, "drops": [],
        "color": (100, 90, 80), "draw_size": (4, 3),
        "ranged": False, "is_boss": False,
    },
    # ★★ Medium
    "spider": {
        "max_hp": 25, "str_val": 2, "dex_val": 3, "int_val": 1, "def_val": 1,
        "atk_damage": 4, "attack_range": 1.3, "attack_cd": 50,
        "detect_range": 5.5, "move_speed": 1.3, "wander_range": 4.0,
        "xp_reward": 20, "gold_reward": 10, "drops": ["spider_silk"],
        "color": (40, 35, 55), "draw_size": (4, 3),
        "ranged": False, "is_boss": False,
    },
    "undead": {
        "max_hp": 35, "str_val": 3, "dex_val": 1, "int_val": 2, "def_val": 3,
        "atk_damage": 6, "attack_range": 1.3, "attack_cd": 55,
        "detect_range": 5.0, "move_speed": 0.9, "wander_range": 4.0,
        "xp_reward": 30, "gold_reward": 15, "drops": ["morgul_shard"],
        "color": (130, 140, 160), "draw_size": (4, 3),
        "ranged": False, "is_boss": False,
    },
    # ★★★ Hard
    "uruk_berserker": {
        "max_hp": 65, "str_val": 7, "dex_val": 3, "int_val": 0, "def_val": 5,
        "atk_damage": 12, "attack_range": 1.4, "attack_cd": 55,
        "detect_range": 6.0, "move_speed": 1.1, "wander_range": 4.0,
        "xp_reward": 60, "gold_reward": 35, "drops": ["uruk_shield"],
        "color": (110, 75, 45), "draw_size": (5, 4),
        "ranged": False, "is_boss": False,
    },
    # ★★★★ Very Hard
    "nazgul": {
        "max_hp": 120, "str_val": 9, "dex_val": 6, "int_val": 5, "def_val": 8,
        "atk_damage": 20, "attack_range": 2.0, "attack_cd": 60,
        "detect_range": 8.0, "move_speed": 0.9, "wander_range": 6.0,
        "xp_reward": 120, "gold_reward": 80, "drops": ["morgul_blade"],
        "color": (30, 25, 40), "draw_size": (5, 5),
        "ranged": False, "is_boss": False,
    },
    # ★★★★★ Boss
    "balrog": {
        "max_hp": 500, "str_val": 15, "dex_val": 5, "int_val": 8, "def_val": 12,
        "atk_damage": 30, "attack_range": 2.0, "attack_cd": 70,
        "detect_range": 8.0, "move_speed": 0.7, "wander_range": 4.0,
        "xp_reward": 1000, "gold_reward": 500, "drops": ["one_ring"],
        "color": (200, 60, 10), "draw_size": (8, 8),
        "ranged": False, "is_boss": True,
    },
    "orc": {
        "max_hp": 25, "str_val": 2, "dex_val": 1, "int_val": 0, "def_val": 1,
        "atk_damage": 4, "attack_range": 1.2, "attack_cd": 50,
        "detect_range": 5.0, "move_speed": 1.0, "wander_range": 4.0,
        "xp_reward": 20, "gold_reward": 10, "drops": ["orc_blood"],
        "color": (80, 100, 60), "draw_size": (4, 3),
        "ranged": False, "is_boss": False,
    },
    "wight": {
        "max_hp": 40, "str_val": 4, "dex_val": 2, "int_val": 0, "def_val": 3,
        "atk_damage": 7, "attack_range": 1.3, "attack_cd": 45,
        "detect_range": 6.0, "move_speed": 1.2, "wander_range": 5.0,
        "xp_reward": 35, "gold_reward": 18, "drops": ["morgul_shard"],
        "color": (160, 170, 180), "draw_size": (4, 4),
        "ranged": False, "is_boss": False,
    },
    "uruk_archer": {
        "max_hp": 30, "str_val": 2, "dex_val": 5, "int_val": 0, "def_val": 2,
        "atk_damage": 5, "attack_range": 6.0, "attack_cd": 60,
        "detect_range": 7.0, "move_speed": 1.3, "wander_range": 4.0,
        "xp_reward": 30, "gold_reward": 15, "drops": [],
        "color": (90, 70, 50), "draw_size": (4, 4),
        "ranged": True, "is_boss": False,
    },
    "cave_troll": {
        "max_hp": 200, "str_val": 8, "dex_val": 1, "int_val": 0, "def_val": 8,
        "atk_damage": 15, "attack_range": 1.5, "attack_cd": 60,
        "detect_range": 6.0, "move_speed": 0.6, "wander_range": 3.0,
        "xp_reward": 300, "gold_reward": 150, "drops": ["mithril_coat"],
        "color": (120, 100, 80), "draw_size": (6, 6),
        "ranged": False, "is_boss": True,
    },
}
