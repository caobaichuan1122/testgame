# ============================================================
#  工具函数：等距坐标转换、距离、角度
# ============================================================
import math
import os
import pygame
from settings import HALF_W, HALF_H, INTERNAL_WIDTH, INTERNAL_HEIGHT, PIXEL_SCALE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# --- 等距坐标转换 ---

def world_to_screen(wx, wy):
    sx = (wx - wy) * HALF_W
    sy = (wx + wy) * HALF_H
    return sx, sy


def screen_to_world(sx, sy):
    wx = (sx / HALF_W + sy / HALF_H) / 2
    wy = (sy / HALF_H - sx / HALF_W) / 2
    return wx, wy


# --- UI 坐标缩放 ---

def ui(v):
    """将内部分辨率坐标缩放为屏幕分辨率坐标"""
    return int(v * PIXEL_SCALE)


# --- 数学工具 ---

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def normalize(dx, dy):
    d = math.sqrt(dx * dx + dy * dy)
    if d < 0.0001:
        return 0.0, 0.0
    return dx / d, dy / d


def angle_between(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))


def angle_diff(a, b):
    d = (b - a) % 360
    if d > 180:
        d -= 360
    return d


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


# --- 字体缓存 ---
_font_cache = {}
_font_path = None  # 缓存字体路径


def _resolve_font_path():
    """查找支持中文的字体文件路径，找不到则返回None（使用默认字体）"""
    global _font_path
    if _font_path is not None:
        return _font_path if _font_path != "" else None

    import settings
    if getattr(settings, "LANGUAGE", "en") == "zh":
        # 优先查找本地 assets/font.ttf
        local_font = os.path.join(ASSETS_DIR, "font.ttf")
        if os.path.isfile(local_font):
            _font_path = local_font
            return _font_path
        # 在系统字体中查找中文字体
        for name in ("simhei", "microsoftyahei", "dengxian", "simsun"):
            path = pygame.font.match_font(name)
            if path:
                _font_path = path
                return _font_path
    _font_path = ""  # 标记为已查找但未找到
    return None


def get_font(size):
    if size not in _font_cache:
        font_path = _resolve_font_path()
        if font_path:
            _font_cache[size] = pygame.font.Font(font_path, size)
        else:
            _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


# 内部分辨率字体（实体浮动文字，画在 canvas 上）
FONT_SM = 12
FONT_MD = 14
FONT_LG = 20

# 屏幕分辨率字体（UI 文字，画在 screen 上）
FONT_UI_SM = 24
FONT_UI_MD = 28
FONT_UI_LG = 48


# --- 渲染工具 ---

def create_surface(width=INTERNAL_WIDTH, height=INTERNAL_HEIGHT):
    return pygame.Surface((width, height), pygame.SRCALPHA)


def draw_iso_diamond(surface, color, sx, sy, w=None, h=None):
    if w is None:
        w = HALF_W
    if h is None:
        h = HALF_H
    points = [
        (sx, sy),
        (sx + w, sy + h),
        (sx, sy + 2 * h),
        (sx - w, sy + h),
    ]
    pygame.draw.polygon(surface, color, points)


def draw_text(surface, text, x, y, font, color=(230, 230, 230), center=False):
    rendered = font.render(str(text), False, color)
    if center:
        x = x - rendered.get_width() // 2
        y = y - rendered.get_height() // 2
    surface.blit(rendered, (x, y))
    return rendered.get_width(), rendered.get_height()


def draw_bar(surface, x, y, w, h, ratio, color, bg_color=(40, 40, 40)):
    ratio = clamp(ratio, 0.0, 1.0)
    pygame.draw.rect(surface, bg_color, (x, y, w, h))
    if ratio > 0:
        pygame.draw.rect(surface, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(surface, (80, 80, 80), (x, y, w, h), 1)
