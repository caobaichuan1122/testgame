# ============================================================
#  玩家角色：8方向移动、三种战斗、属性、背包
# ============================================================
import math
import pygame
from entity import Entity
from stats import Stats
from inventory import Inventory
from settings import PLAYER_SPEED, PLAYER_COLOR, HALF_W, HALF_H
from utils import normalize
from sprite_manager import load_entity_sprites
from i18n import t, tf, get_item_name


# 8方向移动映射（WASD → 世界坐标偏移）
DIR_MAP = {
    "W": (-1, -1),
    "S": (1, 1),
    "A": (-1, 1),
    "D": (1, -1),
}


class Player(Entity):
    def __init__(self, wx, wy):
        super().__init__(wx, wy)
        self.stats = Stats(hp=80, mp=40, str_=4, dex=3, int_=3, def_=3, level=1)
        self.inventory = Inventory()
        self.inventory.gold = 50

        # 朝向（战斗动画可能用到）
        self.facing_angle = 0.0
        self.facing_dx = 1.0
        self.facing_dy = 0.0

        # 移动
        self.speed = PLAYER_SPEED / 60.0  # 转换为每帧移动量

        # 交互
        self.interact_target = None  # 附近可交互的NPC

        # 消息提示
        self.messages = []  # [(text, timer), ...]

        # 精灵
        self.sprites = load_entity_sprites("player")  # None if no assets
        self.moving = False

    def update(self, game):
        # 消息计时
        self.messages = [(t, c - 1) for t, c in self.messages if c > 1]

        self._handle_movement(game)
        self._check_interact(game)

        # 探索任务检测
        if game.quest_manager:
            discovered = game.quest_manager.on_player_move(self.wx, self.wy)
            for name in discovered:
                self.add_message(tf("discovered", name=name))
                game.chat_log.add(tf("discovered_area", name=name), "quest")

        # Advance sprite animation
        if self.sprites:
            state = "walk" if self.moving else "idle"
            self.sprites.update(state)

        # 应用装备防御加成到 stats
        self.stats.def_ = max(self.stats.def_,
                              3 + self.inventory.get_total_defense())

    def _handle_movement(self, game):
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dx += DIR_MAP["W"][0]
            dy += DIR_MAP["W"][1]
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dx += DIR_MAP["S"][0]
            dy += DIR_MAP["S"][1]
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx += DIR_MAP["A"][0]
            dy += DIR_MAP["A"][1]
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += DIR_MAP["D"][0]
            dy += DIR_MAP["D"][1]

        if dx != 0 or dy != 0:
            self.moving = True
            dx, dy = normalize(dx, dy)
            self.facing_dx = dx
            self.facing_dy = dy
            self.facing_angle = math.degrees(math.atan2(dy, dx))

            new_wx = self.wx + dx * self.speed
            new_wy = self.wy + dy * self.speed

            # 碰撞检测：分轴
            if game.iso_map.is_walkable(new_wx, self.wy):
                self.wx = new_wx
            if game.iso_map.is_walkable(self.wx, new_wy):
                self.wy = new_wy
        else:
            self.moving = False

    def _check_interact(self, game):
        """检查附近是否有可交互NPC"""
        self.interact_target = game.entities.get_nearest_npc(
            self.wx, self.wy, 3.0
        )

    def handle_keydown(self, key, game):
        """处理按键事件"""
        # 交互
        if key == pygame.K_e:
            if self.interact_target:
                self.interact_target.interact(game)

    def _on_enemy_kill(self, enemy, game):
        """敌人被击杀时的回调"""
        xp = enemy.xp_reward
        gold = enemy.gold_reward
        leveled = self.stats.add_xp(xp)
        self.inventory.gold += gold
        self.add_message(f"+{xp}XP +{gold}G")
        if leveled:
            self.add_message(tf("level_up", level=self.stats.level))

        # 通知任务系统
        if game.quest_manager:
            game.quest_manager.on_enemy_kill(enemy.enemy_type)

        # 掉落物品
        for item_id in enemy.drops:
            self.inventory.add_item(item_id)
            name = get_item_name(item_id)
            self.add_message(tf("got_item", name=name))
            # 通知收集任务
            if game.quest_manager:
                game.quest_manager.on_collect(item_id)

    def on_projectile_hit(self, enemy, damage, game):
        """投射物击中敌人的回调"""
        from combat import check_crit
        is_crit = check_crit(self.stats.dex)
        if is_crit:
            damage = int(damage * 1.5)
        enemy.stats.take_damage(damage)
        msg = f"-{damage}" + (" CRIT!" if is_crit else "")
        self.add_message(msg)
        if not enemy.stats.alive:
            self._on_enemy_kill(enemy, game)

    def add_message(self, text, duration=90):
        self.messages.append((text, duration))
        if len(self.messages) > 5:
            self.messages.pop(0)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_cam(self.wx, self.wy)

        if self.sprites:
            frame = self.sprites.get_frame()
            if frame:
                ax, ay = self.sprites.anchor
                surface.blit(frame, (int(sx) - ax, int(sy) - ay))
        else:
            # 玩家主体（菱形方块）
            body_w, body_h = 6, 4
            points = [
                (sx, sy - 8),
                (sx + body_w, sy - 8 + body_h),
                (sx, sy - 8 + body_h * 2),
                (sx - body_w, sy - 8 + body_h),
            ]
            pygame.draw.polygon(surface, PLAYER_COLOR, points)

            # 头部
            pygame.draw.circle(surface, (100, 200, 255), (int(sx), int(sy) - 12), 3)

    def draw_labels(self, surface, camera):
        """在屏幕层绘制浮动消息（避免缩放模糊）"""
        from utils import get_font, FONT_UI_SM
        from settings import PIXEL_SCALE

        sx, sy = camera.world_to_cam(self.wx, self.wy)
        scr_x = sx * PIXEL_SCALE
        scr_y = sy * PIXEL_SCALE

        msg_font = get_font(FONT_UI_SM)
        for i, (text, timer) in enumerate(self.messages):
            msg_surf = msg_font.render(text, False, (255, 255, 200))
            surface.blit(msg_surf,
                         (int(scr_x) - msg_surf.get_width() // 2,
                          int(scr_y) - 66 - i * 28))

