# ============================================================
#  Isometric tile map: coordinate transforms, collision, diamond rendering
# ============================================================
import pygame
from core.settings import (
    HALF_W, HALF_H, TILE_W, TILE_H, MAP_COLS, MAP_ROWS,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    COLOR_GRASS, COLOR_GRASS_DARK, COLOR_DIRT, COLOR_STONE, COLOR_STONE_DARK,
    COLOR_WATER, COLOR_WATER_DEEP, COLOR_SAND, COLOR_BRIDGE,
    COLOR_TREE, COLOR_WALL, COLOR_CAVE, COLOR_CLIFF, COLOR_FENCE,
    COLOR_HOUSE_WALL, COLOR_ROOF,
)
from core.utils import world_to_screen
from assets.sprite_manager import load_tile_sprites

# Tile types
TILE_EMPTY = 0
TILE_GRASS = 1
TILE_GRASS2 = 2
TILE_DIRT = 3
TILE_STONE = 4
TILE_STONE2 = 5
TILE_WATER = 6
TILE_WATER2 = 7
TILE_SAND = 8
TILE_BRIDGE = 9
TILE_TREE = 10
TILE_WALL = 11
TILE_CAVE = 12
TILE_CLIFF = 13
TILE_FENCE = 14
TILE_HOUSE_WALL = 15   # tall warm-stone wall with window slots
TILE_ROOF = 16         # terracotta roof interior (wall fill + pyramid)

# Tile color mapping
TILE_COLORS = {
    TILE_EMPTY:      None,
    TILE_GRASS:      COLOR_GRASS,
    TILE_GRASS2:     COLOR_GRASS_DARK,
    TILE_DIRT:       COLOR_DIRT,
    TILE_STONE:      COLOR_STONE,
    TILE_STONE2:     COLOR_STONE_DARK,
    TILE_WATER:      COLOR_WATER,
    TILE_WATER2:     COLOR_WATER_DEEP,
    TILE_SAND:       COLOR_SAND,
    TILE_BRIDGE:     COLOR_BRIDGE,
    TILE_TREE:       COLOR_TREE,
    TILE_WALL:       COLOR_WALL,
    TILE_CAVE:       COLOR_CAVE,
    TILE_CLIFF:      COLOR_CLIFF,
    TILE_FENCE:      COLOR_FENCE,
    TILE_HOUSE_WALL: COLOR_HOUSE_WALL,
    TILE_ROOF:       COLOR_HOUSE_WALL,  # floor diamond uses wall tone
}

# Impassable tiles
SOLID_TILES = {
    TILE_WATER, TILE_WATER2, TILE_TREE, TILE_WALL,
    TILE_CLIFF, TILE_FENCE, TILE_HOUSE_WALL, TILE_ROOF,
}


