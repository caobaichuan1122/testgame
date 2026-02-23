# ============================================================
#  Entity base class + EntityManager
# ============================================================
import pygame
from utils import world_to_screen


class Entity:
    """Base class for all game entities."""

    def __init__(self, wx, wy):
        self.wx = float(wx)
        self.wy = float(wy)
        self.active = True

    @property
    def sort_key(self):
        """Depth sort key: higher wx+wy draws on top (painter's algorithm)."""
        return self.wx + self.wy

    def update(self, game):
        pass

    def draw(self, surface, camera):
        pass

    def draw_labels(self, surface, camera):
        """Draw text labels onto screen layer (subclasses may override)."""
        pass


class EntityManager:
    """Manages all entities: categorized update/draw/spatial queries."""

    def __init__(self):
        self.player = None
        self.enemies = []
        self.npcs = []
        self.projectiles = []

    def all_entities(self):
        """Return list of all active entities (for depth-sorted drawing)."""
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
        # Remove expired projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, surface, camera):
        """Draw all entities sorted by depth."""
        entities = self.all_entities()
        entities.sort(key=lambda e: e.sort_key)
        for e in entities:
            e.draw(surface, camera)

    def draw_labels(self, surface, camera):
        """Draw text labels for all entities on screen layer (called after scaling)."""
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
        """Return list of active enemies within radius."""
        from utils import distance
        result = []
        for e in self.enemies:
            if e.active and e.stats.alive:
                if distance(wx, wy, e.wx, e.wy) <= radius:
                    result.append(e)
        return result

    def get_nearest_npc(self, wx, wy, radius):
        """Return nearest NPC within radius, or None."""
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
