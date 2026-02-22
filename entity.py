# ============================================================
#  Entity 基类 + EntityManager
# ============================================================
import pygame
from utils import world_to_screen


class Entity:
    """所有游戏实体的基类"""

    def __init__(self, wx, wy):
        self.wx = float(wx)
        self.wy = float(wy)
        self.active = True

    @property
    def sort_key(self):
        """深度排序键：wx + wy 越大越靠前（画家算法）"""
        return self.wx + self.wy

    def update(self, game):
        pass

    def draw(self, surface, camera):
        pass

    def draw_labels(self, surface, camera):
        """绘制文字标签到屏幕层（子类可覆盖）"""
        pass


class EntityManager:
    """管理所有实体：分类更新/绘制/空间查询"""

    def __init__(self):
        self.player = None
        self.enemies = []
        self.npcs = []
        self.projectiles = []

    def all_entities(self):
        """返回所有活跃实体的列表（用于深度排序绘制）"""
        entities = []
        if self.player and self.player.active:
            entities.append(self.player)
        entities.extend(e for e in self.enemies if e.active)
        entities.extend(n for n in self.npcs if n.active)
        entities.extend(p for p in self.projectiles if p.active)
        return entities

    def update(self, game):
        if self.player:
            self.player.update(game)
        for e in self.enemies:
            if e.active:
                e.update(game)
        for n in self.npcs:
            if n.active:
                n.update(game)
        for p in self.projectiles:
            if p.active:
                p.update(game)
        # 清理已死亡的投射物
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface, camera):
        """按深度排序绘制所有实体"""
        entities = self.all_entities()
        entities.sort(key=lambda e: e.sort_key)
        for e in entities:
            e.draw(surface, camera)

    def draw_labels(self, surface, camera):
        """在屏幕层绘制所有实体的文字标签（缩放后调用）"""
        entities = self.all_entities()
        entities.sort(key=lambda e: e.sort_key)
        for e in entities:
            e.draw_labels(surface, camera)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_projectile(self, proj):
        self.projectiles.append(proj)

    def get_enemies_in_range(self, wx, wy, radius):
        """返回指定范围内的活跃敌人列表"""
        from utils import distance
        result = []
        for e in self.enemies:
            if e.active and e.stats.alive:
                if distance(wx, wy, e.wx, e.wy) <= radius:
                    result.append(e)
        return result

    def get_nearest_npc(self, wx, wy, radius):
        """返回最近的NPC（如果在范围内）"""
        from utils import distance
        best = None
        best_dist = radius + 1
        for n in self.npcs:
            if not n.active:
                continue
            d = distance(wx, wy, n.wx, n.wy)
            if d <= radius and d < best_dist:
                best = n
                best_dist = d
        return best
