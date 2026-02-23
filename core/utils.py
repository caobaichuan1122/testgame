# ============================================================
#  Utility functions: isometric transforms, distance, angles
# ============================================================
import math
import os
import pygame
from core.settings import HALF_W, HALF_H, INTERNAL_WIDTH, INTERNAL_HEIGHT, PIXEL_SCALE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


# --- Isometric coordinate transforms ---

def world_to_screen(wx, wy):
    sx = (wx - wy) * HALF_W
    sy = (wx + wy) * HALF_H
    return sx, sy


def screen_to_world(sx, sy):
    wx = (sx / HALF_W + sy / HALF_H) / 2
    wy = (sy / HALF_H - sx / HALF_W) / 2
    return wx, wy


# --- UI coordinate scaling ---

def ui(v):
    """Scale internal-resolution coordinate to screen-resolution."""
    return int(v * PIXEL_SCALE)


# --- Math utilities ---

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


# --- Font cache ---
_font_cache = {}
_font_path = None  # cached font path


def _resolve_font_path():
    """Find a font file that supports CJK characters; return None to use default."""
    global _font_path
    if _font_path is not None:
        return _font_path if _font_path != "" else None

    import settings
    if getattr(settings, "LANGUAGE", "en") == "zh":
        # Prefer local assets/font.ttf
        local_font = os.path.join(ASSETS_DIR, "font.ttf")
        if os.path.isfile(local_font):
            _font_path = local_font
            return _font_path
        # Search system fonts for CJK support
        for name in ("simhei", "microsoftyahei", "dengxian", "simsun"):
            path = pygame.font.match_font(name)
            if path:
                _font_path = path
                return _font_path
    _font_path = ""  # mark as searched but not found
    return None


def get_font(size):
    if size not in _font_cache:
        font_path = _resolve_font_path()
        if font_path:
            _font_cache[size] = pygame.font.Font(font_path, size)
        else:
            _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


# Internal-resolution fonts (entity floating text, drawn on canvas)
FONT_SM = 12
FONT_MD = 14
FONT_LG = 20

# Screen-resolution fonts (UI text, drawn on screen)
FONT_UI_SM = 24
FONT_UI_MD = 28
FONT_UI_LG = 48


# --- Rendering utilities ---

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
