# ============================================================
#  NPC: dialogue/shop/quest triggers + speech bubble + follow behavior
# ============================================================
import math
import random as rnd
import pygame
from entity import Entity
from settings import COLOR_NPC
from sprite_manager import load_entity_sprites
from i18n import t, tf


class NPC(Entity):
    def __init__(self, wx, wy, name="NPC", npc_type="talk",
                 dialogue_id=None, shop_id=None, quest_ids=None,
                 color=None, behavior="idle", patrol_points=None,
                 wander_radius=3.0, idle_lines=None):
        super().__init__(wx, wy)
        self.name = name
        self.npc_type = npc_type  # "talk", "shop", "quest"
        self.dialogue_id = dialogue_id
        self.shop_id = shop_id
        self.quest_ids = quest_ids or []
        self.color = color or COLOR_NPC
        self.sprites = load_entity_sprites(f"npcs/{self.name.lower()}")

        # Overhead icon
        self._icon = ""           # Currently displayed icon
        self._icon_bob = 0        # Floating animation counter

        # Behavior system
        self.behavior = behavior  # "idle", "patrol", "wander", "follow"
        self._saved_behavior = behavior  # Save original behavior (restored after follow ends)
        self.home_wx = float(wx)
        self.home_wy = float(wy)
        self.patrol_points = patrol_points or []
        self._patrol_index = 0
        self.wander_radius = wander_radius
        self._move_target = None   # (tx, ty)
        self._move_speed = 0.01    # NPC moves slowly
        self._follow_speed = 0.025  # Follow mode moves faster
        self._wait_timer = 0       # Wait frames after reaching target
        self._moving = False

        # Speech bubble
        self.idle_lines = idle_lines or []
        self._bubble_text = ""
        self._bubble_timer = 0     # Remaining display frames
        self._bubble_cooldown = 0  # Cooldown frames to prevent frequent triggers

    def update(self, game):
        """Update NPC state: icon + movement + bubble."""
        self._icon_bob += 1
        self._update_icon(game)
        self._update_movement(game)
        self._update_bubble(game)

        # Escort arrival detection in follow behavior
        if self.behavior == "follow" and game.quest_manager:
            arrived_qid = game.quest_manager.on_escort_arrive(self.wx, self.wy)
            if arrived_qid:
                self.behavior = "idle"
                self._bubble_text = t("escort_arrived")
                self._bubble_timer = 180
                game.chat_log.add(
                    tf("npc_arrived_dest", name=self.name), "quest")

    def _update_icon(self, game):
        """Update overhead icon based on NPC type and quest status."""
        if self.npc_type == "shop":
            self._icon = "$"
        elif self.npc_type == "quest" and game.quest_manager:
            # Check quest status
            for qid in self.quest_ids:
                quest = game.quest_manager.get_quest(qid)
                if quest:
                    if quest["status"] == "available":
                        self._icon = "!"   # New quest available
                        return
                    elif quest["status"] == "completable":
                        self._icon = "?"   # Quest ready to complete
                        return
                    elif quest["status"] == "active":
                        self._icon = "..."  # In progress
                        return
            self._icon = ""
        elif self.npc_type == "talk":
            self._icon = "..."
        else:
            self._icon = ""

    def _update_bubble(self, game):
        """Update speech bubble."""
        if self._bubble_timer > 0:
            self._bubble_timer -= 1
        if self._bubble_cooldown > 0:
            self._bubble_cooldown -= 1
            return

        # Check if player is nearby
        player = game.entities.player
        if not player or not self.idle_lines:
            return
        dx = player.wx - self.wx
        dy = player.wy - self.wy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 4.0 and self._bubble_timer <= 0 and self._bubble_cooldown <= 0:
            if rnd.random() < 0.005:  # ~0.5% per frame, triggers on average every 3 seconds
                self._bubble_text = rnd.choice(self.idle_lines)
                self._bubble_timer = 180  # 3 seconds display
                self._bubble_cooldown = 300  # 5 seconds cooldown

    def _update_movement(self, game):
        """NPC movement behavior."""
        if self.behavior == "idle":
            self._moving = False
            return

        if self.behavior == "follow":
            self._update_follow(game)
            return

        # Wait timer
        if self._wait_timer > 0:
            self._wait_timer -= 1
            self._moving = False
            return

        # Need new target
        if self._move_target is None:
            if self.behavior == "patrol" and self.patrol_points:
                self._move_target = self.patrol_points[self._patrol_index]
                self._patrol_index = (
                    (self._patrol_index + 1) % len(self.patrol_points)
                )
            elif self.behavior == "wander":
                angle = rnd.random() * math.pi * 2
                r = rnd.random() * self.wander_radius
                tx = self.home_wx + math.cos(angle) * r
                ty = self.home_wy + math.sin(angle) * r
                self._move_target = (tx, ty)
            else:
                self._moving = False
                return

        # Move toward target
        tx, ty = self._move_target
        dx = tx - self.wx
        dy = ty - self.wy
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.1:
            # Reached target
            self._move_target = None
            self._wait_timer = rnd.randint(60, 180)  # Wait 1-3 seconds
            self._moving = False
            return

        # Normalize and move
        dx /= dist
        dy /= dist
        new_wx = self.wx + dx * self._move_speed
        new_wy = self.wy + dy * self._move_speed

        if game.iso_map and game.iso_map.is_walkable(new_wx, new_wy):
            self.wx = new_wx
            self.wy = new_wy
            self._moving = True
        else:
            # Hit obstacle, abandon current target
            self._move_target = None
            self._wait_timer = rnd.randint(30, 90)
            self._moving = False

    def _update_follow(self, game):
        """Follow player movement."""
        player = game.entities.player
        if not player:
            self._moving = False
            return

        dx = player.wx - self.wx
        dy = player.wy - self.wy
        dist = math.sqrt(dx * dx + dy * dy)

        # Follow at a certain distance
        if dist < 1.5:
            self._moving = False
            return
        if dist > 15.0:
            # Too far, teleport near player
            self.wx = player.wx - 1.0
            self.wy = player.wy - 1.0
            self._moving = False
            return

        dx /= dist
        dy /= dist
        new_wx = self.wx + dx * self._follow_speed
        new_wy = self.wy + dy * self._follow_speed

        if game.iso_map and game.iso_map.is_walkable(new_wx, new_wy):
            self.wx = new_wx
            self.wy = new_wy
            self._moving = True
        else:
            self._moving = False

    def start_follow(self):
        """Start following player."""
        self._saved_behavior = self.behavior
        self.behavior = "follow"

    def interact(self, game):
        """Interact with NPC."""
        if self.npc_type == "shop":
            if self.shop_id and game.shop_manager:
                game.ui.open_shop(self.shop_id)
            elif self.dialogue_id:
                game.ui.open_dialogue(self.dialogue_id, self.name)
        elif self.npc_type == "quest":
            # Check for available/completable quests
            handled = False
            if game.quest_manager:
                for qid in self.quest_ids:
                    quest = game.quest_manager.get_quest(qid)
                    if quest:
                        if quest["status"] == "available":
                            game.quest_manager.accept_quest(qid)
                            # Escort quest: NPC starts following after accepting
                            if quest["type"] == "escort":
                                self.start_follow()
                            game.ui.open_dialogue(
                                qid + "_accept", self.name)
                            handled = True
                            break
                        elif quest["status"] == "completable":
                            game.quest_manager.complete_quest(qid, game)
                            game.ui.open_dialogue(
                                qid + "_complete", self.name)
                            handled = True
                            break
                        elif quest["status"] == "active":
                            game.ui.open_dialogue(
                                qid + "_progress", self.name)
                            handled = True
                            break
            if not handled and self.dialogue_id:
                game.ui.open_dialogue(self.dialogue_id, self.name)
        else:
            if self.dialogue_id:
                game.ui.open_dialogue(self.dialogue_id, self.name)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_cam(self.wx, self.wy)

        self._canvas_top_y = sy - 8 - 14  # default for color block

        if self.sprites:
            # Advance idle/walk animation
            state = "walk" if self._moving else "idle"
            self.sprites.update(state)
            frame = self.sprites.get_frame()
            if frame:
                ax, ay = self.sprites.anchor
                dx = int(sx) - ax
                dy = int(sy) - ay
                surface.blit(frame, (dx, dy))
                self._canvas_top_y = dy - 4
            else:
                self._draw_color_body(surface, sx, sy)
        else:
            self._draw_color_body(surface, sx, sy)

    def draw_labels(self, surface, camera):
        """Draw name, icon, bubble on screen layer (avoid scaling blur)."""
        from settings import PIXEL_SCALE
        from utils import get_font, FONT_UI_SM

        sx, sy = camera.world_to_cam(self.wx, self.wy)
        # Convert canvas coordinates to screen coordinates
        scr_x = sx * PIXEL_SCALE
        name_top_y = getattr(self, '_canvas_top_y', sy - 22) * PIXEL_SCALE

        font = get_font(FONT_UI_SM)

        # Name
        name_surf = font.render(self.name, False, (255, 255, 200))
        surface.blit(name_surf,
                     (int(scr_x) - name_surf.get_width() // 2,
                      int(name_top_y)))

        # Overhead icon (floating effect)
        if self._icon:
            bob = math.sin(self._icon_bob * 0.05) * 6
            icon_y = name_top_y - 28 + bob
            if self._icon == "!":
                icon_color = (255, 220, 50)
            elif self._icon == "?":
                icon_color = (100, 255, 100)
            elif self._icon == "$":
                icon_color = (255, 215, 0)
            else:
                icon_color = (180, 180, 180)
            icon_surf = font.render(self._icon, False, icon_color)
            surface.blit(icon_surf,
                         (int(scr_x) - icon_surf.get_width() // 2,
                          int(icon_y)))

        # Speech bubble
        if self._bubble_timer > 0 and self._bubble_text:
            self._draw_bubble(surface, scr_x, name_top_y - 30)

    def _draw_bubble(self, surface, sx, base_y):
        """Draw NPC overhead speech bubble (screen resolution)."""
        from utils import get_font, FONT_UI_SM
        font = get_font(FONT_UI_SM)

        # Auto word-wrap
        max_chars = 18
        text = self._bubble_text
        lines = []
        while len(text) > max_chars:
            idx = text.rfind(' ', 0, max_chars)
            if idx == -1:
                idx = max_chars
            lines.append(text[:idx])
            text = text[idx:].lstrip()
        if text:
            lines.append(text)

        line_h = 22
        pad_x, pad_y = 8, 6
        max_w = 0
        rendered = []
        for line in lines:
            surf = font.render(line, False, (40, 30, 20))
            rendered.append(surf)
            max_w = max(max_w, surf.get_width())

        bw = max_w + pad_x * 2
        bh = len(lines) * line_h + pad_y * 2
        bx = int(sx) - bw // 2
        by = int(base_y) - bh - 8

        # Fade-out effect
        alpha = 255
        if self._bubble_timer < 30:
            alpha = int(255 * self._bubble_timer / 30)

        # Bubble background
        bubble_surf = pygame.Surface((bw, bh + 8), pygame.SRCALPHA)
        bubble_surf.fill((255, 250, 230, min(alpha, 220)))
        # Small triangle tail
        tri_x = bw // 2
        pygame.draw.polygon(bubble_surf, (255, 250, 230, min(alpha, 220)),
                            [(tri_x - 5, bh), (tri_x + 5, bh), (tri_x, bh + 8)])
        # Border
        pygame.draw.rect(bubble_surf, (180, 160, 120, alpha),
                         (0, 0, bw, bh), 1)

        bubble_surf.set_alpha(alpha)
        surface.blit(bubble_surf, (bx, by))

        # Text
        for i, surf in enumerate(rendered):
            surf.set_alpha(alpha)
            surface.blit(surf, (bx + pad_x, by + pad_y + i * line_h))

    def _draw_color_body(self, surface, sx, sy):
        """Fallback: draw NPC as color diamond + circle."""
        w, h = 5, 4
        points = [
            (sx, sy - h * 2),
            (sx + w, sy - h),
            (sx, sy),
            (sx - w, sy - h),
        ]
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.circle(surface, self.color,
                           (int(sx), int(sy) - h * 2 - 3), 3)
