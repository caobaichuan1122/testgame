# ============================================================
#  投射物：箭矢、魔法弹
# ============================================================
import math
import pygame
from entity import Entity
from utils import distance
from sprite_manager import load_single_sprite


class Projectile(Entity):
    def __init__(self, wx, wy, angle_deg, speed, damage, max_range,
                 color, owner="player"):
        super().__init__(wx, wy)
        self.angle = angle_deg
        self.speed = speed / 60.0
        self.damage = damage
        self.max_range = max_range
        self.color = color
        self.owner = owner  # "player" or "enemy"

        self.start_wx = wx
        self.start_wy = wy
        self.dx = math.cos(math.radians(angle_deg))
        self.dy = math.sin(math.radians(angle_deg))

        self.trail = []  # 尾迹坐标

        # Try loading a sprite for this projectile type
        proj_type = "arrow" if color == (200, 180, 100) else "magic_bolt"
        self.sprites = load_single_sprite(f"projectiles/{proj_type}.png")

    def update(self, game):
        if not self.active:
            return

        # 移动
        self.wx += self.dx * self.speed
        self.wy += self.dy * self.speed

        # 记录尾迹
        self.trail.append((self.wx, self.wy))
        if len(self.trail) > 5:
            self.trail.pop(0)

        # 检查射程
        dist = distance(self.start_wx, self.start_wy, self.wx, self.wy)
        if dist > self.max_range:
            self.active = False
            return

        # 检查地图碰撞
        if not game.iso_map.is_in_bounds(self.wx, self.wy):
            self.active = False
            return
        if not game.iso_map.is_walkable(self.wx, self.wy):
            self.active = False
            return

        # 检查实体碰撞
        if self.owner == "player":
            for enemy in game.entities.enemies:
                if not enemy.active or not enemy.stats.alive:
                    continue
                if distance(self.wx, self.wy, enemy.wx, enemy.wy) < 0.8:
                    game.entities.player.on_projectile_hit(
                        enemy, self.damage, game)
                    self.active = False
                    return
        elif self.owner == "enemy":
            player = game.entities.player
            if player and player.stats.alive:
                if distance(self.wx, self.wy, player.wx, player.wy) < 0.8:
                    player.stats.take_damage(self.damage)
                    player.add_message(f"-{self.damage}")
                    self.active = False
                    return

    def draw(self, surface, camera):
        if not self.active:
            return

        sx, sy = camera.world_to_cam(self.wx, self.wy)

        # 尾迹 (always drawn for both sprite and fallback)
        for i, (twx, twy) in enumerate(self.trail):
            tsx, tsy = camera.world_to_cam(twx, twy)
            alpha = (i + 1) / len(self.trail) * 0.5
            c = tuple(int(v * alpha) for v in self.color)
            pygame.draw.circle(surface, c, (int(tsx), int(tsy)), 1)

        # 主体
        if self.sprites:
            frame = self.sprites.get_frame()
            if frame:
                ax, ay = self.sprites.anchor
                surface.blit(frame, (int(sx) - ax, int(sy) - ay))
            else:
                pygame.draw.circle(surface, self.color, (int(sx), int(sy)), 2)
        else:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), 2)