class IsoMap:
    def __init__(self, cols=MAP_COLS, rows=MAP_ROWS):
        self.cols = cols
        self.rows = rows
        self.grid = [[TILE_GRASS for _ in range(cols)] for _ in range(rows)]
        self.tile_sprites = load_tile_sprites()  # None if no assets

    def set_tile(self, col, row, tile_id):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.grid[row][col] = tile_id

    def get_tile(self, col, row):
        if 0 <= col < self.cols and 0 <= row < self.rows:
            return self.grid[row][col]
        return TILE_WALL  # Out of bounds treated as wall

    def fill_rect(self, c1, r1, c2, r2, tile_id):
        for r in range(r1, r2):
            for c in range(c1, c2):
                self.set_tile(c, r, tile_id)

    def is_walkable(self, wx, wy):
        """Check if world coordinates are walkable."""
        col = int(wx)
        row = int(wy)
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return False
        return self.grid[row][col] not in SOLID_TILES

    def nearest_walkable(self, wx, wy):
        """Return the nearest walkable (wx, wy) via spiral search from the given position."""
        if self.is_walkable(wx, wy):
            return (float(wx), float(wy))
        cx, cy = int(wx), int(wy)
        for radius in range(1, 10):
            for dc in range(-radius, radius + 1):
                for dr in range(-radius, radius + 1):
                    if abs(dc) == radius or abs(dr) == radius:
                        nx, ny = cx + dc + 0.5, cy + dr + 0.5
                        if self.is_walkable(nx, ny):
                            return (nx, ny)
        return (float(wx), float(wy))

    def is_in_bounds(self, wx, wy):
        return 0 <= wx < self.cols and 0 <= wy < self.rows

    def draw(self, surface, camera):
        """Draw tiles within visible range (viewport culling)."""
        cam_x, cam_y = camera.offset_x, camera.offset_y

        for row in range(self.rows):
            for col in range(self.cols):
                tile_id = self.grid[row][col]
                color = TILE_COLORS.get(tile_id)
                if color is None:
                    continue

                sx, sy = world_to_screen(col, row)
                sx -= cam_x
                sy -= cam_y

                # Viewport culling
                if (sx + HALF_W < -TILE_W or sx - HALF_W > INTERNAL_WIDTH + TILE_W or
                        sy < -TILE_H * 4 or sy > INTERNAL_HEIGHT + TILE_H * 4):
                    continue

                # Sprite rendering (if available) with fallback to color blocks
                if self.tile_sprites and tile_id in self.tile_sprites:
                    sprite = self.tile_sprites[tile_id]
                    surface.blit(sprite,
                                 (sx - sprite.get_width() // 2,
                                  sy + HALF_H - sprite.get_height()))
                else:
                    # Floor diamond
                    points = [
                        (sx,          sy),
                        (sx + HALF_W, sy + HALF_H),
                        (sx,          sy + TILE_H),
                        (sx - HALF_W, sy + HALF_H),
                    ]
                    pygame.draw.polygon(surface, color, points)

                    # --- Elevated tiles ---
                    if tile_id in (TILE_TREE, TILE_WALL, TILE_CLIFF, TILE_FENCE,
                                   TILE_HOUSE_WALL, TILE_ROOF):

                        # Height and face base-color per tile type
                        if tile_id == TILE_TREE:
                            h, fc = 10, color
                        elif tile_id == TILE_FENCE:
                            h, fc = 3, color
                        elif tile_id in (TILE_HOUSE_WALL, TILE_ROOF):
                            h, fc = 14, COLOR_HOUSE_WALL
                        else:
                            h, fc = 6, color

                        dark   = (max(0, fc[0]-40), max(0, fc[1]-40), max(0, fc[2]-40))
                        darker = (max(0, fc[0]-65), max(0, fc[1]-65), max(0, fc[2]-65))
                        light  = (min(255, fc[0]+22), min(255, fc[1]+22), min(255, fc[2]+22))

                        # Left face
                        pygame.draw.polygon(surface, dark, [
                            (sx - HALF_W, sy + HALF_H),
                            (sx,          sy + TILE_H),
                            (sx,          sy + TILE_H - h),
                            (sx - HALF_W, sy + HALF_H - h),
                        ])
                        # Right face
                        pygame.draw.polygon(surface, darker, [
                            (sx + HALF_W, sy + HALF_H),
                            (sx,          sy + TILE_H),
                            (sx,          sy + TILE_H - h),
                            (sx + HALF_W, sy + HALF_H - h),
                        ])
                        # Top face (terracotta for TILE_ROOF, lighter stone otherwise)
                        top_col = COLOR_ROOF if tile_id == TILE_ROOF else light
                        pygame.draw.polygon(surface, top_col, [
                            (sx,          sy - h),
                            (sx + HALF_W, sy + HALF_H - h),
                            (sx,          sy + TILE_H - h),
                            (sx - HALF_W, sy + HALF_H - h),
                        ])

                        # === Window slots on house walls ===
                        if tile_id == TILE_HOUSE_WALL:
                            win = (18, 18, 30)
                            # Left-face window: small dark diamond in parallelogram center
                            wlx = sx - HALF_W * 3 // 4
                            wly = sy + HALF_H - h // 3
                            pygame.draw.polygon(surface, win, [
                                (wlx - 2, wly),
                                (wlx,     wly - 2),
                                (wlx + 2, wly),
                                (wlx,     wly + 2),
                            ])
                            # Right-face window
                            wrx = sx + HALF_W * 3 // 4
                            wry = sy + HALF_H - h // 3
                            pygame.draw.polygon(surface, win, [
                                (wrx - 2, wry),
                                (wrx,     wry - 2),
                                (wrx + 2, wry),
                                (wrx,     wry + 2),
                            ])

                        # === Pyramid roof peak for TILE_ROOF ===
                        if tile_id == TILE_ROOF:
                            h_peak = 6
                            # Pyramid base = elevated top-diamond corners
                            b_s = (sx,          sy + TILE_H - h)
                            b_w = (sx - HALF_W, sy + HALF_H - h)
                            b_e = (sx + HALF_W, sy + HALF_H - h)
                            apex = (sx, sy - h - h_peak)

                            r = COLOR_ROOF
                            r_lt = (min(255, r[0]+18), min(255, r[1]+18), min(255, r[2]+18))
                            r_dk = (max(0,   r[0]-25), max(0,   r[1]-25), max(0,   r[2]-25))

                            # Front-left slope (lighter, catches "light")
                            pygame.draw.polygon(surface, r_lt, [b_w, b_s, apex])
                            # Front-right slope (darker, in shadow)
                            pygame.draw.polygon(surface, r_dk, [b_s, b_e, apex])
