# ============================================================
#  等距瓦片地图：坐标转换、碰撞、菱形渲染
# ============================================================
import pygame
from settings import (
    HALF_W, HALF_H, TILE_W, TILE_H, MAP_COLS, MAP_ROWS,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    COLOR_GRASS, COLOR_GRASS_DARK, COLOR_DIRT, COLOR_STONE, COLOR_STONE_DARK,
    COLOR_WATER, COLOR_WATER_DEEP, COLOR_SAND, COLOR_BRIDGE,
    COLOR_TREE, COLOR_WALL, COLOR_CAVE, COLOR_CLIFF,
)
from utils import world_to_screen
from sprite_manager import load_tile_sprites

# 瓦片类型
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

# 瓦片颜色映射
TILE_COLORS = {
    TILE_EMPTY: None,
    TILE_GRASS: COLOR_GRASS,
    TILE_GRASS2: COLOR_GRASS_DARK,
    TILE_DIRT: COLOR_DIRT,
    TILE_STONE: COLOR_STONE,
    TILE_STONE2: COLOR_STONE_DARK,
    TILE_WATER: COLOR_WATER,
    TILE_WATER2: COLOR_WATER_DEEP,
    TILE_SAND: COLOR_SAND,
    TILE_BRIDGE: COLOR_BRIDGE,
    TILE_TREE: COLOR_TREE,
    TILE_WALL: COLOR_WALL,
    TILE_CAVE: COLOR_CAVE,
    TILE_CLIFF: COLOR_CLIFF,
}

# 不可通行的瓦片
SOLID_TILES = {TILE_WATER, TILE_WATER2, TILE_TREE, TILE_WALL, TILE_CLIFF}


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
        return TILE_WALL  # 越界视为墙

    def fill_rect(self, c1, r1, c2, r2, tile_id):
        for r in range(r1, r2):
            for c in range(c1, c2):
                self.set_tile(c, r, tile_id)

    def is_walkable(self, wx, wy):
        """检查世界坐标是否可通行"""
        col = int(wx)
        row = int(wy)
        if col < 0 or col >= self.cols or row < 0 or row >= self.rows:
            return False
        return self.grid[row][col] not in SOLID_TILES

    def is_in_bounds(self, wx, wy):
        return 0 <= wx < self.cols and 0 <= wy < self.rows

    def draw(self, surface, camera):
        """绘制可见范围内的瓦片（视口裁剪）"""
        cam_x, cam_y = camera.offset_x, camera.offset_y
        margin = 3  # 额外绘制边缘瓦片

        for row in range(self.rows):
            for col in range(self.cols):
                tile_id = self.grid[row][col]
                color = TILE_COLORS.get(tile_id)
                if color is None:
                    continue

                # 世界坐标就是网格坐标（每格=1单位）
                sx, sy = world_to_screen(col, row)
                sx -= cam_x
                sy -= cam_y

                # 视口裁剪
                if (sx + HALF_W < -TILE_W or sx - HALF_W > INTERNAL_WIDTH + TILE_W or
                        sy < -TILE_H * 2 or sy > INTERNAL_HEIGHT + TILE_H * 2):
                    continue

                # Sprite rendering (if available) with fallback to color blocks
                if self.tile_sprites and tile_id in self.tile_sprites:
                    sprite = self.tile_sprites[tile_id]
                    surface.blit(sprite,
                                 (sx - sprite.get_width() // 2,
                                  sy + HALF_H - sprite.get_height()))
                else:
                    # 绘制菱形
                    points = [
                        (sx, sy),
                        (sx + HALF_W, sy + HALF_H),
                        (sx, sy + TILE_H),
                        (sx - HALF_W, sy + HALF_H),
                    ]
                    pygame.draw.polygon(surface, color, points)

                    # 树木和墙壁额外绘制高度块
                    if tile_id in (TILE_TREE, TILE_WALL, TILE_CLIFF):
                        h = 10 if tile_id == TILE_TREE else 6
                        dark = tuple(max(0, c - 40) for c in color)
                        # 左面
                        left_face = [
                            (sx - HALF_W, sy + HALF_H),
                            (sx, sy + TILE_H),
                            (sx, sy + TILE_H - h),
                            (sx - HALF_W, sy + HALF_H - h),
                        ]
                        pygame.draw.polygon(surface, dark, left_face)
                        # 右面
                        right_face = [
                            (sx + HALF_W, sy + HALF_H),
                            (sx, sy + TILE_H),
                            (sx, sy + TILE_H - h),
                            (sx + HALF_W, sy + HALF_H - h),
                        ]
                        darker = tuple(max(0, c - 60) for c in color)
                        pygame.draw.polygon(surface, darker, right_face)
                        # 顶面
                        top_points = [
                            (sx, sy - h),
                            (sx + HALF_W, sy + HALF_H - h),
                            (sx, sy + TILE_H - h),
                            (sx - HALF_W, sy + HALF_H - h),
                        ]
                        lighter = tuple(min(255, c + 20) for c in color)
                        pygame.draw.polygon(surface, lighter, top_points)
