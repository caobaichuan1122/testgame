# ============================================================
#  SceneManager: 16 independent 30×30 zone scenes
#
#  World layout (4×4 grid of zones):
#   col→  0           1           2           3
#  row↓
#   0     shire       rivendell   lothlorien  weathertop
#   1     fangorn     hobbiton    misty_mts   moria
#   2     rohan_west  rohan_ctr   rohan_east  dead_marshes
#   3     anduin      osgiliath   mordor      mount_doom
#
#  Transitions: walking off a scene edge teleports the
#  player to the adjacent scene with a brief black fade.
# ============================================================
import pygame

SCENE_SIZE = 30   # every scene is SCENE_SIZE × SCENE_SIZE tiles

# zone_id → (col_block, row_block) in the 4×4 world grid
ZONE_GRID = {
    "shire":        (0, 0), "rivendell":    (1, 0),
    "lothlorien":   (2, 0), "weathertop":   (3, 0),
    "fangorn":      (0, 1), "hobbiton":     (1, 1),
    "misty_mts":    (2, 1), "moria":        (3, 1),
    "rohan_west":   (0, 2), "rohan_center": (1, 2),
    "rohan_east":   (2, 2), "dead_marshes": (3, 2),
    "anduin":       (0, 3), "osgiliath":    (1, 3),
    "mordor":       (2, 3), "mount_doom":   (3, 3),
}

# Reverse: (col_block, row_block) → zone_id
GRID_TO_ZONE = {v: k for k, v in ZONE_GRID.items()}

# Cardinal direction → (dcol, drow)
_DIR_DELTA = {
    "east":  ( 1,  0),
    "west":  (-1,  0),
    "south": ( 0,  1),
    "north": ( 0, -1),
}


class SceneManager:
    """Holds all zone scenes; manages the active scene and fade animation."""

    FADE_SPEED = 14   # alpha decremented per frame (255 / 14 ≈ 18 frames fade)

    def __init__(self):
        # zone_id → { "iso_map": IsoMap, "enemies": [...], "npcs": [...] }
        self.scenes: dict = {}
        self.active_id: str | None = None
        # Fade overlay: 255 = fully black, 0 = fully transparent
        self.fade_alpha: int = 0

    # ------------------------------------------------------------------
    #  Scene access
    # ------------------------------------------------------------------
    @property
    def active(self) -> dict:
        return self.scenes[self.active_id]

    @property
    def iso_map(self):
        return self.active["iso_map"]

    # ------------------------------------------------------------------
    #  Navigation
    # ------------------------------------------------------------------
    def neighbor_id(self, direction: str) -> str | None:
        """Return zone_id of the neighbor in *direction*, or None at world edge."""
        cb, rb = ZONE_GRID[self.active_id]
        dc, dr = _DIR_DELTA[direction]
        return GRID_TO_ZONE.get((cb + dc, rb + dr))

    # ------------------------------------------------------------------
    #  Fade animation (call update_fade every frame)
    # ------------------------------------------------------------------
    def start_fade(self):
        """Start a fade-in from black (call after scene switch)."""
        self.fade_alpha = 255

    def update_fade(self):
        """Tick: decrease fade alpha."""
        if self.fade_alpha > 0:
            self.fade_alpha = max(0, self.fade_alpha - self.FADE_SPEED)

    def draw_fade(self, surface: pygame.Surface):
        """Blit black overlay; call AFTER the world draw."""
        if self.fade_alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

    # ------------------------------------------------------------------
    #  Metadata helper
    # ------------------------------------------------------------------
    def zone_meta(self, zones_list: list) -> dict | None:
        for z in zones_list:
            if z["id"] == self.active_id:
                return z
        return None
