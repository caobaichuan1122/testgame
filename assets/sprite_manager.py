# ============================================================
#  sprite_manager.py - Sprite loading, caching, animation
#  If assets exist, entities render sprites; otherwise fall
#  back to the existing color-block rendering.
# ============================================================
import os
import json
import pygame

# --------------- paths ---------------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = _BASE_DIR  # sprite_manager.py lives inside the assets/ folder
SPRITE_CONFIG_PATH = os.path.join(ASSETS_DIR, "config.json")

# --------------- global cache ---------------
_image_cache: dict[str, pygame.Surface] = {}
_config_cache: dict | None = None


def _get_config() -> dict | None:
    """Load and cache assets/config.json. Returns None if missing."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if os.path.isfile(SPRITE_CONFIG_PATH):
        try:
            with open(SPRITE_CONFIG_PATH, "r", encoding="utf-8") as f:
                _config_cache = json.load(f)
        except Exception:
            _config_cache = {}
    else:
        _config_cache = {}
    return _config_cache


# --------------- low-level loaders ---------------

def load_image(path: str, colorkey=None) -> pygame.Surface | None:
    """Load a single image, cache it. Returns None on failure."""
    if path in _image_cache:
        return _image_cache[path]
    full = os.path.join(ASSETS_DIR, path) if not os.path.isabs(path) else path
    if not os.path.isfile(full):
        return None
    try:
        img = pygame.image.load(full).convert_alpha()
        if colorkey is not None:
            img.set_colorkey(colorkey)
        _image_cache[path] = img
        return img
    except Exception:
        return None


def load_sheet(path: str, frame_w: int, frame_h: int) -> list[pygame.Surface] | None:
    """Load a spritesheet and cut into a flat list of frames (row-major)."""
    sheet = load_image(path)
    if sheet is None:
        return None
    cols = sheet.get_width() // frame_w
    rows = sheet.get_height() // frame_h
    frames = []
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * frame_w, r * frame_h, frame_w, frame_h)
            frame = sheet.subsurface(rect).copy()
            frames.append(frame)
    return frames


def load_tile_set(path: str, tile_w: int, tile_h: int) -> dict[int, pygame.Surface] | None:
    """Load a tileset image, cut tiles, return {index: Surface}."""
    sheet = load_image(path)
    if sheet is None:
        return None
    cols = sheet.get_width() // tile_w
    rows = sheet.get_height() // tile_h
    tiles = {}
    idx = 0
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * tile_w, r * tile_h, tile_w, tile_h)
            tiles[idx] = sheet.subsurface(rect).copy()
            idx += 1
    return tiles


# --------------- Animation ---------------

class Animation:
    """Frame-based animation: list of Surfaces + timing."""

    def __init__(self, frames: list[pygame.Surface], speed: int = 6, loop: bool = True):
        self.frames = frames
        self.speed = speed  # ticks per frame
        self.loop = loop
        self.index = 0
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.index += 1
            if self.index >= len(self.frames):
                self.index = 0 if self.loop else len(self.frames) - 1

    def get_frame(self) -> pygame.Surface:
        return self.frames[self.index]

    def reset(self):
        self.index = 0
        self.timer = 0


# --------------- SpriteSet ---------------

class SpriteSet:
    """Manages multiple animation states for one entity."""

    def __init__(self, anims: dict[str, Animation], anchor: tuple[int, int] = (0, 0)):
        self.anims = anims       # {"idle": Animation, "walk": Animation, ...}
        self.anchor = anchor     # (ax, ay) offset from top-left to foot
        self.current: str | None = None

    def update(self, state: str = "idle"):
        if state != self.current:
            self.current = state
            if state in self.anims:
                self.anims[state].reset()
        if self.current and self.current in self.anims:
            self.anims[self.current].update()

    def get_frame(self, state: str | None = None) -> pygame.Surface | None:
        key = state or self.current or "idle"
        if key in self.anims:
            return self.anims[key].get_frame()
        # fallback: first anim, first frame
        if self.anims:
            return next(iter(self.anims.values())).frames[0]
        return None


# --------------- high-level loaders ---------------

def load_tile_sprites() -> dict[int, pygame.Surface] | None:
    """Load tile sprites according to config. Returns {tile_id: Surface} or None."""
    cfg = _get_config()
    if not cfg or "tiles" not in cfg:
        return None
    tc = cfg["tiles"]
    source = tc.get("source")
    tile_w = tc.get("tile_w", 32)
    tile_h = tc.get("tile_h", 16)
    mapping = tc.get("mapping")  # {"1": 0, "2": 1, ...}

    if not source:
        return None

    raw = load_tile_set(source, tile_w, tile_h)
    if raw is None:
        return None

    if mapping:
        result = {}
        for tile_id_str, sheet_idx in mapping.items():
            tid = int(tile_id_str)
            if sheet_idx in raw:
                result[tid] = raw[sheet_idx]
        return result if result else None
    else:
        # no mapping: use raw indices directly as tile_ids
        return raw


def load_entity_sprites(entity_key: str) -> SpriteSet | None:
    """Load a SpriteSet for an entity from config.

    entity_key examples: "player", "enemies/slime", "npcs/villager"
    """
    cfg = _get_config()
    if not cfg:
        return None

    # Navigate nested keys: "enemies/slime" -> cfg["enemies"]["slime"]
    parts = entity_key.replace("\\", "/").split("/")
    node = cfg
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return None

    if not isinstance(node, dict) or "source" not in node:
        return None

    source = node["source"]
    frame_w = node.get("frame_w", 32)
    frame_h = node.get("frame_h", 32)
    anchor = tuple(node.get("anchor", [frame_w // 2, frame_h - 2]))
    anim_defs = node.get("anims", {})

    all_frames = load_sheet(source, frame_w, frame_h)
    if all_frames is None:
        return None

    cols = 1
    sheet = load_image(source)
    if sheet:
        cols = sheet.get_width() // frame_w

    anims: dict[str, Animation] = {}

    if anim_defs:
        for anim_name, adef in anim_defs.items():
            row = adef.get("row", 0)
            n_frames = adef.get("frames", 1)
            speed = adef.get("speed", 6)
            loop = adef.get("loop", True)
            start = row * cols
            frames = all_frames[start: start + n_frames]
            if frames:
                anims[anim_name] = Animation(frames, speed, loop)
    else:
        # No animation definitions: treat all frames as a single "idle" anim
        if all_frames:
            anims["idle"] = Animation(all_frames, speed=6, loop=True)

    if not anims:
        return None

    return SpriteSet(anims, anchor)


def load_single_sprite(path: str, anchor: tuple[int, int] | None = None) -> SpriteSet | None:
    """Load a single image as a one-frame SpriteSet (useful for projectiles)."""
    img = load_image(path)
    if img is None:
        return None
    if anchor is None:
        anchor = (img.get_width() // 2, img.get_height() // 2)
    anim = Animation([img], speed=999, loop=True)
    return SpriteSet({"idle": anim}, anchor)
