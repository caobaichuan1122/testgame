# ============================================================
#  Minimap: top-down overview of the tile map + entity dots
# ============================================================
import pygame
from world.iso_map import TILE_COLORS
from core.utils import get_font, FONT_UI_SM

TILE_PX = 2        # screen pixels per map tile
BORDER  = 2        # frame border width
PAD     = 8        # distance from screen edge


class MinimapUI:
    def __init__(self):
        self.visible = True
        self._map_surf = None   # pre-rendered tile colors (rebuilt on load)

    # ------------------------------------------------------------------
    #  Build (call once after the map loads)
    # ------------------------------------------------------------------
    def build(self, iso_map):
        """Pre-render all tile colours into a static surface."""
        w = iso_map.cols * TILE_PX
        h = iso_map.rows * TILE_PX
        surf = pygame.Surface((w, h))
        surf.fill((15, 15, 15))
        for row in range(iso_map.rows):
            for col in range(iso_map.cols):
                color = TILE_COLORS.get(iso_map.grid[row][col])
                if color:
                    surf.set_at((col * TILE_PX,     row * TILE_PX),     color)
                    surf.set_at((col * TILE_PX + 1, row * TILE_PX),     color)
                    surf.set_at((col * TILE_PX,     row * TILE_PX + 1), color)
                    surf.set_at((col * TILE_PX + 1, row * TILE_PX + 1), color)
        self._map_surf = surf

    def toggle(self):
        self.visible = not self.visible

    # ------------------------------------------------------------------
    #  Draw (called every frame from ui_manager)
    # ------------------------------------------------------------------
    def draw(self, surface, player, entities):
        if not self.visible or self._map_surf is None or not player:
            return

        sw, sh = surface.get_size()
        map_w, map_h = self._map_surf.get_size()

        # Box position: bottom-right corner
        bx = sw - map_w - BORDER * 2 - PAD
        by = sh - map_h - BORDER * 2 - PAD

        # Semi-transparent dark background
        bg = pygame.Surface((map_w + BORDER * 2, map_h + BORDER * 2),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        surface.blit(bg, (bx, by))

        # Gold border frame
        pygame.draw.rect(surface, (180, 160, 100),
                         (bx, by, map_w + BORDER * 2, map_h + BORDER * 2),
                         BORDER)

        # Tile map
        mx = bx + BORDER
        my = by + BORDER
        surface.blit(self._map_surf, (mx, my))

        # Enemy dots (red)
        for e in entities.enemies:
            if e.active:
                ex = int(e.wx) * TILE_PX
                ey = int(e.wy) * TILE_PX
                pygame.draw.rect(surface, (220, 60, 60),
                                 (mx + ex, my + ey, TILE_PX, TILE_PX))

        # NPC dots (yellow)
        for n in entities.npcs:
            if n.active:
                nx = int(n.wx) * TILE_PX
                ny = int(n.wy) * TILE_PX
                pygame.draw.rect(surface, (220, 200, 60),
                                 (mx + nx, my + ny, TILE_PX, TILE_PX))

        # Player dot (white, 1px larger for visibility)
        px = int(player.wx) * TILE_PX
        py = int(player.wy) * TILE_PX
        pygame.draw.rect(surface, (255, 255, 255),
                         (mx + px - 1, my + py - 1, TILE_PX + 2, TILE_PX + 2))

        # "M: map" key hint above the minimap
        font = get_font(FONT_UI_SM)
        hint = font.render("M: map", False, (160, 150, 130))
        surface.blit(hint, (bx, by - hint.get_height() - 2))
